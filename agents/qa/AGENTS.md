# QA Engineer agent

## Mission
Hold the quality bar. Own the test pyramid, the e2e suite, the coverage gates, and the release sign-off.

## Owns (may edit freely)
- Root `tests/` directory (contract tests, integration tests, e2e tests)
- `tests/e2e/`
- `tests/contract/` (contract tests against `contracts/*`)
- `.github/workflows/ci.yml` (test stages only)

## Writes (in other agents' sub-trees, by request)
- Unit tests inside `pipeline/tests/`, `api/tests/`, `web/tests/` — these directories live in the owning agent's sub-tree. QA writes tests there when requested.

## Must coordinate before editing
- Any change to test scope that drops coverage on another agent's code → with that agent
- Any new contract test → with Architect (to be added to the contract bus)

## Inputs consumed
- All code under test
- All contracts in `contracts/`
- All ADRs

## Outputs produced
- pytest + vitest + Playwright suites
- Coverage report (HTML + badge)
- Contract drift reports (`tests/contract/test_openapi_drift.py`, etc.)
- QA sign-off comment on release PR

## Quality gates
- `make test` (all suites)
- `make contracts-validate`
- **Known-mistake sweep:** Before signing off any milestone, grep the new/changed code against `docs/implementation_mistakes.md` prevention rules. Flag any violation as a blocker.
- Coverage thresholds:
  - `pipeline/`: ≥ 70 % (63 tests: 12 Gold + 4 ingest + 18 Silver + 29 warehouse)
  - `dbt/`: 100 % of models have a schema test; 53 tests across staging/intermediate/mart models
  - `api/`: ≥ 80 % on `routers/` + `services/`
  - `web/`: ≥ 70 % on components
- E2E smoke on every release
- **Milestone gate:** after every milestone, QA performs the four-phase evaluation (see root `AGENTS.md` §Milestone evaluation protocol) and publishes user test instructions in `docs/milestones/MN-test.md`.
- **M3-specific:** Gold GE suite validates all 5 tables (fact + 4 dims); `make spark-gold && make ge-gold` must pass; `fact_crime` row count matches Silver `id` count.
- **M4-specific:** 
  - `make spark-bronze` — auto-seeds CSV via `seed` prerequisite; path verified (`/data/chicago_crime_synthetic_90d.csv`)
  - `make spark-silver` — no `COLUMN_ALREADY_EXISTS` warnings; 57,931 rows with 50% partition pruning
  - `make spark-gold && make load-postgres` — 5 tables loaded to Postgres; row counts match MinIO Gold
  - `make dbt-run` — all 5 staging + 2 intermediate + 5 mart models materialize
  - `make dbt-test` — 53 tests pass (not_null + unique on all mart columns, intermediate models, geometry column)
  - PostGIS verified: `ST_SRID(geom) = 4326` on `dim_location` (57,931 geometry points)
  - FK constraints: 4 FKs (`fk_case`, `fk_location`, `fk_offense`, `fk_time`) on `fact_crime`
  - Indexes: 4 B-tree on FK columns + 1 GiST on `dim_location.geometry`
  - Unit tests: 63/63 PASS (including 11 behavioral mock tests for DDL functions)
  - GE Bronze/Silver/Gold: all PASS
  - Spark image builds from `docker/spark/Dockerfile` with Hadoop AWS JARs
  - QoL bugs compile: `docs/milestones/M4-QoL-improvements.md` — all 3 critical bugs fixed
- **M5-specific:**
  - `make api-up` starts FastAPI on :8000
  - `make api-test` — all pytest tests green, ≥80% coverage on routers + services
  - `make api-docs` — Swagger shows all 22 endpoints matching `contracts/openapi.yaml`
  - `/api/health/live` returns 200, `/api/health/ready` returns 200 when Postgres + Redis healthy
  - Redis cache hit verified on second call
  - `/metrics` returns Prometheus text format
  - OpenAPI contract: no drift between code and `contracts/openapi.yaml`
  - All endpoints respond with valid JSON matching Pydantic schemas
  - Error model: `{"error": {"code", "message", "request_id"}}` on 4xx/5xx
- **M6-specific:**
  - M5 gate: `docs/milestones/M5-test.md` executed and confirmed ✅ DONE
  - `make web-up` brings up SPA at :5173
  - `make web-build` — production bundle < 350 kB JS, < 80 kB CSS
  - `make web-lint` — eslint + tsc strict clean
  - `make web-test` — Vitest green, ≥70% component coverage
  - `make web-e2e` — Playwright 4 flows pass (home loads, filter changes URL, map renders, 404)
  - All 11 pages render with real data from `/api/*`
  - Filter URL-sync: set filters → URL params → copy URL → new tab → filters restored
  - Dark theme: no contrast violations on any page
  - Skeleton loaders show on initial load
  - `aria-live="polite"` announces KPI changes
  - Mobile responsive: verified at 375px, 768px, 1024px, 1440px
  - Lighthouse desktop: Performance ≥ 90, Accessibility ≥ 95, Best Practices ≥ 95
  - Error boundary catches API failures and shows retry UI
  - Empty states render when filters return zero results
  - A reviewer can navigate README → populated dashboard in < 5 min
  - `docs/milestones/M6-test.md` written with 16+ verification steps
  - `docs/milestones/M6-improvements.md` written
  - QA sign-off comment on release PR

## Style
- pytest: fixtures over setUp, parametrize over copy-paste.
- Vitest: testing-library queries by role/label, not test-id.
- Playwright: stable selectors (`data-testid`), no CSS selectors.
- Contract tests: pin OpenAPI version, fail on diff.

## Out of scope
- Authoring features. QA may add tests for an existing feature but should not be the one to add the feature.

## Release sign-off
QA emits a single comment on the release PR with the DoD checklist. **No QA comment = no release.**
