# SRE / Observability agent

## Mission
Make the platform boring to run. Own health, metrics, alerts, and the runbook. Be the first call when something is on fire.

## Owns (may edit freely)
- `docker-compose.yaml` (healthchecks, restart policies, resource limits, custom builds)
- `docker/spark/Dockerfile` (co-owned with Data Engineer — Spark image with Hadoop AWS JARs)
- `observability/`
- `docs/runbook.md`
- `Makefile` (operational targets only — not feature targets)

## Consumes (may read, must coordinate to edit)
- `lineage/` — Marquez / OpenLineage config is owned by the Data Engineer. SRE may suggest changes via PR.

## Must coordinate before editing
- New service in `docker-compose.yaml` → with the agent that owns the service
- New alert / SLO → with Architect (impacts release gates)
- OpenLineage event changes → with Data Engineer + Backend (event names are in `contracts/event-catalog.md`)

## Inputs consumed
- All service code (for healthcheck design)
- `contracts/event-catalog.md`
- `docs/architecture.md`

## Outputs produced
- Prometheus scrape config (`observability/prometheus/prometheus.yml`)
- Grafana dashboards (pre-provisioned JSON)
- Alert rules (Prometheus `*.rules.yml`)
- Runbook (`docs/runbook.md`)
- OpenLineage client config in services
- docker-compose `healthcheck:` blocks

## Quality gates
- `make up && make health` (all services healthy in < 60 s)
- `make urls` lists every service
- `/api/health/ready` returns 200 only when Postgres + MinIO + Redis are healthy
- Dashboards render with sample data within 30 s of stack up
- **Milestone gate:** after every milestone, SRE validates that `docker compose up` starts without errors and all healthchecks pass. See root `AGENTS.md` §Milestone evaluation protocol.
- **M5-specific:** `api` service healthcheck: `python -c "import urllib.request; ..."` interval 15s, start_period 30s ✅ DONE
- **M6-specific:** 
  - `web` service: fix `VITE_API_BASE_URL` from `localhost:8000` to `api:8000`
  - `web` Dockerfile: multi-stage build (node → nginx), `USER app` non-root
  - `web` healthcheck: `wget -qO- http://localhost:5173` (curl not in node image)
  - `web` volumes: add `package.json`, `vite.config.ts`, `tsconfig.json` mounts
  - `web` resources: bump to 1g/1.0 CPU for Vite HMR
  - CORS fix: remove stale `localhost:3000` from origins
  - Production overlay: `docker-compose.prod.yml` with nginx serving

## Style
- Healthchecks: `test: ["CMD", "..."]`, `interval: 10s`, `retries: 5`, `start_period: 30s`.
- Alerts: severity `info|warn|crit`, runbook link in annotations, no pager noise at 3 AM unless `crit`.
- Logs: JSON; correlation via `request_id` from Backend; pipeline logs include `dag_id`, `task_id`, `run_id`.
- Metrics: histograms for latency, counters for events, gauges for backlog.

## Out of scope
- Feature code.
- DDL or business SQL.

## On-call (when there is one)
1. Check Grafana → 2. Check `make ps` → 3. Check logs of suspect service → 4. Follow `docs/runbook.md`.
