# Assessment Evidence Template — Standardized Evidence Collection

**Date:** 2026-06-06
**Status:** ACTIVE
**Usage:** Every assessment check must include evidence in the format below.

---

## 1. Evidence File Structure

```
reports/assessment/evidence/
├── gates/                          # Phase 2: Automated gate outputs
│   ├── lint.txt
│   ├── test.txt
│   ├── contracts.txt
│   ├── agents.txt
│   ├── quality.txt
│   ├── gitleaks.txt
│   ├── api-test.txt
│   └── web-test.txt
├── e2e/                            # Phase 3: Playwright E2E outputs
│   └── e2e.txt
├── code-inspections/               # Phase 5: Code inspection results
│   ├── M0-inspection.md
│   ├── M1-inspection.md
│   ├── M2-inspection.md
│   ├── M3-inspection.md
│   ├── M4-inspection.md
│   ├── M5-inspection.md
│   └── M6-inspection.md
├── critic-evaluations/             # Phase 4: Critic persona evaluations
│   ├── data-analyst.md
│   ├── citizen.md
│   ├── executive.md
│   ├── journalist.md
│   ├── first-timer.md
│   ├── policy-maker.md
│   ├── community-organizer.md
│   └── news-editor.md
├── cross-cutting/                  # Phase 6: Cross-cutting analysis
│   └── cross-cutting.md
├── S1-*.md                         # Critical severity evidence (hard block)
├── S2-*.md                         # High severity evidence
└── summary.md                      # Aggregated summary
```

---

## 2. Evidence Formats by Check Type

### 2.1 Automated Gate Evidence

**Format:** Raw command output captured to file.

```markdown
# Gate: [gate-name]
**Timestamp:** [ISO-8601]
**Command:** `[exact command run]`
**Exit Code:** [0 = PASS, non-0 = FAIL]

## Output
```
[raw command output]
```

## Verdict
[PASS | FAIL]
**Severity if FAIL:** [S1 | S2 | S3 | S4]
**Details:** [brief explanation of failure]
```

### 2.2 Code Inspection Evidence

**Format:** Structured checklist with file references.

```markdown
# Inspection: M[N] — [Milestone Name]
**Timestamp:** [ISO-8601]
**Inspector:** [Agent name]
**Files examined:** [count]

## Check Results

| # | Check | Verdict | Evidence | Severity |
|---|-------|---------|----------|----------|
| M[N]-01 | [check description] | PASS | `file_path:line_number` | S1 |
| M[N]-02 | [check description] | FAIL | [description of gap] + `file_path:line_number` | S2 |

## FAIL Details

### M[N]-[XX]: [Check Name]
- **File:** `path/to/file.py:line_number`
- **Expected:** [what should exist]
- **Actual:** [what actually exists]
- **Fix suggestion:** [how to fix]
```

### 2.3 Critic Evaluation Evidence

**Format:** Rubric scoring with per-criterion notes.

```markdown
# Critic Evaluation: [Persona Name]
**Timestamp:** [ISO-8601]
**Evaluator:** [Agent name]
**Pages evaluated:** [list of pages]

## Rubric Scores

| # | Criterion | Score | Evidence | Notes |
|---|-----------|-------|----------|-------|
| [XX-1] | [criterion name] | [0-10] | [screenshot path or command output] | [specific observation] |
| [XX-2] | [criterion name] | [0-10] | [evidence reference] | [observation] |

## Composite Score
**Weighted Average:** [calculated score] / 10
**Verdict:** [PASS (≥8) | CONDITIONAL (7-7.9) | FAIL (<7)]

## Screenshots
- [page-name].png — [what it shows]

## Recommendations
1. [Specific, actionable improvement]
2. [Another improvement]
```

### 2.4 Cross-Cutting Analysis Evidence

**Format:** Pattern verification results.

```markdown
# Cross-Cutting Analysis
**Timestamp:** [ISO-8601]
**Scope:** M0–M6

## Pattern Verification

| Pattern | Files Checked | Violations | Evidence |
|---------|--------------|------------|----------|
| `::date` SQL cast (MISTAKE-001) | [count] service files | [count] | `grep -r "::date" api/app/services/` |
| Hardcoded coordinates (MISTAKE-002) | [count] map components | [count] | `grep -r "41.8781" web/src/` |
| Missing ErrorBoundary (MISTAKE-005) | [count] page components | [count] | [manual inspection] |
| [additional patterns] | | | |

## Cross-File Consistency

| Check | Result | Evidence |
|-------|--------|----------|
| All service files use same date handling | PASS/FAIL | [grep results] |
| All map components receive coords from backend | PASS/FAIL | [code references] |
| All error boundaries wrap independent components | PASS/FAIL | [code references] |
```

### 2.5 S1/S2 Finding Evidence

**Format:** Structured incident report for severity items.

```markdown
# Finding: [S1|S2]-[NN] — [Title]
**Timestamp:** [ISO-8601]
**Severity:** [S1 | S2]
**Milestone:** [M0-M6]
**Owner:** [Agent name]

## Description
[Clear description of the issue]

## Reproduction Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Evidence
- **Command output:** `[command that demonstrates issue]`
- **File reference:** `path/to/file.py:line_number`
- **Screenshot:** [if applicable]

## Impact
[Who is affected and how]

## Suggested Fix
[Specific fix recommendation]

## Status
[open | triaged | in_progress | fixed | verified]
```

---

## 3. Evidence Collection Rules

### 3.1 Timing
- Automated evidence: captured during `run_assessment.sh` execution
- Manual evidence: collected during Phase 4-5, timestamped at collection time
- All evidence files must include ISO-8601 timestamp

### 3.2 Naming Convention
- Gate outputs: `{gate-name}.txt` (raw output)
- Inspection results: `M{N}-inspection.md`
- Critic evaluations: `{persona-slug}.md`
- Severity findings: `{S1|S2}-{NN}-{slug}.md`
- Cross-cutting: `cross-cutting.md`

### 3.3 Retention
- Evidence from each assessment run is retained in `reports/assessment/evidence/`
- Previous runs are archived with timestamp prefix: `YYYY-MM-DDTHH-MM-SS/`
- Minimum retention: 90 days or 3 assessment cycles (whichever is longer)

### 3.4 Validation
- `validate_assessment.sh` checks that:
  - Every FAIL check has associated evidence
  - Every S1/S2 finding has a reproduction section
  - Every critic evaluation has screenshots
  - Evidence files are non-empty and well-formed

---

## 4. Evidence Quality Standards

| Standard | Requirement | Verification |
|----------|-------------|--------------|
| **Reproducibility** | Another agent can reproduce the finding using the evidence | `validate_assessment.sh` checks evidence completeness |
| **Specificity** | Evidence points to exact file:line or command output | Grep/file reference required for code issues |
| **Timestamp** | All evidence includes collection time | ISO-8601 format enforced |
| **Objectivity** | Evidence is factual (command output, screenshot) not subjective | Subjective notes separated from evidence |
| **Actionability** | Each finding includes a suggested fix | Template requires fix recommendation |

---

## Changelog

| Date | Entry | Author |
|------|-------|--------|
| 2026-06-06 | Initial evidence template with 5 format types | Assessment Framework |
