import os
import json
import pickle
import faiss

from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI

# Paths
FAISS_INDEX_PATH = "index.faiss"
PICKLE_PATH = "store.pkl"

# Embedding model (small, efficient)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def build_vectorstore():
    """Load dataset and build FAISS vectorstore."""
    with open("Tayyiba.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Wrap dataset as LangChain Documents
    docs = [
        Document(
            page_content=f"{item['instruction']} {item['output']}",
            metadata={"skill": item["skill"]}
        )
        for item in data
    ]

    # Create FAISS index
    vectorstore = FAISS.from_documents(docs, embeddings)

    # Save both FAISS + metadata
    vectorstore.save_local(".")

    with open(PICKLE_PATH, "wb") as f:
        pickle.dump(docs, f)

    print("✅ Vectorstore created and saved.")
    return vectorstore

def load_vectorstore():
    """Load existing FAISS vectorstore if available, else build new one."""
    if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(PICKLE_PATH):
        print("📂 Loading existing FAISS index...")
        vectorstore = FAISS.load_local(".", embeddings, allow_dangerous_deserialization=True)
        return vectorstore
    else:
        return build_vectorstore()

def query_system(question: str):
    """Retrieve context and pass into Gemini LLM for answer."""
    vectorstore = load_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    # Retrieve context
    context_docs = retriever.get_relevant_documents(question)
    context = "\n".join([doc.page_content for doc in context_docs])
    print("🔍 Retrieving relevant context...", context)
    # Call Gemini LLM via LangChain
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key="AIzaSyBfYxmpCKsEgdLBRNUezVMSGJyt4ElAbrc"
    )

    prompt = f"""You are a Python tutor. 
Only answer using the provided context about Python.

Question: {question}

Context:
{context}

Answer:"""

    return llm.invoke(prompt).content

# Interactive loop
if __name__ == "__main__":
    while True:
        q = input("\nAsk me about Python (type 'exit' to quit): ")
        if q.lower() == "exit":
            break
        print("\n📌 Answer:", query_system(q))
