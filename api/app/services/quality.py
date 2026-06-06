from app.schemas.quality import DbtResult, GeResult, QualitySummary


async def get_quality_summary() -> QualitySummary:
    """Return data quality summary.

    TODO: Connect to GE validation reports in S3A and dbt run results.
    Currently returns last-known values from the M4 verification run.
    """
    return QualitySummary(
        great_expectations=GeResult(success_pct=100.0, last_run=None),
        dbt=DbtResult(passed=53, failed=0, last_run=None),
    )
