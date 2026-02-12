from typing import Any, Dict, List, Optional


def _fmt_pct(x: Optional[float]) -> str:
    if x is None:
        return "n/a"
    try:
        return f"{float(x):.1f}%"
    except Exception:
        return str(x)


def build_final_report(payload: Dict[str, Any]) -> str:
    """
    Build a human-readable executive report string for Swagger/demo.
    Expects payload to include driver_summary + decision for multi-metric mode.
    """
    mode = (payload or {}).get("mode", "unknown")

    if mode == "multi_metric_fallback":
        driver = (payload or {}).get("driver_summary") or {}
        decision = (payload or {}).get("decision") or {}
        style = (payload or {}).get("style") or "executive"

        if driver.get("status") != "ok":
            return "Executive report unavailable due to insufficient KPI data."

        changes = driver.get("changes_pct") or {}
        exec_sum = driver.get("executive_summary") or driver.get("executive_takeaway") or ""
        main_driver = driver.get("main_driver") or "unknown"

        risk = decision.get("risk_signal", "UNKNOWN")
        trend = decision.get("trend_direction", "UNKNOWN")
        confidence = decision.get("confidence", None)
        risk_score = decision.get("risk_score", None)

        lines: List[str] = []
        if style == "basic":
            lines.append("KPI SUMMARY")
        else:
            lines.append("EXECUTIVE KPI BRIEF")

        if exec_sum:
            lines.append(exec_sum)

        lines.append(f"Main driver: {main_driver}")
        lines.append(
            "MoM changes: "
            f"Revenue {_fmt_pct(changes.get('revenue'))}, "
            f"Orders {_fmt_pct(changes.get('orders'))}, "
            f"AOV {_fmt_pct(changes.get('aov'))}, "
            f"Customers {_fmt_pct(changes.get('customers'))}"
        )

        tail = f"Signals: Trend={trend}, Risk={risk}"
        if risk_score is not None:
            tail += f" ({risk_score}/100)"
        if confidence is not None:
            tail += f", Confidence={confidence}"
        lines.append(tail)

        next_actions = decision.get("next_actions") or []
        if style != "basic" and next_actions:
            lines.append("Next actions:")
            for a in next_actions[:5]:
                lines.append(f"- {a}")

        return "\n".join(lines)

    if mode == "fallback_legacy":
        return "Legacy analysis completed. See `legacy` for details."

    return f"Mode={mode}. Keys={list((payload or {}).keys())}"
