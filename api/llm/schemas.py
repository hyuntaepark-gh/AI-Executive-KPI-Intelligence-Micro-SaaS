from pydantic import BaseModel, Field
from typing import List, Optional, Literal

Metric = Literal["revenue", "orders", "customers", "aov"]
Grain = Literal["day", "week", "month"]
Intent = Literal["explain", "trend", "compare"]
CompareTo = Literal["previous_period", "yoy"]

class DateRange(BaseModel):
    mode: Literal["relative", "absolute"]
    preset: Optional[
        Literal["last_7_days", "last_30_days", "last_quarter", "this_month", "last_month", "yoy"]
    ] = None
    start: Optional[str] = None  # YYYY-MM-DD
    end: Optional[str] = None    # YYYY-MM-DD

class AskPlan(BaseModel):
    intent: Intent
    metrics: List[Metric] = Field(min_length=1)
    grain: Grain = "month"
    date_range: DateRange
    breakdown: Optional[List[str]] = None
    compare_to: Optional[CompareTo] = None
