# Assessment Rubric — Critic Persona Evaluation Criteria

**Date:** 2026-06-06
**Status:** ACTIVE
**Scoring:** 10-point scale per criterion (0 = fails completely, 10 = exceeds standard)

---

## Scoring Scale Definition

| Score | Label | Definition |
|-------|-------|-----------|
| **10** | Exceeds | Significantly surpasses expectation; production-grade, best-in-class |
| **9** | Excellent | Meets all criteria with polish; no issues found |
| **8** | Good | Meets all criteria; minor improvements possible |
| **7** | Acceptable | Meets core criteria; some gaps but functional |
| **6** | Marginal | Meets minimum criteria; notable gaps require attention |
| **5** | Below Standard | Partially meets criteria; significant gaps |
| **4** | Poor | Major criteria unmet; core functionality impacted |
| **3** | Bad | Most criteria unmet; significant rework needed |
| **2** | Very Bad | Critical failures across multiple criteria |
| **1** | Broken | Application is non-functional for this persona |
| **0** | Not Present | Feature/capability does not exist |

**Minimum passing score:** 7/10 per criterion, 8/10 average across all criteria.

---

## 1. Data Analyst Persona

**Perspective:** "Can I trust the numbers and use them for analysis?"
**Pages evaluated:** Dashboard (/), Crime Types (/crime-types), Locations (/locations), Analysis (/analysis)

### Rubric

| # | Criterion | 10 (Exceeds) | 7 (Acceptable) | 4 (Poor) | 0 (Not Present) | Weight |
|---|-----------|-------------|----------------|----------|-----------------|--------|
| DA-1 | **Data Accuracy** — KPI numbers match API response exactly | All numbers match with ±0 rounding | Numbers match within 1% | Numbers diverge > 5% | No KPIs shown | 25% |
| DA-2 | **Filter Responsiveness** — Charts update within 2s of filter change | < 1s update, optimistic UI | 2-5s update, loading indicator | > 5s or no update | Filters don't affect charts | 20% |
| DA-3 | **Data Completeness** — All expected dimensions visible (time, location, type) | All dimensions present with drill-down | Most dimensions present | Missing 2+ dimensions | Only one dimension shown | 15% |
| DA-4 | **Sort/Filter Capability** — Tables support column sorting and search | Sort + search + pagination | Sort works, search missing | Sort broken or missing | No sortable tables | 15% |
| DA-5 | **Export/Share** — Data can be exported or URL shared with filters | CSV export + shareable URL with filters | Shareable URL works | URL shares but filters lost | No export or sharing | 10% |
| DA-6 | **Chart Readability** — Labels, axes, legends are clear and correctly formatted | All labels present, number formatting (K, %, locale) | Most labels present, minor formatting issues | Missing labels or wrong format | Charts are unlabeled | 15% |

### Scoring Formula
```
DA Score = (DA-1 × 0.25) + (DA-2 × 0.20) + (DA-3 × 0.15) + (DA-4 × 0.15) + (DA-5 × 0.10) + (DA-6 × 0.15)
```

---

## 2. Citizen (Non-Technical) Persona

**Perspective:** "Can I understand this without a data science degree?"
**Pages evaluated:** Dashboard (/), Crime Types (/crime-types), Locations (/locations), Analysis (/analysis)

### Rubric

| # | Criterion | 10 (Exceeds) | 7 (Acceptable) | 4 (Poor) | 0 (Not Present) | Weight |
|---|-----------|-------------|----------------|----------|-----------------|--------|
| CI-1 | **Jargon-Free Labels** — No technical field names in UI | All labels use plain English, tooltips explain terms | Most labels plain, 1-2 technical terms | Multiple technical terms (primary_type, domestic_pct) | All labels are field names | 25% |
| CI-2 | **Contextual Help** — Explanations available for key concepts | "What does this mean?" tooltips on all charts + About section | About section present, some tooltips | No tooltips, minimal context | No help anywhere | 20% |
| CI-3 | **Data Source Transparency** — Source and freshness clearly stated | Source, date range, and last updated visible on every page | Source stated on Dashboard only | Source mentioned in About | No source information | 15% |
| CI-4 | **Map Interpretability** — Geographic data is meaningful and labeled | Districts labeled, legend clear, hover shows details | Map renders with basic legend | Map renders but no labels | Map missing or broken | 20% |
| CI-5 | **Visual Hierarchy** — Most important information is most prominent | KPIs above fold, charts ordered by importance, clear layout | KPIs visible, layout mostly logical | No clear hierarchy, everything equal | Cluttered or broken layout | 20% |

### Scoring Formula
```
CI Score = (CI-1 × 0.25) + (CI-2 × 0.20) + (CI-3 × 0.15) + (CI-4 × 0.20) + (CI-5 × 0.20)
```

---

## 3. Executive (Decision-Maker) Persona

**Perspective:** "Can I get the key insights in under 30 seconds?"
**Pages evaluated:** Dashboard (/), Crime Types (/crime-types), Locations (/locations), Analysis (/analysis)

### Rubric

| # | Criterion | 10 (Exceeds) | 7 (Acceptable) | 4 (Poor) | 0 (Not Present) | Weight |
|---|-----------|-------------|----------------|----------|-----------------|--------|
| EX-1 | **Above-the-Fold KPIs** — Key metrics visible without scrolling | 4 KPIs with sparklines + delta indicators visible immediately | KPIs visible, no sparklines | KPIs below fold or missing | No KPIs | 25% |
| EX-2 | **5-Second Comprehension** — Situation clear within 5 seconds | Title + 4 KPIs + trend direction obvious | KPIs visible, trend unclear | Requires scrolling or reading | No clear summary | 25% |
| EX-3 | **Color Consistency** — Semantic colors used consistently (red=concern, green=positive) | Consistent palette across all charts, colorblind-safe | Mostly consistent, 1-2 inconsistencies | Random colors, no semantic meaning | No color coding | 15% |
| EX-4 | **Numbers Add Up** — KPI totals match chart totals | All numbers reconcilable across views | Minor rounding differences (< 1%) | Significant mismatches | Numbers don't relate | 20% |
| EX-5 | **Information Density** — 4-6 charts max per page, no overload | Perfect density, each chart adds unique insight | 5-7 charts, mostly necessary | 8+ charts or missing key views | Cluttered or empty | 15% |

### Scoring Formula
```
EX Score = (EX-1 × 0.25) + (EX-2 × 0.25) + (EX-3 × 0.15) + (EX-4 × 0.20) + (EX-5 × 0.15)
```

---

## 4. Journalist (Investigative) Persona

**Perspective:** "Can I find stories and anomalies in this data?"
**Pages evaluated:** Dashboard (/), Crime Types (/crime-types), Locations (/locations), Analysis (/analysis)

### Rubric

| # | Criterion | 10 (Exceeds) | 7 (Acceptable) | 4 (Poor) | 0 (Not Present) | Weight |
|---|-----------|-------------|----------------|----------|-----------------|--------|
| JO-1 | **Time Comparison** — Can compare different periods side-by-side | Period-over-period comparison with delta | Can filter by date range but no comparison | Date filter exists but no comparison | No time filtering | 20% |
| JO-2 | **Anomaly Visibility** — Spikes/drops are visually prominent | Anomaly markers on trend chart with z-score labels | Trend chart shows spikes but no markers | Trend exists but anomalies hidden | No trend chart | 20% |
| JO-3 | **District Comparison** — Can compare areas side-by-side | District selector with multi-district overlay | Can view one district at a time | District data exists but not comparable | No district views | 20% |
| JO-4 | **Crime Type Trends** — Can see types increasing/decreasing | Multi-line chart with trend direction per type | Top-N bar chart shows current distribution | Only total counts, no type breakdown | No type analysis | 20% |
| JO-5 | **Data Export** — Can get raw data for further analysis | CSV export + shareable filtered URL | Shareable URL works | Can view data but not export | No data access | 20% |

### Scoring Formula
```
JO Score = (JO-1 × 0.20) + (JO-2 × 0.20) + (JO-3 × 0.20) + (JO-4 × 0.20) + (JO-5 × 0.20)
```

---

## 5. First-Timer (Onboarding) Persona

**Perspective:** "Can I figure out how to use this in under 2 minutes?"
**Pages evaluated:** Dashboard (/), Crime Types (/crime-types), Locations (/locations), Analysis (/analysis)

### Rubric

| # | Criterion | 10 (Exceeds) | 7 (Acceptable) | 4 (Poor) | 0 (Not Present) | Weight |
|---|-----------|-------------|----------------|----------|-----------------|--------|
| FT-1 | **Clear Title/Hero** — "Chicago Crime Dashboard" visible immediately | Title + subtitle + hero KPI visible on load | Title visible, no subtitle | Title below fold | No title | 20% |
| FT-2 | **Onboarding Path** — "About this dashboard" or welcome message present | Expandable About section + quick-start guide | About section present | No onboarding, just raw data | No guidance | 20% |
| FT-3 | **Loading Feedback** — Skeleton loaders shown during data fetch | Skeleton shimmer matching exact layout | Basic spinner or loading text | Blank screen during load | No loading state | 15% |
| FT-4 | **Error Recovery** — Helpful error messages with retry option | "Something went wrong" + retry button + error details in dev | Error message shown, no retry | Generic error or blank page | No error handling | 20% |
| FT-5 | **Navigation Intuition** — Sidebar links clearly labeled with icons | Icons + labels + active state + logical grouping | Labels present, no icons | Links exist but unclear | No navigation | 25% |

### Scoring Formula
```
FT Score = (FT-1 × 0.20) + (FT-2 × 0.20) + (FT-3 × 0.15) + (FT-4 × 0.20) + (FT-5 × 0.25)
```

---

## 6. Policy Maker (Stakeholder) Persona

**Perspective:** "Are these numbers defensible for policy decisions?"
**Pages evaluated:** Dashboard (/), Analysis (/analysis)

### Rubric

| # | Criterion | 10 (Exceeds) | 7 (Acceptable) | 4 (Poor) | 0 (Not Present) | Weight |
|---|-----------|-------------|----------------|----------|-----------------|--------|
| PM-1 | **Defensible KPIs** — Numbers backed by verifiable data with methodology note | KPIs + methodology + data source + date range | KPIs with data source | KPIs without context | No KPIs | 30% |
| PM-2 | **Neighborhood Granularity** — Can drill down to specific areas | District + community area + block-level data | District-level data | Only city-level aggregates | No geographic breakdown | 30% |
| PM-3 | **Trend Analysis** — Can see trends over time for specific areas | Time series with district filter + comparison | Time series with city-level filter | Only current snapshot | No temporal data | 25% |
| PM-4 | **Caveat Visibility** — Limitations and data freshness stated | Limitations + freshness + methodology on every page | Limitations in About section | No caveats mentioned | No transparency | 15% |

### Scoring Formula
```
PM Score = (PM-1 × 0.30) + (PM-2 × 0.30) + (PM-3 × 0.25) + (PM-4 × 0.15)
```

---

## 7. Community Organizer (Stakeholder) Persona

**Perspective:** "Can I use this to advocate for my neighborhood?"
**Pages evaluated:** Locations (/locations)

### Rubric

| # | Criterion | 10 (Exceeds) | 7 (Acceptable) | 4 (Poor) | 0 (Not Present) | Weight |
|---|-----------|-------------|----------------|----------|-----------------|--------|
| CO-1 | **Neighborhood Search** — Can find specific areas by name | Search + autocomplete + district/community area views | Search works, no autocomplete | Can browse but no search | No location search | 30% |
| CO-2 | **Comparative View** — Can compare neighborhoods side-by-side | Multi-select comparison with delta indicators | Can view one neighborhood at a time | Data exists but not comparable | No comparison | 30% |
| CO-3 | **Actionable Insights** — Shows trends that suggest action areas | Trend + anomaly + ranking per neighborhood | Basic stats per neighborhood | Only raw counts | No insights | 25% |
| CO-4 | **Shareable Findings** — Can share a filtered view with stakeholders | Shareable URL + screenshot-friendly layout | Shareable URL works | Can view but not share | No sharing | 15% |

### Scoring Formula
```
CO Score = (CO-1 × 0.30) + (CO-2 × 0.30) + (CO-3 × 0.25) + (CO-4 × 0.15)
```

---

## 8. News Editor (Stakeholder) Persona

**Perspective:** "Can I find headline-worthy stories quickly?"
**Pages evaluated:** Dashboard (/), Analysis (/analysis)

### Rubric

| # | Criterion | 10 (Exceeds) | 7 (Acceptable) | 4 (Poor) | 0 (Not Present) | Weight |
|---|-----------|-------------|----------------|----------|-----------------|--------|
| NE-1 | **Headline Findings** — Top 3 insights visible on Dashboard | Hero KPIs + trend + anomaly highlighted | KPIs visible, trends present | Data exists but no highlights | No summary view | 25% |
| NE-2 | **Surprise Detection** — Anomalies and unusual patterns flagged | Anomaly markers + z-score labels + trend context | Trend shows spikes, no markers | No anomaly detection | No trend data | 25% |
| NE-3 | **Context for Stories** — Data source, methodology, and limitations visible | Source + methodology + date range + caveats on every page | Source in About only | Minimal context | No context | 25% |
| NE-4 | **Export for Article** — Can get numbers and charts for publication | CSV export + high-res chart export + shareable URL | Shareable URL works | Can view but not export | No export | 25% |

### Scoring Formula
```
NE Score = (NE-1 × 0.25) + (NE-2 × 0.25) + (NE-3 × 0.25) + (NE-4 × 0.25)
```

---

## 9. Composite Critic Score

### Weighted Average

| Persona | Weight | Rationale |
|---------|--------|-----------|
| Data Analyst | 25% | Primary power user — data accuracy is core |
| Citizen | 15% | Accessibility and understandability |
| Executive | 15% | Decision-maker — speed to insight |
| Journalist | 10% | Investigative use case — depth of analysis |
| First-Timer | 10% | Onboarding — usability baseline |
| Policy Maker | 10% | Stakeholder — defensibility of data |
| Community Organizer | 8% | Stakeholder — neighborhood-level utility |
| News Editor | 7% | Stakeholder — headline discovery |

### Composite Formula
```
Critic Composite = (DA × 0.25) + (CI × 0.15) + (EX × 0.15) + (JO × 0.10) + 
                   (FT × 0.10) + (PM × 0.10) + (CO × 0.08) + (NE × 0.07)
```

### Pass/Fail Thresholds

| Threshold | Score | Action |
|-----------|-------|--------|
| **Pass** | ≥ 8.0 | Proceed to next milestone |
| **Conditional Pass** | 7.0 – 7.9 | Fix identified gaps, re-evaluate |
| **Fail** | < 7.0 | Must remediate before proceeding |
| **Hard Fail** | Any persona < 6.0 | Specific persona area must be reworked |

---

## Changelog

| Date | Entry | Author |
|------|-------|--------|
| 2026-06-06 | Initial rubric: 8 personas, 44 criteria, 10-point scale | Assessment Framework |
