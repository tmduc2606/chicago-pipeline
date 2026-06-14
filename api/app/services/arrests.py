from datetime import date
from typing import Any

from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.arrests import DistrictArrest
from app.schemas.crime_types import CrimeTypeArrest
from app.services.cache import cached

SCHEMA = "warehouse"


def _build_filter(
    from_date: str | None = None,
    to_date: str | None = None,
    types: str | None = None,
) -> tuple[str, dict[str, Any]]:
    conditions = []
    params: dict[str, Any] = {}
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
    return where, params


@cached(ttl=300)
async def get_arrests_by_district(
    db: AsyncSession,
    from_date: str | None = None,
    to_date: str | None = None,
    types: str | None = None,
    redis: Redis | None = None,
) -> list[DistrictArrest]:
    where, params = _build_filter(from_date, to_date, types)

    sql = text(f"""
        SELECT l.district,
               COUNT(*)::int AS total,
               SUM(CASE WHEN f.is_arrested THEN 1 ELSE 0 END)::int AS arrests,
               ROUND(
                   100.0 * SUM(CASE WHEN f.is_arrested THEN 1 ELSE 0 END)
                   / NULLIF(COUNT(*), 0), 1
               ) AS arrest_rate
        FROM {SCHEMA}.fact_crime f
        JOIN {SCHEMA}.dim_time t ON f.time_id = t.time_id
        JOIN {SCHEMA}.dim_location l ON f.location_id = l.location_id
        JOIN {SCHEMA}.dim_offense o ON f.offense_id = o.offense_id
        {where}
        GROUP BY l.district
        ORDER BY l.district
    """)
    result = await db.execute(sql, params)
    rows = result.fetchall()
    return [
        DistrictArrest(
            district=int(r.district),
            arrest_rate=float(r.arrest_rate or 0),
            total=r.total,
        )
        for r in rows
    ]


@cached(ttl=300)
async def get_arrests_by_type(
    db: AsyncSession,
    from_date: str | None = None,
    to_date: str | None = None,
    types: str | None = None,
    redis: Redis | None = None,
) -> list[CrimeTypeArrest]:
    where, params = _build_filter(from_date, to_date, types)

    sql = text(f"""
        SELECT o.primary_type,
               ROUND(
                   100.0 * SUM(CASE WHEN f.is_arrested THEN 1 ELSE 0 END)
                   / NULLIF(COUNT(*), 0), 1
               ) AS arrest_rate
        FROM {SCHEMA}.fact_crime f
        JOIN {SCHEMA}.dim_time t ON f.time_id = t.time_id
        JOIN {SCHEMA}.dim_offense o ON f.offense_id = o.offense_id
        {where}
        GROUP BY o.primary_type
        ORDER BY o.primary_type
    """)
    result = await db.execute(sql, params)
    rows = result.fetchall()
    return [
        CrimeTypeArrest(
            primary_type=str(r.primary_type),
            arrest_rate=float(r.arrest_rate or 0),
        )
        for r in rows
    ]
