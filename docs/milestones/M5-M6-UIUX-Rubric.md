# Chicago Crime Dashboard — UI/UX Design Rubric

**Created:** 2026-06-05
**Updated:** 2026-06-05 (finalized after Senior DE review)
**Purpose:** Lock all UI/UX decisions before M5 (FastAPI) & M6 (React) implementation
**Status:** APPROVED

---

## 1. Dashboard Layout & Navigation

| Decision | Options | Final Choice |
|----------|---------|-------------|
| **Sidebar behavior** | Persistent / Collapsible / Auto-hide | **Collapsible** (icons on tablet, full on desktop) |
| **Sidebar position** | Left / Right | **Left** (standard for data dashboards) |
| **Top bar contents** | Filters only / Filters + Breadcrumb / Filters + Title | **Global filters + page title** |
| **Content grid** | Fixed-width / Fluid / Container-query-based | **Fluid with max-width 1440px** |
| **Page transitions** | None / Fade / Slide | **Fade (200ms, standard easing)** |
| **Footer** | None / Minimal / Status bar | **Minimal — pipeline status indicator + last updated** |

---

## 2. Information Architecture — 9 Pages + 404

| # | Route | Page | Hero Viz | Supporting Viz | Key Question Answered |
|---|-------|------|----------|----------------|----------------------|
| 1 | `/` | **Landing** | Hero KPI (total crimes, arrest rate, last updated) | Quick links to 6 sections | "What is this dashboard?" |
| 2 | `/overview` | **Executive Overview** | 4 KPI cards with sparklines | Trend line + heatmap (weekday×hour) + top-5 crime types | "What's happening right now?" |
| 3 | `/time` | **Time Intelligence** | Multi-line trend chart | 7×24 heatmap; 14-day forecast band; anomaly markers | "How are crimes trending?" |
| 4 | `/geo` | **Geographic Insights** | MapLibre cluster map | Choropleth toggle (district/community_area) | "Where are crimes concentrated?" |
| 5 | `/crime-types` | **Crime Type Analysis** | Top-10 horizontal bar | Multi-line trend per top-5 types | "What types of crimes are most common?" |
| 6 | `/arrests` | **Arrest Effectiveness** | Donut (arrest vs not) | Bar by district; bar by type; arrest rate over time | "How effective are arrests?" |
| 7 | `/context` | **Contextual Factors** | Domestic split donut | Top location_description bar; day-of-week heatmap | "What context surrounds crimes?" |
| 8 | `/admin/pipeline` | **Pipeline Status** | DAG status cards | Run history table | "Is the pipeline healthy?" |
| 9 | `/admin/quality` | **Data Quality** | GE pass/fail summary | dbt test results | "Is the data trustworthy?" |
| 10 | `/about` | **About** | Data sources, methodology, limitations | Static content | "Where does this data come from?" |
| 11 | `*` | **404** | Themed illustration | Link back to Landing | "Page not found" |

### Decisions

- [x] **Separate Landing page** (not Overview) — hero moment + navigation hub, avoids redundancy
- [x] **Pipeline/Quality behind `/admin`** — operational concerns, cleaner IA, add auth later without refactoring
- [x] **9th page: About/Data Sources/Methodology** — trust signal for crime data (source, freshness, methodology, limitations)

---

## 3. Chart Types & Visualization Matrix

| Data Domain | Chart Type | Library | Interaction | "View as Table" |
|-------------|------------|---------|-------------|-----------------|
| **KPI cards** | Stat tile + sparkline | Recharts (mini Line) | Hover → exact value | **Yes** |
| **Crime trend** | Area chart | Recharts `AreaChart` | Tooltip, zoom, legend toggle | **Yes** |
| **Forecast** | Area + confidence band | Recharts `AreaChart` + `ReferenceArea` | Hover → forecast value | No |
| **Anomalies** | Scatter overlay on trend | Recharts `ReferenceDot` | Click → anomaly details | **Yes** |
| **Heatmap (hour×day)** | ECharts `heatmap` | **ECharts** | Hover → count | No |
| **Choropleth** | Filled polygon map | MapLibre GL JS | Hover → popup, click → drill | No |
| **Cluster map** | H3 hex clusters | MapLibre GL JS | Hover → count, zoom → expand | No |
| **Top N crime types** | Horizontal bar | Recharts `BarChart` layout="vertical" | Click → filter to type | **Yes** |
| **Arrest by district** | Grouped bar | Recharts `BarChart` | Hover → arrest rate | **Yes** |
| **Domestic split** | Donut chart | Recharts `PieChart` | Hover → count + % | No |
| **Top locations** | Horizontal bar | Recharts `BarChart` | Hover → count | No |
| **Crime type trend** | Multi-line | Recharts `LineChart` | Legend toggle, tooltip | No |

### Decisions

- [x] **Sparklines inside KPI cards** (mini Recharts Line + big number + delta indicator)
- [x] **ECharts for heatmap** — native 7×24 matrix, hover tooltips, color gradients; Recharts for all other charts
- [x] **"View as table" toggle** on: KPI cards, trend area, anomaly scatter, top-N bars, arrest bars only. Skip on: heatmap, choropleth, forecast, donut, location bars, multi-line

---

## 4. Global Filter System

| Filter | Component | Options | Default |
|--------|-----------|---------|---------|
| **Date range** | shadcn `Calendar` + `Popover` | Presets: 7d, 30d, 90d, YTD, All, Custom | All |
| **Crime type** | shadcn `Command` (searchable multi-select) | All primary_types from API | All |
| **District** | Multi-select with checkboxes | Districts 1–25 | All |
| **Arrest status** | Toggle group | All / Arrest / Non-arrest | All |
| **Community area** | Multi-select (optional) | Community areas 1–77 | All |

### Filter behavior

- Filters live in **Zustand** store
- **Serialized to URL query params** (`?from=2024-01-01&to=2024-03-31&types=THEFT,BATTERY`)
- Browser back/forward restores filters
- TanStack Query key includes all filter values → automatic cache invalidation
- "Reset filters" button clears all
- **Shareable URLs** — enables bookmarkable insights, collaborative analysis, portfolio showcase

### Decisions

- [x] **Filters in top bar (always visible)** — no slide-out panel
- [x] **Filter chips/badges** showing active filters
- [x] **Shareable URLs** — Zustand → URL param sync; trivial to implement, high value

---

## 5. Loading, Empty, and Error States

| State | Component | Behavior |
|-------|-----------|----------|
| **Loading (initial)** | `DashboardSkeleton` | Shimmer placeholders matching exact layout (card skeletons, chart outlines, map gray box) |
| **Loading (refetch)** | Subtle spinner in top-right | Data still visible, background refresh indicator |
| **Empty (first use)** | `EmptyState` variant="welcome" | Illustration + "Welcome to Chicago Crime Dashboard" |
| **Empty (no results)** | `EmptyState` variant="no-results" | "No crimes match your filters" + "Try widening your date range" CTA |
| **Error (network)** | `ErrorBoundary` | Card with error icon + "Something went wrong" + Retry button |
| **Error (404)** | `NotFound` | "Page not found" + link back to Landing |
| **Error (503)** | `ServiceUnavailable` | "Pipeline is down" + last known data timestamp |

### Decisions

- [x] **Skeleton loaders** (shimmer placeholders matching exact layout)
- [x] **Error details in dev mode only** — `process.env.NODE_ENV === 'development'` shows stack trace
- [x] **Global "connection status" indicator** (green/red dot in top bar)

---

## 6. Mobile Responsiveness

| Breakpoint | Layout | Sidebar | Content Grid | Charts |
|------------|--------|---------|--------------|--------|
| **< 768px** (mobile) | Single column | Hamburger → Sheet (slide-over) | 1 column, stacked | Full-width, reduced height (200px) |
| **768–1024px** (tablet) | 2-column | Collapsed (icons only) | 2 columns | Side-by-side where logical |
| **1024–1440px** (desktop) | Full | Full sidebar | 3 columns | Standard height (300px) |
| **> 1440px** (wide) | Full | Full sidebar | 4 columns | Standard height, wider charts |

### Mobile-specific

- KPI cards: 2×2 grid on mobile, 4×1 on desktop
- Tables: switch from tabular to card layout on mobile
- Maps: touch-friendly controls (larger zoom buttons)
- Filters: bottom sheet on mobile instead of top bar

### Decisions

- [x] **Responsive-first** (shadcn Sheet handles mobile sidebar elegantly)
- [x] **Dedicated mobile layout deferred to P2** — responsive covers 90% of cases for portfolio project
- [x] **Maps: touch-friendly controls** on mobile (larger zoom buttons)

---

## 7. Accessibility (WCAG 2.2 AA)

| Criterion | Requirement | Implementation |
|-----------|-------------|----------------|
| **Color contrast** | 4.5:1 text, 3:1 graphics | Design tokens already define; verify all chart colors |
| **Keyboard navigation** | All functionality via keyboard | Recharts `tabIndex`, MapLibre keyboard pan/zoom, shadcn focus rings |
| **Focus visible** | Visible focus indicator | `ring-2 ring-blue-500 ring-offset-2` on all interactive elements |
| **Screen reader** | Charts need text alternatives | `aria-label` on chart containers, hidden data tables |
| **Target size** | 44×44px minimum | All buttons, filters, chart legends |
| **Color not sole indicator** | Use patterns/labels/shapes | Chart labels + patterns + color (hatching, dots for colorblind) |
| **KPI live updates** | Announce when numbers change | `aria-live="polite"` on KPI cards |
| **Skip link** | Skip to main content | At top of page |

### Decisions

- [x] **WCAG AA** (not AAA) — sufficient for portfolio; high contrast mode deferred to P2
- [x] **"View as table" button** on KPIs + top-N bars + arrest rates (not every chart)
- [x] **Screen reader announcements** for KPI live updates (`aria-live="polite"`)
- [x] **Colorblind patterns** (hatching, dots) on charts + color labels
- [x] **Colorblind palette testing** — verify categorical palette against simulators

---

## 8. Performance Budget

| Metric | Target | Strategy |
|--------|--------|----------|
| **Initial JS bundle** | < 350 kB | Code-split per route (9 chunks), lazy-load below fold |
| **Initial CSS** | < 80 kB | Tailwind purge, minimal custom CSS |
| **Lighthouse Performance** | ≥ 90 | Code-splitting, lazy loading, virtual scrolling |
| **Lighthouse Accessibility** | ≥ 95 | WCAG AA compliance, ARIA labels |
| **Lighthouse Best Practices** | ≥ 95 | HTTPS, no deprecated APIs |
| **First Contentful Paint** | < 1.5s | Skeleton loaders, CDN for fonts |
| **Largest Contentful Paint** | < 2.5s | Lazy-load maps, defer heavy charts |
| **Time to Interactive** | < 3.5s | Code-split, prefetch on hover |

### Decisions

- [x] **Bundle analysis on every build** — `rollup-plugin-visualizer` (zero-cost, portfolio screenshot)
- [x] **Prefetch on hover only** — TanStack Query `prefetchQuery` on `onMouseEnter`; preserves code-splitting
- [x] **Performance monitoring** — `web-vitals` library + `reportWebVitals()` (console in dev, endpoint in prod)

---

## 9. Design System Components

| Component | shadcn/ui Base | Customization | Priority |
|-----------|----------------|---------------|----------|
| **KpiCard** | `Card` | + sparkline, delta indicator, JetBrains Mono number | P0 |
| **TrendChart** | `Card` | + Recharts AreaChart, gradient fill, tooltip | P0 |
| **HeatmapChart** | `Card` | + ECharts heatmap, weekday×hour grid | P0 |
| **ChoroplethMap** | `Card` | + MapLibre GL, GeoJSON boundaries, popup | P0 |
| **ClusterMap** | `Card` | + MapLibre GL, H3 clusters, circle layer | P1 |
| **HorizontalBar** | `Card` | + Recharts BarChart layout="vertical" | P0 |
| **GroupedBar** | `Card` | + Recharts BarChart with multiple Bar | P1 |
| **DonutChart** | `Card` | + Recharts PieChart, inner radius | P1 |
| **DataTable** | `Table` | + TanStack Table, sorting, pagination, virtual scroll | P0 |
| **DateRangePicker** | `Calendar` + `Popover` | + presets (7d, 30d, 90d, YTD, All) | P0 |
| **FilterBar** | `Command` + `Badge` | + multi-select, search, active chips | P0 |
| **Skeleton** | `Skeleton` | + shimmer animation, layout variants | P0 |
| **EmptyState** | — | + illustration, title, description, CTA | P0 |
| **ErrorBoundary** | — | + error icon, message, retry button | P0 |
| **Sidebar** | `Sheet` (mobile) / `Collapsible` (desktop) | + nav items, icons, active state | P0 |
| **TopBar** | `Header` | + page title, filters, global search | P0 |
| **ConnectionDot** | — | + green/red status, pulse animation | P0 |

---

## 10. Color Palette Validation

| Palette | Colors | Use Case | Colorblind Safe? |
|---------|--------|----------|------------------|
| **Categorical** | 10 colors (CTA red, navy, amber, blue, green, purple, orange, cyan, lime, yellow) | Crime types, district comparisons | ✅ + patterns (hatching/dots) |
| **Sequential** | Navy → Red (5-step gradient) | Choropleth maps (crime density) | ✅ Intuitive |
| **Diverging** | Blue → White → Red | Arrest rate (above/below avg) | ✅ Standard |
| **Status** | Green, Amber, Red, Blue | Success, warning, danger, info | ✅ Universal |

### Decisions

- [x] **Test categorical palette against colorblind simulators** — verify all 10 colors
- [x] **Add patterns (hatching, dots)** to charts for colorblind users
- [x] **Dark-only theme for M6** — dark is modern dashboard standard; light mode toggle implemented in M8 ✅

---

## Summary — All Finalized Decisions

| # | Decision | Final Choice |
|---|----------|-------------|
| 1 | Landing page | Separate (`/`) — hero + nav hub |
| 2 | Pipeline/Quality visibility | Behind `/admin` |
| 3 | 9th page | About/Data Sources/Methodology |
| 4 | Heatmap library | ECharts (native 7×24) |
| 5 | Filter position | Top bar (always visible) |
| 6 | Filter chips | Yes |
| 7 | Filter URLs | Shareable (Zustand → URL params) |
| 8 | Loading pattern | Skeleton loaders |
| 9 | Error details | Dev mode only |
| 10 | Global connection indicator | Yes (green/red dot) |
| 11 | Mobile strategy | Responsive-first (dedicated layout P2) |
| 12 | Accessibility level | WCAG AA |
| 13 | Screen reader KPIs | `aria-live="polite"` |
| 14 | Dark/Light mode | Dark + light toggle (M8) |
| 15 | Prefetch strategy | Hover only |
| 16 | Bundle analysis | Yes (rollup-plugin-visualizer) |
| 17 | Performance monitoring | Yes (web-vitals) |
| 18 | High contrast mode | Skip (P2) |
| 19 | "View as table" | KPIs + top-N bars + arrest rates |
| 20 | Sparklines in KPIs | Yes |
| 21 | Colorblind patterns | Yes (hatching/dots) |
| 22 | Colorblind palette testing | Yes |

---

## Notes

- All decisions finalized after Senior DE review on 2026-06-05.
- EDA department (new agents) deferred to M7; LLM integration deferred to M8.
- Phased plan: M5 (FastAPI) → M6 (React) → M7 (EDA) → M8 (Production Hardening). Original M8 (LLM) and M9 (Production) were merged/renumbered per stakeholder decision (16 GB RAM constraint, public dashboard scope).
