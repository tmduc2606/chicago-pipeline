"""Run Great Expectations validation on Bronze or Silver data."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_src = Path("/opt/pipeline/src")
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from pyspark.sql import SparkSession

from chicago_pipeline.common.logger import get_logger
from chicago_pipeline.common.settings import settings

log = get_logger(__name__)


def _build_spark(app_name: str = "GEValidation") -> SparkSession:
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


def _load_suite(suite_path: str) -> list[dict]:
    with open(suite_path) as f:
        suite = json.load(f)
    return suite.get("expectations", [])


def _apply_config_overrides(expectations: list[dict]) -> list[dict]:
    """Override expectation kwargs from pipeline config (Phase 1: district set)."""
    district_allowed = settings.validation.get("districts", {}).get("allowed")
    if district_allowed:
        for exp in expectations:
            if (
                exp["expectation_type"] == "expect_column_values_to_be_in_set"
                and exp["kwargs"].get("column") == "district"
            ):
                exp["kwargs"]["value_set"] = district_allowed
                log.info("district_set_overridden", count=len(district_allowed))
    return expectations


def _validate_expectation(df, exp: dict) -> tuple[bool, str]:
    exp_type = exp["expectation_type"]
    kwargs = exp.get("kwargs", {})

    if exp_type == "expect_column_values_to_not_be_null":
        col = kwargs["column"]
        count = df.filter(f"{col} IS NULL").count()
        return count == 0, f"{count} null values in {col}"

    elif exp_type == "expect_column_values_to_be_unique":
        col = kwargs["column"]
        total = df.count()
        distinct = df.select(col).distinct().count()
        return total == distinct, f"{total - distinct} duplicates in {col}"

    elif exp_type == "expect_column_values_to_match_regex":
        col = kwargs["column"]
        regex = kwargs["regex"]
        from pyspark.sql.functions import col as spark_col, regexp_count, lit
        bad = df.filter(regexp_count(spark_col(col), lit(regex)) == 0).count()
        return bad == 0, f"{bad} values in {col} don't match regex"

    elif exp_type == "expect_column_values_to_be_between":
        col = kwargs["column"]
        min_val = kwargs.get("min_value")
        max_val = kwargs.get("max_value")
        from pyspark.sql.functions import col as spark_col
        condition = spark_col(col).between(min_val, max_val)
        bad = df.filter(~condition).count()
        return bad == 0, f"{bad} values in {col} outside [{min_val}, {max_val}]"

    elif exp_type == "expect_table_row_count_to_be_between":
        min_val = kwargs.get("min_value", 0)
        max_val = kwargs.get("max_value")
        count = df.count()
        ok = count >= min_val
        if max_val is not None:
            ok = ok and count <= max_val
        return ok, f"row count {count} not in [{min_val}, {max_val}]"

    elif exp_type == "expect_column_values_to_be_of_type":
        col = kwargs["column"]
        expected = kwargs["type_"]
        actual = df.schema[col].dataType.simpleString()
        return actual == expected, f"{col} type is {actual}, expected {expected}"

    elif exp_type == "expect_column_values_to_be_in_set":
        from pyspark.sql.functions import col as spark_col
        col = kwargs["column"]
        value_set = set(kwargs["value_set"])
        bad = df.filter(~spark_col(col).isin(list(value_set))).count()
        return bad == 0, f"{bad} values in {col} not in allowed set"

    else:
        return True, f"SKIPPED: {exp_type} (not implemented)"


def _write_report_local(report: dict, suite_name: str) -> Path:
    report_path = Path("/opt/great_expectations/reports") / f"{suite_name}_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    return report_path


def _write_report_s3a(spark: SparkSession, report: dict, suite_name: str) -> str | None:
    bucket = settings.storage.get("bucket", "lake")
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    ts_str = now.strftime("%H%M%S")
    s3_path = f"s3a://{bucket}/reports/ge/{suite_name}/{date_str}/{ts_str}_report.json"

    try:
        rdd = spark.sparkContext.parallelize([json.dumps(report, default=str)])
        rdd.coalesce(1).saveAsTextFile(s3_path)
        return s3_path
    except Exception as e:
        log.warning("ge_report_s3a_failed", path=s3_path, error=str(e))
        return None


def _check_schema_evolution(df, suite_name: str) -> list[str]:
    warnings = []
    schema_cols = {f.name for f in df.schema.fields}

    if suite_name == "chicago_crime_silver":
        expected = {
            "id", "case_number", "date", "block", "iucr", "primary_type",
            "description", "location_description", "arrest", "domestic",
            "beat", "district", "ward", "community_area", "fbi_code",
            "latitude", "longitude", "updated_on",
            "is_arrested", "is_domestic", "is_domestic_arrest",
            "is_unassigned_district", "is_unassigned_community", "is_unassigned_ward",
            "date_year", "date_month", "date_dow",
            "updated_on_ts", "hours_to_update",
        }
        missing = expected - schema_cols
        extra = schema_cols - expected - {"_ingest_ts", "ingest_date", "year", "month"}
        if missing:
            warnings.append(f"Missing expected columns: {sorted(missing)}")
        if extra:
            warnings.append(f"Unexpected new columns: {sorted(extra)}")

    return warnings


def run_validation(
    data_path: str,
    suite_name: str = "chicago_crime_bronze",
    checkpoint_name: str = "bronze_checkpoint",
) -> bool:
    spark = _build_spark(f"GEValidation-{suite_name}")
    df = spark.read.parquet(data_path)

    suite_path = Path("/opt/great_expectations/suites") / f"{suite_name}.json"
    expectations = _load_suite(str(suite_path))
    expectations = _apply_config_overrides(expectations)

    all_passed = True
    results = []

    for exp in expectations:
        passed, msg = _validate_expectation(df, exp)
        severity = exp.get("meta", {}).get("severity", "info")
        status = "PASS" if passed else "FAIL"
        log.info(
            "ge_expectation",
            expectation=exp["expectation_type"],
            status=status,
            severity=severity,
            message=msg,
        )
        results.append({
            "expectation": exp["expectation_type"],
            "status": status,
            "severity": severity,
            "message": msg,
        })
        if not passed and severity == "critical":
            all_passed = False

    from chicago_pipeline.common.drift import run_drift_detection
    drift = run_drift_detection(df, suite_name, data_path, spark)

    report = {
        "suite": suite_name,
        "data_path": data_path,
        "success": all_passed,
        "schema_warnings": _check_schema_evolution(df, suite_name),
        "drift": drift,
        "results": results,
    }

    _write_report_local(report, suite_name)
    s3_path = _write_report_s3a(spark, report, suite_name)

    if all_passed:
        print(f"VALIDATION PASSED: {suite_name}")
    else:
        print(f"VALIDATION FAILED: {suite_name}")
        for r in results:
            if r["status"] == "FAIL":
                print(f"  FAIL [{r['severity']}]: {r['expectation']}")
                print(f"        {r['message']}")

    if s3_path:
        log.info("ge_report_written", path=s3_path)

    spark.stop()
    return all_passed


if __name__ == "__main__":
    data_path = sys.argv[1] if len(sys.argv) > 1 else "s3a://lake/bronze/chicago_crime"
    suite = sys.argv[2] if len(sys.argv) > 2 else "chicago_crime_bronze"
    checkpoint = sys.argv[3] if len(sys.argv) > 3 else "bronze_checkpoint"

    ok = run_validation(data_path, suite, checkpoint)
    sys.exit(0 if ok else 1)
