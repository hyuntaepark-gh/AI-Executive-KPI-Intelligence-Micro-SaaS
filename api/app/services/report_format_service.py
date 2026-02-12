from __future__ import annotations

from typing import Any, Dict, List


def build_final_report(response: Dict[str, Any]) -> str:
    """
    Build a human-readable report string for Swagger/demo.
    Works for both:
    - mode == "multi_metric_fallback" (with driver_summary/decision)
    - mode == "fallback_legacy"
    - direct agent responses (if they already contain similar fields)
    """
    mode = (response or {}).get("mode", "unknown")

    # multi-metric fallback
    if mode == "multi_metric_fallback":
        driver = (response or {}).get("driver_summary", {}) or {}
        decision = (response or {}).get("decision", {}) or {}

        exec_sum = driver.get("executive_summary") or driver.get("executive_takeaway") or ""
        main_driver = driver.get("main_driver") or "unknown"
        changes = driver.get("changes_pct") or {}

        rev = changes.get("revenue")
        orders = changes.get("orders")
        aov = changes.get("aov")
        customers = changes.get("customers")

        risk_signal = decision.get("risk_signal", "UNKNOWN")
        trend = decision.get("trend_direction", "UNKNOWN")
        confidence = decision.get("confidence", None)
        next_actions: List[str] = decision.get("next_actions") or []

        lines: List[str] = []
        lines.append("EXECUTIVE KPI SUMMARY")
        lines.append(f"Mode: {mode}")
        if exec_sum:
            lines.append(f"Executive Summary: {exec_sum}")
        lines.append(f"Main Driver: {main_driver}")

        def _fmt(x):
            if x is None:
                return "n/a"
            try:
                return f"{float(x):.1f}%"
            except Exception:
                return str(x)

        lines.append("MoM Changes:")
        lines.append(f"- Revenue: {_fmt(rev)}")
        lines.append(f"- Orders: {_fmt(orders)}")
        lines.append(f"- AOV: {_fmt(aov)}")
        lines.append(f"- Customers: {_fmt(customers)}")

        lines.append("Decision Signals:")
        lines.append(f"- Risk: {risk_signal}")
        lines.append(f"- Trend: {trend}")
        if confidence is not None:
            lines.append(f"- Confidence: {confidence}")

        if next_actions:
            lines.append("Next Actions:")
            for a in next_actions[:5]:
                lines.append(f"- {a}")

        return "\n".join(lines)

    # single legacy fallback wrapper
    if mode == "fallback_legacy":
        legacy = (response or {}).get("legacy") or {}
        return build_final_report(legacy)

    # legacy endpoint output (AskResponse shape)
    if "result" in (response or {}):
        result = response.get("result") or {}
        parsed = response.get("parsed") or {}

        metric = parsed.get("metric") or result.get("metric") or "unknown"
        range_ = parsed.get("range") or result.get("range") or "unknown"
        narrative = result.get("narrative") or ""
        risk = result.get("risk") or ""
        reco = result.get("recommendation") or ""

        lines = [
            "KPI ANSWER (LEGACY)",
            f"Metric: {metric}",
            f"Range: {range_}",
        ]
        if narrative:
            lines.append(f"Narrative: {narrative}")
        if risk:
            lines.append(f"Risk: {risk}")
        if reco:
            lines.append(f"Recommendation: {reco}")

        return "\n".join(lines)

    # unknown / agent direct
    return f"Mode: {mode}\nRaw response keys: {list((response or {}).keys())}"
