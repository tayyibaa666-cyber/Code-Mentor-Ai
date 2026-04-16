from langchain_community.vectorstores import FAISS

from security.config import VECTOR_DB_DIR, FAISS_INDEX_PATH, embeddings
import os

def load_vectorstore() -> FAISS:
    """Safely load FAISS vectorstore from local files."""
    if os.path.exists(FAISS_INDEX_PATH):
        try:
            # Try loading with the newer API first
            vs = FAISS.load_local(
                folder_path=VECTOR_DB_DIR,
                embeddings=embeddings, 
                allow_dangerous_deserialization=True
            )
            return vs
        except TypeError:
            # Fallback for older langchain versions
            try:
                vs = FAISS.load_local(
                    VECTOR_DB_DIR,
                    embeddings, 
                    allow_dangerous_deserialization=True
                )
                return vs
            except Exception as e:
                raise RuntimeError(f"Failed to load FAISS index. Try re-uploading your data. Error: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Failed to load FAISS index. Try re-uploading your data. Error: {str(e)}")
    else:
        raise FileNotFoundError("Vectorstore not found. Please upload data first.")

