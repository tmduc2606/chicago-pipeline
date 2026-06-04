"""Unit tests for Silver layer (M2)."""
import json
import os
import tempfile
from pathlib import Path

import pytest


def test_silver_module_importable():
    from chicago_pipeline.silver import to_silver
    assert hasattr(to_silver, "silver_transform")
    assert hasattr(to_silver, "SILVER_COLUMNS")


def test_silver_columns_definition():
    from chicago_pipeline.silver.to_silver import SILVER_COLUMNS
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
    assert set(SILVER_COLUMNS.keys()) == expected
    assert len(SILVER_COLUMNS) == 29


def test_extension_columns_dtypes():
    from chicago_pipeline.silver.to_silver import SILVER_COLUMNS
    from pyspark.sql.types import BooleanType, IntegerType, TimestampType
    bool_flags = ["is_arrested", "is_domestic", "is_domestic_arrest",
                  "is_unassigned_district", "is_unassigned_community", "is_unassigned_ward"]
    for c in bool_flags:
        assert isinstance(SILVER_COLUMNS[c], BooleanType), f"{c} should be BooleanType"

    int_date = ["date_year", "date_month", "date_dow"]
    for c in int_date:
        assert isinstance(SILVER_COLUMNS[c], IntegerType), f"{c} should be IntegerType"

    assert isinstance(SILVER_COLUMNS["updated_on_ts"], TimestampType), "updated_on_ts should be TimestampType"
    assert isinstance(SILVER_COLUMNS["hours_to_update"], IntegerType), "hours_to_update should be IntegerType"


def test_extension_functions_exist():
    from chicago_pipeline.silver.to_silver import (
        _standardize_text, _add_updated_on_ts, _add_date_components,
        _add_conforming_booleans, _add_hours_to_update,
    )
    assert callable(_standardize_text)
    assert callable(_add_updated_on_ts)
    assert callable(_add_date_components)
    assert callable(_add_conforming_booleans)
    assert callable(_add_hours_to_update)


def test_text_cols_defined():
    from chicago_pipeline.silver.to_silver import TEXT_COLS
    assert len(TEXT_COLS) == 7
    assert "primary_type" in TEXT_COLS
    assert "beat" in TEXT_COLS


def test_silver_suite_loadable():
    suite_path = Path(__file__).resolve().parents[2] / "great_expectations" / "suites" / "chicago_crime_silver.json"
    assert suite_path.exists(), f"Silver suite not found at {suite_path}"
    with open(suite_path) as f:
        suite = json.load(f)
    assert suite["expectation_suite_name"] == "chicago_crime_silver"
    assert len(suite["expectations"]) >= 18


def test_ge_config_exists():
    config_path = Path(__file__).resolve().parents[2] / "great_expectations" / "great_expectations.yml"
    assert config_path.exists(), f"GE config not found at {config_path}"
    content = config_path.read_text()
    assert "spark_s3" in content
    assert "FileDataContext" in content or "class_name" in content


def test_ge_checkpoints_exist():
    checkpoints_dir = Path(__file__).resolve().parents[2] / "great_expectations" / "checkpoints"
    assert (checkpoints_dir / "bronze_checkpoint.yml").exists()
    assert (checkpoints_dir / "silver_checkpoint.yml").exists()


def test_ge_validation_script_exists():
    script_path = Path(__file__).resolve().parents[2] / "great_expectations" / "run_validation.py"
    assert script_path.exists()
    content = script_path.read_text()
    assert "run_validation" in content
    assert "SparkSession" in content


def test_ge_reports_dir_creatable():
    reports_dir = Path(__file__).resolve().parents[2] / "great_expectations" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    assert reports_dir.exists()


def test_ge_suite_expectations_structure():
    suite_path = Path(__file__).resolve().parents[2] / "great_expectations" / "suites" / "chicago_crime_bronze.json"
    with open(suite_path) as f:
        suite = json.load(f)
    for exp in suite["expectations"]:
        assert "expectation_type" in exp
        assert "kwargs" in exp
        assert "meta" in exp


def test_silver_config_in_base_yaml():
    import yaml
    config_path = Path(__file__).resolve().parents[2] / "pipeline" / "conf" / "base.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    assert "silver" in config
    silver = config["silver"]
    assert "prefix" in silver
    assert "chicago_bbox" in silver
    assert "date_range" in silver
    assert "validation" in config
    districts = config["validation"]["districts"]
    assert "allowed" in districts
    assert len(districts["allowed"]) == 25
    assert "slack_webhook_url" in districts
    assert "auto_remediate" in districts


def test_drift_module_importable():
    from chicago_pipeline.common.drift import (
        run_drift_detection, _detect_district_drift, _compare_district_sets,
        _send_slack_alert, _auto_remediate_districts,
    )
    assert callable(run_drift_detection)
    assert callable(_detect_district_drift)
    assert callable(_compare_district_sets)
    assert callable(_send_slack_alert)
    assert callable(_auto_remediate_districts)


def test_drift_detection_no_drift():
    from chicago_pipeline.common.drift import _compare_district_sets
    allowed = list(range(1, 26))
    actual = list(range(1, 26))
    drift = _compare_district_sets(allowed, actual, "test_suite", "test")
    assert not drift["drift_detected"]
    assert drift["new_values"] == []
    assert drift["missing_values"] == []


def test_drift_detection_with_new_values():
    from chicago_pipeline.common.drift import _compare_district_sets
    allowed = list(range(1, 26))
    actual = list(range(1, 28))
    drift = _compare_district_sets(allowed, actual, "test_suite", "test")
    assert drift["drift_detected"]
    assert drift["new_values"] == [26, 27]
    assert drift["missing_values"] == []


def test_drift_detection_with_missing_values():
    from chicago_pipeline.common.drift import _compare_district_sets
    allowed = list(range(1, 26))
    actual = list(range(1, 24))
    drift = _compare_district_sets(allowed, actual, "test_suite", "test")
    assert drift["drift_detected"]
    assert drift["new_values"] == []
    assert drift["missing_values"] == [24, 25]


def test_settings_validation_property():
    from chicago_pipeline.common.settings import settings
    v = settings.validation
    assert "districts" in v
    assert v["districts"]["allowed"] == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
