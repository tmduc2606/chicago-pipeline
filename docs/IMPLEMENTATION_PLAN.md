# End-to-End Chicago Crime DBMS — Implementation Plan (2024–2026)

> Status: **APPROVED v1.0** — authored 2026-06-03, the project architect agent.
> Scope: an overhaul of the original design in `reports/End-to-end Chicago DBMS.docx` into a portfolio-grade, multi-agent data platform.

---

## Table of Contents

0. [Senior-DE Evaluation of the Original Design](#0-senior-de-evaluation-of-the-original-design)
1. [Revised Target Architecture](#1-revised-target-architecture)
2. [Final Tech Stack (locked)](#2-final-tech-stack-locked)
3. [Repo Structure (target)](#3-repo-structure-target)
4. [Section I — Data Engineering Implementation Plan](#4-section-i--data-engineering-implementation-plan)
5. [Section II — Back-end (FastAPI) Implementation Plan](#5-section-ii--back-end-fastapi-implementation-plan)
6. [Section III — Front-end (React) Implementation Plan](#6-section-iii--front-end-react-implementation-plan)
7. [Section IV — Cross-cutting (DevEx, CI/CD, Multi-agent)](#7-section-iv--cross-cutting-devex-cicd-multi-agent)
8. [Section V — Implementation Milestones](#8-section-v--implementation-milestones)
9. [Section VI — "Shining & Exquisite" Polish Checklist](#9-section-vi--shining--exquisite-polish-checklist)
10. [Open Items](#10-open-items)

---

## 0. Senior-DE Evaluation of the Original Design

### 0.1 What is solid
- Clear **Bronze → Silver → Gold → Warehouse** medallion; mirrors industry norm (Databricks, Snowflake, dbt-Labs).
- **Star schema** with `fact_crime` + 4 dimensions (`dim_time`, `dim_location`, `dim_offense`, `dim_case`) is the right shape; 3NF/BCNF with selective denormalization.
- Open dataset (Kaggle Chicago Crime 2024–2026) → reproducible.
- Airflow + Spark + Docker + Postgres is a credible, modern stack.
- Honest acknowledgment that raw data should not sit in Postgres.

### 0.2 What is weak / risky for a portfolio piece
| # | Issue | Impact | Fix in overhaul |
|---|-------|--------|-----------------|
| 1 | **SeaweedFS** as the object store is uncommon; reviewers prefer MinIO. | Lower credibility. | **Replace with MinIO (S3-compatible).** |
| 2 | **Streamlit** is a script-on-Python; not a SPA. | Looks junior for a 2024–2026 web front-end. | **Replace with FastAPI + React (Vite/TS/Tailwind/shadcn).** |
| 3 | No **data quality** framework. | A senior pipeline has boundary checks. | **Add Great Expectations** at Bronze→Silver and Silver→Gold. |
| 4 | No **dbt** for the semantic/mart layer. | KPI logic ends up in Streamlit, scattered. | **Spark → Silver/Gold Parquet, dbt → dimensional + marts.** |
| 5 | No **CI/CD**, no **tests**, no **observability**. | Doesn't read as "production-shape." | **GitHub Actions, pytest suite, Prometheus + Grafana.** |
| 6 | No **lineage / governance** stub. | Reviewers expect at least a hint. | **OpenLineage + Marquez stub** (lightweight). |
| 7 | KPI catalogue in §III is thin. | A senior piece should show analytical depth. | **Extend** with forecasting, anomaly, hotspot clustering, decomposition. |
| 8 | The "Gold" and "Warehouse" are conflated. | Hard to reason about ownership. | **Gold = curated Parquet; Warehouse = Postgres star schema; Marts = dbt marts on top.** |
| 9 | The docx is the *only* spec; no engineering design doc. | Less professional. | **This plan** + ADRs in `docs/adr/`. |

### 0.3 Net verdict
The bones are right. The overhaul swaps a few choices (MinIO, dbt, GE, React) and adds the senior-DE polish layer (CI/CD, tests, observability, lineage, ADRs, a `Makefile`, a `docker-compose` for the full stack with healthchecks, a `README` that stands alone).

---

## 1. Revised Target Architecture

```
                    ┌──────────────────────┐
                    │  Kaggle CSV (source) │
                    └──────────┬───────────┘
                               │ download (Airflow: ingest_dag)
                               ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │  Bronze  (MinIO: s3a://lake/bronze/chicago_crime/2024..2026/...) │   raw + _ingest_ts
 └──────────────────────────────────────────────────────────────────┘
                               │ Great Expectations checkpoint #1
                               ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │  Silver  (MinIO: s3a://lake/silver/chicago_crime/                │
 │          partitioned by year/month, Parquet, snake_case)         │
 └──────────────────────────────────────────────────────────────────┘
                               │ Great Expectations checkpoint #2
                               ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │  Gold    (MinIO: s3a://lake/gold/chicago_crime/                  │
 │          conformed dimensions + business aggregates)             │
 └──────────────────────────────────────────────────────────────────┘
                               │ dbt seeds + run
                               ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │  Warehouse (PostgreSQL 15 + PostGIS 3.3)                         │
 │    star schema:  fact_crime, dim_time, dim_location,             │
 │                  dim_offense, dim_case                           │
 │    marts:        mart_kpi_daily, mart_arrest_by_district,        │
 │                  mart_hotspot_grid, mart_crime_type_trend        │
 └──────────────────────────────────────────────────────────────────┘
                               │  FastAPI (async)
                               ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │  React SPA  (Vite + TS + Tailwind + shadcn/ui + Recharts +       │
 │              MapLibre + TanStack Query + Zustand)                │
 └──────────────────────────────────────────────────────────────────┘
  Sidecars: Airflow UI · MinIO Console · PGAdmin · Prometheus · Grafana
```

---

## 2. Final Tech Stack (locked)

| Layer | Technology | Version | Why |
|---|---|---|---|
| **Object store** | MinIO | RELEASE.2024-09 | S3-API, well-known |
| **Orchestration** | Apache Airflow | 2.9.x | DAGs + TaskFlow |
| **Batch transform** | Apache Spark | 3.5.x (PySpark) | Bronze/Silver |
| **SQL transform** | dbt-core + dbt-postgres | 1.8.x | Dimensional + marts |
| **Warehouse DB** | PostgreSQL + PostGIS | 16 / 3.4 | Geo + analytics |
| **Data quality** | Great Expectations | 0.18.x | Boundary checks |
| **Lineage** | OpenLineage + Marquez (stub) | 1.x / 0.30 | Lightweight lineage |
| **API** | FastAPI + Uvicorn | 0.111 / 0.30 | Async, OpenAPI |
| **ORM/DB driver** | SQLAlchemy 2.x (async) + asyncpg | latest | Type-safe, fast |
| **Cache** | Redis | 7-alpine | API response cache |
| **Web app** | Vite + React 18 + TypeScript | latest | Modern, fast HMR |
| **UI kit** | shadcn/ui (Radix) + Tailwind | latest | Polished components |
| **Charts** | Recharts + ECharts (heatmaps) + MapLibre GL | latest | Rich viz |
| **State** | TanStack Query + Zustand | latest | Server + client state |
| **Container** | Docker Compose v2 | n/a | One-shot stack |
| **Observability** | Prometheus + Grafana | 2.54 / 11.2 | Pipeline metrics |
| **CI/CD** | GitHub Actions | n/a | Lint/test/build/scan |
| **Auth** | None (public dashboard) | – | Per stakeholder decision |
| **Tests** | pytest + Vitest + Playwright | latest | Multi-layer |
| **Linters** | ruff, mypy, eslint, prettier, black | latest | Consistent code |
| **Pre-commit** | pre-commit hooks | latest | Gate commits |
| **Multi-agent charter** | `AGENTS.md` + `agents/<role>/` | n/a | Repo-wide policy |

---

## 3. Repo Structure (target)

```
chicago-pipeline/
├── README.md                          # landing page for reviewers
├── LICENSE
├── AGENTS.md                          # multi-agent charter (root)
├── Makefile                           # make up / down / test / lint / dbt / spark / pipeline
├── docker-compose.yaml                # full stack
├── .env.example
├── .editorconfig
├── .pre-commit-config.yaml
├── .gitignore
├── CODEOWNERS
├── docs/
│   ├── IMPLEMENTATION_PLAN.md         # this file
│   ├── architecture.md
│   ├── data-model.md                  # ERD, dbt DAG image
│   ├── api.md                         # OpenAPI narrative
│   ├── ui.md                          # design system + page list
│   ├── adr/
│   │   ├── 0001-minio-over-seaweedfs.md
│   │   ├── 0002-spark-then-dbt.md
│   │   ├── 0003-fastapi-react.md
│   │   └── 0004-no-auth-public.md
│   └── runbook.md
├── data/                              # sample CSVs (≤ 1 MB) for local testing
│   └── README.md
│
├── agents/                            # multi-agent spec (see §7)
│   ├── architect/{AGENTS,PROMPT,CONTRACTS}.md
│   ├── data-engineer/{AGENTS,PROMPT,CONTRACTS}.md
│   ├── backend/{AGENTS,PROMPT,CONTRACTS}.md
│   ├── frontend/{AGENTS,PROMPT,CONTRACTS}.md
│   ├── qa/{AGENTS,PROMPT,CONTRACTS}.md
│   ├── sre/{AGENTS,PROMPT,CONTRACTS}.md
│   ├── docs/{AGENTS,PROMPT,CONTRACTS}.md
│   └── security/{AGENTS,PROMPT,CONTRACTS}.md
│
├── contracts/                         # shared, versioned artefacts
│   ├── README.md
│   ├── openapi.yaml
│   ├── dbt-manifest.json
│   ├── api-types.ts
│   ├── event-catalog.md
│   ├── design-tokens.json
│   └── CHANGELOG.md
│
├── pipeline/                          # data engineering work
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── conf/
│   │   ├── base.yaml
│   │   └── local.yaml
│   ├── src/chicago_pipeline/
│   │   ├── __init__.py
│   │   ├── common/
│   │   │   ├── logger.py
│   │   │   ├── s3.py
│   │   │   ├── spark_session.py
│   │   │   ├── db.py
│   │   │   └── settings.py
│   │   ├── ingest/download_kaggle.py
│   │   ├── bronze/to_bronze.py
│   │   ├── silver/to_silver.py
│   │   ├── gold/to_gold.py
│   │   ├── warehouse/
│   │   │   ├── load_postgres.py
│   │   │   └── post_create.sql
│   │   └── quality/
│   │       ├── ge_bronze.py
│   │       └── ge_silver.py
│   ├── tests/
│   │   ├── test_silver_schema.py
│   │   ├── test_gold_aggregates.py
│   │   └── test_postgres_load.py
│   └── great_expectations/
│       ├── great_expectations.yml
│       └── expectations/{bronze,silver}_suite.json
│
├── dbt/                               # dbt project
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── packages.yml
│   ├── models/
│   │   ├── staging/{stg_crime,stg_location,stg_offense}.sql
│   │   ├── intermediate/int_crime_enriched.sql
│   │   ├── marts/
│   │   │   ├── mart_kpi_daily.sql
│   │   │   ├── mart_arrest_by_district.sql
│   │   │   ├── mart_hotspot_grid.sql
│   │   │   ├── mart_crime_type_trend.sql
│   │   │   └── mart_temporal_heatmap.sql
│   │   └── schema.yml
│   ├── macros/
│   ├── seeds/{chicago_community_areas.csv,chicago_districts.csv}
│   └── tests/
│
├── airflow/                           # orchestration
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── dags/
│   │   ├── ingest_dag.py
│   │   ├── bronze_to_silver_dag.py
│   │   ├── silver_to_gold_dag.py
│   │   ├── gold_to_warehouse_dag.py
│   │   ├── dbt_build_dag.py
│   │   ├── data_quality_dag.py
│   │   └── pipeline_healthcheck_dag.py
│   └── plugins/
│
├── api/                               # FastAPI backend
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── settings.py
│   │   ├── deps.py
│   │   ├── db/{base,session,models}.py
│   │   ├── schemas/{crime,kpi,geo,common}.py
│   │   ├── routers/{overview,timeseries,geo,crime_types,arrests,context,filters,pipeline,health}.py
│   │   ├── services/{crime_service,geo_service,forecast_service,cache}.py
│   │   ├── middleware/{request_id,timing}.py
│   │   └── utils/{geo,dates}.py
│   ├── tests/{test_routes,test_schemas,test_geo}.py
│   └── alembic/
│
├── web/                               # React SPA
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   ├── public/{og.png,favicon.svg}
│   ├── src/
│   │   ├── main.tsx, App.tsx, router.tsx
│   │   ├── styles/globals.css
│   │   ├── lib/{api,format,queryKeys,theme}.ts
│   │   ├── components/
│   │   │   ├── ui/                 # shadcn/ui primitives
│   │   │   ├── layout/{AppShell,Sidebar,Topbar,Footer}.tsx
│   │   │   ├── charts/{KpiCard,TrendLine,HeatmapHourDay,TopNBar,Donut,ChoroplethMap,ClusterMap,ForecastBand,AnomalyMarkers}.tsx
│   │   │   ├── filters/{DateRangePicker,CrimeTypeSelect,DistrictSelect,ArrestToggle}.tsx
│   │   │   └── feedback/{Skeleton,EmptyState,ErrorBoundary}.tsx
│   │   ├── pages/{Overview,TimeIntelligence,GeographicInsights,CrimeTypeAnalysis,ArrestEffectiveness,ContextualFactors,DataQuality,PipelineStatus,NotFound}.tsx
│   │   ├── hooks/
│   │   ├── store/
│   │   └── assets/
│   ├── tests/{components,e2e}
│   └── .storybook/
│
├── lineage/                           # OpenLineage + Marquez stub
│   └── README.md
│
├── observability/
│   ├── prometheus/prometheus.yml
│   └── grafana/
│       ├── provisioning/
│       └── dashboards/{pipeline-health,api-latency}.json
│
├── scripts/
│   ├── bootstrap.sh
│   ├── seed.sh
│   ├── run_pipeline.sh
│   └── reset.sh
│
└── .github/
    ├── workflows/{ci.yml,docker-publish.yml,codeql.yml}
    └── PULL_REQUEST_TEMPLATE.md
```

---

## 4. Section I — Data Engineering Implementation Plan

### 4.1 Medallion contract

| Layer | Owner | Format | Partition | Schema policy | Retention |
|---|---|---|---|---|---|
| **Bronze** | Spark (`to_bronze.py`) | CSV/Parquet (as-received) + `_ingest_ts` | `ingest_date=YYYY-MM-DD` | Preserve raw; no transformations except adding metadata. | 30 days |
| **Silver** | Spark (`to_silver.py`) | Parquet (snappy) | `year=YYYY/month=MM` | snake_case, typed, deduped, validated. | 1 year |
| **Gold** | Spark (`to_gold.py`) | Parquet (snake_case) | `year=YYYY` | Conformed to warehouse keys; business aggregates. | Indefinite |
| **Warehouse** | PostgreSQL+PostGIS via dbt | Tables | n/a (indexes only) | Star schema + indexes; PostGIS GIST on `geom`. | Indefinite |
| **Marts** | dbt | Materialized views / tables | n/a | Pure SQL transformations on warehouse; marts feed the API. | Indefinite |

### 4.2 Star schema

```sql
-- Dimensions
dim_case      (case_id PK, case_number UNIQUE, updated_on)
dim_time      (time_id PK, ts, date, day, month, year, hour, weekday, is_weekend)
dim_location  (location_id PK, block, location_description, latitude, longitude,
               x_coordinate, y_coordinate, district, ward, community_area, geom GEOMETRY(Point,4326))
dim_offense   (offense_id PK, iucr UNIQUE, primary_type, description, fbi_code)

-- Fact
fact_crime    (crime_id PK, time_id FK, location_id FK, offense_id FK, case_id FK,
               arrest BOOL, domestic BOOL, beat, fbi_code)

-- Indexes
CREATE INDEX ON fact_crime (time_id);
CREATE INDEX ON fact_crime (location_id);
CREATE INDEX ON fact_crime (offense_id);
CREATE INDEX ON dim_time (date);
CREATE INDEX ON dim_location USING GIST (geom);
```

### 4.3 dbt marts

| Mart | Grain | Used by |
|---|---|---|
| `mart_kpi_daily` | day | Overview KPI cards, trend line |
| `mart_arrest_by_district` | district × day | Arrest page, choropleth |
| `mart_hotspot_grid` | H3 r8 cell | Cluster map |
| `mart_crime_type_trend` | primary_type × month | Crime type page |
| `mart_temporal_heatmap` | weekday × hour | Heatmap page |
| `mart_geo_choropleth` | district (joined to boundary GeoJSON) | Choropleth page |
| `mart_anomalies` | day (z-score > 3) | Anomaly markers |

### 4.4 Airflow DAGs

| DAG | Schedule | Tasks |
|---|---|---|
| `ingest_dag` | `@daily` | `kaggle_download` → `verify_checksum` → `upload_bronze` |
| `bronze_to_silver_dag` | `@daily` after `ingest_dag` | `ge_checkpoint_bronze` → `spark_silver` → `ge_checkpoint_silver` |
| `silver_to_gold_dag` | `@daily` | `spark_gold` |
| `gold_to_warehouse_dag` | `@daily` | `spark_load_staging` → `dbt_run` → `dbt_test` |
| `dbt_build_dag` | manual | `dbt_deps` → `dbt_run` → `dbt_test` → `dbt_docs_generate` |
| `data_quality_dag` | `@hourly` | GE run on Gold Parquet + dbt source freshness |
| `pipeline_healthcheck_dag` | `*/15 * * * *` | Checks all services, alerts via logs |

TaskFlow API + `ExternalTaskSensor` between DAGs.

### 4.5 Data quality gates

**Bronze → Silver** (Great Expectations):
- `id` not null, unique
- `date` parsable, between 2024-01-01 and `now()`
- `latitude`/`longitude` within Chicago bbox
- `primary_type` not null
- Row count ≥ 95 % of source

**Silver → Gold**:
- `iucr` mapped to offense
- `case_number` uniqueness
- `district` in known set
- Spatial join completeness: ≥ 99 % of points inside a community area polygon

**dbt tests**:
- `not_null` on all PKs
- `unique` on all PKs
- `relationships` for FKs
- `accepted_values` for `primary_type`, `district`
- Custom singular test: `assert_no_future_dates.sql`
- Freshness checks on `mart_kpi_daily.max(date)` ≤ 2 days

### 4.6 Observability

- **Prometheus** scrapes:
  - Airflow `exporter` (`:9112`)
  - FastAPI `/metrics`
  - PostgreSQL `pg_exporter` (`:9187`)
  - MinIO `/minio/v2/metrics`
  - Custom pipeline metrics pushed by Spark jobs (via `prometheus_client` in driver)
- **Grafana dashboards** (pre-provisioned JSON):
  - `pipeline-health`: DAG success rate, job duration, last-run timestamps
  - `api-latency`: p50/p95/p99 per route, error rate
  - `db-load`: row counts, index usage, long queries

### 4.7 Lineage

- **OpenLineage** events emitted by Spark (`openlineage-spark`) and dbt (`dbt-ol`).
- **Marquez** (single Docker container) for storage + web UI.
- Lightweight; reviewer can see end-to-end graph.

### 4.8 Acceptance criteria (data engineering)
- `make up && make pipeline` ingests → Silver → Gold → dbt → warehouse, all tests pass.
- All Great Expectations and dbt tests run in CI and on a local `make quality`.
- `make dbt-docs` produces navigable dbt documentation.
- A second run is **idempotent** (no duplicate rows in `fact_crime`).

---

## 5. Section II — Back-end (FastAPI) Implementation Plan

### 5.1 Stack
- **FastAPI 0.111+** (async), **Uvicorn 0.30+**
- **Pydantic v2** (validation, settings)
- **SQLAlchemy 2.x async** + **asyncpg**
- **Alembic** (optional, for non-dbt schema tweaks)
- **Redis 7** (`redis.asyncio`) for response cache (TTL 5 min per route)
- **structlog** for JSON logging
- **prometheus-fastapi-instrumentator** for `/metrics`
- **uv** for fast Python env management
- **ruff** + **mypy** strict

### 5.2 Module layout
Already shown in §3 (`api/app/`). Each router thin → delegates to a `services/` module that holds SQL.

### 5.3 Endpoints

| Method | Path | Returns |
|---|---|---|
| GET | `/api/overview` | KPI bundle: total crimes, arrest rate, domestic %, delta vs previous period |
| GET | `/api/timeseries?granularity=daily\|weekly\|monthly&from&to&types` | `[{"ts": "...", "count": int, "arrests": int}]` |
| GET | `/api/timeseries/forecast?horizon=14&type=` | history + forecast band |
| GET | `/api/timeseries/anomalies?z=3` | `[{"ts": ..., "z": ..., "count": ...}]` |
| GET | `/api/heatmap?from&to&types` | 7×24 matrix |
| GET | `/api/geo/clusters?from&to&types&zoom` | clustered points (H3 cells) |
| GET | `/api/geo/choropleth?level=district\|community_area&metric=count\|arrest_rate` | per-polygon values |
| GET | `/api/crime-types/top?limit=10&from&to` | top N primary types |
| GET | `/api/crime-types/trend?type=...` | monthly trend per type |
| GET | `/api/arrests/by-district?from&to` | per-district arrest rate |
| GET | `/api/arrests/by-type` | per-type arrest rate |
| GET | `/api/context/domestic` | domestic vs not split |
| GET | `/api/context/location` | top location_description |
| GET | `/api/filters` | available filter values |
| GET | `/api/pipeline/status` | last run per DAG (proxies Airflow REST) |
| GET | `/api/pipeline/runs?dag_id=&limit=` | run history |
| GET | `/api/quality/summary` | GE/dbt latest results |
| GET | `/api/health`, `/api/health/ready`, `/api/health/live` | K8s probes |
| GET | `/docs`, `/redoc` | OpenAPI |
| GET | `/metrics` | Prometheus |

### 5.4 Performance practices
- All read endpoints are **pure SQL** against dbt marts; no row-by-row Python.
- **Pagination** (`limit` + `cursor`) on every list endpoint.
- Redis cache keys include query hash; **stale-while-revalidate** with 60 s background refresh.
- Heavy aggregations materialized in dbt.
- `gzip` middleware; CORS allowlist configurable via env.
- p95 target < 300 ms for `/api/overview` and `/api/timeseries` on local stack.

### 5.5 Error model
- Standard `{"error": {"code": "...", "message": "...", "request_id": "..."}}`.
- HTTP 4xx/5xx with proper codes (`404`, `422`, `500`).
- `request_id` propagated to logs and to the SPA (shown in dev overlay).

### 5.6 Testing
- `pytest` + `httpx.AsyncClient` for route smoke tests.
- `factory_boy` + `pydantic` fixtures.
- DB tests run against a **throwaway schema** created per test.
- Coverage target ≥ 80 % on `routers/` and `services/`.

### 5.7 Acceptance criteria
- `make api-up` brings up FastAPI.
- `make api-test` runs the suite green.
- `make api-docs` opens Swagger with all 19 endpoints.
- The SPA can hit every endpoint it needs.

---

## 6. Section III — Front-end (React) Implementation Plan

### 6.1 Design language

- **Theme:** dark by default with a "Chicago" accent palette (deep navy `#0B1F3A`, CTA red `#C8102E`, signal amber `#FFB400`, cool slate `#475569`, plus ECharts categorical palette). Light theme as alternate.
- **Typography:** Inter (UI) + JetBrains Mono (numbers, IDs). Loaded from local `woff2` (no CDN dep).
- **Layout:** persistent **left sidebar** (collapsible) + **top bar** (date range, global filters, theme toggle, last-updated indicator) + **content area** + **footer** (data source, build SHA, dbt run time).
- **Components:** built from shadcn/ui — Button, Card, Tabs, Sheet, Dialog, Tooltip, DropdownMenu, Select, Calendar, Command, Skeleton, Toast.
- **Motion:** subtle — `framer-motion` for KPI delta indicators, page transitions, sidebar collapse.
- **Iconography:** `lucide-react`. Empty states with hand-drawn SVG illustrations in `web/src/assets/`.
- **Accessibility:** WCAG AA color contrast, focus rings, semantic landmarks, keyboard navigation on every chart's data table view.

### 6.2 Pages (extending the docx §III catalogue)

| # | Route | Page | Hero viz | Supporting viz | Docx reference |
|---|---|---|---|---|---|
| 1 | `/` | **Executive Overview** | 4 KPI cards (total, arrest %, domestic %, Δ vs prev period) | trend line + heatmap (weekday×hour) + top-5 crime types | "Executive Crime Overview" |
| 2 | `/time` | **Time Intelligence** | Stacked area trend | 7×24 heatmap; seasonality decomposition; **14-day forecast band**; **anomaly markers** | "Time Intelligence" + extended |
| 3 | `/geo` | **Geographic Insights** | **MapLibre cluster map** of incidents | Choropleth (district OR community area) toggle; arrest vs non-arrest toggle; **H3 hotspot grid** | "Geographic Insights" |
| 4 | `/crime-types` | **Crime Type Analysis** | Top-10 horizontal bar | Multi-line trend per top-5; sankey-like ribbon of type ↔ location-description; per-type KPI card | "Crime Type Analysis" + extended |
| 5 | `/arrests` | **Arrest Effectiveness** | Donut: arrest vs not | Bar by district; bar by primary type; line of arrest rate over time; small-multiple sparklines | "Arrest Effectiveness" |
| 6 | `/context` | **Contextual Factors** | Sunburst: primary_type → description | Domestic vs non-domestic stacked bar; location_description top-15; day-of-week × arrest matrix | "Contextual Factors" |
| 7 | `/quality` | **Data Quality** | Suite results table (GE + dbt) | Pass/fail per check; last-run timestamp; failures drill-down to sample rows | new |
| 8 | `/pipeline` | **Pipeline Status** | DAG run timeline (Gantt) | Airflow DAG list with last 10 runs; dbt run log; S3 storage gauge; PG row counts | new |
| 9 | `*` | 404 themed | – | – | – |

### 6.3 Global filter bar (sticky)
- Date range (Calendar with presets: 7d, 30d, 90d, YTD, all, custom)
- Crime type multi-select (search + chip count)
- District / community area multi-select
- Arrest status toggle (all / arrest / non-arrest)
- Reset button · "Save view" (URL-encoded filters)
- Filters live in **Zustand** and are reflected in URL query string.

### 6.4 Performance practices
- Code-splitting per route (`React.lazy`).
- TanStack Query with **5 min stale time**; prefetch on hover for nav links.
- Charts lazy-load via `IntersectionObserver`; skeletons while loading.
- Map tiles served from a static PMTiles file committed to the repo (~5 MB Chicago community-area boundaries) — no external API key.
- Bundle budget: < 350 kB initial JS, < 80 kB initial CSS.

### 6.5 Testing
- **Vitest** for components (testing-library).
- **Playwright** for 4 e2e flows: `home loads`, `filter changes URL`, `map renders clusters`, `404`.
- **Storybook** (optional, time-permitting) for the chart library.

### 6.6 Acceptance criteria
- `make web-up` brings up the SPA at `http://localhost:5173`.
- All 8 pages render with real data from `/api/*`.
- Light + dark themes work; no contrast violations on any page.
- Lighthouse desktop: Performance ≥ 90, Accessibility ≥ 95, Best Practices ≥ 95.
- A reviewer with zero context can navigate from the README to a populated dashboard in < 5 min.

---

## 7. Section IV — Cross-cutting (DevEx, CI/CD, Multi-agent)

### 7.1 Makefile (root)
```
make up / down / up-lite / ps / logs / health / urls
make pipeline        # ingest → silver → gold → dbt
make spark-bronze / spark-silver / spark-gold
make dbt-deps / dbt-run / dbt-test / dbt-docs
make quality         # GE + dbt tests
make api-up / api-test
make web-up / web-build / web-lint / web-test / web-e2e
make contracts-validate
make agents-lint
make lint / format / test
make reset           # destroy volumes, restart fresh
```

### 7.2 CI/CD (`.github/workflows/ci.yml`)
1. **Lint job:** ruff + mypy (api/pipeline), eslint + tsc (web).
2. **Unit tests:** pytest (api + pipeline), vitest (web).
3. **Contracts job:** `make contracts-validate` (OpenAPI drift, missing agent files, broken references).
4. **Build:** docker buildx for `pipeline`, `api`, `web` images.
5. **Compose validate:** `docker compose config -q`.
6. **Integration smoke:** `make up-lite && make pipeline && make api-test && make web-build`.

### 7.3 Multi-agent collaboration framework

#### 7.3.1 Agent roster (8 + 1 coordinator)

| # | Agent | Sub-folder | Owns | Primary outputs | Decides |
|---|---|---|---|---|---|
| 0 | **Lead Architect** (coordinator) | `agents/architect/` | ADRs, system boundaries, contracts bus, integration reviews | `docs/adr/*`, contract-version bumps, conflict arbitration | Cross-cutting decisions; final say on contract changes |
| 1 | **Data Engineer** | `agents/data-engineer/` | `pipeline/`, `dbt/`, `airflow/`, `great_expectations/`, MinIO layout | PySpark jobs, dbt models + tests, GE suites, DAGs | Schema of Bronze/Silver/Gold; dbt naming; partition keys |
| 2 | **Backend Engineer** | `agents/backend/` | `api/`, contract tests | FastAPI routers, pydantic schemas, SQLAlchemy models, OpenAPI | Endpoint shapes; response shapes; error model |
| 3 | **Frontend Engineer** | `agents/frontend/` | `web/`, Storybook, design tokens | React pages, chart components, hooks, e2e tests | Component API; design tokens; UX patterns |
| 4 | **QA Engineer** | `agents/qa/` | `**/tests/`, `tests/e2e/`, fuzzers, contract tests, coverage gates | pytest + vitest + Playwright suites; coverage reports; quality report | Quality gates; release readiness sign-off |
| 5 | **SRE / Observability** | `agents/sre/` | `observability/`, `docker-compose.yaml` healthchecks, OpenLineage stub, alerting, runbook | Prometheus rules, Grafana dashboards, alerts, `runbook.md` | Health/SLO definitions; alert thresholds |
| 6 | **Docs / Storyteller** | `agents/docs/` | `README.md`, `docs/*`, ADR drafts, demo GIF | Landing-page copy, screenshots, FAQ, CHANGELOG, blog post | Narrative; tone; demo flow |
| 7 | **Security & Compliance** | `agents/security/` | secrets handling, SBOM, Trivy scans, license policy, CODEOWNERS | `.env.example`, `SECURITY.md`, `CODEOWNERS`, `dependabot.yml` | Secret rotation; license whitelist; vuln response |

#### 7.3.2 Per-agent sub-folder shape
Each agent owns three files in its sub-folder:
- `AGENTS.md` — role, scope, authority, owned paths, handoff expectations, style.
- `PROMPT.md` — the system prompt to bootstrap the LLM agent.
- `CONTRACTS.md` — what the agent consumes and produces (in/out artefacts).

Root `AGENTS.md` indexes them and defines global non-negotiables and DoD.

#### 7.3.3 Handoff template
Every cross-agent PR uses the **Handoff Template** (see `AGENTS.md` and `contracts/CHANGELOG.md`).

#### 7.3.4 Contract bus rules
| Contract | Producer | Consumers | Versioning |
|---|---|---|---|
| `openapi.yaml` | Backend | Frontend, QA, Docs | SemVer; PR with red/green diff |
| `dbt-manifest.json` | Data Engineer | Backend, Docs, QA | Regenerated on every dbt run; committed |
| `api-types.ts` | Backend (codegen) | Frontend | Generated; do not hand-edit |
| `event-catalog.md` | Data Engineer + Backend | SRE, Security | Append-only; breaking = ADR |
| `design-tokens.json` | Frontend | Docs | JSON; semver |

Breaking contract change = ADR + both producer & consumer sign-off + migration note in `contracts/CHANGELOG.md`.

#### 7.3.5 Collaboration patterns
1. **Vertical slice (default):** Architect issues a slice → Data Engineer exposes a mart → Backend wraps an endpoint → Frontend renders a chart → QA verifies → Docs publishes.
2. **Contract-first:** Producer proposes a contract → Architect reviews → all consumers ack → implementation follows.
3. **Spike:** Any agent may request a spike PR (label `spike`); exempt from DoD but produces a one-page memo in `docs/spikes/`.
4. **Hotfix:** Security or SRE cuts a hotfix branch with a single reviewer; full DoD waived, follow-up issue within 48 h.

#### 7.3.6 Acceptance criteria (multi-agent layer)
- All 8 sub-agent `AGENTS.md` files exist and reference their `PROMPT.md` and `CONTRACTS.md`.
- Root `AGENTS.md` is the single entry point.
- `contracts/openapi.yaml` is auto-generated and committed; CI fails on drift.
- `contracts/CHANGELOG.md` has at least one entry per release.
- Every PR that touches > 1 owned sub-tree uses the Handoff Template and lists an Architect reviewer.

### 7.4 Observability + secrets
- `.env.example` is committed; `.env` is git-ignored.
- All services read secrets from env vars; no hard-coded credentials.
- Optional **Grafana alerting** webhook stub left in `observability/grafana/`.

---

## 8. Section V — Implementation Milestones

Every milestone (M0–M9) follows the same four-phase cycle. **No milestone is considered complete until all four phases pass.**

| Phase | Duration (suggested) | Deliverables |
|---|---|---|
| **M0. Skeleton & docs** | 0.5 d | Repo structure, `Makefile`, `docker-compose.yaml` (services + healthchecks), `.env.example`, `README.md`, `AGENTS.md` + 8 sub-agent files, `contracts/`, ADRs 0001–0004, `CODEOWNERS`. |
| **M1. Ingestion → Bronze** | 0.5 d | `pipeline/ingest/download_kaggle.py`, `pipeline/bronze/to_bronze.py`, `ingest_dag`. |
| **M2. Bronze → Silver (Spark + GE)** | 1 d | `to_silver.py`, GE suite, `bronze_to_silver_dag`. |
| **M3. Silver → Gold (Spark)** | 0.5 d | `to_gold.py`, `silver_to_gold_dag`. |
| **M4. Warehouse (Postgres + dbt)** | 1.5 d | Star schema DDL, dbt project, 6 marts, `dbt_build_dag`, dbt tests. |
| **M5. API (FastAPI)** | 1.5 d | All 22 endpoints, schemas, services, Redis cache, health checks, tests, OpenAPI. |
| **M6. Web (React)** | 2.5 d | AppShell, dark theme, 9 pages + About + 404, all charts, skeleton loaders, filters (URL-synced), responsive layout, tests, Lighthouse pass. |
| **Phase 2: EDA** | | |
| **M7. EDA Layer** | 2 d | EDA notebooks, interactive exploration, 3-layer hierarchy (baseline→intermediate→advanced), insight reports, visualization catalog. New agents: EDA Lead, EDA Researcher. |
| **M8. Agentic AI** | 2 d | Natural language query interface, insight synthesis, LLM integration (open-source API agents, local lightweight LLMs). New agent: LLM Integration. |
| **Phase 3: Production** | | |
| **M9. Production Hardening** | 1.5 d | Auth (optional JWT/API key for admin), Prometheus + Grafana dashboards, light mode toggle, production Docker Compose, README rewrite, GIF/screenshots, demo script, final review pass. |
| **Total** | **~14 working days** | |

### UI/UX decisions (locked)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Landing page | Separate (`/`) | Hero moment + navigation hub; avoids redundancy |
| Pipeline/Quality routes | Behind `/admin` | Operational concerns, cleaner IA |
| 9th page | About/Data Sources/Methodology | Trust signal for crime data |
| Theme (M6) | Dark-only | Modern dashboard standard; light mode toggle deferred to M9 |
| Filter URLs | Shareable (Zustand → URL params) | Enables bookmarkable insights, portfolio showcase |
| Mobile strategy | Responsive-first (shadcn Sheet) | 90% coverage; dedicated layout deferred to P2 |
| Prefetch | Hover-based only | Preserves code-splitting, respects performance budget |
| Heatmap library | ECharts | Native 7×24 matrix, hover tooltips |
| "View as table" | KPIs + top-N bars + arrest rates | Skip on heatmap, choropleth, forecast |
| Error details | Dev mode only | `NODE_ENV === 'development'` shows stack trace |
| Bundle analysis | Yes (rollup-plugin-visualizer) | Zero-cost, portfolio screenshot |
| High contrast mode | Skip (WCAG AA sufficient) | P2 if needed |
| Performance monitoring | Yes (web-vitals) | Trivial to add |
| Sparklines in KPIs | Yes | Mini Recharts Line inside Card |
| Filter position | Top bar (always visible) | No slide-out panel |
| Filter chips | Yes | Active filter badges |
| Loading pattern | Skeleton loaders | Shimmer placeholders matching layout |
| Global connection indicator | Yes (green/red dot) | |
| Screen reader KPIs | `aria-live="polite"` | Announce when numbers change |
| Colorblind patterns | Yes (hatching/dots) | |
| Colorblind palette testing | Yes | |

### Per-milestone cycle

Each milestone completes when:

1. **Implement** — owning agent(s) produce the deliverables.
2. **Evaluate & debug** — QA agent runs all checks (lint, tests, contract validation, structural checks, agent spec, security scan). Bug-fix PR if needed.
3. **User test** — QA agent publishes `docs/milestones/MN-test.md` with numbered commands, expected output, and pass/fail criteria. User verifies before proceeding.
4. **Improvements** — Architect and QA propose improvements (label `improvement/milestone-N`); documented for later milestones or M9 polish.

### Gate rule
**M(N+1) does not start until M(N) user test instructions have been executed and the user has confirmed the milestone.**

See root `AGENTS.md` §Milestone evaluation protocol for the full spec.

### Agent practices

- **Look-and-Feel Update Catalogue**: After all important features work, set up focusing on animations, optimality and eligibility.
- **QoL & Look-and-Feel Cumulative Catalogue**: Maintained after each successful implementation and major debugging phases.
- **Assessment**: Frequent end-to-end evaluation with tests on features. Hotfixes must completely resolve issues retaining across past to current stages.

---

## 9. Section VI — "Shining & Exquisite" Polish Checklist (the bar)

- [ ] `make up && make pipeline` works on a clean machine (Docker only, no global Python deps).
- [ ] `README.md` has: hero GIF of dashboard, architecture diagram, "5-minute quick start", screenshots of every page, badge strip, FAQ.
- [ ] No console errors or React warnings on any page.
- [ ] No `print`, no `TODO`, no commented-out code in main branches.
- [ ] Every chart has hover tooltips with formatted numbers (K, %, locale).
- [ ] Every page has a "What am I looking at?" expandable section (analyst-friendly).
- [ ] Empty/loading/error states everywhere.
- [ ] All endpoints paginated and rate-limited (60 rpm/IP via slowapi).
- [ ] OpenAPI docs link in the SPA footer → opens in new tab.
- [ ] `make demo` script seeds 90 days of synthetic data so the dashboard is populated even before a real run.
- [ ] `/api/health/ready` returns 200 only when Postgres + MinIO + Redis are healthy.
- [ ] GitHub Actions: green badge in README.
- [ ] Two ADRs in `docs/adr/` for every non-obvious decision.

---

## 10. Open Items

Locked-in by stakeholder:
- MinIO (S3) over SeaweedFS
- Batch only (no Kafka streaming path)
- Spark (Silver) + dbt (Gold/marts) as the transform engines
- Vite + React + TS + Tailwind + shadcn/ui + Recharts + ECharts (heatmap only)
- Great Expectations as data quality framework
- Docker Compose only (no K8s)
- No auth (public dashboard) — admin routes behind `/admin` (no auth for M5/M6)
- Dark-only theme for M6; light mode toggle deferred to M9
- Shareable filter URLs (Zustand → URL params)
- Responsive-first mobile strategy

Confirmed:
1. **Demo data**: generate 90 days of synthetic-but-realistic Chicago crime data so the dashboard is populated from first run. ✅ Done (57,931 rows).
2. **Map tiles**: use MapLibre + a static PMTiles file (no API key) for choropleth. ✅ Locked.
3. **Forecasting**: exponential smoothing in SQL (no Python ML dependency). ✅ Locked.
4. **Geo clustering**: H3 r8 (~150 m cells). ✅ Locked.
5. **CI**: GitHub Actions. ✅ Locked.
6. **License**: MIT. ✅ Locked.

---

*End of plan — execute M0 next. M5 (FastAPI) begins after M4 user confirmation.*
