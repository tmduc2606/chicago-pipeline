# Architecture

> Authored by the **Architect** agent. Reviewed by the **Data Engineer** and **Backend** agents.

## Agent ownership table

Every top-level directory has exactly one owning agent. Other agents may read freely, but any change must be authored (or co-authored) by the owner.

| Directory | Owner | Notes |
|---|---|---|
| `pipeline/` | Data Engineer | PySpark jobs, configs, tests |
| `dbt/` | Data Engineer | dbt project, models, seeds, tests |
| `airflow/` | Data Engineer | DAGs (SRE co-owns `docker-compose.yaml` healthchecks) |
| `great_expectations/` | Data Engineer | GE suites, checkpoints |
| `lineage/` | Data Engineer | OpenLineage + Marquez config (SRE consumes) |
| `api/` | Backend Engineer | FastAPI service, tests, alembic |
| `web/` | Frontend Engineer | React SPA, Storybook, tests |
| `observability/` | SRE | Prometheus, Grafana, alerts |
| `contracts/` | Architect (orchestration) | Individual files produced by their respective agents |
| `docs/` | Docs Agent | Architecture, runbook, UI, data-model; ADRs drafted by Docs, signed by Architect |
| `docs/adr/` | Architect (sign-off) | Docs drafts; Architect is the gatekeeper |
| `scripts/` | SRE (operational) / Architect (cross-cutting) | Healthchecks, validation, seed |
| `scripts/notebooks/` | EDA Lead / EDA Researcher | EDA notebooks, analysis cells |
| `reports/eda/` | EDA Lead | Insight reports, index |
| `tests/` | QA Engineer | All test suites |
| `.github/` | Security (dependabot, codeql) + QA (ci.yml) | CI/CD config |
| `data/` | Data Engineer | Sample data, README |
| `agents/` | Architect | Charter, per-agent rules |
| `web/src/config/viz-catalog.yaml` | EDA Lead | Chart registry |
| `web/src/config/insights.json` | EDA Lead | Aggregated insight entries |

## System diagram

```
Kaggle CSV  ──►  Bronze (MinIO)  ──GE──►  Silver (MinIO)  ──GE──►  Gold (MinIO)
                                                                     │
                                                                     ▼
                                                   dbt marts ◄── Postgres (PostGIS)
                                                                     │
                                                                     ▼
                                                         FastAPI (19 routes)
                                                                     │
                                                                     ▼
                                                         React SPA (9 pages)
                                                                     │
                                                                     ▼
                                                         EDA Layer (10 analyses)
                                                          │              │
                                                          ▼              ▼
                                                  Insight Reports   InsightsPage
```

## Key decisions

See `docs/adr/` for all architecture decision records. Summary:

| ADR | Decision | Status |
|---|---|---|
| 0001 | MinIO over SeaweedFS for the data lake | Accepted |
| 0002 | Spark for Silver, dbt for Gold / marts | Accepted |
| 0003 | FastAPI + React replacing Streamlit | Accepted |
| 0004 | Public dashboard (no authentication) | Accepted |
