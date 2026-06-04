"""
Silver -> Gold DAG -- Chicago Crime DBMS.

Schedule: @daily (after bronze_to_silver_dag)
SLA: 60 minutes
On-call: data-engineer

Validates Silver data with Great Expectations, transforms to Gold
(star schema: fact_crime + 4 dimension tables), and writes Parquet
to MinIO. Runs final GE validation on Gold fact table.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.models.variable import Variable
from airflow.operators.python import PythonOperator

sys.path.insert(0, "/opt/pipeline/src")

from chicago_pipeline.common.logger import get_logger

log = get_logger(__name__)

DEFAULT_ARGS = {
    "owner": "data-engineer",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(minutes=60),
}

SILVER_PATH = "s3a://lake/silver/chicago_crime"
GOLD_PATH = "s3a://lake/gold/chicago_crime"
GOLD_FACT_PATH = f"{GOLD_PATH}/fact_crime"

S3A_CONF = {
    "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
    "spark.hadoop.fs.s3a.endpoint": "http://minio:9000",
    "spark.hadoop.fs.s3a.access.key": Variable.get("MINIO_ROOT_USER", "minio"),
    "spark.hadoop.fs.s3a.secret.key": Variable.get("MINIO_ROOT_PASSWORD", "change_me_local"),
    "spark.hadoop.fs.s3a.path.style.access": "true",
    "spark.hadoop.fs.s3a.connection.ssl.enabled": "false",
}


@dag(
    dag_id="silver_to_gold_dag",
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["gold", "transform", "star-schema"],
    description="Validate Silver, transform to Gold star schema, validate Gold",
    doc_md=__doc__,
)
def silver_to_gold_dag() -> None:

    from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

    ge_checkpoint_silver = SparkSubmitOperator(
        task_id="ge_checkpoint_silver",
        application="/opt/great_expectations/run_validation.py",
        name="GEValidation-silver",
        conn_id="spark_default",
        master="spark://spark-master:7077",
        application_args=[SILVER_PATH, "chicago_crime_silver", "silver_checkpoint"],
        verbose=True,
        conf=S3A_CONF,
    )

    spark_gold = SparkSubmitOperator(
        task_id="spark_gold",
        application="/opt/pipeline/src/chicago_pipeline/gold/to_gold.py",
        name="SilverToGold",
        conn_id="spark_default",
        master="spark://spark-master:7077",
        application_args=[SILVER_PATH, GOLD_PATH],
        verbose=True,
        conf=S3A_CONF,
    )

    ge_checkpoint_gold = SparkSubmitOperator(
        task_id="ge_checkpoint_gold",
        application="/opt/great_expectations/run_validation.py",
        name="GEValidation-gold",
        conn_id="spark_default",
        master="spark://spark-master:7077",
        application_args=[GOLD_FACT_PATH, "chicago_crime_gold", "gold_checkpoint"],
        verbose=True,
        conf=S3A_CONF,
    )

    ge_checkpoint_silver >> spark_gold >> ge_checkpoint_gold


dag_instance = silver_to_gold_dag()
