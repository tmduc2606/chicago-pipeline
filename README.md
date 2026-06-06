# Chicago Pipeline

> End-to-end data platform for the Chicago Crime Database Management System (2024–2026).
> Built and maintained by a multi-agent LLM team — see [`AGENTS.md`](./AGENTS.md) and the [implementation plan](./docs/IMPLEMENTATION_PLAN.md).

[![Stack](https://img.shields.io/badge/stack-Spark%20%7C%20dbt%20%7C%20FastAPI%20%7C%20React-blue)](./docs/IMPLEMENTATION_PLAN.md)
[![Compose](https://img.shields.io/badge/docker-compose-12%20services-2496ED)](./docker-compose.yaml)
[![License](https://img.shields.io/badge/license-MIT-green)](#license)

## What is this?

A portfolio-grade, portfolio-bright data platform that:

1. **Ingests** the [Chicago Crime 2024–2026 Kaggle dataset](https://www.kaggle.com/datasets/aliafzal9323/chicago-crime-dataset-2024-2026) (or a 90-day synthetic seed) into a **Bronze** layer on MinIO.
2. **Cleans and normalises** the data with PySpark + Great Expectations into a **Silver** layer.
3. **Aggregates** the data into a **Gold** layer (curated business aggregates).
4. **Materialises a star-schema warehouse** (PostgreSQL + PostGIS) and a set of dbt **marts** for analytics.
5. **Exposes** 19 HTTP endpoints via a typed FastAPI service.
6. **Visualises** the data in a polished React SPA (Vite + TS + Tailwind + shadcn/ui + Recharts + MapLibre).
7. **Observes** itself via Prometheus + Grafana + OpenLineage/Marquez.

> **Detailed plan:** [`docs/IMPLEMENTATION_PLAN.md`](./docs/IMPLEMENTATION_PLAN.md) · **Multi-agent charter:** [`AGENTS.md`](./AGENTS.md)

## Quick start

> Requirements: Docker Desktop (or Docker Engine) with Compose v2.

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

When the stack is up, these are the entry points (see `make urls`):

| Service | URL | Notes |
|---|---|---|
| React dashboard | http://localhost:5173 | The portfolio centerpiece |
| FastAPI Swagger | http://localhost:8000/docs | 19 routes |
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
                                                          FastAPI (19 routes)
                                                                  │
                                                                  ▼
                                                          React SPA (8 pages)
```

> Full diagram and per-layer ownership in [`docs/IMPLEMENTATION_PLAN.md`](./docs/IMPLEMENTATION_PLAN.md).

## Repository layout

```
chicago-pipeline/
├── AGENTS.md                      # multi-agent charter (root)
├── Makefile                       # make up / down / test / pipeline / ...
├── docker-compose.yaml            # 12 services, all with healthchecks
├── docs/                          # architecture, plan, ADRs, runbook
├── agents/                        # 8 specialised LLM agents
│   ├── architect/
│   ├── data-engineer/
│   ├── backend/
│   ├── frontend/
│   ├── qa/
│   ├── sre/
│   ├── docs/
│   └── security/
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

## Multi-agent team

This repo is built by a team of eight specialised LLM agents. Each one owns a sub-tree, has its own rules of engagement, and hands off work through the [`contracts/`](./contracts/README.md) bus. See [`AGENTS.md`](./AGENTS.md) for the full charter.

| Agent | Role | Owns |
|---|---|---|
| **Architect** | Coordinator | `docs/adr/`, `contracts/` orchestration, conflict resolution |
| **Data Engineer** | Pipeline | `pipeline/`, `dbt/`, `airflow/`, `great_expectations/`, `lineage/` |
| **Backend** | API | `api/`, `contracts/openapi.yaml`, `contracts/api-types.ts` |
| **Frontend** | UI | `web/`, `contracts/design-tokens.json` |
| **QA** | Quality | all `tests/`, CI test stages, release sign-off |
| **SRE** | Operations | `docker-compose.yaml` healthchecks, `observability/`, `docs/runbook.md` |
| **Docs** | Storyteller | `README.md`, `docs/`, `CHANGELOG.md`, demo GIF |
| **Security** | Compliance | `.env.example`, `SECURITY.md`, `CODEOWNERS`, dep scanning |

## Development

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
make agents-lint         # gate: every agent has 3 files
```

## License

MIT. See `LICENSE`.
