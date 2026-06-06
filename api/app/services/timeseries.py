from datetime import date

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.timeseries import (
    AnomalyPoint,
    ForecastBundle,
    ForecastPoint,
    Heatmap,
    TimeseriesPoint,
)
from app.services.cache import cached

SCHEMA = "warehouse"


def _build_date_filter(
    from_date: str | None,
    to_date: str | None,
    prefix: str = "t.",
) -> tuple[str, dict]:
    conditions = []
    params: dict = {}
    if from_date:
        try:
            params["from_date"] = date.fromisoformat(from_date)
            conditions.append(f"{prefix}date >= :from_date")
        except ValueError:
            pass
    if to_date:
        try:
            params["to_date"] = date.fromisoformat(to_date)
            conditions.append(f"{prefix}date <= :to_date")
        except ValueError:
            pass
    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    return where, params


@cached(ttl=300)
async def get_timeseries(
    db: AsyncSession,
    granularity: str = "daily",
    from_date: str | None = None,
    to_date: str | None = None,
    redis=None,
) -> list[TimeseriesPoint]:
    where, params = _build_date_filter(from_date, to_date)
    if granularity == "daily":
        group_expr = "t.date"
    elif granularity == "weekly":
        group_expr = "date_trunc('week', t.date)"
    else:
        group_expr = "date_trunc('month', t.date)"
    sql = text(f"""
        SELECT {group_expr} AS ts,
               COUNT(*)::int AS count,
               SUM(CASE WHEN f.is_arrested THEN 1 ELSE 0 END)::int AS arrests
        FROM {SCHEMA}.fact_crime f
        JOIN {SCHEMA}.dim_time t ON f.time_id = t.time_id
        {where}
        GROUP BY ts
        ORDER BY ts
    """)
    result = await db.execute(sql, params)
    rows = result.fetchall()
    return [TimeseriesPoint(ts=str(r.ts), count=r.count, arrests=r.arrests) for r in rows]


@cached(ttl=300)
async def get_forecast(
    db: AsyncSession,
    horizon: int = 14,
    redis=None,
) -> ForecastBundle:
    hist_sql = text(f"""
        SELECT t.date AS ts,
               COUNT(*)::int AS count,
               SUM(CASE WHEN f.is_arrested THEN 1 ELSE 0 END)::int AS arrests
        FROM {SCHEMA}.fact_crime f
        JOIN {SCHEMA}.dim_time t ON f.time_id = t.time_id
        GROUP BY t.date
        ORDER BY t.date
    """)
    hist_result = await db.execute(hist_sql)
    hist_rows = hist_result.fetchall()
    history = [
        TimeseriesPoint(ts=str(r.ts), count=r.count, arrests=r.arrests)
        for r in hist_rows
    ]

    counts = [r.count for r in hist_rows]
    if not counts:
        return ForecastBundle(history=[], forecast=[])

    import statistics

    avg = statistics.mean(counts)
    std = statistics.stdev(counts) if len(counts) > 1 else 0.0

    last_date = hist_rows[-1].ts if hist_rows else ""
    forecast = []
    if last_date:
        from datetime import date as _date
        from datetime import timedelta

        base = _date.fromisoformat(str(last_date)[:10])
        for i in range(1, horizon + 1):
            d = base + timedelta(days=i)
            yhat = round(avg)
            yhat_lower = max(0, round(avg - std))
            yhat_upper = round(avg + std)
            forecast.append(
                ForecastPoint(
                    ts=str(d),
                    yhat=float(yhat),
                    yhat_lower=float(yhat_lower),
                    yhat_upper=float(yhat_upper),
                )
            )

    return ForecastBundle(history=history, forecast=forecast)


@cached(ttl=300)
async def get_anomalies(
    db: AsyncSession,
    z: float = 3.0,
    redis=None,
) -> list[AnomalyPoint]:
    sql = text(f"""
        WITH daily AS (
            SELECT t.date AS ts, COUNT(*)::int AS count
            FROM {SCHEMA}.fact_crime f
            JOIN {SCHEMA}.dim_time t ON f.time_id = t.time_id
            GROUP BY t.date
        ),
        stats AS (
            SELECT AVG(count) AS avg, STDDEV(count) AS std FROM daily
        )
        SELECT d.ts, d.count,
               ROUND((d.count - s.avg) / NULLIF(s.std, 0), 2) AS z_score
        FROM daily d, stats s
        WHERE ABS((d.count - s.avg) / NULLIF(s.std, 0)) > :z
        ORDER BY d.ts
    """)
    result = await db.execute(sql, {"z": z})
    rows = result.fetchall()
    return [AnomalyPoint(ts=str(r.ts), z=float(r.z_score), count=r.count) for r in rows]


@cached(ttl=300)
async def get_heatmap(
    db: AsyncSession,
    from_date: str | None = None,
    to_date: str | None = None,
    types: str | None = None,
    redis=None,
) -> Heatmap:
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

    sql = text(f"""
        SELECT COALESCE(t.date_dow, 0) AS weekday,
               COALESCE(t.hour, 0) AS hour,
               COUNT(f.crime_id)::int AS count
        FROM {SCHEMA}.fact_crime f
        JOIN {SCHEMA}.dim_time t ON f.time_id = t.time_id
        JOIN {SCHEMA}.dim_offense o ON f.offense_id = o.offense_id
        {where}
        GROUP BY t.date_dow, t.hour
        ORDER BY t.date_dow, t.hour
    """)
    result = await db.execute(sql, params)
    rows = result.fetchall()
    matrix = [[0] * 24 for _ in range(7)]
    for r in rows:
        wd = int(r.weekday) % 7
        hr = int(r.hour) % 24
        matrix[wd][hr] = int(r.count)
    return Heatmap(matrix=matrix)
