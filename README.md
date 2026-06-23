# Canyon - Chicago Crime Pipeline

[![Stack](https://img.shields.io/badge/stack-Spark%20%7C%20dbt%20%7C%20Airflow%20%7C%20MinIO%20%7C%20FastAPI%20%7C%20React-blue)](./docs/IMPLEMENTATION_PLAN.md)
[![Docker Compose](https://img.shields.io/badge/docker--compose-14%20services-2496ED)](./docker-compose.yaml)
[![Release](https://img.shields.io/badge/release-final-success)](./docker-compose.yaml)
[![License](https://img.shields.io/badge/license-MIT-green)](#license)

## Project Overview

An end-to-end data pipeline for the Chicago Crime tracking system that:

1. **Ingests** real Chicago crime data (~52K rows, 2019–2025) into a **Bronze** layer on MinIO.
2. **Cleans and normalises** the data with PySpark + Great Expectations into a **Silver** layer.
3. **Aggregates** the data into a **Gold** layer (curated business aggregates).
4. **Composes into a star-schema warehouse** (PostgreSQL + PostGIS) and a set of dbt **marts** for analytics.
5. **Exposes** 21 HTTP endpoints via a typed FastAPI service.
6. **Visualises** the data in a polished React SPA (Vite + TS + Tailwind + Recharts + MapLibre). 6 pages: Dashboard, Analysis, Crime Types, Locations, Insights, About.
7. **Observes** itself via Prometheus + Grafana + OpenLineage/Marquez.
8. **Dark/light theme** toggle for comfortable viewing.

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

# 3. Seed data (already placed in) + run the full pipeline
# Run the pipeline stages inside the container with the following commands:
docker compose exec -T spark-master /opt/spark/bin/spark-submit --master spark://spark-master:7077 --py-files /opt/pipeline/src /opt/pipeline/src/chicago_pipeline/bronze/to_bronze.py /data/chicago_crime.csv
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

![alt text](https://github.com/tmduc2606/chicago-pipeline/blob/main/reports/DA%20-%20Canyon.drawio.png "DA - Canyon")

## Repository layout

```
chicago-pipeline/
├── Makefile                       # make up / down / test / pipeline / ...
├── docker-compose.yaml            # 13 services, all with healthchecks
├── data/                          # stripped Chicago crime dataset (2019 - 2025)
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

# Pipeline (run from host — place data/chicago_crime.csv first, see data/README.md)
docker compose exec -T spark-master /opt/spark/bin/spark-submit --master spark://spark-master:7077 --py-files /opt/pipeline/src /opt/pipeline/src/chicago_pipeline/bronze/to_bronze.py /data/chicago_crime.csv
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

## FAQ

**Q: Is this real Chicago crime data?**
A: Yes — the pipeline uses a real stratified sample of ~52K rows from the Chicago Crime dataset (2019–2025), sourced from Kaggle. A synthetic fallback is also available via `python scripts/seed.py synthetic`.

**Q: How do I reset the stack to a clean state?**
A: Run `docker compose down -v` to remove all volumes, then `docker compose up -d --build` to rebuild and restart.

**Q: What's the default login for Grafana?**
A: Username: `admin`, Password: `change_me_local` (set in `.env`).

**Q: How many API endpoints are there?**
A: 21 endpoints covering overview, timeseries, geo, crime types, arrests, context, filters, pipeline status, and health checks. See the full list at `http://localhost:8000/docs`.
