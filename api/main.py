from datetime import date
from typing import Optional

from fastapi import FastAPI

from api.app.schemas import KPIIn, AnalyzeRequest, AnalyzeResponse
from api.app.services.kpi_service import fetch_kpi, upsert_kpi
from api.app.services.report_service import fetch_latest_two_months, build_monthly_report
from api.app.services.analyze_service import build_metric_sql, fetch_metric_rows, build_narrative
from api.app.db import get_conn

app = FastAPI(title="Micro SaaS KPI API", version="0.2.0")

@app.get("/")
def home():
    return {"message": "Micro SaaS API running"}


@app.get("/health")
def health_check():
    conn = get_conn()
    conn.close()
    return {"status": "database connected"}


@app.get("/kpi")
def get_kpi(from_: Optional[date] = None, to: Optional[date] = None):
    return {"data": fetch_kpi(from_, to)}


@app.post("/kpi")
def add_kpi(payload: KPIIn):
    saved = upsert_kpi(
        month=payload.month,
        revenue=payload.revenue,
        orders=payload.orders,
        customers=payload.customers,
        aov=payload.aov,
    )
    return {"status": "ok", "saved": saved}


@app.get("/report/monthly")
def report_monthly():
    rows = fetch_latest_two_months()
    if len(rows) < 2:
        return {"error": "Need at least 2 months in kpi_monthly."}
    base, target = rows[0], rows[1]
    return build_monthly_report(base, target)


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest):
    sql = build_metric_sql(metric=payload.metric, range_=payload.range)
    rows = fetch_metric_rows(sql)
    narrative, risk, recommendation = build_narrative(payload.metric, rows, payload.style)

    return AnalyzeResponse(
        metric=payload.metric,
        range=payload.range,
        sql=sql,
        data=rows,
        narrative=narrative,
        risk=risk,
        recommendation=recommendation,
    )