# M0 — User test instructions

> Date: 2026-06-03 | Milestone: M0 Skeleton & docs

## Prerequisites

- Docker Desktop (or Docker Engine + Compose v2) installed and running.
- Ports `3000, 3001, 5432, 6379, 8000, 8080, 8081, 9000, 9001, 9090, 5173` available.

## Test steps

### 1. Verify repo structure

```bash
# From the project root
ls -la
```

**Expected:** You should see: `AGENTS.md`, `README.md`, `Makefile`, `docker-compose.yaml`, `.env.example`, `.gitignore`, `.editorconfig`, `.pre-commit-config.yaml`, `CODEOWNERS`, `LICENSE`, `SECURITY.md`, `CHANGELOG.md`, plus directories `agents/`, `contracts/`, `docs/`, `pipeline/`, `dbt/`, `airflow/`, `api/`, `web/`, `observability/`, `lineage/`, `scripts/`, `data/`.

**Pass if:** All files and directories are present.

### 2. Verify agent spec

```bash
ls agents/*/AGENTS.md agents/*/PROMPT.md agents/*/CONTRACTS.md
```

**Expected:** 24 files (8 agents × 3 files each).

**Pass if:** All 24 files exist and are non-empty.

### 3. Verify contracts bus

```bash
ls contracts/
```

**Expected:** `README.md`, `openapi.yaml`, `dbt-manifest.json`, `api-types.ts`, `event-catalog.md`, `design-tokens.json`, `CHANGELOG.md`.

**Pass if:** All 7 files exist.

### 4. Validate contracts

```bash
python -c "
import os, json, yaml
repo = '.'
yaml.safe_load(open('contracts/openapi.yaml'))
json.load(open('contracts/dbt-manifest.json'))
json.load(open('contracts/design-tokens.json'))
print('All contracts valid.')
"
```

**Expected:** `All contracts valid.`

**Pass if:** No errors.

### 5. Verify ADRs

```bash
ls docs/adr/
```

**Expected:** 4 ADR files: `0001-minio-over-seaweedfs.md`, `0002-spark-then-dbt.md`, `0003-fastapi-react.md`, `0004-no-auth-public.md`.

**Pass if:** All 4 ADRs present with Context, Decision, Consequences, Alternatives sections.

### 6. Verify implementation plan

```bash
head -5 docs/IMPLEMENTATION_PLAN.md
```

**Expected:** Title: `# End-to-End Chicago Crime DBMS — Implementation Plan (2024–2026)`.

**Pass if:** File is present and starts with the expected title.

### 7. Verify architecture doc

```bash
grep "Agent ownership table" docs/architecture.md
```

**Expected:** `## Agent ownership table`.

**Pass if:** Ownership table present with all 8 agents listed.

### 8. Check .env template

```bash
cat .env.example
```

**Expected:** Contains `POSTGRES_DB=chicago`, `POSTGRES_USER=chicago`, `MINIO_ROOT_USER=minio`, `AIRFLOW_ADMIN_USER=admin`, `GRAFANA_ADMIN_USER=admin`. All passwords are `change_me_local`.

**Pass if:** All placeholder values present, no real secrets.

### 9. Verify Makefile targets

```bash
make help
# On Windows without make, parse directly:
python -c "import re; mf=open('Makefile').read(); targets=re.findall(r'^(\w[\w-]*)\s*:', mf, re.MULTILINE); print('\n'.join(targets))"
```

**Expected:** A list of targets including `up`, `down`, `pipeline`, `quality`, `api-test`, `web-build`, `lint`, `test`, `demo`, `contracts-validate`, `agents-lint`.

**Pass if:** All expected targets listed.

### 10. Verify CHANGELOG

```bash
head -20 CHANGELOG.md
```

**Expected:** Contains `## [Unreleased]` with entries for "Added (M0)", "Fixed (M0 precision pass)", and "Added (milestone evaluation protocol)".

**Pass if:** All three sections present.

### 11. Seed test data (dry-run)

```bash
bash scripts/seed.sh
```

**Expected:** Script runs without error and produces `data/chicago_crime_synthetic_90d.csv` with ~54,000 rows.

**Pass if:** File created, row count between 50,000 and 60,000.

**Cleanup:** `rm data/chicago_crime_synthetic_90d.csv` (optional, the file is gitignored).

## Known limitations (not yet implemented)

- `docker compose up` will fail because the `pipeline/`, `api/`, `web/`, `airflow/` directories are empty (M1–M8 deliverables).
- `make pipeline` will fail (no Spark jobs or dbt project yet).
- `make api-test` will fail (no FastAPI service yet).
- `make web-build` will fail (no React app yet).
- Prometheus, Grafana, and Marquez will start but have no dashboards or scrape targets yet.
