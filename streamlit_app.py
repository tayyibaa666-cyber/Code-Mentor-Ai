import streamlit as st
import requests
import os
import json
import time
from typing import List, Dict

# Page configuration
st.set_page_config(
    page_title="Code Mentor AI",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
UPLOAD_ENDPOINT = f"{API_BASE_URL}/video/upload"
CHAT_ENDPOINT = f"{API_BASE_URL}/video/chat"
CLEAR_ENDPOINT = f"{API_BASE_URL}/video/chat/clear"
QUIZ_ENDPOINT = f"{API_BASE_URL}/video/chat/generate-quiz"
STATS_ENDPOINT = f"{API_BASE_URL}/stats"

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: #f5f5f5;
        margin-right: 20%;
    }
    .stButton>button {
        width: 100%;
        border-radius: 0.5rem;
    }
    .uploaded-file {
        padding: 0.5rem;
        background-color: #e8f5e9;
        border-radius: 0.3rem;
        margin: 0.3rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{int(time.time())}"
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "show_quiz" not in st.session_state:
    st.session_state.show_quiz = False
if "pending_quiz" not in st.session_state:
    st.session_state.pending_quiz = None
if "show_quiz_prompt" not in st.session_state:
    st.session_state.show_quiz_prompt = False
if "quiz_prompt_message_id" not in st.session_state:
    st.session_state.quiz_prompt_message_id = None


def check_api_connection() -> bool:
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def upload_files(files: List) -> Dict:
    """Upload files to the API"""
    try:
        files_data = []
        for file in files:
            files_data.append(("files", (file.name, file.getvalue(), file.type)))
        
        response = requests.post(UPLOAD_ENDPOINT, files=files_data, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to API. Please make sure the FastAPI server is running on " + API_BASE_URL}
    except Exception as e:
        return {"error": str(e)}


def send_chat_message(question: str, skill: str, session_id: str) -> Dict:
    """Send chat message to the API"""
    try:
        data = {
            "question": question,
            "skill": skill,
            "session_id": session_id
        }
        response = requests.post(CHAT_ENDPOINT, data=data, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to API. Please make sure the FastAPI server is running on " + API_BASE_URL}
    except Exception as e:
        return {"error": str(e)}


def clear_chat_history(session_id: str) -> Dict:
    """Clear chat history"""
    try:
        data = {"session_id": session_id}
        response = requests.post(CLEAR_ENDPOINT, data=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to API. Please make sure the FastAPI server is running."}
    except Exception as e:
        return {"error": str(e)}


def get_stats() -> Dict:
    """Get vectorstore statistics"""
    try:
        response = requests.get(STATS_ENDPOINT)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def generate_quiz(session_id: str, num_questions: int = 5) -> Dict:
    """Generate quiz from conversation history"""
    try:
        data = {
            "session_id": session_id,
            "num_questions": num_questions
        }
        print(f"Calling quiz endpoint: {QUIZ_ENDPOINT}")
        print(f"Request data: {data}")
        response = requests.post(QUIZ_ENDPOINT, data=data, timeout=60)
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text[:500]}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError as e:
        error_msg = f"Cannot connect to API at {QUIZ_ENDPOINT}. Please make sure the FastAPI server is running."
        print(f"Connection error: {e}")
        return {"error": error_msg}
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP error: {e}. Response: {response.text if 'response' in locals() else 'No response'}"
        print(f"HTTP error: {error_msg}")
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"Error generating quiz: {str(e)}"
        print(f"Exception: {error_msg}")
        import traceback
        print(traceback.format_exc())
        return {"error": error_msg}


# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    
    # Skill level selection
    skill_level = st.selectbox(
        "Skill Level",
        ["all", "beginner", "intermediate", "advanced"],
        index=0,
        help="Select your programming skill level"
    )
    
    st.markdown("---")
    
    # File upload section
    st.markdown("## 📁 Upload Files")
    st.markdown("Upload JSON, CSV, PDF, or TXT files to build the knowledge base")
    
    uploaded_files = st.file_uploader(
        "Choose files",
        type=["json", "csv", "pdf", "txt"],
        accept_multiple_files=True,
        help="Supported formats: JSON, CSV, PDF, TXT"
    )
    
    if st.button("📤 Upload Files", type="primary"):
        if uploaded_files:
            with st.spinner("Uploading files..."):
                result = upload_files(uploaded_files)
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.success(result.get("message", "Files uploaded successfully!"))
                    if "warnings" in result:
                        for warning in result["warnings"]:
                            st.warning(warning)
                    # Store uploaded file names
                    for file in uploaded_files:
                        if file.name not in st.session_state.uploaded_files:
                            st.session_state.uploaded_files.append(file.name)
                    st.rerun()
        else:
            st.warning("Please select files to upload")
    
    # Show uploaded files
    if st.session_state.uploaded_files:
        st.markdown("---")
        st.markdown("### Uploaded Files")
        for file_name in st.session_state.uploaded_files:
            st.markdown(f'<div class="uploaded-file">📄 {file_name}</div>', unsafe_allow_html=True)
    
    # Stats section
    st.markdown("---")
    st.markdown("## 📊 Statistics")
    if st.button("🔄 Refresh Stats"):
        stats = get_stats()
        if "error" not in stats:
            st.metric("Total Documents", stats.get("total_documents", 0))
            st.metric("Vector Dimension", stats.get("vector_dimension", 0))
        else:
            st.info("No vectorstore loaded yet")
    
    # Clear chat button
    st.markdown("---")
    if st.button("🗑️ Clear Chat History", type="secondary"):
        result = clear_chat_history(st.session_state.session_id)
        if "error" not in result:
            st.session_state.messages = []
            st.success("Chat history cleared!")
            st.rerun()


# Check API connection
if not check_api_connection():
    st.error(f"⚠️ Cannot connect to API at {API_BASE_URL}. Please make sure the FastAPI server is running.")
    st.info("To start the API server, run: `uvicorn main:app --reload --host 127.0.0.1 --port 8000`")
    st.stop()

# Main content area
st.markdown('<h1 class="main-header">💻 Code Mentor AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Your friendly programming assistant - Ask me anything about coding!</p>', unsafe_allow_html=True)

# Display chat messages
chat_container = st.container()
with chat_container:
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "skill" in message:
                st.caption(f"Skill Level: {message['skill']}")
            
            # Check if this message has an associated quiz
            if message.get("type") == "quiz" and "quiz_data" in message:
                quiz_data = message["quiz_data"]
                st.markdown("---")
                st.markdown(f"### 📝 {quiz_data.get('quiz_title', 'Programming Quiz')}")
                st.markdown(f"**{len(quiz_data.get('questions', []))} questions generated**")
                
                # Check if DOCX files are already generated (stored in quiz_data)
                if "docx_student" in quiz_data and "docx_answers" in quiz_data:
                    # Use pre-generated DOCX files
                    docx_student = quiz_data["docx_student"]
                    docx_answers = quiz_data["docx_answers"]
                else:
                    # Generate DOCX files on the fly
                    try:
                        from utills.generate_quiz_docx import create_quiz_docx, create_quiz_docx_student_version
                        docx_student, docx_student_path = create_quiz_docx_student_version(
                            quiz_data, 
                            session_id=st.session_state.session_id,
                            save_to_disk=True
                        )
                        docx_answers, docx_answers_path = create_quiz_docx(
                            quiz_data,
                            session_id=st.session_state.session_id,
                            save_to_disk=True
                        )
                        # Update quiz_data with paths
                        quiz_data["docx_student_path"] = docx_student_path
                        quiz_data["docx_answers_path"] = docx_answers_path
                        if docx_student_path:
                            quiz_data["docx_student_filename"] = os.path.basename(docx_student_path)
                        if docx_answers_path:
                            quiz_data["docx_answers_filename"] = os.path.basename(docx_answers_path)
                    except Exception as e:
                        st.error(f"Error generating DOCX: {str(e)}")
                        docx_student = None
                        docx_answers = None
                
                # Download buttons
                if docx_student and docx_answers:
                    col1, col2 = st.columns(2)
                    
                    # Get filenames if available
                    student_filename = quiz_data.get("docx_student_filename", f"quiz_{st.session_state.session_id}_{idx}.docx")
                    answers_filename = quiz_data.get("docx_answers_filename", f"quiz_answers_{st.session_state.session_id}_{idx}.docx")
                    
                    with col1:
                        st.download_button(
                            label="📄 Download Quiz (DOCX)",
                            data=docx_student,
                            file_name=student_filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key=f"download_quiz_docx_{idx}",
                            help="Student version without answers",
                            type="primary"
                        )
                        # Show file path and direct link if available
                        if quiz_data.get("docx_student_path"):
                            file_path = quiz_data['docx_student_path']
                            st.caption(f"📁 Saved: {file_path}")
                            # Direct link to file via API
                            if quiz_data.get("docx_student_filename"):
                                file_url = f"{API_BASE_URL}/public/quizzes/{quiz_data['docx_student_filename']}"
                                st.markdown(f"🔗 [Direct Link]({file_url})")
                    
                    with col2:
                        st.download_button(
                            label="📄 Download Answer Key (DOCX)",
                            data=docx_answers,
                            file_name=answers_filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key=f"download_quiz_answers_{idx}",
                            help="Teacher version with answers"
                        )
                        # Show file path and direct link if available
                        if quiz_data.get("docx_answers_path"):
                            file_path = quiz_data['docx_answers_path']
                            st.caption(f"📁 Saved: {file_path}")
                            # Direct link to file via API
                            if quiz_data.get("docx_answers_filename"):
                                file_url = f"{API_BASE_URL}/public/quizzes/{quiz_data['docx_answers_filename']}"
                                st.markdown(f"🔗 [Direct Link]({file_url})")
                else:
                    # Fallback to JSON if DOCX generation failed
                    quiz_json = json.dumps(quiz_data, indent=2, ensure_ascii=False)
                    quiz_bytes = quiz_json.encode('utf-8')
                    st.download_button(
                        label="📥 Download Quiz (JSON)",
                        data=quiz_bytes,
                        file_name=f"quiz_{st.session_state.session_id}_{idx}.json",
                        mime="application/json",
                        key=f"download_quiz_{idx}"
                    )
                    st.warning("DOCX generation failed. JSON file available instead.")
                
                # Show preview of questions
                with st.expander("📋 Preview Quiz Questions"):
                    for i, q in enumerate(quiz_data.get("questions", [])[:3], 1):
                        st.markdown(f"**Q{i}:** {q.get('question', '')}")
                        st.markdown(f"*Correct Answer: {q.get('correct_answer', 'N/A')}*")
                    if len(quiz_data.get("questions", [])) > 3:
                        st.caption(f"... and {len(quiz_data.get('questions', [])) - 3} more questions")

# Chat input
if prompt := st.chat_input("Ask me a programming question..."):
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "skill": skill_level
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
        st.caption(f"Skill Level: {skill_level}")
    
    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = send_chat_message(prompt, skill_level, st.session_state.session_id)
            
            if "error" in response:
                st.error(f"Error: {response['error']}")
            else:
                answer = response.get("answer", "No response received")
                st.markdown(answer)
                
                # Show detected difficulty and query count
                detected_skill = response.get("detected_difficulty", response.get("skill", skill_level))
                query_count = response.get("query_count", 0)
                st.caption(f"Detected Level: {detected_skill} | Queries: {query_count}")
                
                # Check for quiz prompt
                if "quiz_prompt" in response:
                    st.session_state.show_quiz_prompt = True
                    st.session_state.quiz_prompt_message_id = len(st.session_state.messages)
                    st.info(f"💡 {response['quiz_prompt']}")
                
                # Add assistant message to chat
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "skill": detected_skill
                })

# Handle quiz prompt buttons (outside chat input handler so they persist)
if st.session_state.show_quiz_prompt:
    st.markdown("---")
    st.info("💡 Would you like to take a quick quiz based on our conversation?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Yes, generate quiz", key="quiz_yes_button", type="primary"):
            st.session_state.show_quiz_prompt = False
            with st.spinner("Generating quiz and creating DOCX file..."):
                print(f"🔵 Button clicked! Calling quiz endpoint: {QUIZ_ENDPOINT}")
                print(f"🔵 Session ID: {st.session_state.session_id}")
                
                quiz_result = generate_quiz(st.session_state.session_id, num_questions=5)
                
                print(f"🔵 Quiz result received: {type(quiz_result)}")
                if isinstance(quiz_result, dict):
                    print(f"🔵 Quiz result keys: {list(quiz_result.keys())}")
                
                # Check for errors first
                if "error" in quiz_result:
                    st.error(f"❌ Error: {quiz_result['error']}")
                    st.stop()
                
                # Verify we got quiz data
                if not isinstance(quiz_result, dict) or "questions" not in quiz_result:
                    st.error(f"❌ Unexpected response format: {quiz_result}")
                    st.stop()
                
                # Generate DOCX file immediately and save to public folder
                try:
                    from utills.generate_quiz_docx import create_quiz_docx, create_quiz_docx_student_version
                    docx_student_bytes, docx_student_path = create_quiz_docx_student_version(
                        quiz_result, 
                        session_id=st.session_state.session_id,
                        save_to_disk=True
                    )
                    docx_answers_bytes, docx_answers_path = create_quiz_docx(
                        quiz_result,
                        session_id=st.session_state.session_id,
                        save_to_disk=True
                    )
                    
                    # Store quiz with DOCX files (both bytes and paths)
                    quiz_result["docx_student"] = docx_student_bytes
                    quiz_result["docx_answers"] = docx_answers_bytes
                    quiz_result["docx_student_path"] = docx_student_path
                    quiz_result["docx_answers_path"] = docx_answers_path
                    
                    # Extract just the filename for URL
                    if docx_student_path:
                        quiz_result["docx_student_filename"] = os.path.basename(docx_student_path)
                    if docx_answers_path:
                        quiz_result["docx_answers_filename"] = os.path.basename(docx_answers_path)
                    
                    st.session_state.pending_quiz = quiz_result
                    st.success("Quiz generated and saved successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating DOCX: {str(e)}")
                    import traceback
                    st.error(traceback.format_exc())
                    # Still store quiz data even if DOCX fails
                    st.session_state.pending_quiz = quiz_result
                    st.rerun()
    with col2:
        if st.button("❌ No, skip", key="quiz_no_button"):
            st.session_state.show_quiz_prompt = False
            st.info("Quiz skipped. Continue chatting!")
            st.rerun()

# Handle pending quiz - add it as a chat message
if st.session_state.pending_quiz:
    # Add quiz as an assistant message in chat
    quiz_data = st.session_state.pending_quiz
    quiz_title = quiz_data.get('quiz_title', 'Programming Quiz')
    num_questions = len(quiz_data.get('questions', []))
    
    quiz_message = {
        "role": "assistant",
        "content": f"📝 I've generated a quiz for you: **{quiz_title}** ({num_questions} questions). Click the download button below to get the DOCX file!",
        "type": "quiz",
        "quiz_data": quiz_data
    }
    st.session_state.messages.append(quiz_message)
    st.session_state.pending_quiz = None
    st.rerun()


# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>Code Mentor AI - Your friendly programming assistant</p>
        <p>Powered by FastAPI & Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)

