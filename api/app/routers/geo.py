from fastapi import APIRouter, Depends, Query
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_redis
from app.schemas.geo import ChoroplethBucket, GeoCluster
from app.services.geo import get_choropleth, get_geo_clusters

router = APIRouter()


@router.get("/geo/clusters", response_model=list[GeoCluster])
async def geo_clusters(
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    types: str | None = Query(None, description="Comma-separated primary types"),
    zoom: int = Query(8),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> list[GeoCluster]:
    return await get_geo_clusters(  # type: ignore[no-any-return]
        db, redis=redis, from_date=from_date,
        to_date=to_date, types=types, zoom=zoom,
    )


@router.get("/geo/choropleth", response_model=list[ChoroplethBucket])
async def choropleth(
    level: str = Query("district", pattern="^(district|community_area)$"),
    metric: str = Query("count", pattern="^(count|arrest_rate)$"),
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    types: str | None = Query(None, description="Comma-separated primary types"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> list[ChoroplethBucket]:
    return await get_choropleth(  # type: ignore[no-any-return]
        db, redis=redis, level=level, metric=metric,
        from_date=from_date, to_date=to_date, types=types,
    )
