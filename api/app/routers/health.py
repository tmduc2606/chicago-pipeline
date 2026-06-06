from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_redis

router = APIRouter()


@router.get("/health/live")
async def liveness():
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness(db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)):
    try:
        await db.execute(text("SELECT 1"))
        await redis.ping()
        return {"status": "ready"}
    except Exception:
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=503, content={"status": "not ready"})


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)):
    checks = {"postgres": False, "redis": False}
    try:
        await db.execute(text("SELECT 1"))
        checks["postgres"] = True
    except Exception:
        pass
    try:
        await redis.ping()
        checks["redis"] = True
    except Exception:
        pass
    all_healthy = all(checks.values())
    from fastapi.responses import JSONResponse
    status_code = 200 if all_healthy else 503
    status_msg = "healthy" if all_healthy else "degraded"
    return JSONResponse(
        status_code=status_code,
        content={"status": status_msg, "checks": checks},
    )