"""
Ingest DAG — Chicago Crime DBMS.

Schedule: @daily
SLA: 30 minutes
On-call: data-engineer

Downloads source CSV (Kaggle or synthetic fallback), verifies integrity,
and uploads as Bronze Parquet to MinIO.
"""

from __future__ import annotations

import csv
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from airflow.decorators import dag, task
from airflow.operators.python import PythonOperator

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
        "spark.hadoop.fs.s3a.endpoint": "http://minio:9000",
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
    description="Download source CSV and upload to Bronze on MinIO",
    doc_md=__doc__,
)
def ingest_dag() -> None:

    @task(task_id="kaggle_download")
    def kaggle_download() -> int:
        try:
            import kagglehub
            dataset = os.getenv("KAGGLE_DATASET", "chicago/chicago-crime-2024-2026")
            path = kagglehub.dataset_download(dataset)
            csv_files = list(Path(path).glob("*.csv"))
            if not csv_files:
                raise FileNotFoundError(f"No CSV found in {path}")
            import shutil
            shutil.copy(csv_files[0], SOURCE_CSV)
            count = verify_csv(SOURCE_CSV)
            log.info("kaggle_download_success", path=str(csv_files[0]), rows=count)
            return count
        except Exception as exc:
            log.warning("kaggle_fallback_to_synthetic", error=str(exc))
            return generate_synthetic(
                SOURCE_CSV,
                days=SYNTHETIC_DAYS,
                start_date=SYNTHETIC_START,
                seed=SYNTHETIC_SEED,
            )

    @task(task_id="verify_checksum")
    def verify_checksum(**kwargs) -> int:
        ti = kwargs["ti"]
        row_count = ti.xcom_pull(task_ids="kaggle_download")
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

    dl = kaggle_download()
    vc = verify_checksum()
    dl >> vc >> upload_bronze


dag_instance = ingest_dag()
