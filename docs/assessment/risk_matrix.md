# Assessment Risk Matrix — Severity Tiers & Hard-Block Rules

**Date:** 2026-06-06
**Status:** ACTIVE
**Authority:** Root AGENTS.md §Milestone evaluation protocol

---

## 1. Severity Tier Definitions

Every assessment check item is classified into one of four severity tiers. The tier determines the score impact, resolution SLA, and whether the assessment can pass.

| Tier | Name | Definition | Score Impact | Resolution SLA | Assessment Impact |
|------|------|-----------|--------------|----------------|-------------------|
| **S1** | Critical | Breaks production, causes data loss, exposes security vulnerability, or blocks all users | **-25% per item** | Must fix before next milestone | **HARD BLOCK** — assessment fails if any S1 is open |
| **S2** | High | Degrades user experience, causes performance regression, or violates contract | **-10% per item** | Fix within current milestone | **SOFT BLOCK** — requires Architect override to proceed |
| **S3** | Medium | Code quality, maintainability, or documentation gap | **-5% per item** | Fix or document technical debt | Warning — tracked in overhaul |
| **S4** | Low | Style, naming, minor polish, or non-blocking improvement | **-1% per item** | Fix opportunistically | Informational — logged only |

---

## 2. Hard-Block Rules

An assessment **fails automatically** if any of the following conditions are true:

### 2.1 Critical Severity (S1) — Automatic Failure

| Rule ID | Condition | Rationale |
|---------|-----------|-----------|
| HB-01 | Any S1 check item is marked FAIL | Critical issues block production deployment |
| HB-02 | `make lint` fails | Code does not compile/pass static analysis |
| HB-03 | `make test` fails | Existing functionality is broken |
| HB-04 | `gitleaks detect` finds secrets | Security breach — no exceptions |
| HB-05 | `make contracts-validate` fails | Cross-agent contract is broken |
| HB-06 | Any Playwright E2E test crashes (not asserts — crashes) | Application is unstable |
| HB-07 | API health endpoint returns 500 | Core infrastructure is down |
| HB-08 | Database connection fails | Data layer is unavailable |

### 2.2 High Severity (S2) — Architect Override Required

| Rule ID | Condition | Rationale |
|---------|-----------|-----------|
| HO-01 | More than 3 S2 items are open | Cumulative high-severity debt exceeds threshold |
| HO-02 | Any S2 item is older than 2 milestones | Stale technical debt |
| HO-03 | S2 item affects cross-cutting concern (security, auth, data integrity) | Cross-cutting S2 items have outsized risk |

### 2.3 Cumulative Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| Total S1 open | > 0 | **FAIL** — cannot proceed |
| Total S2 open | > 5 | **WARNING** — Architect must review |
| Total S3 open | > 15 | **WARNING** — schedule tech debt sprint |
| Overall score | < 70% | **FAIL** — milestone incomplete |
| Critic average score | < 6/10 | **WARNING** — user experience insufficient |

---

## 3. Severity Classification by Check Category

### 3.1 Automated Gates

| Check | Default Severity | Rationale |
|-------|-----------------|-----------|
| `make lint` (ruff) | S1 | Code style violations block CI |
| `make lint` (mypy) | S2 | Type safety gaps (pre-existing allowed) |
| `make lint` (eslint) | S1 | Frontend code quality |
| `make lint` (tsc) | S1 | TypeScript compilation |
| `make test` (pytest) | S1 | Backend functionality broken |
| `make test` (vitest) | S1 | Frontend functionality broken |
| `make contracts-validate` | S1 | Cross-agent contract broken |
| `make agents-lint` | S2 | Agent spec non-compliance |
| `make quality` (GE) | S1 | Data quality gate failed |
| `make quality` (dbt) | S1 | Data model tests failed |
| `gitleaks detect` | S1 | Secret exposure |
| `make api-test` | S1 | API regression |
| `make web-test` | S1 | Frontend regression |
| `make web-e2e` | S1 | E2E flow broken |

### 3.2 Code Inspections

| Check Type | Default Severity | Rationale |
|------------|-----------------|-----------|
| File exists and is non-empty | S1 | Missing deliverable |
| Correct function/class signature | S2 | API contract drift |
| Required imports present | S2 | Dependency missing |
| Error handling present | S2 | Resilience gap |
| Tests cover new code | S2 | Coverage regression |
| Documentation updated | S3 | Doc drift |
| Style guide compliance | S4 | Naming/formatting |

### 3.3 Critic Evaluations

| Check Type | Default Severity | Rationale |
|------------|-----------------|-----------|
| Data accuracy (numbers match) | S1 | Trust violation |
| Core functionality works | S1 | Feature broken |
| Accessibility violation (WCAG AA) | S2 | Legal/compliance risk |
| Performance below threshold | S2 | User experience degradation |
| Usability issue | S3 | UX friction |
| Visual polish | S4 | Aesthetic improvement |

---

## 4. Score Calculation with Severity Weighting

### 4.1 Per-Milestone Score

```
Base Score = (checks passed / total checks) × 100%

Severity Penalty = Σ (S1_count × 25) + Σ (S2_count × 10) + Σ (S3_count × 5) + Σ (S4_count × 1)

Milestone Score = max(0, Base Score - Severity Penalty)
```

### 4.2 Hard-Block Override

```
If any S1 check is FAIL:
    Milestone Score = 0 (automatic failure)
    Grade = F
    Cannot proceed to next milestone
```

### 4.3 Overall Assessment Score

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

### 4.4 Grade Boundaries (with Hard-Block)

| Grade | Score | Meaning | Action |
|-------|-------|---------|--------|
| **A** | 95–100% | Production-ready, all gates green | Ship it |
| **B** | 85–94% | Minor issues, safe to proceed | Fix S2 items |
| **C** | 70–84% | Needs remediation | Fix before next milestone |
| **D** | 50–69% | Significant gaps | Blocking issues — must remediate |
| **F** | <50% or any S1 open | Critical failures | Must restart or fix S1 items |

---

## 5. Evidence Requirements per Severity

| Severity | Evidence Required | Format |
|----------|-------------------|--------|
| **S1** | Command output, screenshot, or code reference proving failure | `reports/assessment/evidence/S1-{ID}.md` |
| **S2** | Command output or code reference with context | `reports/assessment/evidence/S2-{ID}.md` |
| **S3** | Description of gap with code reference | Noted in checklist |
| **S4** | Description of improvement opportunity | Noted in checklist |

---

## 6. Escalation Protocol

```
S1 found → STOP assessment → Create bug-fix PR → Block milestone
S2 found → Log in overhaul → Architect review → Decide: fix now or override
S3 found → Log in overhaul → Schedule for next sprint or M9 polish
S4 found → Log in overhaul → Address opportunistically
```

---

## 7. Override Authority

| Severity | Who Can Override | Conditions |
|----------|-----------------|------------|
| S1 | **Nobody** | Must be fixed — no override possible |
| S2 | **Architect** | With documented justification and mitigation plan |
| S3 | **Owning Agent** | With technical debt ticket created |
| S4 | **Owning Agent** | No formal process needed |

---

## Changelog

| Date | Entry | Author |
|------|-------|--------|
| 2026-06-06 | Initial risk matrix with S1-S4 tiers and hard-block rules | Assessment Framework |
