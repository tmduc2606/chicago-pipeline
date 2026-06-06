# M6 Cumulative Overhaul — React Dashboard Plan

**Date:** 2026-06-05
**Scope:** Full M6 React dashboard (9 pages + About + 404)
**Status:** DRAFT — awaiting user verification
**Reviewers:** All 8 agents (Architect, Backend, Frontend, QA, SRE, Data Engineer, Docs, Security)

---

## Executive Summary

M5 (FastAPI) is complete with 42/42 tests passing and all 19 data endpoints returning 200. However, the multi-agent review uncovered **6 critical gaps**, **8 high-priority items**, and **12 medium-priority items** that must be addressed before or during M6. The `web/` directory is currently empty (placeholder README only) — the entire React frontend must be scaffolded from scratch.

**Key finding:** The filter system is the #1 risk. 8 of 21 API endpoints lack filter parameters, and the `FilterOptions` schema is missing `community_areas`. Without these fixes, the dashboard will show unfiltered data on most pages.

---

## Part 1: Where Adjustments Could Be Made

### CRITICAL — Blocks M6 Start

| # | Issue | Owner | Impact |
|---|-------|-------|--------|
| C1 | **M5 gate not formally closed** — No `docs/milestones/M5-test.md` exists. Per root AGENTS.md gate rule, M6 cannot begin until M5 user test instructions are executed and confirmed. | Backend + QA | Blocks M6 start |
| C2 | **Filter parameter drift** — 8 of 21 endpoints lack `from`/`to`/`types` filter params. Dashboard will show unfiltered data on geo, arrests, context, heatmap pages. | Backend | Breaks filter sync contract |
| C3 | **Heatmap endpoint accepts no params** — `/api/heatmap` has zero query parameters. Heatmap is hero viz on 3 pages (Overview, Time, Context). | Backend | Heatmap ignores all filters |
| C4 | **FilterOptions missing `community_areas`** — Schema only returns `date_min`, `date_max`, `primary_types`, `districts`. M6 rubric requires community area filter. | Backend | Filter bar incomplete |
| C5 | **`web/` directory is empty** — No `package.json`, no `Dockerfile`, no source code. The entire React app must be scaffolded. | Frontend | No M6 deliverable exists |
| C6 | **`VITE_API_BASE_URL` uses localhost** — `docker-compose.yaml:276` passes `http://localhost:8000` but container-to-container needs `http://api:8000`. | SRE | API unreachable from web container |

### HIGH — Fix During M6 Phase 1

| # | Issue | Owner | Fix |
|---|-------|-------|-----|
| H1 | **CORS overly permissive** — `allow_methods=["*"]` and `allow_headers=["*"]`. Also `localhost:3000` is Grafana, not frontend. | Security | Lock to `["GET", "OPTIONS"]` and `["Content-Type", "X-Request-ID"]` |
| H2 | **Healthcheck fragile** — `curl` may not exist in Node image. | SRE | Use `wget` or Node-based probe |
| H3 | **No CSP headers** — FastAPI sets no Content-Security-Policy. | Security | Add CSP middleware |
| H4 | **web/Dockerfile missing** — Multi-stage build needed (Node build → nginx production). | SRE + Frontend | Create Dockerfile |
| H5 | **`docker-compose.yaml` web volumes incomplete** — Missing `package.json`, `vite.config.ts`, `tsconfig.json` mounts for hot-reload. | SRE | Add missing volume mounts |
| H6 | **No resource limits tuned for Vite** — 512m may be tight for HMR. | SRE | Bump to 1g/1.0 CPU for dev |
| H7 | **TimeseriesPoint.arrests optional** — Frontend will get NaN on arrest rate charts if arrests is null. | Backend | Make `arrests` required with default 0 |
| H8 | **ChoroplethBucket.key is string** — Districts are integers (1-25). Frontend must convert for GeoJSON matching. | Backend | Add `label` field or change type |

### MEDIUM — Fix During M6 Phase 2-3

| # | Issue | Owner | Fix |
|---|-------|-------|-----|
| M1 | README stale — says "19 endpoints" and "8 pages" | Docs | Update to 21 endpoints, 11 pages |
| M2 | No nginx for production serving | SRE | Add `docker-compose.prod.yml` overlay |
| M3 | No `VITE_SOURCEMAP=false` in prod | Frontend | Set in Dockerfile |
| M4 | `ward` not exposed in choropleth API | Backend | Add to `ALLOWED_GROUP_COLS` |
| M5 | No rate limiting on API | Security | Add `slowapi` middleware |
| M6 | FAQ missing in README | Docs | Add 8+ anticipated questions |
| M7 | No `docs/milestones/M6-test.md` | QA | Create before M6 closure |
| M8 | No `docs/milestones/M6-improvements.md` | QA + Architect | Create before M6 closure |
| M9 | CHANGELOG M6 section missing | Docs | Add comprehensive entry |
| M10 | `docs/architecture.md` says "8 pages" | Docs | Update to 11 |
| M11 | Source maps in production bundle | Security | Disable via env var |
| M12 | Secret-leak CI check missing | Security | Add grep step to CI |

---

## Part 2: Revised M6 Plan

### Phase 0: M5 Closure (Prerequisite)

| Task | Owner | Duration |
|------|-------|----------|
| Create `docs/milestones/M5-test.md` with 14-section verification | Backend | 0.5h |
| User executes M5 test instructions and confirms | User | 0.5h |
| Architect records M5 sign-off | Architect | 5min |

### Phase 1: Backend Prep (Before Frontend Integration)

| Task | Owner | Duration |
|------|-------|----------|
| Add `from`/`to`/`types` filter params to 8 endpoints | Backend | 1h |
| Add `community_areas` to FilterOptions schema | Backend | 15min |
| Make `TimeseriesPoint.arrests` non-null (default 0) | Backend | 10min |
| Add `label` field to ChoroplethBucket | Backend | 10min |
| Fix CORS: lock methods/headers, remove localhost:3000 | Backend | 10min |
| Regenerate `contracts/api-types.ts` | Backend | 5min |
| Add `from`/`to`/`types` to `/api/heatmap` | Backend | 30min |
| Add `from`/`to`/`types` to `/api/crime-types/trend` | Backend | 15min |

### Phase 2: Frontend Scaffold

| Task | Owner | Duration |
|------|-------|----------|
| Create `web/package.json` with all dependencies | Frontend | 15min |
| Create `web/vite.config.ts` with aliases, chunks, proxy | Frontend | 15min |
| Create `web/tailwind.config.ts` mapping design-tokens.json | Frontend | 30min |
| Create `web/tsconfig.json` (strict) | Frontend | 5min |
| Create `web/Dockerfile` (multi-stage: node → nginx) | Frontend + SRE | 30min |
| Create `web/src/main.tsx`, `App.tsx`, `routes.tsx` | Frontend | 30min |
| Create Zustand stores: `filterStore` (URL sync), `uiStore` | Frontend | 45min |
| Create TanStack Query setup: `queryKeys.ts`, API client | Frontend | 30min |
| Fix `docker-compose.yaml` web service definition | SRE | 15min |

### Phase 3: Layout Shell

| Task | Owner | Duration |
|------|-------|----------|
| `AppShell.tsx` — TopBar + Sidebar + content grid | Frontend | 1h |
| `Sidebar.tsx` — nav items, icons, active state, Sheet/Collapsible | Frontend | 1h |
| `TopBar.tsx` — page title + filter slot + ConnectionDot | Frontend | 30min |
| `ConnectionDot.tsx` — green/red pulse from `/api/health/live` | Frontend | 15min |
| `DashboardSkeleton.tsx` — shimmer placeholders | Frontend | 30min |
| `ErrorBoundary.tsx` — catch + retry | Frontend | 15min |
| `EmptyState.tsx` — welcome + no-results variants | Frontend | 15min |
| `NotFound.tsx` — 404 themed | Frontend | 15min |

### Phase 4: Filter System

| Task | Owner | Duration |
|------|-------|----------|
| `FilterBar.tsx` — orchestrates all filter controls | Frontend | 45min |
| `DateRangePicker.tsx` — Calendar + Popover + presets | Frontend | 30min |
| `CrimeTypeFilter.tsx` — Command searchable multi-select | Frontend | 30min |
| `DistrictFilter.tsx` — multi-select checkboxes | Frontend | 20min |
| `ArrestStatusFilter.tsx` — toggle group | Frontend | 10min |
| `ActiveFilters.tsx` — chips/badges | Frontend | 15min |
| URL sync verification — Zustand → query params → browser back/forward | QA | 30min |

### Phase 5: Chart Components

| Task | Owner | Duration |
|------|-------|----------|
| `KpiCard.tsx` — stat + sparkline + delta + aria-live | Frontend | 45min |
| `ChartCard.tsx` — wrapper with "View as table" toggle | Frontend | 30min |
| `TrendChart.tsx` — Recharts AreaChart + gradient | Frontend | 45min |
| `HeatmapChart.tsx` — ECharts wrapper (7×24 matrix) | Frontend | 1h |
| `HorizontalBar.tsx` — Recharts BarChart vertical | Frontend | 30min |
| `GroupedBar.tsx` — Recharts multi-Bar | Frontend | 30min |
| `DonutChart.tsx` — Recharts PieChart inner radius | Frontend | 30min |
| `DataTable.tsx` — TanStack Table + sorting + pagination | Frontend | 45min |
| `ForecastChart.tsx` — Area + ReferenceArea band | Frontend | 30min |
| `AnomalyChart.tsx` — ReferenceDot overlay | Frontend | 20min |

### Phase 6: Map Components

| Task | Owner | Duration |
|------|-------|----------|
| Download Chicago boundaries PMTiles (~5 MB) | Frontend | 10min |
| `ChoroplethMap.tsx` — MapLibre + PMTiles + fill layer | Frontend | 1.5h |
| `ClusterMap.tsx` — MapLibre + H3 hex + circle layer | Frontend | 1h |
| Layer order: basemap → choropleth → clusters → popups | Frontend | 30min |

### Phase 7: Pages

| # | Page | Route | Hero Viz | Supporting Viz | Duration |
|---|------|-------|----------|----------------|----------|
| 1 | Landing | `/` | Hero KPI | Quick links to 6 sections | 30min |
| 2 | Overview | `/overview` | 4 KPI cards + sparklines | Trend + Heatmap + top-5 bar | 1h |
| 3 | Time | `/time` | Multi-line trend | Heatmap + forecast + anomalies | 1h |
| 4 | Geo | `/geo` | Cluster map | Choropleth toggle | 1h |
| 5 | Crime Types | `/crime-types` | Top-10 horizontal bar | Multi-line per type | 45min |
| 6 | Arrests | `/arrests` | Donut | District bar + type bar + trend | 45min |
| 7 | Context | `/context` | Domestic donut | Location bar + day heatmap | 45min |
| 8 | Pipeline | `/admin/pipeline` | DAG status cards | Run history table | 30min |
| 9 | Quality | `/admin/quality` | GE summary | dbt results | 30min |
| 10 | About | `/about` | Static content | — | 15min |

### Phase 8: Responsive + A11y + Performance

| Task | Owner | Duration |
|------|-------|----------|
| Mobile pass: test 375px, 768px, 1024px, 1440px | Frontend | 1h |
| Keyboard navigation audit | Frontend + QA | 30min |
| `aria-live="polite"` on KPI cards verification | QA | 15min |
| Colorblind palette testing (simulators) | QA | 15min |
| Bundle analysis with rollup-plugin-visualizer | Frontend | 15min |
| Lighthouse CI: Perf ≥ 90, A11y ≥ 95 | QA | 30min |

### Phase 9: Testing + Closure

| Task | Owner | Duration |
|------|-------|----------|
| Vitest: 15-20 component tests | Frontend | 1h |
| Playwright: 4 e2e flows | QA | 1h |
| `docs/milestones/M6-test.md` | QA | 30min |
| `docs/milestones/M6-improvements.md` | QA + Architect | 15min |
| CHANGELOG.md M6 section | Docs | 15min |
| README.md updates (page count, FAQ) | Docs | 30min |
| Demo screenshots/GIFs | Frontend + Docs | 30min |
| `gitleaks detect` on all new files | Security | 5min |
| QA sign-off | QA | 5min |
| Architect sign-off | Architect | 5min |

---

## Part 3: Component Architecture

### File Structure
```
web/
├── Dockerfile                    # Multi-stage: node → nginx
├── package.json
├── pnpm-lock.yaml
├── vite.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── postcss.config.js
├── public/
│   ├── chicago-boundaries.pmtiles  # ~5 MB
│   └── favicon.ico
├── src/
│   ├── main.tsx                   # Entry point
│   ├── App.tsx                    # Router + providers
│   ├── routes.tsx                 # Route config array
│   ├── index.css                  # Tailwind imports
│   ├── lib/
│   │   ├── queryKeys.ts           # TanStack Query key factory
│   │   ├── api.ts                 # Fetch wrapper
│   │   └── utils.ts               # cn(), formatNumber(), etc.
│   ├── stores/
│   │   ├── filterStore.ts         # Zustand + URL sync
│   │   └── uiStore.ts             # Sidebar, connection status
│   ├── hooks/
│   │   ├── useOverview.ts         # TanStack Query hooks
│   │   ├── useTimeseries.ts
│   │   ├── useGeo.ts
│   │   ├── useCrimeTypes.ts
│   │   ├── useArrests.ts
│   │   ├── useContext.ts
│   │   ├── useFilters.ts
│   │   └── usePipeline.ts
│   ├── pages/
│   │   ├── LandingPage.tsx
│   │   ├── OverviewPage.tsx
│   │   ├── TimePage.tsx
│   │   ├── GeoPage.tsx
│   │   ├── CrimeTypesPage.tsx
│   │   ├── ArrestsPage.tsx
│   │   ├── ContextPage.tsx
│   │   ├── PipelinePage.tsx
│   │   ├── QualityPage.tsx
│   │   ├── AboutPage.tsx
│   │   └── NotFoundPage.tsx
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppShell.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── TopBar.tsx
│   │   │   └── ConnectionDot.tsx
│   │   ├── charts/
│   │   │   ├── KpiCard.tsx
│   │   │   ├── ChartCard.tsx
│   │   │   ├── TrendChart.tsx
│   │   │   ├── HeatmapChart.tsx
│   │   │   ├── HorizontalBar.tsx
│   │   │   ├── GroupedBar.tsx
│   │   │   ├── DonutChart.tsx
│   │   │   ├── ForecastChart.tsx
│   │   │   ├── AnomalyChart.tsx
│   │   │   └── EChartsWrapper.tsx
│   │   ├── maps/
│   │   │   ├── ChoroplethMap.tsx
│   │   │   └── ClusterMap.tsx
│   │   ├── filters/
│   │   │   ├── FilterBar.tsx
│   │   │   ├── DateRangePicker.tsx
│   │   │   ├── CrimeTypeFilter.tsx
│   │   │   ├── DistrictFilter.tsx
│   │   │   ├── ArrestStatusFilter.tsx
│   │   │   └── ActiveFilters.tsx
│   │   └── ui/
│   │       ├── DashboardSkeleton.tsx
│   │       ├── EmptyState.tsx
│   │       ├── ErrorBoundary.tsx
│   │       ├── NotFound.tsx
│   │       ├── ServiceUnavailable.tsx
│   │       └── DataTable.tsx
│   └── assets/
│       └── empty-state.svg
└── tests/
    ├── e2e/
    │   ├── landing.spec.ts
    │   ├── filter-url-sync.spec.ts
    │   ├── geo-map.spec.ts
    │   └── not-found.spec.ts
    └── components/
        ├── KpiCard.test.tsx
        ├── FilterBar.test.tsx
        ├── Sidebar.test.tsx
        └── ChartCard.test.tsx
```

### Zustand Store Design

```typescript
// filterStore.ts — URL-synced
interface FilterState {
  dateRange: { from: string | null; to: string | null };
  crimeTypes: string[];
  districts: number[];
  arrestStatus: 'all' | 'arrest' | 'non-arrest';
  communityAreas: number[];
  setDateRange: (range) => void;
  setCrimeTypes: (types) => void;
  setDistricts: (districts) => void;
  setArrestStatus: (status) => void;
  setCommunityAreas: (areas) => void;
  reset: () => void;
}

// URL sync middleware: zustand/middleware → useQuery → URL params
// Key: ?from=2024-01-01&to=2024-03-31&types=THEFT,BATTERY&districts=1,2&arrest=all
```

### TanStack Query Key Factory

```typescript
export const queryKeys = {
  all: ['filters'] as const,
  overview: (filters) => ['overview', filters] as const,
  timeseries: (filters, granularity) => ['timeseries', filters, granularity] as const,
  forecast: (horizon) => ['forecast', horizon] as const,
  anomalies: (z) => ['anomalies', z] as const,
  heatmap: (filters) => ['heatmap', filters] as const,
  clusters: (filters, zoom) => ['clusters', filters, zoom] as const,
  choropleth: (filters, level, metric) => ['choropleth', filters, level, metric] as const,
  crimeTypesTop: (filters, limit) => ['crimeTypesTop', filters, limit] as const,
  crimeTypeTrend: (filters, type) => ['crimeTypeTrend', filters, type] as const,
  arrestsByDistrict: (filters) => ['arrestsByDistrict', filters] as const,
  arrestsByType: () => ['arrestsByType'] as const,
  domestic: (filters) => ['domestic', filters] as const,
  locations: () => ['locations'] as const,
  filters: () => ['filterOptions'] as const,
  pipeline: () => ['pipeline'] as const,
  quality: () => ['quality'] as const,
} as const;
```

### Docker Compose Web Service (Fixed)

```yaml
  web:
    build:
      context: ./web
      dockerfile: Dockerfile
      target: development
    container_name: ccp-web
    depends_on:
      api:
        condition: service_healthy
    environment:
      VITE_API_BASE_URL: http://api:8000
    ports:
      - "5173:5173"
    volumes:
      - ./web/src:/opt/web/src
      - ./web/public:/opt/web/public
      - ./web/package.json:/opt/web/package.json:ro
      - ./web/vite.config.ts:/opt/web/vite.config.ts:ro
      - ./web/tsconfig.json:/opt/web/tsconfig.json:ro
    deploy:
      resources:
        limits:
          memory: 1g
          cpus: "1.0"
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:5173"]
      interval: 15s
      timeout: 5s
      retries: 5
      start_period: 60s
    restart: unless-stopped
```

---

## Part 4: Updated Agent Responsibilities

### Backend Engineer (M6 additions)
- Add filter params (`from`, `to`, `types`) to 8 endpoints before Phase 2
- Extend `FilterOptions` schema with `community_areas`
- Make `TimeseriesPoint.arrests` non-null
- Add `label` field to `ChoroplethBucket`
- Regenerate `contracts/api-types.ts` after changes
- Fix CORS origins and methods

### Frontend Engineer (M6 scope)
- Scaffold entire React app from scratch (Phase 2)
- Build 7 reusable chart components, 2 map components, 5 filter components
- Build 11 pages with real API data
- Implement URL-synced filter system
- Achieve Lighthouse Perf ≥ 90, A11y ≥ 95
- Create web/Dockerfile (multi-stage)
- Write 15-20 Vitest tests

### QA Engineer (M6 additions)
- Verify M5 gate closure
- Create `docs/milestones/M6-test.md`
- Run Playwright 4 flows
- Lighthouse CI verification
- Filter URL sync testing
- Mobile responsive verification (375px, 768px, 1024px, 1440px)

### SRE (M6 additions)
- Fix docker-compose.yaml web service (API URL, volumes, healthcheck, resource limits)
- Create web/Dockerfile review
- Add nginx config for production serving
- Verify healthcheck works in Node image

### Data Engineer (M6 additions)
- Verify all 5 marts support M6 page requirements
- Consider adding date-aware `mart_crime_type_trend_ts` if needed
- Expand FilterOptions data source

### Docs (M6 additions)
- Update README.md (page count, endpoint count, FAQ)
- Update `docs/architecture.md` React layer
- Add CHANGELOG.md M6 section
- Capture demo screenshots/GIFs

### Security (M6 additions)
- Fix CORS methods/headers
- Add CSP headers to FastAPI
- Add secret-leak CI check
- Verify web/Dockerfile runs non-root

### Architect (M6 additions)
- Enforce M5 gate before M6 start
- Write ADR for `/admin` route visibility
- Review all contract changes
- Record M6 sign-off

---

## Part 5: Risk Register

| # | Risk | Probability | Impact | Mitigation |
|---|------|-------------|--------|------------|
| R1 | Filter parameter drift causes unfiltered data on dashboard | High | Critical | Backend adds filter params to all endpoints in Phase 1 |
| R2 | M5 gate delays M6 start | Medium | High | Backend produces M5-test.md immediately |
| R3 | ECharts integration issues (not React-native) | Medium | Medium | Isolated wrapper component, fallback to Recharts |
| R4 | PMTiles file too large or incompatible | Low | Medium | Use GeoJSON fallback (~2 MB) |
| R5 | Lighthouse score below target | Medium | High | Code-split per route, lazy-load maps, virtual scroll |
| R6 | Mobile responsive breaks on edge cases | Medium | Low | Responsive-first with Tailwind breakpoints |
| R7 | Vite dev server memory pressure in Docker | Low | Medium | Bump to 1g memory limit |

---

## Part 6: Recommended Build Sequence

```
M5 Closure → Backend Prep → Frontend Scaffold → Layout Shell → Filters →
Charts → Maps → Pages → Responsive → A11y → Performance → Testing → Closure
```

**Critical path:** M5 Closure → Backend Filter Params → Frontend Scaffold → Filter System → Pages

**Parallel work possible:**
- Backend filter params (Phase 1) can overlap with Frontend scaffold (Phase 2)
- Chart components (Phase 5) can overlap with Map components (Phase 6)
- Testing (Phase 9) starts as soon as first page is complete

---

## Part 7: Acceptance Criteria (M6 DoD)

- [ ] All 11 pages render with real data from `/api/*`
- [ ] Filter URL-sync works (date range, crime type, district, arrest status)
- [ ] Skeleton loaders display on initial load
- [ ] Dark theme verified across all pages
- [ ] Error boundary catches API failures and shows retry UI
- [ ] Empty states render when filters return zero results
- [ ] `make web-build` produces bundle < 350 kB JS, < 80 kB CSS
- [ ] `make web-lint` (eslint + tsc strict) passes
- [ ] `make web-test` (Vitest) passes with ≥ 70% component coverage
- [ ] `make web-e2e` (Playwright, 4 flows) passes
- [ ] Lighthouse: Perf ≥ 90, A11y ≥ 95, Best Practices ≥ 95
- [ ] Mobile responsive at 375px, 768px, 1024px, 1440px
- [ ] `aria-live="polite"` announces KPI changes
- [ ] No console errors or React warnings
- [ ] CORS origins correct (no stale localhost:3000)
- [ ] web/Dockerfile runs as non-root
- [ ] No `VITE_.*PASSWORD` or `VITE_.*SECRET` in source
- [ ] CHANGELOG.md M6 section written
- [ ] README.md updated (page count, endpoint count, FAQ)
- [ ] `docs/milestones/M6-test.md` written and executed
- [ ] `docs/milestones/M6-improvements.md` written
- [ ] QA agent signs off
- [ ] Architect sign-off recorded

---

## Approval

- [ ] Architect — review and approve M6 Cumulative Overhaul
- [ ] Backend Engineer — confirm filter param changes feasible
- [ ] Frontend Engineer — confirm scaffold timeline
- [ ] QA — confirm test strategy
- [ ] SRE — confirm Docker changes
- [ ] User — verify and approve M6 plan
