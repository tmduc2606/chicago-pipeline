from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pyspark.sql.functions as F
from pyspark.sql import DataFrame, SparkSession, Window
from pyspark.sql.types import BooleanType, FloatType, IntegerType, StringType, TimestampType

_src = Path(__file__).resolve().parents[2]
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from chicago_pipeline.common.logger import get_logger
from chicago_pipeline.common.settings import settings

log = get_logger(__name__)

DOWNTOWN_LAT = 41.8819
DOWNTOWN_LON = -87.6278
EARTH_RADIUS_KM = 6371.0


def _gold_path(output_root: str, table: str) -> str:
    return f"{output_root}/{table}"


def _haversine_km(lat_col: str, lon_col: str) -> F.Column:
    lat1_r = F.radians(F.lit(DOWNTOWN_LAT))
    lon1_r = F.radians(F.lit(DOWNTOWN_LON))
    lat2_r = F.radians(F.col(lat_col))
    lon2_r = F.radians(F.col(lon_col))
    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r
    a = F.pow(F.sin(dlat / 2), 2) + F.cos(lat1_r) * F.cos(lat2_r) * F.pow(F.sin(dlon / 2), 2)
    c = F.lit(2) * F.asin(F.sqrt(a))
    return (c * EARTH_RADIUS_KM).cast(FloatType())


def _build_dim_time(spark: SparkSession, cfg: dict) -> DataFrame:
    start = cfg.get("date_range", {}).get("start", "2024-01-01")
    end = cfg.get("date_range", {}).get("end", "2026-12-31")
    start_ts = int(datetime.strptime(start, "%Y-%m-%d").timestamp())
    end_ts = int(datetime.strptime(end, "%Y-%m-%d").timestamp())
    total_hours = (end_ts - start_ts) // 3600 + 24

    df = spark.range(total_hours).withColumn(
        "ts",
        F.to_timestamp(F.lit(start_ts) + F.col("id") * 3600),
    )
    df = (
        df.withColumn("date", F.to_date(F.col("ts")))
        .withColumn("year", F.year(F.col("ts")))
        .withColumn("month", F.month(F.col("ts")))
        .withColumn("day", F.dayofmonth(F.col("ts")))
        .withColumn("hour", F.hour(F.col("ts")))
        .withColumn("weekday", F.date_format(F.col("ts"), "EEEE"))
        .withColumn("is_weekend", F.dayofweek(F.col("ts")).isin([1, 7]))
        .withColumn("date_dow", (F.dayofweek(F.col("ts")) - F.lit(1)).cast(IntegerType()))
        .withColumn("time_id", F.xxhash64(F.col("date"), F.col("hour")))
    )
    return df.select("time_id", "date", "year", "month", "day", "hour", "weekday", "is_weekend", "date_dow").orderBy("time_id")


def _build_dim_offense(df: DataFrame) -> DataFrame:
    dim = df.select("iucr", "primary_type", "description", "fbi_code").distinct()
    w = F.row_number().over(Window.partitionBy("iucr").orderBy(F.col("primary_type")))
    dim = dim.withColumn("_rn", w).filter(F.col("_rn") == 1).drop("_rn")
    dim = dim.withColumn("offense_id", F.xxhash64(F.col("iucr")))
    return dim.select("offense_id", "iucr", "primary_type", "description", "fbi_code").orderBy("offense_id")


def _build_dim_location(df: DataFrame, cfg: dict) -> DataFrame:
    dt_bbox = cfg.get("downtown_bbox", {})
    dt_min_lat = dt_bbox.get("min_lat", 41.880)
    dt_max_lat = dt_bbox.get("max_lat", 41.895)
    dt_min_lon = dt_bbox.get("min_lon", -87.635)
    dt_max_lon = dt_bbox.get("max_lon", -87.618)

    dim = df.select(
        "block", "location_description", "district", "ward",
        "community_area", "latitude", "longitude",
    ).distinct()

    dim = dim.withColumn(
        "is_downtown",
        F.when(
            F.col("latitude").isNull() | F.col("longitude").isNull(), F.lit(False),
        ).otherwise(
            F.col("latitude").between(dt_min_lat, dt_max_lat)
            & F.col("longitude").between(dt_min_lon, dt_max_lon),
        ),
    )

    dim = dim.withColumn(
        "distance_to_downtown_km",
        F.when(
            F.col("latitude").isNull() | F.col("longitude").isNull(), F.lit(999999.0).cast(FloatType()),
        ).otherwise(_haversine_km("latitude", "longitude")),
    )

    dim = dim.withColumn(
        "geom_wkt",
        F.when(
            F.col("latitude").isNull() | F.col("longitude").isNull(), F.lit(None).cast(StringType()),
        ).otherwise(
            F.concat(F.lit("POINT ("), F.col("longitude"), F.lit(" "), F.col("latitude"), F.lit(")")),
        ),
    )

    # Use monotonically_increasing_id for a guaranteed-unique surrogate key
    dim = dim.withColumn("location_id", F.monotonically_increasing_id())
    return dim.select(
        "location_id", "block", "location_description", "district", "ward",
        "community_area", "latitude", "longitude", "is_downtown",
        "distance_to_downtown_km", "geom_wkt",
    ).orderBy("location_id")


def _build_dim_case(df: DataFrame) -> DataFrame:
    dim = df.select("case_number", "updated_on").distinct()
    dim = dim.withColumn("case_id", F.xxhash64(F.col("case_number")))
    return dim.select("case_id", "case_number", "updated_on").orderBy("case_id")


def _build_fact_crime(df: DataFrame, dim_time: DataFrame, dim_offense: DataFrame, dim_location: DataFrame, dim_case: DataFrame) -> DataFrame:
    dim_time_daily = (
        dim_time
        .groupBy("date")
        .agg(F.min("time_id").alias("time_id"))
    )

    # Join fact to dim_location on the real location columns (not a hash)
    fact = (
        df
        .join(F.broadcast(dim_offense.select("iucr", "offense_id")), "iucr", "left")
        .join(
            F.broadcast(dim_location.select(
                "location_id", "block", "location_description", "district",
                "ward", "community_area", "latitude", "longitude",
            )),
            ["block", "location_description", "district", "ward", "community_area", "latitude", "longitude"],
            "left",
        )
        .withColumnRenamed("location_id", "location_id_fk")
        .join(F.broadcast(dim_case.select("case_number", "case_id")), "case_number", "left")
        .join(F.broadcast(dim_time_daily), "date", "left")
    )

    fact = fact.withColumn(
        "crime_id",
        F.xxhash64(F.col("id"), F.col("case_number")),
    )

    fact = fact.withColumn(
        "_gold_ingest_ts",
        F.lit(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")).cast(TimestampType()),
    )

    fact = fact.withColumn("year", F.year(F.col("date")))

    fact_cols = [
        "crime_id", "time_id", "offense_id", "case_id", "location_id_fk",
        "arrest", "domestic", "beat", "fbi_code",
        "is_arrested", "is_domestic", "is_domestic_arrest",
        "is_unassigned_district", "is_unassigned_community", "is_unassigned_ward",
        "hours_to_update", "date_dow", "year", "_gold_ingest_ts",
    ]
    fact_cols_existing = [c for c in fact_cols if c in fact.columns]
    extra_fact_cols = [c for c in fact_cols if c not in fact.columns]
    for c in extra_fact_cols:
        fact = fact.withColumn(c, F.lit(None).cast(IntegerType()))
    return fact.select(fact_cols).withColumnRenamed("location_id_fk", "location_id")


def gold_transform(spark: SparkSession, silver_path: str, output_root: str | None = None) -> dict[str, int]:
    cfg = settings.gold
    bucket = settings.storage.get("bucket", "lake")
    prefix = cfg.get("prefix", "gold/chicago_crime")
    output_root = output_root or f"s3a://{bucket}/{prefix}"

    log.info("gold_read_silver", path=silver_path)
    df = spark.read.parquet(silver_path)
    total_silver = df.count()
    log.info("gold_silver_row_count", count=total_silver)

    log.info("gold_build_dim_time")
    dim_time = _build_dim_time(spark, cfg)

    log.info("gold_build_dim_offense")
    dim_offense = _build_dim_offense(df)

    log.info("gold_build_dim_location")
    dim_location = _build_dim_location(df, cfg)

    log.info("gold_build_dim_case")
    dim_case = _build_dim_case(df)

    log.info("gold_build_fact_crime")
    fact = _build_fact_crime(df, dim_time, dim_offense, dim_location, dim_case)

    counts = {
        "silver_input": total_silver,
        "fact_crime": fact.count(),
        "dim_time": dim_time.count(),
        "dim_location": dim_location.count(),
        "dim_offense": dim_offense.count(),
        "dim_case": dim_case.count(),
    }

    log.info("gold_write_dim_time", path=_gold_path(output_root, "dim_time"))
    dim_time.write.mode("overwrite").parquet(_gold_path(output_root, "dim_time"))

    log.info("gold_write_dim_offense", path=_gold_path(output_root, "dim_offense"))
    dim_offense.write.mode("overwrite").parquet(_gold_path(output_root, "dim_offense"))

    log.info("gold_write_dim_location", path=_gold_path(output_root, "dim_location"))
    dim_location.write.mode("overwrite").parquet(_gold_path(output_root, "dim_location"))

    log.info("gold_write_dim_case", path=_gold_path(output_root, "dim_case"))
    dim_case.write.mode("overwrite").parquet(_gold_path(output_root, "dim_case"))

    log.info("gold_write_fact_crime", path=_gold_path(output_root, "fact_crime"))
    fact.write.mode("overwrite").partitionBy("year").parquet(_gold_path(output_root, "fact_crime"))

    log.info("gold_write_complete", counts=counts)
    return counts


if __name__ == "__main__":
    from chicago_pipeline.common.spark_session import get_spark

    silver_path = sys.argv[1] if len(sys.argv) > 1 else "s3a://lake/silver/chicago_crime"
    output_root = sys.argv[2] if len(sys.argv) > 2 else None
    spark = get_spark(app_name="GoldTransform")
    try:
        counts = gold_transform(spark, silver_path, output_root)
        print(f"Gold transform complete: {counts}")
    finally:
        spark.stop()
