import os
import json

# pip install openai
try:
    from openai import OpenAI
except Exception:
    OpenAI = None


SYSTEM_PROMPT = """You are an analytics SQL agent.
Return ONLY a SQL query for PostgreSQL.

Rules:
- Use only SELECT statements.
- Default table is demo_sales_daily with columns:
  d (date), country (text), revenue (numeric), orders (int), customers (int)
- Prefer grouped, aggregated queries for trend/compare questions.
- Always include ORDER BY for time series queries.
- If user asks "by country", include country in SELECT/GROUP BY.
- If user asks "trend", return a time series (d) aggregated by day or week.
- Keep it simple and fast.
"""

FEWSHOTS = [
    {
        "q": "show revenue trend",
        "a": "SELECT d, SUM(revenue) AS revenue FROM demo_sales_daily GROUP BY 1 ORDER BY 1"
    },
    {
        "q": "show revenue trend by country",
        "a": "SELECT d, country, SUM(revenue) AS revenue FROM demo_sales_daily GROUP BY 1,2 ORDER BY 1,2"
    },
    {
        "q": "top 5 countries by revenue",
        "a": "SELECT country, SUM(revenue) AS revenue FROM demo_sales_daily GROUP BY 1 ORDER BY 2 DESC LIMIT 5"
    },
]


def _fallback_sql(question: str) -> str:
    q = question.lower()
    if "trend" in q and "country" in q:
        return "SELECT d, country, SUM(revenue) AS revenue FROM demo_sales_daily GROUP BY 1,2 ORDER BY 1,2"
    if "trend" in q:
        return "SELECT d, SUM(revenue) AS revenue FROM demo_sales_daily GROUP BY 1 ORDER BY 1"
    if "top" in q and "country" in q:
        return "SELECT country, SUM(revenue) AS revenue FROM demo_sales_daily GROUP BY 1 ORDER BY 2 DESC LIMIT 10"
    return "SELECT d, country, revenue, orders, customers FROM demo_sales_daily ORDER BY d, country"


def build_sql_from_question(question: str) -> str:
    """
    Natural language -> SQL (Postgres)
    - If OPENAI_API_KEY and openai SDK exist: use LLM
    - Else fallback rules
    """
    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not api_key or OpenAI is None:
        return _fallback_sql(question)

    client = OpenAI(api_key=api_key)

    # few-shot messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for ex in FEWSHOTS:
        messages.append({"role": "user", "content": ex["q"]})
        messages.append({"role": "assistant", "content": ex["a"]})

    messages.append({"role": "user", "content": question})

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.1,
    )

    sql = resp.choices[0].message.content.strip()

    if sql.startswith("```"):
        sql = sql.strip("`")
        sql = sql.replace("sql", "", 1).strip()

    sql = sql.strip().rstrip(";").strip()
    return sql
