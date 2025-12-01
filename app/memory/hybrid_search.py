from typing import List, Optional
from langchain_core.documents import Document
import numpy as np


def rerank_with_recency(docs: List[Document]) -> List[Document]:
    year_scores = []
    for doc in docs:
        year = doc.metadata.get("year")
        if year:
            try:
                year_scores.append(int(year))
            except:
                year_scores.append(0)
        else:
            year_scores.append(0)

    max_year = max(year_scores) if year_scores else 0
    scores = [1 + (y - max_year) * 0.01 for y in year_scores]  # slight boost
    ranked = sorted(zip(scores, docs), reverse=True, key=lambda x: x[0])
    return [d for _, d in ranked]


def unique_sources(docs: List[Document]) -> List[Document]:
    seen = set()
    result = []
    for d in docs:
        src = d.metadata.get("source", "")
        if src not in seen:
            seen.add(src)
            result.append(d)
    return result


def hybrid_select(
    docs: List[Document],
    k: int = 5,
    prefer_year: Optional[int] = None,
    doc_type: Optional[str] = None,
) -> List[Document]:
    # filter by type if required
    if doc_type:
        docs = [d for d in docs if d.metadata.get("type") == doc_type]

    # filter by year if question hints at a target year
    if prefer_year:
        docs = [d for d in docs if d.metadata.get("year") == str(prefer_year)] or docs

    # recency boost
    docs = rerank_with_recency(docs)

    # source diversity
    docs = unique_sources(docs)

    return docs[:k]
