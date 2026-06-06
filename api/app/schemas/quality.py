from pydantic import BaseModel


class GeResult(BaseModel):
    success_pct: float | None = None
    last_run: str | None = None


class DbtResult(BaseModel):
    passed: int | None = None
    failed: int | None = None
    last_run: str | None = None


class QualitySummary(BaseModel):
    great_expectations: GeResult
    dbt: DbtResult