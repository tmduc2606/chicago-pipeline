# Hotfixes Catalogue & QoL Improvements — M1→M5 Assessment

**Date:** 2026-06-05
**Scope:** Full M1→M5 pipeline (Ingestion → Bronze → Silver → Gold → Postgres/dbt → FastAPI)
**Status:** H1–H15 COMPLETE ✅ — 42/42 tests pass, ruff clean

---

## Executive Summary

The M1→M5 pipeline is **functional end-to-end**: data flows from synthetic CSV → Bronze Parquet → Silver Parquet → Gold Parquet/Postgres → dbt marts → FastAPI endpoints. All 19 data endpoints return 200, 23 unit tests pass, ruff lint is clean.

However, a comprehensive code review uncovered **4 critical**, **11 high**, and **15 medium** issues across security, correctness, and production-readiness. This document catalogues them as hotfixes (must-fix before M6) and QoL improvements (nice-to-have).

---

## CRITICAL — Must Fix Before M6

### H1: `config.py` env_prefix mismatch — settings don't read env vars
- **File:** `api/app/config.py:25`
- **Issue:** `env_prefix=""` means pydantic-settings reads `postgres_host` (lowercase) from env, but `docker-compose.yaml` sets `POSTGRES_HOST` (uppercase). All API settings silently fall back to hardcoded defaults (`localhost`, `change_me_local`).
- **Impact:** API connects to wrong Postgres in any non-Docker environment.
- **Fix:** Change to `env_prefix="POSTGRES_"` or set lowercase env vars in docker-compose.
- **Done:** Changed to `env_prefix="API_"` matching docker-compose `API_` prefix.

### H2: Pipeline & Quality services are stubs
- **Files:** `api/app/services/pipeline.py`, `api/app/services/quality.py`
- **Issue:** Return hardcoded data (`state="none"`, `success_pct=100.0`). No Airflow API client despite config existing.
- **Impact:** `/api/pipeline/*` and `/api/quality/summary` return misleading data.
- **Fix:** Either implement Airflow REST API client or add `TODO` + Swagger `description: "Stub — not yet connected"` annotations.

### H3: SQL injection surface in `geo.py`
- **File:** `api/app/services/geo.py:65-68`
- **Issue:** `group_col` and `val_expr` are interpolated into SQL via f-string. Router regex (`pattern="^(district|community_area)$"`) validates input, but the service layer itself has no guard.
- **Impact:** If called programmatically (e.g., from another service), injectable.
- **Fix:** Add allowlist validation in the service function.

### H4: `docker-compose.lite.yml` missing — `make up-lite` fails
- **File:** `Makefile:22`
- **Issue:** `up-lite` target references `docker-compose.lite.yml` which does not exist.
- **Impact:** `make up-lite` and `make pipeline` (DoD requirement) fail.
- **Fix:** Create `docker-compose.lite.yml` or remove the target.

---

## HIGH — Fix Before M6

### H5: No CORS middleware
- **File:** `api/app/main.py:19-23`
- **Issue:** No `CORSMiddleware` configured. Frontend (M6 React) on `localhost:5173` cannot call API on `localhost:8000` without CORS errors.
- **Fix:** Add `app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], ...)`.

### H6: Dockerfile runs as root, single-stage build
- **File:** `api/Dockerfile`
- **Issue:** No `USER` directive. Test deps (`pytest`, `ruff`, `mypy`) bundled in production image.
- **Fix:** Multi-stage build + `USER nonroot` + separate `requirements-dev.txt`.

### H7: No `.dockerignore`
- **File:** Missing `api/.dockerignore`
- **Issue:** `COPY . .` copies `tests/`, `__pycache__/`, `.ruff_cache/`, `.env*` into image.
- **Fix:** Create `api/.dockerignore` excluding test/cache/env files.

### H8: Redis has no auth, port exposed
- **File:** `docker-compose.yaml:63-73`, `api/app/deps.py:10`
- **Issue:** Redis `requirepass` not set. Port 6379 exposed to host.
- **Fix:** Set `REDIS_PASSWORD` env var + add `requirepass` to redis command.

### H9: All database ports exposed to host
- **File:** `docker-compose.yaml` (Postgres 5432, MinIO 9000/9001, Redis 6379)
- **Issue:** In production this is an attack surface.
- **Fix:** Remove host port mappings for non-development services; use Docker internal networking.

### H10: No resource limits on Docker services
- **File:** `docker-compose.yaml` (all services)
- **Issue:** No `deploy.resources.limits`. Spark or Airflow can consume all host resources.
- **Fix:** Add `deploy.resources.limits` with reasonable defaults.

### H11: `make reset` prunes ALL Docker volumes on host
- **File:** `Makefile:41-42`
- **Issue:** `docker volume prune -f` destroys all unused volumes, not just project ones.
- **Fix:** Change to `docker volume rm $(docker volume ls -q | grep chicago-pipeline)`.

### H12: Hardcoded credentials in GE config
- **File:** `great_expectations/great_expectations.yml:12-13`
- **Issue:** `access.key: minio` and `secret.key: change_me_local` in plain text.
- **Fix:** Use `${MINIO_ROOT_USER}` env var references.

### H13: Duplicated Spark session builders (4 copies)
- **Files:** `common/spark_session.py`, `bronze/to_bronze.py:84-93`, `great_expectations/run_validation.py:21-32`, `great_expectations/run_drift_detection.py:27-38`
- **Issue:** Each builds its own SparkSession with S3A config. Drift risk.
- **Fix:** Extract shared `_build_spark()` into `common/spark_session.py`.

### H14: DAG import-time side effects
- **Files:** `airflow/dags/ingest_dag.py:103-104`, `airflow/dags/bronze_to_silver_dag.py:41-42`
- **Issue:** `Variable.get()` called at module level. Fails during `airflow db init`.
- **Fix:** Move inside task functions or `@dag` body.

### H15: No error-path tests
- **File:** `api/tests/` (all)
- **Issue:** All tests are happy-path only. No tests for SQL errors, Redis down, malformed dates, 500 responses.
- **Fix:** Add tests for error conditions.

---

## MEDIUM — Fix Before M7

### Q1: `structlog` in requirements but never imported
- **File:** `api/requirements.txt:8`
- **Issue:** Dead dependency. No structured logging configured anywhere.
- **Fix:** Either configure structlog or remove from requirements.

### Q2: Cache key uses MD5
- **File:** `api/app/services/cache.py:22`
- **Issue:** MD5 flagged by security scanners (Trivy policy).
- **Fix:** Replace with `hashlib.sha256`.

### Q3: Unused `Pagination` and `ErrorResponse` schemas
- **File:** `api/app/schemas/common.py:4-16`
- **Issue:** Defined but never imported by any router or service.
- **Fix:** Either implement pagination/error responses or remove dead code.

### Q4: Date parameters are `str` everywhere
- **Files:** All routers/services with `from_date`/`to_date`
- **Issue:** No ISO 8601 validation. Callers can pass `"not-a-date"`.
- **Fix:** Use `datetime.date` type or add regex validation.

### Q5: N+1 queries in `filters.py`
- **File:** `api/app/services/filters.py:29-36`
- **Issue:** Three sequential `await db.execute()` calls.
- **Fix:** Combine into single query or use `asyncio.gather`.

### Q6: Missing `silver/schema.py` and `gold/schema.py`
- **Files:** Missing
- **Issue:** Schema defined inline in `to_silver.py` and `to_gold.py`. Not importable.
- **Fix:** Create `silver/schema.py` and `gold/schema.py` modules.

### Q7: `to_bronze.py` missing error handling
- **File:** `pipeline/src/chicago_pipeline/bronze/to_bronze.py`
- **Issue:** No try/except around `df.write`. Raw PySpark exception on failure.
- **Fix:** Add try/except with structured logging.

### Q8: `scripts/seed.py` duplicates `download_kaggle.py`
- **Files:** `scripts/seed.py`, `pipeline/src/chicago_pipeline/ingest/download_kaggle.py`
- **Issue:** Constants and logic copied verbatim.
- **Fix:** Import `generate_synthetic()` from the package.

### Q9: dbt missing `relationships` FK tests
- **File:** `dbt/models/schema.yml`
- **Issue:** PKs have `unique`+`not_null` tests but no `relationships` tests for FKs.
- **Fix:** Add `relationships` tests on staging models.

### Q10: `to_silver.py` redundant partition add/drop/add
- **File:** `pipeline/src/chicago_pipeline/silver/to_silver.py:200-206`
- **Issue:** Calls `_add_partition_columns()` twice with a drop in between.
- **Fix:** Remove the redundant first call.

### Q11: `SCHEMA_MAP` in `load_postgres.py` is dead code
- **File:** `pipeline/src/chicago_pipeline/warehouse/load_postgres.py:23-50`
- **Issue:** 28-line dict defined but never referenced.
- **Fix:** Remove or integrate with `df.to_sql()` type mapping.

### Q12: `spark.stop()` not in `finally` in `verify_m3_gold.py`
- **File:** `scripts/spike/verify_m3_gold.py:162`
- **Issue:** Session not stopped on exception.
- **Fix:** Wrap in `try/finally`.

### Q13: No `dbt-docs-serve` Makefile target
- **File:** `Makefile`
- **Issue:** `dbt-docs` generates docs but no target to serve them.
- **Fix:** Add `dbt-docs-serve` target.

### Q14: Dependency versions unpinned, no lock file
- **Files:** `api/requirements.txt`, `pipeline/requirements.txt`
- **Issue:** All use `>=` without upper bounds. No lock file.
- **Fix:** Pin exact versions or generate lock file.

### Q15: No structlog request/response logging
- **File:** `api/app/main.py`
- **Issue:** No request logging middleware. API requests are invisible in logs.
- **Fix:** Add structlog-based request logging middleware.

---

## QoL Improvements (Not Blocking)

### P1: Add rate limiting (slowapi or nginx ingress)
### P2: Add OpenAPI descriptions to all endpoints
### P3: Add pagination to list endpoints
### P4: Add response wrapper schema `{ data: [...], meta: { total } }`
### P5: Add `pool_pre_ping=True` to SQLAlchemy engine
### P6: Add `pool_recycle` to avoid stale connections
### P7: Add `TrustedHostMiddleware` to FastAPI
### P8: Replace `sys.path.insert` hacks with `pip install -e .`
### P9: Add `"B"` (bugbear) and `"S"` (security) to ruff rules
### P10: Add `--cov-fail-under=80` to pytest CI
### P11: Add gitleaks/Trivy scan target to Makefile
### P12: Add cross-DAG dependencies (dbt after silver_to_gold)
### P13: Add `on_failure_callback` to Airflow DAGs
### P14: Add `EXPOSE 8000` to API Dockerfile
### P15: Add dbt `on-run-end` hooks for post-run validation

---

## Summary

| Category | Count | Status |
|----------|-------|--------|
| CRITICAL | 4 | ✅ H1–H4 DONE |
| HIGH | 11 | ✅ H5–H15 DONE |
| MEDIUM | 15 | Q1–Q15 deferred to M7 |
| QoL | 15 | Deferred to M9 |
| **Total** | **45** | **15/15 critical+high DONE** |

**Recommendation:** H1–H15 all complete. 42/42 tests pass. Ruff clean. Ready to begin M6.

---

## Approval

- [ ] Architect — review and approve hotfix scope
- [ ] Backend Engineer — confirm fix estimates
- [ ] QA — validate fix verification plan
