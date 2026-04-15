from langchain_google_genai import ChatGoogleGenerativeAI
from security.config import GOOGLE_GENAI_API_KEY
from fastapi import HTTPException
from typing import List, Dict
import json
import re

QUIZ_GENERATION_PROMPT = """
You are an expert programming quiz generator. Based on the conversation history below, generate a comprehensive quiz with multiple-choice questions (MCQs) to test the user's understanding.

Conversation History:
{chat_history}

Generate a quiz with {num_questions} multiple-choice questions based on the topics discussed in the conversation.

Guidelines:
- Questions should cover the main programming concepts discussed
- Each question should have 4 options (A, B, C, D)
- Only ONE option should be correct
- Include questions of varying difficulty based on the conversation topics
- Make questions practical and relevant to what was discussed
- Provide clear explanations for each answer

Output format (JSON only):
{{
    "quiz_title": "Brief title for the quiz",
    "questions": [
        {{
            "question": "Question text here",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "A" | "B" | "C" | "D",
            "explanation": "Brief explanation of why this is correct"
        }}
    ]
}}
"""


def generate_quiz_from_history(chat_history: List[Dict[str, str]], num_questions: int = 5) -> dict:
    """
    Generate a quiz based on conversation history.
    
    Args:
        chat_history: List of message dictionaries with "role" and "content"
        num_questions: Number of questions to generate (default: 5)
    
    Returns:
        dict with quiz_title and questions list
    """
    if not GOOGLE_GENAI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Google API key is not configured."
        )
    
    if not chat_history:
        raise HTTPException(
            status_code=400,
            detail="No conversation history available to generate quiz."
        )
    
    # Format chat history for prompt
    history_text = "\n".join([
        f"{msg.get('role', 'user').title()}: {msg.get('content', '')}"
        for msg in chat_history
    ])
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GOOGLE_GENAI_API_KEY,
        temperature=0.7
    )
    
    prompt = QUIZ_GENERATION_PROMPT.format(
        chat_history=history_text,
        num_questions=num_questions
    )
    
    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            # Clean up common JSON issues
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)
            
            result = json.loads(json_str)
            
            # Validate structure
            if "questions" not in result:
                raise ValueError("Quiz response missing 'questions' field")
            
            # Ensure all questions have required fields
            validated_questions = []
            for q in result.get("questions", []):
                if all(key in q for key in ["question", "options", "correct_answer"]):
                    validated_questions.append({
                        "question": q["question"],
                        "options": q["options"][:4],  # Ensure exactly 4 options
                        "correct_answer": q["correct_answer"].upper(),
                        "explanation": q.get("explanation", "No explanation provided.")
                    })
            
            if not validated_questions:
                raise ValueError("No valid questions generated")
            
            return {
                "quiz_title": result.get("quiz_title", "Programming Quiz"),
                "questions": validated_questions[:num_questions]  # Limit to requested number
            }
        else:
            raise ValueError("No JSON found in response")
            
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse quiz JSON: {str(e)}. Response: {content[:200]}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating quiz: {str(e)}"
        )

