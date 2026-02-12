from datetime import date, timedelta, datetime
from typing import Optional, List, Tuple, Dict, Any

ALLOWED_BREAKDOWNS = {"category", "seller_id", "country"}

def _parse_yyyy_mm_dd(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()

def resolve_date_range(dr: Dict[str, Any]) -> Tuple[date, date]:
    mode = dr.get("mode")
    if mode == "absolute":
        start = _parse_yyyy_mm_dd(dr["start"])
        end = _parse_yyyy_mm_dd(dr["end"])
        return start, end

    preset = dr.get("preset") or "last_30_days"
    today = date.today()

    if preset == "last_7_days":
        return today - timedelta(days=7), today
    if preset == "last_30_days":
        return today - timedelta(days=30), today
    if preset == "this_month":
        return today.replace(day=1), today
    if preset == "last_month":
        first_this = today.replace(day=1)
        last_prev = first_this - timedelta(days=1)
        first_prev = last_prev.replace(day=1)
        return first_prev, first_this
    if preset == "yoy":
        return today - timedelta(days=365), today

    # last_quarter (simple approximation: 90 days)
    if preset == "last_quarter":
        return today - timedelta(days=90), today

    return today - timedelta(days=30), today

def build_kpi_sql(
    metric: str,
    grain: str,
    start: date,
    end: date,
    breakdown: Optional[List[str]] = None,
) -> Tuple[str, Dict[str, Any]]:

    metric_expr = {
        "revenue": "SUM(net_revenue)",
        "orders": "COUNT(DISTINCT order_id)",
        "customers": "COUNT(DISTINCT customer_id)",
        "aov": "SUM(net_revenue) / NULLIF(COUNT(DISTINCT order_id), 0)",
    }[metric]

    grain_expr = {
        "day": "date_trunc('day', order_date)::date",
        "week": "date_trunc('week', order_date)::date",
        "month": "date_trunc('month', order_date)::date",
    }[grain]

    select_cols = [f"{grain_expr} AS period"]
    group_cols = [grain_expr]

    if breakdown:
        for b in breakdown:
            if b not in ALLOWED_BREAKDOWNS:
                raise ValueError(f"breakdown not allowed: {b}")
            select_cols.append(b)
            group_cols.append(b)

    sql = f"""
    SELECT
      {", ".join(select_cols)},
      {metric_expr} AS value
    FROM analytics.sales_fact
    WHERE order_date >= :start AND order_date < :end
    GROUP BY {", ".join(group_cols)}
    ORDER BY {", ".join(group_cols)};
    """.strip()

    params = {"start": start, "end": end}
    return sql, params
