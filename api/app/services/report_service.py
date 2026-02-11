from psycopg2.extras import RealDictCursor
from ..db import get_conn

def fetch_latest_two_months():
    conn = get_conn(dict_cursor=True)
    cur = conn.cursor()
    cur.execute("""
        SELECT month, revenue, orders, customers, aov
        FROM kpi_monthly
        ORDER BY month DESC
        LIMIT 2;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return list(reversed(rows))

def build_monthly_report(base, target):
    rev_change = float(target["revenue"]) - float(base["revenue"])
    rev_change_pct = (rev_change / float(base["revenue"])) if base["revenue"] else None

    orders_change_pct = (target["orders"] - base["orders"]) / base["orders"] if base["orders"] else None
    aov_change_pct = (float(target["aov"]) - float(base["aov"])) / float(base["aov"]) if base["aov"] else None

    driver = None
    if orders_change_pct is not None and aov_change_pct is not None:
        driver = "Orders" if abs(orders_change_pct) >= abs(aov_change_pct) else "AOV"

    if rev_change_pct is not None:
        summary = f"From {base['month']} to {target['month']}, revenue changed by {rev_change:.0f} ({rev_change_pct*100:.1f}%)."
    else:
        summary = f"From {base['month']} to {target['month']}, revenue changed by {rev_change:.0f}."

    risk_flags = []
    if aov_change_pct is not None and aov_change_pct < -0.10:
        risk_flags.append("AOV dropped materially (possible discounting or weaker pricing).")
    if orders_change_pct is not None and orders_change_pct < -0.10:
        risk_flags.append("Orders dropped materially (possible demand or funnel issue).")
    if target["customers"] < base["customers"]:
        risk_flags.append("Customers decreased (possible retention/acquisition issue).")

    risk = "No major risk signals detected." if not risk_flags else " | ".join(risk_flags)

    if driver == "Orders":
        recommendation = "Focus on demand levers: acquisition, conversion funnel, and retention."
    elif driver == "AOV":
        recommendation = "Focus on pricing/mix: reduce excessive discounting, improve upsell/cross-sell, and optimize product mix."
    else:
        recommendation = "Collect more months of data to confidently identify the primary driver."

    driver_text = f"Primary driver: {driver}" if driver else "Primary driver unclear"

    return {
        "summary": summary,
        "driver": driver_text,
        "risk": risk,
        "recommendation": recommendation,
        "meta": {
            "from_month": str(base["month"]),
            "to_month": str(target["month"]),
            "revenue_change": rev_change,
            "revenue_change_pct": rev_change_pct,
            "orders_change_pct": orders_change_pct,
            "aov_change_pct": aov_change_pct,
        }
    }
