import sys
import os

# Make `app` root importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.rag_loader import load_reports, split_documents
from memory.normalizer import normalize_documents
from memory.rag_retriever import RAGRetriever
from agents.reasoner import reason
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


def build_vector_store(docs):
    model = "sentence-transformers/all-MiniLM-L6-v2"
    embeddings = HuggingFaceEmbeddings(model_name=model)
    return FAISS.from_documents(docs, embeddings)


question = "What are NVIDIA's largest business risks?"

docs = split_documents(normalize_documents(load_reports()))
vector_store = build_vector_store(docs)
retriever = RAGRetriever(vector_store)

retrieved = retriever.retrieve(question, k=5)
answer = reason(question, retrieved)

print("\n💬 FINAL ANSWER:\n", answer)
