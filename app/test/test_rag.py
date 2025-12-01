# app/test/test_rag.py
import sys
import os

# Make `app` root importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.rag_chain import run_rag_query  # type: ignore


if __name__ == "__main__":
    question = input("Ask something about your reports (e.g., 'What are NVDA risks?'):\n> ")
    print("\nRunning RAG query...\n")
    answer = run_rag_query(question)
    print(answer)
