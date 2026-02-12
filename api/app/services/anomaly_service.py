from typing import Any, Dict, List, Optional, Tuple


def _abs(x: Optional[float]) -> float:
    return abs(x) if x is not None else 0.0


def build_anomalies(driver_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Build simple anomaly list from changes_pct:
    - top movers by absolute % change
    """
    if not driver_summary or driver_summary.get("status") != "ok":
        return []

    changes = driver_summary.get("changes_pct") or {}
    items: List[Tuple[str, Optional[float]]] = [
        ("revenue", changes.get("revenue")),
        ("orders", changes.get("orders")),
        ("aov", changes.get("aov")),
        ("customers", changes.get("customers")),
    ]

    items_sorted = sorted(items, key=lambda x: _abs(x[1]), reverse=True)

    anomalies: List[Dict[str, Any]] = []
    for metric, pct in items_sorted[:3]:
        if pct is None:
            continue
        anomalies.append(
            {
                "metric": metric,
                "pct_change": round(float(pct), 2),
                "severity": "HIGH" if _abs(pct) >= 15 else ("MEDIUM" if _abs(pct) >= 8 else "LOW"),
            }
        )

    return anomalies
