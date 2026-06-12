from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_redis
from app.services.export import get_export_csv

router = APIRouter()


@router.get("/export/csv", response_class=PlainTextResponse)
async def export_csv(
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    types: str | None = Query(None, description="Comma-separated primary types"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    csv = await get_export_csv(
        db, redis=redis,
        from_date=from_date, to_date=to_date, types=types,
    )
    return PlainTextResponse(
        content=csv,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=crime-data.csv"},
    )
