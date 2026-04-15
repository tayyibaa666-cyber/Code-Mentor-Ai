# Quiz Feature Implementation

## Overview

This implementation adds automatic difficulty analysis and quiz generation features to the Code Mentor AI application.

## Features Implemented

### 1. **Automatic Difficulty Analysis**
- Every user question is analyzed using Gemini to determine its difficulty level (beginner/intermediate/advanced)
- The detected difficulty is used to tailor the response style
- Difficulty levels are tracked per session

### 2. **Quiz Trigger System**
- After 6-8 queries, the system automatically prompts the user: "Would you like to take a quick quiz based on our conversation? (Yes/No)"
- The quiz prompt appears in the chat interface
- Users can choose to take the quiz or skip it

### 3. **Quiz Generation**
- If the user chooses "Yes", a quiz is generated using Gemini based on the conversation history
- The quiz includes multiple-choice questions (MCQs) covering topics discussed
- Each question has 4 options with one correct answer
- Explanations are provided for each question

### 4. **Quiz UI in Streamlit**
- Interactive quiz display with radio buttons for each question
- Submit button to check answers
- Score calculation and detailed results
- Expandable explanations for each question

## Files Created/Modified

### New Files:
1. **`api/services/difficulty_analyzer.py`**
   - Analyzes question difficulty using Gemini
   - Returns difficulty level and reasoning

2. **`api/services/quiz_generator.py`**
   - Generates quizzes from conversation history
   - Creates MCQs with explanations

### Modified Files:
1. **`api/services/chat_history.py`**
   - Added query count tracking
   - Added difficulty tracking
   - Added quiz trigger logic

2. **`api/services/chat.py`**
   - Integrated difficulty analysis
   - Added quiz prompt triggering
   - Returns detected difficulty and query count

3. **`api/chat.py`**
   - Added `/chat/generate-quiz` endpoint
   - Updated clear endpoint to reset query count

4. **`streamlit_app.py`**
   - Added quiz display section
   - Added quiz generation UI
   - Added quiz submission and scoring

## API Endpoints

### New Endpoint:
- **POST `/video/chat/generate-quiz`**
  - Parameters:
    - `session_id` (optional, default: "default")
    - `num_questions` (optional, default: 5)
  - Returns: Quiz with title and questions array

### Updated Response:
The `/video/chat` endpoint now returns:
- `detected_difficulty`: Automatically detected difficulty level
- `query_count`: Current number of queries in the session
- `quiz_prompt`: Quiz prompt message (if query count is 6-8)

## Usage Flow

1. **User asks questions** → System analyzes difficulty → Responds appropriately
2. **After 6-8 queries** → System shows quiz prompt
3. **User clicks "Yes"** → Quiz is generated from conversation history
4. **User takes quiz** → Answers questions → Submits → Sees score and explanations
5. **User can continue chatting** or reset quiz view

## Configuration

Quiz trigger settings in `api/services/chat_history.py`:
```python
QUIZ_TRIGGER_MIN = 6  # Minimum queries before quiz prompt
QUIZ_TRIGGER_MAX = 8  # Maximum queries before quiz prompt
```

## Technical Details

- **Difficulty Analysis**: Uses Gemini 2.5 Flash with temperature 0.3
- **Quiz Generation**: Uses Gemini 2.5 Flash with temperature 0.7 for creativity
- **Quiz Format**: JSON with questions, options, correct_answer, and explanation
- **Session Management**: All tracking is per session_id

## Example Quiz Response

```json
{
  "quiz_title": "Python Programming Quiz",
  "questions": [
    {
      "question": "What is the primary use of Python?",
      "options": ["Web development", "Data science", "Game development", "All of the above"],
      "correct_answer": "D",
      "explanation": "Python is versatile and used in all these areas."
    }
  ]
}
```

## Notes

- Quiz generation requires conversation history
- Difficulty analysis happens for every question
- Quiz questions are based on actual conversation topics
- All features use Gemini (not Groq) as requested

