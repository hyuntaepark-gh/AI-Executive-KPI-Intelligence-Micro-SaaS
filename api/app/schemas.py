from datetime import date
from typing import Optional, Literal
from pydantic import BaseModel, Field

class KPIIn(BaseModel):
    month: date
    revenue: float
    orders: int
    customers: int
    aov: float

class AnalyzeRequest(BaseModel):
    metric: Literal["revenue", "orders", "aov", "customers"] = "revenue"
    range: Literal["last_3_months", "last_6_months", "all"] = "last_3_months"
    style: Literal["brief", "executive", "detailed"] = "executive"

class AnalyzeResponse(BaseModel):
    metric: str
    range: str
    sql: str
    data: list[dict]
    narrative: str
    risk: str
    recommendation: str
