import sys
import os

# Make `app` root importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from typing import List, Optional
from langchain_core.documents import Document

from memory.hybrid_search import hybrid_select


class RAGRetriever:
    def __init__(self, vector_store):
        """
        vector_store must support similarity_search(query, k)
        Example: FAISS, Chroma, Pinecone, Weaviate etc.
        """
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        k: int = 5,
        prefer_year: Optional[int] = None,
        doc_type: Optional[str] = None,
    ) -> List[Document]:
        """
        Hybrid retrieval combining semantic search + metadata ranking + recency + source diversity.
        """
        # raw semantic search
        raw = self.vector_store.similarity_search(query, k=20)

        if not raw:
            return []

        # hybrid strategy
        refined = hybrid_select(
            docs=raw,
            k=k,
            prefer_year=prefer_year,
            doc_type=doc_type,
        )

        return refined
