"""One-off EDA inspection for M2 Silver proposal validation.

Reads /tmp/chicago_synthetic.csv, takes a sample (default 100%), runs the inspect_df()
pattern from references/notebooks/01_eda_and_inspection.ipynb, and emits:
  - head(3)
  - info()
  - describe(include="all").T
  - missing values (top 10)
  - duplicates
  - nunique() per column
  - top value + freq for the top-3 most-cardinal categoricals

This is a spike — not part of the pipeline. Run with spark-submit on master.
"""
from __future__ import annotations

import sys
from pathlib import Path

_src = Path("/opt/pipeline/src")
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def build_spark() -> SparkSession:
    return (
        SparkSession.builder
        .appName("M2-Silver-EDA")
        .config("spark.driver.memory", "1g")
        .getOrCreate()
    )


def inspect_df(df, name: str, spark: SparkSession) -> None:
    print(f"\n========================= {name} =========================")
    print("--- head(3) ---")
    df.show(3, truncate=False)
    print("--- schema ---")
    df.printSchema()
    print(f"--- row count: {df.count()} ---")
    print("--- column count:", len(df.columns), "---")
    print("--- missing values (top 10) ---")
    missing = (
        df.select([F.sum(F.when(F.col(c).isNull(), 1).otherwise(0)).alias(c) for c in df.columns])
        .toPandas()
        .T
        .rename(columns={0: "null_count"})
        .sort_values("null_count", ascending=False)
        .head(10)
    )
    print(missing)
    print("--- duplicates (full row) ---")
    print(df.count() - df.dropDuplicates().count())
    print("--- cardinality (nunique) ---")
    nunique_pdf = (
        df.select([F.countDistinct(c).alias(c) for c in df.columns])
        .toPandas()
        .T
        .rename(columns={0: "nunique"})
        .sort_values("nunique", ascending=False)
    )
    print(nunique_pdf)
    print(f"--- top value + freq for ALL columns ---")
    for c in df.columns:
        try:
            top = (
                df.groupBy(c)
                .count()
                .orderBy(F.col("count").desc())
                .limit(3)
                .toPandas()
            )
            print(f"\n  [{c}] nunique={nunique_pdf.loc[c, 'nunique']}, nulls={int(missing.loc[c, 'null_count']) if c in missing.index else 0}")
            print(top.to_string(index=False))
        except Exception as e:
            print(f"  [{c}] error: {e}")


def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/chicago_synthetic.csv"
    sample_fraction = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 42

    spark = build_spark()
    spark.sparkContext.setLogLevel("WARN")

    print(f"Reading {csv_path}")
    full = (
        spark.read
        .option("header", True)
        .option("inferSchema", False)
        .csv(csv_path)
    )

    total = full.count()
    print(f"Total rows in CSV: {total}")

    if sample_fraction >= 1.0:
        data = full
        label = "FULL"
    else:
        data = full.sample(withReplacement=False, fraction=sample_fraction, seed=seed)
        label = f"SAMPLE_{int(sample_fraction*100)}pct"
        print(f"Sampled rows (fraction={sample_fraction}, seed={seed}): {data.count()}")

    inspect_df(data, f"CHICAGO_CRIME_{label}", spark)

    spark.stop()


if __name__ == "__main__":
    main()
