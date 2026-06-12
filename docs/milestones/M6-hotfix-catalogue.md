# M6 Hotfix Catalogue

**Date:** 2026-06-06
**Source:** `reports/m6_results/` — screenshots + filter_logs.txt
**Author:** QA Agent (analysis) → Architect (sign-off)

---

## Executive Summary

9 bugs identified from M6 user testing. Root causes cluster around:
1. One missed service file (`context.py`) still using the broken `::date` SQL cast — causes 500 errors on context endpoints
2. Wrong data source for the hourly heatmap (daily data pretending to be hourly)
3. Hardcoded coordinates in the choropleth map (all dots stacked at Chicago center)
4. Race condition in both map components between React Query data arrival and MapLibre `style.load` event
5. No error isolation — one component crash takes down the entire page

---

## BUG-01 | context.py `::date` cast — 500 errors on filter apply

| Field | Value |
|-------|-------|
| **Severity** | HIGH |
| **File** | `api/app/services/context.py:17-22` |
| **Agent** | Backend Engineer |
| **Phase** | P0 |

**Symptom:** `/api/context/domestic` and `/api/context/location` return HTTP 500 whenever `from_date` or `to_date` are passed. Filter logs show `from_date=0002-06-06` (year truncated from 2024→0002).

**Root cause:** `_build_filter()` passes raw string params with SQL `:from_date::date` cast. asyncpg intercepts the string before PostgreSQL processes the cast, truncating the year. This is the exact same bug already fixed in `overview.py`, `geo.py`, `arrests.py`, `timeseries.py` (main filter), and `crime_types.py` — but `context.py` was missed.

**Cascading effects:**
- Dashboard → Domestic vs Non-Domestic donut chart fails (black/empty)
- Dashboard → Top Locations list fails
- Locations page → Top Locations list fails
- Locations page renders blank (cascading failure)

**Fix:** Replace `:from_date::date` + string param with `date.fromisoformat(from_date)` + no cast. Add `try/except ValueError` guard.

---

## BUG-02 | timeseries.py `get_heatmap()` `::date` cast — latent bug

| Field | Value |
|-------|-------|
| **Severity** | LOW (endpoint unused by frontend) |
| **File** | `api/app/services/timeseries.py:162-167` |
| **Agent** | Backend Engineer |
| **Phase** | P0 |

**Symptom:** `/api/heatmap` would 500 on date filters if called. Not currently triggered.

**Root cause:** Same `::date` cast pattern as BUG-01.

**Fix:** Convert to `date.fromisoformat()` + `try/except ValueError`.

---

## BUG-03 | ChoroplethMap hardcoded coordinates — all dots on single point

| Field | Value |
|-------|-------|
| **Severity** | HIGH |
| **File** | `web/src/components/maps/ChoroplethMap.tsx:39` |
| **Agent** | Backend + Frontend Engineer |
| **Phase** | P2 |

**Symptom:** Every data feature gets `coordinates: [-87.6298, 41.8781]` (Chicago center). All 25 district dots render on top of each other at one point.

**Root cause:** Backend `get_choropleth()` returns `key`, `label`, `value` per district — no lat/lng. Frontend hardcodes center point.

**Fix:** Backend adds `AVG(l.latitude)` and `AVG(l.longitude)` to choropleth query. Frontend reads `lat`/`lng` from each bucket.

---

## BUG-04 | HourlyHeatmap uses wrong data source — shows mostly zeros

| Field | Value |
|-------|-------|
| **Severity** | MEDIUM |
| **File** | `web/src/components/charts/HourlyHeatmap.tsx:10-13, 24-29` |
| **Agent** | Frontend Engineer |
| **Phase** | P1 |

**Symptom:** "Crimes by Hour of Day" chart shows only 2–3 visible bars; rest are zero.

**Root cause:** Component fetches daily timeseries and calls `getHours()` on date-only strings → always returns 0. The API has a dedicated `/api/heatmap` endpoint that returns a proper weekday×hour matrix.

**Fix:** Switch to `api.heatmap()` endpoint. Update `api.ts` to accept filter params and fix `HeatmapResponse` type.

---

## BUG-05 | Locations page blank on first load

| Field | Value |
|-------|-------|
| **Severity** | HIGH |
| **File** | `web/src/pages/LocationsPage.tsx` |
| **Agent** | Frontend Engineer |
| **Phase** | P3 |

**Symptom:** `localhost:5173/locations` shows completely blank dark page — no sidebar, no content, no error.

**Root cause:** BUG-01 causes `/api/context/location` to 500. Map components may throw during initialization. ErrorBoundary catches crash but replaces entire route content. If error panel itself fails to render, page appears blank.

**Fix:** Fix BUG-01 (primary). Wrap map components in individual ErrorBoundary.

---

## BUG-06 | Dashboard maps empty on first load (race condition)

| Field | Value |
|-------|-------|
| **Severity** | MEDIUM |
| **Files** | `web/src/components/maps/ChoroplethMap.tsx:123-135`, `ClusterMap.tsx:99-111` |
| **Agent** | Frontend Engineer |
| **Phase** | P2 |

**Symptom:** "Choropleth by District" and "Crime Clusters" show empty black card containers on first dashboard load. Maps appear after navigating away and back.

**Root cause:** Race condition between React Query data arrival and MapLibre `style.load` event. When data arrives before style loads, the second `useEffect` registers a new `style.load` listener. If style already loaded, listener never fires.

**Fix:** In second `useEffect`, after attaching listener, re-check `styleLoaded.current` and call `addDataToMap()` immediately if true.

---

## BUG-07 | `api.heatmap()` missing filter params + wrong type

| Field | Value |
|-------|-------|
| **Severity** | MEDIUM (blocks BUG-04 fix) |
| **File** | `web/src/lib/api.ts:26-32, 96-97` |
| **Agent** | Frontend Engineer |
| **Phase** | P1 |

**Symptom:** `HeatmapResponse` type defines `matrix: string[]` but backend returns `matrix: number[][]`. `api.heatmap()` accepts no filter params.

**Fix:** Update type to `matrix: number[][]`. Add `params?: URLSearchParams` parameter.

---

## BUG-08 | ChoroplethMap missing `level`/`metric` query params

| Field | Value |
|-------|-------|
| **Severity** | LOW (works via backend defaults) |
| **Files** | `web/src/lib/api.ts:102-103`, `ChoroplethMap.tsx:26` |
| **Agent** | Frontend Engineer |
| **Phase** | P2 |

**Symptom:** Frontend never sends `level` or `metric` params. Works by accident via FastAPI defaults.

**Fix:** Hardcode `level=district&metric=count` in the frontend call.

---

## BUG-09 | Locations page no ErrorBoundary isolation for map crashes

| Field | Value |
|-------|-------|
| **Severity** | MEDIUM |
| **File** | `web/src/pages/LocationsPage.tsx:23-26` |
| **Agent** | Frontend Engineer |
| **Phase** | P3 |

**Symptom:** If either map throws, ErrorBoundary replaces entire page content — including header, other map, and location list.

**Fix:** Wrap each map in its own `<ErrorBoundary>`.

---

## Execution Plan

| Phase | Bugs | Agent | Rationale |
|-------|------|-------|-----------|
| **P0** | BUG-01, BUG-02 | Backend Engineer | Foundation fix — context endpoints broken |
| **P1** | BUG-04, BUG-07 | Frontend Engineer | Heatmap data source + type fix |
| **P2** | BUG-03, BUG-06, BUG-08 | Backend + Frontend | Choropleth coordinates + race condition |
| **P3** | BUG-05, BUG-09 | Frontend Engineer | Error boundary isolation |

## Test Verification

After all fixes:
- [ ] `make test` — 42/42 backend tests pass
- [ ] `make lint` — ruff + tsc clean
- [ ] All 13 data endpoints return 200 with real data
- [ ] Dashboard loads fully on first visit (all 8 charts + 2 maps)
- [ ] Locations page loads fully (maps + location list)
- [ ] Date filters work on all pages (no 500 errors)
- [ ] Hourly heatmap shows 24 bars (not 2–3)
- [ ] Choropleth map shows dots at district locations (not all at center)
