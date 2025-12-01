import sys
import os

# Make `app` root importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.rag_loader import load_reports
from memory.rag_loader import split_documents
from memory.normalizer import normalize_documents

docs = load_reports()
docs = normalize_documents(docs)
docs = split_documents(docs)
print(len(docs))
print(docs[0].page_content[:300], )
