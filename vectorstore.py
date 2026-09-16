import os
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from db import get_db_conn
from settings import get_settings

DATA_DIR = "data"
DB_FAISS_PATH = "vectorstore/db_faiss"

def build_faiss_from_pdfs(user_id=None):
    
    conn = get_db_conn()
    cur = conn.cursor()
    if user_id:
        cur.execute("SELECT filepath FROM pdfs WHERE user_id=?", (user_id,))
    else:
        cur.execute("SELECT filepath FROM pdfs")
    rows = cur.fetchall()
    conn.close()
    pdf_paths = [r["filepath"] for r in rows]
    if not pdf_paths:
        return False, "No PDFs found to build vectorstore."
   
    docs = []
    for p in pdf_paths:
        if os.path.exists(p):
            loader = PyPDFLoader(p)
            docs.extend(loader.load())
    settings = get_settings()
    chunk_size = settings["chunk_size"]
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=50)
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        
        encode_kwargs={
            "device": "cpu"  
        }
    )
    db = FAISS.from_documents(docs, embedding_model)
    os.makedirs(os.path.dirname(DB_FAISS_PATH), exist_ok=True)
    db.save_local(DB_FAISS_PATH)
    return True, f"FAISS built with {len(docs)} chunks."

def load_vectorstore():
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        
        encode_kwargs={
            "device": "cpu"
        }
    )
    return FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)