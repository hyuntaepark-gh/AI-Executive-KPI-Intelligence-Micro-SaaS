import os
import re
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text

from api.app.services.agent_intelligence import build_sql_from_question

router = APIRouter(prefix="/kpi", tags=["kpi"])

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
if not DATABASE_URL:
    DATABASE_URL = "postgresql+psycopg://admin:admin123@localhost:5432/analytics"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


# ----------------------------
# Models
# ----------------------------
class KPIQueryRequest(BaseModel):
    question: str = Field(..., examples=["show revenue trend by country"])
    max_rows: int = 200


class RiskVisual(BaseModel):
    badge_color: str
    arrow: str


class KPIQueryResponse(BaseModel):
    ok: bool
    sql: str
    rows: List[Dict[str, Any]]
    risk_score: float
    risk_visual: RiskVisual
    notes: Optional[List[str]] = None


# ----------------------------
# Risk gauge helpers
# ----------------------------
def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def compute_risk_score(rows: List[Dict[str, Any]]) -> float:
    if not rows:
        return 0.0

    keys = set().union(*[r.keys() for r in rows])
    if "return_rate" in keys or "late_rate" in keys:
        rr = []
        lr = []
        for r in rows:
            if "return_rate" in r and r["return_rate"] is not None:
                rr.append(float(r["return_rate"]))
            if "late_rate" in r and r["late_rate"] is not None:
                lr.append(float(r["late_rate"]))
        rr_avg = sum(rr) / len(rr) if rr else 0.0
        lr_avg = sum(lr) / len(lr) if lr else 0.0
        score = (rr_avg * 100 * 0.6) + (lr_avg * 100 * 0.4)
        return clamp(score, 0, 100)
    if "revenue" in keys:
        rev = [float(r["revenue"]) for r in rows if r.get("revenue") is not None]
        if len(rev) >= 3:
            mean = sum(rev) / len(rev)
            if mean > 0:
                var = sum((x - mean) ** 2 for x in rev) / (len(rev) - 1)
                std = var ** 0.5
                cv = std / mean
                score = (cv - 0.05) / (0.35 - 0.05) * 100
                return clamp(score, 0, 100)

    return 25.0


def risk_visual_from_score(score: float, rows: List[Dict[str, Any]]) -> RiskVisual:
    """
    badge_color:
      green(0~33), yellow(33~66), red(66~100)
    arrow:
    """
    if score < 33:
        color = "green"
    elif score < 66:
        color = "yellow"
    else:
        color = "red"

    arrow = "→"
    if rows:
        keys = set().union(*[r.keys() for r in rows])
        metric = None
        if "revenue" in keys:
            metric = "revenue"
        elif "return_rate" in keys:
            metric = "return_rate"
        elif "late_rate" in keys:
            metric = "late_rate"

        if metric:
            vals = [r.get(metric) for r in rows if r.get(metric) is not None]
            if len(vals) >= 2:
                prev = float(vals[-2])
                last = float(vals[-1])
                if last > prev:
                    arrow = "↑"
                elif last < prev:
                    arrow = "↓"

    return RiskVisual(badge_color=color, arrow=arrow)


# ----------------------------
# SQL safety
# ----------------------------
FORBIDDEN = re.compile(r"\b(insert|update|delete|drop|alter|truncate|create)\b", re.IGNORECASE)


def assert_safe_sql(sql: str) -> None:
    s = sql.strip().strip(";")
    if not s.lower().startswith("select"):
        raise HTTPException(status_code=400, detail="Only SELECT statements are allowed.")
    if FORBIDDEN.search(s):
        raise HTTPException(status_code=400, detail="Unsafe SQL detected.")
    if ";" in s:
        raise HTTPException(status_code=400, detail="Multiple statements are not allowed.")


# ----------------------------
# Endpoint
# ----------------------------
@router.post("/query", response_model=KPIQueryResponse)
def query_kpi(req: KPIQueryRequest):
    sql = build_sql_from_question(req.question)

    assert_safe_sql(sql)

    with engine.begin() as conn:
        result = conn.execute(text(sql))
        fetched = result.fetchmany(req.max_rows)
        cols = result.keys()
        rows = [dict(zip(cols, r)) for r in fetched]

    score = float(compute_risk_score(rows))
    visual = risk_visual_from_score(score, rows)

    return KPIQueryResponse(
        ok=True,
        sql=sql,
        rows=rows,
        risk_score=round(score, 2),
        risk_visual=visual,
        notes=[
            "risk_score is a heuristic for demo purposes.",
            "Only SELECT is allowed; unsafe SQL is blocked.",
        ],
    )
