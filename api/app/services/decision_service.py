from typing import Any, Dict, List, Optional


def _abs(x: Optional[float]) -> float:
    return abs(x) if x is not None else 0.0


def build_decision_signals(driver_summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert driver_summary into decision-grade signals:
      - risk_signal: HIGH/MEDIUM/LOW
      - trend_direction: UP/DOWN/FLAT
      - confidence: 0~1
      - risk_score: 0~100
      - next_actions: list[str]
    """
    if not driver_summary or driver_summary.get("status") != "ok":
        return {
            "risk_signal": "UNKNOWN",
            "trend_direction": "UNKNOWN",
            "confidence": 0.2,
            "risk_score": 10,
            "next_actions": ["Insert at least 2 months of KPI data and rerun analysis."],
        }

    changes = driver_summary.get("changes_pct") or {}
    rev = changes.get("revenue")
    orders = changes.get("orders")
    aov = changes.get("aov")
    customers = changes.get("customers")
    main_driver = driver_summary.get("main_driver")

    # Trend direction
    if rev is None:
        trend = "UNKNOWN"
    elif rev <= -2:
        trend = "DOWN"
    elif rev >= 2:
        trend = "UP"
    else:
        trend = "FLAT"

    # Risk thresholds
    risk = "LOW"
    driver_drop = None
    if main_driver == "orders":
        driver_drop = orders
    elif main_driver == "aov":
        driver_drop = aov

    if rev is not None:
        if rev <= -15:
            risk = "HIGH"
        elif rev <= -8 and (driver_drop is not None and driver_drop <= -10):
            risk = "HIGH"
        elif rev <= -8:
            risk = "MEDIUM"

    # If revenue is flat but driver is volatile, still MEDIUM
    if risk == "LOW" and (driver_drop is not None and driver_drop <= -10):
        risk = "MEDIUM"

    # Confidence: more complete metrics => higher
    filled = sum(v is not None for v in [rev, orders, aov, customers])
    confidence = 0.55 + 0.1 * filled  # 0.65~0.95
    confidence = max(0.0, min(1.0, confidence))

    # Risk score (0~100)
    # Base score from categorical risk + magnitude boost from revenue change
    score = 10
    if risk == "MEDIUM":
        score = 45
    elif risk == "HIGH":
        score = 80

    # Magnitude boost: abs(rev)*4 (e.g., 10% -> 40 points), capped
    if rev is not None:
        try:
            score = min(100, max(score, int(min(100, _abs(float(rev)) * 4))))
        except Exception:
            pass

    actions: List[str] = []
    if risk == "HIGH":
        actions.append("Investigate top contributors immediately (segment, channel, region).")
        actions.append("Run anomaly checks on ingestion/ETL and KPI definitions.")
    if main_driver == "orders":
        actions.append("Break down orders by acquisition channel and customer cohort.")
        actions.append("Check cancellation rate, stockouts, and traffic-to-order conversion.")
    if main_driver == "aov":
        actions.append("Break down AOV by product mix and discount/price bands.")
        actions.append("Check return/refund impact and pricing/promotions changes.")
    if customers is not None and customers <= -8:
        actions.append("Analyze churn/retention: new vs returning customers, reactivation rate.")

    if not actions:
        actions.append("Monitor KPIs and set alert thresholds for significant deviations.")

    return {
        "risk_signal": risk,
        "trend_direction": trend,
        "confidence": round(confidence, 2),
        "risk_score": score,
        "next_actions": actions[:6],
    }
