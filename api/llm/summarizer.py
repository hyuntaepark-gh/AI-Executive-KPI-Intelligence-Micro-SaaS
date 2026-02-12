import json
from openai import OpenAI
from api.core.config import OPENAI_API_KEY, OPENAI_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM = """
You are an analytics insight writer.
Use ONLY the provided results. Do not guess.

Output JSON with:
- executive_summary (string)
- key_findings (array of strings)
- drivers (array of strings)
- next_actions (array of strings)
"""

def summarize(question: str, plan: dict, results: dict) -> dict:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is missing")

    payload = {
        "question": question,
        "plan": plan,
        "results": results,
    }

    resp = client.responses.create(
        model=OPENAI_MODEL,
        input=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": json.dumps(payload)},
        ],
    )
    text = resp.output_text.strip()
    return json.loads(text)
