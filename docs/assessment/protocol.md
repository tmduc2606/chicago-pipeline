# Chicago Pipeline — Unified Assessment Framework (M0–M7)

**Date:** 2026-06-14
**Status:** ACTIVE
**Version:** 3.0
**Authority:** Root AGENTS.md §Milestone evaluation protocol
**Replaces:** `docs/assessment/protocol.md` v2.0 + `docs/eda-assessment/protocol.md` v1.1

---

## 1. Framework Overview

### 1.1 Philosophy

A **single assessment system** evaluates all milestones (M0–M7) using one unified protocol with milestone-specific persona weights. This replaces the previous dual-system approach (M0-M6 production + M7 EDA).

| Principle | Implementation |
|-----------|---------------|
| **Severity-weighted scoring** | S1 (Critical) items block assessment; S2-S4 apply score penalties |
| **Hard-block on Critical** | Assessment fails automatically if any S1 finding is open |
| **Milestone-specific personas** | Same 8 personas, different weights per milestone type |
| **Automation-first** | 8-phase pipeline covers gates, E2E, inspections, and scoring |
| **Evidence-based findings** | Every finding requires command output, code reference, or screenshot |

### 1.2 Document Architecture

```
docs/assessment/
├── protocol.md              ← This file: unified framework
├── rubric.md                ← 10-point rubrics for all personas
├── risk_matrix.md           ← Severity tiers (S1-S4) and hard-block rules
├── evidence_template.md     ← Evidence collection formats
├── checklist.md             ← Per-milestone inspection checklists
├── tracking.md              ← Living tracking document
├── remediation.md           ← Fix candidates and projected gains
└── preparation.md           ← Pre-assessment checklist
```

---

## 2. Unified Persona Set

8 personas evaluate all milestones with context-dependent weights:

| Persona | Weight (M0-M4) | Weight (M5-M6) | Weight (M7) | Perspective |
|---------|:--------------:|:--------------:|:-----------:|-------------|
| **Data Analyst** | 25% | 25% | 15% | "Can I trust the numbers?" |
| **Citizen** | 15% | 15% | 10% | "Can I understand this?" |
| **Executive** | 15% | 15% | 10% | "30-second insight?" |
| **Data Scientist** | 5% | 5% | 30% | "Is this analysis sound?" |
| **Journalist** | 10% | 10% | 5% | "Can I find stories?" |
| **First-Timer** | 10% | 10% | 5% | "Figure out in 2 min?" |
| **Policy Maker** | 10% | 10% | 10% | "Defensible for policy?" |
| **Visualization Expert** | 10% | 10% | 15% | "Are charts clear and effective?" |

**Rationale:** M7 elevates Data Scientist (statistical rigor) and Visualization Expert (chart quality). M5-M6 elevates Data Analyst (data accuracy) and First-Timer (onboarding).

---

## 3. Evaluation Dimensions

| Dimension | Weight (M0-M4) | Weight (M5-M6) | Weight (M7) | Owner |
|-----------|:--------------:|:--------------:|:-----------:|-------|
| **Automated Gates** | 30% | 25% | 15% | QA |
| **Code Quality** | 25% | 20% | 10% | QA |
| **Functional (E2E)** | 20% | 20% | 10% | QA |
| **Critic Evaluation** | 15% | 25% | 40% | QA + personas |
| **Data/EDA Quality** | 10% | 10% | 25% | QA |

---

## 4. Severity System

### 4.1 Severity Tiers

| Tier | Name | Score Impact | Block Status |
|------|------|-------------|-------------|
| **S1** | Critical | -25% per item | **HARD BLOCK** — assessment fails if any S1 is open |
| **S2** | High | -10% per item | Architect override required |
| **S3** | Medium | -5% per item | Tracked in overhaul |
| **S4** | Low | -1% per item | Informational |

### 4.2 Hard-Block Rules

An assessment **fails automatically** if:
- Any S1 check item is marked FAIL
- `make lint` fails
- `make test` fails
- `gitleaks detect` finds secrets
- `make contracts-validate` fails
- Any Playwright E2E test crashes
- API health endpoint returns 500
- Database connection fails

### 4.3 Override Authority

| Severity | Override | Conditions |
|----------|----------|------------|
| S1 | **Nobody** | Must be fixed — no override |
| S2 | **Architect** | Documented justification + mitigation plan |
| S3 | **Owning Agent** | Technical debt ticket created |
| S4 | **Owning Agent** | No formal process |

---

## 5. Test Taxonomy (L0–L4)

| Level | Definition | Chicago Pipeline Equivalent | Evidence Location |
|-------|-----------|---------------------------|-------------------|
| **L0** | Fast unit tests (<60ms) | Pipeline pytest, API pytest, Web vitest | `evidence/gates/test.txt` |
| **L1** | Unit tests with deps (<400ms) | API tests with mocked DB | `evidence/gates/api-test.txt` |
| **L2** | Functional tests (SQL, FS) | dbt tests, GE expectations, contracts | `evidence/gates/quality.txt` |
| **L3** | Tests against deployed services | Playwright E2E + Critic evaluations | `evidence/e2e/e2e.txt` + `evidence/critic-evaluations/` |
| **L4** | Integration / smoke | Full `make pipeline`, manual verification | `evidence/code-inspections/` |

---

## 6. Assessment Execution Protocol

### 8-Phase Pipeline

```
Phase 1: Prerequisites          → Automated (docker, required files, agent files)
Phase 2: Automated Gates        → Automated (lint, test, contracts, quality, gitleaks)
Phase 3: Playwright E2E         → Automated (web-e2e)
Phase 4: Critic Evaluations     → Semi-automated (10-point rubric per persona)
Phase 5: Code Inspections       → Automated + manual (pattern checks, checklists)
Phase 6: Cross-Cutting Analysis → Automated (pattern consistency, call-site verification)
Phase 7: Score Calculation      → Automated (severity-weighted scoring)
Phase 8: Report Generation      → Automated (summary + tracking document)
```

### Execution Commands

```bash
# Full assessment (all 8 phases)
bash scripts/run_assessment.sh --milestone M7 --full

# Individual phases
bash scripts/run_assessment.sh --gates-only       # Phase 2
bash scripts/run_assessment.sh --e2e-only          # Phase 3
bash scripts/run_assessment.sh --critic            # Phase 4
bash scripts/run_assessment.sh --inspections       # Phase 5
bash scripts/run_assessment.sh --cross-cutting     # Phase 6
bash scripts/run_assessment.sh --scoring           # Phase 7
bash scripts/run_assessment.sh --report            # Phase 8

# Web-specific testing
bash scripts/run_assessment.sh --web-testing       # Map load, filter edge cases, perf

# EDA-specific testing
bash scripts/run_assessment.sh --eda-testing       # Notebook execution, report consistency
```

### Output Locations

| Output | Location | Purpose |
|--------|----------|---------|
| Gate results | `reports/assessment/evidence/gates/` | Raw command outputs |
| E2E results | `reports/assessment/evidence/e2e/` | Playwright output |
| Code inspections | `reports/assessment/evidence/code-inspections/` | Pattern check results |
| Critic evaluations | `reports/assessment/evidence/critic-evaluations/` | Persona scoring |
| Cross-cutting | `reports/assessment/evidence/cross-cutting/` | Pattern consistency |
| Scoring | `reports/assessment/evidence/scoring.md` | Score calculation |
| Summary | `reports/assessment/summary.md` | Final results |
| Tracking | `docs/assessment/tracking.md` | Living findings document |

---

## 7. Score Calculation

### 7.1 Per-Milestone Score

```
Base Score = (checks passed / total checks) × 100%

Severity Penalty = Σ (S1_count × 25) + Σ (S2_count × 10) + Σ (S3_count × 5) + Σ (S4_count × 1)

Milestone Score = max(0, Base Score - Severity Penalty)

Hard Block: If any S1 check is FAIL → Milestone Score = 0
```

### 7.2 Overall Assessment Score

```
Overall = Σ (Milestone Score × Milestone Weight)

Weights:
  M0: 5%   (foundation)
  M1: 10%  (ingestion)
  M2: 10%  (transformation)
  M3: 10%  (aggregation)
  M4: 15%  (warehouse)
  M5: 15%  (API)
  M6: 20%  (Frontend + UI/UX)
  M7: 15%  (EDA)
```

### 7.3 Grade Boundaries

| Grade | Score | Meaning | Action |
|-------|-------|---------|--------|
| **A** | 95–100% | Production-ready, all gates green | Ship it |
| **B** | 85–94% | Minor issues, safe to proceed | Fix S2 items |
| **C** | 70–84% | Needs remediation | Fix before next milestone |
| **D** | 50–69% | Significant gaps | Blocking issues |
| **F** | <50% or any S1 open | Critical failures | Must restart or fix S1 |

---

## 8. Critic Evaluation Protocol

### 8.1 Evaluation Template

Each critic persona evaluation follows this structure:

```markdown
# Critic Evaluation: [Persona Name]
**Timestamp:** [ISO-8601]
**Evaluator:** [Agent name]
**Milestone:** [M0–M7]
**Pages evaluated:** [list]

## Rubric Scores (from docs/assessment/rubric.md)
| # | Criterion | Score (0-10) | Evidence | Notes |
|---|-----------|-------------|----------|-------|
| [XX-1] | [criterion] | [score] | [screenshot/command] | [observation] |

## Composite Score
**Weighted Average:** [score] / 10
**Verdict:** [PASS (≥8) | CONDITIONAL (7-7.9) | FAIL (<7)]
```

### 8.2 Pass/Fail Thresholds

| Threshold | Score | Action |
|-----------|-------|--------|
| **Pass** | ≥ 8.0 | Proceed to next milestone |
| **Conditional Pass** | 7.0 – 7.9 | Fix identified gaps, re-evaluate |
| **Fail** | < 7.0 | Must remediate before proceeding |
| **Hard Fail** | Any persona < 6.0 | Specific persona area must be reworked |

---

## 9. Cross-Cutting Analysis Protocol

### 9.1 Pattern Verification

Every assessment must verify cross-file pattern consistency using the implementation_mistakes.md prevention rules:

| Pattern | Verification Method | Evidence |
|---------|-------------------|----------|
| MISTAKE-001: `::date` SQL cast | `grep -r "::date" api/app/services/` | `evidence/code-inspections/` |
| MISTAKE-002: Hardcoded coordinates | `grep -r "41.8781" web/src/` | `evidence/code-inspections/` |
| MISTAKE-004: Map race condition | Check MapLibre components for `styleLoaded` ref | `evidence/code-inspections/` |
| MISTAKE-005: Missing ErrorBoundary | Check all page components | `evidence/code-inspections/` |
| MISTAKE-008: Param name mismatch | Compare frontend `api.ts` with backend `Query()` | `evidence/cross-cutting/` |
| MISTAKE-010: Pattern repetition | Grep for broken pattern across siblings | `evidence/cross-cutting/` |

### 9.2 Call-Site Verification

For every modified function or endpoint:
- All call sites checked
- Downstream consumers identified
- Backward compatibility verified

---

## 10. Per-Milestone Gate Criteria

### M0 (Foundation)
| Gate | Check | Pass/Fail |
|------|-------|-----------|
| S1 | Docker compose up succeeds | |
| S1 | Health check returns 200 | |
| S1 | Seed generates CSV | |
| S2 | README renders correctly | |
| S2 | Agent files present (all dirs) | |

### M1 (Ingestion)
| Gate | Check | Pass/Fail |
|------|-------|-----------|
| S1 | Bronze Parquet exists in MinIO | |
| S1 | Row count ≥ 61,000 | |
| S2 | Schema matches gold-schema.json | |
| S2 | Partitioning by year works | |

### M2 (Transformation)
| Gate | Check | Pass/Fail |
|------|-------|-----------|
| S1 | Silver Parquet exists | |
| S1 | No nulls in required columns | |
| S2 | Type casting correct | |
| S2 | Deduplication logic verified | |

### M3 (Aggregation)
| Gate | Check | Pass/Fail |
|------|-------|-----------|
| S1 | Gold star schema (5 tables) | |
| S1 | FK constraints valid | |
| S2 | Aggregation correctness spot-check | |
| S2 | Index coverage on FK columns | |

### M4 (Warehouse)
| Gate | Check | Pass/Fail |
|------|-------|-----------|
| S1 | dbt 53/53 tests pass | |
| S1 | PostGIS geometry verified | |
| S1 | 63/63 unit tests pass | |
| S2 | GE Bronze/Silver/Gold PASS | |
| S2 | Model documentation complete | |

### M5 (API)
| Gate | Check | Pass/Fail |
|------|-------|-----------|
| S1 | 42/42 pytest tests pass | |
| S1 | Health endpoints return 200 | |
| S1 | OpenAPI drift clean | |
| S2 | Redis cache hit verified | |
| S2 | Error model consistent | |

### M6 (Frontend)
| Gate | Check | Pass/Fail |
|------|-------|-----------|
| S1 | 40/40 E2E tests pass | |
| S1 | Build < 350kB JS, < 80kB CSS | |
| S1 | Maps load within 5s | |
| S2 | Filter edge cases validated | |
| S2 | Dark theme no contrast violations | |
| S2 | Mobile responsive (375px–1440px) | |
| S2 | Filter URL-sync works | |
| S3 | Skeleton loaders present | |
| S3 | Error boundary isolation | |

### M7 (EDA)
| Gate | Check | Pass/Fail |
|------|-------|-----------|
| S1 | Notebook 45/45 cells execute, 0 errors | |
| S1 | 39/39 reports exist and follow template | |
| S1 | TypeScript clean (`npx tsc --noEmit`) | |
| S2 | Statistical tests present (chi-square, t-test, Cramér's V, Wilson CI) | |
| S2 | All findings verified against actual output | |
| S2 | No stale caveats in reports | |
| S2 | insights.json values match actual data | |
| S3 | Methodology section documents all methods | |
| S3 | Colorblind-safe palette used | |

---

## 11. Agent Responsibilities During Assessment

### QA Engineer (Assessment Owner)
- Executes the 8-phase assessment pipeline
- Collects evidence for all phases
- Performs critic persona evaluations
- Validates assessment completeness via `validate_assessment.sh`
- Publishes results in `reports/assessment/`
- Maintains EDA backlog and insight reports

### Architect (Review Gate)
- Reviews S2 findings for override decisions
- Validates cross-cutting analysis
- Signs off on final assessment grade
- Records assessment completion in PR

### Owning Agents (Remediation)
- Fix findings in their domain (S1 immediately, S2 within milestone)
- Provide evidence of fix
- Update tracking document status

---

## 12. CI/CD Integration

The assessment runs on every PR via `.github/workflows/ci.yml`:

| Job | What It Checks | Required |
|-----|---------------|----------|
| lint | ruff + mypy + eslint + tsc | Yes |
| contracts | OpenAPI spec + agent files | Yes |
| security | gitleaks secret scan | Yes |
| test | api pytest + web vitest | Yes |
| e2e | Playwright tests | Yes (after test passes) |
| agents | Agent file structure | Yes |

---

## Changelog

| Date | Entry | Author |
|------|-------|--------|
| 2026-06-14 | v3.0 — Unified framework: single protocol for M0-M7, 8 personas, milestone-specific weights | QA Agent |
| 2026-06-06 | v2.0 — 8-phase pipeline, severity system, critic rubrics | Assessment Framework |
| 2026-06-06 | v1.0 — Initial framework | Assessment Framework |
