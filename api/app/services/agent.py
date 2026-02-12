from api.llm.planner import make_plan
from api.app.sql.builder import resolve_date_range, build_kpi_sql
from api.db.runner import run_sql
from api.llm.summarizer import summarize

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
        results[metric] = run_sql(sql, params)

    report = summarize(
        question=question,
        plan=plan.model_dump(),
        results=results,
    )

    return {
        "question": question,
        "plan": plan.model_dump(),
        "results": results,
        "report": report,
    }
