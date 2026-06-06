from fastapi import APIRouter, Depends, Query
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_redis
from app.schemas.overview import OverviewKpi
from app.services.overview import get_overview

router = APIRouter()


@router.get("/overview", response_model=OverviewKpi)
async def overview(
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    types: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    return await get_overview(
        db, redis=redis,
        from_date=from_date, to_date=to_date, types=types,
    )