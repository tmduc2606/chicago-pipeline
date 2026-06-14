# M7 — EDA Layer Implementation Plan

> Status: **COMPLETE** — authored 2026-06-12, updated 2026-06-13
> Scope: EDA notebooks, insight reports, web integration, new agents

## 1. Architecture decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| 3-layer hierarchy replacement | **Topic × Tag taxonomy** | Scalable to hundreds of analyses; searchable; no label ambiguity |
| Notebook structure | **Single notebook, 7 sections** | User preference; easier to maintain |
| Insight delivery | **Static JSON + markdown** | No backend changes needed; notebook pre-computes everything |
| Web integration | **New `/insights` page with filterable cards** | Surfaces findings directly in the dashboard |
| Glitch display (high-cardinality features) | **Top-N + "Other" aggregation** | Handles 90 IUCR codes, 77 community areas gracefully |

## 2. Topic × Tag taxonomy

### Topics
- `overview` — Dataset summary and statistics
- `distribution` — Frequency and composition analyses
- `temporal` — Time-based analyses
- `spatial` — Geographic analyses
- `categorical` — Crime type and domestic analyses
- `relational` — Cross-dimensional analyses

### Tags
- `distribution` — How data is distributed across a dimension
- `trend` — How something changes over time
- `comparison` — Comparing groups or periods
- `correlation` — Relationship between variables
- `composition` — Parts of a whole
- `clustering` — Grouping similar entities

### Difficulty (1–5)
1. Single aggregation + simple chart
2. Multi-dimensional aggregation + standard chart
3. Statistical test or complex aggregation
4. Machine learning or advanced statistics
5. Advanced ML or deep learning

## 3. Final EDA list (39 analyses)

### A. Core EDA List (25) — Notebook + Reports

| # | Section | Analysis | Topic | Tag | Diff |
|---|---------|----------|-------|-----|:----:|
| 1 | Overview | Total number of crime records | overview | distribution | 1 |
| 2 | Overview | Number of unique crime types | overview | distribution | 1 |
| 3 | Overview | Number of unique crime descriptions | overview | distribution | 1 |
| 4 | Overview | Unique locations, districts, wards, community areas | overview | distribution | 1 |
| 5 | Overview | Summary of arrests and domestic incidents | overview | distribution | 1 |
| 6 | Distribution | Crime by primary type | distribution | distribution | 1 |
| 7 | Distribution | Crime by description | distribution | distribution | 2 |
| 8 | Distribution | Crime by IUCR code | distribution | distribution | 2 |
| 9 | Distribution | Crime by location description | spatial | distribution | 2 |
| 10 | Distribution | Top crime types with highest counts | distribution | distribution | 1 |
| 11 | Temporal | Crime trend by year | temporal | trend | 1 |
| 12 | Temporal | Crime trend by month | temporal | trend | 1 |
| 13 | Temporal | Crime trend by day | temporal | trend | 1 |
| 14 | Temporal | Crime trend by hour | temporal | distribution | 1 |
| 15 | Temporal | Crime trend by day of week | temporal | distribution | 1 |
| 16 | Temporal | Trend of each crime type over time | temporal | trend | 2 |
| 17 | Temporal | Top crime types in each year | temporal | comparison | 2 |
| 18 | Temporal | Top crime types in each month | temporal | comparison | 2 |
| 19 | Temporal | Seasonal pattern of crime | temporal | trend | 2 |
| 20 | Temporal | Weekday vs weekend patterns | temporal | comparison | 2 |
| 21 | Spatial | Crime by district | spatial | distribution | 1 |
| 22 | Spatial | Crime by ward | spatial | distribution | 1 |
| 23 | Spatial | Crime by community area | spatial | distribution | 1 |
| 24 | Spatial | Crime concentration by block/location | spatial | distribution | 2 |
| 25 | Spatial | Hotspot visualization across Chicago | spatial | distribution | 3 |

### B. Extended EDA List (14) — Web App + Reports

| # | Section | Analysis | Topic | Tag | Diff |
|---|---------|----------|-------|-----|:----:|
| 26 | Arrest | Arrest rate by crime type | categorical | comparison | 2 |
| 27 | Arrest | Arrest rate by year | temporal | trend | 2 |
| 28 | Arrest | Arrest rate by district | spatial | comparison | 2 |
| 29 | Arrest | Arrest rate by location type | spatial | comparison | 2 |
| 30 | Arrest | Domestic vs non-domestic crimes | categorical | comparison | 2 |
| 31 | Advanced | Hotspot stability over time | temporal | trend | 3 |
| 32 | Advanced | Month-by-location heatmap | spatial | distribution | 3 |
| 33 | Advanced | District-by-month heatmap | spatial | distribution | 3 |
| 34 | Advanced | Location-by-day heatmap | spatial | distribution | 3 |
| 35 | Pattern | Crime co-occurrence by area | relational | correlation | 4 |
| 36 | Pattern | Neighborhood clustering by crime profile | relational | clustering | 4 |
| 37 | Pattern | Crime diversity across community areas | spatial | composition | 3 |
| 38 | Pattern | Correlation between crime type and time | relational | correlation | 3 |
| 39 | Pattern | Correlation between crime type and location | relational | correlation | 3 |

## 4. Deliverables

### 4.1 EDA Notebook (`scripts/notebooks/M7_EDA.ipynb`)

Single notebook with 7 sections, 39 analysis cells.

### 4.2 Insight Reports (`reports/eda/`)

```
reports/eda/
├── INDEX.md
├── overview/          (5 reports)
├── distribution/      (5 reports)
├── temporal/          (10 reports)
├── spatial/           (5 reports)
├── arrest-domestic/   (5 reports) [Extended]
├── advanced-temporal-spatial/  (4 reports) [Extended]
└── pattern-discovery/ (5 reports) [Extended]
```

### 4.3 Web Integration

**New files:**
- `web/src/pages/InsightsPage.tsx`
- `web/src/config/insights.json` (14 extended entries)
- `web/src/config/viz-catalog.yaml`

**Modified files:**
- `web/src/App.tsx` — add `/insights` route
- `web/src/components/layout/Sidebar.tsx` — add "Insights" nav item (4th position)

### 4.4 Agent Files

**New directories:**
```
agents/eda-lead/
├── AGENTS.md
├── PROMPT.md
└── CONTRACTS.md

agents/eda-researcher/
├── AGENTS.md
├── PROMPT.md
└── CONTRACTS.md
```

## 5. Implementation order

| Step | What | Files |
|------|------|-------|
| 1 | Write M7 plan | `docs/milestones/M7-plan.md` |
| 2 | Create EDA Lead agent files | `agents/eda-lead/*` |
| 3 | Create EDA Researcher agent files | `agents/eda-researcher/*` |
| 4 | Create agent directories in root AGENTS.md | `AGENTS.md` |
| 5 | Restructure notebook with 7 sections | `scripts/notebooks/M7_EDA.ipynb` |
| 6 | Create 39 insight reports | `reports/eda/**/*.md` |
| 7 | Generate insights.json (14 extended) | `web/src/config/insights.json` |
| 8 | Create InsightsPage | `web/src/pages/InsightsPage.tsx` |
| 9 | Add route + nav item | `App.tsx`, `Sidebar.tsx` |
| 10 | Create visualization catalog | `web/src/config/viz-catalog.yaml` |
| 11 | Update IMPLEMENTATION_PLAN.md | `docs/IMPLEMENTATION_PLAN.md` |
| 12 | Run lint + tests | `make lint`, `make test` |

## 6. Gate verification

- [x] All 39 notebook cells exist in `scripts/notebooks/M7_EDA.ipynb`
- [x] 39 insight reports exist in `reports/eda/`
- [x] `insights.json` has 14 entries (extended list)
- [x] `/insights` page renders in the web app
- [x] Topic/tag filters work on the Insights page
- [x] Both agent AGENTS.md files exist
- [x] `viz-catalog.yaml` has all chart entries
- [x] `make lint` green
- [x] `make test` green
