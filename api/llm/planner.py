import json
from openai import OpenAI
from api.core.config import OPENAI_API_KEY, OPENAI_MODEL
from api.llm.schemas import AskPlan

SYSTEM = """
You are an analytics query planner.
Return ONLY valid JSON.

Rules:
- metrics must be from: revenue, orders, customers, aov
- intent must be one of: explain, trend, compare
- grain must be one of: day, week, month
- if question is vague about time, prefer last_30_days
- if "performance" or "business" and "drop" appear, choose metrics: ["revenue", "orders", "customers", "aov"]
- if "why" or "reason" appears, set intent to "explain"
- if "drop" appears, set compare_to to "previous_period"
- if a year-over-year comparison is requested, set compare_to to "yoy"
- breakdown may be omitted
"""

client = OpenAI(api_key=OPENAI_API_KEY)


def _safe_json_load(text: str) -> dict:
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _normalize_plan_payload(raw_data: dict, question: str) -> dict:
    q = (question or "").lower().strip()
    data: dict = {}

    # 1) metrics
    raw_metrics = raw_data.get("metrics")
    if isinstance(raw_metrics, str):
        metrics = [raw_metrics]
    elif isinstance(raw_metrics, list) and raw_metrics:
        metrics = raw_metrics
    elif ("performance" in q or "business" in q) and "drop" in q:
        metrics = ["revenue", "orders", "customers", "aov"]
    else:
        metrics = ["revenue"]

    allowed_metrics = {"revenue", "orders", "customers", "aov"}
    metrics = [m for m in metrics if m in allowed_metrics]
    if not metrics:
        metrics = ["revenue"]
    data["metrics"] = metrics

    # 2) intent
    intent = raw_data.get("intent")
    if intent not in {"explain", "trend", "compare"}:
        if "why" in q or "reason" in q or "drop" in q:
            intent = "explain"
        elif "compare" in q or "vs" in q or "versus" in q:
            intent = "compare"
        else:
            intent = "trend"
    data["intent"] = intent

    # 3) compare_to
    compare_to = raw_data.get("compare_to")
    if compare_to not in {None, "previous_period", "yoy"}:
        compare_to = None

    if compare_to is None:
        if "year over year" in q or "yoy" in q:
            compare_to = "yoy"
        elif "drop" in q:
            compare_to = "previous_period"

    if compare_to is not None:
        data["compare_to"] = compare_to

    # 4) grain
    grain = raw_data.get("grain")
    if grain not in {"day", "week", "month"}:
        if any(x in q for x in ["quarter", "year", "annual", "yoy"]):
            grain = "month"
        elif any(x in q for x in ["week", "weekly"]):
            grain = "week"
        else:
            grain = "day"
    data["grain"] = grain

    # 5) breakdown
    raw_breakdown = raw_data.get("breakdown")
    allowed_breakdowns = {"category", "seller_id", "country"}

    if isinstance(raw_breakdown, str):
        breakdown = [raw_breakdown] if raw_breakdown in allowed_breakdowns else None
    elif isinstance(raw_breakdown, list):
        cleaned = [b for b in raw_breakdown if b in allowed_breakdowns]
        breakdown = cleaned if cleaned else None
    else:
        breakdown = None

    data["breakdown"] = breakdown

    # 6) FORCE clean date_range to match DateRange schema exactly
    # DateRange schema:
    # mode: relative|absolute
    # preset: optional
    # start: optional
    # end: optional
    data["date_range"] = {
        "mode": "relative",
        "preset": "last_30_days",
        "start": None,
        "end": None,
    }

    return data


def make_plan(question: str) -> AskPlan:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is missing")

    resp = client.responses.create(
        model=OPENAI_MODEL,
        input=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": question},
        ],
    )

    text = (resp.output_text or "").strip()
    raw_data = _safe_json_load(text)
    normalized = _normalize_plan_payload(raw_data, question)

    return AskPlan.model_validate(normalized)