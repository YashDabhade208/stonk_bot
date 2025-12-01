# app/memory/rag_chain.py
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from core.config import OPENROUTER_API_KEY, OPENROUTER_MODEL
from .rag_vectorstore import get_vectorstore


# LLM (same OpenRouter config)
llm = ChatOpenAI(
    api_key=OPENROUTER_API_KEY,
    model=OPENROUTER_MODEL,
    base_url="https://openrouter.ai/api/v1",
    temperature=0,
)


def _get_retriever():
    vs = get_vectorstore()
    if vs is None:
        return None
    return vs.as_retriever(search_kwargs={"k": 4})


prompt = ChatPromptTemplate.from_template(
    """
You are a stock research assistant.

Use the following context from company reports, filings, and notes to
answer the user's question. If the context is not sufficient, say you
don't have enough information rather than guessing.

Context:
{context}

Question:
{question}

Answer in 3-6 bullet points, concise and specific.
"""
)


def get_rag_chain():
    retriever = _get_retriever()
    if retriever is None:
        return None

    # LCEL style: parallel retrieval + passthrough
    rag_chain = (
        RunnableParallel(
            {
                "question": RunnablePassthrough(),
                "context": retriever,
            }
        )
        | prompt
        | llm
    )
    return rag_chain


def run_rag_query(question: str) -> Optional[str]:
    chain = get_rag_chain()
    if chain is None:
        return "RAG index not available (no documents)."

    res = chain.invoke(question)
    return res.content
