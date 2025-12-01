import re
from langchain_core.documents import Document

RE_PAGE_NUMBER = re.compile(r"^\s*page\s*\d+\s*$", re.IGNORECASE)
RE_WHITESPACE = re.compile(r"\s+")

COMMON_FOOTERS = [
    "forward-looking statements",
    "all rights reserved",
    "safe harbor",
    "this press release contains",
    "cookie policy",
    "privacy policy",
]

def clean_text(text: str) -> str:
    # Remove page number-only lines
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        if RE_PAGE_NUMBER.match(line):
            continue
        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    # Remove common boilerplate spam
    for phrase in COMMON_FOOTERS:
        text = re.sub(phrase, "", text, flags=re.IGNORECASE)

    # Collapse weird whitespace
    text = RE_WHITESPACE.sub(" ", text)

    return text.strip()


def normalize_documents(docs: list[Document]) -> list[Document]:
    normalized = []
    seen_contents = set()  # dedupe
    for doc in docs:
        cleaned = clean_text(doc.page_content)
        if not cleaned:
            continue
        if cleaned in seen_contents:
            continue
        seen_contents.add(cleaned)
        normalized.append(Document(page_content=cleaned, metadata=doc.metadata))
    return normalized
