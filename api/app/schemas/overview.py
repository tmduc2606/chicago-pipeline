from pydantic import BaseModel


class OverviewKpi(BaseModel):
    total: int
    arrest_rate: float
    domestic_pct: float
    delta_pct: float
    prev_total: int = 0