import sys
from datetime import UTC, datetime
from pathlib import Path

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


def bronze_writer(spark: SparkSession, source_csv: str, output_root: str | None = None) -> int:
    cfg = settings.bronze
    bucket = settings.storage.get("bucket", "lake")
    prefix = cfg.get("prefix", "bronze/chicago_crime")
    partition_col = cfg.get("partition_by", "ingest_date")
    ingest_ts_col = cfg.get("ingest_ts_column", "_ingest_ts")
    output_root = output_root or f"s3a://{bucket}/{prefix}"

    now = datetime.now(UTC)
    ingest_date_str = now.strftime("%Y-%m-%d")

    df = (
        spark.read.schema(BRONZE_SCHEMA)
        .option("header", True)
        .csv(source_csv)
        .withColumn(ingest_ts_col, lit(now.isoformat()))
        .withColumn(partition_col, to_date(lit(ingest_date_str)))
    )

    output_path = f"{output_root}/{partition_col}={ingest_date_str}"
    df.write.mode("overwrite").parquet(output_path)

    row_count = df.count()
    log.info(
        "bronze_write_complete",
        source=source_csv,
        output=output_path,
        rows=row_count,
    )
    return row_count


if __name__ == "__main__":
    _src = Path(__file__).resolve().parents[2]
    if str(_src) not in sys.path:
        sys.path.insert(0, str(_src))

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
