from typing import List, Dict
from collections import defaultdict

# In-memory storage for chat history
# Format: {session_id: [{"role": "user", "content": "question"}, {"role": "assistant", "content": "answer"}, ...]}
_chat_history: Dict[str, List[Dict[str, str]]] = defaultdict(list)

# Track query counts and difficulty levels per session
_query_counts: Dict[str, int] = defaultdict(int)
_difficulty_tracking: Dict[str, List[str]] = defaultdict(list)

# Maximum number of messages to keep per session (10 messages = 5 user + 5 assistant)
MAX_HISTORY_MESSAGES = 10

# Quiz trigger settings
QUIZ_TRIGGER_MIN = 6
QUIZ_TRIGGER_MAX = 8


def get_chat_history(session_id: str = "default") -> List[Dict[str, str]]:
    """Get chat history for a session."""
    return _chat_history[session_id][-MAX_HISTORY_MESSAGES:]


def add_message(session_id: str, role: str, content: str) -> None:
    """
    Add a message to chat history.
    
    Args:
        session_id: Session identifier
        role: "user" or "assistant"
        content: Message content
    """
    _chat_history[session_id].append({"role": role, "content": content})
    
    # Keep only last MAX_HISTORY_MESSAGES
    if len(_chat_history[session_id]) > MAX_HISTORY_MESSAGES:
        _chat_history[session_id] = _chat_history[session_id][-MAX_HISTORY_MESSAGES:]


def clear_chat_history(session_id: str = "default") -> None:
    """Clear chat history for a session."""
    _chat_history[session_id] = []


def format_chat_history_for_prompt(history: List[Dict[str, str]]) -> str:
    """
    Format chat history for inclusion in the prompt.
    
    Args:
        history: List of message dictionaries with "role" and "content"
    
    Returns:
        Formatted string of chat history
    """
    if not history:
        return "No previous conversation history."
    
    formatted = []
    for msg in history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            formatted.append(f"User: {content}")
        elif role == "assistant":
            formatted.append(f"Assistant: {content}")
    
    return "\n".join(formatted)


def increment_query_count(session_id: str) -> int:
    """Increment and return the query count for a session."""
    _query_counts[session_id] += 1
    return _query_counts[session_id]


def get_query_count(session_id: str) -> int:
    """Get the current query count for a session."""
    return _query_counts[session_id]


def reset_query_count(session_id: str) -> None:
    """Reset query count for a session."""
    _query_counts[session_id] = 0


def add_difficulty(session_id: str, difficulty: str) -> None:
    """Track difficulty level for a session."""
    _difficulty_tracking[session_id].append(difficulty)
    # Keep only last 10 difficulty levels
    if len(_difficulty_tracking[session_id]) > 10:
        _difficulty_tracking[session_id] = _difficulty_tracking[session_id][-10:]


def get_difficulty_history(session_id: str) -> List[str]:
    """Get difficulty history for a session."""
    return _difficulty_tracking[session_id]


def should_trigger_quiz(session_id: str) -> bool:
    """Check if quiz should be triggered based on query count."""
    count = get_query_count(session_id)
    return QUIZ_TRIGGER_MIN <= count <= QUIZ_TRIGGER_MAX

