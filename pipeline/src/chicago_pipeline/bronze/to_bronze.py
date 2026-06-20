from __future__ import annotations

import sys
from pathlib import Path

_src = Path(__file__).resolve().parents[2]
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from datetime import datetime, timezone

from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, to_date
from pyspark.sql.types import (
    FloatType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

from chicago_pipeline.common.logger import get_logger
from chicago_pipeline.common.settings import settings

log = get_logger(__name__)

# ── Title Case (raw Kaggle) → snake_case column map ────────────────────────
COLUMN_MAP: dict[str, str] = {
    "ID": "id",
    "Case Number": "case_number",
    "Date": "date",
    "Block": "block",
    "IUCR": "iucr",
    "Primary Type": "primary_type",
    "Description": "description",
    "Location Description": "location_description",
    "Arrest": "arrest",
    "Domestic": "domestic",
    "Beat": "beat",
    "District": "district",
    "Ward": "ward",
    "Community Area": "community_area",
    "FBI Code": "fbi_code",
    "Latitude": "latitude",
    "Longitude": "longitude",
    "Updated On": "updated_on",
}
# Extra columns present in raw Kaggle CSV that we don't need
DROP_COLS: set[str] = {"X Coordinate", "Y Coordinate", "Year", "Location"}

BRONZE_SCHEMA = StructType([
    StructField("id", IntegerType()),
    StructField("case_number", StringType()),
    StructField("date", StringType()),
    StructField("block", StringType()),
    StructField("iucr", StringType()),
    StructField("primary_type", StringType()),
    StructField("description", StringType()),
    StructField("location_description", StringType()),
    StructField("arrest", IntegerType()),
    StructField("domestic", IntegerType()),
    StructField("beat", StringType()),
    StructField("district", IntegerType()),
    StructField("ward", IntegerType()),
    StructField("community_area", IntegerType()),
    StructField("fbi_code", StringType()),
    StructField("latitude", FloatType()),
    StructField("longitude", FloatType()),
    StructField("updated_on", StringType()),
])


def _rename_and_prune(df):
    """If the CSV has Title Case columns (raw Kaggle), rename to snake_case
    and drop extra columns.  If already snake_case, pass through unchanged."""
    src_cols = df.columns
    # Only rename columns that exist in the source
    rename_map = {c: COLUMN_MAP[c] for c in src_cols if c in COLUMN_MAP}
    if rename_map:
        for old, new in rename_map.items():
            df = df.withColumnRenamed(old, new)
        log.info("bronze_renamed_columns", count=len(rename_map))
    # Drop extra columns not in the target schema
    target_names = {f.name for f in BRONZE_SCHEMA}
    to_drop = [c for c in df.columns if c not in target_names]
    if to_drop:
        df = df.drop(*to_drop)
        log.info("bronze_dropped_columns", columns=to_drop)
    return df


def bronze_writer(spark: SparkSession, source_csv: str, output_root: str | None = None) -> int:
    cfg = settings.bronze
    bucket = settings.storage.get("bucket", "lake")
    prefix = cfg.get("prefix", "bronze/chicago_crime")
    partition_col = cfg.get("partition_by", "ingest_date")
    ingest_ts_col = cfg.get("ingest_ts_column", "_ingest_ts")
    output_root = output_root or f"s3a://{bucket}/{prefix}"

    now = datetime.now(timezone.utc)
    ingest_date_str = now.strftime("%Y-%m-%d")

    # Read with header + inferSchema so we get the raw column names
    raw_df = spark.read.option("header", True).option("inferSchema", True).csv(source_csv)

    # Rename Title Case → snake_case if needed, drop extras
    df = _rename_and_prune(raw_df)

    # Cast to the expected bronze schema (coerce types)
    for field in BRONZE_SCHEMA:
        df = df.withColumn(field.name, df[field.name].cast(field.dataType))

    df = (
        df
        .withColumn(ingest_ts_col, lit(now.isoformat()))
        .withColumn(partition_col, to_date(lit(ingest_date_str)))
    )

    output_path = f"{output_root}/{partition_col}={ingest_date_str}"
    df_to_write = df.drop(partition_col)
    df_to_write.write.mode("overwrite").parquet(output_path)

    row_count = df.count()
    log.info(
        "bronze_write_complete",
        source=source_csv,
        output=output_path,
        rows=row_count,
    )
    return row_count


if __name__ == "__main__":
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/chicago_crime/source.csv"
    spark = (
        SparkSession.builder
        .appName("BronzeWriter")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.endpoint", settings.storage.get("endpoint", "http://minio:9000"))
        .config("spark.hadoop.fs.s3a.access.key", settings.storage.get("access_key", "minio"))
        .config("spark.hadoop.fs.s3a.secret.key", settings.storage.get("secret_key", "minio123"))
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        .getOrCreate()
    )
    count = bronze_writer(spark, csv_path)
    print(f"Written {count} rows to Bronze")
    spark.stop()
