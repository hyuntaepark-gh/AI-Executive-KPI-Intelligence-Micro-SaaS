import json
from openai import OpenAI
from api.core.config import OPENAI_API_KEY, OPENAI_MODEL
from api.llm.schemas import AskPlan

SYSTEM = """
You are an analytics query planner.
Return ONLY valid JSON matching AskPlan.

Rules:
- metrics must be from: revenue, orders, customers, aov
- if question is vague about time, use relative last_30_days
- if "performance" or "business" and "drop" appear, choose metrics: revenue, orders, customers, aov
- if "why" or "reason" appears, set intent to "explain"
- if "drop" appears, set compare_to to "previous_period"
- grain: month if range >= 60 days else day
- breakdown can be: category, seller_id, country (optional)
"""

client = OpenAI(api_key=OPENAI_API_KEY)

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

    text = resp.output_text.strip()
    data = json.loads(text)
    return AskPlan.model_validate(data)
