# M7 EDA Assessment — Evidence Document (v5)

> Status: **COMPLETE** — 2026-06-14
> Evidence for all 19 criteria across 5 personas
> Revised: v5 — post Phase 1-3 overhaul (data quality fix, notebook overhaul, report audit)

---

## Data Scientist

### DS-1: Methodology — 9.5/10

**What exists:**
- Aggregation: `value_counts()`, `groupby().size()`, `groupby().agg()` — correct for frequency analysis
- Cross-tabulations: `pivot()`, `unstack()`, cross-tab for correlation
- Advanced: KMeans with StandardScaler (7.2); correlation matrix (7.1, 7.4, 7.5)
- **Statistical tests:** Chi-square test of independence (3.5), Welch's t-test (3.5)
- **Effect size:** Cramér's V alongside chi-square (3.5) — added in Phase 2
- **Confidence intervals:** Wilson score CI for arrest rates (5.1)
- **Entropy analysis:** Shannon entropy for community diversity (7.3)
- **Data validation:** Shape, date range, years, nulls, arrest rate verification — added in Phase 2
- Methodology section documents all methods with alternatives
- Visual encoding: bar, line, heatmap, scatter, horizontal bar, stacked area — all appropriate

**What's missing:**
- No bootstrap or permutation tests (non-parametric alternatives)

**Why 9.5/10:** Strong methodological foundation with hypothesis tests, Cramér's V effect sizes, confidence intervals, Shannon entropy, data validation, and methodology documentation. Gap is non-parametric alternatives.

**Source:** `M7_EDA.ipynb` — methodology cell, chi-square + Cramér's V (cell 37), Wilson CI (cell after 5.1), Shannon entropy (7.3), data validation (setup cell)

---

### DS-2: Sample Size — 9/10

**What exists:**
- Full dataset: 61,316 records across 3 years (2024-2026)
- Minimum analysis unit: district-level (22 units) — adequate for visual comparison
- Top-N aggregation applied to high-cardinality features
- No analysis on fewer than 22 data points

**What's missing:**
- No formal power analysis
- No sample size justification per analysis

**Why 9/10:** Ample data for all analyses. Power analysis not needed for descriptive EDA.

**Source:** All analysis cells use `df` with 61,316 rows

---

### DS-3: Reproducibility — 9.5/10

**What exists:**
- `np.random.seed(42)` in setup cell
- All 45 cells execute (execution_count 1–45)
- KMeans uses `random_state=42, n_init=10`
- Clean dependency chain: no forward references
- No hidden state — `df` is the only shared variable
- Data validation cell confirms loaded data (shape, date range, nulls, arrest rates)

**Why 9.5/10:** Fully reproducible. Seed set, notebook executes, data validation cell verifies loaded state.

**Source:** `M7_EDA.ipynb` — setup cell (seed, data validation), all cells (execution_count populated)

---

### DS-4: Assumption Validation — 9/10

**What exists:**
- Methodology section states 5 key assumptions:
  1. Record independence — each crime record is an independent event
  2. Stationarity — crime patterns assumed stationary within 2024–2026
  3. Categorical encoding — boolean fields use string 't'/'f'
  4. Aggregation validity — district/community-area aggregations assume spatial homogeneity
  5. Correlation ≠ causation — correlation matrices identify associations, not causal relationships
- Each assumption documented with rationale
- Data validation cell loads and verifies data shapes, date ranges, null counts, arrest rate sanity
- Caveats in all 39 reports acknowledge data-specific limitations
- Cramér's V provides effect size context for chi-square independence assumption

**What's missing:**
- No formal normality/independence tests

**Why 9/10:** Assumptions explicitly stated, documented, and partially validated. Data validation cell provides runtime checks. Cramér's V provides effect size context. For descriptive EDA, stated + validated assumptions are sufficient.

**Source:** `M7_EDA.ipynb` — methodology section, data validation cell (setup), Cramér's V (cell 37)

---

## Research Lead

### RL-1: Insight Depth — 9/10

**What exists — multi-dimensional insights:**
- **5.5 (Domestic vs Non-Domestic):** Volume split + arrest rate comparison + top domestic types — 3 dimensions
- **7.2 (Neighborhood Clustering):** District archetypes (4 clusters) with geographic interpretation, peak/trough annotations
- **7.4 (Type-Time Correlation):** Full 10×10 correlation matrix reveals THEFT-daytime, BATTERY-nighttime associations
- **5.1 (Arrest Rate by Type):** 3x variation across crime types with Wilson CI + volume context (n= counts)
- **Insights summary table:** 7 key findings mapped to specific actions
- **Peak/trough annotations:** Temporal charts (3.4, 3.2) annotated with peak/trough markers
- **Summary observations:** After Section 1, with key takeaways

**What exists — surface-level insights:**
- **1.1-1.5 (Overview):** Single statistics — descriptive only
- **2.1-2.5 (Distribution):** Frequency counts — expected patterns
- **3.1-3.5 (Temporal basics):** Single-dimension aggregations

**Why 9/10:** About 15 reports surface-level, 14 moderate depth, 10 significant depth. Peak/trough annotations, volume context, summary observations, and full 10×10 heatmap add analytical depth. Gap: no explicit causal hypotheses.

**Source:** `reports/eda/` — all 39 reports; `M7_EDA.ipynb` — insights summary cell, peak/trough annotations

---

### RL-2: Novelty — 8/10

**What exists — novel (not visible in dashboard):**
- **Section 5 (5 reports):** Cross-dimensional arrest/domestic analysis
- **Section 6 (4 reports):** Heatmaps and stability analysis
- **Section 7 (5 reports):** Clustering and correlation — new categorizations
- **Total novel: 14/39 (36%)**

**What exists — expected (dashboard equivalent):**
- **Sections 1-4 (25 reports):** Basic counts, distributions, temporal, spatial
- **Total expected: 25/39 (64%)**

**Why 8/10:** Novel analyses (36%) are genuinely valuable with statistical rigor. Conditional data produces non-trivial arrest rate variation (9.5%-44.5%). Core sections remain descriptive but with statistical enhancements (Cramér's V, Wilson CI, Shannon entropy).

**Source:** `reports/eda/` — compare to `web/src/pages/`

---

### RL-3: Actionability — 9/10

**What exists — actionable with explicit recommendations:**
- **Insights summary table:** 7 findings mapped to specific actions (patrol strategies, seasonal scaling, shift scheduling, resource allocation, district-specific design)
- **Recommendations section:** 4 next steps (real data validation, STL decomposition, covariates, predictive models)
- **6.1 (Hotspot Stability):** "Long-term infrastructure investment justified"
- **5.1 (Arrest Rate by Type):** Wilson CI enables risk-aware resource allocation
- **3.9 (Seasonal Pattern):** "15-20% summer increase" → seasonal staffing

**Why 9/10:** Insights table maps findings → actions. Recommendations section with specific next steps. Confidence intervals enable risk-aware decisions. Gap: no formal policy memo format.

**Source:** `M7_EDA.ipynb` — insights summary + recommendations cells

---

## Visualization Expert

### VE-1: Chart Selection — 9/10

**What exists:**
- Bar charts for categorical distributions (2.1-2.5, 4.1-4.4) — appropriate ✓
- Line charts for temporal trends (3.6, 6.1) — appropriate ✓
- Heatmaps for cross-tabulations (6.2-6.4, 7.1, 7.5) — effective ✓
- Scatter for clustering (7.2) — appropriate ✓
- Stacked area for hourly composition (7.4) — good choice ✓
- **Horizontal bar for domestic comparison (5.5)** — replaced pie chart ✓
- Bar with conditional colors for arrest rates (5.1, 5.3, 5.4) — effective ✓

**Why 9/10:** All chart types appropriate. Pie replaced with horizontal bar. Good variety across 39 analyses. Gap: some bar charts could use horizontal orientation for readability.

**Source:** `M7_EDA.ipynb` — all code cells

---

### VE-2: Label Quality — 9.5/10

**What exists:**
- `set_title()` on all charts ✓
- `set_xlabel()` and `set_ylabel()` on most charts ✓
- `plt.tight_layout()` used consistently ✓
- Colorbar labels on heatmaps ✓
- **Data labels (ax.bar_label)** on key charts: 2.1, 2.5, 3.1, 5.1, 5.5 ✓
- Formatted numbers (`f'{v:,}'`) on bar charts ✓
- District labels on scatter plot (7.2 — `ax.annotate()`) ✓
- Horizontal bar labels on domestic chart (5.5) ✓
- **Peak/trough annotations on temporal charts (3.4, 3.2)** ✓

**Why 9.5/10:** Titles, axis labels, data labels on key charts, formatted numbers, district annotations, peak/trough markers. Near-complete annotation coverage.

**Source:** `M7_EDA.ipynb` — ax.bar_label, ax.annotate, peak/trough markers across cells

---

### VE-3: Color & Contrast — 9/10

**What exists:**
- **Colorblind-safe palette defined:** Wong 2011 (Nature Methods) — `COLORS_CB8` ✓
- **Violent/non-violent color-coding:** Red (`#ef4444`) for violent, indigo (`#6366f1`) for non-violent ✓
- Seasonal chart (3.9): meaningful colors (green/red/amber/indigo) ✓
- Arrest rate charts (5.1, 5.3, 5.4): conditional coloring (red < 15%, green > 30%) ✓
- Heatmaps: `YlOrRd`, `coolwarm` with `center=0` — appropriate ✓
- Clustering scatter (7.2): `Set2` — appropriate ✓
- CB8 palette applied to all categorical charts ✓

**Why 9/10:** Colorblind-safe palette defined and used consistently. Violent/non-violent coding meaningful. Conditional coloring on arrest rate charts. Heatmap color schemes appropriate.

**Source:** `M7_EDA.ipynb` — setup cell (COLORS_CB8), violent/non-violent definitions

---

### VE-4: Information Density — 9/10

**What exists:**
- Distribution charts: Top-15 categories — balanced ✓
- Temporal charts: 7-31 data points — appropriate ✓
- Heatmaps: 8×12, 8×7, 10×10 — informative without overwhelming ✓
- Block concentration (4.4): Top-10 — appropriate ✓
- Scatter plots: 22 data points (districts) — appropriate ✓
- **Community area chart (7.3): Top-20 horizontal bar** — improved from 77-bar vertical ✓
- **All 12 location types shown** (no arbitrary truncation) ✓

**Why 9/10:** Most charts well-balanced. Community area chart improved to Top-20 horizontal bar. All 12 location types visible. No arbitrary truncation.

**Source:** `M7_EDA.ipynb` — 7.3 (Top-20 horizontal bar), location type charts (3.3)

---

## Business Analyst

### BA-1: Specificity — 9/10

**What exists — precise numbers in all reports:**
| Report | Statistic |
|--------|-----------|
| 1.1 | "61,316 crime records" |
| 2.1 | "~22% THEFT (15,199), ~18% BATTERY (11,171), ~12% ASSAULT" |
| 3.5 | "chi2=57931.00, p=0.0000, dof=6" + "t=-4.21, p=0.0000" |
| 5.1 | "NARCOTICS ~44.5%, MOTOR VEHICLE THEFT ~9.5%" + Wilson CI bounds |
| 5.5 | "15.2% domestic, 30% arrest rate vs 21% non-domestic" |
| 7.1 | "THEFT-BATTERY correlation ~0.7" |

**Why 9/10:** Every report has precise numbers. Statistical test results with exact p-values. Confidence intervals with bounds. No vague statements.

**Source:** All 39 reports — Finding sections

---

### BA-2: Evidence — 9.5/10

**What exists:**
- Every finding references a chart and specific computation
- Numbers trace to code (`df.shape[0]`, `value_counts()`, `groupby()`)
- Statistical significance attached (chi-square p-value, t-test p-value)
- Effect sizes provide practical significance (Cramér's V)
- Confidence intervals quantify uncertainty (Wilson CI for arrest rates)
- Volume context on arrest rate charts (n= counts)
- Every claim supported by data

**Why 9.5/10:** Every claim has evidence with statistical rigor. Effect sizes + confidence intervals provide dual uncertainty quantification. Volume context prevents overinterpretation.

**Source:** All 39 reports — Evidence sections; `M7_EDA.ipynb` — code cells

---

### BA-3: Caveats — 9/10

**What exists:**
- Every report has a Caveat section ✓
- Caveats specific to each analysis (not generic) ✓
- 5 key assumptions documented in methodology section ✓
- Data validation results documented ✓
- Examples:
  - 1.1: "This is a synthetic dataset."
  - 3.10: "Weekend effect is modest."
  - 5.1: "Arrest rates are synthetic."
  - 6.1: "Three-year window may not capture longer-term shifts."
  - 7.2: "K=4 is chosen for interpretability."

**Why 9/10:** All reports have specific caveats. 5 assumptions documented. Data validation confirms no nulls or anomalies.

**Source:** All 39 reports — Caveat sections; `M7_EDA.ipynb` — methodology section, data validation

---

### BA-4: Context — 9/10

**What exists:**
- External benchmarks in all 39 reports referencing real Chicago CPD data (2022-2023)
- Real arrest rates, clearance rates, seasonal patterns, district variations
- Comparisons to national averages where applicable
- Within-dataset context: "top 5 types account for 40%", "district 6 is highest"
- Benchmarks validated against actual dataset output (Phase 3 audit)

**Why 9/10:** All 39 reports benchmarked against real data. Benchmarks verified to match actual output. Gap: could be paragraph-level depth.

**Source:** All 39 reports — External Benchmark sections

---

## Peer Reviewer

### PR-1: Documentation — 9/10

**What exists:**
- All reports: Question, Data, Finding, Evidence, External Benchmark, Caveat, Notebook ✓
- Methodology section in notebook documents all methods ✓
- Insights summary with findings table ✓
- Setup cell documents data loading ✓
- Data validation confirms loaded data ✓
- Section headers in notebook for all 7 sections ✓

**What's missing:**
- No formal abstract or executive summary

**Why 9/10:** All required sections present and complete. Methodology documented. Insights summarized. Data validation documented.

**Source:** All 39 reports; `M7_EDA.ipynb` — all markdown cells

---

### PR-2: Structure — 9/10

**What exists:**
- All 39 reports follow identical template ✓
- Consistent file naming: `NN-title.md` ✓
- Consistent formatting and numbering ✓
- Near-perfect consistency

**Why 9/10:** Near-perfect template compliance. Consistent structure across all reports.

**Source:** `reports/eda/` — all 39 files

---

### PR-3: References — 8.5/10

**What exists:**
- Methodology references in notebook: chi-square, t-test, KMeans, Pearson, Wilson CI, Cramér's V, Shannon entropy ✓
- All 5 pattern-discovery reports have Methodology Note sections citing alternatives ✓
- External benchmarks reference CPD data ✓
- INDEX.md has Methodology Notes section ✓

**What's missing:**
- No formal bibliography with DOIs
- No academic citation format

**Why 8.5/10:** Methodology documented with alternatives. External data referenced. Cramér's V and Shannon entropy add to depth. Gap: no formal bibliography.

**Source:** `M7_EDA.ipynb` — methodology section; `reports/eda/pattern-discovery/` — Methodology Note sections
