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
    }
    assert set(SILVER_COLUMNS.keys()) == expected


def test_bronze_suite_loadable():
    suite_path = Path(__file__).resolve().parents[2] / "great_expectations" / "suites" / "chicago_crime_bronze.json"
    assert suite_path.exists(), f"Bronze suite not found at {suite_path}"
    with open(suite_path) as f:
        suite = json.load(f)
    assert suite["expectation_suite_name"] == "chicago_crime_bronze"
    assert len(suite["expectations"]) >= 5


def test_silver_suite_loadable():
    suite_path = Path(__file__).resolve().parents[2] / "great_expectations" / "suites" / "chicago_crime_silver.json"
    assert suite_path.exists(), f"Silver suite not found at {suite_path}"
    with open(suite_path) as f:
        suite = json.load(f)
    assert suite["expectation_suite_name"] == "chicago_crime_silver"
    assert len(suite["expectations"]) >= 5


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
    assert "RuntimeBatchRequest" in content


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
