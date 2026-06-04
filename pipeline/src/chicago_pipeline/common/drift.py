"""District drift detection, Slack alerting, and auto-remediation."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any
from urllib.request import Request, urlopen

from chicago_pipeline.common.logger import get_logger
from chicago_pipeline.common.settings import settings

log = get_logger(__name__)

DRIFT_REPORT_PREFIX = "s3a://lake/reports/drift"


def _send_slack_alert(drift: dict) -> bool:
    webhook = settings.validation.get("districts", {}).get("slack_webhook_url", "")
    if not webhook:
        log.info("slack_alert_skipped", reason="no webhook configured")
        return False

    new = drift.get("new_values", [])
    missing = drift.get("missing_values", [])
    lines = [f":warning: *District Drift Detected* — {drift.get('suite_name', 'unknown')}"]
    if new:
        lines.append(f"*New districts:* {new}")
    if missing:
        lines.append(f"*Missing districts:* {missing}")
    lines.append(f"*Path:* {drift.get('data_path', 'N/A')}")
    payload = json.dumps({"text": "\n".join(lines)}).encode()

    try:
        req = Request(webhook, data=payload, headers={"Content-Type": "application/json"})
        urlopen(req, timeout=10)
        log.info("slack_alert_sent", new_values=new, missing_values=missing)
        return True
    except Exception as e:
        log.warning("slack_alert_failed", error=str(e))
        return False


def _auto_remediate_districts(drift: dict) -> list[int]:
    if not settings.validation.get("districts", {}).get("auto_remediate", False):
        log.info("auto_remediate_skipped", reason="auto_remediate disabled")
        return []

    new_values = drift.get("new_values", [])
    if not new_values:
        return []

    config_path = os.getenv("CONFIG_PATH", "/opt/pipeline/conf/base.yaml")
    try:
        with open(config_path) as f:
            raw = f.read()

        import yaml
        config = yaml.safe_load(raw)
        current = config.get("validation", {}).get("districts", {}).get("allowed", [])
        updated = sorted(set(current + new_values))
        config.setdefault("validation", {}).setdefault("districts", {})["allowed"] = updated

        import yaml as yaml_out
        with open(config_path, "w") as f:
            yaml_out.dump(config, f, default_flow_style=False)

        log.info("auto_remediation_done", new_values=new_values, updated_allowed=updated)
        return updated
    except Exception as e:
        log.warning("auto_remediation_failed", error=str(e))
        return []


def _detect_district_drift(
    df: Any,
    suite_name: str,
    data_path: str = "",
) -> dict:
    from pyspark.sql.functions import col as spark_col

    if "district" not in df.columns:
        return {
            "drift_detected": False,
            "new_values": [],
            "missing_values": [],
            "note": "SKIPPED: district column not present in this dataset",
        }

    allowed_raw = settings.validation.get("districts", {}).get("allowed", [])
    allowed = sorted(allowed_raw) if allowed_raw else []

    actual_rows = df.select(spark_col("district")).distinct().collect()
    actual = sorted([r["district"] for r in actual_rows if r["district"] is not None])

    return _compare_district_sets(allowed, actual, suite_name, data_path)


def _compare_district_sets(
    allowed: list[int],
    actual: list[int],
    suite_name: str,
    data_path: str = "",
) -> dict:
    """Pure comparison of allowed vs actual district sets — no PySpark dependency."""
    allowed_set = set(allowed)
    actual_set = set(actual)

    new_values = sorted(actual_set - allowed_set)
    missing_values = sorted(allowed_set - actual_set)

    drift = {
        "suite_name": suite_name,
        "data_path": data_path or "unknown",
        "drift_detected": bool(new_values or missing_values),
        "allowed_set": allowed,
        "actual_set": actual,
        "new_values": new_values,
        "missing_values": missing_values,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if new_values:
        log.warning("district_drift_new", new_values=new_values)
    if missing_values:
        log.warning("district_drift_missing", missing_values=missing_values)
    if not drift["drift_detected"]:
        log.info("district_drift_none")

    return drift


def _write_drift_report(spark: Any, drift: dict, suite_name: str) -> str | None:
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    ts_str = now.strftime("%H%M%S")
    s3_path = f"{DRIFT_REPORT_PREFIX}/{suite_name}/{date_str}/{ts_str}_drift.json"

    try:
        rdd = spark.sparkContext.parallelize([json.dumps(drift, default=str)])
        rdd.coalesce(1).saveAsTextFile(s3_path)
        log.info("drift_report_written", path=s3_path)
        return s3_path
    except Exception as e:
        log.warning("drift_report_s3a_failed", path=s3_path, error=str(e))
        return None


def run_drift_detection(
    df: Any,
    suite_name: str,
    data_path: str = "",
    spark: Any | None = None,
) -> dict:
    drift = _detect_district_drift(df, suite_name, data_path)

    if drift["drift_detected"]:
        _send_slack_alert(drift)
        _auto_remediate_districts(drift)

    if spark:
        _write_drift_report(spark, drift, suite_name)

    return drift
