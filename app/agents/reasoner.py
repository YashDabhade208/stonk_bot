import sys
import os

# Make `app` root importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List
from langchain_core.documents import Document
from memory.user_memory import load_memory

from agents.classifier import classify_task, TaskType
from langchain_openai import ChatOpenAI
from core.config import OPENROUTER_API_KEY, OPENROUTER_MODEL


# LLM Client (OpenRouter)
llm = ChatOpenAI(
    api_key=OPENROUTER_API_KEY,
    model=OPENROUTER_MODEL,
    base_url="https://openrouter.ai/api/v1",
    temperature=0,
)


def format_docs(docs: List[Document]) -> str:
    """
    Convert retrieved docs to plain readable text with source tagging.
    """
    out = []
    for d in docs:
        out.append(f"[{d.metadata.get('source')}] {d.page_content}")
    return "\n\n".join(out)


def ask_llm(prompt: str) -> str:
    """
    Simple wrapper around ChatOpenAI.invoke() for compatibility.
    """
    res = llm.invoke(prompt)
    return res.content


def reason(query: str, docs: List[Document]) -> str:
    """
    Core reasoning layer – decides the strategy based on task type.
    """
    task = classify_task(query)
    context = format_docs(docs)
    memory_items = load_memory()
    memory_context = "\n".join(f"- {m}" for m in memory_items)

    if memory_context:
        context = f"User Memory:\n{memory_context}\n\n---\n\n{context}"

    if task == TaskType.FACT:
        prompt = (
            "Answer the question using ONLY the information below.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {query}\n"
            "Answer concisely and cite the sources in parentheses at the end."
        )
        return ask_llm(prompt)

    if task == TaskType.SUMMARY:
        prompt = (
            "Summarize the content below in 5 bullet points.\n\n"
            f"{context}"
        )
        return ask_llm(prompt)

    if task == TaskType.COMPARISON:
        prompt = (
            "Compare the relevant information below.\n\n"
            f"{context}\n\n"
            f"Question: {query}"
        )
        return ask_llm(prompt)

    if task == TaskType.CALCULATION:
        prompt = (
            "Extract the numerical data from the context and compute step by step.\n\n"
            f"{context}\n\n"
            f"Question: {query}"
        )
        return ask_llm(prompt)

    if task == TaskType.INSIGHT:
        prompt = (
            "Generate an insight-driven answer that synthesizes the evidence below.\n\n"
            f"{context}\n\n"
            f"Question: {query}"
        )
        return ask_llm(prompt)

    # fallback
    prompt = (
        "Answer the question using the context below.\n\n"
        f"{context}\n\n"
        f"Question: {query}"
    )
    return ask_llm(prompt)
