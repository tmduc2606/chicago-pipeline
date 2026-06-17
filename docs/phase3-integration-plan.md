# Phase 3 Integration Plan — M7 (EDA) → M8 (Production Hardening)

> **Status:** APPROVED — authored 2026-06-17, the project architect agent.
> **Scope:** Final integration, evaluation, and production hardening of the chicago-pipeline platform.
> **Milestones covered:** M7 (EDA Layer — integration verification) → M8 (Production Hardening).

---

## Table of Contents

1. [Current State Assessment](#1-current-state-assessment)
2. [M7 Integration & Debug Plan](#2-m7-integration--debug-plan)
3. [M8 Production Hardening Plan](#3-m8-production-hardening-plan)
4. [Agent File Cleanup](#4-agent-file-cleanup)
5. [Evaluation & Debugging Framework](#5-evaluation--debugging-framework)
6. [Execution Order & Commits](#6-execution-order--commits)

---

## 1. Current State Assessment

| Milestone | Status | Owner | Notes |
|-----------|--------|-------|-------|
| M0–M4 | ✅ Complete | Data Engineer | Pipeline, warehouse, dbt — all green |
| M5 (API) | ✅ Complete | Backend | 42/42 tests, OpenAPI clean |
| M6 (Web) | ✅ Complete | Frontend | Grade A, 40/40 E2E, 8.39 composite |
| **M7 (EDA)** | 🟡 Partial | QA | Notebook + reports exist; integration unverified |
| **M8 (Production)** | 🔴 Not started | SRE + all | Needs scoping and execution |

### M7 What's Done
- `scripts/notebooks/M7_EDA.ipynb` — 39 analyses across 7 sections
- `reports/eda/` — 39 insight reports in 7 subdirectories
- `web/src/pages/InsightsPage.tsx` — Insights page component
- `web/src/config/insights.json` — 14 extended insight entries
- `web/src/config/viz-catalog.yaml` — Chart registry
- `agents/eda-lead/` and `agents/eda-researcher/` agent files

### M7 What Needs Verification
- Insights page renders with real data from the running API
- All 39 reports follow the template (topic, tag, difficulty, caveat)
- `insights.json` values match actual notebook output
- Playwright E2E covers Insights page (load, filter, card render)
- `make lint && make test` still green after M7 changes

### What's NOT in Scope
- **M8 Agentic AI** — removed (redundant, 16 GB RAM constraint)
- **Auth (JWT/API key)** — removed (public portfolio dashboard)
- **LLM Integration agent** — not needed

---

## 2. M7 Integration & Debug Plan

**Goal:** Verify the EDA layer is fully integrated and the Insights page works end-to-end.

### Phase A: M7 Verification Steps

| Step | Agent | Action | Pass/Fail Criteria |
|------|-------|--------|--------------------|
| A1 | **QA** | Run `make lint && make test` | All suites green |
| A2 | **QA** | Verify `InsightsPage.tsx` renders in the running stack | Page loads at `/insights`, cards render |
| A3 | **QA** | Verify all 39 reports exist and follow template | `reports/eda/INDEX.md` lists all 39; each has topic/tag/difficulty/caveat |
| A4 | **QA** | Verify `insights.json` values match notebook output | Spot-check 5 entries against `M7_EDA.ipynb` outputs |
| A5 | **QA** | Run Playwright E2E — Insights page | Page loads, topic filter works, card count > 0 |
| A6 | **QA** | Publish `docs/milestones/M7-test.md` | Numbered commands, expected output, pass/fail criteria |
| A7 | **Architect** | Review M7 gate — sign off or open bug-fix PR | All S1 items pass |

### M7 Debugging Protocol

If any step fails:

1. **QA opens a `bugfix/m7-integration` PR** with the finding
2. **Owning agent reviews** (Frontend for page issues, Data Engineer for data issues)
3. **Fix is applied** and verified by QA
4. **Architect signs off** on the fix

**Severity handling:**
- **S1 (Critical):** Page doesn't load, notebook won't execute → hard block, fix immediately
- **S2 (High):** Reports missing template sections, insights.json stale → fix before M8
- **S3 (Medium):** Minor formatting issues → log for M8 polish
- **S4 (Low):** Cosmetic issues → log for opportunistic fix

---

## 3. M8 Production Hardening Plan

**Goal:** Harden the platform for a clean, portfolio-grade presentation.

### Phase B: M8 Production Hardening Steps

| Step | Agent | Action | Pass/Fail Criteria |
|------|-------|--------|--------------------|
| B1 | **SRE** | Verify all healthchecks: `make up && make health` | All 13 services healthy in < 60s |
| B2 | **SRE** | Verify Prometheus + Grafana dashboards render | Dashboards load with real data within 30s |
| B3 | **Frontend** | Implement light mode toggle | Theme switch works, no contrast violations in either mode |
| B4 | **Frontend** | Add "About / Data Sources / Methodology" page | New page at `/about` with source attribution, methodology, limitations |
| B5 | **QA** | Run full assessment: `bash scripts/run_assessment.sh` | All 8 phases complete, no S1 findings |
| B6 | **QA** | Run critic evaluations (8-persona rubric) | All personas ≥ 7.0, composite ≥ 8.0 |
| B7 | **Security** | Run `gitleaks detect` on all new files | No secrets found |
| B8 | **Docs** | Update `README.md` with final screenshots/GIF, FAQ | README stands alone for reviewers |
| B9 | **Docs** | Update `CHANGELOG.md` with M7 + M8 release notes | v0.8.0 entry complete |
| B10 | **Architect** | Final sign-off — all DoD items checked | Release comment on PR |

### M8 Deliverables Checklist

- [ ] `make up && make health` — all services healthy
- [ ] `make pipeline` — end-to-end pipeline runs clean
- [ ] `make lint` — ruff + mypy + eslint + tsc green
- [ ] `make test` — pytest + vitest green
- [ ] `make contracts-validate` — no drift
- [ ] Light mode toggle works
- [ ] About page exists and renders
- [ ] Grafana dashboards render with data
- [ ] `gitleaks` clean
- [ ] README updated with screenshots
- [ ] CHANGELOG updated
- [ ] Architect sign-off recorded

---

## 4. Agent File Cleanup

Several agent files reference the old milestone structure (M8 Agentic AI, M9 with auth). These must be updated before M8 begins.

| Step | Agent | File | Change |
|------|-------|------|--------|
| C1 | **Architect** | `agents/architect/AGENTS.md` | Remove M8 Agentic AI, update M9→M8, remove auth reference |
| C2 | **QA** | `agents/qa/AGENTS.md` | Remove `make agents-lint` from cross-milestone gate; update M7 scope to complete |
| C3 | **Architect** | `agents/qa/AGENTS.md` | Update milestone scope references (M0–M7 → M0–M8) |

---

## 5. Evaluation & Debugging Framework

### 5.1 Four-Phase Cycle (per milestone)

Every milestone follows the same cycle. **No milestone is complete until all four phases pass.**

```
Phase 1: Implement     → Owning agent(s) produce deliverables
Phase 2: Evaluate      → QA runs all checks (lint, tests, contracts, structural, security)
Phase 3: User Test     → QA publishes MN-test.md; user verifies
Phase 4: Improvements  → Non-blocking improvements documented for polish
```

### 5.2 Assessment Execution (QA-owned)

```bash
# Full assessment (all 8 phases)
bash scripts/run_assessment.sh --milestone M7 --full
bash scripts/run_assessment.sh --milestone M8 --full

# Individual phases (for debugging)
bash scripts/run_assessment.sh --gates-only    # Phase 2: lint, test, contracts
bash scripts/run_assessment.sh --e2e-only       # Phase 3: Playwright
bash scripts/run_assessment.sh --critic         # Phase 4: Persona evaluations
bash scripts/run_assessment.sh --inspections    # Phase 5: Code pattern checks
bash scripts/run_assessment.sh --cross-cutting  # Phase 6: Cross-file consistency
bash scripts/run_assessment.sh --scoring        # Phase 7: Score calculation
bash scripts/run_assessment.sh --report         # Phase 8: Summary report
```

### 5.3 Severity System

| Tier | Name | Impact | Block Status |
|------|------|--------|-------------|
| **S1** | Critical | -25% per item | **HARD BLOCK** — assessment fails automatically |
| **S2** | High | -10% per item | Architect override required |
| **S3** | Medium | -5% per item | Tracked for polish |
| **S4** | Low | -1% per item | Informational |

**Hard-block rules:** Assessment fails if any S1 is open, `make lint` fails, `make test` fails, `gitleaks` finds secrets, or `make contracts-validate` fails.

### 5.4 Grade Boundaries

| Grade | Score | Meaning |
|-------|-------|---------|
| **A** | 95–100% | Production-ready, all gates green |
| **B** | 85–94% | Minor issues, safe to proceed |
| **C** | 70–84% | Needs remediation |
| **D** | 50–69% | Significant gaps |
| **F** | <50% or any S1 open | Critical failures |

### 5.5 Debugging Protocol

1. **Identify** — QA runs assessment, identifies failing check
2. **Classify** — Assign severity (S1–S4)
3. **Assign** — Route to owning agent based on file ownership
4. **Fix** — Owning agent creates bug-fix PR
5. **Verify** — QA re-runs the failing check
6. **Sign off** — Architect confirms fix (S2+ requires Architect override)

### 5.6 Cross-Milestone Regression Gate

Before M8 begins, M0–M6 must still pass:

```bash
make lint && make test && make pipeline && make contracts-validate
```

---

## 6. Execution Order & Commits

### Recommended Sequence

| Order | Step | Agent | Commit Message |
|-------|------|-------|----------------|
| 1 | C1: Fix Architect AGENTS.md | Architect | `chore: update architect agent — remove M8 Agentic AI, M9→M8` |
| 2 | C2+C3: Fix QA AGENTS.md | QA + Architect | `chore: update QA agent — remove agents-lint gate, update milestone refs` |
| 3 | A1: Run lint + test | QA | — (verification only) |
| 4 | A2–A5: M7 integration verification | QA | — (verification only) |
| 5 | A6: Publish M7 test instructions | QA | `docs: publish M7 user test instructions` |
| 6 | B1–B2: SRE healthcheck verification | SRE | — (verification only) |
| 7 | B3: Light mode toggle | Frontend | `feat: add light mode theme toggle` |
| 8 | B4: About page | Frontend | `feat: add About / Data Sources / Methodology page` |
| 9 | B5–B6: Full assessment + critic eval | QA | `docs: run M8 assessment — Grade A` |
| 10 | B7: Security scan | Security | — (verification only) |
| 11 | B8: README update | Docs | `docs: update README with final screenshots and FAQ` |
| 12 | B9: CHANGELOG update | Docs | `docs: update CHANGELOG.md with v0.8.0 release notes` |
| 13 | B10: Architect sign-off | Architect | `chore: architect sign-off on M8 production hardening` |

### Gate Rule

**M8 does not start until M7 user test instructions have been executed and the user has confirmed M7.**

---

*End of Phase 3 Integration Plan — execute M7 verification first.*
