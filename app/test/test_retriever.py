# test/test_retriever.py
import sys
import os

# Make `app` root importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from memory.rag_loader import load_reports, split_documents
from memory.normalizer import normalize_documents
from memory.rag_retriever import RAGRetriever
from memory.rag_vectorstore import get_vectorstore

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings  # or your embedding model
from langchain_huggingface import HuggingFaceEmbeddings


def build_vector_store(docs):
    model = "sentence-transformers/all-MiniLM-L6-v2"
    embeddings = HuggingFaceEmbeddings(model_name=model)
    return FAISS.from_documents(docs, embeddings)


def main():
    print("📌 Loading docs...")
    docs = load_reports()
    docs = normalize_documents(docs)
    chunks = split_documents(docs)

    print(f"Loaded {len(chunks)} chunks into memory.")

    print("📌 Building vector store (first time)...")
    vector_store = build_vector_store(chunks)

    retriever = RAGRetriever(vector_store)

    query = "What are NVIDIA's main business risks?"
    print(f"\n🔎 Query: {query}")

    retrieved = retriever.retrieve(query, k=5)

    print(f"\nTop {len(retrieved)} retrieved chunks:\n")
    for d in retrieved:
        print("📄", d.metadata)
        print(d.page_content[:220], "\n")


if __name__ == "__main__":
    main()
