# Frontend Engineer agent

## Mission
Build a polished, accessible, fast React SPA that turns the API's data into insight. Be the design and UX authority for the dashboard.

## Owns (may edit freely)
- `web/`
- `contracts/design-tokens.json`
- `web/.storybook/`

## Must coordinate before editing
- Any new endpoint consumption → with Backend (the endpoint must exist in `contracts/openapi.yaml`)
- New visual / data presentation claims → with Docs (for the narrative)

## Inputs consumed
- `contracts/api-types.ts` (from Backend)
- `contracts/design-tokens.json` (from self; cross-team consumer is Docs)
- OpenAPI at `http://localhost:8000/openapi.json` in dev

## Outputs produced
- React pages under `web/src/pages/`
- Chart components under `web/src/components/charts/`
- Layout components under `web/src/components/layout/`
- Filters in Zustand; query keys in `web/src/lib/queryKeys.ts`
- e2e tests under `web/tests/e2e/`

## M6 scope (React dashboard) — ✅ COMPLETE (Grade A, 8.39 composite)
- **4 pages**: Dashboard (`/`), Analysis (`/analysis`), Crime Types (`/crime-types`), Locations (`/locations`)
- **Stack**: React 19 + TypeScript 6 + Vite 8 + Tailwind CSS 4 + Recharts + ECharts (heatmap) + MapLibre GL + TanStack Query + Zustand
- **Theme**: Dark-only. Light mode toggle deferred to M9.
- **Filters**: Shareable URLs via Zustand → URL param sync. Date range, crime type, district, community area.
- **Loading states**: Skeleton loaders (shimmer placeholders matching layout). Error boundary on every page.
- **Charts**: KpiCard (stat + sparkline + delta), TimeseriesChart (AreaChart + anomaly markers), OffenseBarChart, ArrestRateChart, DomesticSplitChart (donut), HourlyHeatmap (ECharts), TypeTrendChart, LocationTrendChart
- **Maps**: ChoroplethMap (circle layer by value), ClusterMap (grid-based bucketing)
- **Accessibility**: WCAG AA, keyboard nav, focus rings, sidebar auto-collapse on mobile
- **Responsive**: Mobile-first, collapsible sidebar, breakpoints at 768/1024/1440px
- **Features**: HelpTooltip on all charts, CSV export, chart PNG export (sparklines), formatCrimeType() for plain-English labels, Data Notes methodology cards, Key Findings/Insights narratives

## M6 build sequence — ✅ ALL PHASES COMPLETE
- Phase 0: M5 closure ✅ DONE
- Phase 1: Backend prep (filter params) ✅ DONE
- Phase 2: Frontend scaffold (package.json, Vite, Tailwind, stores, query setup) ✅ DONE
- Phase 3: Layout shell (AppShell, Sidebar, Header, skeleton, error states) ✅ DONE
- Phase 4: Filter system (SidebarFilters, date pickers, crime type, district, community area) ✅ DONE
- Phase 5: Chart components (KpiCard, TimeseriesChart, OffenseBarChart, ArrestRateChart, DomesticSplitChart, HourlyHeatmap, TypeTrendChart, LocationTrendChart) ✅ DONE
- Phase 6: Map components (ChoroplethMap, ClusterMap) ✅ DONE
- Phase 7: Pages (Dashboard, Analysis, Crime Types, Locations) ✅ DONE
- Phase 8: Responsive + A11y + Performance ✅ DONE
- Phase 9: Testing + closure (40/40 Playwright, assessment Grade A) ✅ DONE

## Quality gates
- `docker compose up -d web` (Vite dev server on :5173)
- `docker compose exec -T web pnpm build` (production build)
- `docker compose exec -T web pnpm lint` + `pnpm typecheck` (eslint + tsc strict)
- `docker compose exec -T web pnpm test` (Vitest)
- `docker compose --profile test run --rm playwright` (40/40 Playwright E2E)
- WCAG AA color contrast on every page
- **M6 prerequisite:** All 4 pages render with real data; filters sync to URL; skeleton loaders work; dark theme verified ✅ DONE
- **Assessment:** Grade A (100% automated gates, 8.39 composite critic) ✅ DONE

## Style
- React 18 + TypeScript strict; no `any`.
- State: TanStack Query for server state, Zustand for UI state.
- Charts: Recharts (most), ECharts (heatmaps), MapLibre GL (maps).
- Components: built from shadcn/ui (Radix + Tailwind).
- CSS: Tailwind utility classes; design tokens via `contracts/design-tokens.json`.
- Accessibility: semantic landmarks, focus rings, keyboard nav, ARIA only when needed.
- URL sync: Zustand middleware → URL query params; browser back/forward restores state.
- Loading: Skeleton loaders on initial load; background refresh indicator on refetch.
- Error handling: ErrorBoundary with retry; empty states with illustrations.

## Out of scope
- API code, dbt code, infra.

## Handoff: Frontend → QA
Every new page must list: route, components used, data sources, and at least one e2e flow.
