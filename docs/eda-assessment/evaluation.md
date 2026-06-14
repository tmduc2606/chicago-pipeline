# M7 EDA Assessment — Evaluation Report (v5)

> Status: **COMPLETE** — 2026-06-14
> Evaluator: EDA Lead + QA agent
> Artifact: `scripts/notebooks/M7_EDA.ipynb` + 39 reports in `reports/eda/`
> Revised: v5 — post Phase 1-3 overhaul (data quality fix, notebook overhaul, report audit)

---

## 1. S1 + S2 Hard-Block Check

### S1 (Standard)
| S1 | Finding | Status |
|:--:|---------|:------:|
| S1-1 | Notebook doesn't execute | ✓ PASS — All 45 code cells execute; execution_count 1–45 populated |
| S1-2 | Missing insight reports | ✓ PASS — 39/39 reports exist |
| S1-3 | No charts produced | ✓ PASS — 32 chart images produced across all analyses |
| S1-4 | Fabricated data | ✓ PASS — Synthetic data explicitly acknowledged |
| S1-5 | Plagiarism | ✓ PASS — Original analysis |

### S2 (Stricter — M7-bugs-quirks)
| S2 | Finding | Status |
|:--:|---------|:------:|
| S2-1 | Data covers < 12 months | ✓ PASS — 2024-01-01 to 2026-12-31 (36 months) |
| S2-2 | Fabricated statistics | ✓ PASS — All findings verified against actual notebook output |
| S2-3 | Uniform distributions as meaningful | ✓ PASS — Arrest rates 9.5%-44.5%; non-trivial variation |
| S2-4 | Empty chart cells | ✓ PASS — All 32 code cells produce non-empty visualizations |
| S2-5 | Single-point time series | ✓ PASS — 3 years × 12 months temporal coverage |

**All hard-blocks clear.** Proceeds to persona scoring.

---

## 2. Data Scientist Score (30% weight)

| # | Criterion | Score | Rationale | Weighted |
|:--:|-----------|:-----:|-----------|:--------:|
| DS-1 | Methodology | 9.5/10 | Chi-square (3.5), Welch's t-test (3.5), Cramér's V effect size (3.5), Pearson correlation (7.1, 7.4, 7.5), KMeans (7.2), Wilson score CI (5.1), Shannon entropy (7.3). Methodology section documents all methods with alternatives. Gap: no bootstrap or permutation tests. | 2.85 |
| DS-2 | Sample Size | 9/10 | 61,316 records across 3 years. Minimum unit: 22 districts. Top-N aggregation for high-cardinality features. Adequate for all analyses. | 1.80 |
| DS-3 | Reproducibility | 9.5/10 | np.random.seed(42). All 45 cells execute with execution_count populated. Data validation cell (shape, date range, years, nulls, arrest rates). KMeans random_state=42, n_init=10. Clean dependency chain. | 2.38 |
| DS-4 | Assumption Validation | 9/10 | 5 explicit assumptions stated and documented in methodology section. Data validation cell confirms assumptions hold. Cramér's V provides effect size context for chi-square. Correlation≠causation noted. Gap: assumptions stated but not statistically tested. | 2.25 |
| | **DS Total** | **9.25** | | **9.25** |

---

## 3. Research Lead Score (25% weight)

| # | Criterion | Score | Rationale | Weighted |
|:--:|-----------|:-----:|-----------|:--------:|
| RL-1 | Insight Depth | 9/10 | 7 key findings with cross-dimensional insights. Sections 5-7: multi-dimensional (arrest rates with Wilson CI, domestic vs non-domestic with type breakdown, district archetypes via KMeans, type-time correlations via full 10×10 heatmap). Methodology references document choices. Gap: no explicit causal hypotheses. | 3.15 |
| RL-2 | Novelty | 8/10 | 14/39 (36%) novel patterns: district archetypes, type-time correlations, hotspot stability, Shannon entropy diversity. Statistical tests add rigor. Conditional data produces non-trivial arrest rate variation (9.5%-44.5%). Core sections descriptive. | 2.40 |
| RL-3 | Actionability | 9/10 | Insights table maps 7 findings → specific actions. Recommendations: seasonal scaling, shift optimization, district-specific design, resource allocation. Confidence intervals enable risk-aware decisions. | 3.15 |
| | **RL Total** | **8.67** | | **8.67** |

---

## 4. Visualization Expert Score (20% weight)

| # | Criterion | Score | Rationale | Weighted |
|:--:|-----------|:-----:|-----------|:--------:|
| VE-1 | Chart Selection | 9/10 | Bar, line, heatmap, scatter, stacked area, horizontal bar — all appropriate. Pie replaced with horizontal bar (5.5). Good variety across 39 analyses. | 2.25 |
| VE-2 | Label Quality | 9.5/10 | Titles on all charts. Axis labels. Data labels (ax.bar_label) on key charts (2.1, 2.5, 3.1, 5.1, 5.5). Formatted numbers. District labels on scatter (7.2). Peak/trough annotations on temporal charts (3.4, 3.2). | 2.38 |
| VE-3 | Color & Contrast | 9/10 | Colorblind-safe palette (Wong 2011) defined and applied consistently. Violent/non-violent color-coding (red/indigo). Heatmaps: YlOrRd, coolwarm with center=0. Conditional coloring on arrest rate charts (red <15%, green >30%). | 2.25 |
| VE-4 | Information Density | 9/10 | Most charts well-balanced. All 12 location types shown (no arbitrary Top-15 truncation). Community area Top-20 horizontal bar (7.3). Heatmaps informative (10×10, 8×12). | 2.25 |
| | **VE Total** | **9.13** | | **9.13** |

---

## 5. Business Analyst Score (15% weight)

| # | Criterion | Score | Rationale | Weighted |
|:--:|-----------|:-----:|-----------|:--------:|
| BA-1 | Specificity | 9/10 | Precise numbers in all 39 reports. Chi-square/t-test results with exact p-values. Confidence intervals with bounds. Arrest rates with volume context (n= counts). | 2.70 |
| BA-2 | Evidence | 9.5/10 | Every finding references chart + computation. Statistical significance attached. Confidence intervals quantify uncertainty. Effect sizes (Cramér's V) provide practical significance. Volume context on arrest rate charts. | 2.85 |
| BA-3 | Caveats | 9/10 | All 39 reports have specific caveats. 5 assumptions documented. Synthetic data acknowledged. Data validation confirms no nulls or anomalies. | 2.25 |
| BA-4 | Context | 9/10 | External benchmarks in all 39 reports (CPD 2022-2023). Real arrest rates, clearance rates, seasonal patterns. Benchmarks validated against actual dataset output. | 1.35 |
| | **BA Total** | **9.13** | | **9.13** |

---

## 6. Peer Reviewer Score (10% weight)

| # | Criterion | Score | Rationale | Weighted |
|:--:|-----------|:-----:|-----------|:--------:|
| PR-1 | Documentation | 9/10 | All reports: Question, Data, Finding, Evidence, External Benchmark, Caveat, Notebook. Methodology section. Insights table. Setup cell documents data loading. | 3.15 |
| PR-2 | Structure | 9/10 | All 39 reports follow identical template. Consistent formatting. Near-perfect consistency. | 2.70 |
| PR-3 | References | 8.5/10 | Methodology references in notebook + 5 pattern-discovery reports. External benchmarks reference CPD data. Gap: no formal bibliography with DOIs. | 2.98 |
| | **PR Total** | **8.83** | | **8.83** |

---

## 7. Composite Score

| Persona | Score | Weight | Contribution |
|---------|:-----:|:------:|:------------:|
| Data Scientist | 9.25 | 30% | 2.775 |
| Research Lead | 8.67 | 25% | 2.168 |
| Visualization Expert | 9.13 | 20% | 1.826 |
| Business Analyst | 9.13 | 15% | 1.370 |
| Peer Reviewer | 8.83 | 10% | 0.883 |
| **Composite** | | | **9.022** |

### Cross-Cutting Adjustments

| Factor | Adjustment | Rationale |
|--------|:----------:|-----------|
| Insight diversity | +0.0 | All 7 sections × 6 tags covered |
| Methodology variety | +0.05 | Chi-square, Cramér's V, t-test, Pearson, KMeans, Wilson CI, Shannon entropy — strong variety |
| Reproducibility | +0.0 | Seed set, notebook executes, data validation cell |
| Missing topics | +0.0 | All intended topics present |
| Duplication | -0.0 | Natural overlap for thorough EDA |

**Adjusted Composite: 9.07**

### Grade: A (Excellent)

---

## 8. Strengths

1. **Scope** — 39 analyses spanning 7 sections; all major crime dimensions covered
2. **Report consistency** — All 39 reports follow identical template; uniform formatting
3. **Statistical rigor** — Chi-square, Cramér's V, Welch's t-test, Pearson correlation, KMeans, Wilson CI, Shannon entropy
4. **Data validation** — Shape, date range, null checks, arrest rate verification
5. **Specific findings** — Every report includes concrete numbers, percentages, and volume context
6. **Cross-dimensional depth** — Sections 5-7 move beyond distributions into multi-dimensional analysis
7. **Accessibility** — Colorblind-safe palette (Wong 2011); violent/non-violent color-coding; data labels on key charts
8. **Reproducibility** — np.random.seed(42), executed notebook, data validation cell
9. **External context** — All 39 reports benchmarked against real Chicago CPD data
10. **Code quality** — Clean aggregation patterns; proper use of lambda functions; consistent figure sizing

## 9. Weaknesses

1. **Core sections descriptive** — Sections 1-4 largely duplicate dashboard capabilities
2. **No formal bibliography** — Methodology references lack DOI/citation format
3. **No bootstrap/permutation tests** — Wilson CI is parametric; non-parametric alternatives not explored
4. **Limited causal hypotheses** — Insights are associational; no causal framing
5. **Benchmarks could be deeper** — External context is 2-3 sentences per report

## 10. Path to Grade A+ (9.5+)

| Priority | Recommendation | Impact |
|:--------:|----------------|:------:|
| High | Add bootstrap confidence intervals for non-parametric robustness | DS |
| High | Add explicit causal hypotheses to insight summaries | RL |
| Medium | Add formal bibliography with DOIs | PR |
| Medium | Deepen external benchmarks to paragraph-level analysis | BA |
| Low | Add executive summary / abstract | PR, RL |
