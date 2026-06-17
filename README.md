# Chicago Pipeline

> End-to-end data platform for the Chicago Crime Database Management System (2024–2026).
> See the [implementation plan](./docs/IMPLEMENTATION_PLAN.md) for the full architecture and design rationale.

[![Stack](https://img.shields.io/badge/stack-Spark%20%7C%20dbt%20%7C%20FastAPI%20%7C%20React-blue)](./docs/IMPLEMENTATION_PLAN.md)
[![Compose](https://img.shields.io/badge/docker-compose-13%20services-2496ED)](./docker-compose.yaml)
[![License](https://img.shields.io/badge/license-MIT-green)](#license)

## What is this?

A portfolio-grade, portfolio-bright data platform that:

1. **Ingests** the [Chicago Crime 2024–2026 Kaggle dataset](https://www.kaggle.com/datasets/aliafzal9323/chicago-crime-dataset-2024-2026) (or a 90-day synthetic seed) into a **Bronze** layer on MinIO.
2. **Cleans and normalises** the data with PySpark + Great Expectations into a **Silver** layer.
3. **Aggregates** the data into a **Gold** layer (curated business aggregates).
4. **Materialises a star-schema warehouse** (PostgreSQL + PostGIS) and a set of dbt **marts** for analytics.
5. **Exposes** 21 HTTP endpoints via a typed FastAPI service.
6. **Visualises** the data in a polished React SPA (Vite + TS + Tailwind + Recharts + MapLibre). 4 pages: Dashboard, Analysis, Crime Types, Locations.
7. **Observes** itself via Prometheus + Grafana + OpenLineage/Marquez.

> **Detailed plan:** [`docs/IMPLEMENTATION_PLAN.md`](./docs/IMPLEMENTATION_PLAN.md)

### Assessment Status

| Metric | Value |
|--------|-------|
| Automated Gates | 100% (32/32) — Grade A |
| Composite Critic Score | 8.39 / 10 — PASS |
| All Personas | ≥ 7.0 (no hard failures) |
| Findings | 0 open (all resolved) |

## Quick start

> Requirements: Docker Desktop (or Docker Engine) with Compose v2.

### Linux / macOS

```bash
# 1. Copy the env template and edit secrets
cp .env.example .env

# 2. Bring up the full stack
make up

# 3. (Optional) Seed 90 days of synthetic data + run the full pipeline
make demo

# 4. Open the dashboard
open http://localhost:5173
```

### Windows (PowerShell)

```powershell
# 1. Copy the env template
Copy-Item .env.example .env

# 2. Bring up the full stack
docker compose up -d --build

# 3. (Optional) Seed 90 days of synthetic data + run the full pipeline
# Generate synthetic CSV on the host (writes to data/chicago_crime_synthetic_90d.csv)
python scripts/seed.py

# Run pipeline stages inside the container
docker compose exec -T spark-master /opt/spark/bin/spark-submit --master spark://spark-master:7077 --py-files /opt/pipeline/src /opt/pipeline/src/chicago_pipeline/bronze/to_bronze.py /data/chicago_crime_synthetic_90d.csv
docker compose exec -T spark-master /opt/spark/bin/spark-submit --master spark://spark-master:7077 --py-files /opt/pipeline/src /opt/pipeline/src/chicago_pipeline/silver/to_silver.py
docker compose exec -T spark-master /opt/spark/bin/spark-submit --master spark://spark-master:7077 --py-files /opt/pipeline/src /opt/pipeline/src/chicago_pipeline/gold/to_gold.py
docker compose exec -T spark-master bash -c "PYTHONPATH=/opt/pipeline/src ENV=local python3 /opt/pipeline/src/chicago_pipeline/warehouse/load_postgres.py"
docker compose exec -T spark-master bash -c "cd /opt/dbt && dbt deps --profiles-dir . && dbt run --profiles-dir . && dbt test --profiles-dir ."

# 4. Open the dashboard
Start-Process http://localhost:5173
```

### Git Bash (Windows alternative)

If you have Git Bash installed, you can use the Linux commands with `MSYS_NO_PATHCONV=1` for Docker paths:

```bash
export MSYS_NO_PATHCONV=1
docker compose up -d --build
```

When the stack is up, these are the entry points (see `make urls`):

| Service | URL | Notes |
|---|---|---|
| React dashboard | http://localhost:5173 | The portfolio centerpiece |
| FastAPI Swagger | http://localhost:8000/docs | 21 routes |
| Airflow UI | http://localhost:8080 | 7 DAGs |
| MinIO Console | http://localhost:9001 | Data lake |
| Grafana | http://localhost:3000 | Pipeline & API health |
| Marquez (lineage) | http://localhost:3001 | End-to-end lineage graph |
| Prometheus | http://localhost:9090 | Metrics |

## Architecture

```
Kaggle CSV  ─►  Bronze (MinIO)  ─GE─►  Silver (MinIO)  ─GE─►  Gold (MinIO)
                                                                  │
                                                                  ▼
                                                dbt marts ◄── Postgres (PostGIS)
                                                                  │
                                                                  ▼
                                                           FastAPI (21 routes)
                                                                   │
                                                                   ▼
                                                           React SPA (4 pages)
```

> Full diagram and per-layer ownership in [`docs/IMPLEMENTATION_PLAN.md`](./docs/IMPLEMENTATION_PLAN.md).

## Repository layout

```
chicago-pipeline/
├── Makefile                       # make up / down / test / pipeline / ...
├── docker-compose.yaml            # 13 services, all with healthchecks
├── docs/                          # architecture, plan, ADRs, runbook
├── contracts/                     # shared, versioned artefacts (the wires)
├── pipeline/                      # PySpark jobs (Bronze/Silver/Gold)
├── dbt/                           # dbt project (warehouse + marts)
├── airflow/                       # 7 DAGs
├── api/                           # FastAPI service
├── web/                           # React SPA
├── observability/                 # Prometheus + Grafana
├── lineage/                       # OpenLineage + Marquez config
└── scripts/                       # healthcheck, validate, seed
```

## Development

### Linux / macOS (with make)

```bash
make up         # start the stack
make health     # show health of all services
make pipeline   # ingest -> silver -> gold -> dbt
make quality    # Great Expectations + dbt tests
make api-test   # pytest (api)
make web-test   # vitest (web)
make web-e2e    # playwright
make lint       # ruff + mypy + eslint + tsc
make contracts-validate  # gate: contracts bus consistent
```

### Windows (PowerShell)

```powershell
# Stack lifecycle
docker compose up -d --build          # start the stack
docker compose ps                     # show running containers
docker compose down                   # stop the stack
docker compose down -v                # destroy volumes and restart fresh

# Health check
bash scripts/healthcheck.sh

# Pipeline (run from host — seed.py generates CSV on host, pipeline runs in container)
python scripts/seed.py                                                            # generate synthetic CSV
docker compose exec -T spark-master /opt/spark/bin/spark-submit --master spark://spark-master:7077 --py-files /opt/pipeline/src /opt/pipeline/src/chicago_pipeline/bronze/to_bronze.py /data/chicago_crime_synthetic_90d.csv
docker compose exec -T spark-master /opt/spark/bin/spark-submit --master spark://spark-master:7077 --py-files /opt/pipeline/src /opt/pipeline/src/chicago_pipeline/silver/to_silver.py
docker compose exec -T spark-master /opt/spark/bin/spark-submit --master spark://spark-master:7077 --py-files /opt/pipeline/src /opt/pipeline/src/chicago_pipeline/gold/to_gold.py
docker compose exec -T spark-master bash -c "PYTHONPATH=/opt/pipeline/src ENV=local python3 /opt/pipeline/src/chicago_pipeline/warehouse/load_postgres.py"
docker compose exec -T spark-master bash -c "cd /opt/dbt && dbt deps --profiles-dir . && dbt run --profiles-dir . && dbt test --profiles-dir ."

# API
docker compose exec -T api pytest -q --cov=app --cov-report=term-missing   # api tests
docker compose exec -T api ruff check app                                   # api lint
docker compose exec -T api mypy app                                         # api typecheck

# Web
docker compose exec -T web pnpm test                                        # unit tests
docker compose --profile test run --rm playwright                           # e2e tests
docker compose exec -T web pnpm lint                                        # web lint
docker compose exec -T web pnpm typecheck                                   # web typecheck

# Contracts
bash scripts/validate_contracts.sh                                          # validate contracts

# Code quality
docker compose exec -T api ruff format app                                  # format api code
docker compose exec -T web pnpm format                                      # format web code
```

### Git Bash (Windows alternative)

```bash
export MSYS_NO_PATHCONV=1
# Then use any of the Linux commands above
docker compose up -d --build
docker compose exec -T api pytest -q
docker compose --profile test run --rm playwright
```

## License

MIT. See `LICENSE`.
