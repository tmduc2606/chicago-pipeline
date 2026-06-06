from pydantic import BaseModel


class DagStatus(BaseModel):
    dag_id: str
    last_run: str | None = None
    state: str


class DagRun(BaseModel):
    run_id: str
    dag_id: str
    state: str
    start: str | None = None
    end: str | None = None