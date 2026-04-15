from fastapi import HTTPException
from langchain_google_genai import ChatGoogleGenerativeAI
from ds.prompt.chat import SYSTEM_PROMPT
from security.config import GOOGLE_GENAI_API_KEY
from utills.build_and_update_vectorstore import build_or_update_vectorstore
from utills.extract_text_from_file import extract_text_from_file
from api.services.chat_history import (
    add_message, format_chat_history_for_prompt, get_chat_history,
    increment_query_count, should_trigger_quiz,
    add_difficulty
)
from api.services.difficulty_analyzer import analyze_difficulty
from typing import List, Dict, Optional
import json

async def upload_file_create_vectorstore(files, vectorstore):
    import security.config as config
    all_docs = []
    errors = []

    for file in files:
        try:
            docs = await extract_text_from_file(file)
            all_docs.extend(docs) # a = [1,2,3] , b = [4,5,6] => a.extend(b) => a = [1,2,3,4,5,6]
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")

    if not all_docs:
        raise HTTPException(
            status_code=400, 
            detail=f"No documents extracted. Errors: {errors}"
        )

    # This will update the global vectorstore in config
    config.vectorstore = build_or_update_vectorstore(all_docs)
    
    response = {"message": f"✅ {len(all_docs)} chunks added to vectorstore."}
    if errors:
        response["warnings"] = errors # type: ignore
    return response

def generate_questions_answers(question, skill_, vectorstore, chat_history: Optional[List[Dict[str, str]]] = None, session_id: str = "default"):
    # Analyze difficulty level of the question
    history_text = ""
    if chat_history:
        history_text = format_chat_history_for_prompt(chat_history)
    
    try:
        difficulty_analysis = analyze_difficulty(question, history_text)
        detected_difficulty = difficulty_analysis["difficulty"]
        add_difficulty(session_id, detected_difficulty)
    except Exception as e:
        # Fallback to requested skill level if analysis fails
        print(f"Difficulty analysis failed: {e}")
        detected_difficulty = skill_ if skill_ != "all" else "intermediate"
    
    # Get top K results
    try:
        results = vectorstore.similarity_search(question, k=3, filter={"skill": skill_} if skill_ != "all" else {})
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching vectorstore: {str(e)}"
        )

    print("Context : ",results)
    if not results:
        # No context found - the model will use its general programming knowledge
        context = "No relevant information found in the knowledge base. Use your general programming knowledge to answer this programming question."
    else:
        context = "\n\n".join([doc.page_content for doc in results])
    
    print("Chat History : ",history_text)
    if not GOOGLE_GENAI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Google API key is not configured. Please set GOOGLE_GENAI_API_KEY environment variable."
        )
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GOOGLE_GENAI_API_KEY,
        temperature=0.0
    )

    prompt = SYSTEM_PROMPT.format(
        skill=detected_difficulty,  # Use detected difficulty instead of requested skill
        question=question,
        context=context,
        chat_history=history_text
        )

    try:
        response = llm.invoke(prompt)
        raw = response.content
        # Ensure answer is always a string before storing in chat history
        if isinstance(raw, (list, dict)):
            try:
                answer = json.dumps(raw, ensure_ascii=False)
            except Exception:
                answer = str(raw)
        else:
            answer = str(raw)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating response: {str(e)}"
        )
    
    # Store messages in chat history (answer is guaranteed to be a string)
    add_message(session_id, "user", question)
    add_message(session_id, "assistant", answer)
    
    # Increment query count
    query_count = increment_query_count(session_id)
    
    # Get updated history
    updated_history = get_chat_history(session_id)
    
    # Check if quiz should be triggered
    quiz_prompt = None
    if should_trigger_quiz(session_id):
        quiz_prompt = "Would you like to take a quick quiz based on our conversation? (Yes/No)"
    
    response_data = {
        "question": question,
        "skill": detected_difficulty,
        "answer": answer,
        "context": results,
        "chat_history": updated_history,
        "query_count": query_count,
        "detected_difficulty": detected_difficulty
    }
    
    if quiz_prompt:
        response_data["quiz_prompt"] = quiz_prompt
    
    return response_data

