import sys
import os

# Make `app` root importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.rag_loader import load_reports, split_documents
from memory.normalizer import normalize_documents
from memory.rag_retriever import RAGRetriever
from agents.reasoner import reason
from agents.reflection import reflect
from memory.user_memory import load_memory, save_memory

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import os
import json


# complete clean slate for memory
MEMORY_FILE = "app/data/user_memory.json"
if os.path.exists(MEMORY_FILE):
    os.remove(MEMORY_FILE)


def build_vector_store(docs):
    model = "sentence-transformers/all-MiniLM-L6-v2"
    embeddings = HuggingFaceEmbeddings(model_name=model)
    return FAISS.from_documents(docs, embeddings)


def agent_step(query: str, vector_store, retriever, log=True):
    retrieved = retriever.retrieve(query, k=5)
    answer = reason(query, retrieved)

    if log:
        print(f"\n🧠 USER: {query}")
        print(f"🤖 AGENT: {answer}")

    # Reflection + memory update
    history = f"User: {query}\nAgent: {answer}"
    new = reflect(history)

    if new:
        mem = load_memory()
        mem.extend(new)
        save_memory(mem)
        if log:
            print(f"💾 Memory saved: {new}")

    return answer


def main():
    print("📌 Loading + embedding documents...")
    docs = split_documents(normalize_documents(load_reports()))
    vector_store = build_vector_store(docs)
    retriever = RAGRetriever(vector_store)

    # STEP 1 — Create memory
    agent_step("I prefer short bullet point answers.", vector_store, retriever)

    # STEP 2 — Check whether memory influences response
    agent_step("What are NVIDIA's main business strengths?", vector_store, retriever)

    # STEP 3 — Print raw memory content
    print("\n📂 MEMORY FILE CONTENT:")
    print(json.dumps(load_memory(), indent=2))



if __name__ == "__main__":
    main()
