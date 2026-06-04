from __future__ import annotations

import sys
from pathlib import Path

_src = Path(__file__).resolve().parents[2]
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    BooleanType,
    DateType,
    FloatType,
    IntegerType,
    StringType,
    TimestampType,
)

from chicago_pipeline.common.logger import get_logger
from chicago_pipeline.common.settings import settings

log = get_logger(__name__)

SILVER_COLUMNS = {
    "id": IntegerType(),
    "case_number": StringType(),
    "date": DateType(),
    "block": StringType(),
    "iucr": StringType(),
    "primary_type": StringType(),
    "description": StringType(),
    "location_description": StringType(),
    "arrest": BooleanType(),
    "domestic": BooleanType(),
    "beat": StringType(),
    "district": IntegerType(),
    "ward": IntegerType(),
    "community_area": IntegerType(),
    "fbi_code": StringType(),
    "latitude": FloatType(),
    "longitude": FloatType(),
    "updated_on": StringType(),
    "is_arrested": BooleanType(),
    "is_domestic": BooleanType(),
    "is_domestic_arrest": BooleanType(),
    "is_unassigned_district": BooleanType(),
    "is_unassigned_community": BooleanType(),
    "is_unassigned_ward": BooleanType(),
    "date_year": IntegerType(),
    "date_month": IntegerType(),
    "date_dow": IntegerType(),
    "updated_on_ts": TimestampType(),
    "hours_to_update": IntegerType(),
}

TEXT_COLS = [
    "primary_type", "description", "location_description",
    "block", "fbi_code", "case_number", "beat",
]


def _cast_columns(df: DataFrame) -> DataFrame:
    for col_name, dtype in SILVER_COLUMNS.items():
        if col_name == "date":
            df = df.withColumn(
                col_name,
                F.coalesce(
                    F.to_date(F.col(col_name), "MM/dd/yyyy hh:mm:ss a"),
                    F.to_date(F.col(col_name), "yyyy-MM-dd'T'HH:mm:ss"),
                    F.to_date(F.col(col_name)),
                ),
            )
        elif col_name == "arrest":
            df = df.withColumn(
                col_name,
                F.when(F.col(col_name).cast("int") == 1, True).otherwise(False),
            )
        elif col_name == "domestic":
            df = df.withColumn(
                col_name,
                F.when(F.col(col_name).cast("int") == 1, True).otherwise(False),
            )
        elif col_name in df.columns:
            df = df.withColumn(col_name, F.col(col_name).cast(dtype))
    return df


def _filter_chicago_bbox(df: DataFrame) -> DataFrame:
    cfg = settings.silver.get("chicago_bbox", {})
    min_lat = cfg.get("min_lat", 41.644)
    max_lat = cfg.get("max_lat", 42.023)
    min_lon = cfg.get("min_lon", -87.940)
    max_lon = cfg.get("max_lon", -87.524)
    return df.filter(
        (F.col("latitude").between(min_lat, max_lat))
        & (F.col("longitude").between(min_lon, max_lon))
    )


def _filter_date_range(df: DataFrame) -> DataFrame:
    cfg = settings.silver.get("date_range", {})
    start = cfg.get("start", "2024-01-01")
    end = cfg.get("end", "2026-12-31")
    return df.filter(F.col("date").between(start, end))


def _dedup(df: DataFrame) -> DataFrame:
    default_dedup = ["id", "case_number", "date", "primary_type", "latitude", "longitude"]
    dedup_cols = settings.silver.get("dedup_columns", default_dedup)
    existing = [c for c in dedup_cols if c in df.columns]
    return df.dropDuplicates(existing)


def _add_partition_columns(df: DataFrame) -> DataFrame:
    return (
        df.withColumn("year", F.year("date"))
        .withColumn("month", F.month("date"))
    )


def _standardize_text(df: DataFrame) -> DataFrame:
    for c in TEXT_COLS:
        df = df.withColumn(c, F.trim(F.col(c)))
    return df


def _add_updated_on_ts(df: DataFrame) -> DataFrame:
    return df.withColumn(
        "updated_on_ts",
        F.coalesce(
            F.to_timestamp(F.col("updated_on"), "MM/dd/yyyy hh:mm:ss a"),
            F.to_timestamp(F.col("updated_on"), "yyyy-MM-dd'T'HH:mm:ss"),
            F.to_timestamp(F.col("updated_on")),
        ),
    )


def _add_date_components(df: DataFrame) -> DataFrame:
    return (
        df.withColumn("date_year", F.year(F.col("date")))
        .withColumn("date_month", F.month(F.col("date")))
        .withColumn("date_dow", F.dayofweek(F.col("date")))
    )


def _add_conforming_booleans(df: DataFrame) -> DataFrame:
    return (
        df.withColumn("is_arrested", F.col("arrest"))
        .withColumn("is_domestic", F.col("domestic"))
        .withColumn("is_domestic_arrest", F.col("arrest") & F.col("domestic"))
        .withColumn("is_unassigned_district", F.col("district").isNull())
        .withColumn("is_unassigned_community", F.col("community_area").isNull())
        .withColumn("is_unassigned_ward", F.col("ward").isNull())
    )


def _add_hours_to_update(df: DataFrame) -> DataFrame:
    return df.withColumn(
        "hours_to_update",
        F.greatest(
            F.least(
                ((F.unix_timestamp(F.col("updated_on_ts")) - F.unix_timestamp(F.col("date").cast("timestamp"))) / F.lit(3600)).cast(IntegerType()),
                F.lit(365 * 24),
            ),
            F.lit(0),
        ),
    )


def silver_transform(spark: SparkSession, bronze_path: str, output_root: str | None = None) -> int:
    cfg = settings.silver
    bucket = settings.storage.get("bucket", "lake")
    prefix = cfg.get("prefix", "silver/chicago_crime")
    output_root = output_root or f"s3a://{bucket}/{prefix}"

    log.info("silver_read_bronze", path=bronze_path)
    df = spark.read.parquet(bronze_path)

    if "ingest_date" in df.columns:
        latest = df.agg(F.max("ingest_date")).collect()[0][0]
        if latest is not None:
            df = df.filter(F.col("ingest_date") == latest)
            log.info("silver_partition_pruned", latest_ingest_date=str(latest))

    original_count = df.count()
    log.info("silver_bronze_row_count", count=original_count)

    df = _cast_columns(df)
    df = _standardize_text(df)
    df = _filter_date_range(df)
    df = _filter_chicago_bbox(df)
    df = _dedup(df)
    df = _add_updated_on_ts(df)
    df = _add_date_components(df)
    df = _add_conforming_booleans(df)
    df = _add_hours_to_update(df)
    df = _add_partition_columns(df)

    transformed_count = df.count()
    log.info("silver_transformed_row_count", count=transformed_count)

    df = df.drop("year").drop("month")
    df = _add_partition_columns(df)

    df.write.mode("overwrite").partitionBy("year", "month").parquet(output_root)

    log.info(
        "silver_write_complete",
        output=output_root,
        rows=transformed_count,
        dropped=original_count - transformed_count,
    )
    return transformed_count


if __name__ == "__main__":
    from chicago_pipeline.common.spark_session import get_spark

    bronze_path = sys.argv[1] if len(sys.argv) > 1 else "s3a://lake/bronze/chicago_crime"
    spark = get_spark(app_name="SilverTransform")
    count = silver_transform(spark, bronze_path)
    print(f"Silver transform complete: {count} rows")
    spark.stop()
