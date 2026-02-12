import re
from typing import Dict, Optional

SUPPORTED_METRICS = ["revenue", "orders", "customers", "aov"]
SUPPORTED_RANGES = ["last_2_months", "last_3_months", "last_6_months", "ytd"]
SUPPORTED_STYLES = ["basic", "executive"]

def _detect_metric(q: str) -> str:
    ql = q.lower()
    # keyword-based
    if "revenue" in ql or "sales" in ql:
        return "revenue"
    if "order" in ql or "orders" in ql:
        return "orders"
    if "customer" in ql or "customers" in ql:
        return "customers"
    if "aov" in ql or "average order value" in ql:
        return "aov"
    # default
    return "revenue"

def _detect_range(q: str) -> str:
    ql = q.lower()

    # explicit months like "last 6 months"
    m = re.search(r"last\s+(\d+)\s+months?", ql)
    if m:
        n = int(m.group(1))
        if n <= 2:
            return "last_2_months"
        if n <= 3:
            return "last_3_months"
        return "last_6_months"

    # natural language
    if "ytd" in ql or "year to date" in ql or "this year" in ql:
        return "ytd"
    if "last quarter" in ql or "quarter" in ql:
        return "last_3_months"
    if "last 2 months" in ql:
        return "last_2_months"
    if "last 3 months" in ql or "recent" in ql or "recently" in ql:
        return "last_3_months"
    if "last 6 months" in ql or "past 6 months" in ql:
        return "last_6_months"

    # default
    return "last_3_months"

def _normalize_style(style: Optional[str]) -> str:
    if not style:
        return "executive"
    s = style.lower().strip()
    return s if s in SUPPORTED_STYLES else "executive"

def parse_question(question: str, style: Optional[str] = None) -> Dict[str, str]:
    metric = _detect_metric(question)
    range_ = _detect_range(question)
    style_ = _normalize_style(style)

    # safety: enforce supported lists
    if metric not in SUPPORTED_METRICS:
        metric = "revenue"
    if range_ not in SUPPORTED_RANGES:
        range_ = "last_3_months"
    if style_ not in SUPPORTED_STYLES:
        style_ = "executive"

    return {"metric": metric, "range": range_, "style": style_}
