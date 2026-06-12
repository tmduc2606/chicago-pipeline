# Implementation Mistakes Catalogue

**Purpose:** Cumulative record of anti-patterns discovered during implementation. Every agent must check this file before writing code that touches the affected services or layers.

**How to use:**
- **Before coding:** Grep for the service/file you're touching; check if a mistake entry applies.
- **During review:** Cross-reference new code against prevention rules.
- **At milestone gate:** QA verifies no known mistake patterns exist in new code.

---

## MISTAKE-001 | asyncpg rejects `::date` SQL cast on string params

| Field | Value |
|-------|-------|
| **Severity** | HIGH |
| **Discovered** | M5 (overview), M6 (context — missed) |
| **Services affected** | Any service using `_build_filter()` with date params: `overview.py`, `geo.py`, `arrests.py`, `timeseries.py`, `crime_types.py`, `context.py` |
| **Root cause** | asyncpg intercepts parameter binding before PostgreSQL processes `::date`. A string like `"2024-06-06"` sent as `:from_date::date` gets truncated to year `0002` by asyncpg's type inference. |
| **Symptom** | HTTP 500 on any endpoint with date filters; date values corrupted in query |
| **Fix pattern** | Convert to Python `date` object before passing as param. Remove `::date` from SQL. |
| **Code** | ```python\nfrom datetime import date\ntry:\n    params[\"from_date\"] = date.fromisoformat(from_date)\n    conditions.append(\"t.date >= :from_date\")\nexcept ValueError:\n    pass  # skip filter on invalid date\n```\n**Never:** `conditions.append(\"t.date >= :from_date::date\")` with `params[\"from_date\"] = from_date` |
| **Prevention rule** | **RULE:** In any service file, date params MUST be converted via `date.fromisoformat()` before passing to asyncpg. SQL casts like `::date` or `CAST(... AS date)` are forbidden on asyncpg-bound params. |

---

## MISTAKE-002 | Frontend hardcodes coordinates when backend lacks lat/lng

| Field | Value |
|-------|-------|
| **Severity** | HIGH |
| **Discovered** | M6 |
| **Services affected** | `ChoroplethMap.tsx`, any map component rendering grouped data |
| **Root cause** | Backend `get_choropleth()` returned `key`, `label`, `value` but no `lat`/`lng`. Frontend hardcoded `[-87.6298, 41.8781]` (Chicago center) for every feature, stacking all dots at one point. |
| **Symptom** | Map renders but all data points are at the same location; "inaccurate / non-realistic" display |
| **Fix pattern** | Backend adds `AVG(l.latitude)` and `AVG(l.longitude)` to the GROUP BY query. Frontend reads `item.lat`, `item.lng` from the response. |
| **Prevention rule** | **RULE:** Any map component rendering geographic data MUST receive coordinates from the backend. Never hardcode lat/lng as a fallback. If the backend endpoint doesn't return coordinates, fix the backend first. |

---

## MISTAKE-003 | Wrong API endpoint for heatmap data

| Field | Value |
|-------|-------|
| **Severity** | MEDIUM |
| **Discovered** | M6 |
| **Services affected** | `HourlyHeatmap.tsx`, `api.ts` |
| **Root cause** | HourlyHeatmap fetched daily timeseries (`/api/timeseries?granularity=daily`) and called `getHours()` on date-only strings. `new Date("2024-06-01").getHours()` returns `0` (midnight UTC), so all counts accumulated at hour 0. |
| **Symptom** | "Crimes by Hour of Day" chart shows only 2-3 visible bars; rest are zero |
| **Fix pattern** | Use the dedicated `/api/heatmap` endpoint which returns a proper 7x24 (weekday x hour) matrix. Update `api.ts` to accept filter params and fix the response type. |
| **Prevention rule** | **RULE:** Before implementing a chart, check if a dedicated backend endpoint exists for that aggregation. Never re-purpose a different granularity endpoint and extract the needed dimension client-side. |

---

## MISTAKE-004 | Race condition between React Query and MapLibre style.load

| Field | Value |
|-------|-------|
| **Severity** | MEDIUM |
| **Discovered** | M6 |
| **Services affected** | `ChoroplethMap.tsx`, `ClusterMap.tsx`, any MapLibre component |
| **Root cause** | When React Query data arrives before MapLibre `style.load` event, the second `useEffect` registers a new listener. But if the style already loaded, this listener never fires. Data is lost. |
| **Symptom** | Maps show as empty black card containers on first load; appear after navigating away and back |
| **Fix pattern** | After attaching the `style.load` listener, re-check `styleLoaded.current` and call `addDataToMap()` immediately if true. |
| **Code** | ```tsx\nuseEffect(() => {\n  const map = mapRef.current;\n  if (!map || !data) return;\n  if (!styleLoaded.current) {\n    const onStyleLoad = () => {\n      styleLoaded.current = true;\n      map.resize();\n      addDataToMap(map, data);\n    };\n    map.on(\"style.load\", onStyleLoad);\n    if (styleLoaded.current) {\n      map.off(\"style.load\", onStyleLoad);\n      addDataToMap(map, data);\n    }\n    return;\n  }\n  addDataToMap(map, data);\n}, [data]);\n```\n**Never:** `map.on(\"style.load\", () => { ... })` without re-checking `styleLoaded` after. |
| **Prevention rule** | **RULE:** In any MapLibre component, if data can arrive asynchronously via React Query, the `useEffect` that applies data to the map MUST re-check `styleLoaded` after attaching the listener. |

---

## MISTAKE-005 | No error boundary isolation — one crash takes down the page

| Field | Value |
|-------|-------|
| **Severity** | MEDIUM |
| **Discovered** | M6 |
| **Services affected** | `DashboardPage.tsx`, `LocationsPage.tsx`, any page with multiple independent data components |
| **Root cause** | A single `<ErrorBoundary>` wraps the entire Routes tree. If any child component throws (e.g., map initialization), the ErrorBoundary replaces ALL route content with the error panel — including headers, other charts, and lists. |
| **Symptom** | Blank page or single error panel replacing all content when one component crashes |
| **Fix pattern** | Wrap each independent data-fetching component in its own `<ErrorBoundary>`. |
| **Code** | ```tsx\n<div className=\"grid grid-cols-1 gap-4 lg:grid-cols-2\">\n  <ErrorBoundary>\n    <ChoroplethMap />\n  </ErrorBoundary>\n  <ErrorBoundary>\n    <ClusterMap />\n  </ErrorBoundary>\n</div>\n```\n**Never:** Render multiple independent data components without individual ErrorBoundary wrappers. |
| **Prevention rule** | **RULE:** Every independent data-fetching component (chart, map, list) on a page MUST be wrapped in its own `<ErrorBoundary>`. The page-level ErrorBoundary is a fallback, not the primary mechanism. |

---

## MISTAKE-006 | Pydantic non-optional fields reject SQL COALESCE results

| Field | Value |
|-------|-------|
| **Severity** | LOW |
| **Discovered** | M6 |
| **Services affected** | `schemas/geo.py`, any Pydantic model backed by aggregation queries |
| **Root cause** | Backend SQL used `COALESCE(ROUND(AVG(l.latitude)::numeric, 6), 0)` but the Pydantic schema had `lat: float` (required). If the column was missing from the response entirely (not NULL, but absent), Pydantic validation failed with "Field required". |
| **Symptom** | HTTP 500 with Pydantic validation error in logs |
| **Fix pattern** | Use optional fields with defaults for aggregation results that may be NULL or absent: `lat: float = 0.0` |
| **Prevention rule** | **RULE:** Any Pydantic field backed by a SQL aggregation (AVG, SUM, COUNT) MUST use a default value (`= 0.0`, `= 0`, `= ""`) to handle NULL results gracefully. |

---

## MISTAKE-007 | Pipeline-init service dependency causes cascading startup failures

| Field | Value |
|-------|-------|
| **Severity** | MEDIUM |
| **Discovered** | M6 |
| **Services affected** | `docker-compose.yaml`, API startup |
| **Root cause** | API depended on `pipeline-init` via `service_completed_successfully`. This dependency is recreated on every `docker compose up`, causing the API to restart unexpectedly. |
| **Symptom** | API container restarts mid-request; data endpoints return 500 during pipeline execution |
| **Fix pattern** | Remove `service_completed_successfully` dependency. API starts immediately and waits for data via health endpoint. |
| **Prevention rule** | **RULE:** Never use `service_completed_successfully` as a dependency for services that should be always-on. Use health-check-based readiness instead. |

---

## MISTAKE-008 | Frontend date param name mismatch with backend

| Field | Value |
|-------|-------|
| **Severity** | MEDIUM |
| **Discovered** | M6 |
| **Services affected** | `filters.ts`, `api.ts`, `DashboardPage.tsx`, `AnalysisPage.tsx` |
| **Root cause** | Frontend `filtersToParams()` sent `from`/`to` but backend expected `from_date`/`to_date`. The `api.overview()` function also didn't pass params to the fetch call. |
| **Symptom** | Date filters appear to work in the UI but API ignores them; data doesn't change |
| **Fix pattern** | Ensure param names match exactly between frontend `filtersToParams()` and backend `Query()` declarations. Pass `params` to all `api.*()` calls. |
| **Prevention rule** | **RULE:** When adding a new filter param, update both `filtersToParams()` AND the backend `Query()` in the same change. Verify param names match character-for-character. |

---

## MISTAKE-009 | Late bug detection — no pre-gate user simulation

| Field | Value |
|-------|-------|
| **Severity** | HIGH |
| **Discovered** | M6 (all 9 bugs surfaced in user test, not during implementation) |
| **Root cause** | No structured user simulation before declaring "Implementation complete" |
| **Symptom** | Bugs reach user test that could have been caught by clicking through the UI |
| **Fix pattern** | Before any milestone gate sign-off, owning agent MUST load the page in a browser and click through every primary flow |
| **Prevention rule** | **RULE:** No milestone gate sign-off without a "click-through verification" of every page. QA must verify this was done. |

---

## MISTAKE-010 | Pattern repetition — fix one, miss the siblings

| Field | Value |
|-------|-------|
| **Severity** | HIGH |
| **Discovered** | M6 (`::date` bug existed in 6 service files: overview, geo, arrests, timeseries, crime_types, context) |
| **Root cause** | Bug fixed in one file without checking siblings for the same pattern |
| **Symptom** | Same bug resurfaces on other endpoints after "fix" |
| **Fix pattern** | After any pattern-based bug fix, run `grep -r "broken_pattern" path/` across all sibling files. Add findings to the same PR |
| **Prevention rule** | **RULE:** Every bug fix PR MUST include a "sibling sweep" — grep for the broken pattern across all files in the same directory. QA gate verifies the sweep. |

---

## MISTAKE-011 | No feedback-to-fix traceability

| Field | Value |
|-------|-------|
| **Severity** | MEDIUM |
| **Discovered** | M6 (feedback in `reports/m6_results/` has no status field) |
| **Root cause** | Free-form markdown feedback has no triage/fix/verify lifecycle |
| **Symptom** | Cannot determine which feedback was addressed, which was ignored |
| **Fix pattern** | All feedback must include a status field: `reported | triaged | in_progress | fixed | verified | wontfix` |
| **Prevention rule** | **RULE:** Every feedback artifact MUST have a status field and a link to the PR that resolved it. No orphan feedback allowed. |

---

## MISTAKE-012 | Agent ownership ambiguity on UI artifacts

| Field | Value |
|-------|-------|
| **Severity** | MEDIUM |
| **Discovered** | M6 (overlapping ownership between QA, SE, UI/UX on UI bugs) |
| **Root cause** | No clear owner for "who fixes a bug the QA found" |
| **Symptom** | Bugs sit in triage with no agent claiming them |
| **Fix pattern** | Every feedback item must be assigned a primary owner agent |
| **Prevention rule** | **RULE:** Before adding any new agent or sub-agent, update `docs/architecture.md` ownership table. If two agents could own the same artifact, escalate to Architect for arbitration BEFORE the new agent is spawned. |

---

## MISTAKE-013 | Missing env vars cause downstream container failures

| Field | Value |
|-------|-------|
| **Severity** | MEDIUM |
| **Discovered** | M0–M6 assessment (load_postgres.py crash) |
| **Services affected** | `.env`, `docker-compose.yaml`, `load_postgres.py` |
| **Root cause** | `.env` file omitted `POSTGRES_HOST` and `POSTGRES_PORT`. Docker Compose substituted blank strings. The spark-master container received `POSTGRES_HOST=""` and `POSTGRES_PORT=""`, causing SQLAlchemy to build an invalid connection URL (`...:None`). |
| **Symptom** | `ValueError: invalid literal for int() with base 10: 'None'` on `create_engine()` |
| **Fix pattern** | Ensure `.env` contains ALL variables referenced by `${VAR}` in `docker-compose.yaml`. Cross-reference on every compose change. |
| **Prevention rule** | **RULE:** After any `docker-compose.yaml` change that adds `${VAR}` references, run `grep -oP '\$\{[A-Z_]+\}' docker-compose.yaml | sort -u` and verify every variable exists in `.env`. |

---

## MISTAKE-014 | Host scripts cannot run inside containers

| Field | Value |
|-------|-------|
| **Severity** | LOW |
| **Discovered** | M0–M6 assessment (README quick-start) |
| **Services affected** | `scripts/seed.py`, `docker-compose.yaml` |
| **Root cause** | `scripts/` directory is NOT mounted into the spark-master container. Only `./pipeline:/opt/pipeline` and `./data:/data` are mounted. Running `docker compose exec spark-master python scripts/seed.py` fails with "No such file or directory". |
| **Symptom** | `python3: can't open file 'scripts/seed.py': [Errno 2] No such file or directory` |
| **Fix pattern** | `scripts/seed.py` generates a CSV on the HOST filesystem at `data/chicago_crime_synthetic_90d.csv`. The `data/` directory IS mounted into the container at `/data`. So: run seed on the host first, then run pipeline stages in the container. |
| **Prevention rule** | **RULE:** Scripts that write to host-mounted volumes (e.g., `data/`) MUST run on the host, not inside the container. Document the execution context (host vs container) in every script's docstring. |

---

## MISTAKE-015 | Hidden DOM elements interfere with E2E selectors

| Field | Value |
|-------|-------|
| **Severity** | LOW |
| **Discovered** | M0–M6 assessment (Playwright heatmap test) |
| **Services affected** | `web/src/components/charts/KpiCard.tsx`, `web/e2e/dashboard.spec.ts` |
| **Root cause** | Adding a hidden `<canvas className="hidden">` to KpiCard (for sparkline PNG export) caused `page.locator("canvas").first()` in Playwright to match the hidden canvas instead of the visible ECharts heatmap canvas. |
| **Symptom** | `expect(locator).toBeVisible()` fails because the first canvas has `class="hidden"` |
| **Fix pattern** | Use `page.locator("canvas:not(.hidden)")` or `page.locator("canvas:visible")` in E2E tests when hidden utility elements exist. |
| **Prevention rule** | **RULE:** When adding hidden utility elements (export canvases, portals), update all E2E selectors that might match them. Prefer semantic selectors (`[data-testid]`) over element-type selectors. |

---

## MISTAKE-016 | Assessment script timeout too short for E2E

| Field | Value |
|-------|-------|
| **Severity** | LOW |
| **Discovered** | M0–M6 assessment |
| **Services affected** | `scripts/run_assessment.sh` |
| **Root cause** | Default 120s bash timeout was insufficient for the Playwright E2E suite (40 tests take ~3.5 min). The script appeared to complete but was actually killed mid-execution. |
| **Symptom** | E2E tests show "passed" in partial output but the full suite never completes |
| **Fix pattern** | Set timeout to 900000ms (15 min) when calling the assessment script. |
| **Prevention rule** | **RULE:** When running the full assessment pipeline, always specify `--timeout 900000` or run with `MSYS_NO_PATHCONV=1` in Git Bash with adequate timeout. |

---

## Changelog

| Date | Entry | Author |
|------|-------|--------|
| 2026-06-06 | Initial catalogue: MISTAKE-001 through MISTAKE-008 (M6 discoveries) | QA Agent |
| 2026-06-06 | Added MISTAKE-009 through MISTAKE-012 (M6 critic pass setup) | Architect Agent |
| 2026-06-09 | Added MISTAKE-013 through MISTAKE-016 (M0–M6 assessment findings) | QA Agent |
