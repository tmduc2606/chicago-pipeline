"""M3 Gold Layer Verification — one-off validation of all Gold tables.

Run: docker compose exec spark-master /opt/spark/bin/spark-submit /opt/scripts/spike/verify_m3_gold.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_src = Path("/opt/pipeline/src")
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

GOLD_PATH = "s3a://lake/gold/chicago_crime"
SILVER_PATH = "s3a://lake/silver/chicago_crime"
PASS = "PASS"
FAIL = "FAIL"
results: list[tuple[str, str, str]] = []


def check(name: str, condition: bool, detail: str = ""):
    status = PASS if condition else FAIL
    results.append((name, status, detail))
    symbol = "OK" if condition else "!!"
    print(f"  [{symbol}] {name}: {status}" + (f" ({detail})" if detail else ""))


def main():
    spark = SparkSession.builder.appName("VerifyM3Gold").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    print("\n" + "=" * 60)
    print(" M3 GOLD LAYER VERIFICATION")
    print("=" * 60)

    # --- 1. Tables exist ---
    print("\n--- 1. Table existence ---")
    tables = {}
    for t in ["fact_crime", "dim_time", "dim_location", "dim_offense", "dim_case"]:
        try:
            tables[t] = spark.read.parquet(f"{GOLD_PATH}/{t}")
            check(f"Table {t} exists", True)
        except Exception as e:
            check(f"Table {t} exists", False, str(e))

    # --- 2. Row counts ---
    print("\n--- 2. Row counts ---")
    counts = {name: df.count() for name, df in tables.items()}
    for name, cnt in counts.items():
        print(f"    {name:<18s} {cnt:>7,} rows")
    check("fact_crime == silver", counts["fact_crime"] == 57_931, f"{counts['fact_crime']}")
    check("dim_time range 2024-2026", counts["dim_time"] == 26_304, f"{counts['dim_time']}")
    check("dim_offense > 500", counts["dim_offense"] > 500, f"{counts['dim_offense']}")
    check("dim_location == fact", counts["dim_location"] == counts["fact_crime"])
    check("dim_case == fact", counts["dim_case"] == counts["fact_crime"])

    # --- 3. Schema checks ---
    print("\n--- 3. Schema checks ---")
    fact = tables["fact_crime"]
    expected_fact_cols = {
        "crime_id", "time_id", "offense_id", "case_id", "location_id",
        "arrest", "domestic", "beat", "fbi_code", "is_arrested",
        "is_domestic", "is_domestic_arrest", "is_unassigned_district",
        "is_unassigned_community", "is_unassigned_ward", "hours_to_update",
        "date_dow", "_gold_ingest_ts", "year",
    }
    actual_cols = set(fact.columns)
    check("fact_crime has 19 columns", len(fact.columns) == 19, f"{len(fact.columns)}")
    check("fact_crime expected columns present", expected_fact_cols.issubset(actual_cols))

    for t_name in ["dim_time", "dim_offense", "dim_location", "dim_case"]:
        df = tables[t_name]
        check(f"{t_name} has > 0 columns", len(df.columns) > 0, f"{len(df.columns)}")

    # --- 4. PK uniqueness ---
    print("\n--- 4. PK uniqueness ---")
    check("fact_crime.crime_id unique", fact.select("crime_id").distinct().count() == counts["fact_crime"])
    check("dim_time.time_id unique", tables["dim_time"].select("time_id").distinct().count() == counts["dim_time"])
    check("dim_offense.offense_id unique", tables["dim_offense"].select("offense_id").distinct().count() == counts["dim_offense"])
    check("dim_location.location_id unique", tables["dim_location"].select("location_id").distinct().count() == counts["dim_location"])
    check("dim_case.case_id unique", tables["dim_case"].select("case_id").distinct().count() == counts["dim_case"])

    # --- 5. PK not null ---
    print("\n--- 5. PK not null ---")
    check("fact_crime.crime_id not null", fact.filter(F.col("crime_id").isNull()).count() == 0)
    check("dim_time.time_id not null", tables["dim_time"].filter(F.col("time_id").isNull()).count() == 0)
    check("dim_offense.offense_id not null", tables["dim_offense"].filter(F.col("offense_id").isNull()).count() == 0)
    check("dim_location.location_id not null", tables["dim_location"].filter(F.col("location_id").isNull()).count() == 0)
    check("dim_case.case_id not null", tables["dim_case"].filter(F.col("case_id").isNull()).count() == 0)

    # --- 6. FK integrity ---
    print("\n--- 6. FK integrity (fact -> dims) ---")
    for dim_name, fk_col in [("dim_time", "time_id"), ("dim_offense", "offense_id"),
                              ("dim_case", "case_id"), ("dim_location", "location_id")]:
        pk_col = tables[dim_name].columns[0]
        orphans = fact.join(tables[dim_name], fact[fk_col] == tables[dim_name][pk_col], "left_anti")
        orphan_cnt = orphans.count()
        check(f"fact -> {dim_name}.{pk_col}", orphan_cnt == 0, f"{orphan_cnt} orphans" if orphan_cnt else "")

    # --- 7. dim_offense IUCR completeness ---
    print("\n--- 7. dim_offense completeness ---")
    doff = tables["dim_offense"]
    check("dim_offense iucr not null", doff.filter(F.col("iucr").isNull()).count() == 0)
    check("dim_offense primary_type not null", doff.filter(F.col("primary_type").isNull()).count() == 0)
    check("dim_offense has > 500 unique IUCR", doff.select("iucr").distinct().count() > 500)

    # --- 8. dim_time coverage ---
    print("\n--- 8. dim_time coverage ---")
    dt = tables["dim_time"]
    min_date = dt.agg(F.min("date")).collect()[0][0]
    max_date = dt.agg(F.max("date")).collect()[0][0]
    check("dim_time starts 2024-01-01", str(min_date) == "2024-01-01", str(min_date))
    check("dim_time ends 2026-12-31", str(max_date) == "2026-12-31", str(max_date))
    check("dim_time has weekday column", "weekday" in dt.columns)

    # --- 9. dim_location geographic checks ---
    print("\n--- 9. dim_location geography ---")
    dl = tables["dim_location"]
    check("dim_location is_downtown column", "is_downtown" in dl.columns)
    check("dim_location distance_to_downtown_km column", "distance_to_downtown_km" in dl.columns)
    check("dim_location geom_wkt column", "geom_wkt" in dl.columns)
    check("dim_location latitude not null", dl.filter(F.col("latitude").isNull()).count() == 0)
    check("dim_location longitude not null", dl.filter(F.col("longitude").isNull()).count() == 0)

    # --- 10. Year partition ---
    print("\n--- 10. Year partition ---")
    check("fact_crime has 'year' column", "year" in fact.columns)
    years = sorted([r.year for r in fact.select("year").distinct().collect()])
    check("fact_crime has year column with data", 2024 in years, str(years))

    # --- 11. Gold ingestion timestamp ---
    print("\n--- 11. Pipeline observability ---")
    check("fact_crime has _gold_ingest_ts column", "_gold_ingest_ts" in fact.columns)
    ts_nulls = fact.filter(F.col("_gold_ingest_ts").isNull()).count()
    check("fact_crime._gold_ingest_ts not null", ts_nulls == 0)

    # --- 12. dim_case block column ---
    print("\n--- 12. dim_case metadata ---")
    dc = tables["dim_case"]
    check("dim_case has case_number column", "case_number" in dc.columns)
    check("dim_case has updated_on column", "updated_on" in dc.columns)
    check("dim_case case_number not null", dc.filter(F.col("case_number").isNull()).count() == 0)

    # --- Summary ---
    print("\n" + "=" * 60)
    passed = sum(1 for _, s, _ in results if s == PASS)
    failed = sum(1 for _, s, _ in results if s == FAIL)
    total = len(results)
    print(f" VERIFICATION SUMMARY: {passed}/{total} passed, {failed} failed")
    print("=" * 60)
    if failed:
        print("\nFailed checks:")
        for name, status, detail in results:
            if status == FAIL:
                print(f"  !! {name}: {detail}")
    else:
        print("\n ALL CHECKS PASSED -- Gold layer is healthy!")

    spark.stop()
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
