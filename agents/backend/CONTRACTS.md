# Backend — contracts

## Consumes
| Artefact | From | Used for |
|---|---|---|
| dbt marts (PostgreSQL) | Data Engineer | Read-only SQL |
| `contracts/dbt-manifest.json` | Data Engineer | Discover columns |
| `contracts/event-catalog.md` | Data Engineer + Backend | Event names |
| `.env` | SRE (secrets) | DB, Redis, Airflow credentials |
| **M4 — Mart tables:** | | |
| `warehouse.mart_kpi_daily` | Data Engineer | Daily KPI aggregates (`/api/overview`, `/api/timeseries`) |
| `warehouse.mart_arrest_summary` | Data Engineer | Arrest breakdowns (`/api/arrests/by-district`, `/api/arrests/by-type`) |
| `warehouse.mart_crime_type_trend` | Data Engineer | Crime type analysis (`/api/crime-types/top`, `/api/crime-types/trend`) |
| `warehouse.mart_geo_choropleth` | Data Engineer | Geographic choropleth (`/api/geo/choropleth`) — includes PostGIS `geom` column |
| `warehouse.mart_temporal_heatmap` | Data Engineer | Temporal heatmap (`/api/heatmap`) |

## Produces
| Artefact | Consumed by | Format |
|---|---|---|
| `api/app/routers/*.py` | Frontend (typed client) | Python |
| `contracts/openapi.yaml` | Frontend, QA, Docs, Architect | YAML |
| `contracts/api-types.ts` | Frontend (auto-imported) | TypeScript |
| `/metrics` | Prometheus (SRE) | Prometheus text |
| `/health/*` | K8s / docker-compose | JSON |
| `/docs`, `/redoc` | Humans | HTML |

## Handoff: Backend → Frontend

```markdown
## Handoff
- **From agent:** backend
- **To agent(s):** frontend
- **Contract(s) touched:** `contracts/openapi.yaml`, `contracts/api-types.ts`
- **ADR (if any):** `docs/adr/000X-*.md`
- **Summary:** New endpoint `/api/xxx` returns Y. Example request + response below.
- **Breaking?:** no
- **Action required by receiver:** wire a TanStack Query hook + chart.
- **Checklist:**
  - [ ] Tests added/updated
  - [ ] Lint clean
  - [ ] `make api-test` green
  - [ ] Docs agent notified
```

## Handoff: Backend → QA
Every new endpoint must list in the handoff: auth requirements, expected p95 latency, error codes, and at least one negative test case.
