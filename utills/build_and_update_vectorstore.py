from security.config import VECTOR_DB_DIR, FAISS_INDEX_PATH, embeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import os
import security.config as config


def build_or_update_vectorstore(new_docs: list[Document]) -> FAISS:
    """Build or update FAISS vectorstore with new documents."""
    if config.vectorstore is not None:
        # Update existing vectorstore
        config.vectorstore.add_documents(new_docs)
    elif os.path.exists(FAISS_INDEX_PATH):
        # Load existing FAISS and add documents
        config.vectorstore = FAISS.load_local(
            VECTOR_DB_DIR, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        config.vectorstore.add_documents(new_docs)
    else:
        # Create new FAISS index
        config.vectorstore = FAISS.from_documents(new_docs, embeddings)

    # Save updated FAISS
    config.vectorstore.save_local(VECTOR_DB_DIR)

    return config.vectorstore
