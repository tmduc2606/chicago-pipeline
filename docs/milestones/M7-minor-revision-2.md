# Minor Revision M7 | No.2

> Status: **PROPOSAL** — Awaiting approval
> Date: 2026-06-13
> Basis: M7 EDA Assessment v2 — Grade C (6.26)
> Goal: Raise composite from C (6.26) toward B- (7.0+) through targeted fixes

---

## 1. Assessment Gap Summary

| Persona | Current | Target | Gap | Key Criteria to Fix |
|---------|:-------:|:------:|:---:|---------------------|
| Data Scientist | 5.95 | 7.0+ | +1.05 | DS-3 Reproducibility (5→7), DS-4 Assumptions (4→5), DS-1 Methodology (7→8) |
| Research Lead | 6.35 | 7.0+ | +0.65 | RL-3 Actionability (6→7) |
| Visualization Expert | 6.25 | 7.5+ | +1.25 | VE-2 Labels (6→8), VE-3 Color (5→7), VE-4 Density (7→8) |
| Business Analyst | 7.10 | 7.5+ | +0.40 | BA-4 Context (4→5) |
| Peer Reviewer | 6.20 | 7.0+ | +0.80 | PR-3 References (2→4), PR-1 Documentation (8→9) |

---

## 2. Fixes by Priority

### HIGH — Reproducibility & Execution (DS-3: 5→7)

| # | Fix | File | Detail | Est. Impact |
|---|-----|------|--------|:-----------:|
| H1 | Add global random seed | `M7_EDA.ipynb` setup cell | Add `np.random.seed(42)` after imports | DS-3 +1 |
| H2 | Execute notebook | `M7_EDA.ipynb` | Run all cells, verify output, commit populated notebook | DS-3 +1, DS-4 +1 |

**Before:**
```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')
```

**After:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)
```

**Expected score change:** DS-3 5→7 (+0.50 weighted)

---

### MEDIUM — Chart Quality (VE-2: 6→8, VE-3: 5→7, VE-4: 7→8)

| # | Fix | File | Detail | Est. Impact |
|---|-----|------|--------|:-----------:|
| M1 | Add data labels to key bar charts | `M7_EDA.ipynb` cells 2.1, 4.1, 5.1 | Add `ax.bar_label(ax.containers[0])` or `ax.text()` annotations on top 5 bar charts | VE-2 +1 |
| M2 | Color-code violent vs non-violent | `M7_EDA.ipynb` cells 2.1, 3.6 | Apply red palette for violent (BATTERY, ASSAULT, ROBBERY), blue for non-violent (THEFT, NARCOTICS, etc.) | VE-3 +1 |
| M3 | Fix community area chart crowding | `M7_EDA.ipynb` cell 7.3 | Change to horizontal bar chart OR Top-20 + "Other" aggregation | VE-4 +1 |
| M4 | Add methodology references | `M7_EDA.ipynb` cells 7.1, 7.2, 7.4 | Add markdown cells citing sklearn KMeans, Pearson correlation before respective analyses | PR-3 +1 |

**Chart fixes detail:**

Cell 2.1 (Distribution by Primary Type):
```python
# Before: no annotations
type_counts.plot(kind='bar', ax=ax, color='#6366f1')

# After: add value labels
bars = type_counts.plot(kind='bar', ax=ax, color='#6366f1')
ax.bar_label(ax.containers[0], fmt='%d', fontsize=8)
```

Cell 7.3 (Community Area Diversity):
```python
# Before: 77 vertical bars, crowded
ax.bar(comm_diversity['community_area'].astype(str), comm_diversity['n_types'], color='#6366f1')
plt.xticks(rotation=90)

# After: horizontal bar, Top-20
top20 = comm_diversity.head(20)
ax.barh(top20['community_area'].astype(str), top20['n_types'], color='#6366f1')
ax.set_xlabel('Number of Unique Crime Types')
```

**Expected score change:** VE-2 6→8, VE-3 5→7, VE-4 7→8 (+0.70 weighted)

---

### MEDIUM — References & Documentation (PR-3: 2→4, PR-1: 8→9)

| # | Fix | File | Detail | Est. Impact |
|---|-----|------|--------|:-----------:|
| M5 | Add methodology references | `M7_EDA.ipynb` | Before Section 7, add markdown cell with methodology notes | PR-3 +1 |
| M6 | Add data dictionary reference | `reports/eda/INDEX.md` | Add brief table of warehouse columns used in analyses | PR-1 +0 |

**Proposed methodology cell (before Section 7):**
```markdown
### Methodology Notes

- **Correlation analysis (7.1, 7.4, 7.5):** Pearson correlation coefficient computed on
  aggregated district-level counts. Correlation does not imply causation.
  Reference: `scipy.stats.pearsonr` / pandas `.corr()`.

- **KMeans clustering (7.2):** K=4 chosen for interpretability. Features standardized
  using `sklearn.preprocessing.StandardScaler` before clustering.
  Reference: sklearn KMeans documentation.

- **Heatmaps (6.2-6.4, 7.1, 7.5):** Seaborn `heatmap()` with `YlOrRd` or `coolwarm`
  colormap. Color intensity represents count or proportion.
```

**Expected score change:** PR-3 2→4 (+0.20 weighted)

---

### LOW — Context & Statistical Testing (BA-4: 4→5, DS-1: 7→8)

| # | Fix | File | Detail | Est. Impact |
|---|-----|------|--------|:-----------:|
| L1 | Add external context benchmarks | `reports/eda/*.md` | Add 1-2 sentences per report comparing to known Chicago crime patterns where applicable | BA-4 +1 |
| L2 | Add chi-square test on day-of-week | `M7_EDA.ipynb` cell 3.5 | Run `scipy.stats.chi2_contingency` on weekday distribution | DS-1 +1 |

**L1 detail — contextual benchmarks to add:**

| Report | Benchmark to reference |
|--------|----------------------|
| 1.1 (Total records) | "Real CPD data typically has 250K-300K+ records per year" |
| 2.1 (Primary type) | "THEFT is consistently the #1 crime type in real Chicago data" |
| 3.9 (Seasonal) | "Real Chicago crime data shows strong summer peaks (July-August)" |
| 3.10 (Weekday/weekend) | "Real data shows stronger Friday/Saturday peaks for violent crime" |
| 5.1 (Arrest rate by type) | "Real CPD arrest rates vary from 5% (THEFT) to 50%+ (narcotics)" |
| 5.5 (Domestic) | "Real domestic violence reports constitute ~12-15% of total crime" |

**L2 detail — chi-square test cell:**
```python
from scipy.stats import chi2_contingency

day_counts = df['weekday'].value_counts().reindex(
    ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
)
chi2, p_value, dof, expected = chi2_contingency(
    pd.crosstab(df['is_weekend'], df['weekday'])
)
print(f'Chi-square statistic: {chi2:.2f}')
print(f'p-value: {p_value:.4f}')
print(f'Degrees of freedom: {dof}')
```

**Expected score change:** BA-4 4→5, DS-1 7→8 (+0.20 weighted)

---

## 3. Report Updates Required

After notebook changes, these reports need corresponding updates:

| Report | Change | Reason |
|--------|--------|--------|
| `reports/eda/INDEX.md` | Update methodology note | New references section |
| `reports/eda/overview/01-total-records.md` | Add external benchmark to Finding | BA-4 improvement |
| `reports/eda/distribution/01-by-primary-type.md` | Add external benchmark to Finding | BA-4 improvement |
| `reports/eda/temporal/09-seasonal-pattern.md` | Add external benchmark to Finding | BA-4 improvement |
| `reports/eda/temporal/10-weekday-vs-weekend.md` | Add external benchmark to Finding | BA-4 improvement |
| `reports/eda/arrest-domestic/01-arrest-rate-by-type.md` | Add external benchmark to Finding | BA-4 improvement |
| `reports/eda/arrest-domestic/05-domestic-vs-non-domestic.md` | Add external benchmark to Finding | BA-4 improvement |
| `reports/eda/pattern-discovery/01-crime-co-occurrence.md` | Add methodology reference to Caveat | PR-3 improvement |
| `reports/eda/pattern-discovery/02-neighborhood-clustering.md` | Add methodology reference to Caveat | PR-3 improvement |
| `reports/eda/pattern-discovery/04-type-time-correlation.md` | Add methodology reference to Caveat | PR-3 improvement |

---

## 4. Expected Score Improvement

| Persona | Current | Fix Contribution | Expected After |
|---------|:-------:|:----------------:|:--------------:|
| Data Scientist | 5.95 | H1+H2: +0.50, L2: +0.10 | **6.55** |
| Research Lead | 6.35 | L1 (partial): +0.10 | **6.45** |
| Visualization Expert | 6.25 | M1+M2+M3: +0.70 | **6.95** |
| Business Analyst | 7.10 | L1: +0.15 | **7.25** |
| Peer Reviewer | 6.20 | M5: +0.20 | **6.40** |

| | Composite |
|---|:---------:|
| Current | 6.26 |
| Expected | **6.70** |
| Target Grade | C+ (6.5–6.9) |

---

## 5. Implementation Order

| Step | What | Files | Depends On |
|:----:|------|-------|:----------:|
| 1 | Add global random seed | `M7_EDA.ipynb` setup cell | — |
| 2 | Add methodology references markdown cell | `M7_EDA.ipynb` before Section 7 | — |
| 3 | Add data labels to key bar charts | `M7_EDA.ipynb` cells 2.1, 4.1, 5.1 | — |
| 4 | Color-code violent vs non-violent | `M7_EDA.ipynb` cells 2.1, 3.6 | — |
| 5 | Fix community area chart (horizontal bar, Top-20) | `M7_EDA.ipynb` cell 7.3 | — |
| 6 | Add chi-square test cell | `M7_EDA.ipynb` after cell 3.5 | — |
| 7 | Execute full notebook, verify output | `M7_EDA.ipynb` all cells | Steps 1-6 |
| 8 | Update reports with external benchmarks | 6 reports in `reports/eda/` | Step 7 |
| 9 | Update INDEX.md with methodology note | `reports/eda/INDEX.md` | Step 2 |
| 10 | Run lint + TypeScript check | `ruff`, `npx tsc --noEmit` | Steps 1-9 |

---

## 6. Files Modified

| File | Change Type |
|------|:-----------:|
| `scripts/notebooks/M7_EDA.ipynb` | Modified (seed, labels, colors, methods, chi-square, executed) |
| `reports/eda/INDEX.md` | Modified (methodology note) |
| `reports/eda/overview/01-total-records.md` | Modified (benchmark) |
| `reports/eda/distribution/01-by-primary-type.md` | Modified (benchmark) |
| `reports/eda/temporal/09-seasonal-pattern.md` | Modified (benchmark) |
| `reports/eda/temporal/10-weekday-vs-weekend.md` | Modified (benchmark) |
| `reports/eda/arrest-domestic/01-arrest-rate-by-type.md` | Modified (benchmark) |
| `reports/eda/arrest-domestic/05-domestic-vs-non-domestic.md` | Modified (benchmark) |
| `reports/eda/pattern-discovery/01-crime-co-occurrence.md` | Modified (methodology reference) |
| `reports/eda/pattern-discovery/02-neighborhood-clustering.md` | Modified (methodology reference) |
| `reports/eda/pattern-discovery/04-type-time-correlation.md` | Modified (methodology reference) |

---

## 7. Verification

- [ ] `np.random.seed(42)` present in setup cell
- [ ] `execution_count` populated on all cells (notebook executed)
- [ ] Value annotations on bar charts 2.1, 4.1, 5.1
- [ ] Violent/non-violent color coding on charts 2.1, 3.6
- [ ] Community area chart is horizontal bar, Top-20
- [ ] Methodology markdown cell before Section 7
- [ ] Chi-square test cell present with output
- [ ] 6 reports updated with external benchmarks
- [ ] 3 reports updated with methodology references
- [ ] `ruff check M7_EDA.ipynb` clean
- [ ] `npx tsc --noEmit` clean
- [ ] `python -c "import json; json.load(open('web/src/config/insights.json'))"` valid

---

*Awaiting approval to proceed.*
