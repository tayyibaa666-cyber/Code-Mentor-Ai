from langchain_community.document_loaders import PDFPlumberLoader
from fastapi import UploadFile
from langchain_core.documents import Document
import json
import pandas as pd
from security.config import text_splitter
import os

async def extract_text_from_file(file: UploadFile) -> list[Document]:
    """Extract text and return as LangChain Documents with metadata."""
    filename = file.filename.lower() if file.filename else ""
    docs = []

    if filename.endswith(".json"):
        content = await file.read()
        data = json.loads(content)
        for item in data:
            instruction = item.get('instruction', '')
            output = item.get('output', '')
            skill = item.get('skill', 'unknown')
            docs.append(
                Document(
                    page_content=f"{instruction} {output}".strip(),
                    metadata={"skill": f"{skill}".lower().strip(), "source": file.filename}
                )
            )

    elif filename.endswith(".csv"):
        content = await file.read()
        df = pd.read_csv(pd.io.common.BytesIO(content)) # type: ignore
        for _, row in df.iterrows():
            skill = row.get("skill", "unknown") if "skill" in row else "unknown"
            docs.append(
                Document(
                    page_content=" ".join(map(str, row.values)),
                    metadata={"skill": skill, "source": file.filename}
                )
            )

    elif filename.endswith(".txt"):
        content = await file.read()
        text = content.decode("utf-8")
        chunks = text_splitter.split_text(text)
        docs.extend([
            Document(
                page_content=chunk, 
                metadata={"skill": "unknown", "source": file.filename}
            ) 
            for chunk in chunks
        ])

    elif filename.endswith(".pdf"):
        temp_path = f"temp_{file.filename}"
        try:
            content = await file.read()
          
            with open(temp_path, "wb") as f:
                f.write(content)
           
         
            loader = PDFPlumberLoader(temp_path)
          
            raw_docs = loader.load()
            
            for d in raw_docs:
                chunks = text_splitter.split_text(d.page_content)
               
                for chunk in chunks:
                   
                    docs.append(
                        Document(
                            page_content=chunk, 
                            metadata={"skill": "unknown", "source": file.filename}
                        )
                    )
            
        except Exception as e:
            print(f"error :{e}")
        finally:
           if os.path.exists(temp_path):
              os.remove(temp_path)
            
    else:
        raise ValueError("Unsupported file format. Only JSON, CSV, TXT, and PDF allowed.")

    return docs
