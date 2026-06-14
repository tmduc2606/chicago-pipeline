from fastapi import APIRouter, Query

from app.schemas.pipeline import DagRun, DagStatus
from app.services.pipeline import get_pipeline_runs, get_pipeline_status

router = APIRouter()


@router.get("/pipeline/status", response_model=list[DagStatus])
async def pipeline_status() -> list[DagStatus]:
    return await get_pipeline_status()


@router.get("/pipeline/runs", response_model=list[DagRun])
async def pipeline_runs(
    dag_id: str = Query(...),
    limit: int = Query(10, ge=1, le=100),
) -> list[DagRun]:
    return await get_pipeline_runs(dag_id, limit=limit)