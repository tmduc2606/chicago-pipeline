from datetime import date
from io import StringIO
from typing import Any

from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.cache import cached

SCHEMA = "warehouse"


@cached(ttl=300)
async def get_export_csv(
    db: AsyncSession,
    from_date: str | None = None,
    to_date: str | None = None,
    types: str | None = None,
    redis: Redis | None = None,
) -> str:
    conditions: list[str] = []
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

    sql = text(f"""
        SELECT t.date,
               o.primary_type,
               f.is_arrested,
               f.is_domestic,
               l.location_description,
               l.district,
               l.community_area
        FROM {SCHEMA}.fact_crime f
        JOIN {SCHEMA}.dim_time t ON f.time_id = t.time_id
        JOIN {SCHEMA}.dim_offense o ON f.offense_id = o.offense_id
        JOIN {SCHEMA}.dim_location l ON f.location_id = l.location_id
        {where}
        ORDER BY t.date DESC
        LIMIT 10000
    """)
    result = await db.execute(sql, params)
    rows = result.fetchall()

    buf = StringIO()
    buf.write("date,primary_type,is_arrested,is_domestic,location_description,district,community_area\n")
    for r in rows:
        buf.write(
            f"{r.date},{r.primary_type},{r.is_arrested},{r.is_domestic},"
            f"{r.location_description},{r.district},{r.community_area}\n"
        )
    return buf.getvalue()
