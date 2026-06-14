from fastapi import APIRouter, Depends, Query
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_redis
from app.schemas.arrests import DistrictArrest
from app.schemas.crime_types import CrimeTypeArrest
from app.services.arrests import get_arrests_by_district, get_arrests_by_type

router = APIRouter()


@router.get("/arrests/by-district", response_model=list[DistrictArrest])
async def arrests_by_district(
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    types: str | None = Query(None, description="Comma-separated primary types"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> list[DistrictArrest]:
    return await get_arrests_by_district(  # type: ignore[no-any-return]
        db, redis=redis, from_date=from_date,
        to_date=to_date, types=types,
    )


@router.get("/arrests/by-type", response_model=list[CrimeTypeArrest])
async def arrests_by_type(
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    types: str | None = Query(None, description="Comma-separated primary types"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> list[CrimeTypeArrest]:
    return await get_arrests_by_type(  # type: ignore[no-any-return]
        db, redis=redis, from_date=from_date,
        to_date=to_date, types=types,
    )
