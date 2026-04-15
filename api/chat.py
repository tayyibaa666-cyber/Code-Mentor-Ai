from fastapi import Form, HTTPException, UploadFile, File
from fastapi import APIRouter
from enums.skill import SkillLevel
from typing import Optional
import security.config as config
from api.services.chat import generate_questions_answers, upload_file_create_vectorstore
from api.services.chat_history import get_chat_history, clear_chat_history, reset_query_count
from api.services.quiz_generator import generate_quiz_from_history


router = APIRouter(prefix="/video", tags=["Video Generation"])



@router.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    """
    Upload JSON, CSV, PDF, or TXT files and build/update FAISS vectorstore.
    PDFs and TXTs are chunked into ~350 token segments (80 overlap).
    """
    response = await upload_file_create_vectorstore(files, config.vectorstore)
    return response



@router.post("/chat")
async def chat(
    question: str = Form(...),
    skill: SkillLevel = Form(SkillLevel.all),
    session_id: str = Form("default")
):
    """
    Generate chat response based on skill level (beginner/intermediate/advanced/all).
    Maintains chat history for the last 10 messages per session.
    """
    skill_ = skill.lower().strip()
    if skill_ not in ["beginner", "intermediate", "advanced", "all"]:
        raise HTTPException(
            status_code=400, 
            detail="Invalid skill level. Choose from: beginner, intermediate, advanced, all."
        )
    if config.vectorstore is None:
        raise HTTPException(
            status_code=503, 
            detail="Vectorstore not loaded. Please upload data first."
        )
    
    # Get chat history for this session
    history = get_chat_history(session_id)
    
    # Generate response with chat history
    response = generate_questions_answers(question, skill_, config.vectorstore, history, session_id)

    return response


@router.post("/chat/clear")
async def clear_chat(session_id: str = Form("default")):
    """
    Clear chat history for a session.
    """
    clear_chat_history(session_id)
    reset_query_count(session_id)
    return {"message": f"Chat history cleared for session: {session_id}"}


@router.post("/chat/generate-quiz")
async def generate_quiz_endpoint(
    session_id: str = Form("default"),
    num_questions: Optional[int] = Form(5)
):
    """
    Generate a quiz based on conversation history.
    """
    print(f"✅ Quiz generation endpoint hit! Session: {session_id}, Questions: {num_questions}")
    history = get_chat_history(session_id)
    print(f"Chat history length: {len(history)}")
    
    if not history:
        print("⚠️ No chat history found")
        raise HTTPException(
            status_code=400,
            detail="No conversation history available. Please chat first before generating a quiz."
        )
    
    try:
        print("🔄 Generating quiz from history...")
        quiz = generate_quiz_from_history(history, num_questions)
        print(f"✅ Quiz generated successfully! Questions: {len(quiz.get('questions', []))}")
        return quiz
    except Exception as e:
        print(f"❌ Error generating quiz: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error generating quiz: {str(e)}"
        )
