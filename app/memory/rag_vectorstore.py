# app/memory/rag_vectorstore.py
from pathlib import Path
from typing import Optional

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from .rag_loader import load_reports, split_documents


BASE_DIR = Path(__file__).resolve().parents[1]
INDEX_DIR = BASE_DIR / "memory" / "faiss_index"

# Local, free embedding model
_embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def _build_vectorstore() -> Optional[FAISS]:
    """
    Load docs from disk, chunk them, create FAISS index, and persist it.
    """
    docs = load_reports()
    if not docs:
        print("[RAG] No documents found in app/data/reports")
        return None

    chunks = split_documents(docs)
    if not chunks:
        print("[RAG] No chunks created from documents")
        return None

    vs = FAISS.from_documents(chunks, _embeddings)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    vs.save_local(str(INDEX_DIR))
    print(f"[RAG] Built and saved FAISS index at {INDEX_DIR}")
    return vs


def get_vectorstore(rebuild: bool = False) -> Optional[FAISS]:
    """
    Load existing FAISS index if present, otherwise build it.
    """
    if rebuild:
        return _build_vectorstore()

    if INDEX_DIR.exists():
        try:
            vs = FAISS.load_local(
                str(INDEX_DIR),
                _embeddings,
                allow_dangerous_deserialization=True,
            )
            return vs
        except Exception:
            print("[RAG] Failed to load existing FAISS index, rebuilding...")
            return _build_vectorstore()

    return _build_vectorstore()
