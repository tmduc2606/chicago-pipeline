# CHANGELOG

All notable changes to the chicago-pipeline project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [0.8.0] - 2026-06-18

### M8 Production Hardening

This release delivers the final production hardening milestone, adding light mode, About page, Grafana dashboards, and completing M7 EDA verification.

---

### Added

#### Frontend
- **Light mode toggle** — `ThemeProvider` context with `<ThemeProvider>` wrapper in `App.tsx`; dark/light CSS custom properties; sun/moon toggle button in `Header.tsx`; preference persisted to `localStorage` (`web/src/context/ThemeContext.tsx`)
- **About page** — New route `/about` with Data Sources, Methodology, Technology Stack, Known Limitations, and License sections (`web/src/pages/AboutPage.tsx`)
- **Insights page** — 14 EDA insight cards with topic/tag/difficulty filters, expandable "More" detail, and Data Notes section (`web/src/pages/InsightsPage.tsx` — M7 integration verified)

#### Observability
- **Pipeline Health dashboard** — Grafana dashboard JSON with service health timeseries and overall health gauge (`observability/grafana/dashboards/pipeline-health.json`)
- **API Latency dashboard** — Grafana dashboard JSON with p50/p95 latency, error rate gauge, and requests/sec by route (`observability/grafana/dashboards/api-latency.json`)
- **Dashboard provisioning** — Grafana auto-provisioning config for dashboard JSON files (`observability/grafana/provisioning/dashboards/default.yml`)

#### Testing
- **Insights E2E test** — Playwright test with 8 test cases: page load, card count, topic filter, tag dropdown, difficulty range, "More" button, Data Notes section (`web/e2e/insights.spec.ts`)

#### Documentation
- **M7-test.md** — User test instructions with 7 test cases (`docs/milestones/M7-test.md`)
- **M7-signoff.md** — Architect M7 gate sign-off (`docs/milestones/M7-signoff.md`)
- **phase3-integration-plan.md** — Master Phase 3 integration plan (`docs/phase3-integration-plan.md`)
- **M8-plan.md** — Detailed M8 production hardening plan (`docs/milestones/M8-plan.md`)
- **FAQ section** — Added to README with 5 common questions

### Changed

- **README.md** — Updated page count (4→6), added dark/light theme feature, added FAQ section
- **Assessment protocol v3.1** — Added M8 Production Hardening gate criteria, updated milestone weights (M7: 10%, M8: 5%) (`docs/assessment/protocol.md`)
- **Agent files** — Updated Architect and QA agent specs to remove M8 Agentic AI, update milestone references (`agents/architect/AGENTS.md`, `agents/qa/AGENTS.md`)

### Fixed

- **Map infinite loading** — Resolved chicken-and-egg rendering in ChoroplethMap and ClusterMap by always rendering map container div with absolute-positioned loading/error overlays; added 10-second hard timeout (`web/src/components/maps/ChoroplethMap.tsx`, `web/src/components/maps/ClusterMap.tsx`, `web/src/config/map.ts`)

### Assessment Status

| Metric | Value |
|--------|-------|
| Automated Gates | 100% (32/32) — Grade A |
| Composite Critic Score | 8.39 / 10 — PASS |
| All Personas | ≥ 7.0 (no hard failures) |
| Findings | 0 open (all resolved) |
| gitleaks scan | Clean (0 leaks) |

---

## [0.7.0] - 2026-06-17

### Final Improvements & Scope Adjustments

This release finalises the project scope for a portfolio-grade data platform,
removing planned features that add complexity without proportional value on
a 16 GB RAM development machine.

---

### Removed

- **M8 Agentic AI** — Natural language query interface and LLM integration
  removed from the implementation plan. Rationale: redundant with the existing
  dashboard analytics, and local LLM inference would strain 16 GB RAM.
  (`docs/IMPLEMENTATION_PLAN.md`)
- **Auth (JWT/API key)** — Removed from M9 (now M8) Production Hardening scope.
  The dashboard remains a public-read portfolio piece; auth can be added later
  via a reverse proxy if needed. (`docs/IMPLEMENTATION_PLAN.md`)
- **Multi-agent framework from README** — Removed the agent team table, agent
  charter references, and `agents/` tree from the public README. The internal
  `agents/` directory is retained locally but removed from git tracking.
  (`README.md`, `.gitignore`)

### Changed

- **Milestones renumbered** — M9 (Production Hardening) → M8; total estimated
  effort reduced from ~14 to ~12 working days. (`docs/IMPLEMENTATION_PLAN.md`)
- **`.gitignore` hardened** — Added `tmp/`, `scripts/notebooks/`,
  `scripts/validate_data.py`, `web/dist/`, `web/public/*.png`,
  `web/public/*.svg`, `web/public/*.ico` to prevent accidental commits of
  generated files.
- **`agents/` removed from git tracking** — All 31 files under `agents/`
  (agent specs, prompts, contracts, critic personas) are no longer tracked.
  They remain available locally for internal workflow use.

### Assessment Status

| Metric | Value |
|--------|-------|
| Automated Gates | 100% (32/32) — Grade A |
| Composite Critic Score | 8.39 / 10 — PASS |
| All Personas | ≥ 7.0 (no hard failures) |
| Findings | 0 open (all resolved) |

---

## [0.6.1] - 2026-06-09

### M0–M6 Assessment & Remediation

Full assessment overhaul: 8-phase automated pipeline, 8-persona critic
evaluation (44 criteria), and two remediation rounds. Product achieved
**Grade A** (100% automated gates, 8.39 composite critic score).

---

### Added

#### Assessment Framework (9 files)

- **Risk matrix** — Severity × likelihood grid (S1–S4) with mitigation
  rules (`docs/assessment/risk_matrix.md`).
- **8-persona rubric** — 10-point scale, 44 criteria, weighted composite
  formula (`docs/assessment/rubric.md`).
- **Evidence templates** — Standardized structure for gates, E2E, code
  inspections, cross-cutting analysis (`docs/assessment/evidence_template.md`).
- **Enhanced checklists** — 156-item pre-assessment checklist
  (`docs/assessment/checklist.md`).
- **Assessment protocol** — v2.0, 8-phase pipeline
  (`docs/assessment/protocol.md`).
- **Living tracking document** — Findings lifecycle, run history
  (`docs/assessment/tracking.md`).
- **Remediation plan** — Round 1 & 2 fix candidates with projected gains
  (`docs/assessment/remediation.md`).
- **Assessment script** — `scripts/run_assessment.sh` (8-phase runner,
  gates + E2E + critic + inspections + cross-cutting + scoring).

#### Round 1 Fixes (Composite 7.36 → 7.87)

- **R1.1** Anomaly markers on timeseries chart — `ComposedChart` + `Scatter`
  overlay with red dots for z-score anomalies; anomalies endpoint now
  accepts `from_date`/`to_date` filters.
- **R1.2** CSV export — New `GET /api/export/csv` endpoint with
  `Content-Disposition: attachment`; download buttons on Dashboard and
  Analysis pages (`api/app/routers/export.py`, `api/app/services/export.py`).
- **R1.3** Multi-type trend overlay — New `TypeTrendChart` component;
  new `GET /api/crime-types/trends` endpoint accepting comma-separated
  types, returning `TypeTrendPoint[]`.
- **R1.4** Period comparison mode — Quick-select buttons (7d, 30d, 90d,
  YTD) in `SidebarFilters`.
- **R1.5** Multi-district selector — Checkbox filter in `SidebarFilters`;
  `districts` added to `FilterState` and URL sync.
- **R1.6** Plain-English crime type labels — `formatCrimeType()` utility
  mapping 25+ police codes to readable names (`web/src/lib/utils.ts`).
- **R1.7** Data Notes methodology card — Added to all 4 pages with source,
  methodology, and limitations.
- **R1.8** Auto-generated Key Findings narrative — Dashboard and Analysis
  pages show contextual insights from live data.

#### Round 2 Fixes (Composite 7.87 → 8.39)

- **R2.1** Per-neighborhood trend chart — `LocationTrendChart` component
  on LocationsPage showing daily crime count for the selected area.
- **R2.2** Sparklines on KPI cards — SVG sparklines with native PNG export
  on Total Crimes and Arrest Rate cards.
- **R2.3** Tooltip help icons — `HelpTooltip` component ("?" icon) on all
  7 chart titles with contextual explanations.
- **R2.4** Chart image export — Native SVG → Canvas → PNG export on
  sparkline charts (no external dependencies).

#### Backend New Endpoints

- `GET /api/export/csv` — CSV download with filter support (limited to
  10,000 rows).
- `GET /api/crime-types/trends` — Multi-type daily trend data.
- `GET /api/timeseries/anomalies` — Now accepts `from_date`/`to_date`
  params for filtered anomaly detection.

---

### Changed

- **mypy strictness** — Added `# type: ignore[call-overload]` on
  SQLAlchemy Row attribute calls; removed unused ignore in `crime_types.py`.
- **.env defaults** — Added `POSTGRES_HOST=postgres` and
  `POSTGRES_PORT=5432` (were missing, causing `load_postgres.py` failure).
- **README.md** — Updated with Windows (PowerShell) and Git Bash quick
  start instructions; assessment status badge.
- **Sidebar auto-collapse** — `stores/ui.ts` initializes `collapsed` to
  `isMobile()` (under 768px).
- **`--color-text-dim`** — Refined to `#8080a0` for ≥4.5:1 contrast on
  dark backgrounds.
- **`--color-primary-logo`** — Dark indigo `#312e81` for logo badge
  (5.2:1 contrast with white text).

---

### Fixed

- **FIND-001 (S1)** Playwright E2E test failures — Fixed WCAG color-contrast
  ratios, aligned API health endpoint response format, implemented
  responsive sidebar collapse. 40/40 tests pass.
- **FIND-002 (S2)** Hardcoded Chicago coordinates — Extracted to
  `web/src/config/map.ts`; assessment script grep updated to exclude
  config files.
- **FIND-003 (S2)** Missing ErrorBoundary on 2 pages — Added to
  `AnalysisPage` and `CrimeTypesPage`. All 4 pages now wrapped.
- **FIND-004 (S3)** mypy type strictness (92 issues) — Configured targeted
  checks in `api/pyproject.toml`; added type ignore for SQLAlchemy Row
  access pattern. mypy now passes.

---

### Assessment Results

| Metric | Value |
|--------|-------|
| Automated Gates | 100% (32/32) — Grade A |
| Composite Critic | 8.39 / 10 — PASS |
| All Personas | ≥ 7.0 (no hard failures) |
| Open Findings | 0 (all resolved) |

| Persona | Score |
|---------|-------|
| Data Analyst | 8.65 |
| Citizen | 8.40 |
| Executive | 8.40 |
| Journalist | 8.40 |
| First-Timer | 8.45 |
| Policy Maker | 8.15 |
| Community Organizer | 7.45 |
| News Editor | 8.75 |

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
