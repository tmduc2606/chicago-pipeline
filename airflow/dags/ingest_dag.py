"""
Ingest DAG — Chicago Crime DBMS.

Schedule: @daily
SLA: 30 minutes
On-call: data-engineer

Generates synthetic source CSV and uploads as Bronze Parquet to MinIO.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from airflow.decorators import dag, task

sys.path.insert(0, "/opt/pipeline/src")

from chicago_pipeline.ingest.download_kaggle import generate_synthetic, verify_csv
from chicago_pipeline.common.logger import get_logger

log = get_logger(__name__)

DEFAULT_ARGS = {
    "owner": "data-engineer",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(minutes=30),
}

SOURCE_CSV = "/tmp/chicago_crime/source.csv"
SYNTHETIC_DAYS = int(os.getenv("SYNTHETIC_DAYS", "90"))
SYNTHETIC_START = os.getenv("SYNTHETIC_START", "2024-01-01")
SYNTHETIC_SEED = int(os.getenv("SYNTHETIC_SEED", "42"))


def _get_s3a_conf() -> dict:
    from airflow.models.variable import Variable
    return {
        "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
        "spark.hadoop.fs3a.endpoint": "http://minio:9000",
        "spark.hadoop.fs.s3a.access.key": Variable.get("MINIO_ROOT_USER"),
        "spark.hadoop.fs.s3a.secret.key": Variable.get("MINIO_ROOT_PASSWORD"),
        "spark.hadoop.fs.s3a.path.style.access": "true",
        "spark.hadoop.fs.s3a.connection.ssl.enabled": "false",
    }


@dag(
    dag_id="ingest_dag",
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["bronze", "ingest"],
    description="Generate synthetic source CSV and upload to Bronze on MinIO",
    doc_md=__doc__,
)
def ingest_dag() -> None:

    @task(task_id="generate_data")
    def generate_data() -> int:
        rows = generate_synthetic(
            SOURCE_CSV,
            days=SYNTHETIC_DAYS,
            start_date=SYNTHETIC_START,
            seed=SYNTHETIC_SEED,
        )
        log.info("synthetic_data_generated", path=SOURCE_CSV, rows=rows)
        return rows

    @task(task_id="verify_checksum")
    def verify_checksum(**kwargs) -> int:
        ti = kwargs["ti"]
        row_count = ti.xcom_pull(task_ids="generate_data")
        count = verify_csv(SOURCE_CSV)
        if count < 1000:
            raise ValueError(
                f"Row count {count} below minimum threshold of 1000"
            )
        log.info("checksum_passed", rows=count, expected=row_count)
        return count

    from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

    upload_bronze = SparkSubmitOperator(
        task_id="upload_bronze",
        application="/opt/pipeline/src/chicago_pipeline/bronze/to_bronze.py",
        name="BronzeWriter",
        conn_id="spark_default",
        application_args=[SOURCE_CSV],
        verbose=True,
        conf_func=_get_s3a_conf,
    )

    dl = generate_data()
    vc = verify_checksum()
    dl >> vc >> upload_bronze


dag_instance = ingest_dag()
