# app/memory/rag_loader.py
from pathlib import Path
from typing import List

from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import UnstructuredHTMLLoader
from datetime import datetime
from langchain_text_splitters import RecursiveCharacterTextSplitter


BASE_DIR = Path(__file__).resolve().parents[1]
REPORTS_DIR = BASE_DIR / "data" / "reports"


def load_reports() -> List[Document]:
    """
    Load .txt, .md and .csv files from app/data/reports as LangChain Documents.
    """
    docs: List[Document] = []

    if not REPORTS_DIR.exists():
        print("[Loader] reports directory not found — skipping.")
        return docs

    # PDF
    for path in REPORTS_DIR.glob("*.pdf"):
        try:
            loader = PyPDFLoader(str(path))
            loaded = loader.load()
            docs.extend(loaded)
            print(f"[PDF] Loaded {len(loaded)} pages from {path.name}")
        except Exception as e:
            print(f"[PDF] Failed to load {path.name}: {e}")

    # TXT
    for path in REPORTS_DIR.glob("*.txt"):
        try:
            loader = TextLoader(str(path), encoding="utf-8")
            loaded = loader.load()
            docs.extend(loaded)
            print(f"[TXT] Loaded {len(loaded)} docs from {path.name}")
        except Exception as e:
            print(f"[TXT] Failed to load {path.name}: {e}")

    # HTML
    for path in REPORTS_DIR.glob("*.html"):
        try:
            loader = UnstructuredHTMLLoader(str(path))
            loaded = loader.load()
            docs.extend(loaded)
            print(f"[HTML] Loaded {len(loaded)} docs from {path.name}")
        except Exception as e:
            print(f"[HTML] Failed to load {path.name}: {e}")


    # MD
    for path in REPORTS_DIR.glob("*.md"):
        try:
            loader = TextLoader(str(path), encoding="utf-8")
            loaded = loader.load()
            docs.extend(loaded)
            print(f"[MD] Loaded {len(loaded)} docs from {path.name}")
        except Exception as e:
            print(f"[MD] Failed to load {path.name}: {e}")

    # CSV
    for path in REPORTS_DIR.glob("*.csv"):
        try:
            loader = CSVLoader(
                file_path=str(path),
                csv_args={
                    "delimiter": ",",
                    "quotechar": '"'
                },
                encoding="utf-8"
            )
            loaded = loader.load()
            docs.extend(loaded)
            print(f"[CSV] Loaded {len(loaded)} rows from {path.name}")
        except Exception as e:
            print(f"[CSV] Failed to load {path.name}: {e}")

    print(f"[Loader] Total loaded documents: {len(docs)}")
    return docs


def split_documents(docs: list[Document]) -> list[Document]:
    if not docs:
        print("[Splitter] No documents to split.")
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunks = []
    chunk_counter = 0

    for doc in docs:
        file_name = Path(doc.metadata.get("source", "")).name if doc.metadata.get("source") else "unknown"

        # try to extract year from filename
        year = None
        for part in file_name.split("-"):
            if part.isdigit() and 1990 <= int(part) <= datetime.now().year:
                year = part
                break

        sub_chunks = splitter.split_documents([doc])
        for idx, c in enumerate(sub_chunks):
            chunk_counter += 1
            c.metadata["chunk_id"] = chunk_counter
            c.metadata["source"] = file_name
            c.metadata["type"] = Path(file_name).suffix.lower().replace(".", "")
            if year:
                c.metadata["year"] = year

            chunks.append(c)

    print(f"[Splitter] Split into {len(chunks)} chunks with metadata.")
    print(chunks[0].metadata)
    return chunks
