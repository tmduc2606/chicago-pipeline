# Chicago Pipeline — M0→M6 Assessment Framework

**Date:** 2026-06-06
**Status:** FRAMEWORK — Ready for execution
**Version:** 2.0
**Authority:** Root AGENTS.md §Milestone evaluation protocol

---

## 1. Framework Overview

### 1.1 Philosophy

This assessment evaluates the project through **two complementary systems** aligned with production-grade practices (Google Engineering Practices, Sourcegraph Code Review Checklist, Microsoft severity classification):

1. **Agent Assessment** — technical correctness, code quality, architectural integrity (automated + manual inspection)
2. **Critic Evaluation** — end-user perspectives that assess usability, trust, and real-world value (structured 10-point rubrics)

The tension between these systems ensures balanced quality — agents optimize for technical excellence while critics ensure the system serves its actual purpose.

### 1.2 Design Principles

| Principle | Implementation |
|-----------|---------------|
| **Severity-weighted scoring** | S1 (Critical) items block assessment; S2-S4 apply score penalties (see `docs/assessment/risk_matrix.md`) |
| **Hard-block on Critical** | Assessment fails automatically if any S1 finding is open — no override possible |
| **Structured critic rubrics** | Every persona gets a 10-point rubric with measurable criteria (see `docs/assessment/rubric.md`) |
| **Cross-cutting analysis** | Pattern consistency verified across files and milestones (not just per-milestone) |
| **Evidence-based findings** | Every finding requires command output, code reference, or screenshot (see `docs/assessment/evidence_template.md`) |
| **Automation-first** | 8-phase automated pipeline covers gates, E2E, inspections, and scoring |

### 1.3 Document Architecture

```
docs/assessment/
        ├── protocol.md                ← This file: Framework protocol (how to assess)
        ├── risk_matrix.md             ← Severity tiers (S1-S4) and hard-block rules
        ├── rubric.md                  ← 10-point rubrics for all critic personas
        ├── evidence_template.md       ← Standardized evidence collection formats
        ├── checklist.md               ← Per-milestone code inspection checklists
        ├── tracking.md                ← Living tracking document (findings + status)
        ├── remediation.md             ← Fix candidates and projected gains
        ├── preparation.md             ← Pre-assessment checklist
        └── reports/assessment/           ← Automated evidence output
```

---

## 2. Dual Assessment System

### 2.1 Agent Assessment (Technical)

Evaluates whether the system is **built right** — correctness, quality, security, performance.

| Dimension | Weight | Owner | Checks |
|-----------|--------|-------|--------|
| **Data Engineering** | 25% | Data Engineer | Pipeline, dbt, GE, schema |
| **Backend (API)** | 20% | Backend Engineer | FastAPI, endpoints, caching |
| **Frontend (UI)** | 15% | Frontend Engineer | React, charts, maps, filters |
| **Data Quality** | 15% | QA Engineer | GE expectations, dbt tests |
| **Infrastructure** | 10% | SRE | Docker, health checks, compose |
| **Documentation** | 5% | Docs Agent | README, ADRs, changelog |
| **Security** | 5% | Security Agent | Secrets, CORS, CSP |
| **Architecture** | 5% | Architect | Contracts, ADRs, ownership |
| **Cross-Cutting** | — | Architect + QA | Pattern consistency, call-site verification |

### 2.2 Critic Evaluation (User Experience)

Evaluates whether the system **works for ME** — the end-user perspectives.

| Persona | Weight | Pages | Key Question |
|---------|--------|-------|-------------|
| **Data Analyst** | 25% | /, /crime-types, /locations, /analysis | "Can I trust the numbers?" |
| **Citizen** | 15% | /, /crime-types, /locations, /analysis | "Can I understand this?" |
| **Executive** | 15% | /, /crime-types, /locations, /analysis | "30-second insight?" |
| **Journalist** | 10% | /, /crime-types, /locations, /analysis | "Can I find stories?" |
| **First-Timer** | 10% | /, /crime-types, /locations, /analysis | "Figure out in 2 min?" |
| **Policy Maker** | 10% | /, /analysis | "Defensible for policy?" |
| **Community Organizer** | 8% | /locations | "Advocate for my neighborhood?" |
| **News Editor** | 7% | /, /analysis | "Headline-worthy findings?" |

---

## 3. Severity System

### 3.1 Severity Tiers (from `docs/assessment/risk_matrix.md`)

| Tier | Name | Score Impact | Block Status |
|------|------|-------------|-------------|
| **S1** | Critical | -25% per item | **HARD BLOCK** — assessment fails if any S1 is open |
| **S2** | High | -10% per item | Architect override required |
| **S3** | Medium | -5% per item | Tracked in overhaul |
| **S4** | Low | -1% per item | Informational |

### 3.2 Hard-Block Rules

An assessment **fails automatically** if:
- Any S1 check item is marked FAIL
- `make lint` fails
- `make test` fails
- `gitleaks detect` finds secrets
- `make contracts-validate` fails
- Any Playwright E2E test crashes
- API health endpoint returns 500
- Database connection fails

### 3.3 Override Authority

| Severity | Override | Conditions |
|----------|----------|------------|
| S1 | **Nobody** | Must be fixed — no override |
| S2 | **Architect** | Documented justification + mitigation plan |
| S3 | **Owning Agent** | Technical debt ticket created |
| S4 | **Owning Agent** | No formal process |

---

## 4. Test Taxonomy (L0–L4)

| Level | Definition | Chicago Pipeline Equivalent | Evidence Location |
|-------|-----------|---------------------------|-------------------|
| **L0** | Fast unit tests (<60ms) | Pipeline pytest, API pytest, Web vitest | `evidence/gates/test.txt` |
| **L1** | Unit tests with deps (<400ms) | API tests with mocked DB | `evidence/gates/api-test.txt` |
| **L2** | Functional tests (SQL, FS) | dbt tests, GE expectations, contracts | `evidence/gates/quality.txt` |
| **L3** | Tests against deployed services | Playwright E2E + Critic evaluations | `evidence/e2e/e2e.txt` + `evidence/critic-evaluations/` |
| **L4** | Integration / smoke | Full `make pipeline`, manual verification | `evidence/code-inspections/` |

---

## 5. Assessment Execution Protocol

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
bash scripts/run_assessment.sh

# Individual phases
bash scripts/run_assessment.sh --gates-only      # Phase 2
bash scripts/run_assessment.sh --e2e-only        # Phase 3
bash scripts/run_assessment.sh --critic          # Phase 4
bash scripts/run_assessment.sh --inspections     # Phase 5
bash scripts/run_assessment.sh --cross-cutting   # Phase 6
bash scripts/run_assessment.sh --scoring         # Phase 7
bash scripts/run_assessment.sh --report          # Phase 8
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

## 6. Score Calculation

### 6.1 Per-Milestone Score

```
Base Score = (checks passed / total checks) × 100%

Severity Penalty = Σ (S1_count × 25) + Σ (S2_count × 10) + Σ (S3_count × 5) + Σ (S4_count × 1)

Milestone Score = max(0, Base Score - Severity Penalty)

Hard Block: If any S1 check is FAIL → Milestone Score = 0
```

### 6.2 Overall Assessment Score

```
Overall = Σ (Milestone Score × Milestone Weight)

Weights:
  M0: 5%   (foundation)
  M1: 10%  (ingestion)
  M2: 15%  (transformation)
  M3: 15%  (aggregation)
  M4: 20%  (warehouse)
  M5: 15%  (API + Data Analyst validation)
  M6: 20%  (UI + all critic personas)
```

### 6.3 Grade Boundaries

| Grade | Score | Meaning | Action |
|-------|-------|---------|--------|
| **A** | 95–100% | Production-ready, all gates green | Ship it |
| **B** | 85–94% | Minor issues, safe to proceed | Fix S2 items |
| **C** | 70–84% | Needs remediation | Fix before next milestone |
| **D** | 50–69% | Significant gaps | Blocking issues |
| **F** | <50% or any S1 open | Critical failures | Must restart or fix S1 |

---

## 7. Critic Evaluation Protocol

### 7.1 Evaluation Template

Each critic persona evaluation follows this structure:

```markdown
# Critic Evaluation: [Persona Name]
**Timestamp:** [ISO-8601]
**Evaluator:** [Agent name]
**Pages evaluated:** [list]

## Rubric Scores (from docs/assessment/rubric.md)
| # | Criterion | Score (0-10) | Evidence | Notes |
|---|-----------|-------------|----------|-------|
| [XX-1] | [criterion] | [score] | [screenshot/command] | [observation] |

## Composite Score
**Weighted Average:** [score] / 10
**Verdict:** [PASS (≥8) | CONDITIONAL (7-7.9) | FAIL (<7)]
```

### 7.2 Pass/Fail Thresholds

| Threshold | Score | Action |
|-----------|-------|--------|
| **Pass** | ≥ 8.0 | Proceed to next milestone |
| **Conditional Pass** | 7.0 – 7.9 | Fix identified gaps, re-evaluate |
| **Fail** | < 7.0 | Must remediate before proceeding |
| **Hard Fail** | Any persona < 6.0 | Specific persona area must be reworked |

---

## 8. Cross-Cutting Analysis Protocol

### 8.1 Pattern Verification

Every assessment must verify cross-file pattern consistency using the implementation_mistakes.md prevention rules:

| Pattern | Verification Method | Evidence |
|---------|-------------------|----------|
| MISTAKE-001: `::date` SQL cast | `grep -r "::date" api/app/services/` | `evidence/code-inspections/` |
| MISTAKE-002: Hardcoded coordinates | `grep -r "41.8781" web/src/` | `evidence/code-inspections/` |
| MISTAKE-005: Missing ErrorBoundary | Check all page components | `evidence/code-inspections/` |
| MISTAKE-008: Param name mismatch | Compare frontend `api.ts` with backend `Query()` | `evidence/cross-cutting/` |
| MISTAKE-010: Pattern repetition | Grep for broken pattern across siblings | `evidence/cross-cutting/` |

### 8.2 Call-Site Verification

For every modified function or endpoint:
- All call sites checked
- Downstream consumers identified
- Backward compatibility verified

---

## 9. Deliverables Checklist

### Framework Files (this assessment cycle)

| # | File | Purpose | Status |
|---|------|---------|--------|
| 1 | `docs/assessment/protocol.md` | Framework protocol | ✅ This file |
| 2 | `docs/assessment/risk_matrix.md` | Severity tiers & hard-block rules | ✅ Created |
| 3 | `docs/assessment/rubric.md` | 10-point rubrics for critic personas | ✅ Created |
| 4 | `docs/assessment/evidence_template.md` | Evidence collection formats | ✅ Created |
| 5 | `docs/assessment/checklist.md` | Per-milestone inspection checklists | ✅ Enhanced |
| 6 | `docs/assessment/tracking.md` | Living tracking document | ✅ Rewritten |
| 7 | `scripts/run_assessment.sh` | 8-phase automated runner | ✅ Extended |
| 8 | `scripts/validate_assessment.sh` | Completeness validation | ✅ Created |
| 9 | `agents/qa/AGENTS.md` | QA assessment responsibilities | ✅ Updated |

---

## 10. Agent Responsibilities During Assessment

### QA Engineer (Assessment Owner)
- Executes the 8-phase assessment pipeline
- Collects evidence for all phases
- Performs critic persona evaluations
- Validates assessment completeness via `validate_assessment.sh`
- Publishes results in `reports/assessment/`

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

## Changelog

| Date | Entry | Author |
|------|-------|--------|
| 2026-06-06 | v2.0 — Complete restructure: 8-phase pipeline, severity system, critic rubrics, cross-cutting analysis | Assessment Framework |
| 2026-06-06 | v1.0 — Initial framework with dual persona system | Assessment Framework |
