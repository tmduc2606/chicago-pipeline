#!/usr/bin/env python3
"""
Gold Layer Query Tool — Chicago Crime DBMS
Run: docker compose exec spark-master /opt/spark/bin/spark-submit /opt/scripts/explore/gold_query.py
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
TABLES = {
    "fact": "fact_crime",
    "time": "dim_time",
    "location": "dim_location",
    "offense": "dim_offense",
    "case": "dim_case",
}


def build_spark() -> SparkSession:
    return (
        SparkSession.builder
        .appName("Gold-Query")
        .config("spark.driver.memory", "1g")
        .getOrCreate()
    )


def cmd_help():
    print("""
Gold Query Tool -- Available commands:

  tables                         List all gold tables with row counts
  schema <table>                 Show columns and types for a table
  head <table> [n]               Show first n rows (default: 5)
  count <table> [column]         Row count, or count by column value
  filter <table> <col> <val>     Filter rows where col == val
  agg <table> <col> [agg_fn]     Aggregation (sum/mean/min/max/count)
  join                           Show fact->dim FK integrity check
  search <table> <col> <term>    Search for a substring in a column
  qotd                           Question of the day (random insight)
  quit                           Exit

Aliases for <table>:
  fact, time, location, offense, case
  (or full name: fact_crime, dim_time, etc.)

Examples:
  head fact 10
  count offense primary_type
  filter fact arrest True
  filter fact year 2025
  agg fact hours_to_update mean
  search offense primary_type THEFT
  join
""")


def resolve_table(name: str) -> str:
    name = name.lower().strip()
    if name in TABLES:
        return TABLES[name]
    if name in TABLES.values():
        return name
    return name


def cmd_tables(spark: SparkSession):
    print(f"  {'Table':<18s} {'Rows':>10s} {'Cols':>5s}")
    print("  " + "-" * 35)
    for alias, t in TABLES.items():
        df = spark.read.parquet(f"{GOLD_PATH}/{t}")
        print(f"  {t:<18s} {df.count():>10,} {len(df.columns):>5d}")
    print()


def cmd_schema(spark: SparkSession, table: str):
    t = resolve_table(table)
    df = spark.read.parquet(f"{GOLD_PATH}/{t}")
    print(f"  {t} columns ({len(df.columns)}):")
    for field in df.schema.fields:
        print(f"    {field.name:<30s} {field.dataType.simpleString()}")
    print()


def cmd_head(spark: SparkSession, table: str, n: int = 5):
    t = resolve_table(table)
    df = spark.read.parquet(f"{GOLD_PATH}/{t}")
    df.show(n, truncate=False)


def cmd_count(spark: SparkSession, table: str, col: str = None):
    t = resolve_table(table)
    df = spark.read.parquet(f"{GOLD_PATH}/{t}")
    if col:
        df.groupBy(col).count().orderBy(F.col("count").desc()).show(20, truncate=False)
    else:
        print(f"  {t}: {df.count():,} rows")


def cmd_filter(spark: SparkSession, table: str, col: str, val: str):
    t = resolve_table(table)
    df = spark.read.parquet(f"{GOLD_PATH}/{t}")
    filtered = df.filter(F.col(col) == val)
    print(f"  {t}: {col}={val} -> {filtered.count():,} rows")
    filtered.show(10, truncate=False)


def cmd_agg(spark: SparkSession, table: str, col: str, agg_fn: str = "count"):
    t = resolve_table(table)
    df = spark.read.parquet(f"{GOLD_PATH}/{t}")
    fn_map = {
        "sum": F.sum,
        "mean": F.mean,
        "avg": F.mean,
        "min": F.min,
        "max": F.max,
        "count": F.count,
        "stddev": F.stddev,
    }
    fn = fn_map.get(agg_fn.lower(), F.count)
    result = df.agg(fn(F.col(col)).alias(f"{agg_fn}_{col}"))
    result.show(truncate=False)


def cmd_join(spark: SparkSession):
    print("  FK integrity: fact_crime -> dimension tables\n")
    fact = spark.read.parquet(f"{GOLD_PATH}/fact_crime")
    checks = [
        ("dim_time", "time_id"),
        ("dim_offense", "offense_id"),
        ("dim_case", "case_id"),
        ("dim_location", "location_id"),
    ]
    all_pass = True
    for dim_name, fk_col in checks:
        dim = spark.read.parquet(f"{GOLD_PATH}/{dim_name}")
        pk_col = dim.columns[0]
        orphans = fact.join(dim, fact[fk_col] == dim[pk_col], "left_anti")
        orphan_cnt = orphans.count()
        if orphan_cnt == 0:
            print(f"    {fk_col:>12s} -> {dim_name}: PASS")
        else:
            print(f"    {fk_col:>12s} -> {dim_name}: FAIL ({orphan_cnt} orphan rows)")
            all_pass = False
            orphans.show(5, truncate=False)
    print(f"\n  Overall: {'PASS' if all_pass else 'FAIL'}\n")


def cmd_search(spark: SparkSession, table: str, col: str, term: str):
    t = resolve_table(table)
    df = spark.read.parquet(f"{GOLD_PATH}/{t}")
    results = df.filter(F.lower(F.col(col)).contains(term.lower()))
    cnt = results.count()
    print(f"  {t}.{col} LIKE '%{term}%' -> {cnt:,} rows")
    results.show(20, truncate=False)


def cmd_qotd(spark: SparkSession):
    insights = [
        ("fact_crime", "arrest", "Arrest rate across all crimes"),
        ("dim_offense", "primary_type", "Most common crime types"),
        ("dim_time", "weekday_name", "Crimes by day of week"),
        ("dim_time", "month", "Crimes by month"),
        ("dim_location", "district", "Crimes by district"),
        ("dim_location", "is_downtown", "Downtown vs non-downtown crime"),
        ("fact_crime", "year", "Crimes by year"),
    ]
    import random
    table, col, title = random.choice(insights)
    df = spark.read.parquet(f"{GOLD_PATH}/{table}")
    print(f"\n  {title}:")
    df.groupBy(col).count().orderBy(F.col("count").desc()).show(15, truncate=False)


if __name__ == "__main__":
    spark = build_spark()
    spark.sparkContext.setLogLevel("WARN")
    try:
        print("Gold Query Tool -- type 'help' for commands, 'quit' to exit\n")
        while True:
            try:
                raw = input("gold> ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not raw:
                continue
            parts = raw.split()
            verb = parts[0].lower()
            try:
                if verb in ("quit", "q"):
                    break
                elif verb == "help":
                    cmd_help()
                elif verb == "tables":
                    cmd_tables(spark)
                elif verb == "schema":
                    if len(parts) < 2:
                        print("  Usage: schema <table>")
                    else:
                        cmd_schema(spark, parts[1])
                elif verb == "head":
                    if len(parts) < 2:
                        print("  Usage: head <table> [n]")
                    else:
                        n = int(parts[2]) if len(parts) > 2 else 5
                        cmd_head(spark, parts[1], n)
                elif verb == "count":
                    if len(parts) < 2:
                        print("  Usage: count <table> [column]")
                    else:
                        cmd_count(spark, parts[1], parts[2] if len(parts) > 2 else None)
                elif verb == "filter":
                    if len(parts) < 4:
                        print("  Usage: filter <table> <col> <val>")
                    else:
                        cmd_filter(spark, parts[1], parts[2], parts[3])
                elif verb == "agg":
                    if len(parts) < 3:
                        print("  Usage: agg <table> <col> [agg_fn]")
                    else:
                        cmd_agg(spark, parts[1], parts[2], parts[3] if len(parts) > 3 else "count")
                elif verb == "join":
                    cmd_join(spark)
                elif verb == "search":
                    if len(parts) < 4:
                        print("  Usage: search <table> <col> <term>")
                    else:
                        cmd_search(spark, parts[1], parts[2], parts[3])
                elif verb == "qotd":
                    cmd_qotd(spark)
                else:
                    print(f"  Unknown command: {verb}. Type 'help' for options.")
            except Exception as e:
                print(f"  Error: {e}")
    finally:
        spark.stop()
