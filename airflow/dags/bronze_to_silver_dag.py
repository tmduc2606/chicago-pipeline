"""
Bronze → Silver DAG — Chicago Crime DBMS.

Schedule: @daily (after ingest_dag)
SLA: 45 minutes
On-call: data-engineer

Validates Bronze data with Great Expectations, transforms to Silver
(cleaned, typed, deduped), and writes Parquet to MinIO.
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
    "execution_timeout": timedelta(minutes=45),
}

BRONZE_PATH = "s3a://lake/bronze/chicago_crime"
SILVER_PATH = "s3a://lake/silver/chicago_crime"


@dag(
    dag_id="bronze_to_silver_dag",
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["silver", "transform"],
    description="Validate Bronze and transform to Silver layer",
    doc_md=__doc__,
)
def bronze_to_silver_dag() -> None:

    @task(task_id="ge_checkpoint_bronze")
    def ge_checkpoint_bronze() -> bool:
        from great_expectations.core import ExpectationSuite
        from great_expectations.core.batch import RuntimeBatchRequest
        from great_expectations.data_context import FileDataContext

        context = FileDataContext(context_root_dir="/opt/great_expectations")

        batch_request = RuntimeBatchRequest(
            datasource_name="spark_s3",
            data_connector_name="default_runtime_data_connector_name",
            data_asset_name="chicago_crime",
            runtime_parameters={"path": BRONZE_PATH},
            batch_identifiers={"id": "bronze_validation"},
        )

        result = context.run_checkpoint(
            checkpoint_name="bronze_checkpoint",
            batch_request=batch_request,
            run_name=f"bronze_{datetime.now().isoformat()}",
        )

        if not result.success:
            log.error("bronze_validation_failed", result=result.to_json_dict())
            raise ValueError("Bronze validation failed — check GE report")

        log.info("bronze_validation_passed")
        return True

    @task(task_id="spark_silver")
    def spark_silver() -> int:
        from chicago_pipeline.common.spark_session import get_spark
        from chicago_pipeline.silver.to_silver import silver_transform

        spark = get_spark(app_name="BronzeToSilver")
        try:
            count = silver_transform(spark, BRONZE_PATH, SILVER_PATH)
            log.info("silver_transform_complete", rows=count)
            return count
        finally:
            spark.stop()

    @task(task_id="ge_checkpoint_silver")
    def ge_checkpoint_silver() -> bool:
        from great_expectations.core.batch import RuntimeBatchRequest
        from great_expectations.data_context import FileDataContext

        context = FileDataContext(context_root_dir="/opt/great_expectations")

        batch_request = RuntimeBatchRequest(
            datasource_name="spark_s3",
            data_connector_name="default_runtime_data_connector_name",
            data_asset_name="chicago_crime_silver",
            runtime_parameters={"path": SILVER_PATH},
            batch_identifiers={"id": "silver_validation"},
        )

        result = context.run_checkpoint(
            checkpoint_name="silver_checkpoint",
            batch_request=batch_request,
            run_name=f"silver_{datetime.now().isoformat()}",
        )

        if not result.success:
            log.error("silver_validation_failed", result=result.to_json_dict())
            raise ValueError("Silver validation failed — check GE report")

        log.info("silver_validation_passed")
        return True

    bronze_valid = ge_checkpoint_bronze()
    silver_count = spark_silver()
    silver_valid = ge_checkpoint_silver()

    bronze_valid >> silver_count >> silver_valid


dag_instance = bronze_to_silver_dag()
