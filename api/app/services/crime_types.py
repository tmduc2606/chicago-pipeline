from datetime import date

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.crime_types import CrimeTypeCount
from app.schemas.timeseries import TimeseriesPoint
from app.services.cache import cached

SCHEMA = "warehouse"


@cached(ttl=300)
async def get_top_types(
    db: AsyncSession,
    from_date: str | None = None,
    to_date: str | None = None,
    types: str | None = None,
    limit: int = 10,
    redis=None,
) -> list[CrimeTypeCount]:
    conditions = []
    params: dict = {"limit": limit}
    if from_date:
        try:
            params["from_date"] = date.fromisoformat(from_date)
            conditions.append("t.date >= :from_date")
        except ValueError:
            pass
    if to_date:
        try:
            params["to_date"] = date.fromisoformat(to_date)
            conditions.append("t.date <= :to_date")
        except ValueError:
            pass
    if types:
        type_list = [t.strip() for t in types.split(",") if t.strip()]
        if type_list:
            placeholders = ", ".join(f":type_{i}" for i in range(len(type_list)))
            conditions.append(f"o.primary_type IN ({placeholders})")
            for i, t in enumerate(type_list):
                params[f"type_{i}"] = t
    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    sql = text(f"""
        SELECT o.primary_type, COUNT(*)::int AS count
        FROM {SCHEMA}.fact_crime f
        JOIN {SCHEMA}.dim_time t ON f.time_id = t.time_id
        JOIN {SCHEMA}.dim_offense o ON f.offense_id = o.offense_id
        {where}
        GROUP BY o.primary_type
        ORDER BY count DESC
        LIMIT :limit
    """)
    result = await db.execute(sql, params)
    rows = result.fetchall()
    return [CrimeTypeCount(primary_type=str(r.primary_type), count=r.count) for r in rows]


@cached(ttl=300)
async def get_type_trend(
    db: AsyncSession,
    primary_type: str,
    from_date: str | None = None,
    to_date: str | None = None,
    redis=None,
) -> list[TimeseriesPoint]:
    conditions = ["o.primary_type = :primary_type"]
    params: dict = {"primary_type": primary_type}
    if from_date:
        conditions.append("t.date >= :from_date")
        params["from_date"] = date.fromisoformat(from_date)
    if to_date:
        conditions.append("t.date <= :to_date")
        params["to_date"] = date.fromisoformat(to_date)
    where = f"WHERE {' AND '.join(conditions)}"

    sql = text(f"""
        SELECT t.date AS ts,
               COUNT(*)::int AS count,
               SUM(CASE WHEN f.is_arrested THEN 1 ELSE 0 END)::int AS arrests
        FROM {SCHEMA}.fact_crime f
        JOIN {SCHEMA}.dim_time t ON f.time_id = t.time_id
        JOIN {SCHEMA}.dim_offense o ON f.offense_id = o.offense_id
        {where}
        GROUP BY t.date
        ORDER BY t.date
    """)
    result = await db.execute(sql, params)
    rows = result.fetchall()
    return [
        TimeseriesPoint(ts=str(r.ts), count=r.count, arrests=r.arrests or 0)
        for r in rows
    ]
