from __future__ import annotations

import sys
from pathlib import Path

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    BooleanType,
    DateType,
    FloatType,
    IntegerType,
    StringType,
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
}


def _cast_columns(df: DataFrame) -> DataFrame:
    for col_name, dtype in SILVER_COLUMNS.items():
        if col_name == "date":
            df = df.withColumn(col_name, F.to_date(F.col(col_name), "MM/dd/yyyy hh:mm:ss a"))
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


def silver_transform(spark: SparkSession, bronze_path: str, output_root: str | None = None) -> int:
    cfg = settings.silver
    bucket = settings.storage.get("bucket", "lake")
    prefix = cfg.get("prefix", "silver/chicago_crime")
    output_root = output_root or f"s3a://{bucket}/{prefix}"

    log.info("silver_read_bronze", path=bronze_path)
    df = spark.read.parquet(bronze_path)

    original_count = df.count()
    log.info("silver_bronze_row_count", count=original_count)

    df = _cast_columns(df)
    df = _filter_date_range(df)
    df = _filter_chicago_bbox(df)
    df = _dedup(df)
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
    _src = Path(__file__).resolve().parents[2]
    if str(_src) not in sys.path:
        sys.path.insert(0, str(_src))

    from chicago_pipeline.common.spark_session import get_spark

    bronze_path = sys.argv[1] if len(sys.argv) > 1 else "s3a://lake/bronze/chicago_crime"
    spark = get_spark(app_name="SilverTransform")
    count = silver_transform(spark, bronze_path)
    print(f"Silver transform complete: {count} rows")
    spark.stop()
