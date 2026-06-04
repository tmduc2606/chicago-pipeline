"""
dbt Build DAG — runs dbt models and tests.

Schedule: @daily after Silver→Gold completes.
Owned by: Data Engineer agent.

All tasks execute inside spark-master (where dbt-postgres is installed).
"""
from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

DAG_ID = "dbt_build"

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
    description="Run dbt models and tests",
    schedule_interval="@daily",
    start_date=days_ago(1),
    catchup=False,
    tags=["dbt", "warehouse", "marts"],
) as dag:

    dbt_deps = BashOperator(
        task_id="dbt_deps",
        bash_command=(
            "docker compose exec -T spark-master "
            'bash -c "cd /opt/dbt && dbt deps --profiles-dir ."'
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

    dbt_docs = BashOperator(
        task_id="dbt_docs",
        bash_command=(
            "docker compose exec -T spark-master "
            'bash -c "cd /opt/dbt && dbt docs generate --profiles-dir ."'
        ),
    )

    dbt_deps >> dbt_run >> dbt_test >> dbt_docs
