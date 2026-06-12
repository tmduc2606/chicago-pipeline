from fastapi import APIRouter, Depends, Query
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_redis
from app.schemas.crime_types import CrimeTypeCount
from app.schemas.timeseries import TimeseriesPoint, TypeTrendPoint
from app.services.crime_types import get_multi_type_trend, get_top_types, get_type_trend

router = APIRouter()


@router.get("/crime-types/top", response_model=list[CrimeTypeCount])
async def crime_types_top(
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    types: str | None = Query(None, description="Comma-separated primary types"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    return await get_top_types(
        db, redis=redis, from_date=from_date,
        to_date=to_date, types=types, limit=limit,
    )


@router.get("/crime-types/trend", response_model=list[TimeseriesPoint])
async def crime_type_trend(
    type: str = Query(..., alias="type"),
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    return await get_type_trend(
        db, redis=redis, primary_type=type,
        from_date=from_date, to_date=to_date,
    )


@router.get("/crime-types/trends", response_model=list[TypeTrendPoint])
async def crime_types_trends(
    types: str = Query(..., description="Comma-separated primary types"),
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    return await get_multi_type_trend(
        db, redis=redis, types=types,
        from_date=from_date, to_date=to_date,
    )
