from pydantic import BaseModel


class TimeseriesPoint(BaseModel):
    ts: str
    count: int
    arrests: int = 0


class ForecastPoint(BaseModel):
    ts: str
    yhat: float
    yhat_lower: float
    yhat_upper: float


class ForecastBundle(BaseModel):
    history: list[TimeseriesPoint]
    forecast: list[ForecastPoint]


class AnomalyPoint(BaseModel):
    ts: str
    z: float
    count: int


class Heatmap(BaseModel):
    matrix: list[list[int]]


class TypeTrendPoint(BaseModel):
    primary_type: str
    ts: str
    count: int
    arrests: int = 0