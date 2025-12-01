from enum import Enum


class TaskType(Enum):
    FACT = "fact"
    SUMMARY = "summary"
    COMPARISON = "comparison"
    CALCULATION = "calculation"
    INSIGHT = "insight"
    UNKNOWN = "unknown"


def classify_task(query: str) -> TaskType:
    q = query.lower()

    if any(x in q for x in ["risk", "ceo", "revenue", "who", "what", "when"]):
        return TaskType.FACT

    if any(x in q for x in ["summarize", "overview", "explain", "in simple terms"]):
        return TaskType.SUMMARY

    if any(x in q for x in ["compare", "difference between", "vs", "versus"]):
        return TaskType.COMPARISON

    if any(x in q for x in ["average", "min", "max", "closing price", "calculate", "growth rate"]):
        return TaskType.CALCULATION

    if any(x in q for x in ["should i invest", "analysis", "insight", "opinion", "is it undervalued"]):
        return TaskType.INSIGHT

    return TaskType.UNKNOWN
