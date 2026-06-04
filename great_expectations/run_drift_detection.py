"""
Standalone district drift detection — Spark submit entrypoint.

Usage:
    spark-submit --master spark://spark-master:7077 \\
        /opt/great_expectations/run_drift_detection.py \\
        s3a://lake/silver/chicago_crime \\
        chicago_crime_silver
"""
from __future__ import annotations

import sys
from pathlib import Path

_src = Path("/opt/pipeline/src")
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from chicago_pipeline.common.drift import run_drift_detection
from chicago_pipeline.common.logger import get_logger
from chicago_pipeline.common.settings import settings
from pyspark.sql import SparkSession

log = get_logger(__name__)


def _build_spark(app_name: str = "DriftDetection") -> SparkSession:
    return (
        SparkSession.builder
        .appName(app_name)
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.endpoint", settings.storage.get("endpoint", "http://minio:9000"))
        .config("spark.hadoop.fs.s3a.access.key", settings.storage.get("access_key", "minio"))
        .config("spark.hadoop.fs.s3a.secret.key", settings.storage.get("secret_key", "minio123"))
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        .getOrCreate()
    )


def main():
    data_path = sys.argv[1] if len(sys.argv) > 1 else "s3a://lake/silver/chicago_crime"
    suite_name = sys.argv[2] if len(sys.argv) > 2 else "chicago_crime_silver"

    spark = _build_spark(f"DriftDetection-{suite_name}")
    try:
        df = spark.read.parquet(data_path)
        drift = run_drift_detection(df, suite_name, data_path, spark)

        if drift.get("drift_detected"):
            print(f"DRIFT DETECTED: {suite_name}")
            if drift.get("new_values"):
                print(f"  New districts: {drift['new_values']}")
            if drift.get("missing_values"):
                print(f"  Missing districts: {drift['missing_values']}")
        else:
            print(f"NO DRIFT: {suite_name}")

        sys.exit(0)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
