from app.schemas.pipeline import DagRun, DagStatus


async def get_pipeline_status() -> list[DagStatus]:
    """Return pipeline DAG statuses.

    TODO: Connect to Airflow REST API (GET /api/v1/dags) using
    settings.airflow_base_url, airflow_user, airflow_password.
    Currently returns placeholder data.
    """
    return [
        DagStatus(dag_id="ingest_dag", last_run=None, state="none"),
        DagStatus(dag_id="bronze_to_silver_dag", last_run=None, state="none"),
        DagStatus(dag_id="silver_to_gold_dag", last_run=None, state="none"),
        DagStatus(dag_id="dbt_build_dag", last_run=None, state="none"),
    ]


async def get_pipeline_runs(dag_id: str, limit: int = 10) -> list[DagRun]:
    """Return recent runs for a given DAG.

    TODO: Connect to Airflow REST API (GET /api/v1/dags/{dag_id}/runs).
    Currently returns placeholder data.
    """
    return [
        DagRun(run_id="placeholder", dag_id=dag_id, state="success", start=None, end=None),
    ]
