from fastapi import APIRouter, Depends, Query
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_redis
from app.schemas.timeseries import AnomalyPoint, ForecastBundle, Heatmap, TimeseriesPoint
from app.services.timeseries import get_anomalies, get_forecast, get_heatmap, get_timeseries

router = APIRouter()


@router.get("/timeseries", response_model=list[TimeseriesPoint])
async def timeseries(
    granularity: str = Query("daily", pattern="^(daily|weekly|monthly)$"),
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> list[TimeseriesPoint]:
    return await get_timeseries(  # type: ignore[no-any-return]
        db, redis=redis, granularity=granularity,
        from_date=from_date, to_date=to_date,
    )


@router.get("/timeseries/forecast", response_model=ForecastBundle)
async def forecast(
    horizon: int = Query(14, ge=1, le=60),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> ForecastBundle:
    return await get_forecast(db, redis=redis, horizon=horizon)  # type: ignore[no-any-return]


@router.get("/timeseries/anomalies", response_model=list[AnomalyPoint])
async def anomalies(
    z: float = Query(3.0),
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> list[AnomalyPoint]:
    return await get_anomalies(  # type: ignore[no-any-return]
        db, redis=redis, z=z,
        from_date=from_date, to_date=to_date,
    )


@router.get("/heatmap", response_model=Heatmap)
async def heatmap(
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    types: str | None = Query(None, description="Comma-separated primary types"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> Heatmap:
    return await get_heatmap(db, redis=redis, from_date=from_date, to_date=to_date, types=types)  # type: ignore[no-any-return]
