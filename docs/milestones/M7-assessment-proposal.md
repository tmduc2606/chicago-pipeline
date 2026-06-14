# M7 EDA Separated Assessment — Evaluation Plan Proposal

> Status: **IMPLEMENTED** — 2026-06-13
> Date: 2026-06-12
> Scope: Purely Data Analysis & Visualizations criteria (M7 EDA Layer)

---

## 1. Design Philosophy

### 1.1 Why a Separate Assessment?

The existing M0-M6 assessment evaluates the **production system** (web app, API, pipeline) through personas focused on usability, trust, and real-world value. The M7 EDA Layer requires a **distinctive assessment** because:

| M0-M6 Assessment | M7 EDA Assessment |
|------------------|-------------------|
| Evaluates web application UI/UX | Evaluates notebook analysis quality |
| Personas: Citizen, Executive, Journalist | Personas: Data Scientist, Research Lead, Visualization Expert |
| Criteria: Filter responsiveness, chart readability | Criteria: Statistical rigor, insight depth, methodology |
| Focus: "Can I use this dashboard?" | Focus: "Is this analysis sound and actionable?" |
| Output: Web pages, API endpoints | Output: Notebook cells, insight reports, charts |

### 1.2 Core Principles

| Principle | Implementation |
|-----------|---------------|
| **Analysis-first** | Every criterion evaluates the quality of the analytical work, not the delivery mechanism |
| **Reproducibility** | Analyses must be reproducible from the notebook with clear inputs/outputs |
| **Insight specificity** | Findings must be specific (numbers, percentages, comparisons), not vague |
| **Caveat completeness** | Every analysis must acknowledge limitations and data quality issues |
| **Visualization effectiveness** | Charts must communicate clearly, not just exist |

---

## 2. Assessment Personas

### 2.1 Persona Definitions

| Persona | Weight | Perspective | Key Question |
|---------|--------|-------------|-------------|
| **Data Scientist** | 30% | "Is this analysis statistically sound?" | Methodology, rigor, reproducibility |
| **Research Lead** | 25% | "Are the insights actionable and novel?" | Depth, novelty, decision value |
| **Visualization Expert** | 20% | "Are the charts clear and effective?" | Clarity, accuracy, accessibility |
| **Business Analyst** | 15% | "Can I use this for decision-making?" | Specificity, evidence, caveats |
| **Peer Reviewer** | 10% | "Would this pass academic peer review?" | Completeness, documentation, standards |

### 2.2 Why These Personas?

- **Data Scientist** — Ensures statistical rigor and methodological soundness
- **Research Lead** — Ensures insights go beyond surface-level observations
- **Visualization Expert** — Ensures charts communicate effectively
- **Business Analyst** — Ensures findings are actionable for real decisions
- **Peer Reviewer** — Ensures academic-quality documentation and standards

---

## 3. Evaluation Criteria

### 3.1 Data Scientist Persona (30%)

**Perspective:** "Is this analysis statistically sound?"

| # | Criterion | 10 (Exceeds) | 7 (Acceptable) | 4 (Poor) | 0 (Not Present) | Weight |
|---|-----------|-------------|----------------|----------|-----------------|--------|
| DS-1 | **Methodology** — Appropriate statistical methods used | Methods match question type; assumptions validated | Standard methods applied correctly | Methods misapplied or inappropriate | No statistical methods | 30% |
| DS-2 | **Sample Size** — Adequate data for the analysis | All analyses use sufficient data; power analysis considered | Most analyses have adequate samples | Some analyses have small samples | Analyses without data validation | 20% |
| DS-3 | **Reproducibility** — Analysis can be reproduced from notebook | Notebook cells run independently; seeds set; no hidden state | Notebook runs top-to-bottom; minor issues | Notebook has execution dependencies | Notebook doesn't run | 25% |
| DS-4 | **Assumption Validation** — Statistical assumptions checked | Assumptions stated and tested (normality, independence) | Assumptions stated but not tested | Assumptions violated without acknowledgment | No assumption discussion | 25% |

**Scoring Formula:**
```
DS Score = (DS-1 × 0.30) + (DS-2 × 0.20) + (DS-3 × 0.25) + (DS-4 × 0.25)
```

### 3.2 Research Lead Persona (25%)

**Perspective:** "Are the insights actionable and novel?"

| # | Criterion | 10 (Exceeds) | 7 (Acceptable) | 4 (Poor) | 0 (Not Present) | Weight |
|---|-----------|-------------|----------------|----------|-----------------|--------|
| RL-1 | **Insight Depth** — Findings go beyond surface observations | Multi-dimensional insights; cross-tabulations; causal hypotheses | Clear patterns identified; some depth | Surface-level observations; only descriptive | No insights articulated | 35% |
| RL-2 | **Novelty** — Insights reveal non-obvious patterns | Novel findings not visible in dashboard; unexpected relationships | Some novel patterns; goes beyond M6 | Mostly what dashboard already shows | Duplicate of dashboard | 30% |
| RL-3 | **Actionability** — Findings inform concrete decisions | Clear recommendations; policy implications; resource allocation | Actionable for some stakeholders | Observations but no clear action | No actionable content | 35% |

**Scoring Formula:**
```
RL Score = (RL-1 × 0.35) + (RL-2 × 0.30) + (RL-3 × 0.35)
```

### 3.3 Visualization Expert Persona (20%)

**Perspective:** "Are the charts clear and effective?"

| # | Criterion | 10 (Exceeds) | 7 (Acceptable) | 4 (Poor) | 0 (Not Present) | Weight |
|---|-----------|-------------|----------------|----------|-----------------|--------|
| VE-1 | **Chart Selection** — Appropriate chart type for the data | Best chart type for the question; alternatives considered | Appropriate chart type used | Wrong chart type for the data | No charts | 25% |
| VE-2 | **Label Quality** — Axes, titles, legends are clear | All labels present; formatted numbers; units specified | Most labels present; minor issues | Missing labels or wrong format | Unlabeled charts | 25% |
| VE-3 | **Color & Contrast** — Color choices are effective and accessible | Colorblind-safe palette; meaningful color use; good contrast | Reasonable colors; some issues | Poor color choices; accessibility issues | Default/unconsidered colors | 25% |
| VE-4 | **Information Density** — Charts show appropriate amount of data | Right balance; not too sparse, not too cluttered | Acceptable density | Too sparse or too cluttered | Inappropriate density | 25% |

**Scoring Formula:**
```
VE Score = (VE-1 × 0.25) + (VE-2 × 0.25) + (VE-3 × 0.25) + (VE-4 × 0.25)
```

### 3.4 Business Analyst Persona (15%)

**Perspective:** "Can I use this for decision-making?"

| # | Criterion | 10 (Exceeds) | 7 (Acceptable) | 4 (Poor) | 0 (Not Present) | Weight |
|---|-----------|-------------|----------------|----------|-----------------|--------|
| BA-1 | **Specificity** — Findings include concrete numbers | Exact figures, percentages, comparisons; no vague language | Most findings have numbers | Some vague statements ("high", "low") | No specific numbers | 30% |
| BA-2 | **Evidence** — Every claim backed by data | Chart + numbers for every finding; clear data provenance | Most claims have evidence | Some unsupported claims | No evidence | 30% |
| BA-3 | **Caveats** — Limitations clearly stated | Every analysis has caveats; data quality issues flagged | Most analyses have caveats | Some missing caveats | No caveats | 25% |
| BA-4 | **Context** — Findings placed in broader context | Comparisons to benchmarks, industry standards, or baselines | Some context provided | Findings in isolation | No context | 15% |

**Scoring Formula:**
```
BA Score = (BA-1 × 0.30) + (BA-2 × 0.30) + (BA-3 × 0.25) + (BA-4 × 0.15)
```

### 3.5 Peer Reviewer Persona (10%)

**Perspective:** "Would this pass academic peer review?"

| # | Criterion | 10 (Exceeds) | 7 (Acceptable) | 4 (Poor) | 0 (Not Present) | Weight |
|---|-----------|-------------|----------------|----------|-----------------|--------|
| PR-1 | **Documentation** — Analysis is fully documented | Question, data, method, findings, caveats all documented | Most sections documented | Partial documentation | No documentation | 35% |
| PR-2 | **Structure** — Report follows consistent template | All reports follow template; consistent format | Most reports follow template | Inconsistent formatting | No template | 30% |
| PR-3 | **References** — Related work and limitations cited | References to methodology; limitations discussed | Some references | Minimal references | No references | 35% |

**Scoring Formula:**
```
PR Score = (PR-1 × 0.35) + (PR-2 × 0.30) + (PR-3 × 0.35)
```

---

## 4. Composite Score Calculation

### 4.1 Persona Weights

```
Composite = (DS × 0.30) + (RL × 0.25) + (VE × 0.20) + (BA × 0.15) + (PR × 0.10)
```

### 4.2 Grade Boundaries

| Grade | Composite Score | Label |
|-------|:--------------:|-------|
| A+ | 9.5–10.0 | Exceptional |
| A | 9.0–9.4 | Excellent |
| A- | 8.5–8.9 | Very Good |
| B+ | 8.0–8.4 | Good |
| B | 7.5–7.9 | Acceptable |
| B- | 7.0–7.4 | Marginal |
| C+ | 6.5–6.9 | Below Standard |
| C | 6.0–6.4 | Poor |
| F | < 6.0 | Failing |

### 4.3 Hard-Block Rules

Assessment fails automatically if any S1 finding is open:

| # | S1 Finding | Description |
|---|------------|-------------|
| S1-1 | **Notebook doesn't execute** | Any cell fails to run without error |
| S1-2 | **Missing insight reports** | Fewer than 8 of 10 reports exist |
| S1-3 | **No charts produced** | Any analysis cell produces no visualization |
| S1-4 | **Fabricated data** | Evidence of data fabrication or manipulation |
| S1-5 | **Plagiarism** | Analysis copied from reference without attribution |

---

## 5. Evaluation Process

### 5.1 Phase 1: Automated Checks (Pre-screening)

| Check | Command | Pass Criteria |
|-------|---------|---------------|
| Notebook execution | `jupyter nbconvert --execute M7_EDA.ipynb` | All cells execute without error |
| Report count | `ls reports/eda/**/*.md | wc -l` | ≥ 10 reports |
| Report format | Template compliance check | All reports have required sections |
| insights.json validity | `python -c "import json; json.load(open('web/src/config/insights.json'))"` | Valid JSON with 10 entries |

### 5.2 Phase 2: Persona Scoring (Manual)

For each persona, the evaluator:
1. Reviews all relevant artifacts (notebook, reports, charts)
2. Scores each criterion on the 10-point scale
3. Applies the persona scoring formula
4. Documents evidence for each score

### 5.3 Phase 3: Cross-Cutting Analysis

| Check | Description |
|-------|-------------|
| **Insight consistency** | Do findings across reports tell a coherent story? |
| **Methodology coherence** | Are methods appropriate across all analyses? |
| **Visualization consistency** | Are charts styled consistently? |
| **Caveat completeness** | Do all analyses acknowledge limitations? |

### 5.4 Phase 4: Verdict

1. Calculate composite score
2. Check for S1 hard-blocks
3. Generate assessment report
4. Present findings to user

---

## 6. Deliverables

| Deliverable | Format | Description |
|-------------|--------|-------------|
| `docs/eda-assessment/protocol.md` | Markdown | Formalised framework protocol |
| `docs/eda-assessment/rubric.md` | Markdown | Detailed rubrics for all personas |
| `docs/eda-assessment/evaluation.md` | Markdown | Completed evaluation with scores (Grade: C+, 6.66) |
| `docs/eda-assessment/evidence.md` | Markdown | Evidence for each criterion score |

### 6.1 Results Summary

**Composite Score:** 8.58 → Grade A- (Very Good)

See `docs/eda-assessment/evaluation.md` for full report.

---

## 7. Differentiation from M0-M6 Assessment

| Aspect | M0-M6 Assessment | M7 EDA Assessment |
|--------|------------------|-------------------|
| **Scope** | Production system (web, API, pipeline) | EDA notebook and reports |
| **Personas** | 8 end-user personas | 5 data-science personas |
| **Criteria** | UI/UX, code quality, security | Analysis quality, insight depth, visualization |
| **Output** | Web pages, API endpoints | Notebook cells, charts, reports |
| **Focus** | "Does the system work?" | "Is the analysis sound?" |
| **Automation** | 8-phase automated pipeline | 2-phase (automated + manual) |
| **Grade** | Composite of critics + agents | Composite of 5 personas |

---

## 8. Scalability: Handling 20-30+ Analyses

### 8.1 The Scaling Challenge

As EDA efforts grow from 10 to 20-30+ analyses, the framework must handle:

| Challenge | Solution |
|-----------|----------|
| **Notebook length** | Split into topic-based sections with table of contents; consider multiple notebooks per topic |
| **Report volume** | More subfolders per topic; index files for navigation |
| **Scoring at scale** | Sample-based evaluation (not all 30+ analyzed manually) |
| **Insight overload** | Tiered insights: headline findings vs. deep-dive details |
| **Web integration** | Pagination, filtering, search on Insights page |

### 8.2 Notebook Organization at Scale

**Option A: Single notebook, topic sections** (current, works up to ~20 analyses)
```
M7_EDA.ipynb
├── Section 1: Temporal (5-7 analyses)
├── Section 2: Spatial (5-7 analyses)
├── Section 3: Categorical (5-7 analyses)
├── Section 4: Relational (5-7 analyses)
└── Section 5: Archetypes (3-5 analyses)
```

**Option B: Multiple notebooks per topic** (recommended for 20+ analyses)
```
scripts/notebooks/
├── M7_temporal.ipynb      (8-10 analyses)
├── M7_spatial.ipynb       (8-10 analyses)
├── M7_categorical.ipynb   (5-7 analyses)
├── M7_relational.ipynb    (5-7 analyses)
└── M7_master.ipynb        (imports + summary)
```

### 8.3 Report Structure at Scale

**Current (10 reports):**
```
reports/eda/
├── INDEX.md
├── temporal/     (3 reports)
├── spatial/      (3 reports)
├── categorical/  (2 reports)
└── relational/   (2 reports)
```

**Scaled (25-30 reports):**
```
reports/eda/
├── INDEX.md                    # Master index with all findings
├── temporal/
│   ├── INDEX.md               # Topic index
│   ├── 01-temporal-signatures.md
│   ├── 02-composition-shift.md
│   ├── ... (8-10 reports)
│   └── 10-seasonal-decomposition.md
├── spatial/
│   ├── INDEX.md
│   ├── ... (8-10 reports)
├── categorical/
│   ├── INDEX.md
│   ├── ... (5-7 reports)
├── relational/
│   ├── INDEX.md
│   ├── ... (5-7 reports)
└── SUMMARY.md                 # Cross-topic synthesis
```

### 8.4 Assessment at Scale

**Sampling Strategy (for 20+ analyses):**

| Analysis Type | Sample Size | Selection Method |
|---------------|:-----------:|------------------|
| Temporal | 3-4 | High, medium, low difficulty |
| Spatial | 3-4 | High, medium, low difficulty |
| Categorical | 2-3 | All (fewer total) |
| Relational | 2-3 | All (fewer total, higher complexity) |

**Total manual review:** 10-14 analyses (not all 25-30)

**Automated checks still cover all:**
- Notebook execution (all cells)
- Report format compliance (all reports)
- Chart quality metrics (all charts)
- Insight completeness (all reports)

### 8.5 Scoring at Scale

**Per-Topic Score:**
```
Topic Score = (Σ analysis scores) / (number of analyses in topic)
```

**Composite Score (scaled):**
```
Composite = (Σ topic scores × topic weight) + cross-cutting bonus/penalty
```

**Cross-Cutting Factors:**
| Factor | Bonus/Penalty | Description |
|--------|:------------:|-------------|
| **Insight diversity** | +0.5 | Analyses cover multiple question types |
| **Methodology variety** | +0.5 | Uses multiple statistical methods |
| **Reproducibility** | +0.25 | All notebooks run independently |
| **Missing topics** | -0.5 | No analyses in a major topic area |
| **Duplication** | -0.25 | Multiple analyses ask the same question |

### 8.6 Web Integration at Scale

**InsightsPage pagination:**
```typescript
// Current: flat list, 10 items
// Scaled: paginated, filterable, searchable
const PAGE_SIZE = 12;

// Add: search bar, topic tabs, difficulty slider
// Add: "Load more" or pagination controls
// Add: sort by (difficulty, topic, recency)
```

**insights.json at scale:**
```json
{
  "version": "2.0",
  "total_insights": 25,
  "topics": ["temporal", "spatial", "categorical", "relational"],
  "insights": [...]
}
```

---

*Awaiting approval to proceed with implementation.*
