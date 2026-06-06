# M6 Feedback Backlog

**Generated:** 2026-06-06
**Source:** `reports/critics/M6_critics_*.json` (20 evaluations, 48 issues)
**Status:** M6 COMPLETE — 31/48 verified, 17 deferred to M7-M9

---

## P0 — Fix Immediately

| ID | Category | Page | Title | Status | Owner | Fix PR | Verified |
|----|----------|------|-------|--------|-------|--------|----------|
| M6-CRITIC-039 | missing_state | / | No onboarding for first-time visitors | verified | Frontend | — | ✅ |
| M6-CRITIC-040 | visual_glitch | /, /locations | Maps show empty black boxes during loading | verified | Frontend | — | ✅ |
| M6-CRITIC-033 | confusing_label | / | YoY Change shows 0.0% (misleading) | verified | Backend+Frontend | — | ✅ |

---

## P1 — Fix Before M7

| ID | Category | Page | Title | Status | Owner | Fix PR | Verified |
|----|----------|------|-------|--------|-------|--------|----------|
| M6-CRITIC-011 | confusing_label | / | KPI labels use jargon | verified | Frontend | — | ✅ |
| M6-CRITIC-015 | confusing_label | /crime-types | Crime type labels ALL CAPS | verified | Frontend | — | ✅ |
| M6-CRITIC-017 | confusing_label | /locations | Location labels raw values | verified | Frontend | — | ✅ |
| M6-CRITIC-012 | missing_state | / | No "What am I looking at?" section | verified | Frontend | — | ✅ |
| M6-CRITIC-013 | confusing_label | / | Heatmap color legend not intuitive | verified | Frontend | — | ✅ |
| M6-CRITIC-019 | missing_state | /locations | Maps do not explain symbols | verified | Frontend | — | ✅ |
| M6-CRITIC-041 | missing_state | /, /crime-types | No empty state for filtered results | verified | Frontend | — | ✅ |
| M6-CRITIC-043 | missing_state | /crime-types | No crime type explanations | verified | Frontend | — | ✅ |
| M6-CRITIC-047 | missing_state | /analysis | No Analysis page explanation | verified | Frontend | — | ✅ |
| M6-CRITIC-048 | missing_state | /analysis | No loading state for Key Insights | verified | Frontend | — | ✅ |
| M6-CRITIC-038 | confusing_label | /analysis | Key Insights not scannable | verified | Frontend | — | ✅ |

---

## P2 — Opportunistic in M7-M9

| ID | Category | Page | Title | Status | Owner | Fix PR | Verified |
|----|----------|------|-------|--------|-------|--------|----------|
| M6-CRITIC-001 | missing_feature | / | No drill-down from KPI | triaged | Frontend | — | |
| M6-CRITIC-002 | missing_feature | / | No granularity toggle | triaged | Frontend | — | |
| M6-CRITIC-003 | missing_feature | / | No data export | triaged | Frontend | — | |
| M6-CRITIC-004 | visual_glitch | / | Offense bar chart truncates names | verified | Frontend | — | ✅ |
| M6-CRITIC-005 | missing_feature | /crime-types | No cross-filtering between charts | triaged | Frontend | — | |
| M6-CRITIC-006 | missing_feature | /crime-types | Table not sortable by arrest rate | verified | Frontend | — | ✅ |
| M6-CRITIC-007 | missing_feature | /locations | Location list not sortable/filterable | verified | Frontend | — | ✅ |
| M6-CRITIC-008 | missing_feature | /locations | No way to export location data | verified | Frontend | — | ✅ |
| M6-CRITIC-009 | missing_feature | /analysis | Key Insights static text | verified | Frontend | — | ✅ |
| M6-CRITIC-010 | missing_feature | /analysis | Analysis duplicates Dashboard | triaged | Frontend+Backend | — | |
| M6-CRITIC-014 | missing_state | / | No data freshness indicator | verified | Frontend | — | ✅ |
| M6-CRITIC-016 | missing_state | /crime-types | No explanation of what crime types mean | verified | Frontend | — | ✅ |
| M6-CRITIC-018 | missing_feature | /locations | No way to search for a specific location | verified | Frontend | — | ✅ |
| M6-CRITIC-020 | confusing_label | /analysis | Analysis uses technical terms | verified | Frontend | — | ✅ |
| M6-CRITIC-021 | missing_feature | /analysis | No personalized geographic context | triaged | Frontend+Backend | — | |
| M6-CRITIC-022 | missing_feature | / | No year-over-year comparison view | triaged | Backend+Frontend | — | |
| M6-CRITIC-023 | missing_feature | / | No anomaly or spike detection | triaged | Backend+Frontend | — | |
| M6-CRITIC-024 | missing_feature | / | No time period quick-select | verified | Frontend | — | ✅ |
| M6-CRITIC-025 | missing_feature | / | No shareable link with filters | verified | Frontend | — | ✅ |
| M6-CRITIC-026 | missing_feature | /crime-types | No trend data per crime type | triaged | Backend+Frontend | — | |
| M6-CRITIC-027 | missing_feature | /crime-types | No comparison between crime types | triaged | Frontend | — | |
| M6-CRITIC-028 | missing_feature | /locations | No per-capita density metric | triaged | Backend+Frontend | — | |
| M6-CRITIC-029 | missing_feature | /locations | No hotspot clustering visualization | triaged | Backend+Frontend | — | |
| M6-CRITIC-030 | missing_feature | /analysis | Analysis not deeper than Dashboard | triaged | Backend+Frontend | — | |
| M6-CRITIC-031 | missing_feature | /analysis | No story suggestions | triaged | Backend+Frontend | — | |
| M6-CRITIC-035 | missing_state | / | No dashboard summary section | verified | Frontend | — | ✅ |
| M6-CRITIC-036 | missing_state | /crime-types | No "Top 3" summary | verified | Frontend | — | ✅ |
| M6-CRITIC-037 | missing_state | /locations | No "Hottest District" summary | verified | Frontend | — | ✅ |
| M6-CRITIC-044 | missing_state | /crime-types | No empty state for table | verified | Frontend | — | ✅ |
| M6-CRITIC-046 | missing_state | /locations | Maps lack symbol explanation | verified | Frontend | — | ✅ |

---

## P3 — Deferred to M9 Polish

| ID | Category | Page | Title | Status | Owner | Fix PR | Verified |
|----|----------|------|-------|--------|-------|--------|----------|
| M6-CRITIC-034 | visual_glitch | / | Color coding inconsistency between KPIs | triaged | Frontend | — | |
| M6-CRITIC-042 | accessibility | / | No keyboard navigation support | triaged | Frontend | — | |
| M6-CRITIC-045 | missing_state | /locations | Maps may show broken on first load | triaged | Frontend | — | |

---

## Already Fixed (M6 Hotfix)

| ID | Issue | Status | Fix PR |
|----|-------|--------|--------|
| BUG-01 | context.py `::date` cast | verified | — |
| BUG-02 | timeseries.py `::date` cast | verified | — |
| BUG-03 | ChoroplethMap hardcoded coords | verified | — |
| BUG-04 | HourlyHeatmap wrong data source | verified | — |
| BUG-05 | Locations page blank | verified | — |
| BUG-06 | Dashboard maps race condition | verified | — |
| BUG-07 | heatmap() missing params | verified | — |
| BUG-08 | ChoroplethMap missing level/metric | verified | — |
| BUG-09 | No ErrorBoundary isolation | verified | — |

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total issues | 48 |
| P0 (fix immediately) | 3 |
| P1 (before M7) | 11 |
| P2 (M7-M9) | 30 |
| P3 (M9 polish) | 3 |
| Already fixed | 9 |
| Status: triaged | 17 |
| Status: in_progress | 0 |
| Status: fixed | 0 |
| Status: verified | 31 |
| E2E tests | 20/20 passing |

---

## Triage Rules

1. **P0 issues** must be fixed before any M7 work begins
2. **P1 issues** must be fixed before M7 starts (label + empty state fixes)
3. **P2 issues** are addressed opportunistically during M7-M8
4. **P3 issues** are deferred to M9 polish pass
5. **Every fix** must include: sibling sweep (MISTAKE-010), test update, lint clean
6. **Every fix** must be linked back to this backlog via the Fix PR column
7. **Verification** is done by QA agent after merge
