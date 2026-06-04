"""Unit tests for warehouse layer (M4)."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, create_autospec

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

# Ensure the pipeline source is on sys.path for import
_src = REPO_ROOT / "pipeline" / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from chicago_pipeline.warehouse.load_postgres import (
    FK_DEFS,
    _add_foreign_keys,
    _add_indexes,
    _add_pk,
    _infer_partitions,
    _postgis_add_column,
)


# ---- file-existence tests (structural) ----


def test_warehouse_package_exists():
    init_file = REPO_ROOT / "pipeline" / "src" / "chicago_pipeline" / "warehouse" / "__init__.py"
    assert init_file.exists()


def test_load_postgres_module_exists():
    mod = REPO_ROOT / "pipeline" / "src" / "chicago_pipeline" / "warehouse" / "load_postgres.py"
    assert mod.exists()
    content = mod.read_text()
    assert "load_gold_to_postgres" in content
    assert "_infer_partitions" in content
    assert "_add_foreign_keys" in content
    assert "_add_pk" in content
    assert "FK_DEFS" in content
    assert "_ensure_ddl" not in content  # removed — to_sql handles DDL


def test_initdb_schema_exists():
    sql = REPO_ROOT / "scripts" / "initdb" / "01-schema.sql"
    assert sql.exists()
    content = sql.read_text()
    assert "CREATE EXTENSION IF NOT EXISTS postgis" in content
    assert "CREATE SCHEMA IF NOT EXISTS warehouse" in content


def test_dbt_project_exists():
    yml = REPO_ROOT / "dbt" / "dbt_project.yml"
    assert yml.exists()
    content = yml.read_text()
    assert "name: chicago_crime" in content
    assert "profile: chicago_crime" in content


def test_dbt_profiles_exists():
    yml = REPO_ROOT / "dbt" / "profiles.yml"
    assert yml.exists()
    content = yml.read_text()
    assert "type: postgres" in content


def test_staging_models_exist():
    models = ["stg_fact_crime.sql", "stg_dim_time.sql", "stg_dim_location.sql",
              "stg_dim_offense.sql", "stg_dim_case.sql"]
    for m in models:
        p = REPO_ROOT / "dbt" / "models" / "staging" / m
        assert p.exists(), f"Missing staging model: {m}"


def test_intermediate_models_exist():
    models = ["int_fact_with_geom.sql", "int_time_enriched.sql"]
    for m in models:
        p = REPO_ROOT / "dbt" / "models" / "intermediate" / m
        assert p.exists(), f"Missing intermediate model: {m}"


def test_mart_models_exist():
    models = ["mart_kpi_daily.sql", "mart_arrest_summary.sql",
              "mart_crime_type_trend.sql", "mart_geo_choropleth.sql",
              "mart_temporal_heatmap.sql"]
    for m in models:
        p = REPO_ROOT / "dbt" / "models" / "marts" / m
        assert p.exists(), f"Missing mart model: {m}"


def test_schema_yml_exists():
    yml = REPO_ROOT / "dbt" / "models" / "schema.yml"
    assert yml.exists()
    content = yml.read_text()
    assert "sources:" in content
    assert "models:" in content


def test_dbt_build_dag_exists():
    dag = REPO_ROOT / "airflow" / "dags" / "dbt_build_dag.py"
    assert dag.exists()
    content = dag.read_text()
    assert "dbt_build" in content
    assert "dbt_run" in content
    assert "dbt_test" in content


def test_warehouse_load_dag_exists():
    dag = REPO_ROOT / "airflow" / "dags" / "warehouse_load_dag.py"
    assert dag.exists()
    content = dag.read_text()
    assert "load_postgres" in content
    assert "dbt_run" in content


def test_gold_schema_contract_has_warehouse_refs():
    contract = REPO_ROOT / "contracts" / "gold-schema.json"
    assert contract.exists()
    content = contract.read_text()
    data = json.loads(content)
    assert data["design_decisions"]["geom_wkt"] == "Placeholder column as WKT string; PostGIS cast deferred to load_postgres.py (M4)"
    assert "sin_cos_encoding" in data["design_decisions"]
    assert "M4" in data["design_decisions"]["sin_cos_encoding"]


def test_makefile_has_load_postgres():
    mf = REPO_ROOT / "Makefile"
    content = mf.read_text()
    assert "load-postgres" in content
    assert "pipeline" in content


def test_makefile_targets_spark_master():
    mf = REPO_ROOT / "Makefile"
    content = mf.read_text()
    assert "spark-master" in content
    lines = content.split("\n")
    in_dbt_section = False
    for line in lines:
        if "dbt-" in line or "load-postgres" in line:
            in_dbt_section = True
        if in_dbt_section and line.strip():
            assert "airflow-webserver" not in line, f"Makefile target references airflow-webserver: {line}"
        if in_dbt_section and not line.strip():
            in_dbt_section = False


def test_dags_use_docker_compose_exec():
    for dag_file in ["dbt_build_dag.py", "warehouse_load_dag.py"]:
        path = REPO_ROOT / "airflow" / "dags" / dag_file
        content = path.read_text()
        assert "docker compose exec -T spark-master" in content, f"{dag_file} should use docker compose exec spark-master"
        assert "airflow-webserver" not in content, f"{dag_file} should not reference airflow-webserver"


# ---- behavioral tests for _infer_partitions ----


def test_infer_partitions_basic():
    result = _infer_partitions("gold/chicago_crime/fact_crime/year=2024/part-000.parquet")
    assert result == {"year": "2024"}
    result = _infer_partitions("gold/chicago_crime/silver/year=2024/month=01/part-000.parquet")
    assert result == {"year": "2024", "month": "01"}


def test_infer_partitions_no_partition():
    assert _infer_partitions("gold/chicago_crime/dim_time/part-000.parquet") == {}


def test_infer_partitions_intermediate_dirs_ignored():
    result = _infer_partitions("prefix/table/year=2024/month=01/part-000.parquet")
    assert result == {"year": "2024", "month": "01"}
    # non-parquet file should return empty
    assert _infer_partitions("prefix/table/year=2024/month=01/notes.txt") == {}


def test_infer_partitions_non_parquet_no_partition():
    """Files that don't end in .parquet should not yield partitions."""
    assert _infer_partitions("prefix/table/year=2024/file.csv") == {}


# ---- behavioral tests for _add_pk, _add_foreign_keys, _add_indexes, _postgis ----


def _make_mock_engine():
    """Create a mock SQLAlchemy engine for testing DDL functions."""
    engine = MagicMock()
    conn = MagicMock()
    engine.begin.return_value = conn
    conn.__enter__.return_value = conn
    return engine


def test_add_pk_adds_constraint():
    engine = _make_mock_engine()
    conn = engine.begin.return_value.__enter__.return_value
    conn.execute.return_value.fetchone.return_value = None  # PK does not exist

    _add_pk(engine, "dim_time")

    # Should check for PK existence then add it
    calls = [c[0][0] for c in conn.execute.call_args_list]
    pk_check = [c for c in calls if "pg_constraint" in str(c)]
    pk_add = [c for c in calls if "ADD PRIMARY KEY" in str(c)]
    assert len(pk_check) >= 1, "Should check pg_constraint for existing PK"
    assert len(pk_add) >= 1, "Should execute ALTER TABLE ADD PRIMARY KEY"
    assert "dim_time" in str(pk_add[0])
    assert "time_id" in str(pk_add[0])


def test_add_pk_skips_if_exists():
    engine = _make_mock_engine()
    conn = engine.begin.return_value.__enter__.return_value
    conn.execute.return_value.fetchone.return_value = (1,)  # PK already exists

    _add_pk(engine, "dim_location")

    calls = [str(c[0][0]) for c in conn.execute.call_args_list]
    pk_add = [c for c in calls if "ADD PRIMARY KEY" in c]
    assert len(pk_add) == 0, "Should skip PK creation when PK already exists"


def test_add_foreign_keys_all_fks():
    engine = _make_mock_engine()

    _add_foreign_keys(engine, "fact_crime")

    conn = engine.begin.return_value.__enter__.return_value
    calls = [str(c[0][0]) for c in conn.execute.call_args_list]
    assert any("fk_time" in c for c in calls)
    assert any("fk_location" in c for c in calls)
    assert any("fk_offense" in c for c in calls)
    assert any("fk_case" in c for c in calls)


def test_add_indexes_executes_sql():
    engine = _make_mock_engine()

    _add_indexes(engine)

    conn = engine.begin.return_value.__enter__.return_value
    calls = [str(c[0][0]) for c in conn.execute.call_args_list]
    assert any("idx_fact_time_id" in c for c in calls)
    assert any("idx_fact_location_id" in c for c in calls)
    assert any("idx_fact_offense_id" in c for c in calls)
    assert any("idx_fact_case_id" in c for c in calls)
    assert any("idx_dim_location_geometry" in c for c in calls)


def test_add_indexes_includes_gist():
    engine = _make_mock_engine()

    _add_indexes(engine)

    conn = engine.begin.return_value.__enter__.return_value
    calls = [str(c[0][0]) for c in conn.execute.call_args_list]
    gist = [c for c in calls if "USING GIST" in c]
    assert len(gist) == 1
    assert "geometry" in gist[0]


def test_postgis_add_column_executes():
    engine = _make_mock_engine()

    _postgis_add_column(engine)

    conn = engine.begin.return_value.__enter__.return_value
    calls = [str(c[0][0]) for c in conn.execute.call_args_list]
    alter = [c for c in calls if "ADD COLUMN" in c and "geometry" in c]
    update = [c for c in calls if "UPDATE" in c and "ST_GeomFromText" in c]
    assert len(alter) >= 1, "Should ALTER TABLE ADD COLUMN geometry"
    assert len(update) >= 1, "Should UPDATE dim_location SET geometry"


def test_fk_defs_well_formed():
    """Verify FK_DEFS structure covers all expected keys."""
    assert "fact_crime" in FK_DEFS
    assert len(FK_DEFS["fact_crime"]) == 4
    for fk in FK_DEFS["fact_crime"]:
        assert "FOREIGN KEY" in fk
        assert "REFERENCES warehouse.dim_" in fk


def test_fk_defs_tables_exist():
    """Verify each FK_DEFS key has a corresponding table in SCHEMA_MAP."""
    from chicago_pipeline.warehouse.load_postgres import SCHEMA_MAP
    for table_name in FK_DEFS:
        assert table_name in SCHEMA_MAP, f"FK_DEFS references {table_name} but missing from SCHEMA_MAP"


# ---- behavioral tests for SCHEMA_MAP ----


def test_schema_map_has_all_tables():
    from chicago_pipeline.warehouse.load_postgres import SCHEMA_MAP, GOLD_TABLES
    for table in GOLD_TABLES:
        assert table in SCHEMA_MAP, f"Missing SCHEMA_MAP entry for {table}"


def test_schema_map_column_types():
    from chicago_pipeline.warehouse.load_postgres import SCHEMA_MAP
    assert SCHEMA_MAP["fact_crime"]["crime_id"] == "BIGINT"
    assert SCHEMA_MAP["dim_time"]["time_id"] == "BIGINT"
    assert SCHEMA_MAP["dim_location"]["location_id"] == "BIGINT"
    assert SCHEMA_MAP["dim_offense"]["offense_id"] == "BIGINT"
    assert SCHEMA_MAP["dim_case"]["case_id"] == "BIGINT"


# ---- behavioral test for _read_gold_parquet error path ----


def test_read_gold_parquet_empty_bucket_raises():
    """Verify that _read_gold_parquet raises FileNotFoundError for non-existent buckets."""
    from chicago_pipeline.warehouse.load_postgres import _read_gold_parquet

    s3_client = MagicMock()
    s3_client.list_objects_v2.return_value = {}

    with pytest.raises(FileNotFoundError, match="No objects found"):
        _read_gold_parquet(s3_client, "my-bucket", "prefix", "dim_time")
