from datetime import date, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.overview import OverviewKpi
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


def _build_prev_where(
    from_date: str | None,
    to_date: str | None,
) -> tuple[str, dict]:
    """Build WHERE clause for the previous comparison period using Python date math."""
    params: dict = {}
    try:
        if from_date and to_date:
            fd = date.fromisoformat(from_date)
            td = date.fromisoformat(to_date)
            span = td - fd
            prev_start = fd - span
            prev_end = fd
            params["prev_start"] = prev_start
            params["prev_end"] = prev_end
            return "WHERE t.date >= :prev_start AND t.date < :prev_end", params
        elif from_date:
            fd = date.fromisoformat(from_date)
            params["prev_end"] = fd
            params["prev_start"] = fd - timedelta(days=30)
            return "WHERE t.date >= :prev_start AND t.date < :prev_end", params
        elif to_date:
            td = date.fromisoformat(to_date)
            params["prev_end"] = td - timedelta(days=365)
            params["prev_start"] = td - timedelta(days=395)
            return "WHERE t.date >= :prev_start AND t.date < :prev_end", params
    except ValueError:
        pass
    return (
        "WHERE t.date >= (SELECT MAX(date) FROM warehouse.dim_time) - INTERVAL '365 days'"
        " AND t.date < (SELECT MAX(date) FROM warehouse.dim_time) - INTERVAL '335 days'"
    ), params


@cached(ttl=300)
async def get_overview(
    db: AsyncSession,
    from_date: str | None = None,
    to_date: str | None = None,
    types: str | None = None,
    redis=None,
) -> OverviewKpi:
    where, params = _build_filter(from_date, to_date, types)

    offense_join = " JOIN warehouse.dim_offense o ON f.offense_id = o.offense_id" if types else ""

    prev_where, prev_params = _build_prev_where(from_date, to_date)
    params.update(prev_params)

    if types:
        type_list = [t.strip() for t in types.split(",") if t.strip()]
        if type_list:
            placeholders = ", ".join(f":type_{i}" for i in range(len(type_list)))
            prev_where += f" AND o.primary_type IN ({placeholders})"

    sql = text(f"""
        WITH totals AS (
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN f.is_arrested THEN 1 ELSE 0 END) AS total_arrests,
                SUM(CASE WHEN f.is_domestic THEN 1 ELSE 0 END) AS total_domestic
            FROM {SCHEMA}.fact_crime f
            JOIN {SCHEMA}.dim_time t ON f.time_id = t.time_id
            {offense_join}
            {where}
        ),
        prev AS (
            SELECT
                COUNT(*) AS prev_total
            FROM {SCHEMA}.fact_crime f
            JOIN {SCHEMA}.dim_time t ON f.time_id = t.time_id
            {offense_join}
            {prev_where}
        )
        SELECT
            COALESCE(t.total, 0) AS total,
            ROUND(100.0 * t.total_arrests / NULLIF(t.total, 0), 1) AS arrest_rate,
            ROUND(100.0 * t.total_domestic / NULLIF(t.total, 0), 1) AS domestic_pct,
            ROUND(
                100.0 * (t.total - COALESCE(p.prev_total, 0))
                / NULLIF(p.prev_total, 0), 1
            ) AS delta_pct,
            COALESCE(p.prev_total, 0) AS prev_total
        FROM totals t, prev p
    """)

    result = await db.execute(sql, params)
    row = result.one()
    return OverviewKpi(
        total=int(row.total or 0),
        arrest_rate=float(row.arrest_rate or 0),
        domestic_pct=float(row.domestic_pct or 0),
        delta_pct=float(row.delta_pct or 0),
        prev_total=int(row.prev_total or 0),
    )
