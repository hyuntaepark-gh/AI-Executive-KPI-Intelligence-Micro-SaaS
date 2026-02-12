from typing import Dict, List


def parse_intent(question: str) -> Dict[str, object]:
    q = (question or "").lower()

    intent = "unknown"
    if any(k in q for k in ["why", "cause", "reason", "drop", "decline"]):
        intent = "why"
    elif any(k in q for k in ["trend", "over time", "time series", "last", "past"]):
        intent = "trend"
    elif any(k in q for k in ["compare", "vs", "versus", "difference"]):
        intent = "compare"

    keywords: List[str] = []
    for k in ["performance", "revenue", "orders", "customers", "aov", "drop", "trend", "compare", "ytd", "quarter"]:
        if k in q:
            keywords.append(k)

    return {
        "intent": intent,
        "keywords": keywords,
    }
