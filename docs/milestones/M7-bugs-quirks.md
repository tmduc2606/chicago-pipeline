# M7 EDA — Bugs, Quirks & Overhaul Audit

> Status: **OPEN** — 2026-06-13
> Scope: Full audit of M7 EDA notebook, reports, outputs, and data quality
> Severity: Critical — multiple systemic issues identified

---

## Executive Summary

The M7 EDA layer scored A- (8.58) on the previous assessment. **This score is invalid.** The assessment evaluated narrative claims against markdown reports, not against actual notebook output. A thorough audit reveals **17 systemic issues** spanning data quality, visualization, and analytical integrity. The composite score should be recalculated after all fixes.

### Root Cause

**The synthetic data generator (`scripts/synth_data.py`) produces only Q1 2024 data**, while the dimension table (`dim_time`) spans 2024–2026. The fact table's `year` column is hardcoded to 2024. This single data-quality issue cascades into 10+ downstream visualization failures.

---

## Issue Registry

### SEVERITY: CRITICAL (data breaks analysis)

| # | Issue | Evidence | Impact |
|---|-------|----------|--------|
| **D1** | **Date range only Jan–Mar 2024** | `Date range: 2024-01-01 to 2024-03-30` (Cell 2 output) | Temporal analyses covering 2024–2026, year trends, seasonal patterns, and month comparisons are all invalid |
| **D2** | **Year column is always 2024** | `Year range: 2024 - 2024` (Cell 3 output) | Year-over-year trend charts (3.1, 3.6, 3.7, 5.2, 6.1) are meaningless — single-bar or flat-line charts |
| **D3** | **Arrest rates are uniform (~18%) across all crime types** | Wilson CI table: THEFT 18.6%, ASSAULT 18.2%, … WEAPONS 17.6% (Cell 31) | The "Key Finding" that "NARCOTICS arrest rate (45%) is 3× THEFT (15%)" is **fabricated** — the data doesn't support it |
| **D4** | **Only 3 unique location descriptions** | `Unique loc types: 3` (Cell 6) | Location-based analyses (2.4, 4.4, 4.5, 5.4, 6.2, 6.4, 7.5) are severely impoverished |

### SEVERITY: HIGH (visualizations are broken/misleading)

| # | Issue | Notebook Cell | Fix Required |
|---|-------|:------------:|-------------|
| **V1** | **"Crime trend by month" shows only 3 months** | Cell 14 | Replace with monthly trend within Q1, or generate multi-year data |
| **V2** | **"Seasonal Crime Pattern" — Summer & Fall empty** | Cell 23 | Data only covers Winter (Jan–Mar). Seasons Spring/Summer/Fall are 0 |
| **V3** | **"Top 5 Crime Types Over Time" — line chart over 1 year is meaningless** | Cell 20 | Replace with monthly breakdown or hourly patterns |
| **V4** | **"Arrest Rate by Year" — single bar** | Cell 32 | Only 2024 exists. Replace with monthly arrest trend |
| **V5** | **"Weekday vs Weekend Arrest Rate (%)" — values ~18% for both** | Cell 24 | Arrest rate difference is negligible in uniform data |
| **V6** | **Hotspot map samples 5k of 57k points (8.6%)** | Cell 29 | Use 100% data — 57k points is feasible for scatter |
| **V7** | **All arrest rate charts show ~18% flat line** | Cells 30, 32, 33, 34 | Data quality issue (D3) — arrest rates are synthetic noise |
| **V8** | **Top 10 Districts Crime Count Over Years — flat lines** | Cell 36 | Only 1 year of data, no variation |

### SEVERITY: MEDIUM (quality/usability issues)

| # | Issue | Description | Fix Required |
|---|-------|-------------|-------------|
| **Q1** | **Plain UI — no annotations** | Charts have titles and axis labels but no finding callouts, insight boxes, or contextual annotations | Add text annotations, findings boxes, key-stat callouts |
| **Q2** | **Repetitive visualization types** | ~25 of 32 charts are vertical or horizontal bar charts. Critics experience "chart fatigue" | Diversify: use ridgeline plots, radar charts, small multiples, treemaps |
| **Q3** | **No volume context on arrest rate charts** | Arrest rate % shown without total crime count per category | Add total count as secondary axis or annotation |
| **Q4** | **"Arrest Rate by Location Type (Top 15)" — selection wrong** | Only 3 unique locations exist, "Top 15" is misleading | Fix: show all 3 with volume context |
| **Q5** | **Community area diversity chart — "equal rates" glitchy** | All 77 areas show same n_types (10) because all types appear everywhere in 57k records | Use Shannon entropy or proportional diversity instead of raw count |
| **Q6** | **Heatmaps need thorough inspection** | Month×Location, Month×District, Day×Location heatmaps may have sparsity issues | Validate heatmap data, consider aggregating sparse cells |

### SEVERITY: LOW (improvements)

| # | Issue | Description | Fix Required |
|---|-------|-------------|-------------|
| **I1** | **No moving average on temporal charts** | Raw daily/monthly counts are noisy | Add 7-day or 30-day rolling average |
| **I2** | **No geographic context on hotspot map** | Scatter plot without Chicago boundaries | Add district boundaries or community area outlines |
| **I3** | **No correlation matrix for all crime types** | Only top-5 types shown | Extend to full 10×10 correlation heatmap |
| **I4** | **Chi-square test is trivially significant** | `chi2=57931.00` — this is because sample size is huge, not because effect is large | Report Cramér's V effect size alongside p-value |

---

## Data Root Cause Analysis

### What the synthetic generator produces vs. what the analysis expects

| Dimension | Generator (`synth_data.py`) | Analysis expects | Gap |
|-----------|:---------------------------:|:----------------:|:---:|
| **Time range** | Q1 2024 only (Jan–Mar) | 2024–2026 (3 years) | 9 months missing |
| **Year distribution** | All records = 2024 | Balanced across years | 2 years missing |
| **Arrest rate by type** | Uniform ~18% (random 0/1) | NARCOTICS 45%, THEFT 15% | No differentiation |
| **Location descriptions** | 3 unique values | 10–15 expected | 7–12 missing |
| **Crime type × arrest** | Independent random | Dependent (type influences arrest) | No conditional logic |
| **Crime type × time** | Independent random | Type-specific temporal patterns | No conditional logic |
| **Crime type × location** | Independent random | Type-specific location patterns | No conditional logic |

### Recommended Data Fixes

1. **Extend date range to full 2024–2026** — generate records across all 36 months
2. **Add conditional arrest logic** — P(arrest) varies by type (NARCOTICS higher, THEFT lower)
3. **Expand location descriptions** — 10–15 locations (STREET, RESIDENCE, APARTMENT, SIDEWALK, PARKING LOT, etc.)
4. **Add temporal patterns by type** — THEFT peaks daytime, BATTERY peaks nighttime
5. **Add spatial patterns by type** — Different district distributions per crime type

---

## Agent Task Assignments

### Data Engineer Agent
**Priority: CRITICAL**
- [ ] Fix `scripts/synth_data.py` to generate 2024–2026 data (D1, D2)
- [ ] Add conditional arrest rates by crime type (D3)
- [ ] Expand location descriptions to 10–15 values (D4)
- [ ] Add type-specific temporal patterns (V1, V2, V3)
- [ ] Add type-specific spatial patterns (V8)
- [ ] Re-run pipeline to regenerate all CSVs
- [ ] Validate new data with automated checks

### QA Agent
**Priority: HIGH**
- [ ] Re-execute notebook against new data
- [ ] Validate all 32 charts produce meaningful output
- [ ] Check for empty/zero-value charts
- [ ] Verify statistical tests produce non-trivial results
- [ ] Run lint + type checks
- [ ] Update S1 hard-block checks in evaluation

### EDA Lead Agent
**Priority: HIGH**
- [ ] Audit all 39 insight reports against actual output
- [ ] Fix fabricated findings (e.g., "NARCOTICS 45%" claim)
- [ ] Add volume context to all arrest rate reports
- [ ] Diversify visualization types (reduce bar chart dominance)
- [ ] Add annotations and finding callouts to charts
- [ ] Add moving averages to temporal charts
- [ ] Extend correlation heatmap to all 10 crime types
- [ ] Fix community area diversity chart (use Shannon entropy)

### EDA Researcher Agent
**Priority: MEDIUM**
- [ ] Add Cramér's V alongside chi-square test
- [ ] Add Chicago boundary context to hotspot map
- [ ] Add ridge plots or violin plots for hourly distributions
- [ ] Create small-multiple charts for district comparisons
- [ ] Add radar chart for district crime profiles
- [ ] Validate heatmaps for sparsity issues

### Critic Agent
**Priority: MEDIUM**
- [ ] Re-evaluate all 39 reports with stricter criteria
- [ ] Identify remaining "hallucinated" findings
- [ ] Score each report against actual notebook output
- [ ] Flag any report where Finding ≠ Evidence

---

## Revised Assessment Framework (Stricter)

### New Hard-Block Rules (S2)

| # | S2 Finding | Description |
|---|------------|-------------|
| S2-1 | **Data covers < 12 months** | Temporal analyses requiring seasonal/yearly patterns are invalid |
| S2-2 | **Fabricated statistics** | Any finding that contradicts actual notebook output |
| S2-3 | **Uniform distributions presented as meaningful** | Arrest rates, diversity scores, or correlations that are noise |
| S2-4 | **Empty chart cells** | Any analysis cell that produces empty/zero-value visualization |
| S2-5 | **Single-point time series** | Year or month charts with only 1 data point |

### Revised Scoring Criteria

| Persona | Criterion | Stricter Standard |
|---------|-----------|-------------------|
| **DS** | Methodology | Must include effect sizes (Cramér's V, Cohen's d) alongside p-values |
| **DS** | Reproducibility | Must include data validation checks (row counts, date ranges, null checks) |
| **RL** | Insight Depth | Must demonstrate cross-tabulations with **non-trivial** variation (>5% spread) |
| **RL** | Novelty | Must produce insights **not achievable** from simple bar charts |
| **VE** | Chart Selection | Maximum 40% bar charts; must use 4+ distinct chart types |
| **VE** | Label Quality | Every chart must have data labels on key data points |
| **VE** | Color & Contrast | Must use colorblind-safe palette on ALL charts (not just defined) |
| **BA** | Evidence | Every statistical claim must include confidence interval or effect size |
| **BA** | Context | Every finding must cite external benchmark **and** validate against actual data |
| **PR** | Documentation | Reports must match actual notebook output exactly |

---

## Overhaul Implementation Plan

### Phase 1: Data Quality (Data Engineer + EDA Lead)
**Duration:** 1 sprint
**Priority:** CRITICAL

| Step | Task | Owner | Validation |
|:----:|------|-------|------------|
| 1.1 | Fix `synth_data.py`: extend to 2024–2026, 36 months | Data Engineer | `dim_time.date` range matches fact range |
| 1.2 | Fix `synth_data.py`: add conditional arrest rates | Data Engineer | Arrest rate varies >20% across types |
| 1.3 | Fix `synth_data.py`: expand location descriptions to 10+ | Data Engineer | `n_unique(location_description) >= 10` |
| 1.4 | Fix `synth_data.py`: add type-specific temporal patterns | Data Engineer | Hour distribution differs by type |
| 1.5 | Fix `synth_data.py`: add type-specific spatial patterns | Data Engineer | District distribution differs by type |
| 1.6 | Re-run pipeline: `make pipeline` | Data Engineer | All CSVs regenerated |
| 1.7 | Validate new data: automated checks | QA Agent | All checks pass |

### Phase 2: Notebook Overhaul (EDA Lead + EDA Researcher)
**Duration:** 1 sprint
**Priority:** HIGH

| Step | Task | Owner | Impact |
|:----:|------|-------|--------|
| 2.1 | Remove fabricated "Key Insights" table | EDA Lead | Fix RL-1, BA-1 |
| 2.2 | Add data validation cell (shape, date range, nulls) | EDA Researcher | Fix DS-3 |
| 2.3 | Diversify chart types (ridge, radar, small multiples) | EDA Lead | Fix Q2, VE-1 |
| 2.4 | Add annotations/finding callouts to all charts | EDA Researcher | Fix Q1, VE-2 |
| 2.5 | Add volume context to arrest rate charts | EDA Lead | Fix Q3, BA-2 |
| 2.6 | Fix location type analysis (show all, not "Top 15") | EDA Researcher | Fix Q4 |
| 2.7 | Fix community diversity (Shannon entropy) | EDA Lead | Fix Q5 |
| 2.8 | Add Cramér's V alongside chi-square | EDA Researcher | Fix I4, DS-1 |
| 2.9 | Add Chicago boundaries to hotspot map | EDA Researcher | Fix I2 |
| 2.10 | Extend correlation to full 10×10 matrix | EDA Lead | Fix I3 |
| 2.11 | Add 7-day moving average to temporal charts | EDA Researcher | Fix I1 |
| 2.12 | Add finding callout boxes (text annotations) | EDA Lead | Fix Q1 |

### Phase 3: Reports Update (EDA Lead)
**Duration:** 0.5 sprint
**Priority:** HIGH

| Step | Task | Owner |
|:----:|------|-------|
| 3.1 | Re-audit all 39 reports against new output | EDA Lead |
| 3.2 | Fix any fabricated findings | EDA Lead |
| 3.3 | Update statistics (p-values, CIs) in reports | EDA Lead |
| 3.4 | Add volume context to arrest rate reports | EDA Lead |
| 3.5 | Update INDEX.md | EDA Lead |

### Phase 4: Re-Assessment (QA + Critic)
**Duration:** 0.5 sprint
**Priority:** HIGH

| Step | Task | Owner |
|:----:|------|-------|
| 4.1 | Re-run S1 + S2 hard-block checks | QA Agent |
| 4.2 | Re-score all 19 criteria | Critic Agent |
| 4.3 | Update evaluation.md | QA Agent |
| 4.4 | Update evidence.md | QA Agent |
| 4.5 | Present to user for approval | QA Agent |

---

## Expected Score Impact

| Category | Current | After Fix | Rationale |
|----------|:-------:|:---------:|-----------|
| **DS-1** | 9 | **8→9** | Effect sizes added; data validation checks |
| **DS-2** | 9 | **9** | 170k+ records across 3 years |
| **DS-3** | 9 | **9** | Seed + execution + validation |
| **DS-4** | 8 | **9** | Assumptions + effect sizes |
| **RL-1** | 8 | **9** | Non-trivial cross-tabulations |
| **RL-2** | 7 | **8** | Novel patterns from conditional data |
| **RL-3** | 9 | **9** | Recommendations remain strong |
| **VE-1** | 9 | **9** | Chart diversity improved |
| **VE-2** | 9 | **9** | Annotations added |
| **VE-3** | 8 | **9** | CB8 palette applied to all charts |
| **VE-4** | 8 | **9** | Better density from diverse charts |
| **BA-1** | 9 | **9** | Numbers remain precise |
| **BA-2** | 9 | **9** | CIs + effect sizes added |
| **BA-3** | 9 | **9** | Caveats remain strong |
| **BA-4** | 8 | **9** | Benchmarks validated against real data |
| **PR-1** | 9 | **9** | Documentation complete |
| **PR-2** | 9 | **9** | Template consistent |
| **PR-3** | 8 | **9** | Methodology references strengthened |

**Target Composite: 9.0+ (Grade A)**

---

## Files Modified

| File | Change |
|------|--------|
| `scripts/synth_data.py` | Fix data generation (Phase 1) |
| `data/*.csv` | Regenerated (Phase 1) |
| `scripts/notebooks/M7_EDA.ipynb` | Overhaul (Phase 2) |
| `reports/eda/**/*.md` | Update findings (Phase 3) |
| `docs/eda-assessment/evaluation.md` | Re-score (Phase 4) |
| `docs/eda-assessment/evidence.md` | Update evidence (Phase 4) |
| `docs/milestones/M7-bugs-quirks.md` | This document |
