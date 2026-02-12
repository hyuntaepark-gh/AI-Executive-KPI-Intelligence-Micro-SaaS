from ..db import get_conn

def _range_to_limit(range_: str) -> str:
    # Limit by rows after ordering; since months are discrete, this works for a demo MVP.
    if range_ == "last_3_months":
        return "3"
    if range_ == "last_6_months":
        return "6"
    return None  # all

def build_metric_sql(metric: str, range_: str) -> str:
    # metric comes from strict Literal in schema, so safe.
    limit = _range_to_limit(range_)
    base = f"""
        SELECT month, revenue, orders, customers, aov
        FROM kpi_monthly
        ORDER BY month DESC
    """
    if limit:
        base += f"\nLIMIT {limit};"
    else:
        base += ";"
    return base.strip()

def fetch_metric_rows(sql: str):
    conn = get_conn(dict_cursor=True)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    # We ordered DESC, but for narrative it’s nicer ASC
    return list(reversed(rows))

def build_narrative(metric: str, rows: list[dict], style: str = "executive"):
    if not rows:
        return ("No data found.", "No risk signals.", "Insert KPI data first.")

    first = rows[0]
    last = rows[-1]

    def pct_change(a, b):
        if a in (None, 0):
            return None
        return (b - a) / a

    # choose metric value
    metric_map = {
        "revenue": "revenue",
        "orders": "orders",
        "customers": "customers",
        "aov": "aov",
    }
    col = metric_map[metric]
    start = float(first[col])
    end = float(last[col])
    chg = end - start
    chg_pct = pct_change(start, end)

    direction = "increased" if chg > 0 else "decreased" if chg < 0 else "was flat"

    if chg_pct is None:
        headline = f"{metric.upper()} {direction} from {first['month']} to {last['month']}."
    else:
        headline = f"{metric.upper()} {direction} from {first['month']} to {last['month']} ({chg_pct*100:.1f}%)."

    # simple risk rules
    risk = "No major risk signals detected."
    recommendation = "Keep monitoring trends."

    if metric == "revenue":
        # check if revenue up but AOV down = discount risk
        aov_start, aov_end = float(first["aov"]), float(last["aov"])
        orders_start, orders_end = float(first["orders"]), float(last["orders"])
        aov_pct = pct_change(aov_start, aov_end)
        orders_pct = pct_change(orders_start, orders_end)

        if aov_pct is not None and aov_pct < -0.10:
            risk = "AOV dropped materially; revenue growth may be discount-driven."
            recommendation = "Audit discounts, review product mix, and protect margin."
        elif orders_pct is not None and orders_pct < -0.10:
            risk = "Orders dropped materially; demand or funnel may be weakening."
            recommendation = "Investigate acquisition, conversion funnel, and retention actions."
        else:
            recommendation = "Identify which lever moved most (orders vs AOV) and double-down on that driver."

    if style == "brief":
        narrative = headline
    elif style == "detailed":
        narrative = (
            f"{headline} "
            f"Start={start:.2f}, End={end:.2f}, Change={chg:.2f}. "
            f"Data points={len(rows)}."
        )
    else:
        narrative = f"{headline} Focus on the dominant driver and monitor downside risks."

    return (narrative, risk, recommendation)

from openai import OpenAI
import os
from typing import Tuple

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def build_llm_narrative(metric: str, rows: list[dict], style: str = "executive") -> Tuple[str, str, str]:
    """
    LLM-powered narrative.
    Returns (narrative, risk, recommendation).
    Falls back to rule-based build_narrative() if LLM fails or API key missing.
    """
    if not rows:
        return ("No data found.", "No risk signals.", "Insert KPI data first.")

    if not os.getenv("OPENAI_API_KEY"):
        return build_narrative(metric, rows, style=style)

    try:
        prompt = f"""
You are a senior analytics consultant. Write in {style} tone.

Metric: {metric}
Data (monthly rows, oldest -> newest):
{rows}

Return EXACTLY in this format:
INSIGHT: <one paragraph>
RISK: <one paragraph>
RECOMMENDATION: <one paragraph>
""".strip()

        resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        text = resp.choices[0].message.content.strip()

        def _pick(prefix: str) -> str:
            for line in text.splitlines():
                if line.upper().startswith(prefix):
                    return line.split(":", 1)[1].strip()
            return ""

        insight = _pick("INSIGHT")
        risk = _pick("RISK")
        rec = _pick("RECOMMENDATION")

        if not insight or not risk or not rec:
            return build_narrative(metric, rows, style=style)

        return (insight, risk, rec)

    except Exception:
        return build_narrative(metric, rows, style=style)
