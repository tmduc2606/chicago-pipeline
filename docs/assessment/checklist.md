# Assessment Checklists — Per-Milestone Code Inspection

**Purpose:** Reference checklists for manual and automated code inspection during assessment.
**Usage:** Check each item `[x]` pass or `[ ]` fail, note evidence. Severity and verification method included.
**Framework:** `docs/assessment/protocol.md` v2.0

---

## Severity Legend

| Symbol | Severity | Block Status |
|--------|----------|-------------|
| 🔴 | S1 (Critical) | **HARD BLOCK** — assessment fails if any S1 is open |
| 🟠 | S2 (High) | Architect override required |
| 🟡 | S3 (Medium) | Tracked in overhaul |
| 🟢 | S4 (Low) | Informational |

## Verification Methods

| Method | Description | Automated? |
|--------|-------------|-----------|
| `file-exists` | File exists and is non-empty | Yes |
| `command` | Run specific command, check exit code | Yes |
| `grep` | Search for pattern in codebase | Yes |
| `manual` | Human inspection required | No |
| `test` | Run specific test suite | Yes |
| `contract` | Validate against contract file | Yes |

---

## M0 — Skeleton & Docs (18 items)

| # | Check | Severity | Verification | Cross-Reference | Evidence |
|---|-------|----------|-------------|-----------------|----------|
| M0-01 | Repo structure has all 15 top-level directories | 🟠 S2 | `file-exists` | `docs/architecture.md` §3 | `evidence/code-inspections/M0-inspection.md` |
| M0-02 | `.editorconfig` exists and is non-empty | 🟢 S4 | `file-exists` | — | `evidence/code-inspections/M0-inspection.md` |
| M0-03 | `.gitignore` covers Python, Node, Docker, DBT, GE, Spark, Airflow | 🟡 S3 | `grep` | — | `evidence/code-inspections/M0-inspection.md` |
| M0-04 | `README.md` exists with project description + quick start | 🟡 S3 | `file-exists` | `docs/IMPLEMENTATION_PLAN.md` | `evidence/code-inspections/M0-inspection.md` |
| M0-05 | `CHANGELOG.md` exists and is non-empty | 🟡 S3 | `file-exists` | — | `evidence/code-inspections/M0-inspection.md` |
| M0-06 | `LICENSE` exists and is non-empty | 🟡 S3 | `file-exists` | — | `evidence/code-inspections/M0-inspection.md` |
| M0-07 | `Makefile` has 20+ targets (pipeline, api, web, contracts, agents) | 🟠 S2 | `grep` | `Makefile` | `evidence/gates/results.md` |
| M0-08 | `docker-compose.yaml` passes `docker compose config` | 🔴 S1 | `command` | — | `evidence/gates/results.md` |
| M0-09 | `docker-compose.yaml` has correct volume mounts | 🟠 S2 | `manual` | — | `evidence/code-inspections/M0-inspection.md` |
| M0-10 | `docs/adr/` has 4 ADR files (0001–0004) | 🟡 S3 | `file-exists` | `docs/architecture.md` §Key decisions | `evidence/code-inspections/M0-inspection.md` |
| M0-11 | `docs/architecture.md` has agent ownership table | 🟡 S3 | `grep` | `docs/architecture.md` | `evidence/code-inspections/M0-inspection.md` |
| M0-12 | `docs/IMPLEMENTATION_PLAN.md` has milestone table | 🟡 S3 | `grep` | `docs/IMPLEMENTATION_PLAN.md` §8 | `evidence/code-inspections/M0-inspection.md` |
| M0-13 | `docs/implementation_mistakes.md` is non-empty | 🟠 S2 | `file-exists` | — | `evidence/code-inspections/M0-inspection.md` |
| M0-14 | `make agents-lint` passes (24 agent files present) | 🟠 S2 | `command` | `agents/` directory | `evidence/gates/results.md` |
| M0-15 | `make contracts-validate` passes (7 contract files valid) | 🔴 S1 | `command` | `contracts/` directory | `evidence/gates/results.md` |
| M0-16 | `.env.example` has all required environment variables | 🟡 S3 | `grep` | — | `evidence/code-inspections/M0-inspection.md` |
| M0-17 | `.pre-commit-config.yaml` has gitleaks hook | 🟠 S2 | `grep` | — | `evidence/code-inspections/M0-inspection.md` |
| M0-18 | `CODEOWNERS` exists and is non-empty | 🟡 S3 | `file-exists` | — | `evidence/code-inspections/M0-inspection.md` |

---

## M1 — Ingestion → Bronze (16 items)

| # | Check | Severity | Verification | Cross-Reference | Evidence |
|---|-------|----------|-------------|-----------------|----------|
| M1-01 | `pipeline/src/` has `__init__.py` in every package | 🟠 S2 | `file-exists` | — | `evidence/code-inspections/M1-inspection.md` |
| M1-02 | `to_bronze.py` has `main()` entrypoint | 🟠 S2 | `grep` | — | `evidence/code-inspections/M1-inspection.md` |
| M1-03 | `download_kaggle.py` has download + checksum logic | 🟠 S2 | `grep` | — | `evidence/code-inspections/M1-inspection.md` |
| M1-04 | `common/settings.py` uses pydantic BaseSettings | 🟡 S3 | `grep` | — | `evidence/code-inspections/M1-inspection.md` |
| M1-05 | `common/s3.py` has `get_s3_client()` with configurable endpoint | 🟡 S3 | `grep` | — | `evidence/code-inspections/M1-inspection.md` |
| M1-06 | `common/spark_session.py` has `get_spark()` with app name | 🟡 S3 | `grep` | — | `evidence/code-inspections/M1-inspection.md` |
| M1-07 | `conf/base.yaml` has bronze config section | 🟡 S3 | `grep` | — | `evidence/code-inspections/M1-inspection.md` |
| M1-08 | `ingest_dag.py` has DAG definition, retries, SLA, docstring | 🟠 S2 | `grep` | — | `evidence/code-inspections/M1-inspection.md` |
| M1-09 | `bronze_to_silver_dag.py` has DAG definition | 🟠 S2 | `grep` | — | `evidence/code-inspections/M1-inspection.md` |
| M1-10 | Pipeline tests: 4/4 pass (`test_ingest.py`) | 🔴 S1 | `test` | `pipeline/tests/` | `evidence/gates/results.md` |
| M1-11 | Bronze GE suite has 8 expectations | 🟠 S2 | `file-exists` | `great_expectations/` | `evidence/code-inspections/M1-inspection.md` |
| M1-12 | `bronze_checkpoint.yml` is valid YAML | 🟠 S2 | `command` | — | `evidence/code-inspections/M1-inspection.md` |
| M1-13 | `scripts/seed.py` generates synthetic CSV | 🟡 S3 | `command` | — | `evidence/code-inspections/M1-inspection.md` |
| M1-14 | `scripts/healthcheck.sh` checks Docker health | 🟡 S3 | `file-exists` | — | `evidence/code-inspections/M1-inspection.md` |
| M1-15 | `make spark-bronze` executes successfully | 🔴 S1 | `command` | — | `evidence/gates/results.md` |
| M1-16 | Bronze row count >= 1000 (GE validation) | 🔴 S1 | `command` | GE suite | `evidence/gates/results.md` |

---

## M2 — Bronze → Silver (12 items)

| # | Check | Severity | Verification | Cross-Reference | Evidence |
|---|-------|----------|-------------|-----------------|----------|
| M2-01 | `to_silver.py` has transform functions | 🟠 S2 | `grep` | — | `evidence/code-inspections/M2-inspection.md` |
| M2-02 | `common/drift.py` has `detect_district_drift()` | 🟡 S3 | `grep` | — | `evidence/code-inspections/M2-inspection.md` |
| M2-03 | Silver GE suite has 18 expectations | 🟠 S2 | `file-exists` | `great_expectations/` | `evidence/code-inspections/M2-inspection.md` |
| M2-04 | `silver_checkpoint.yml` is valid YAML | 🟠 S2 | `command` | — | `evidence/code-inspections/M2-inspection.md` |
| M2-05 | `run_validation.py` accepts CLI args | 🟡 S3 | `grep` | — | `evidence/code-inspections/M2-inspection.md` |
| M2-06 | `run_drift_detection.py` has drift detection logic | 🟡 S3 | `grep` | — | `evidence/code-inspections/M2-inspection.md` |
| M2-07 | `to_silver.py` defines 11 extension columns | 🟠 S2 | `grep` | — | `evidence/code-inspections/M2-inspection.md` |
| M2-08 | `to_silver.py` has `conform_*` functions for each column | 🟠 S2 | `grep` | — | `evidence/code-inspections/M2-inspection.md` |
| M2-09 | Pipeline tests: 17/17 pass (`test_silver.py`) | 🔴 S1 | `test` | `pipeline/tests/` | `evidence/gates/results.md` |
| M2-10 | `make spark-silver` executes successfully | 🔴 S1 | `command` | — | `evidence/gates/results.md` |
| M2-11 | Silver row count >= 1000 (GE validation) | 🔴 S1 | `command` | GE suite | `evidence/gates/results.md` |
| M2-12 | `to_silver.py` has deduplication logic (idempotency) | 🟠 S2 | `grep` | — | `evidence/code-inspections/M2-inspection.md` |

---

## M3 — Silver → Gold (12 items)

| # | Check | Severity | Verification | Cross-Reference | Evidence |
|---|-------|----------|-------------|-----------------|----------|
| M3-01 | `to_gold.py` has star schema logic | 🟠 S2 | `grep` | `docs/IMPLEMENTATION_PLAN.md` §4.2 | `evidence/code-inspections/M3-inspection.md` |
| M3-02 | Gold GE suite has 12 expectations | 🟠 S2 | `file-exists` | `great_expectations/` | `evidence/code-inspections/M3-inspection.md` |
| M3-03 | `gold_checkpoint.yml` is valid YAML | 🟠 S2 | `command` | — | `evidence/code-inspections/M3-inspection.md` |
| M3-04 | `contracts/gold-schema.json` defines fact + dim schemas | 🟠 S2 | `contract` | `contracts/gold-schema.json` | `evidence/code-inspections/M3-inspection.md` |
| M3-05 | `to_gold.py` creates fact_crime + 4 dims | 🟠 S2 | `grep` | `docs/IMPLEMENTATION_PLAN.md` §4.2 | `evidence/code-inspections/M3-inspection.md` |
| M3-06 | Surrogate keys use xxhash64 or equivalent | 🟠 S2 | `grep` | — | `evidence/code-inspections/M3-inspection.md` |
| M3-07 | `dim_time` has year, month, day, hour, dow, is_weekend | 🟡 S3 | `grep` | — | `evidence/code-inspections/M3-inspection.md` |
| M3-08 | `dim_location` has `geom_wkt` column (WKT format) | 🟠 S2 | `grep` | — | `evidence/code-inspections/M3-inspection.md` |
| M3-09 | Pipeline tests: 12/12 pass (`test_gold.py`) | 🔴 S1 | `test` | `pipeline/tests/` | `evidence/gates/results.md` |
| M3-10 | `make spark-gold` executes successfully | 🔴 S1 | `command` | — | `evidence/gates/results.md` |
| M3-11 | Gold `fact_crime` row count >= 1000 | 🔴 S1 | `command` | — | `evidence/gates/results.md` |
| M3-12 | All 5 tables present (fact + 4 dims) | 🔴 S1 | `command` | — | `evidence/gates/results.md` |

---

## M4 — Warehouse (Postgres + dbt) (17 items)

| # | Check | Severity | Verification | Cross-Reference | Evidence |
|---|-------|----------|-------------|-----------------|----------|
| M4-01 | `load_postgres.py` creates all 5 tables | 🟠 S2 | `grep` | — | `evidence/code-inspections/M4-inspection.md` |
| M4-02 | PostGIS: `ST_GeomFromText(geom_wkt, 4326)` used | 🟠 S2 | `grep` | — | `evidence/code-inspections/M4-inspection.md` |
| M4-03 | Primary keys defined on all tables | 🟠 S2 | `grep` | — | `evidence/code-inspections/M4-inspection.md` |
| M4-04 | Foreign keys from `fact_crime` to all 4 dims | 🟠 S2 | `grep` | — | `evidence/code-inspections/M4-inspection.md` |
| M4-05 | Indexes on FK columns and date columns | 🟠 S2 | `grep` | — | `evidence/code-inspections/M4-inspection.md` |
| M4-06 | `dbt_project.yml` has correct profile reference | 🟠 S2 | `grep` | — | `evidence/code-inspections/M4-inspection.md` |
| M4-07 | `profiles.yml` has postgres target with correct connection | 🟠 S2 | `grep` | — | `evidence/code-inspections/M4-inspection.md` |
| M4-08 | 5 staging models in `dbt/models/staging/` | 🟠 S2 | `file-exists` | — | `evidence/code-inspections/M4-inspection.md` |
| M4-09 | 2 intermediate models in `dbt/models/intermediate/` | 🟠 S2 | `file-exists` | — | `evidence/code-inspections/M4-inspection.md` |
| M4-10 | 5 mart models in `dbt/models/marts/` | 🟠 S2 | `file-exists` | — | `evidence/code-inspections/M4-inspection.md` |
| M4-11 | `schema.yml` has 53+ column tests (not_null + unique on PKs) | 🟠 S2 | `grep` | — | `evidence/code-inspections/M4-inspection.md` |
| M4-12 | Pipeline tests: 31/31 pass (`test_warehouse.py`) | 🔴 S1 | `test` | `pipeline/tests/` | `evidence/gates/results.md` |
| M4-13 | `make load-postgres` executes successfully | 🔴 S1 | `command` | — | `evidence/gates/results.md` |
| M4-14 | `make dbt-run` materializes 12 models | 🔴 S1 | `command` | — | `evidence/gates/results.md` |
| M4-15 | `make dbt-test` passes 53+ tests | 🔴 S1 | `command` | — | `evidence/gates/results.md` |
| M4-16 | PostGIS SRID check: `SRID=4326` on `dim_location` | 🟠 S2 | `command` | — | `evidence/code-inspections/M4-inspection.md` |
| M4-17 | Row counts match: Gold Parquet == Postgres `fact_crime` | 🟠 S2 | `command` | — | `evidence/code-inspections/M4-inspection.md` |

---

## M5 — API (FastAPI) — Agent Checks (20 items)

| # | Check | Severity | Verification | Cross-Reference | Evidence |
|---|-------|----------|-------------|-----------------|----------|
| M5-01 | `main.py` has FastAPI app + registered middleware | 🟠 S2 | `grep` | — | `evidence/code-inspections/M5-inspection.md` |
| M5-02 | `api/app/routers/` has 8+ router files | 🟠 S2 | `file-exists` | `contracts/openapi.yaml` | `evidence/code-inspections/M5-inspection.md` |
| M5-03 | `api/app/schemas/` has 8+ schema files | 🟠 S2 | `file-exists` | — | `evidence/code-inspections/M5-inspection.md` |
| M5-04 | `api/app/services/` has 8+ service files | 🟠 S2 | `file-exists` | — | `evidence/code-inspections/M5-inspection.md` |
| M5-05 | All endpoints have Pydantic request/response models | 🟠 S2 | `grep` | `contracts/openapi.yaml` | `evidence/code-inspections/M5-inspection.md` |
| M5-06 | Services use asyncpg (async DB access) | 🟠 S2 | `grep` | — | `evidence/code-inspections/M5-inspection.md` |
| M5-07 | `services/cache.py` has Redis caching logic | 🟡 S3 | `grep` | — | `evidence/code-inspections/M5-inspection.md` |
| M5-08 | `middleware/gzip.py` registered in `main.py` | 🟡 S3 | `grep` | — | `evidence/code-inspections/M5-inspection.md` |
| M5-09 | `middleware/request_id.py` registered in `main.py` | 🟡 S3 | `grep` | — | `evidence/code-inspections/M5-inspection.md` |
| M5-10 | `CORSMiddleware` configured in `main.py` | 🟠 S2 | `grep` | — | `evidence/code-inspections/M5-inspection.md` |
| M5-11 | `tests/conftest.py` has `mock_db` and `client` fixtures | 🟠 S2 | `grep` | — | `evidence/code-inspections/M5-inspection.md` |
| M5-12 | API tests: 42/42 pass | 🔴 S1 | `test` | `api/tests/` | `evidence/gates/results.md` |
| M5-13 | `make api-lint` passes (ruff + mypy) | 🔴 S1 | `command` | — | `evidence/gates/results.md` |
| M5-14 | `make contracts-validate` passes (OpenAPI valid) | 🔴 S1 | `command` | `contracts/openapi.yaml` | `evidence/gates/results.md` |
| M5-15 | `/docs` returns HTTP 200 | 🔴 S1 | `command` | — | `evidence/gates/results.md` |
| M5-16 | `/api/health/live` returns HTTP 200 | 🔴 S1 | `command` | — | `evidence/gates/results.md` |
| M5-17 | All 13 data endpoints return HTTP 200 with JSON | 🔴 S1 | `command` | `contracts/openapi.yaml` | `evidence/gates/results.md` |
| M5-18 | `test_errors.py` covers 4xx scenarios (422 for invalid input) | 🟠 S2 | `test` | — | `evidence/code-inspections/M5-inspection.md` |
| M5-19 | `gitleaks detect`: 0 secrets found | 🔴 S1 | `command` | — | `evidence/gates/results.md` |
| M5-20 | Security headers present (HSTS, X-Content-Type-Options) | 🟠 S2 | `curl` | — | `evidence/code-inspections/M5-inspection.md` |

---

## M5 — API — Data Analyst Critic Checks (8 items)

| # | Check | Severity | Verification | Cross-Reference | Evidence |
|---|-------|----------|-------------|-----------------|----------|
| M5-C1 | `/api/overview` total matches `COUNT(*) FROM fact_crime` | 🔴 S1 | `command` | dbt mart | `evidence/critic-evaluations/data-analyst.md` |
| M5-C2 | `/api/overview` arrest_rate matches dbt mart value | 🔴 S1 | `command` | dbt mart | `evidence/critic-evaluations/data-analyst.md` |
| M5-C3 | `/api/timeseries` date range filter returns correct subset | 🟠 S2 | `command` | — | `evidence/critic-evaluations/data-analyst.md` |
| M5-C4 | `/api/heatmap` hourly data matches `mart_temporal_heatmap` | 🟠 S2 | `command` | dbt mart | `evidence/critic-evaluations/data-analyst.md` |
| M5-C5 | `/api/geo/choropleth` district counts match `mart_geo_choropleth` | 🟠 S2 | `command` | dbt mart | `evidence/critic-evaluations/data-analyst.md` |
| M5-C6 | `/api/crime-types/top` returns top N matching `mart_crime_type_trend` | 🟠 S2 | `command` | dbt mart | `evidence/critic-evaluations/data-analyst.md` |
| M5-C7 | `/api/filters` returns all distinct values from DB | 🟠 S2 | `command` | — | `evidence/critic-evaluations/data-analyst.md` |
| M5-C8 | Response shapes match OpenAPI spec (Swagger UI) | 🟠 S2 | `contract` | `contracts/openapi.yaml` | `evidence/critic-evaluations/data-analyst.md` |

---

## M6 — Web (React) — Agent Checks (18 items)

| # | Check | Severity | Verification | Cross-Reference | Evidence |
|---|-------|----------|-------------|-----------------|----------|
| M6-01 | `vite.config.ts` has valid Vite configuration | 🟠 S2 | `file-exists` | — | `evidence/code-inspections/M6-inspection.md` |
| M6-02 | `tsconfig.json` has strict mode enabled | 🟠 S2 | `grep` | — | `evidence/code-inspections/M6-inspection.md` |
| M6-03 | `index.css` has dark theme (#0a0a0f background, CSS custom properties) | 🟡 S3 | `grep` | `contracts/design-tokens.json` | `evidence/code-inspections/M6-inspection.md` |
| M6-04 | `main.tsx` renders App component | 🟠 S2 | `grep` | — | `evidence/code-inspections/M6-inspection.md` |
| M6-05 | `App.tsx` has 4 routes (/, /crime-types, /locations, /analysis) | 🟠 S2 | `grep` | `docs/milestones/M5-M6-UIUX-Rubric.md` §2 | `evidence/code-inspections/M6-inspection.md` |
| M6-06 | `components/layout/` has AppShell, Sidebar, Header | 🟠 S2 | `file-exists` | — | `evidence/code-inspections/M6-inspection.md` |
| M6-07 | `pages/` has DashboardPage, CrimeTypesPage, LocationsPage, AnalysisPage | 🟠 S2 | `file-exists` | — | `evidence/code-inspections/M6-inspection.md` |
| M6-08 | `components/charts/` has 6 chart components | 🟠 S2 | `file-exists` | — | `evidence/code-inspections/M6-inspection.md` |
| M6-09 | `components/maps/` has ChoroplethMap, ClusterMap | 🟠 S2 | `file-exists` | — | `evidence/code-inspections/M6-inspection.md` |
| M6-10 | `stores/filters.ts` has Zustand store with URL sync | 🟠 S2 | `grep` | — | `evidence/code-inspections/M6-inspection.md` |
| M6-11 | `hooks/useUrlSync.ts` has bidirectional sync logic | 🟠 S2 | `grep` | — | `evidence/code-inspections/M6-inspection.md` |
| M6-12 | `lib/api.ts` has 13+ endpoint methods | 🟠 S2 | `grep` | `contracts/api-types.ts` | `evidence/code-inspections/M6-inspection.md` |
| M6-13 | `ErrorBoundary.tsx` catches render errors | 🟠 S2 | `grep` | MISTAKE-005 | `evidence/code-inspections/M6-inspection.md` |
| M6-14 | `make web-lint` passes (typecheck + eslint) | 🔴 S1 | `command` | — | `evidence/gates/results.md` |
| M6-15 | `make web-test` passes (2/2 vitest) | 🔴 S1 | `command` | — | `evidence/gates/results.md` |
| M6-16 | Unit tests: 2/2 pass | 🔴 S1 | `test` | `web/tests/` | `evidence/gates/results.md` |
| M6-17 | `make web-e2e` passes (30/30 Playwright) | 🔴 S1 | `command` | — | `evidence/gates/results.md` |
| M6-18 | `pnpm build` produces `dist/` without errors | 🔴 S1 | `command` | — | `evidence/gates/results.md` |

---

## M6 — Web — Playwright Checks (12 items)

| # | Check | Severity | Verification | Cross-Reference | Evidence |
|---|-------|----------|-------------|-----------------|----------|
| M6-P1 | Dark theme renders (#0a0a0f background on dashboard) | 🟡 S3 | `test` | `web/e2e/` | `evidence/e2e/e2e.txt` |
| M6-P2 | Navigation works (all 4 pages load via sidebar) | 🟠 S2 | `test` | `web/e2e/navigation.spec.ts` | `evidence/e2e/e2e.txt` |
| M6-P3 | KPI cards render (4 cards with numeric values) | 🟠 S2 | `test` | `web/e2e/dashboard.spec.ts` | `evidence/e2e/e2e.txt` |
| M6-P4 | Filters sync to URL (change filter → URL params update) | 🟠 S2 | `test` | `web/e2e/filters.spec.ts` | `evidence/e2e/e2e.txt` |
| M6-P5 | Responsive layout (sidebar collapses at mobile viewport) | 🟡 S3 | `test` | `web/e2e/responsive.spec.ts` | `evidence/e2e/e2e.txt` |
| M6-P6 | axe-core scan: 0 WCAG 2.1 AA violations per page | 🟠 S2 | `test` | `web/e2e/accessibility.spec.ts` | `evidence/e2e/e2e.txt` |
| M6-P7 | Keyboard navigation: all interactive elements focusable | 🟡 S3 | `test` | `web/e2e/accessibility.spec.ts` | `evidence/e2e/e2e.txt` |
| M6-P8 | Empty states visible (filter to no data → "No data" message) | 🟡 S3 | `manual` | — | `evidence/code-inspections/M6-inspection.md` |
| M6-P9 | Loading skeletons shown during data fetch | 🟡 S3 | `manual` | — | `evidence/code-inspections/M6-inspection.md` |
| M6-P10 | Error boundary shows recovery UI on error | 🟠 S2 | `manual` | MISTAKE-005 | `evidence/code-inspections/M6-inspection.md` |
| M6-P11 | Console: 0 JS errors on all pages | 🔴 S1 | `test` | `web/e2e/dashboard.spec.ts` | `evidence/e2e/e2e.txt` |
| M6-P12 | No long tasks (> 500ms) on any page | 🟡 S3 | `manual` | — | `evidence/code-inspections/M6-inspection.md` |

---

## M6 — Web — Critic Checks: Data Analyst (6 items)

| # | Check | Severity | Verification | Cross-Reference | Evidence |
|---|-------|----------|-------------|-----------------|----------|
| M6-DA1 | KPI numbers on dashboard match `/api/overview` response | 🔴 S1 | `manual` | `docs/assessment/rubric.md` DA-1 | `evidence/critic-evaluations/data-analyst.md` |
| M6-DA2 | Timeseries chart shows daily granularity | 🟠 S2 | `manual` | `docs/assessment/rubric.md` DA-6 | `evidence/critic-evaluations/data-analyst.md` |
| M6-DA3 | Heatmap shows 7×24 hourly pattern with correct labels | 🟠 S2 | `manual` | `docs/assessment/rubric.md` DA-6 | `evidence/critic-evaluations/data-analyst.md` |
| M6-DA4 | Crime types table is sortable by clicking column headers | 🟠 S2 | `manual` | `docs/assessment/rubric.md` DA-4 | `evidence/critic-evaluations/data-analyst.md` |
| M6-DA5 | Location list is filterable via search input | 🟠 S2 | `manual` | `docs/assessment/rubric.md` DA-4 | `evidence/critic-evaluations/data-analyst.md` |
| M6-DA6 | Analysis page has date range filter that updates all charts | 🟠 S2 | `manual` | `docs/assessment/rubric.md` DA-2 | `evidence/critic-evaluations/data-analyst.md` |

---

## M6 — Web — Critic Checks: Citizen (5 items)

| # | Check | Severity | Verification | Cross-Reference | Evidence |
|---|-------|----------|-------------|-----------------|----------|
| M6-CI1 | No technical jargon in labels (no "primary_type", "domestic_pct") | 🟠 S2 | `manual` | `docs/assessment/rubric.md` CI-1 | `evidence/critic-evaluations/citizen.md` |
| M6-CI2 | Maps load and show meaningful geographic data | 🟠 S2 | `manual` | `docs/assessment/rubric.md` CI-4 | `evidence/critic-evaluations/citizen.md` |
| M6-CI3 | Explanations present ("What does this mean?" or tooltips) | 🟡 S3 | `manual` | `docs/assessment/rubric.md` CI-2 | `evidence/critic-evaluations/citizen.md` |
| M6-CI4 | Data source explained ("Chicago crime data 2024-2026") | 🟡 S3 | `manual` | `docs/assessment/rubric.md` CI-3 | `evidence/critic-evaluations/citizen.md` |
| M6-CI5 | Data freshness shown ("Data as of YYYY-MM-DD") | 🟡 S3 | `manual` | `docs/assessment/rubric.md` CI-3 | `evidence/critic-evaluations/citizen.md` |

---

## M6 — Web — Critic Checks: Executive (5 items)

| # | Check | Severity | Verification | Cross-Reference | Evidence |
|---|-------|----------|-------------|-----------------|----------|
| M6-EX1 | KPIs are first visible element (above the fold) | 🟠 S2 | `manual` | `docs/assessment/rubric.md` EX-1 | `evidence/critic-evaluations/executive.md` |
| M6-EX2 | 5-second comprehension (understand situation without scrolling) | 🟠 S2 | `manual` | `docs/assessment/rubric.md` EX-2 | `evidence/critic-evaluations/executive.md` |
| M6-EX3 | Color coding consistent (red = concern, green = positive) | 🟡 S3 | `manual` | `docs/assessment/rubric.md` EX-3 | `evidence/critic-evaluations/executive.md` |
| M6-EX4 | Numbers add up (KPI totals match chart totals) | 🟠 S2 | `manual` | `docs/assessment/rubric.md` EX-4 | `evidence/critic-evaluations/executive.md` |
| M6-EX5 | No information overload (4-6 charts max per page) | 🟡 S3 | `manual` | `docs/assessment/rubric.md` EX-5 | `evidence/critic-evaluations/executive.md` |

---

## M6 — Web — Critic Checks: Journalist (5 items)

| # | Check | Severity | Verification | Cross-Reference | Evidence |
|---|-------|----------|-------------|-----------------|----------|
| M6-JO1 | Time period comparison possible (compare different periods) | 🟠 S2 | `manual` | `docs/assessment/rubric.md` JO-1 | `evidence/critic-evaluations/journalist.md` |
| M6-JO2 | Anomalies visible in charts (spikes/drops visually prominent) | 🟠 S2 | `manual` | `docs/assessment/rubric.md` JO-2 | `evidence/critic-evaluations/journalist.md` |
| M6-JO3 | District comparison possible (compare areas side by side) | 🟠 S2 | `manual` | `docs/assessment/rubric.md` JO-3 | `evidence/critic-evaluations/journalist.md` |
| M6-JO4 | Crime type trends visible (types increasing/decreasing) | 🟠 S2 | `manual` | `docs/assessment/rubric.md` JO-4 | `evidence/critic-evaluations/journalist.md` |
| M6-JO5 | Data export available ("Copy list" button works) | 🟡 S3 | `manual` | `docs/assessment/rubric.md` JO-5 | `evidence/critic-evaluations/journalist.md` |

---

## M6 — Web — Critic Checks: First-Timer (5 items)

| # | Check | Severity | Verification | Cross-Reference | Evidence |
|---|-------|----------|-------------|-----------------|----------|
| M6-FT1 | Clear title/hero section ("Chicago Crime Dashboard" visible) | 🟠 S2 | `manual` | `docs/assessment/rubric.md` FT-1 | `evidence/critic-evaluations/first-timer.md` |
| M6-FT2 | Onboarding explanation ("About this dashboard" present) | 🟡 S3 | `manual` | `docs/assessment/rubric.md` FT-2 | `evidence/critic-evaluations/first-timer.md` |
| M6-FT3 | Loading states shown (skeleton shimmer during load) | 🟡 S3 | `manual` | `docs/assessment/rubric.md` FT-3 | `evidence/critic-evaluations/first-timer.md` |
| M6-FT4 | Error states helpful ("Something went wrong" + retry) | 🟠 S2 | `manual` | `docs/assessment/rubric.md` FT-4 | `evidence/critic-evaluations/first-timer.md` |
| M6-FT5 | Navigation intuitive (sidebar links clearly labeled) | 🟠 S2 | `manual` | `docs/assessment/rubric.md` FT-5 | `evidence/critic-evaluations/first-timer.md` |

---

## M6 — Web — Stakeholder Checks (3 items)

| # | Check | Severity | Verification | Cross-Reference | Evidence |
|---|-------|----------|-------------|-----------------|----------|
| M6-SK1 | Numbers defensible for policy (KPIs backed by verifiable data) | 🟠 S2 | `manual` | `docs/assessment/rubric.md` PM-1 | `evidence/critic-evaluations/policy-maker.md` |
| M6-SK2 | Neighborhood-level data (can find specific areas) | 🟠 S2 | `manual` | `docs/assessment/rubric.md` PM-2 | `evidence/critic-evaluations/community-organizer.md` |
| M6-SK3 | Headline-worthy findings visible (trends and anomalies prominent) | 🟡 S3 | `manual` | `docs/assessment/rubric.md` NE-1 | `evidence/critic-evaluations/news-editor.md` |

---

## Total Check Counts

| Milestone | S1 | S2 | S3 | S4 | Total |
|-----------|-----|-----|-----|-----|-------|
| M0 | 3 | 6 | 8 | 1 | 18 |
| M1 | 4 | 6 | 4 | 2 | 16 |
| M2 | 3 | 7 | 2 | 0 | 12 |
| M3 | 3 | 7 | 1 | 1 | 12 |
| M4 | 5 | 11 | 0 | 1 | 17 |
| M5 (Agent) | 6 | 10 | 3 | 1 | 20 |
| M5 (Critic) | 2 | 6 | 0 | 0 | 8 |
| M6 (Agent) | 5 | 11 | 1 | 1 | 18 |
| M6 (Playwright) | 1 | 4 | 5 | 2 | 12 |
| M6 (Critic) | 1 | 14 | 7 | 1 | 23 |
| **Total** | **33** | **82** | **31** | **10** | **156** |

---

## Changelog

| Date | Entry | Author |
|------|-------|--------|
| 2026-06-06 | v2.0 — Added severity, verification methods, cross-references to all 156 items | Assessment Framework |
| 2026-06-06 | v1.0 — Initial checklists (162 items) | Assessment Framework |
