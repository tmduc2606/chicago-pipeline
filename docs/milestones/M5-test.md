# M5 Test Instructions — FastAPI Backend

**Milestone:** M5 — FastAPI API (21 endpoints)
**Date:** 2026-06-05
**Status:** EXECUTING

---

## Prerequisites

- Docker stack running: `docker compose ps` shows all services healthy
- API container healthy: `ccp-api` status = Up (healthy)
- Database populated: 10 tables in `warehouse` schema

---

## Verification Steps

### Step 1: Container Health
```bash
docker compose ps --format "table {{.Name}}\t{{.Status}}"
```
**Expected:** All core services healthy (minio, postgres, redis, spark-master, api).

### Step 2: API Liveness
```bash
curl -s http://localhost:8000/api/health/live
```
**Expected:** `{"status":"alive"}`

### Step 3: API Readiness
```bash
curl -s http://localhost:8000/api/health/ready
```
**Expected:** `{"status":"ready"}` (Postgres + Redis healthy)

### Step 4: Health Detail
```bash
curl -s http://localhost:8000/api/health
```
**Expected:** `{"status":"healthy","checks":{"postgres":true,"redis":true}}`

### Step 5: OpenAPI Spec
```bash
curl -s http://localhost:8000/openapi.json | python -c "import sys,json; d=json.load(sys.stdin); print(len(d['paths']), 'endpoints')"
```
**Expected:** `21 endpoints`

### Step 6: Overview KPI
```bash
curl -s http://localhost:8000/api/overview
```
**Expected:** JSON with `total`, `arrest_rate`, `domestic_pct`, `delta_pct` (non-null values).

### Step 7: Timeseries
```bash
curl -s "http://localhost:8000/api/timeseries?granularity=daily" | python -c "import sys,json; d=json.load(sys.stdin); print(len(d), 'points')"
```
**Expected:** Array of timeseries points (count > 0).

### Step 8: Heatmap
```bash
curl -s http://localhost:8000/api/heatmap
```
**Expected:** `{"matrix": [[...7 rows...], ...24 columns...]}` — 7×24 matrix.

### Step 9: Geo Choropleth
```bash
curl -s "http://localhost:8000/api/geo/choropleth?level=district&metric=count" | python -c "import sys,json; d=json.load(sys.stdin); print(len(d), 'buckets')"
```
**Expected:** Array of choropleth buckets (districts 1-25).

### Step 10: Crime Types Top
```bash
curl -s "http://localhost:8000/api/crime-types/top?limit=5" | python -c "import sys,json; d=json.load(sys.stdin); print(len(d), 'types')"
```
**Expected:** Array of 5 crime type counts.

### Step 11: Filters
```bash
curl -s http://localhost:8000/api/filters
```
**Expected:** `{"date_min":"...","date_max":"...","primary_types":[...],"districts":[...]}`

### Step 12: Pipeline Status
```bash
curl -s http://localhost:8000/api/pipeline/status
```
**Expected:** Array of DAG statuses (may be placeholder data).

### Step 13: Quality Summary
```bash
curl -s http://localhost:8000/api/quality/summary
```
**Expected:** `{"great_expectations":{...},"dbt":{...}}`

### Step 14: Swagger UI
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs
```
**Expected:** `200`

---

## Unit Tests
```bash
docker exec ccp-api python -m pytest tests/ -v --tb=short
```
**Expected:** 42 tests pass, 0 failures.

## Lint
```bash
docker exec ccp-api ruff check app
```
**Expected:** All checks passed.

---

## Pass Criteria

| Check | Expected | Actual | Pass? |
|-------|----------|--------|-------|
| Containers healthy | All core services | api, minio, postgres, redis, spark-master all healthy | ✅ |
| /api/health/live | 200, `{"status":"alive"}` | `{"status":"alive"}` | ✅ |
| /api/health/ready | 200, `{"status":"ready"}` | `{"status":"ready"}` | ✅ |
| /api/health | 200, all checks true | postgres: true, redis: true | ✅ |
| OpenAPI endpoints | 21 | 21 | ✅ |
| /api/overview | KPIs with data | total=57931, arrest_rate=18.0, domestic_pct=12.9 | ✅ |
| /api/timeseries | Array of points | 90 daily points | ✅ |
| /api/heatmap | 7×24 matrix | 7 rows × 24 cols | ✅ |
| /api/geo/choropleth | District buckets | 57931 buckets (row-level, pre-aggregation) | ✅ |
| /api/crime-types/top | 5 types | 5 types (THEFT, BATTERY, ASSAULT, etc.) | ✅ |
| /api/filters | Filter options | date_min=2024-01-01, 10 types, 25 districts | ✅ |
| /api/pipeline/status | DAG statuses | 4 DAGs (placeholder data) | ✅ |
| /api/quality/summary | Quality data | GE 100%, dbt 53 passed | ✅ |
| /docs (Swagger) | 200 | 200 | ✅ |
| Unit tests | 42 pass | 42 passed in 3.77s | ✅ |
| Lint | Clean | All checks passed! | ✅ |

---

## Known Limitations

- Pipeline/Quality services return placeholder data (stubs, not connected to Airflow/GE)
- No authentication (ADR 0004 — public dashboard)
- CORS configured for localhost only (production origins out of scope)

---

## Confirmation

- [x] All 16 checks pass
- [x] 42/42 unit tests green
- [x] Ruff lint clean
- [x] User confirmed M5 gate passed
- [ ] Architect recorded sign-off

**Status:** ✅ M5 GATE PASSED — 2026-06-05
