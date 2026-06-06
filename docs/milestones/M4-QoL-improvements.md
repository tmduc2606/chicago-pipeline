# M4 QoL Improvements — Full Pipeline Rerun Catalogue

**Date:** 2026-06-04
**Scope:** End-to-end pipeline rerun M1 → M4 with bug/quirk catalogue
**Pipeline results:** Silver 57,931 rows | Gold 5 tables | Postgres 10 tables | dbt 12/12 models, 53/53 tests | GE Bronze/Silver/Gold PASSED | Unit tests 63/63

---

## Bugs (must-fix before M5)

### 1. Bronze CSV path mismatch — pipeline cannot bootstrap from fresh state
**Severity:** Critical | **Layer:** M1 (Bronze)
**Symptom:** `make spark-bronze` fails with `AnalysisException: [PATH_NOT_FOUND] Path does not exist: file:/tmp/chicago_synthetic.csv`
**Root cause:** Makefile passes `/tmp/chicago_synthetic.csv` to `to_bronze.py`, but `scripts/seed.sh` writes to `data/chicago_crime_synthetic_90d.csv` on the host. Neither path exists inside the spark-master container.
**Fix options:**
- A) Change Makefile to pass `data/chicago_crime_synthetic_90d.csv` and mount `./data:/data` in docker-compose
- B) Have `seed.sh` generate directly into the container via `docker compose exec`
- C) Add a `make seed` target that generates + copies CSV into the container
**Impact:** Blocks fresh pipeline runs. Existing Bronze data masks the bug.

### 2. Hadoop AWS JARs missing from Spark image — S3A broken out-of-box
**Severity:** Critical | **Layer:** M1–M3 (all Spark steps)
**Symptom:** `java.lang.ClassNotFoundException: Class org.apache.hadoop.fs.s3a.S3AFileSystem not found`
**Root cause:** `apache/spark:3.5.1` ships `hadoop-client-api-3.3.4.jar` and `hadoop-client-runtime-3.3.4.jar` but NOT `hadoop-aws-3.3.4.jar` or `aws-java-sdk-bundle-1.12.262.jar`. S3A filesystem class is unavailable.
**Workaround applied:** `curl` downloaded JARs into the running container's `/opt/spark/jars/`. Works until container is removed/rebuilt.
**Fix:** Add to Dockerfile or a custom Spark image:
```dockerfile
RUN curl -sL https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar \
      -o /opt/spark/jars/hadoop-aws-3.3.4.jar && \
    curl -sL https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar \
      -o /opt/spark/jars/aws-java-sdk-bundle-1.12.262.jar
```
**Impact:** `docker compose up --build` or `docker compose down -v` loses JARs. Pipeline is non-reproducible without this fix.

### 3. `docker-compose.yaml` missing volume mount for `./data`
**Severity:** Medium | **Layer:** M1 (Bronze)
**Symptom:** Even after fixing the CSV path in the Makefile, the spark-master container cannot access `data/` on the host.
**Fix:** Add `./data:/data` volume mount to spark-master in `docker-compose.yaml`.
**Impact:** Blocks Option A for Bug #1.

---

## Quirks (should-fix, non-blocking)

### 4. Silver `[COLUMN_ALREADY_EXISTS] ingest_date` warning
**Severity:** Low | **Layer:** M2 (Silver)
**Symptom:** `WARN DataSource: [COLUMN_ALREADY_EXISTS] The column 'ingest_date' already exists.`
**Root cause:** `to_silver.py` drops the `ingest_date` partition column after filtering, then tries to re-add it. The column persists through the filter step.
**Fix:** Remove the redundant `withColumn(ingest_date_col, ...)` in `to_silver.py` after partition pruning. Or skip the drop entirely since Silver doesn't need it.
**Impact:** Cosmetic only. No data corruption.

### 5. Duplicate scripts in `pipeline/scripts/` vs `scripts/`
**Severity:** Low | **Layer:** Cross-cutting
**Symptom:** `pipeline/scripts/explore/gold_explorer.py`, `gold_query.py`, `verify_m3_gold.py` are byte-identical copies of `scripts/explore/` and `scripts/spike/` counterparts.
**Root cause:** Scripts were copied into `pipeline/` for container access but the originals under `scripts/` remain.
**Fix:** Either:
- A) Add `pipeline/scripts/` to `.gitignore` (they're local-only duplicates)
- B) Remove the duplicates and rely on `scripts/` (already mounted as a volume? — check docker-compose)
**Impact:** Confusing for contributors. No runtime impact.

### 6. `dbt/.user.yml` was not gitignored
**Severity:** Low | **Layer:** M4 (dbt)
**Symptom:** `dbt/.user.yml` (dbt auto-generated UUID) appeared in `git status` as untracked.
**Root cause:** `.gitignore` had `dbt/user.yml` but not `dbt/.user.yml` (dot-prefix difference).
**Fix:** Already fixed in this session — `.gitignore` updated to `dbt/.user.yml`.
**Impact:** Would have committed a local-only config file.

---

## Observations (design-level, deferred)

### 7. `pipeline/scripts/` directory structure vs root `scripts/`
**Observation:** The project has two script directories: `scripts/` (root-level, contains initdb, explore, spike) and `pipeline/scripts/` (inside pipeline package, contains M3 test scripts). The naming convention is inconsistent.
**Suggestion:** Consolidate into a single `scripts/` directory. If container access is needed, use volume mounts.

### 8. Silver partition pruning only filters on latest `ingest_date`
**Observation:** `to_silver.py` uses `_infer_partitions` to find the latest `ingest_date` and only processes that partition. This means historical Bronze partitions are ignored unless manually specified.
**Suggestion:** Add a CLI argument or config option to process all partitions or a specific date range.

### 9. Gold `_gold_ingest_ts` set at load time, not Gold write time
**Observation:** `load_postgres.py` sets `_gold_ingest_ts` to the current timestamp at Postgres load time, but the Gold Parquet already has this column from `to_gold.py`. The loader overwrites it.
**Suggestion:** Preserve the Gold Parquet timestamp if the column exists (already implemented as a defensive comment, but could be enforced).

### 10. GE validation runs as standalone PySpark, not integrated with Airflow
**Observation:** GE validation (`run_validation.py`) runs as a separate `spark-submit` invocation, not as an Airflow task. The `bronze_to_silver_dag.py` and `silver_to_gold_dag.py` DAGs don't include GE steps.
**Suggestion:** Add GE validation as Airflow tasks within the existing DAGs for production orchestration.

### 11. dbt profiles require explicit env vars — no defaults
**Observation:** `dbt/profiles.yml` uses `env_var()` without fallback defaults. If `POSTGRES_HOST` etc. are not set, dbt fails immediately.
**Suggestion:** This is intentional (fail-fast on missing config). Document the required env vars in README and `.env.example`.

### 12. No `dbt deps` in the pipeline
**Observation:** `dbt deps` (install packages) is a separate Makefile target but not called automatically before `dbt run`. If `dbt_packages/` is missing, `dbt run` fails.
**Suggestion:** Add `dbt deps` as a prerequisite to `dbt-run` in the Makefile.

### 13. Airflow containers not running — M5/M6 Dockerfiles missing
**Observation:** `docker compose up` fails on `api` and `web` services because their Dockerfiles don't exist yet. The M0-M4 services work standalone.
**Suggestion:** This is expected — M5 (FastAPI) and M6 (React) will add the Dockerfiles. Document the workaround: start only M0-M4 services.

### 14. `make` not available on Windows
**Observation:** The Makefile requires GNU Make, which isn't installed on Windows. All pipeline commands must be run manually via `docker compose exec`.
**Suggestion:** Either:
- A) Install `make` via `choco install make`
- B) Add PowerShell equivalents to a `scripts/pipeline.ps1`
- C) Accept the limitation and document it

---

## Summary Table

| # | Type | Severity | Layer | Status |
|---|------|----------|-------|--------|
| 1 | Bug | Critical | M1 | Must-fix |
| 2 | Bug | Critical | M1–M3 | Must-fix |
| 3 | Bug | Medium | M1 | Must-fix |
| 4 | Quirk | Low | M2 | Should-fix |
| 5 | Quirk | Low | Cross | Should-fix |
| 6 | Quirk | Low | M4 | Fixed ✓ |
| 7 | Observation | — | Cross | Deferred |
| 8 | Observation | — | M2 | Deferred |
| 9 | Observation | — | M4 | Deferred |
| 10 | Observation | — | Cross | Deferred |
| 11 | Observation | — | M4 | Deferred |
| 12 | Observation | — | M4 | Deferred |
| 13 | Observation | — | M5/M6 | Expected |
| 14 | Observation | — | Cross | Deferred |
