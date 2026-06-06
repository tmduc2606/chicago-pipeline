from datetime import date

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.context import BooleanSplit, LocationCount
from app.services.cache import cached

SCHEMA = "warehouse"


def _build_filter(
    from_date: str | None = None,
    to_date: str | None = None,
    types: str | None = None,
) -> tuple[str, dict]:
    conditions = []
    params: dict = {}
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
async def get_domestic_split(
    db: AsyncSession,
    from_date: str | None = None,
    to_date: str | None = None,
    types: str | None = None,
    redis=None,
) -> BooleanSplit:
    where, params = _build_filter(from_date, to_date, types)
    join = f"""
        JOIN {SCHEMA}.dim_time t ON f.time_id = t.time_id
        JOIN {SCHEMA}.dim_offense o ON f.offense_id = o.offense_id
    """ if where else ""

    sql = text(f"""
        SELECT
            COALESCE(SUM(CASE WHEN f.is_domestic THEN 1 ELSE 0 END), 0)::int AS true_count,
            COALESCE(SUM(CASE WHEN NOT f.is_domestic THEN 1 ELSE 0 END), 0)::int AS false_count
        FROM {SCHEMA}.fact_crime f
        {join}
        {where}
    """)
    result = await db.execute(sql, params)
    row = result.one()
    return BooleanSplit(true_count=int(row.true_count), false_count=int(row.false_count))


@cached(ttl=300)
async def get_top_locations(
    db: AsyncSession,
    from_date: str | None = None,
    to_date: str | None = None,
    types: str | None = None,
    limit: int = 15,
    redis=None,
) -> list[LocationCount]:
    where, params = _build_filter(from_date, to_date, types)
    params["limit"] = limit
    join = f"""
        JOIN {SCHEMA}.dim_time t ON f.time_id = t.time_id
        JOIN {SCHEMA}.dim_offense o ON f.offense_id = o.offense_id
    """ if where else ""

    sql = text(f"""
        SELECT l.location_description, COUNT(*)::int AS count
        FROM {SCHEMA}.fact_crime f
        LEFT JOIN {SCHEMA}.dim_location l ON f.location_id = l.location_id
        {join}
        {where}
        {"AND" if where else "WHERE"} l.location_description IS NOT NULL
        GROUP BY l.location_description
        ORDER BY count DESC
        LIMIT :limit
    """)
    result = await db.execute(sql, params)
    rows = result.fetchall()
    return [
        LocationCount(
            location_description=str(r.location_description),
            count=r.count,
        )
        for r in rows
    ]
