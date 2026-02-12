from datetime import date
from typing import Optional

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from api.app.schemas import (
    KPIIn,
    AnalyzeRequest,
    AnalyzeResponse,
    MonthlyAIReportResponse,
)

from api.app.services.kpi_service import fetch_kpi, upsert_kpi
from api.app.services.report_service import fetch_latest_two_months, build_monthly_report
from api.app.services.log_service import (
    insert_analysis_log,
    fetch_analysis_history,
    ensure_analysis_log_table,
)

# Decision signals (risk, trend, confidence, risk_score, next_actions)
from api.app.services.decision_service import build_decision_signals

# Final executive report formatter (expects payload dict)
from api.app.services.report_formatter import build_final_report

# Legacy /ask dependencies
from api.app.schemas import AskRequest, AskResponse
from api.app.services.ask_service import parse_question
from api.app.services.analyze_service import (
    build_metric_sql,
    fetch_metric_rows,
    build_narrative,
    build_llm_narrative,
)

from api.app.db import get_conn

# LLM Agent /ask (optional, may fail due to quota)
from api.app.services.agent import ask_agent

# Driver decomposition summary (rule-based)
from api.app.services.driver_service import build_driver_summary


# =========================
# NEW v1 Routers (Patch)
# =========================
# NOTE:
# Existing /kpi routes already exist in this file.
# To avoid path conflicts, routers are mounted with prefix="/v1".
from api.routers.demo import router as demo_router
from api.routers.kpi import router as kpi_router


app = FastAPI(title="Micro SaaS KPI API", version="1.0.0")

# CORS (useful when attaching a frontend later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict later if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- v1 router mounts (no conflict with legacy routes) ----
app.include_router(demo_router, prefix="/v1", tags=["v1"])
app.include_router(kpi_router, prefix="/v1", tags=["v1"])


@app.on_event("startup")
def on_startup():
    """
    Ensure required tables exist at startup
    (prevents 'relation does not exist' errors).
    """
    try:
        ensure_analysis_log_table()
    except Exception:
        # Do not block server startup
        pass


@app.get("/")
def home():
    return {"message": "Micro SaaS API running"}


# New simplified health endpoint (v1 style)
@app.get("/health")
def health():
    return {"ok": True, "service": "micro-saas-kpi-api", "version": "1.0.0"}


# DB connectivity health check (legacy style kept separately)
@app.get("/health/db")
def health_check_db():
    conn = get_conn()
    conn.close()
    return {"status": "database connected"}


SUPPORTED_METRICS = ["revenue", "orders", "customers", "aov"]
SUPPORTED_RANGES = ["last_2_months", "last_3_months", "last_6_months", "ytd"]
SUPPORTED_STYLES = ["basic", "executive"]


@app.get("/meta")
def meta():
    return {
        "metrics": SUPPORTED_METRICS,
        "ranges": SUPPORTED_RANGES,
        "styles": SUPPORTED_STYLES,
        "examples": [
            {"metric": "revenue", "range": "last_3_months", "style": "executive"},
            {"metric": "orders", "range": "last_6_months", "style": "basic"},
        ],
        "agent_examples": [
            {"question": "Why did revenue drop last quarter?"},
            {"question": "Why did performance drop?"},
            {"question": "Show revenue trend for last 30 days by country"},
        ],
    }


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


@app.post("/report/monthly-ai", response_model=MonthlyAIReportResponse)
def report_monthly_ai():
    rows = fetch_latest_two_months()
    if len(rows) < 2:
        return MonthlyAIReportResponse(
            months=rows,
            summary="Need at least 2 months in kpi_monthly to build a report.",
            risks=["Insufficient data"],
            recommendations=["Insert at least 2 months of KPI data via /kpi."],
        )

    base, target = rows[0], rows[1]
    classic = build_monthly_report(base, target)

    try:
        llm_summary, llm_risk, llm_reco = build_llm_narrative(
            "monthly_report",
            rows,
            style="executive",
        )
        summary = llm_summary
        risks = [llm_risk] if isinstance(llm_risk, str) else (llm_risk or [])
        recommendations = [llm_reco] if isinstance(llm_reco, str) else (llm_reco or [])
    except Exception:
        summary = classic.get("narrative") or "Monthly KPI report generated."
        risks = [classic.get("risk") or "No major risks detected."]
        recommendations = [classic.get("recommendation") or "Monitor KPIs and investigate anomalies."]

    return MonthlyAIReportResponse(
        months=rows,
        summary=summary,
        risks=risks,
        recommendations=recommendations,
    )


# =========================
# /ask (accepts JSON or raw text)
# =========================
class AskAgentRequest(BaseModel):
    question: str


@app.post("/ask")
def ask(payload: AskAgentRequest):
    """
    LLM-based agent with:
      - multi-metric fallback
      - driver decomposition summary
      - decision signals (incl. risk_score)
      - final executive report formatter
    """
    try:
        return ask_agent(payload.question)
    except Exception:
        pass

    q = (payload.question or "").lower()
    multi_keywords = ["performance", "business", "overall", "drop", "why"]

    if any(k in q for k in multi_keywords):
        metrics = ["revenue", "orders", "customers", "aov"]
        outputs = []

        for m in metrics:
            legacy_payload = AskRequest(
                question=f"{m} last_3_months executive",
                style="executive",
            )
            res = ask_legacy(legacy_payload)
            outputs.append(res)

        try:
            driver_summary = build_driver_summary(outputs)
        except Exception as e:
            driver_summary = {
                "status": "error",
                "message": f"driver_summary_failed: {str(e)}",
            }

        try:
            decision = build_decision_signals(driver_summary)
        except Exception as e:
            decision = {
                "risk_signal": "UNKNOWN",
                "trend_direction": "UNKNOWN",
                "confidence": 0.2,
                "risk_score": 10,
                "next_actions": [f"decision_signals_failed: {str(e)}"],
            }

        try:
            final_report = build_final_report(
                {
                    "mode": "multi_metric_fallback",
                    "style": "executive",
                    "driver_summary": driver_summary,
                    "decision": decision,
                    "metrics": metrics,
                }
            )
        except Exception as e:
            final_report = f"final_report_failed: {str(e)}"

        return {
            "mode": "multi_metric_fallback",
            "metrics": metrics,
            "driver_summary": driver_summary,
            "decision": decision,
            "final_report": final_report,
            "results": outputs,
        }

    try:
        legacy_payload = AskRequest(
            question=payload.question,
            style="executive",
        )
        legacy = ask_legacy(legacy_payload)

        try:
            final_report = build_final_report(
                {
                    "mode": "fallback_legacy",
                    "legacy": legacy,
                }
            )
        except Exception as e:
            final_report = f"final_report_failed: {str(e)}"

        return {
            "mode": "fallback_legacy",
            "legacy": legacy,
            "final_report": final_report,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask-text")
def ask_text(question: str = Body(..., media_type="text/plain")):
    return ask(AskAgentRequest(question=question))


@app.post("/ask-legacy", response_model=AskResponse)
def ask_legacy(payload: AskRequest):
    parsed = parse_question(payload.question, style=payload.style)

    sql = build_metric_sql(metric=parsed["metric"], range_=parsed["range"])
    rows = fetch_metric_rows(sql)

    try:
        narrative, risk, recommendation = build_llm_narrative(
            parsed["metric"],
            rows,
            style=parsed["style"],
        )
    except Exception:
        narrative, risk, recommendation = build_narrative(
            parsed["metric"],
            rows,
            style=parsed["style"],
        )

    try:
        insert_analysis_log(
            {
                "metric": parsed["metric"],
                "range": parsed["range"],
                "style": parsed["style"],
                "sql": sql,
                "narrative": narrative,
                "risk": risk,
                "recommendation": recommendation,
            }
        )
    except Exception:
        pass

    result = AnalyzeResponse(
        metric=parsed["metric"],
        range=parsed["range"],
        sql=sql,
        data=rows,
        narrative=narrative,
        risk=risk,
        recommendation=recommendation,
    )

    return AskResponse(
        question=payload.question,
        parsed=parsed,
        result=result,
    )


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest):
    sql = build_metric_sql(metric=payload.metric, range_=payload.range)
    rows = fetch_metric_rows(sql)

    try:
        narrative, risk, recommendation = build_llm_narrative(
            payload.metric,
            rows,
            style=payload.style,
        )
    except Exception:
        narrative, risk, recommendation = build_narrative(
            payload.metric,
            rows,
            style=payload.style,
        )

    try:
        insert_analysis_log(
            {
                "metric": payload.metric,
                "range": payload.range,
                "style": payload.style,
                "sql": sql,
                "narrative": narrative,
                "risk": risk,
                "recommendation": recommendation,
            }
        )
    except Exception:
        pass

    return AnalyzeResponse(
        metric=payload.metric,
        range=payload.range,
        sql=sql,
        data=rows,
        narrative=narrative,
        risk=risk,
        recommendation=recommendation,
    )


@app.get("/history")
def history(limit: int = 20):
    return {"data": fetch_analysis_history(limit=limit)}
