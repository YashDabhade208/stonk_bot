import json
from pathlib import Path

MEMORY_FILE = Path("app/data/user_memory.json")
MEMORY_DIR = MEMORY_FILE.parent


def load_memory() -> list[str]:
    if not MEMORY_FILE.exists():
        return []
    try:
        return json.loads(MEMORY_FILE.read_text())
    except:
        return []


def save_memory(memories: list[str]):
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    deduped = list(dict.fromkeys(memories))  # preserve order, remove duplicates
    MEMORY_FILE.write_text(json.dumps(deduped, indent=2))

