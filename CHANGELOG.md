# Changelog

All notable changes to this project will be documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased] — 2026-06-04

### Added (M0)
- Full repository skeleton (Makefile, docker-compose.yaml, CODEOWNERS, .editorconfig, .pre-commit-config.yaml, .gitignore).
- Multi-agent charter: root `AGENTS.md` + 8 agent sub-folders (`agents/{architect,data-engineer,backend,frontend,qa,sre,docs,security}/`).
- Contracts bus: `openapi.yaml`, `dbt-manifest.json` (placeholder), `api-types.ts`, `event-catalog.md`, `design-tokens.json`, `CHANGELOG.md`.
- Docker Compose stack (12 services): MinIO, PostGIS, Redis, Spark master/worker, Airflow webserver/scheduler, FastAPI, React, Prometheus, Grafana, Marquez.
- ADRs 0001–0004 (MinIO, Spark+dbt, FastAPI+React, no-auth).
- 7 DAGs: ingest, bronze_to_silver, silver_to_gold, gold_to_warehouse, dbt_build, data_quality, pipeline_healthcheck.
- `scripts/`: healthcheck, urls, validate_contracts, validate_agents, seed (90-day synthetic data).
- Implementation plan: `docs/IMPLEMENTATION_PLAN.md`.
- SECURITY.md, LICENSE, README.md.

### Fixed (M0 precision pass)
- `data/README.md`: corrected date range from "2024-01-01 to 2024-04-01" to "2024-01-01 to 2024-03-31 (90 days)".
- `docs/architecture.md`: added agent ownership table (was empty, but referenced by root AGENTS.md).
- `agents/sre/AGENTS.md`: moved `lineage/` from "Owns" to "Consumes" (Data Engineer owns it).
- `agents/backend/AGENTS.md`: replaced non-existent `scripts/check_openapi.py` with `make contracts-validate`.
- `agents/backend/CONTRACTS.md`: removed incorrect "OpenAI keys" reference from `.env` row.
- `agents/frontend/CONTRACTS.md`: removed incorrect OpenLineage row (Frontend does not consume event-catalog.md).
- `agents/docs/CONTRACTS.md`: added missing `docs/adr/000X-*.md` (drafts) entry.
- `agents/architect/AGENTS.md`: clarified docs/adr/ ownership (sign-off authority, not sole ownership).
- `agents/qa/AGENTS.md`: clarified that QA owns root `tests/` and CI, not every agent's internal `tests/` directories.
- Root `AGENTS.md`: clarified ADR workflow (Docs drafts, Architect signs off).

### Added (milestone evaluation protocol)
- Root `AGENTS.md`: added §Milestone evaluation protocol with four-phase cycle (implement → evaluate → user test → improvements) and gate rule.
- `docs/IMPLEMENTATION_PLAN.md`: updated §V with per-milestone cycle and gate rule.
- `agents/architect/AGENTS.md`: added milestone gate to quality gates.
- `agents/qa/AGENTS.md`: added milestone gate to quality gates.
- `agents/sre/AGENTS.md`: added milestone gate to quality gates.

### Added (M0 closure)
- Created `docs/data-model.md` stub (star schema summary + dbt marts reference).
- Created `.github/dependabot.yml` (weekly grouped updates for Python, Node, Docker, GitHub Actions).
- Created `docs/milestones/M0-test.md` (11-step user test instructions for M0).
- Created `docs/milestones/M0-improvements.md` (7 items, 4 done, 2 TODO, 1 noted).

### Added (M1 — Ingestion → Bronze)
- Created `pipeline/` infrastructure: `pyproject.toml`, `requirements.txt`, `conf/{base,local}.yaml`.
- Created `pipeline/src/chicago_pipeline/` package with `common/` subpackage (logger, s3, spark_session, db, settings).
- Created `pipeline/src/chicago_pipeline/ingest/download_kaggle.py` — downloads source CSV (Kaggle or synthetic fallback), verifies integrity.
- Created `pipeline/src/chicago_pipeline/bronze/to_bronze.py` — PySpark job that reads CSV, adds `_ingest_ts` metadata, writes Parquet to MinIO partitioned by `ingest_date`.
- Created `airflow/Dockerfile` (extends apache/airflow:2.9.3 with spark provider and extras).
- Created `airflow/requirements.txt` (spark provider, s3 provider, kagglehub, boto3).
- Created `airflow/dags/ingest_dag.py` — TaskFlow DAG with 3 tasks: `kaggle_download` → `verify_checksum` → `upload_bronze` (SparkSubmitOperator).
- Created `pipeline/tests/test_ingest.py` — 4 unit tests (synthetic generation, reproducibility, CSV verify).
- Fixed Makefile: `spark-*` targets use correct service name `spark-master`, added `--py-files` for PYTHONPATH.

### Added (M1 closure)
- Created `docs/milestones/M1-test.md` (8-step user test instructions for M1).
- Created `docs/milestones/M1-improvements.md` (7 improvement items).

### Added (M1 interactive tools)
- Created `scripts/explore/bronze_explorer.py` — automated Bronze layer report (schema, date range, crime types, arrest stats, time patterns).
- Created `scripts/explore/bronze_query.py` — interactive REPL for querying Bronze data (head, count, filter, schema, summary).

### Fixed (repo cleanup)
- `.gitignore`: added `data/*.csv`, `pipeline/src/*.egg-info/`, `pipeline/build/` for generated artifacts.
- `.gitignore`: added `AGENTS.md`, `agents/`, `scripts/validate_agents.sh`, `CODEOWNERS` to ignore agent scaffolding locally.
- `.gitignore`: added `docs/`, `*.md`, `lineage/` to ignore documentation and agent-authored files locally.
- `.gitignore`: added `references/` to ignore reference repos locally.
- `.gitignore`: added `.github/dependabot.yml` to ignore agent-authored GitHub config.
- `scripts/explore/bronze_explorer.py`: fixed path resolution for new location (`parents[2]` instead of `parents[1]`).
- `scripts/explore/bronze_query.py`: fixed path resolution for new location.
- Cleaned `data/` directory — removed leftover temp CSVs.

### Changed (repo fresh start)
- Removed old git history and created fresh initial commit (40 files, no agent scaffolding).
- All agent files (`agents/`, `AGENTS.md`, `CODEOWNERS`, `scripts/validate_agents.sh`) preserved locally but ignored by git.
- All documentation (`docs/`, `*.md`, `lineage/`) preserved locally but ignored by git.
- All reference repos (`references/`) preserved locally but ignored by git.

### Added (M2 — Bronze → Silver)
- Created `pipeline/src/chicago_pipeline/silver/__init__.py` and `to_silver.py` — PySpark job that reads Bronze, applies schema enforcement, type casting (date, arrest/domestic to bool), Chicago bbox filtering, date range filtering, deduplication, and writes Parquet to Silver partitioned by `year/month`.
- Created `great_expectations/great_expectations.yml` — GE config with SparkDFExecutionEngine for S3/MinIO.
- Created `great_expectations/suites/chicago_crime_bronze.json` — 8 expectations (id not null/unique, date format, primary_type not null, lat/lon bbox, row count).
- Created `great_expectations/suites/chicago_crime_silver.json` — 12 expectations (id not null/unique, date type, arrest/domestic bool types, lat/lon bbox, district set, case_number regex, row count).
- Created `great_expectations/checkpoints/bronze_checkpoint.yml` and `silver_checkpoint.yml` — checkpoint configs.
- Created `great_expectations/run_validation.py` — standalone GE validation runner with report output.
- Created `airflow/dags/bronze_to_silver_dag.py` — TaskFlow DAG with 3 tasks: `ge_checkpoint_bronze` → `spark_silver` → `ge_checkpoint_silver`.
- Created `pipeline/tests/test_silver.py` — 10 unit tests (module import, column definitions, GE suite loading, config validation).
- Updated `pipeline/conf/base.yaml` — added `silver` config (prefix, partition, dedup columns, Chicago bbox, date range).
- Updated `pipeline/src/chicago_pipeline/common/settings.py` — added `silver` property.
- Updated `Makefile` — added `ge-check`, `ge-bronze`, `ge-silver` targets.
- Created `docs/milestones/M2-test.md` (8-step user test instructions for M2).
- Created `docs/milestones/M2-improvements.md` (7 improvement items).

### Fixed (M2 integration)
- `pipeline/src/chicago_pipeline/common/settings.py`, `s3.py`, `db.py`, `logger.py`, `bronze/to_bronze.py`, `silver/to_silver.py`: added `from __future__ import annotations` for Python 3.8 compatibility on `apache/spark:3.5.1`.
- `docker-compose.yaml`: switched Spark image from `bitnami/spark:3.5` (deprecated tag) to `apache/spark:3.5.1` with explicit command-based entrypoints; added `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` env vars to spark-master and spark-worker services.
- `pipeline/conf/local.yaml`: fixed S3 endpoint from `http://localhost:9000` to `http://minio:9000` for inter-container communication.
- `great_expectations/run_validation.py`: rewrote as standalone PySpark validator (GE 1.1.0 removed `FileDataContext.run_checkpoint()` and `fluent_datasources` API is incompatible).
- `great_expectations/suites/chicago_crime_bronze.json`: updated date regex to accept both `MM/dd/yyyy hh:mm:ss AM/PM` and ISO `yyyy-MM-dd'T'HH:mm:ss` formats.
- `Makefile`: `spark-bronze` target now passes `/tmp/chicago_synthetic.csv` explicitly instead of the default `/tmp/chicago_crime/source.csv`.
- `pipeline/tests/test_silver.py`: `test_ge_validation_script_exists` now checks for `SparkSession` instead of removed `RuntimeBatchRequest`.
- `CHANGELOG.md`: added this entry.
- Great Expectations JARs: Hadoop AWS JARs version-matched to Spark 3.5.1 (`hadoop-aws-3.3.4.jar` + `aws-java-sdk-bundle-1.12.262.jar`) to avoid `NoClassDefFoundError`.

### Changed (M2 test)
- `docs/milestones/M2-test.md`: updated with current commands (`mingw32-make`), corrected credentials (`change_me_local`), known issues table, and cleanup instructions.
- `.gitignore`: added `great_expectations/reports/` (generated at runtime).

### Added (M2 Extension — Medallion-aligned conforming features)
- Created `docs/milestones/M2-extension-proposal.md` — Medallion Architecture-aligned proposal for 11 conforming features in Silver (6 boolean flags, 3 date decomposition, `updated_on_ts`, `hours_to_update`).
- Updated `pipeline/src/chicago_pipeline/silver/to_silver.py` — added 5 new stage functions (`_standardize_text`, `_add_updated_on_ts`, `_add_date_components`, `_add_conforming_booleans`, `_add_hours_to_update`), 11 new columns in `SILVER_COLUMNS` (29 total), `TEXT_COLS` list, `TimestampType` import.
- Updated `pipeline/tests/test_silver.py` — added 4 new tests (`test_extension_columns_dtypes`, `test_extension_functions_exist`, `test_text_cols_defined`, `test_silver_suite_count`), total 16 tests.
- Updated `great_expectations/suites/chicago_crime_silver.json` — added 6 `not_null` expectations for boolean flags (18 total).
- Updated `scripts/spike/m2_silver_eda.py` — 100% full dataset inspection (default `fraction=1.0`).
- Created `scripts/spike/verify_m2_extension.py` — verification script for Silver output columns.
- Created `scripts/spike/check_districts.py` — investigates which districts fail GE set validation.

### Added (M2 Extension Enhancement Catalogue)
- Created `docs/milestones/M2-extension-enhancements.md` — 10-item enhancement catalogue (E1–E10).
- **E1 (P1):** Fixed case_number regex in Silver GE suite: `^[A-Z]\d{6,}$` → `^[A-Z]{2}\d{6}$` (matches 2-letter prefix).
- **E2 (P1):** Implemented `expect_column_values_to_be_of_type` handler in `run_validation.py` (was silently SKIPPED).
- **E3 (P1):** Implemented `expect_column_values_to_be_in_set` handler in `run_validation.py` (was silently SKIPPED); updated district set to 25 values (1–25) including 13, 21, 23.
- **E4 (P2):** Added Bronze partition pruning in `to_silver.py` — reads only latest `ingest_date` partition; `dropped=0` (was 57,931).
- **E5 (P2):** Added explicit `F.col("date").cast("timestamp")` for `hours_to_update` edge case.
- **E6 (P3):** Added `_write_report_s3a()` to `run_validation.py` — writes GE reports to `s3a://lake/reports/ge/{suite}/{date}/{ts}_report.json` with local fallback.
- **E7 (P3):** Added `version: 2` to both Bronze and Silver GE suite JSON files.
- **E8 (P3):** Added `_check_schema_evolution()` to `run_validation.py` — checks for missing/extra columns in Silver output.
- **E9 (P3):** Confirmed `is_domestic_arrest` keep as-is (no code change needed).
- **E10 (P3):** Added case_number regex expectation `^[A-Z]{2}\d{6}$` to Bronze GE suite.

### Fixed (M2 Extension integration)
- `great_expectations/run_validation.py`: rewrote validation logic to handle `be_of_type`, `be_in_set` handlers; added S3A report writer with local fallback.
- `pipeline/tests/test_silver.py`: updated `test_silver_suite_count` to expect 18 expectations (was 12).
- `docs/milestones/M2-test.md`: updated Bronze expectations count from 8 to 9, unit tests from 14 to 16.

### Added (M2 real-time district proposal)
- Created `docs/milestones/M2-realtime-district-proposal.md` — 3 solutions for real-time district feature updates (scheduled polling + drift detection, dynamic set validation, event-driven).

### Added (M2 district drift — Phase 1–4)
- **Phase 1 (Config-driven):** Added `validation.districts.allowed` to `pipeline/conf/base.yaml`; `validation` property to `settings.py`; `_apply_config_overrides()` in `run_validation.py` to override `value_set` from config.
- **Phase 2 (Drift detection):** Created `pipeline/src/chicago_pipeline/common/drift.py` — `_detect_district_drift()` function that compares actual district values against allowed set; `run_drift_detection()` orchestrator; `_write_drift_report()` for S3A reports.
- **Phase 3 (Airflow DAG):** Created `great_expectations/run_drift_detection.py` — standalone spark-submit entrypoint. Updated `airflow/dags/bronze_to_silver_dag.py` — replaced broken `FileDataContext` tasks with `SparkSubmitOperator`; added `detect_district_drift` task chained after validation.
- **Phase 4 (Alerting + auto-remediation):** Added `_send_slack_alert()` and `_auto_remediate_districts()` to `common/drift.py` — Slack webhook notification and optional config auto-update.
- Updated `docs/milestones/M2-realtime-district-proposal.md` status to **IMPLEMENTED**.
- Updated `docs/milestones/M2-improvements.md` — added district drift detection to completed items.

### Fixed (M2 consistency — post-verification)
- Removed `expect_column_values_to_be_unique` on `id` from Bronze GE suite: duplicate partitions (same ingest date) are expected in raw Bronze; uniqueness is guaranteed at Silver after dedup.
- Updated `docs/milestones/M2-test.md` — corrected Bronze expectations count from 9 to 8.

### Added (M3 — Silver → Gold star schema)
- Created `pipeline/src/chicago_pipeline/gold/__init__.py` and `to_gold.py` — PySpark job that reads Silver, builds star schema: `fact_crime` (57,931 rows, 19 cols, partitioned by year), `dim_time` (26,304 rows, 9 cols, hourly 2024-01-01 to 2026-12-31), `dim_location` (57,931 rows, 11 cols with `is_downtown`, `distance_to_downtown_km`, `geom_wkt`), `dim_offense` (900 rows, 5 cols), `dim_case` (57,931 rows, 3 cols).
- Surrogate keys via `F.xxhash64()` (deterministic, idempotent). Fixed hash collision: removed `.cast(IntegerType())` from all 5 surrogate key expressions (32-bit truncation caused 4 duplicate `crime_id`s out of 57,931).
- `_build_dim_time`: pre-generates hourly calendar for full project range; joined to fact at daily grain (`hour=0`).
- `_build_dim_location`: Haversine distance to downtown (`DOWNTOWN_LAT=41.8819, DOWNTOWN_LON=-87.6278`), downtown bbox check, `geom_wkt` placeholder for M4 PostGIS.
- `_build_dim_offense`: distinct IUCR codes with crime type lookup.
- `_build_dim_case`: case metadata (case_number, updated_on).
- `fact_crime`: includes `_gold_ingest_ts` timestamp, `year` partition column, 6 boolean flags, `hours_to_update`, `date_dow`.
- Updated `pipeline/conf/base.yaml` — added `gold:` section (prefix, date_range, downtown_bbox).
- Updated `pipeline/src/chicago_pipeline/common/settings.py` — added `gold` property.
- Updated `pipeline/src/chicago_pipeline/common/drift.py` — `_detect_district_drift` now checks `"district" in df.columns` before querying (SKIPPED for Gold datasets without district column).

### Added (M3 Gold GE validation)
- Created `great_expectations/suites/chicago_crime_gold.json` — 12 expectations: `crime_id` not null + unique, 4 FK columns not null, row count > 1000. All 12/12 PASS.
- Updated `great_expectations/run_validation.py` — added Gold schema evolution check (19 expected columns).
- Updated `Makefile` — added `ge-gold` target; updated `ge-check` to include Gold validation.

### Added (M3 Airflow DAG)
- Created `airflow/dags/silver_to_gold_dag.py` — 3-task DAG: `ge_checkpoint_silver` → `spark_silver_to_gold` (SparkSubmitOperator) → `ge_checkpoint_gold`.

### Added (M3 Gold schema contract)
- Created `contracts/gold-schema.json` — v1.0.0 defining 5 tables (fact + 4 dims), column names/types/descriptions, FK relationships. Surrogate keys: `long` (was `integer`, fixed from collision bug).

### Added (M3 tests)
- Created `pipeline/tests/test_gold.py` — 14 unit tests (module import, functions, config, GE suite, DAG, contract, schema).

### Added (M3 interactive test scripts)
- Created `scripts/explore/gold_explorer.py` — 10-section one-shot explorer (table overview, schema, sample, dim_time, dim_offense, dim_location, dim_case, cross-layer consistency, statistics, concept).
- Created `scripts/explore/gold_query.py` — interactive REPL with 11 commands (tables, schema, head, count, filter, agg, join, search, qotd, help, quit).
- Created `scripts/spike/verify_m3_gold.py` — 48 automated checks: table existence, row counts, schema, PK uniqueness, PK not-null, FK integrity, dim_offense completeness, dim_time coverage, dim_location geography, year partition, pipeline observability, dim_case metadata. **48/48 PASS.**
- Created `scripts/test_gold_query_batch.py` — batch runner executing 38 sequential commands through gold_query.py functions. **38/38 PASS.**

### Added (M3 results)
- Created `reports/m3_results.txt` — full output of gold_explorer (10 sections), verify_m3_gold (48 checks), and batch query test (38 commands).

### Added (M3 closure)
- Created `docs/milestones/M3-test.md` — 8-step user test instructions for M3.
- Created `docs/milestones/M3-improvements.md` — 11 proposed enhancements (dim_time hourly join, dim_location dedup, SCD, sin/cos in dbt, GE coverage expansion, etc.).

### Added (M4 agent prep — revised plan)
- Updated `agents/data-engineer/AGENTS.md` — added M4 warehouse ownership: `load_postgres.py`, dbt project (staging/intermediate/marts), `dbt_build_dag.py`, PostGIS geometry cast, initdb schema.
- Updated `agents/data-engineer/CONTRACTS.md` — added M4 outputs: `initdb/01-schema.sql`, `load_postgres.py`, dbt staging/intermediate/mart models, `dbt_build_dag.py`.
- Updated `agents/backend/AGENTS.md` — added M4 inputs: 5 mart tables (`mart_kpi_daily`, `mart_arrest_summary`, `mart_crime_type_trend`, `mart_geo_choropleth`, `mart_temporal_heatmap`); M4 prerequisite gate.
- Updated `agents/backend/CONTRACTS.md` — added M4 consume rows for all 5 dbt marts with API endpoint mapping.
- Updated `agents/qa/AGENTS.md` — added M4 quality gates: `load-postgres` row count check, `dbt-run`/`dbt-test` model materialization, PostGIS `ST_SRID` verification, 5 mart row count > 0.

### Fixed (M4 QoL — Bronze schema)
- `pipeline/src/chicago_pipeline/bronze/to_bronze.py`: drops `ingest_date` from DataFrame before `partitionBy` write. Column only exists in directory structure, not in data files. Eliminates `COLUMN_ALREADY_EXISTS` WARN in Silver reader.

### Added (M4 QoL — Silver partition selection)
- `pipeline/src/chicago_pipeline/silver/to_silver.py`: added `--ingest-date` CLI arg for per-partition processing. Allows targeting a specific Bronze partition instead of auto-detecting latest.

### Fixed (M4 QoL — Makefile)
- Removed duplicate `seed` target (was defined at both line 55 and line 191; second overrode first).
- `dbt-run` now depends on `dbt-deps` — `make dbt-run` always works from fresh state without manual `dbt deps` step.

### Added (M4 QoL — Docker image)
- Created `docker/spark/Dockerfile` — custom Spark image with Hadoop AWS JARs (`hadoop-aws-3.3.4.jar`, `aws-java-sdk-bundle-1.12.262.jar`) and all Python dependencies baked in (boto3, pyarrow, dbt-core 1.8.7, dbt-postgres 1.8.2, pyspark 3.5.3, pytest, pytest-mock).
- `docker-compose.yaml`: spark services now use `build: ./docker/spark` with `ccp-spark:3.5.1` image tag.
- `docker-compose.yaml`: spark-master volumes expanded — added `contracts/`, `scripts/`, `airflow/dags/`, `Makefile` as `:ro` mounts.
- `docker-compose.yaml`: spark-worker volumes expanded — added `./dbt:/opt/dbt` and `./data:/data`.

### Added (M4 QoL — PowerShell pipeline)
- Created `scripts/pipeline.ps1` — PowerShell equivalents for all Makefile targets (seed, spark-bronze, spark-silver, spark-gold, load-postgres, dbt-run, dbt-test, pipeline).

### Added (M4 QoL — cross-platform seed)
- Created `scripts/seed.py` — Python seed script (deterministic, `random.seed(42)`, 57,931 rows, 90 days of synthetic Chicago crime data). Works on Windows without bash.

### Fixed (M4 QoL — Python 3.8 compatibility)
- `pipeline/src/chicago_pipeline/ingest/download_kaggle.py`: added `from __future__ import annotations` for `str | Path` union syntax on Python 3.8.
- `pipeline/tests/test_ingest.py`: rewrote `test_generate_synthetic_reproducible` to use flat `with tmp1, tmp2:` (parenthesized context managers require Python 3.10+).

### Changed (M4 QoL — script paths)
- `scripts/explore/gold_explorer.py`, `gold_query.py`, `scripts/spike/verify_m3_gold.py`, `scripts/test_gold_query_batch.py`: updated docstrings from `/opt/pipeline/scripts/` to `/opt/scripts/` to match docker-compose volume mounts.
- Removed duplicate `pipeline/scripts/` directory (was byte-identical copy of `scripts/explore/` and `scripts/spike/`).
- `.gitignore`: added `pipeline/scripts/` to prevent re-creation of duplicates.

### Verified (M4 QoL — end-to-end pipeline)
- Clean-slate pipeline run M1→M4 on 2026-06-05: Bronze 57,931 → Silver 57,931 → Gold 5 tables → Postgres 5 tables → dbt 12/12 models + 53/53 tests.
- Unit tests: 63/63 PASS.
- GE Bronze: 8/8 PASS (57,931 rows, 19 cols — clean schema).
- GE Silver: 18/18 PASS (57,931 rows, 32 cols, zero COLUMN_ALREADY_EXISTS WARN).
- Postgres: 5 base tables + 5 dbt marts, 4 PKs + 4 FKs + 1 GiST index + 4 B-tree indexes, PostGIS SRID 4326.
