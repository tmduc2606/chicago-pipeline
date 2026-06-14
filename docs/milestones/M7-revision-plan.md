# M7 Revision Plan — Extend EDA List (10 → 39)

> Status: **IN PROGRESS** — Awaiting approval signal
> Date: 2026-06-12
> Scope: Extend from 10 to 39 EDA analyses (25 core + 14 extended)

---

## 1. Item Mapping

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

---

## 2. File Structure

### 2.1 Notebook (39 analyses)

```
scripts/notebooks/M7_EDA.ipynb
├── Section 1: Dataset Overview (5 analyses)
├── Section 2: Crime Distribution (5 analyses)
├── Section 3: Temporal Analysis (10 analyses)
├── Section 4: Spatial Analysis (5 analyses)
├── Section 5: Arrest & Domestic Analysis (5 analyses) [Extended]
├── Section 6: Advanced Spatial & Temporal (4 analyses) [Extended]
└── Section 7: Pattern Discovery (5 analyses) [Extended]
```

### 2.2 Reports (39 reports + INDEX)

```
reports/eda/
├── INDEX.md
├── overview/
│   ├── 01-total-records.md
│   ├── 02-unique-types.md
│   ├── 03-unique-descriptions.md
│   ├── 04-unique-locations.md
│   └── 05-arrests-domestic-summary.md
├── distribution/
│   ├── 01-by-primary-type.md
│   ├── 02-by-description.md
│   ├── 03-by-iucr.md
│   ├── 04-by-location.md
│   └── 05-top-types.md
├── temporal/
│   ├── 01-by-year.md
│   ├── 02-by-month.md
│   ├── 03-by-day.md
│   ├── 04-by-hour.md
│   ├── 05-by-day-of-week.md
│   ├── 06-type-trends.md
│   ├── 07-top-types-by-year.md
│   ├── 08-top-types-by-month.md
│   ├── 09-seasonal-pattern.md
│   └── 10-weekday-vs-weekend.md
├── spatial/
│   ├── 01-by-district.md
│   ├── 02-by-ward.md
│   ├── 03-by-community-area.md
│   ├── 04-by-block-location.md
│   └── 05-hotspot-visualization.md
├── arrest-domestic/ [Extended]
│   ├── 01-arrest-rate-by-type.md
│   ├── 02-arrest-rate-by-year.md
│   ├── 03-arrest-rate-by-district.md
│   ├── 04-arrest-rate-by-location.md
│   └── 05-domestic-vs-non-domestic.md
├── advanced-temporal-spatial/ [Extended]
│   ├── 01-hotspot-stability.md
│   ├── 02-month-location-heatmap.md
│   ├── 03-district-month-heatmap.md
│   └── 04-location-day-heatmap.md
└── pattern-discovery/ [Extended]
    ├── 01-crime-co-occurrence.md
    ├── 02-neighborhood-clustering.md
    ├── 03-crime-diversity.md
    ├── 04-type-time-correlation.md
    └── 05-type-location-correlation.md
```

### 2.3 Web App (14 extended insights)

```
web/src/config/insights.json — 14 entries (extended list only)
web/src/pages/InsightsPage.tsx — filterable cards for 14 items
```

---

## 3. Files to Modify

| File | Change | Priority |
|------|--------|:--------:|
| `scripts/notebooks/M7_EDA.ipynb` | Restructure to 39 analyses (7 sections) | High |
| `reports/eda/INDEX.md` | Update with 39 reports | High |
| `reports/eda/overview/` | Create 5 new reports | High |
| `reports/eda/distribution/` | Create 5 new reports | High |
| `reports/eda/temporal/` | Create 10 new reports (replace 3) | High |
| `reports/eda/spatial/` | Create 5 new reports (replace 3) | High |
| `reports/eda/arrest-domestic/` | Create 5 new reports | High |
| `reports/eda/advanced-temporal-spatial/` | Create 4 new reports | High |
| `reports/eda/pattern-discovery/` | Create 5 new reports | High |
| `web/src/config/insights.json` | Update to 14 extended entries | High |
| `web/src/pages/InsightsPage.tsx` | Update if needed for 14 items | Medium |
| `agents/eda-lead/AGENTS.md` | Update backlog to 39 items | High |
| `agents/eda-lead/PROMPT.md` | Update analysis list | Medium |
| `agents/eda-researcher/AGENTS.md` | Update execution list | High |
| `agents/eda-researcher/PROMPT.md` | Update analysis list | Medium |
| `docs/milestones/M7-plan.md` | Update to 39 analyses | Medium |
| `docs/milestones/M7-assessment-proposal.md` | Update scalability section | Low |

---

## 4. Implementation Order

| Step | What | Files |
|------|------|-------|
| 1 | Update agent modules | `agents/eda-lead/*`, `agents/eda-researcher/*` |
| 2 | Restructure notebook | `scripts/notebooks/M7_EDA.ipynb` |
| 3 | Create overview reports (5) | `reports/eda/overview/*.md` |
| 4 | Create distribution reports (5) | `reports/eda/distribution/*.md` |
| 5 | Create temporal reports (10) | `reports/eda/temporal/*.md` |
| 6 | Create spatial reports (5) | `reports/eda/spatial/*.md` |
| 7 | Create arrest-domestic reports (5) | `reports/eda/arrest-domestic/*.md` |
| 8 | Create advanced reports (4) | `reports/eda/advanced-temporal-spatial/*.md` |
| 9 | Create pattern reports (5) | `reports/eda/pattern-discovery/*.md` |
| 10 | Update INDEX.md | `reports/eda/INDEX.md` |
| 11 | Update insights.json (14 extended) | `web/src/config/insights.json` |
| 12 | Update M7-plan.md | `docs/milestones/M7-plan.md` |
| 13 | Run lint + tests | `make lint`, `make test` |

---

## 5. Verification

- [ ] Notebook has 39 analysis cells (7 sections)
- [ ] 39 insight reports exist in `reports/eda/`
- [ ] `insights.json` has 14 entries (extended list)
- [ ] `/insights` page renders 14 cards
- [ ] Both agent AGENTS.md files updated
- [ ] `make lint` green
- [ ] `make test` green

---

*Awaiting approval to proceed.*
