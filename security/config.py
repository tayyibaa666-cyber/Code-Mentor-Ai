import os
import logging
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import FAISS
from typing import Optional
# Suppress gRPC ALTS warnings (harmless warnings from Google's libraries)
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

# Suppress specific gRPC loggers
logging.getLogger("google.auth").setLevel(logging.ERROR)
logging.getLogger("google.auth.transport.grpc").setLevel(logging.ERROR)
logging.getLogger("google.auth.transport.requests").setLevel(logging.ERROR)

# Load environment variables from .env file
load_dotenv()

# ============ CONFIGURATION ============
VECTOR_DB_DIR = "vectordb"
FAISS_INDEX_PATH = os.path.join(VECTOR_DB_DIR, "index.faiss")
METADATA_PATH = os.path.join(VECTOR_DB_DIR, "metadata.pkl")

# Ensure folder exists
os.makedirs(VECTOR_DB_DIR, exist_ok=True)

# Embedding model
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Text splitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=350, chunk_overlap=80)

# Global FAISS store variable
vectorstore: Optional[FAISS] = None

# Gemini Api Key
GOOGLE_GENAI_API_KEY = os.getenv("GOOGLE_GENAI_API_KEY", "")

# Warn if API key is not set (but don't fail at import time)
if not GOOGLE_GENAI_API_KEY:
    import warnings
    warnings.warn(
        "GOOGLE_GENAI_API_KEY environment variable is not set. "
        "Please set it in your environment or create a .env file with: GOOGLE_GENAI_API_KEY=your_api_key_here",
        UserWarning
    )
