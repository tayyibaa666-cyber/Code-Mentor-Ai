from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from security.config import VECTOR_DB_DIR
from utills.load_vectorstore import load_vectorstore
from api.chat import router as chat_router
import security.config as config
import os
import logging

# Suppress gRPC ALTS warnings (harmless warnings from Google's libraries)
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

# Suppress specific gRPC logger
logging.getLogger("google.auth").setLevel(logging.ERROR)
logging.getLogger("google.auth.transport.grpc").setLevel(logging.ERROR)
logging.getLogger("google.auth.transport.requests").setLevel(logging.ERROR)

# ============================================================
#               FASTAPI APP SETUP
# ============================================================

app = FastAPI(title="Code Mentor AI")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (can be restricted in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# ============================================================
#               HELPER FUNCTIONS
# ============================================================




# def filter_docs_by_skill(docs: List[Document], skill: str) -> List[Document]:
#     """Filter documents by skill level from metadata."""
#     skill_normalized = skill.lower().strip()
#     return [doc for doc in docs if doc.metadata.get("skill", "").lower().strip() == skill_normalized]


# ============================================================
#               APP STARTUP EVENT
# ============================================================

@app.on_event("startup")
async def load_faiss_on_startup():
    """Load FAISS index into memory at startup."""
    try:
        config.vectorstore = load_vectorstore()
        print("✅ FAISS vectorstore loaded successfully on startup.")
    except FileNotFoundError:
        print("⚠️ No existing FAISS index found. Upload data first.")
        config.vectorstore = None
    except Exception as e:
        print(f"❌ Error loading vectorstore: {str(e)}")
        config.vectorstore = None


# ============================================================
#               API ENDPOINTS
# ============================================================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "vectorstore_loaded": config.vectorstore is not None,
        "message": "Python Tutor API is running"
    }




@app.get("/stats")
async def get_stats():
    """Get statistics about the vectorstore."""
    if config.vectorstore is None:
        raise HTTPException(
            status_code=503,
            detail="Vectorstore not loaded"
        )
    
    return {
        "total_documents": config.vectorstore.index.ntotal,
        "vector_dimension": config.vectorstore.index.d,
        "storage_path": VECTOR_DB_DIR
    }


app.include_router(chat_router)

# Mount public folder for serving quiz files
PUBLIC_FOLDER = "public"
os.makedirs(PUBLIC_FOLDER, exist_ok=True)
os.makedirs(os.path.join(PUBLIC_FOLDER, "quizzes"), exist_ok=True)

try:
    app.mount("/public", StaticFiles(directory=PUBLIC_FOLDER), name="public")
except Exception as e:
    print(f"Warning: Could not mount static files: {e}")

# ============================================================
#               RUN COMMAND
# ============================================================
# Run using: uvicorn main:app --reload --host 127.0.0.1 --port 8000