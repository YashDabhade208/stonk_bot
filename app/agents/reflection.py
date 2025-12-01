import json
from langchain_openai import ChatOpenAI
from core.config import OPENROUTER_API_KEY, OPENROUTER_MODEL

llm = ChatOpenAI(
    api_key=OPENROUTER_API_KEY,
    model=OPENROUTER_MODEL,
    base_url="https://openrouter.ai/api/v1",
    temperature=0
)

REFLECTION_PROMPT = """
From the conversation below, extract ONLY long-term user preferences or personal traits.

Save if it fits one of these categories:
- Answer style / format preference
- Investment style (short-term / long-term / risk-averse / aggressive)
- Portfolio holdings (personal tickers)
- Long-term financial goals
- Risk tolerance
- Recurring interests or topics

OUTPUT FORMAT (mandatory):
A pure JSON list of strings. No narration, no markdown.

Examples:
["User prefers short bullet answers"]
["User has long-term investing style", "User risk tolerance is low"]
[]
Conversation:
{history}
"""


def reflect(history: str) -> list[str]:
    res = llm.invoke(REFLECTION_PROMPT.format(history=history)).content

    # Try parse direct JSON list
    try:
        parsed = json.loads(res)
        if isinstance(parsed, list):
            return parsed
    except:
        pass

    # Fallback: extract bracketed JSON-like content
    import re
    match = re.search(r"\[(.*?)\]", res, re.DOTALL)
    if match:
        try:
            return json.loads("[" + match.group(1) + "]")
        except:
            return []

    # *** DETERMINISTIC PATTERN MATCHING: Independent of LLM cooperation ***
    return _extract_preferences_deterministic(history)


def _extract_preferences_deterministic(history: str) -> list[str]:
    """Extract user preferences using deterministic pattern matching, not LLM interpretation."""
    lower = history.lower()
    preferences = []

    # Answer format preferences
    if any(word in lower for word in ["prefer", "like", "want", "format"]):
        if any(word in lower for word in ["short", "brief", "concise", "bullet", "bulleted"]):
            preferences.append("User prefers short bullet point answers")
        elif any(word in lower for word in ["detailed", "comprehensive", "long", "thorough"]):
            preferences.append("User prefers detailed comprehensive answers")
        elif any(word in lower for word in ["numbers", "data", "metrics", "quantitative"]):
            preferences.append("User prefers data-driven quantitative answers")
        elif any(word in lower for word in ["simple", "plain", "easy"]):
            preferences.append("User prefers simple easy to understand answers")

    # Communication style preferences
    if any(word in lower for word in ["formal", "professional"]):
        preferences.append("User prefers formal professional communication")
    elif any(word in lower for word in ["casual", "informal", "friendly"]):
        preferences.append("User prefers casual friendly communication")

    # Investment style preferences (only if explicitly mentioned)
    if "investing style" in lower and "prefer" not in lower:
        return []  # only store if explicitly mentioned
    if any(word in lower for word in ["long-term", "long term", "buy and hold", "investing"]):
        if any(word in lower for word in ["prefer", "like", "want", "my"]):
            preferences.append("User has long-term investing style")
    elif any(word in lower for word in ["short-term", "short term", "trading", "day trading"]):
        if any(word in lower for word in ["prefer", "like", "want", "my"]):
            preferences.append("User has short-term trading style")

    if any(word in lower for word in ["risk-averse", "conservative", "safe", "cautious"]):
        preferences.append("User risk tolerance is low")
    elif any(word in lower for word in ["aggressive", "high-risk", "risky", "growth"]):
        preferences.append("User risk tolerance is high")

    # Topic preferences
    if any(word in lower for word in ["tesla", "tsla"]):
        preferences.append("User is interested in Tesla stock")
    if any(word in lower for word in ["apple", "aapl"]):
        preferences.append("User is interested in Apple stock")
    if any(word in lower for word in ["nvidia", "nvda"]):
        preferences.append("User is interested in NVIDIA stock")
    if any(word in lower for word in ["bitcoin", "btc", "crypto"]):
        preferences.append("User is interested in cryptocurrency")

    # Remove duplicates while preserving order
    seen = set()
    unique_prefs = []
    for pref in preferences:
        if pref not in seen:
            seen.add(pref)
            unique_prefs.append(pref)

    return unique_prefs
