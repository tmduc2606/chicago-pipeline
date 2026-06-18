# Phase C — Final Polish & End-to-End Benchmark Plan

> **Status:** DRAFT — 2026-06-18, Architect agent
> **Scope:** Clean up stale M9 references, run full end-to-end benchmark, fix bugs, final sign-off
> **Depends on:** M8 Production Hardening complete (all 11 steps done)

---

## Step 1: Clean Up Stale M9 References

Six files reference "M9" or "M9 polish pass" that need updating since M9 was renumbered to M8.

### 1.1 `AGENTS.md` (root)

| Line | Current | Updated |
|------|---------|---------|
| §Milestone evaluation protocol | "Every milestone (M0–M9)" | "Every milestone (M0–M8)" |
| §Phase 4 — Improvements | "in a polish pass (M9)" | "in M8 polish" |

### 1.2 `agents/frontend/AGENTS.md`

| Line | Current | Updated |
|------|---------|---------|
| §M6 scope | "Theme: Dark-only. Light mode toggle deferred to M9." | "Theme: Dark + light toggle (implemented in M8)." |

### 1.3 `agents/qa/AGENTS.md`

| Line | Current | Updated |
|------|---------|---------|
| §Severity Handling (S4) | "Log in tracking document. Address opportunistically." | "Log in tracking document. Address opportunistically." (no change needed — S4 doesn't reference M9) |

Actually, checking the QA AGENTS.md more carefully — the S4 plain text says "Address opportunistically" with no M9 reference. No change needed here.

### 1.4 `docs/assessment/preparation.md`

| Line | Current | Updated |
|------|---------|---------|
| §Header | "**Next Milestone:** M7 (or M9 polish pass)" | "**Next Milestone:** M8 (production hardening, final)" |

### 1.5 `docs/assessment/risk_matrix.md`

| Line | Current | Updated |
|------|---------|---------|
| §6. Escalation Protocol (S3) | "S3 found → Log in overhaul → Schedule for next sprint or M9 polish" | "S3 found → Log in overhaul → Schedule for M8 polish" |

### 1.6 `docs/assessment/tracking.md`

| Line | Current | Updated |
|------|---------|---------|
| §Improvement Backlog header | "Non-blocking improvements proposed by Architect and QA agents. Addressed opportunistically or in M9 polish pass." | "Non-blocking improvements proposed by Architect and QA agents. Addressed in M8 polish pass." |

### 1.7 Test files with Known Limitations references

These test files reference "deferred to M9" in their Known Limitations sections. Update to reflect current state:

**`docs/milestones/M6-test.md`:**
- "No JWT auth (public dashboard, auth deferred to M9)" → "No JWT auth (public dashboard, auth out of scope)"
- "No dark/light mode toggle (dark only, toggle deferred to M9)" → "Dark/light mode toggle implemented in M8 ✅"
- "Choropleth map uses random points (real district boundaries deferred to M9)" → "Choropleth map uses simplified district positions (real GeoJSON deferred)"
- "Chunk size warning on build (ECharts+MapLibre bundle ~2.8MB, code splitting deferred to M9)" → "Chunk size warning on build (ECharts+MapLibre bundle ~2.8MB, code splitting deferred)"

**`docs/milestones/M5-test.md`:**
- "CORS configured for localhost only (production origins deferred to M9)" → "CORS configured for localhost only (production origins out of scope)"

**`docs/milestones/M1-M5-Hotfixes-and-QoL.md`:**
- Any rows with "Deferred to M9" → "Deferred (no M9)"

---

## Step 2: End-to-End Benchmark (QA Critic Agent)

Run the full 8-phase assessment pipeline against M8.

### 2.1 Phase 1 — Prerequisites
- [ ] Docker Desktop running
- [ ] All 12 services healthy (`docker compose ps`)
- [ ] Required files exist (source check)
- [ ] Agent files present (all 8 agents × 3 files)

### 2.2 Phase 2 — Automated Gates
- [ ] API lint: `ruff check app` → All checks passed
- [ ] API type check: `mypy app` → Success
- [ ] API tests: `pytest tests/` → 42/42 passed
- [ ] Pipeline tests: `pytest pipeline/tests/` → 63/63 passed
- [ ] Contracts validate: `make contracts-validate` → PASS
- [ ] gitleaks: `gitleaks detect` → 0 leaks

### 2.3 Phase 3 — E2E Verification (Browser)
- [ ] Dashboard loads at `http://localhost:5173/`
- [ ] All 6 pages render: Dashboard, Crime Types, Locations, Analysis, Insights, About
- [ ] Sidebar navigation works for all 6 pages
- [ ] Theme toggle switches dark/light mode
- [ ] At least one chart renders with data
- [ ] Insights page shows 14 cards
- [ ] About page shows all 5 sections
- [ ] No console errors

### 2.4 Phase 4 — Critic Persona Evaluations
Score all 8 personas on all 6 pages (where applicable):

| Persona | Perspective | Min Score |
|---------|-------------|-----------|
| Data Analyst | "Can I trust the numbers?" | 7.0 |
| Citizen | "Can I understand this?" | 7.0 |
| Executive | "30-second insight?" | 7.0 |
| Journalist | "Can I find stories?" | 7.0 |
| First-Timer | "Figure out in 2 min?" | 7.0 |
| Policy Maker | "Defensible for policy?" | 7.0 |
| Community Organizer | "Can I use this for my community?" | 7.0 |
| News Editor | "Is this publication-ready?" | 7.0 |

**Composite target:** ≥ 8.0 (maintaining M6 Grade A)

### 2.5 Phase 5 — Code Inspections
- [ ] `implementation_mistakes.md` prevention rules pass
- [ ] No hardcoded secrets or coordinates
- [ ] Error boundaries on all pages
- [ ] Contract consistency (frontend ↔ backend)

### 2.6 Phase 6 — Cross-Cutting
- [ ] All pipeline stages present (bronze, silver, gold, warehouse, dbt)
- [ ] OpenAPI contract matches frontend API calls
- [ ] No PII exposure in code

### 2.7 Phase 7 — Scoring
- [ ] Base score: (checks passed / total checks) × 100%
- [ ] Severity penalty applied
- [ ] Grade calculated (target: A, ≥ 95%)

### 2.8 Phase 8 — Report
- [ ] `reports/assessment/summary.md` generated
- [ ] `docs/assessment/tracking.md` updated with final run

---

## Step 3: Bug-Fixes & Hot-Fixes

Based on Step 2 findings, classify and fix:

| Severity | Action | SLA |
|----------|--------|-----|
| S1 (Critical) | Immediate fix — broken features, test failures | Before final sign-off |
| S2 (High) | Fix before final sign-off — UX issues | Before final sign-off |
| S3 (Medium) | Fix if time permits — code quality | Opportunistic |
| S4 (Low) | Log for future — cosmetic | Log only |

---

## Step 4: Minor Improvements

Verify and polish:
- [ ] All 6 pages render correctly in dark mode
- [ ] All 6 pages render correctly in light mode
- [ ] Theme toggle persists across page navigation and browser refresh
- [ ] Grafana dashboards accessible and rendering panels
- [ ] About page all 5 sections render with content
- [ ] Insights page filters work (topic, tag, difficulty)
- [ ] No JavaScript console errors on any page
- [ ] No React warnings in development mode
- [ ] Responsive layout verified at 375px, 768px, 1024px, 1440px

---

## Step 5: Final End-to-End Pipeline Test

Run `make demo` from a clean state:

1. `docker compose down -v` (clean slate)
2. `docker compose up -d --build` (rebuild all services)
3. Wait for pipeline-init to complete (Bronze → Silver → Gold → Postgres → dbt)
4. Verify all services healthy
5. Open dashboard, verify all pages render with data
6. Verify all features work (filters, theme toggle, maps, charts, insights, about)

---

## Step 6: Final Sign-Off

- [ ] Update `docs/assessment/tracking.md` with final run results
- [ ] Create `docs/milestones/M8-final-benchmark.md` with critic scores
- [ ] Architect final sign-off on complete platform
- [ ] Total milestone count: M0–M8 (no M9)
- [ ] Platform status: Portfolio-ready ✅

---

*End of Phase C Plan*
