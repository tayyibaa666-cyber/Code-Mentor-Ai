from langchain_google_genai import ChatGoogleGenerativeAI
from security.config import GOOGLE_GENAI_API_KEY
from fastapi import HTTPException
import json
import re

DIFFICULTY_PROMPT = """
Analyze the following programming question and determine its difficulty level.

Question: {question}

Previous conversation context (if any):
{chat_history}

Based on the question, classify it into ONE of these categories:
- "beginner": Basic syntax, simple concepts, "what is", "how do I start", fundamental questions
- "intermediate": Best practices, design patterns, optimization, moderate complexity, implementation details
- "advanced": Complex architectures, performance optimization, advanced patterns, system design, deep technical concepts

Consider:
- The complexity of concepts mentioned
- The depth of knowledge required
- Whether it's asking for basic understanding or advanced application
- The context from previous conversations

Respond with ONLY a JSON object in this exact format:
{{
    "difficulty": "beginner" | "intermediate" | "advanced",
    "reasoning": "Brief explanation of why this difficulty level was chosen"
}}
"""


def analyze_difficulty(question: str, chat_history: str = "") -> dict:
    """
    Analyze a programming question to determine its difficulty level.
    
    Args:
        question: The user's question
        chat_history: Previous conversation context (optional)
    
    Returns:
        dict with "difficulty" (beginner/intermediate/advanced) and "reasoning"
    """
    if not GOOGLE_GENAI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Google API key is not configured."
        )
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GOOGLE_GENAI_API_KEY,
        temperature=0.3
    )
    
    prompt = DIFFICULTY_PROMPT.format(
        question=question,
        chat_history=chat_history if chat_history else "No previous conversation."
    )
    
    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            result = json.loads(json_str)
            
            # Validate difficulty level
            difficulty = result.get("difficulty", "intermediate").lower()
            if difficulty not in ["beginner", "intermediate", "advanced"]:
                difficulty = "intermediate"
            
            return {
                "difficulty": difficulty,
                "reasoning": result.get("reasoning", "Difficulty analyzed based on question complexity.")
            }
        else:
            # Fallback: try to extract difficulty from text
            content_lower = content.lower()
            if "beginner" in content_lower:
                difficulty = "beginner"
            elif "advanced" in content_lower:
                difficulty = "advanced"
            else:
                difficulty = "intermediate"
            
            return {
                "difficulty": difficulty,
                "reasoning": content[:200] if len(content) > 200 else content
            }
            
    except json.JSONDecodeError:
        # Fallback analysis
        question_lower = question.lower()
        if any(word in question_lower for word in ["what is", "how do i start", "basic", "simple", "beginner"]):
            difficulty = "beginner"
        elif any(word in question_lower for word in ["optimize", "performance", "architecture", "system design", "advanced"]):
            difficulty = "advanced"
        else:
            difficulty = "intermediate"
        
        return {
            "difficulty": difficulty,
            "reasoning": "Fallback analysis based on keywords."
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing difficulty: {str(e)}"
        )

