# M6 Test Instructions

## Quick Start

```bash
docker compose down -v
docker compose up -d --build
```

That's it. The `pipeline-init` container automatically runs the full pipeline
(Bronze → Silver → Gold → Postgres → dbt) on every startup. The API starts
immediately (regardless of pipeline-init) but serves `/api/health` only until
the warehouse tables are populated.

**Startup timeline:**
- **0–2 min** — All infrastructure starts (Postgres, MinIO, Redis, Spark, Airflow)
- **2–6 min** — `pipeline-init` runs Bronze → Silver → Gold → Postgres → dbt (53 tests).
  The API and web are already running during this time. The API returns `/api/health/live`
  (200) but data endpoints return errors until the warehouse tables exist.
- **6–7 min** — Fully operational. All charts, maps, and KPIs show real data.

**Important:** The scheduler container (`ccp-airflow-scheduler`) shows `(health: starting)`
for ~2 minutes while Airflow's scheduler registers its first heartbeat. This is normal.
The webserver shows `(healthy)` after ~1 minute.

Monitor progress:
```bash
docker logs -f ccp-pipeline-init
```

You'll see:
```
[1/7] Copying source CSV...
[2/7] Bronze load...
[3/7] Silver transform...
[4/7] Gold transform...
[5/7] Gold → Postgres loader...
[6/7] dbt run...
[7/7] dbt test...
Pipeline init finished successfully
```

Verify everything is up:
```bash
docker compose ps
curl http://localhost:8000/api/health
```
Expected: `{"status":"healthy","checks":{"postgres":true,"redis":true}}`

Open http://localhost:5173 — the dashboard should show real data immediately.

---

## Backend Verification

### 1. Run unit tests (42/42 expected)
```bash
docker exec ccp-api python -m pytest tests/ -q
```
Expected: `42 passed`

### 2. Run lint
```bash
docker exec ccp-api ruff check app
```
Expected: `All checks passed!`

### 3. Verify all 13 data endpoints return 200
```bash
curl http://localhost:8000/api/overview
curl http://localhost:8000/api/heatmap
curl http://localhost:8000/api/geo/clusters
curl http://localhost:8000/api/geo/choropleth?level=district
curl http://localhost:8000/api/crime-types/top
curl http://localhost:8000/api/crime-types/trend?type=THEFT
curl http://localhost:8000/api/arrests/by-district
curl http://localhost:8000/api/arrests/by-type
curl http://localhost:8000/api/context/domestic
curl http://localhost:8000/api/context/location
curl http://localhost:8000/api/filters
curl http://localhost:8000/api/timeseries
curl http://localhost:8000/api/health
```
Expected: All return valid JSON with 200 status.

### 4. Verify filtered endpoints
```bash
curl "http://localhost:8000/api/timeseries?from=2024-06-01&to=2025-12-31&types=THEFT"
curl "http://localhost:8000/api/crime-types/top?from=2024-06-01&to=2025-12-31&types=THEFT"
curl "http://localhost:8000/api/arrests/by-type?from=2024-06-01&to=2025-12-31&types=THEFT"
curl "http://localhost:8000/api/context/domestic?from=2024-06-01&to=2025-12-31&types=THEFT"
curl "http://localhost:8000/api/context/location?from=2024-06-01&to=2025-12-31&types=THEFT"
```
Expected: All return filtered results (smaller totals).

### 5. OpenAPI spec
```bash
curl http://localhost:8000/openapi.json
```
Expected: 21 endpoints documented.

---

## Frontend Verification

### 6. TypeScript type-check
```bash
cd web && npx tsc --noEmit
```
Expected: No errors.

### 7. Unit tests
```bash
cd web && npx vitest run
```
Expected: `2 passed`

### 8. Production build
```bash
cd web && npx vite build
```
Expected: Builds to dist/ without errors.

### 9. Start dev server (optional — skip if using Docker web container)
```bash
cd web && npm run dev
```
Open http://localhost:5173 in browser.

> **Note:** The Docker `web` container runs nginx on port 5173 and proxies
> `/api` → `http://api:8000`. If you run `npm run dev` locally, the Vite
> dev server proxies `/api` → `http://localhost:8000`.

### 10. Dashboard page
- KPI cards show: Total Crimes (57,931), Arrest Rate (18.0%), Domestic % (12.9%), YoY Change (0.0%)
- Timeseries area chart loads with daily data (indigo gradient fill)
- Hourly heatmap shows crime distribution by hour (indigo scale)
- Domestic split donut chart shows 12.9% domestic (rose + indigo ring)
- Offense bar chart shows top crime types (indigo bars)
- Arrest rate bar chart shows rates by district (cyan bars)
- Both maps load with dark basemap (choropleth + cluster)

### 11. Sidebar filters
- Date pickers work (from/to)
- Crime type checkboxes filter data
- Reset button clears all filters
- Charts update when filters change

### 12. Navigation
- Sidebar links: Dashboard, Crime Types, Locations, Analysis
- All pages load without errors
- Crime Types page shows bar charts + sortable table
- Locations page shows dark maps + ranked location list with gradient progress bars
- Analysis page shows stat cards + timeseries + arrest rates + key insights

### 13. Responsive
- Resize browser to < 768px
- Sidebar collapses to mobile menu (hamburger toggle)
- Charts stack vertically on mobile
- Maps resize properly

---

## Troubleshooting

### Pipeline init fails
Check logs:
```bash
docker logs ccp-pipeline-init
```
Common causes:
- MinIO not healthy yet (the `depends_on` should handle this)
- Spark master not ready (wait and retry: `docker compose up -d pipeline-init`)

### API returns 500 / dashboard shows all zeros
The pipeline-init may still be running. Check:
```bash
docker compose ps | grep pipeline-init
```
If it shows `Exited (0)` but API still fails, restart the API:
```bash
docker compose up -d api
```

### Airflow webserver unhealthy
Check logs:
```bash
docker logs ccp-airflow-webserver --tail 30
```
Common causes:
- Missing `command: webserver` in compose (entrypoint shows help and exits)
- DB not initialized (add `_AIRFLOW_DB_MIGRATE: "true"` env var)
- `--hostname` healthcheck flag missing argument (use `--local` instead)

### Web container can't reach API
Verify connectivity from inside the container:
```bash
docker exec ccp-web curl -s http://api:8000/api/health
```
If this returns JSON but `localhost:5173` doesn't work, the nginx proxy is
misconfigured. Check: `docker exec ccp-web cat /etc/nginx/conf.d/default.conf`

### Re-run pipeline manually (without full restart)
```bash
docker exec ccp-spark-master bash -c \
  "cd /opt/pipeline && PYTHONPATH=src python3 -m chicago_pipeline.bronze.to_bronze"
docker exec ccp-spark-master bash -c \
  "cd /opt/pipeline && PYTHONPATH=src python3 -m chicago_pipeline.silver.to_silver"
docker exec ccp-spark-master bash -c \
  "cd /opt/pipeline && PYTHONPATH=src python3 -m chicago_pipeline.gold.to_gold"
docker exec ccp-spark-master bash -c \
  "cd /opt/pipeline && PYTHONPATH=src python3 src/chicago_pipeline/warehouse/load_postgres.py"
docker exec ccp-spark-master bash -c \
  "cd /opt/dbt && dbt run --profiles-dir ."
docker exec ccp-spark-master bash -c \
  "cd /opt/dbt && dbt test --profiles-dir ."
docker compose up -d api
```

---
## Known Limitations

- No JWT auth (public dashboard, auth out of scope)
- Choropleth map uses simplified district positions (real GeoJSON deferred)
- Chunk size warning on build (ECharts+MapLibre bundle ~2.8MB, code splitting deferred)
- Pipeline init runs on every `docker compose up -d` (~2-3 min for full rebuild)
- Airflow scheduler shows `unhealthy` briefly after startup (takes ~90s to register the SchedulerJob)
