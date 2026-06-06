# M4 QoL Hotfixes Catalogue — Post-Evaluation Plan

**Created:** 2026-06-05
**Last updated:** 2026-06-05
**Status:** 4/5 hotfixes implemented. H4 (GE Gold) remains open.
**Scope:** Remaining fixes + new issues discovered during all-rounded evaluation (2026-06-04)
**Evaluation results:** Bronze 57,931 ✓ | Silver 57,931 ✓ | Gold 5 tables ✓ | Postgres 5 tables ✓ | dbt 12/12 + 53/53 ✓ | GE Bronze/Silver ✓ | Unit tests 63/63 ✓

---

## Part A — Original Catalogue Status

Cross-reference with `docs/milestones/M4-QoL-improvements.md`:

| # | Item | Status | Notes |
|---|------|--------|-------|
| 1 | Bronze CSV path mismatch | ✅ FIXED | `scripts/seed.py` + Makefile `seed` target + `/data/` path |
| 2 | Hadoop AWS JARs missing | ✅ FIXED | `docker/spark/Dockerfile` with JARs + all Python deps |
| 3 | Data volume mount | ✅ FIXED | `./data:/data` on both spark-master and spark-worker |
| 4 | Silver COLUMN_ALREADY_EXISTS | ✅ FIXED | Bronze writer drops `ingest_date` before write; `--ingest-date` CLI arg added |
| 5 | Duplicate scripts | ✅ FIXED | `pipeline/scripts/` removed; docstrings updated to `/opt/scripts/` |
| 6 | dbt .user.yml | ✅ FIXED | Added to `.gitignore` in previous M4 session |
| 7 | Script directory inconsistency | ✅ FIXED | `pipeline/scripts/` removed; canonical paths in docstrings |
| 8 | Silver partition pruning | ✅ FIXED | `--ingest-date` CLI arg on `to_silver.py` for per-partition processing |
| 9 | Gold _gold_ingest_ts | ✅ FIXED | Already preserved from Gold Parquet; no change needed |
| 10 | GE in Airflow DAGs | 🔓 OPEN | Deferred — M5 Airflow territory |
| 11 | dbt env var defaults | ✅ BY DESIGN | Fail-fast is intentional; `.env.example` documents vars |
| 12 | dbt deps not wired | ✅ FIXED | `dbt-run` depends on `dbt-deps` in Makefile |
| 13 | Airflow Dockerfiles missing | 🔜 M5 | Expected — M5/M6 territory |
| 14 | make not on Windows | ✅ FIXED | `scripts/pipeline.ps1` created with PowerShell equivalents |

---

## Part B — Fixes Applied During Evaluation (not in original catalogue)

These were implemented on 2026-06-04 to make the all-rounded evaluation pass:

### E1. spark-master volume mounts expanded
**Why:** Unit tests (`test_gold.py`, `test_warehouse.py`) expect `/opt/contracts/`, `/opt/scripts/`, `/opt/airflow/dags/`, `/opt/Makefile` inside the container. Without these mounts, 18 tests fail.
**What:** Added `contracts/`, `scripts/`, `airflow/dags/`, `Makefile` as `:ro` mounts on spark-master.

### E2. Python 3.8 compatibility — `download_kaggle.py`
**Why:** `str | Path` union syntax requires Python 3.10+. Container has Python 3.8.10.
**What:** Added `from __future__ import annotations` to `pipeline/src/chicago_pipeline/ingest/download_kaggle.py`.

### E3. Python 3.8 compatibility — `test_ingest.py`
**Why:** Parenthesized context managers (`with (a, b):`) require Python 3.10+.
**What:** Rewrote `test_generate_synthetic_reproducible` to use flat `with tmp1, tmp2:`.

### E4. spark-worker volume mounts expanded
**Why:** Worker couldn't read `/data/` CSV (file not found error). Also needed `./dbt:/opt/dbt` for consistency.
**What:** Added `./dbt:/opt/dbt` and `./data:/data` to spark-worker volumes.

### E5. docker-compose.yaml duplicate key cleanup
**Why:** Duplicate `restart: unless-stopped` key in spark-master section caused YAML parse warnings.
**What:** Removed the second `restart:` line.

### E6. Dockerfile Python deps baked in
**Why:** Container rebuild lost all pip-installed packages (structlog, dbt, pytest, etc.). Non-reproducible.
**What:** `docker/spark/Dockerfile` now installs all deps: boto3, pyyaml, structlog, python-dotenv, pandas, pyarrow, psycopg2-binary, sqlalchemy, s3fs, dbt-core (<1.9), dbt-postgres (<1.9), pyspark 3.5.3, pytest, pytest-mock.

---

## Part C — Hotfixes

### H1. Silver COLUMN_ALREADY_EXISTS — root cause fix in Bronze writer ✅ DONE
**Severity:** Low | **Layer:** M1–M2 | **Type:** Code quality
**Applied:** `to_bronze.py` drops `ingest_date` from DataFrame before `partitionBy` write. Column only exists in directory structure, not in data files. `to_silver.py` also supports `--ingest-date` CLI arg for per-partition processing.
**Verified:** Silver rerun with `--ingest-date 2026-06-05` — zero WARN messages. 57,931 rows clean.
**Files changed:** `pipeline/src/chicago_pipeline/bronze/to_bronze.py`, `pipeline/src/chicago_pipeline/silver/to_silver.py`

### H2. Make `dbt deps` a prerequisite for `dbt run` ✅ DONE
**Severity:** Low | **Layer:** M4 | **Type:** Makefile improvement
**Applied:** `dbt-run` now depends on `dbt-deps` in Makefile. `make dbt-run` always works from fresh state.
**Verified:** `make dbt-run` completes 12/12 models + 53/53 tests without manual `dbt deps` step.
**Files changed:** `Makefile`

### H3. Add Windows PowerShell pipeline equivalents ✅ DONE
**Severity:** Low | **Layer:** Cross-cutting | **Type:** Developer experience
**Applied:** `scripts/pipeline.ps1` created with PowerShell functions mirroring all Makefile targets.
**Verified:** Available for Windows users.
**Files created:** `scripts/pipeline.ps1`

### H4. GE Gold validation — multi-table directory support 🔓 OPEN
**Severity:** Medium | **Layer:** M3–M4 | **Type:** Quality gap
**Current state:** `run_validation.py` fails with `Conflicting directory structures detected` when pointed at `s3a://lake/gold/chicago_crime/` because Gold has 5 sub-table directories (fact_crime/, dim_time/, etc.) rather than a flat Parquet directory. GE doesn't understand multi-table layouts. Gold quality is currently verified by dbt 53/53 tests + warehouse constraints (PKs, FKs, indexes).
**Proposed fix:** Extend `run_validation.py` to accept a `--tables` flag and run per-table validation:
```bash
python3 run_validation.py s3a://lake/gold/chicago_crime/fact_crime chicago_crime_gold
python3 run_validation.py s3a://lake/gold/chicago_crime/dim_time chicago_crime_gold
...
```
Or create a separate `run_gold_validation.py` that iterates over the 5 tables.
**Files to change:** `great_expectations/run_validation.py`
**Risk:** Medium — requires new GE suite definitions per table or a generic gold suite.
**Expected outcome:** All 5 Gold tables validated by GE, closing the quality gap.

### H5. Consolidate explore/spike scripts into single directory ✅ DONE
**Severity:** Low | **Layer:** Cross-cutting | **Type:** Cleanup
**Applied:** `pipeline/scripts/` removed. Canonical locations: `scripts/explore/` and `scripts/spike/`. Docker-compose mounts updated. Docstrings corrected to `/opt/scripts/` paths.
**Files changed:** `scripts/` (duplicates removed), `docker-compose.yaml` (mounts), `scripts/explore/*.py` (docstrings)

---

## Summary

| Category | Total | Fixed | Remaining |
|----------|-------|-------|-----------|
| Original bugs (1–3) | 3 | 3 ✅ | 0 |
| Original quirks (4–6) | 3 | 3 ✅ | 0 |
| Original observations (7–14) | 8 | 6 ✅ | 1 🔓 (#10), 1 🔜 M5 (#13) |
| Evaluation fixes (E1–E6) | 6 | 6 ✅ | 0 |
| **Hotfixes (H1–H5)** | **5** | **4 ✅** | **1 🔓 (H4)** |

### Truly remaining open items:
- **H4** — GE Gold multi-table validation (medium effort, quality gap)
- **#10** — GE in Airflow DAGs (M5 territory)
