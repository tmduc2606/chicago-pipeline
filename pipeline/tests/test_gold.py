"""Unit tests for Gold layer (M3)."""
import json
from pathlib import Path

import pytest


def test_gold_module_importable():
    from chicago_pipeline.gold import to_gold
    assert hasattr(to_gold, "gold_transform")


def test_gold_functions_exist():
    from chicago_pipeline.gold.to_gold import (
        _build_dim_time, _build_dim_offense, _build_dim_location,
        _build_dim_case, _build_fact_crime,
    )
    assert callable(_build_dim_time)
    assert callable(_build_dim_offense)
    assert callable(_build_dim_location)
    assert callable(_build_dim_case)
    assert callable(_build_fact_crime)


def test_gold_suite_loadable():
    suite_path = Path(__file__).resolve().parents[2] / "great_expectations" / "suites" / "chicago_crime_gold.json"
    assert suite_path.exists(), f"Gold suite not found at {suite_path}"
    with open(suite_path) as f:
        suite = json.load(f)
    assert suite["expectation_suite_name"] == "chicago_crime_gold"
    assert len(suite["expectations"]) >= 12


def test_gold_config_in_base_yaml():
    import yaml
    config_path = Path(__file__).resolve().parents[2] / "pipeline" / "conf" / "base.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    assert "gold" in config
    gold = config["gold"]
    assert gold["prefix"] == "gold/chicago_crime"
    assert "date_range" in gold
    assert "downtown_bbox" in gold
    bbox = gold["downtown_bbox"]
    assert bbox["min_lat"] == 41.880
    assert bbox["max_lat"] == 41.895
    assert bbox["min_lon"] == -87.635
    assert bbox["max_lon"] == -87.618


def test_settings_gold_property():
    from chicago_pipeline.common.settings import settings
    g = settings.gold
    assert g["prefix"] == "gold/chicago_crime"
    assert "downtown_bbox" in g


def test_gold_suite_expectations_structure():
    suite_path = Path(__file__).resolve().parents[2] / "great_expectations" / "suites" / "chicago_crime_gold.json"
    with open(suite_path) as f:
        suite = json.load(f)
    for exp in suite["expectations"]:
        assert "expectation_type" in exp
        assert "kwargs" in exp
        assert "meta" in exp


def test_ge_gold_checkpoint_exists():
    checkpoints_dir = Path(__file__).resolve().parents[2] / "great_expectations" / "checkpoints"
    assert checkpoints_dir.exists()


def test_silver_to_gold_dag_exists():
    dag_path = Path(__file__).resolve().parents[2] / "airflow" / "dags" / "silver_to_gold_dag.py"
    assert dag_path.exists()
    content = dag_path.read_text()
    assert "silver_to_gold_dag" in content
    assert "SparkSubmitOperator" in content
    assert "spark_gold" in content
    assert "ge_checkpoint_gold" in content


def test_run_validation_has_gold_schema_evolution():
    script_path = Path(__file__).resolve().parents[2] / "great_expectations" / "run_validation.py"
    content = script_path.read_text()
    assert "chicago_crime_gold" in content
    assert "Missing expected Gold columns" in content


def test_contract_gold_schema_exists():
    contract_path = Path(__file__).resolve().parents[2] / "contracts" / "gold-schema.json"
    assert contract_path.exists()
    with open(contract_path) as f:
        contract = json.load(f)
    assert contract["version"] == "1.0.0"
    tables = contract["tables"]
    for t in ["fact_crime", "dim_time", "dim_location", "dim_offense", "dim_case"]:
        assert t in tables, f"Missing table {t} in contract"
        assert "columns" in tables[t]
        assert "primary_key" in tables[t]


def test_gold_dim_time_schema_contract():
    contract_path = Path(__file__).resolve().parents[2] / "contracts" / "gold-schema.json"
    with open(contract_path) as f:
        contract = json.load(f)
    dim_time = contract["tables"]["dim_time"]
    expected_cols = {"time_id", "date", "year", "month", "day", "hour", "weekday", "is_weekend", "date_dow"}
    assert set(dim_time["columns"].keys()) == expected_cols
    assert dim_time["columns"]["time_id"]["type"] == "integer"
    assert dim_time["columns"]["date"]["type"] == "date"


def test_gold_fact_crime_schema_contract():
    contract_path = Path(__file__).resolve().parents[2] / "contracts" / "gold-schema.json"
    with open(contract_path) as f:
        contract = json.load(f)
    fact = contract["tables"]["fact_crime"]
    assert "crime_id" in fact["columns"]
    assert "time_id" in fact["columns"]
    assert "offense_id" in fact["columns"]
    assert "case_id" in fact["columns"]
    assert "location_id" in fact["columns"]
    assert fact["partitioned_by"] == ["year"]
    assert set(fact["foreign_keys"].keys()) == {"time_id", "location_id", "offense_id", "case_id"}
