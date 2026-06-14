from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_redis
from app.schemas.filters import FilterOptions
from app.services.filters import get_filters

router = APIRouter()


@router.get("/filters", response_model=FilterOptions)
async def filters(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> FilterOptions:
    return await get_filters(db, redis=redis)  # type: ignore[no-any-return]