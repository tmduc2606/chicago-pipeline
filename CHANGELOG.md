# CHANGELOG

All notable changes to the chicago-pipeline project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [0.6.0] - 2026-06-05

### M6 — Frontend Dashboard (FastAPI + React)

This release delivers the complete frontend dashboard layer, converting the
previously headless API into a full-stack application with an interactive
React dashboard, dark-themed UI, real-time data visualization, and Docker
deployment.

---

### Added

#### Frontend Application (27 source files)

- **Project scaffold** — React 19 + TypeScript 6 + Vite 8 + Tailwind CSS 4
  (`web/`).
- **Dark theme** — 25 CSS custom properties defining a professional dark
  palette: `#0a0a0f` background, indigo primary (`#6366f1`), cyan/amber/rose
  accent colors, custom scrollbars, shimmer loading animations, card glow
  effects (`web/src/index.css`).
- **Layout system** — `AppShell` (flex sidebar + header + scrollable main),
  `Sidebar` (collapsible nav with logo badge, 4 nav items with SVG icons),
  `Header` (active filter pills, API health indicator dot)
  (`web/src/components/layout/`).
- **Filter system** — Zustand store (`filters.ts`) with `from`, `to`, `types`,
  `communityAreas` state; `SidebarFilters` component with date pickers, crime
  type checkboxes, and reset button; `filtersToParams()` serializes to
  `URLSearchParams` for API calls (`web/src/stores/filters.ts`,
  `web/src/components/filters/SidebarFilters.tsx`).
- **UI store** — Sidebar collapse state via Zustand (`web/src/stores/ui.ts`).
- **API client** — Typed `fetchJson<T>()` wrapper with all 13 data endpoint
  methods, AbortSignal support, error handling
  (`web/src/lib/api.ts`).
- **Query client** — TanStack Query with 5-minute stale time, 10-minute GC
  time, 2 retries, no refetch on window focus
  (`web/src/lib/queryClient.ts`).
- **Path aliases** — `@/*` maps to `./src/*` in both `tsconfig.json` and
  `vite.config.ts`.

##### Pages (4)

| Page | Route | Description |
|------|-------|-------------|
| `DashboardPage` | `/` | KPI row (4 cards) + timeseries area chart + heatmap + domestic donut + offense bar + arrest rate bar + 2 maps + top locations list |
| `CrimeTypesPage` | `/crime-types` | Horizontal bar charts (count + arrest rate) + sortable table |
| `LocationsPage` | `/locations` | 2 maps (choropleth + cluster) + ranked location list with progress bars |
| `AnalysisPage` | `/analysis` | Stats row + timeseries + arrest rates + key insights bullet list |

##### Chart Components (6)

| Component | Library | Description |
|-----------|---------|-------------|
| `KpiCard` | — | Stat card with glow hover, icon slot, color variants (default/red/green/cyan/amber), skeleton loader |
| `TimeseriesChart` | Recharts | Area chart with dual gradient fills (indigo total, green arrests), dark tooltip, grid |
| `OffenseBarChart` | Recharts | Horizontal bar, primary-type truncation, dark tooltip |
| `ArrestRateChart` | Recharts | Vertical bar, cyan fill, percentage Y-axis |
| `DomesticSplitChart` | SVG | Custom donut ring with animated stroke-dasharray, legend |
| `HourlyHeatmap` | ECharts | 24-column heatmap, indigo gradient scale, dark tooltip |

##### Map Components (2)

| Component | Style | Description |
|-----------|-------|-------------|
| `ChoroplethMap` | CartoDB Dark Matter | Circle layer with interpolated radius by value, hover popup |
| `ClusterMap` | CartoDB Dark Matter | Grid-based bucketing (zoom-aware), orange circle layer |

##### Testing

- Vitest 4.1.8 + jsdom 29.1.1 + React Testing Library
  (`web/vitest.config.ts`, `web/src/test/setup.ts`).
- `KpiCard.test.tsx` — 2 tests: renders title + number format, percent format.

##### Build & Deploy

- `web/Dockerfile` — Multi-stage: `node:20-alpine` builder → `nginx:alpine`
  production; serves on port 5173.
- `web/nginx.conf` — SPA fallback + reverse proxy `/api` → `http://api:8000`
  + `/metrics` → `http://api:8000`.
- `vite.config.ts` — Dev proxy `/api` → `http://localhost:8000`,
  `/metrics` → `http://localhost:8000`.
- `docker-compose.yaml` — Added `web` service with `depends_on: api
  (service_healthy)`, resource limits (256 MB / 0.5 CPU).

#### Backend Filter Parameters

All 8 data endpoints now accept optional filter query parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `from` | `str` | Start date (inclusive), e.g. `2024-01-01` |
| `to` | `str` | End date (inclusive), e.g. `2026-05-31` |
| `types` | `str` | Comma-separated primary types, e.g. `THEFT,BATTERY` |

Endpoints updated:
- `GET /api/overview` (no filter params — returns global KPIs)
- `GET /api/heatmap` (no filter params)
- `GET /api/geo/clusters?from=&to=&types=`
- `GET /api/geo/choropleth?level=&metric=&from=&to=&types=`
- `GET /api/crime-types/top?from=&to=&types=&limit=`
- `GET /api/crime-types/trend?type=&from=&to=`
- `GET /api/arrests/by-district?from=&to=&types=`
- `GET /api/arrests/by-type?from=&to=&types=`
- `GET /api/context/domestic?from=&to=&types=`
- `GET /api/context/location?from=&to=&types=&limit=`
- `GET /api/timeseries?from=&to=&types=`
- `GET /api/filters` (read-only — returns available filter options)

Schema changes:
- `FilterOptions` — added `community_areas: list[int]`
- `ChoroplethBucket` — added `label: str`
- `TimeseriesPoint.arrests` — changed from `int | None = None` to `int = 0`

#### Infrastructure

- **Airflow 2.10.5** — Upgraded from 2.9.3 to resolve transitive dependency
  conflict (`apache-airflow-providers-standard:1.13.1` requires ≥2.11).
- **Airflow healthcheck fix** — Scheduler: changed `--hostname` (missing arg)
  to `--local`.
- **Airflow env vars** — Added `_AIRFLOW_DB_MIGRATE=true`,
  `_AIRFLOW_WWW_USER_CREATE=true`, `_AIRFLOW_WWW_USER_USERNAME`,
  `_AIRFLOW_WWW_USER_PASSWORD` to webserver service.
- **Airflow command** — Added `command: webserver` to webserver service
  (was missing, causing bare `airflow` to show help and exit).

---

### Fixed

- **`asyncpg` date casting** — All service queries changed `WHERE t.date >=
  :from_date` to `WHERE t.date >= :from_date::date` to prevent `'str' object
  has no attribute 'toordinal'` errors. Affected: `services/arrests.py`,
  `services/crime_types.py`, `services/geo.py`, `services/timeseries.py`.
- **`fact_crime.primary_type` does not exist** — `get_arrests_by_type` and
  `get_top_types` referenced `f.primary_type` directly on `fact_crime` instead
  of joining `dim_offense`. Fixed by adding `JOIN dim_offense o ON
  f.offense_id = o.offense_id` and using `o.primary_type`.
- **Lint E501 line too long** — Reformatted multi-line function calls in all
  router files to stay within line limits.
- **Docker-compose YAML duplicate key** — Removed duplicate `web:` service
  block (was defined at both line 269 and line 354).
- **Warehouse data loss** — Airflow 2.10.5 `db migrate` wiped
  `warehouse.*` tables. Re-ran full pipeline M1→M4 to restore: Bronze
  (57,931 rows) → Silver → Gold (5 tables) → Postgres (5 base tables + PKs
  + FKs + indexes + PostGIS) → dbt (12 models, 53 tests).
- **Web container API unreachable** — nginx config pointed to
  `http://api:8000` (Docker DNS) which worked, but the initial build used a
  cached broken Airflow image that prevented the API from starting. Fixed by
  rebuilding the API container after warehouse restore.

---

### Changed

- **TypeScript 6 migration** — Removed deprecated `baseUrl` from
  `tsconfig.json` (TypeScript 7 blocks it); path aliases work via `paths`
  alone.
- **Recharts Tooltip types** — Updated all `Tooltip` `formatter` callbacks to
  accept `string | number | (string | number)[] | undefined` (Recharts 3.x
  union type).
- **MapLibre paint properties** — Removed invalid `circle-stroke` (not in
  circle layer paint spec); replaced with `circle-stroke-color` where needed.
- **GeoJSON types** — Defined local `GeoJSONFeature` type in map components
  instead of referencing the `GeoJSON` namespace (not in `@types/maplibre-gl`).

---

### Known Limitations

- No JWT auth (public dashboard, auth deferred to M9).
- No dark/light mode toggle (dark only, toggle deferred to M9).
- Forecast and anomaly charts — API endpoints exist but not yet visualized.
- Choropleth map uses random district positions (real GeoJSON boundaries
  deferred to M9).
- Chunk size warning on production build (~2.8 MB JS from ECharts + MapLibre;
  code splitting deferred to M9).
- `_build_filter` helper duplicated across `services/arrests.py`,
  `services/geo.py`, and `services/crime_types.py` (DRY refactor deferred).

---

## [0.5.0] - 2026-06-05

### M5 — FastAPI Backend

See prior changelog entries for M5 details (21 endpoints, 42 tests, Redis
caching, CORS, GZip, RequestID middleware, Prometheus instrumentation).

---

## [0.4.0] - 2026-06-05

### M4 — Warehouse (PostGIS + dbt)

Gold→Postgres loader, dbt project (5 staging, 2 intermediate, 5 marts,
53 tests), PostGIS geometry, interactive exploration scripts.

---

## [0.3.0] - 2026-06-04

### M3 — Gold Layer (Spark)

5 Gold tables: `fact_crime`, `dim_time`, `dim_location`, `dim_offense`,
`dim_case`. xxhash64 surrogate keys, GE Gold 12/12 PASS.

---

## [0.2.0] - 2026-06-04

### M2 — Silver Layer (Spark + GE)

Bronze→Silver transform with GE validation (18 suites), schema evolution
tracking, real-time drift detection.

---

## [0.1.0] - 2026-06-03

### M1 — Ingestion → Bronze

Kaggle download, CSV→Parquet Bronze conversion, Airflow DAG.

---

## [0.0.0] - 2026-06-03

### M0 — Skeleton & Docs

Repository skeleton, 58 files, architecture docs, Makefile, Docker Compose.
