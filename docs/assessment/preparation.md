# M0→M6 Implementation Preparation

**Date:** 2026-06-07
**Status:** READY — Assessment complete, remediation plan defined
**Next Milestone:** M7 (or M9 polish pass)

---

## Current State

### What's Complete (M0-M6)

| Milestone | Status | Evidence |
|-----------|--------|----------|
| M0: Foundation | ✅ Complete | Docker, compose, CI/CD structure |
| M1: Ingestion | ✅ Complete | CSV → Bronze (57,931 rows) |
| M2: Transformation | ✅ Complete | Bronze → Silver (57,931 rows) |
| M3: Aggregation | ✅ Complete | Silver → Gold (5 tables) |
| M4: Warehouse | ✅ Complete | Postgres + PostGIS, dbt models |
| M5: API | ✅ Complete | FastAPI, 42 tests pass |
| M6: UI | ⚠️ Partial | React app runs, E2E tests failing |

### What's Blocked

| Item | Blocker | Resolution |
|------|---------|------------|
| Assessment grade > F | FIND-001 (S1) | Fix 7 Playwright E2E tests |
| Critic evaluations | Manual execution | QA agent runs 8 persona evaluations |

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    Chicago Pipeline                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │  CSV     │───▶│  Bronze  │───▶│  Silver  │              │
│  │  Source  │    │  (S3)    │    │  (S3)    │              │
│  └──────────┘    └──────────┘    └──────────┘              │
│                                      │                       │
│                                      ▼                       │
│                                ┌──────────┐                 │
│                                │   Gold   │                 │
│                                │  (S3)    │                 │
│                                └──────────┘                 │
│                                      │                       │
│                                      ▼                       │
│                                ┌──────────┐                 │
│                                │ Postgres │                 │
│                                │ + PostGIS│                 │
│                                └──────────┘                 │
│                                      │                       │
│                          ┌───────────┴───────────┐          │
│                          ▼                       ▼          │
│                    ┌──────────┐           ┌──────────┐     │
│                    │   dbt    │           │  FastAPI │     │
│                    │  Models  │           │   (S5)   │     │
│                    └──────────┘           └──────────┘     │
│                                              │              │
│                                              ▼              │
│                                        ┌──────────┐        │
│                                        │  React   │        │
│                                        │   (M6)   │        │
│                                        └──────────┘        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Architecture

### Lake Layers (S3/MinIO)

| Layer | Format | Tables | Rows |
|-------|--------|--------|------|
| Bronze | Parquet | chicago_crime | 57,931 |
| Silver | Parquet | chicago_crime | 57,931 |
| Gold | Parquet | fact_crime, dim_time, dim_location, dim_offense, dim_case | 57,931 + 26,304 + 57,931 + 900 + 57,931 |

### Warehouse (Postgres)

| Table | Type | Rows | Keys |
|-------|------|------|------|
| dim_time | TABLE | 26,304 | PK: time_id |
| dim_location | TABLE | 57,931 | PK: location_id, PostGIS geometry |
| dim_offense | TABLE | 900 | PK: offense_id |
| dim_case | TABLE | 57,931 | PK: case_id |
| fact_crime | TABLE | 57,931 | PK: crime_id, FKs to all dims |

### dbt Models

| Layer | Models | Purpose |
|-------|--------|---------|
| Staging | 5 (stg_*) | Source data views |
| Intermediate | 2 (int_*) | Enrichment + geometry |
| Marts | 5 (mart_*) | Business-ready tables |

---

## API Architecture

### Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check |
| `/api/crimes` | GET | List crimes (paginated) |
| `/api/crimes/{id}` | GET | Single crime detail |
| `/api/stats/temporal` | GET | Temporal aggregations |
| `/api/stats/crime-types` | GET | Crime type breakdown |
| `/api/stats/locations` | GET | Location aggregations |
| `/api/stats/arrest-summary` | GET | Arrest statistics |
| `/api/stats/geo-choropleth` | GET | Geographic choropleth data |
| `/api/stats/kpi-daily` | GET | Daily KPI metrics |
| `/api/stats/heatmap` | GET | Temporal heatmap data |
| `/api/filters` | GET | Available filter options |

### Tech Stack

- **Framework:** FastAPI (Python 3.11)
- **Database:** asyncpg + SQLAlchemy (async)
- **Cache:** Redis (via `@cached` decorator)
- **Validation:** Great Expectations (3 checkpoints)

---

## Frontend Architecture

### Pages

| Page | Route | Purpose |
|------|-------|---------|
| Dashboard | `/` | KPI cards + temporal chart + recent crimes |
| Crime Types | `/crime-types` | Crime type breakdown + trends |
| Locations | `/locations` | Map + location stats |
| Analysis | `/analysis` | Deep analysis + filtering |

### Components

| Category | Count | Key Components |
|----------|-------|----------------|
| Charts | 7 | TemporalChart, CrimeTypeBar, ArrestPie, etc. |
| Maps | 2 | ClusterMap, ChoroplethMap |
| Layout | — | Sidebar, Header, ErrorBoundary |
| Filters | — | DateRange, CrimeTypeSelect, LocationSelect |

### Tech Stack

- **Framework:** React 18 + TypeScript
- **State:** Zustand (filters store)
- **Charts:** Recharts
- **Maps:** Leaflet + React-Leaflet
- **Build:** Vite
- **E2E:** Playwright

---

## Infrastructure

### Docker Services (13)

| Service | Image | Purpose |
|---------|-------|---------|
| spark-master | ccp-spark:3.5.1 | Spark driver |
| spark-worker | ccp-spark:3.5.1 | Spark executor |
| postgres | postgres:16 | Warehouse |
| minio | minio/minio | Object storage (S3-compatible) |
| redis | redis:7 | API cache |
| api | chicago-pipeline-api | FastAPI server |
| web | chicago-pipeline-web | React app (nginx) |
| airflow-scheduler | airflow:2.10.5 | DAG scheduler |
| airflow-webserver | airflow:2.10.5 | Airflow UI |
| grafana | grafana/grafana | Monitoring dashboards |
| prometheus | prometheus/prometheus | Metrics collection |
| marquez | marquezproject/marquez | Data lineage |
| pipeline-init | (one-shot) | Pipeline bootstrap |

### Health Checks

| Service | Check | Interval |
|---------|-------|----------|
| postgres | `pg_isready` | 10s |
| minio | `curl /minio/health/live` | 10s |
| redis | `redis-cli ping` | 10s |
| api | `curl /api/health` | 10s |
| web | `wget /` | 10s |
| spark-master | `curl /health` | 10s |

---

## Testing Strategy

### Test Levels

| Level | Tool | Count | Status |
|-------|------|-------|--------|
| L0: Unit | pytest (API) | 42 | ✅ PASS |
| L1: Unit with deps | pytest (mocked DB) | — | — |
| L2: Functional | dbt test | 53 | ✅ PASS |
| L2: Functional | GE validation | 3 | ✅ PASS |
| L3: E2E | Playwright | 40 | ⚠️ 33 pass, 7 fail |
| L4: Integration | Full pipeline | 1 | ✅ PASS |

### Quality Gates

| Gate | Tool | Severity | Status |
|------|------|----------|--------|
| Lint (ruff) | `ruff check` | S2 | ✅ PASS |
| Type check (mypy) | `mypy` | S3 | ⚠️ 92 issues |
| Unit tests | `pytest` | S1 | ✅ PASS |
| Contracts | `validate_contracts.sh` | S1 | ✅ PASS |
| Agent files | `validate_agents.sh` | S2 | ✅ PASS |
| Data quality | `dbt test` | S1 | ✅ PASS |
| Data validation | `GE` | S1 | ✅ PASS |
| Security | `gitleaks` | S1 | ✅ PASS |
| E2E | `Playwright` | S1 | ❌ 7 fail |

---

## Deployment

### Local Development

```bash
# Start all services
docker compose up -d --build

# Run pipeline
docker compose up pipeline-init

# Run tests
docker compose exec -T api python -m pytest -q
docker compose exec -T spark-master bash -c "cd /opt/dbt && dbt test --profiles-dir ."
docker compose --profile test run --rm playwright

# Run assessment
bash scripts/run_assessment.sh
```

### Ports

| Service | Port | URL |
|---------|------|-----|
| Web | 5173 | http://localhost:5173 |
| API | 8000 | http://localhost:8000 |
| Airflow | 8080 | http://localhost:8080 |
| Grafana | 3000 | http://localhost:3000 |
| Marquez | 3001 | http://localhost:3001 |
| MinIO | 9001 | http://localhost:9001 |
| Spark Master | 8081 | http://localhost:8081 |
| Prometheus | 9090 | http://localhost:9090 |

---

## Environment Variables

| Variable | Value | Source |
|----------|-------|--------|
| `POSTGRES_USER` | chicago | `.env` |
| `POSTGRES_PASSWORD` | change_me_local | `.env` |
| `MINIO_ROOT_USER` | minio | `.env` |
| `MINIO_ROOT_PASSWORD` | change_me_local | `.env` |
| `S3_ENDPOINT` | http://minio:9000 | docker-compose.yaml |
| `SPARK_MASTER` | spark://spark-master:7077 | docker-compose.yaml |

---

## Next Actions

> **Follow these steps in order.** Full details: `docs/assessment/remediation.md`

| Step | Task | Finding | Owner | Status |
|------|------|---------|-------|--------|
| **1** | Fix Playwright E2E failures (7 tests) | FIND-001 (S1) | Frontend + QA | ⬜ Pending |
| **2** | Extract hardcoded coordinates to config | FIND-002 (S2) | Frontend | ⬜ Pending |
| **3** | Add ErrorBoundary to 2 pages | FIND-003 (S2) | Frontend | ⬜ Pending |
| **4** | Add mypy type annotations | FIND-004 (S3) | Backend | ⬜ Pending |
| **5** | Run critic evaluations (8 personas) | — | QA | ⬜ Pending |
| **6** | Re-assessment | — | QA | ⬜ Pending |
