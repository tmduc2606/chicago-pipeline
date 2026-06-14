from fastapi import APIRouter, Depends, Query
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_redis
from app.schemas.context import BooleanSplit, LocationCount
from app.services.context import get_domestic_split, get_top_locations

router = APIRouter()


@router.get("/context/domestic", response_model=BooleanSplit)
async def domestic_split(
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    types: str | None = Query(None, description="Comma-separated primary types"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> BooleanSplit:
    return await get_domestic_split(  # type: ignore[no-any-return]
        db, redis=redis, from_date=from_date,
        to_date=to_date, types=types,
    )


@router.get("/context/location", response_model=list[LocationCount])
async def top_locations(
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    types: str | None = Query(None, description="Comma-separated primary types"),
    limit: int = Query(15, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> list[LocationCount]:
    return await get_top_locations(  # type: ignore[no-any-return]
        db, redis=redis, from_date=from_date,
        to_date=to_date, types=types, limit=limit,
    )
