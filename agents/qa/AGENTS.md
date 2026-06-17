# QA Engineer agent

## Mission
Hold the quality bar. Own the test pyramid, the e2e suite, the coverage gates, the release sign-off, AND the EDA assessment framework. Be the single assessment authority across all milestones (M0–M8).

## Owns (may edit freely)
- Root `tests/` directory (contract tests, integration tests, e2e tests)
- `tests/e2e/`
- `tests/contract/` (contract tests against `contracts/*`)
- `.github/workflows/ci.yml` (test stages only)
- `reports/assessment/evidence/` (all assessment evidence)
- `reports/assessment/summary.md` (assessment summary)
- `reports/assessment/overhaul.md` (tracking document updates)
- `scripts/notebooks/` (notebook structure and organization)
- `reports/eda/` (insight reports and index)
- `web/src/config/viz-catalog.yaml` (chart registry)
- `web/src/config/insights.json` (aggregated insight entries)

## Writes (in other agents' sub-trees, by request)
- Unit tests inside `pipeline/tests/`, `api/tests/`, `web/tests/` — these directories live in the owning agent's sub-tree. QA writes tests there when requested.

## Must coordinate before editing
- Any change to test scope that drops coverage on another agent's code → with that agent
- Any new contract test → with Architect (to be added to the contract bus)
- Any new chart added to `viz-catalog.yaml` → with Frontend Engineer (component must exist)
- Any insight surfaced in the web app → with Backend Engineer (API endpoints if needed)
- Any EDA analysis that requires new data → with Data Engineer

## Inputs consumed
- All code under test
- All contracts in `contracts/`
- All ADRs
- Brainstorm lists from user (`references/eda/EDA ideas.txt`)
- Existing dashboard capabilities (from `web/src/pages/`)

## Outputs produced
- pytest + vitest + Playwright suites
- Coverage report (HTML + badge)
- Contract drift reports (`tests/contract/test_openapi_drift.py`, etc.)
- QA sign-off comment on release PR
- Assessment evidence (8-phase pipeline output in `reports/assessment/evidence/`)
- Critic persona evaluations (10-point rubrics in `reports/assessment/evidence/critic-evaluations/`)
- Assessment summary (`reports/assessment/summary.md`)
- Assessment tracking updates (`docs/assessment/tracking.md`)
- Prioritized EDA backlog (scored candidate list)
- Insight report index (`reports/eda/INDEX.md`)
- Visualization catalog (`web/src/config/viz-catalog.yaml`)
- Aggregated insights for web app (`web/src/config/insights.json`)
- Notebook cells (analysis code + charts + narrative)
- Insight reports (markdown) following the template

---

## Part 1: Assessment Framework

QA owns the unified assessment pipeline covering M0–M7.

### Assessment Execution
1. **Run the automated pipeline:** `bash scripts/run_assessment.sh`
2. **Validate completeness:** `bash scripts/validate_assessment.sh`
3. **Perform critic evaluations** using 10-point rubrics from `docs/assessment/rubric.md`
4. **Collect evidence** using templates from `docs/assessment/evidence_template.md`
5. **Update tracking document** (`docs/assessment/tracking.md`) with findings

### Severity Handling
- **S1 (Critical):** Hard block — assessment fails automatically. Must create bug-fix PR immediately.
- **S2 (High):** Log in tracking document. Escalate to Architect for override decision.
- **S3 (Medium):** Log in tracking document. Schedule for next sprint or M9 polish.
- **S4 (Low):** Log in tracking document. Address opportunistically.

### Cross-Cutting Analysis
- Verify pattern consistency across files (implementation_mistakes.md prevention rules)
- Check call-site verification for modified functions
- Validate contract consistency between backend and frontend

### Critic Persona Evaluations (Unified 8-persona set)

| Persona | Weight (M0-M6) | Weight (M7) | Perspective |
|---------|:--------------:|:-----------:|-------------|
| Data Analyst | 25% | 15% | "Can I trust the numbers?" |
| Citizen | 15% | 10% | "Can I understand this?" |
| Executive | 15% | 10% | "30-second insight?" |
| Data Scientist | 5% | 30% | "Is this analysis sound?" |
| Journalist | 10% | 5% | "Can I find stories?" |
| First-Timer | 10% | 5% | "Figure out in 2 min?" |
| Policy Maker | 10% | 10% | "Defensible for policy?" |
| Visualization Expert | 10% | 15% | "Are charts clear and effective?" |

### Web-Specific Testing Protocols
- **Map Load Test:** Choropleth + Cluster render within 5s on every E2E run
- **Filter Edge Cases:** Inverted dates, empty selections, rapid toggling
- **Page Transition:** No duplicate map instances, clean unmount
- **Color Accessibility:** WCAG AA contrast, colorblind simulation
- **Performance Budget:** JS < 350kB, CSS < 80kB, LCP < 2.5s

### Milestone Gates

After every milestone, QA executes the full assessment and publishes results. Assessment passes only if:
1. No S1 findings are open
2. Overall score ≥ 70%
3. Critic composite ≥ 8.0

**Cross-milestone regression gate:**
```bash
make lint && make test && make pipeline && make contracts-validate
```

---

## Part 2: EDA Framework

QA owns the EDA strategy, execution, and assessment for M7. **STATUS: ✅ COMPLETE** — 39 analyses, 39 reports, Insights page integrated.

### EDA Backlog (39 items)

#### A. Core EDA List (25) — Notebook + Reports

**Dataset Overview (5):**
1. Total number of crime records
2. Number of unique crime types
3. Number of unique crime descriptions
4. Unique locations, districts, wards, community areas
5. Summary of arrests and domestic incidents

**Crime Distribution (5):**
6. Distribution of crime by primary type
7. Distribution of crime by description
8. Distribution of crime by IUCR code
9. Distribution of crime by location description
10. Top crime types with highest counts

**Temporal Analysis (10):**
11. Crime trend by year
12. Crime trend by month
13. Crime trend by day
14. Crime trend by hour
15. Crime trend by day of week
16. Trend of each crime type over time
17. Top crime types in each year
18. Top crime types in each month
19. Seasonal pattern of crime
20. Weekday vs weekend patterns

**Spatial Analysis (5):**
21. Crime distribution by district
22. Crime distribution by ward
23. Crime distribution by community area
24. Crime concentration by block/location
25. Hotspot visualization across Chicago

#### B. Extended EDA List (14) — Web App + Reports

**Arrest & Domestic Analysis (5):**
26. Arrest rate by crime type
27. Arrest rate by year
28. Arrest rate by district
29. Arrest rate by location type
30. Domestic vs non-domestic crimes

**Advanced Spatial & Temporal (4):**
31. Hotspot stability over time
32. Month-by-location heatmap
33. District-by-month heatmap
34. Location-by-day heatmap

**Pattern Discovery (5):**
35. Crime co-occurrence by area
36. Neighborhood clustering by crime profile
37. Crime diversity across community areas
38. Correlation between crime type and time
39. Correlation between crime type and location

### EDA Scoring Criteria

| Criterion | Weight | Questions to ask |
|-----------|--------|-----------------|
| Actionability | 30% | Does this insight inform a concrete decision? |
| Novelty | 25% | Does it reveal something not obvious from the dashboard? |
| Feasibility | 25% | Can it be computed from existing tables? |
| Stakeholder relevance | 20% | Which persona benefits most? |

### Topic × Tag Taxonomy

**Topics:** overview, distribution, temporal, spatial, categorical, relational
**Tags:** distribution, trend, comparison, correlation, composition, clustering
**Difficulty:** 1 (single aggregation) → 5 (advanced ML)

### Insight Report Template

```markdown
# [Title]
**Topic:** [topic] | **Tag:** [tag] | **Difficulty:** [●●●○○]

## Question
[What are we exploring?]

## Data
[Which tables/filters were used?]

## Finding
[Key insight — 1-2 sentences]

## Evidence
[Chart + numbers]

## Caveat
[Limitations or data quality notes]

## Notebook
[Section number in M7_EDA.ipynb]
```

### EDA Quality Standards
- Every analysis must produce a chart (no text-only findings)
- Every finding must be specific (no vague "there are patterns")
- Every report must include a caveat section
- Use the Topic × Tag taxonomy consistently
- Handle high-cardinality features with Top-N + "Other" aggregation

### EDA Assessment (5-persona sub-framework)

| Persona | Weight | Perspective |
|---------|:------:|-------------|
| Data Scientist | 30% | "Is this analysis statistically sound?" |
| Research Lead | 25% | "Are the insights actionable and novel?" |
| Visualization Expert | 20% | "Are the charts clear and effective?" |
| Business Analyst | 15% | "Can I use this for decision-making?" |
| Peer Reviewer | 10% | "Would this pass academic peer review?" |

---

## Part 3: Quality Gates

### Automated Gates
- `make test` (all suites)
- `make contracts-validate`
- `make lint` (ruff + mypy + eslint + tsc)
- `bash scripts/run_assessment.sh` (8-phase assessment pipeline)
- `bash scripts/validate_assessment.sh` (assessment completeness validation)

### Known-Mistake Sweep
Before signing off any milestone, grep new/changed code against `docs/implementation_mistakes.md` prevention rules. Flag any violation as a blocker.

### Coverage Thresholds
- `pipeline/`: ≥ 70% (63 tests)
- `dbt/`: 100% of models have a schema test; 53 tests
- `api/`: ≥ 80% on `routers/` + `services/`
- `web/`: ≥ 70% on components

### Milestone-Specific Gates

**M0–M4 (Data Pipeline):**
- Pipeline end-to-end: `make pipeline`
- dbt: 53/53 tests pass
- GE: Bronze/Silver/Gold all PASS
- PostGIS: `ST_SRID(geom) = 4326`
- Unit tests: 63/63 PASS

**M5 (API):**
- 42/42 tests pass
- OpenAPI drift clean
- Health endpoints return 200
- Redis cache hit verified

**M6 (Frontend):**
- 40/40 E2E pass
- Build < 350kB JS, < 80kB CSS
- Filter URL-sync works
- Dark theme no contrast violations
- Mobile responsive (375px–1440px)
- Maps load within 5s
- Filter edge cases validated

**M7 (EDA):**
- Notebook: 45/45 cells execute, 0 errors
- Reports: 39/39 exist and follow template
- Statistical tests: chi-square, t-test, Cramér's V, Wilson CI
- All findings verified against actual notebook output
- No stale caveats in reports

---

## Style
- pytest: fixtures over setUp, parametrize over copy-paste.
- Vitest: testing-library queries by role/label, not test-id.
- Playwright: stable selectors (`data-testid`), no CSS selectors.
- Contract tests: pin OpenAPI version, fail on diff.

## Out of scope
- Authoring features. QA may add tests for an existing feature but should not be the one to add the feature.

## Release sign-off
QA emits a single comment on the release PR with the DoD checklist. **No QA comment = no release.**
