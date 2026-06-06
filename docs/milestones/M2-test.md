# M2 User Test — Bronze → Silver (Spark + GE)

## Prerequisites
- Docker Compose stack running with M2-relevant services:
  ```bash
  docker compose up -d minio postgres redis spark-master spark-worker
  ```
- Synthetic CSV at `/tmp/chicago_synthetic.csv` on both containers
- Credentials: `MINIO_ROOT_USER=minio`, `MINIO_ROOT_PASSWORD=change_me_local`
- **Windows note:** use `mingw32-make` instead of `make`

## Test Steps

### Step 1: Verify Silver module loads
```bash
PYTHONPATH=pipeline/src python -c "from chicago_pipeline.silver.to_silver import silver_transform, SILVER_COLUMNS; print('Silver module OK'); print(f'Columns: {list(SILVER_COLUMNS.keys())}')"
```
**Expected:** Prints "Silver module OK" and lists 29 column names (18 original + 11 new conforming features).

### Step 1.5 — Run M2 Extension EDA (100% full dataset)

```bash
# Copy the EDA script to the spark container
docker compose exec -T spark-master mkdir -p /tmp/spike
docker compose cp scripts/spike/m2_silver_eda.py spark-master:/tmp/spike/m2_silver_eda.py

# Run on the synthetic CSV (100% proportion)
docker compose exec -T spark-master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  /tmp/spike/m2_silver_eda.py /tmp/chicago_synthetic.csv 1.0 42
```

**Expected output:** 57,931-row full dataset, zero nulls, zero duplicates, cardinality as in M2-extension-proposal.md §0.

### Step 2: Verify Silver config
```bash
PYTHONPATH=pipeline/src python -c "from chicago_pipeline.common.settings import settings; print(settings.silver)"
```
**Expected:** Prints silver config with `prefix`, `chicago_bbox`, `date_range`.

### Step 3: Run Silver transformation
```bash
mingw32-make spark-silver
```
**Expected:** Spark job completes, logs show `silver_write_complete` with ~57,931 rows to `s3a://lake/silver/chicago_crime/year=2024/month={1,2,3}/`.

### Step 4: Verify Silver output in MinIO
```bash
# Access MinIO console at http://localhost:9001
# Login: minio / change_me_local
# Navigate to lake → silver → chicago_crime
# Should see Parquet files partitioned by year=YYYY/month=MM
```
**Expected:** Parquet files exist in Silver bucket (~2.4 MB total across 6 files).

### Step 5: Run GE Bronze validation
```bash
mingw32-make ge-bronze
```
**Expected:** `VALIDATION PASSED: chicago_crime_bronze` — 8 expectations pass (no nulls on id/date/primary_type, regex date match, lat/lng in bounds, row count ≥ 1000, case_number regex).

### Step 6: Run GE Silver validation
```bash
mingw32-make ge-silver
```
**Expected:** `VALIDATION PASSED: chicago_crime_silver` — 18 expectations pass (12 original + 6 new `not_null` on boolean flags).

### Step 7: Run Bronze → Silver pipeline
```bash
mingw32-make spark-bronze   # CSV → Bronze Parquet on S3A
mingw32-make spark-silver   # Bronze Parquet → Silver Parquet on S3A
```
**Expected:** Both steps complete end-to-end. `spark-gold` / `dbt-run` / `dbt-test` / `quality` targets are not yet available (M3+).

### Step 8: Run unit tests
```bash
$env:PYTHONPATH = "pipeline/src"; python -m pytest pipeline/tests/ -v
```
**Expected:** All 14 tests pass (4 ingest + 10 silver).

## Pass/Fail Criteria
- [ ] All 9 steps complete without errors
- [ ] Silver Parquet files exist in MinIO (year/month partitions)
- [ ] GE Bronze validation: 8/8 expectations PASS
- [ ] GE Silver validation: 18/18 expectations PASS (12 original + 6 new)
- [ ] 16/16 unit tests pass (4 ingest + 12 silver)

## Known Issues & Fixes

| Issue | Fix |
|-------|-----|
| `minio` not `minio123` | `.env` uses `MINIO_ROOT_PASSWORD=change_me_local` |
| `make` not found on Windows | Use `mingw32-make` instead |
| Source CSV path | Bronze reads from `/tmp/chicago_synthetic.csv` (not `/tmp/chicago_crime/source.csv`) |
| GE 1.1.0 API incompatibility | `run_validation.py` uses standalone PySpark, not GE's broken fluent API |
| Date regex for synthetic data | Bronze expectation accepts both `MM/dd/yyyy hh:mm:ss AM/PM` and ISO `yyyy-MM-dd'T'HH:mm:ss` |
| Spark container env vars | `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` must be set in docker-compose.yaml spark services |
| Hadoop JAR versioning | Use `hadoop-aws-3.3.4.jar` (matches Spark 3.5.1's bundled Hadoop), not 3.3.6 |
| `great_expectations/reports/` | Generated at runtime; in `.gitignore` |

## Cleanup (after testing)
```bash
# Remove caches
Get-ChildItem -Recurse -Directory -Filter "__pycache__" -Path "." | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Directory -Filter ".pytest_cache" -Path "." | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Directory -Filter ".ruff_cache" -Path "." | Remove-Item -Recurse -Force
Remove-Item -Recurse -Force "great_expectations/reports" -ErrorAction SilentlyContinue

# Prune Docker dangling images
docker image prune -f
```
