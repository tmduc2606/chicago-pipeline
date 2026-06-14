from datetime import date
from typing import Any

from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.geo import ChoroplethBucket, GeoCluster
from app.services.cache import cached

SCHEMA = "warehouse"


ALLOWED_GROUP_COLS = {"district", "community_area"}
ALLOWED_METRICS = {"count", "arrest_rate"}

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
async def get_geo_clusters(
    db: AsyncSession,
    from_date: str | None = None,
    to_date: str | None = None,
    types: str | None = None,
    zoom: int = 8,
    redis: Redis | None = None,
) -> list[GeoCluster]:
    grid_size = max(0.001, 0.05 / (2 ** max(0, zoom - 8)))
    where, params = _build_filter(from_date, to_date, types)

    sql = text(f"""
        SELECT
            ROUND(l.latitude::numeric / :grid) * :grid AS lat_bucket,
            ROUND(l.longitude::numeric / :grid) * :grid AS lng_bucket,
            ROUND(AVG(l.latitude)::numeric, 6) AS lat,
            ROUND(AVG(l.longitude)::numeric, 6) AS lng,
            COUNT(*)::int AS cnt
        FROM {SCHEMA}.fact_crime f
        JOIN {SCHEMA}.dim_location l ON f.location_id = l.location_id
        JOIN {SCHEMA}.dim_time t ON f.time_id = t.time_id
        LEFT JOIN {SCHEMA}.dim_offense o ON f.offense_id = o.offense_id
        {where}
        GROUP BY lat_bucket, lng_bucket
        HAVING COUNT(*) > 0
        ORDER BY cnt DESC
    """)
    result = await db.execute(sql, {**params, "grid": grid_size})
    rows = result.fetchall()
    return [
        GeoCluster(
            h3=f"{r.lat_bucket},{r.lng_bucket}",
            lat=float(r.lat),
            lng=float(r.lng),
            count=r.cnt,
        )
        for r in rows
    ]


@cached(ttl=300)
async def get_choropleth(
    db: AsyncSession,
    level: str = "district",
    metric: str = "count",
    from_date: str | None = None,
    to_date: str | None = None,
    types: str | None = None,
    redis: Redis | None = None,
) -> list[ChoroplethBucket]:
    if level not in ALLOWED_GROUP_COLS:
        raise ValueError(f"Invalid level: {level!r}")
    if metric not in ALLOWED_METRICS:
        raise ValueError(f"Invalid metric: {metric!r}")
    group_col = level
    val_expr = "COUNT(*)::float" if metric == "count" else (
        "ROUND(100.0 * SUM(CASE WHEN f.is_arrested THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 1)"
    )
    where, params = _build_filter(from_date, to_date, types)

    sql = text(f"""
        SELECT {group_col}::text AS key,
               {group_col}::text AS label,
               {val_expr} AS value,
               COALESCE(ROUND(AVG(l.latitude)::numeric, 6), 0)::float AS lat,
               COALESCE(ROUND(AVG(l.longitude)::numeric, 6), 0)::float AS lng
        FROM {SCHEMA}.fact_crime f
        JOIN {SCHEMA}.dim_time t ON f.time_id = t.time_id
        JOIN {SCHEMA}.dim_location l ON f.location_id = l.location_id
        JOIN {SCHEMA}.dim_offense o ON f.offense_id = o.offense_id
        {where}
        GROUP BY {group_col}
        HAVING {group_col} IS NOT NULL
        ORDER BY value DESC
    """)
    result = await db.execute(sql, params)
    rows = result.fetchall()
    return [
        ChoroplethBucket(
            key=str(r.key), label=str(r.label), value=float(r.value),
            lat=float(r.lat), lng=float(r.lng),
        )
        for r in rows
    ]
