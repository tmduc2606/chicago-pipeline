"""
Warehouse Load DAG — reads Gold Parquet from MinIO, writes to Postgres via load_postgres.py,
then runs dbt models and tests.

Schedule: @daily after Gold transform completes.
Owned by: Data Engineer agent.

All tasks execute inside spark-master (where dbt-postgres, pandas, pyarrow are installed).
"""
from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

DAG_ID = "warehouse_load"

default_args = {
    "owner": "data-engineer",
    "depends_on_past": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(minutes=30),
}

with DAG(
    dag_id=DAG_ID,
    default_args=default_args,
    description="Load Gold Parquet to Postgres, then run dbt",
    schedule_interval="@daily",
    start_date=days_ago(1),
    catchup=False,
    tags=["warehouse", "postgres", "dbt"],
) as dag:

    load_postgres = BashOperator(
        task_id="load_postgres",
        bash_command=(
            "docker compose exec -T spark-master "
            'bash -c "cd /opt/pipeline && PYTHONPATH=/opt/pipeline/src ENV=local '
            'python3 src/chicago_pipeline/warehouse/load_postgres.py"'
        ),
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=(
            "docker compose exec -T spark-master "
            'bash -c "cd /opt/dbt && dbt run --profiles-dir ."'
        ),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=(
            "docker compose exec -T spark-master "
            'bash -c "cd /opt/dbt && dbt test --profiles-dir ."'
        ),
    )

    load_postgres >> dbt_run >> dbt_test
