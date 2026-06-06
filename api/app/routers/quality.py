from fastapi import APIRouter

from app.schemas.quality import QualitySummary
from app.services.quality import get_quality_summary

router = APIRouter()


@router.get("/quality/summary", response_model=QualitySummary)
async def quality_summary():
    return await get_quality_summary()