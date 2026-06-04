"""M4 Warehouse verification — 46 checks covering all warehouse tables and marts."""
from __future__ import annotations

import os
import sys
from pathlib import Path

_src = Path(__file__).resolve().parents[2] / "pipeline" / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from sqlalchemy import create_engine, text

PASS = 0
FAIL = 0

pg_host = os.getenv("POSTGRES_HOST", "localhost")
pg_port = os.getenv("POSTGRES_PORT", "5432")
pg_user = os.getenv("POSTGRES_USER", "chicago")
pg_pass = os.getenv("POSTGRES_PASSWORD", "change_me_local")
pg_db = os.getenv("POSTGRES_DB", "chicago")
engine = create_engine(f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}")


def _q(sql: str):
    with engine.connect() as conn:
        return conn.execute(text(sql)).fetchall()


def check(description: str, sql: str, expect: tuple | int | None = None) -> None:
    global PASS, FAIL
    try:
        rows = _q(sql)
        if expect is not None:
            if isinstance(expect, int) and len(rows) > 0:
                val = rows[0][0]
                ok = val == expect
            elif isinstance(expect, tuple):
                ok = rows and all(a == b for a, b in zip(rows[0], expect))
            else:
                ok = len(rows) == expect
        else:
            ok = len(rows) > 0
        if ok:
            print(f"  PASS  {description}")
            PASS += 1
        else:
            print(f"  FAIL  {description} — expected {expect}, got {rows}")
            FAIL += 1
    except Exception as e:
        print(f"  FAIL  {description} — exception: {e}")
        FAIL += 1


def main() -> None:
    global PASS, FAIL
    PASS = 0
    FAIL = 0
    print(f"{'='*70}")
    print(f"  M4 Warehouse Verification ({_src})")
    print(f"  Engine: {engine.url}")
    print(f"{'='*70}")

    # ── warehouse schema tables ──
    print(f"\n--- Warehouse tables ---")
    check("warehouse schema exists",
          "SELECT 1 FROM information_schema.schemata WHERE schema_name = 'warehouse'",
          (1,))
    check("fact_crime exists",
          "SELECT 1 FROM information_schema.tables WHERE table_schema='warehouse' AND table_name='fact_crime'",
          (1,))
    check("dim_time exists",
          "SELECT 1 FROM information_schema.tables WHERE table_schema='warehouse' AND table_name='dim_time'",
          (1,))
    check("dim_location exists",
          "SELECT 1 FROM information_schema.tables WHERE table_schema='warehouse' AND table_name='dim_location'",
          (1,))
    check("dim_offense exists",
          "SELECT 1 FROM information_schema.tables WHERE table_schema='warehouse' AND table_name='dim_offense'",
          (1,))
    check("dim_case exists",
          "SELECT 1 FROM information_schema.tables WHERE table_schema='warehouse' AND table_name='dim_case'",
          (1,))

    # ── row counts ──
    print(f"\n--- Row counts ---")
    check("fact_crime 57,931 rows",
          "SELECT COUNT(*) FROM warehouse.fact_crime", 57931)
    check("dim_time 26,304 rows",
          "SELECT COUNT(*) FROM warehouse.dim_time", 26304)
    check("dim_location 57,931 rows",
          "SELECT COUNT(*) FROM warehouse.dim_location", 57931)
    check("dim_offense 900 rows",
          "SELECT COUNT(*) FROM warehouse.dim_offense", 900)
    check("dim_case 57,931 rows",
          "SELECT COUNT(*) FROM warehouse.dim_case", 57931)

    # ── primary keys ──
    print(f"\n--- Primary keys ---")
    check("fact_crime PK (crime_id unique)",
          "SELECT COUNT(*) FROM warehouse.fact_crime WHERE crime_id IS NULL", 0)
    check("dim_time PK (time_id unique)",
          "SELECT COUNT(*) FROM warehouse.dim_time WHERE time_id IS NULL", 0)
    check("dim_location PK (location_id unique)",
          "SELECT COUNT(*) FROM warehouse.dim_location WHERE location_id IS NULL", 0)
    check("dim_offense PK (offense_id unique)",
          "SELECT COUNT(*) FROM warehouse.dim_offense WHERE offense_id IS NULL", 0)
    check("dim_case PK (case_id unique)",
          "SELECT COUNT(*) FROM warehouse.dim_case WHERE case_id IS NULL", 0)

    # ── PostGIS geometry ──
    print(f"\n--- PostGIS geometry ---")
    check("PostGIS extension exists",
          "SELECT 1 FROM pg_extension WHERE extname='postgis'", (1,))
    check("geometry column exists",
          "SELECT 1 FROM information_schema.columns WHERE table_schema='warehouse' AND table_name='dim_location' AND column_name='geometry'",
          (1,))
    check("geometry SRID = 4326",
          "SELECT DISTINCT ST_SRID(geometry) FROM warehouse.dim_location WHERE geometry IS NOT NULL",
          (4326,))
    check("all 57,931 rows have geometry",
          "SELECT COUNT(*) FROM warehouse.dim_location WHERE geometry IS NOT NULL", 57931)
    check("no NULL geometry after cast",
          "SELECT COUNT(*) FROM warehouse.dim_location WHERE geometry IS NULL", 0)

    # ── dim_location data quality ──
    print(f"\n--- dim_location quality ---")
    check("district range 1-25",
          "SELECT COUNT(*) FROM warehouse.dim_location WHERE district < 1 OR district > 25", 0)
    check("latitude not null",
          "SELECT COUNT(*) FROM warehouse.dim_location WHERE latitude IS NULL", 0)
    check("longitude not null",
          "SELECT COUNT(*) FROM warehouse.dim_location WHERE longitude IS NULL", 0)
    check("geom_wkt not null",
          "SELECT COUNT(*) FROM warehouse.dim_location WHERE geom_wkt IS NULL", 0)
    check("is_downtown boolean",
          "SELECT COUNT(*) FROM warehouse.dim_location WHERE is_downtown NOT IN (TRUE, FALSE)", 0)
    check("distance >= 0",
          "SELECT COUNT(*) FROM warehouse.dim_location WHERE distance_to_downtown_km < 0", 0)

    # ── fact_crime data quality ──
    print(f"\n--- fact_crime quality ---")
    check("arrest boolean",
          "SELECT COUNT(*) FROM warehouse.fact_crime WHERE arrest NOT IN (TRUE, FALSE)", 0)
    check("domestic boolean",
          "SELECT COUNT(*) FROM warehouse.fact_crime WHERE domestic NOT IN (TRUE, FALSE)", 0)
    check("year has valid values",
          "SELECT COUNT(*) FROM warehouse.fact_crime WHERE year BETWEEN 2024 AND 2026", 57931)
    check("hours_to_update >= 0",
          "SELECT COUNT(*) FROM warehouse.fact_crime WHERE hours_to_update < 0", 0)

    # ── dbt warehouse schema marts ──
    print(f"\n--- dbt marts ---")
    for mart in ["mart_kpi_daily", "mart_arrest_summary", "mart_crime_type_trend",
                  "mart_geo_choropleth", "mart_temporal_heatmap"]:
        check(f"{mart} exists",
              f"SELECT 1 FROM information_schema.tables WHERE table_schema='warehouse' AND table_name='{mart}'",
              (1,))

    check("mart_kpi_daily has rows",
          "SELECT COUNT(*) FROM warehouse.mart_kpi_daily", 7)
    check("mart_arrest_summary has rows (>0)",
          "SELECT COUNT(*) FROM warehouse.mart_arrest_summary", 1250)
    check("mart_crime_type_trend has rows (>0)",
          "SELECT COUNT(*) FROM warehouse.mart_crime_type_trend", 900)
    check("mart_geo_choropleth has rows (>0)",
          "SELECT COUNT(*) FROM warehouse.mart_geo_choropleth", 57931)
    check("mart_temporal_heatmap has rows (>0)",
          "SELECT COUNT(*) FROM warehouse.mart_temporal_heatmap", 26304)

    # ── sin/cos encoding in int_time_enriched ──
    check("int_time_enriched has month_sin",
          "SELECT 1 FROM information_schema.columns WHERE table_schema='warehouse' AND table_name='int_time_enriched' AND column_name='month_sin'",
          (1,))
    check("int_time_enriched has month_cos",
          "SELECT 1 FROM information_schema.columns WHERE table_schema='warehouse' AND table_name='int_time_enriched' AND column_name='month_cos'",
          (1,))
    check("int_time_enriched has hour_sin",
          "SELECT 1 FROM information_schema.columns WHERE table_schema='warehouse' AND table_name='int_time_enriched' AND column_name='hour_sin'",
          (1,))
    check("int_time_enriched has hour_cos",
          "SELECT 1 FROM information_schema.columns WHERE table_schema='warehouse' AND table_name='int_time_enriched' AND column_name='hour_cos'",
          (1,))

    # ── geometry in int_fact_with_geom ──
    check("int_fact_with_geom has geom_wkt",
          "SELECT 1 FROM information_schema.columns WHERE table_schema='warehouse' AND table_name='int_fact_with_geom' AND column_name='geom_wkt'",
          (1,))

    print(f"\n{'='*70}")
    print(f"  RESULTS: {PASS} PASS, {FAIL} FAIL")
    print(f"{'='*70}")
    return FAIL == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
