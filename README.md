# Code Mentor AI - Streamlit UI

A beautiful web interface for the Code Mentor AI application built with Streamlit.

## Features

- 📁 **File Upload**: Upload JSON, CSV, PDF, or TXT files to build the knowledge base
- 💬 **Chat Interface**: Interactive chat with Code Mentor AI
- 🎯 **Skill Level Selection**: Choose from beginner, intermediate, advanced, or all
- 📊 **Statistics**: View vectorstore statistics
- 🗑️ **Clear History**: Clear chat history when needed
- 💻 **Beautiful UI**: Modern, responsive design

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure your FastAPI server is running:
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

3. Run the Streamlit app:
```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## Configuration

You can set the API base URL using an environment variable:
```bash
export API_BASE_URL=http://127.0.0.1:8000
```

Or modify the `API_BASE_URL` in `streamlit_app.py` directly.

## Usage

1. **Upload Files**: Use the sidebar to upload files (JSON, CSV, PDF, TXT) to build your knowledge base
2. **Select Skill Level**: Choose your programming skill level from the dropdown
3. **Start Chatting**: Type your programming questions in the chat input
4. **View History**: All your conversation history is displayed in the chat area
5. **Clear History**: Use the "Clear Chat History" button to start fresh

## Notes

- The app requires the FastAPI backend to be running
- Chat history is maintained per session
- Files are uploaded to the FastAPI backend for processing
- The UI automatically checks API connectivity on load

