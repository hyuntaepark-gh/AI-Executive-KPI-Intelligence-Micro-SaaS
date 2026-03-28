import json
from api.llm.planner import make_plan
from api.app.sql.builder import resolve_date_range, build_kpi_sql
from api.db.runner import run_sql
from api.llm.summarizer import summarize


def _json_safe(value):
    """
    Convert DB/query results into JSON-serializable Python objects.
    Dates/datetimes become strings automatically.
    """
    return json.loads(json.dumps(value, default=str))


def ask_agent(question: str) -> dict:
    plan = make_plan(question)

    start, end = resolve_date_range(plan.date_range.model_dump())

    results = {}
    for metric in plan.metrics:
        sql, params = build_kpi_sql(
            metric=metric,
            grain=plan.grain,
            start=start,
            end=end,
            breakdown=plan.breakdown,
        )
        raw_rows = run_sql(sql, params)
        results[metric] = _json_safe(raw_rows)

    safe_plan = _json_safe(plan.model_dump())

    report = summarize(
        question=question,
        plan=safe_plan,
        results=results,
    )

    return {
        "question": question,
        "plan": safe_plan,
        "results": results,
        "report": report,
    }