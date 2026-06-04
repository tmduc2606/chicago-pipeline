"""Warehouse layer one-shot explorer (M4) — prints Postgres table summaries."""
from __future__ import annotations

import os
import sys
from pathlib import Path

_src = Path(__file__).resolve().parents[2] / "pipeline" / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from sqlalchemy import create_engine, text

ENV = os.getenv("ENV", "local")


def _engine():
    pg_host = os.getenv("POSTGRES_HOST", "localhost")
    pg_port = os.getenv("POSTGRES_PORT", "5432")
    pg_user = os.getenv("POSTGRES_USER", "chicago")
    pg_pass = os.getenv("POSTGRES_PASSWORD", "change_me_local")
    pg_db = os.getenv("POSTGRES_DB", "chicago")
    return create_engine(f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}")


def _query(engine, sql: str) -> list[tuple]:
    with engine.connect() as conn:
        return conn.execute(text(sql)).fetchall()


def section(title: str, sql: str, engine) -> None:
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")
    rows = _query(engine, sql)
    if not rows:
        print("  (no results)")
        return
    for row in rows:
        print(f"  {row}")


def main() -> None:
    engine = _engine()
    print(f"ENV={ENV}")
    print(f"Engine: {engine.url}")

    section("1. Warehouse tables and row counts", """
        SELECT schemaname, relname AS table_name, n_live_tup AS row_count
        FROM pg_stat_user_tables
        WHERE schemaname = 'warehouse'
        ORDER BY schemaname, relname
    """, engine)

    section("2. fact_crime — top 5 rows", """
        SELECT crime_id, year, arrest, domestic, beat
        FROM warehouse.fact_crime
        ORDER BY crime_id
        LIMIT 5
    """, engine)

    section("3. dim_time — sample (5 rows)", """
        SELECT time_id, date, year, month, day, hour, weekday, is_weekend
        FROM warehouse.dim_time
        ORDER BY time_id
        LIMIT 5
    """, engine)

    section("4. dim_location — sample (5 rows)", """
        SELECT location_id, district, ward, community_area, is_downtown, distance_to_downtown_km
        FROM warehouse.dim_location
        ORDER BY location_id
        LIMIT 5
    """, engine)

    section("5. dim_offense — sample (5 rows)", """
        SELECT offense_id, iucr, primary_type, description, fbi_code
        FROM warehouse.dim_offense
        ORDER BY offense_id
        LIMIT 5
    """, engine)

    section("6. dim_case — sample (5 rows)", """
        SELECT case_id, case_number
        FROM warehouse.dim_case
        ORDER BY case_id
        LIMIT 5
    """, engine)

    section("7. PostGIS geometry count and SRID", """
        SELECT ST_SRID(geometry) AS srid, COUNT(*) AS cnt
        FROM warehouse.dim_location
        WHERE geometry IS NOT NULL
        GROUP BY ST_SRID(geometry)
    """, engine)

    section("8. Mart: mart_kpi_daily — all rows", """
        SELECT * FROM warehouse.mart_kpi_daily ORDER BY date_dow
    """, engine)

    section("9. Mart: mart_arrest_summary — top 5", """
        SELECT district, total_crimes, total_arrests, arrest_rate_pct
        FROM warehouse.mart_arrest_summary
        ORDER BY total_crimes DESC
        LIMIT 5
    """, engine)

    section("10. Mart: mart_crime_type_trend — top 5", """
        SELECT primary_type, total_crimes
        FROM warehouse.mart_crime_type_trend
        ORDER BY total_crimes DESC
        LIMIT 5
    """, engine)

    section("11. Mart: mart_geo_choropleth — top 5", """
        SELECT district, total_crimes
        FROM warehouse.mart_geo_choropleth
        ORDER BY total_crimes DESC
        LIMIT 5
    """, engine)

    section("12. Mart: mart_temporal_heatmap — top 5", """
        SELECT date, weekday, hour, crime_count
        FROM warehouse.mart_temporal_heatmap
        ORDER BY crime_count DESC
        LIMIT 5
    """, engine)


if __name__ == "__main__":
    main()
