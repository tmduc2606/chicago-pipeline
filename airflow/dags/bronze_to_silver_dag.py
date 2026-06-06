"""
Bronze -> Silver DAG -- Chicago Crime DBMS.

Schedule: @daily (after ingest_dag)
SLA: 45 minutes
On-call: data-engineer

Validates Bronze data with Great Expectations, transforms to Silver
(cleaned, typed, deduped), runs district drift detection, and writes
Parquet to MinIO. Alerts on drift detection.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta

from airflow.decorators import dag, task

sys.path.insert(0, "/opt/pipeline/src")

from chicago_pipeline.common.logger import get_logger

log = get_logger(__name__)

DEFAULT_ARGS = {
    "owner": "data-engineer",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(minutes=45),
}

BRONZE_PATH = "s3a://lake/bronze/chicago_crime/ingest_date={{ ds_nodash }}"
SILVER_PATH = "s3a://lake/silver/chicago_crime"


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
    dag_id="bronze_to_silver_dag",
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["silver", "transform", "drift"],
    description="Validate Bronze, transform to Silver, detect district drift",
    doc_md=__doc__,
)
def bronze_to_silver_dag() -> None:

    from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

    ge_checkpoint_bronze = SparkSubmitOperator(
        task_id="ge_checkpoint_bronze",
        application="/opt/great_expectations/run_validation.py",
        name="GEValidation-bronze",
        conn_id="spark_default",
        master="spark://spark-master:7077",
        application_args=[BRONZE_PATH, "chicago_crime_bronze", "bronze_checkpoint"],
        verbose=True,
        conf_func=_get_s3a_conf,
    )

    spark_silver = SparkSubmitOperator(
        task_id="spark_silver",
        application="/opt/pipeline/src/chicago_pipeline/silver/to_silver.py",
        name="BronzeToSilver",
        conn_id="spark_default",
        master="spark://spark-master:7077",
        application_args=[BRONZE_PATH, SILVER_PATH],
        verbose=True,
        conf_func=_get_s3a_conf,
    )

    ge_checkpoint_silver = SparkSubmitOperator(
        task_id="ge_checkpoint_silver",
        application="/opt/great_expectations/run_validation.py",
        name="GEValidation-silver",
        conn_id="spark_default",
        master="spark://spark-master:7077",
        application_args=[SILVER_PATH, "chicago_crime_silver", "silver_checkpoint"],
        verbose=True,
        conf_func=_get_s3a_conf,
    )

    detect_district_drift = SparkSubmitOperator(
        task_id="detect_district_drift",
        application="/opt/great_expectations/run_drift_detection.py",
        name="DriftDetection",
        conn_id="spark_default",
        master="spark://spark-master:7077",
        application_args=[SILVER_PATH, "chicago_crime_silver"],
        verbose=True,
        conf_func=_get_s3a_conf,
    )

    ge_checkpoint_bronze >> spark_silver >> ge_checkpoint_silver >> detect_district_drift


dag_instance = bronze_to_silver_dag()
