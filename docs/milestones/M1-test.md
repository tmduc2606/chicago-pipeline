# M1 — User test instructions

> Date: 2026-06-03 | Milestone: M1 Ingestion → Bronze

## Prerequisites

- Docker Desktop installed and running.
- All M0 tests passed (repo skeleton, contracts, agents, Makefile).
- `.env` file populated from `.env.example` with real passwords.

## Test steps

### 1. Verify pipeline directory structure

```bash
find pipeline/src/chicago_pipeline -type f | sort
# On Windows: Get-ChildItem -Recurse -File pipeline/src/chicago_pipeline | Select FullName
```

**Expected:**
```
pipeline/src/chicago_pipeline/__init__.py
pipeline/src/chicago_pipeline/common/__init__.py
pipeline/src/chicago_pipeline/common/db.py
pipeline/src/chicago_pipeline/common/logger.py
pipeline/src/chicago_pipeline/common/s3.py
pipeline/src/chicago_pipeline/common/settings.py
pipeline/src/chicago_pipeline/common/spark_session.py
pipeline/src/chicago_pipeline/ingest/__init__.py
pipeline/src/chicago_pipeline/ingest/download_kaggle.py
pipeline/src/chicago_pipeline/bronze/__init__.py
pipeline/src/chicago_pipeline/bronze/to_bronze.py
```

**Pass if:** All 11 files present.

### 2. Verify airflow directory

```bash
ls airflow/
```

**Expected:** `Dockerfile`, `requirements.txt`, `dags/`, `plugins/`.

**Pass if:** All files and directories exist.

### 3. Verify ingest DAG

```bash
python -c "
import ast
with open('airflow/dags/ingest_dag.py') as f:
    tree = ast.parse(f.read())
tasks = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.endswith('_task')]
print('Tasks:', tasks)
"
```

**Expected:** `Tasks: ['kaggle_download', 'verify_checksum']`

**Pass if:** All 2 TaskFlow tasks found (plus the SparkSubmitOperator `upload_bronze`).

### 4. Unit tests

```bash
PYTHONPATH=pipeline/src pytest pipeline/tests/ -v
# On Windows: $env:PYTHONPATH='pipeline/src'; pytest pipeline/tests/ -v
```

**Expected:** 4 passed (test_generate_synthetic_creates_file, test_generate_synthetic_reproducible, test_verify_csv, test_verify_csv_empty).

**Pass if:** All 4 tests green.

### 5. Lint pipeline code

```bash
pip install ruff
ruff check pipeline/src --select E,F,I,UP
```

**Expected:** `All checks passed!`

**Pass if:** No lint errors.

### 6. Validate contracts (no regression)

```bash
python -c "import yaml, json; yaml.safe_load(open('contracts/openapi.yaml')); json.load(open('contracts/dbt-manifest.json')); json.load(open('contracts/design-tokens.json')); print('All contracts valid.')"
```

**Expected:** `All contracts valid.`

**Pass if:** No errors.

### 7. Verify synthetic data generation (standalone)

```bash
python -c "
import sys; sys.path.insert(0, 'pipeline/src')
from chicago_pipeline.ingest.download_kaggle import generate_synthetic, verify_csv
rows = generate_synthetic('/tmp/test_m1.csv', days=3, seed=42)
count = verify_csv('/tmp/test_m1.csv')
print(f'Generated {rows} rows, verified {count} rows')
assert rows == count, 'Row count mismatch'
assert 1300 < rows < 2500, f'Unexpected count: {rows}'
print('PASS')
"
```

**Expected:** `Generated X rows, verified X rows` then `PASS`.

**Pass if:** Row count between 1,300 and 2,500 for 3 days; row counts match.

**Cleanup:** `rm /tmp/test_m1.csv`

### 8. Verify Bronze config

```bash
python -c "
import sys; sys.path.insert(0, 'pipeline/src')
from chicago_pipeline.common.settings import settings
print('Bronze prefix:', settings.bronze.get('prefix'))
print('Partition by:', settings.bronze.get('partition_by'))
print('Bucket:', settings.storage.get('bucket'))
"
```

**Expected:** `Bronze prefix: bronze/chicago_crime`, `Partition by: ingest_date`, `Bucket: lake`.

**Pass if:** All config values match expected.

## Known limitations (not yet implemented)

- `docker compose up` will fail on the `api` and `web` containers (empty directories — M5/M6 deliverables).
- `make spark-bronze` requires the full stack up (Spark + MinIO) to actually run; this is tested in M7 CI.
- Airflow `SparkSubmitOperator` requires `spark_default` connection to be configured in Airflow.
- `download_kaggle.py` defaults to synthetic fallback (no Kaggle API key configured).

## Interactive Bronze layer tools

Two scripts to explore the Bronze layer data interactively:

### Bronze Explorer (automated report)

```bash
PYTHONPATH=pipeline/src python scripts/explore/bronze_explorer.py
# On Windows: $env:PYTHONPATH='pipeline/src'; python scripts/explore/bronze_explorer.py
```

**What it shows:**
1. Bronze schema and first 5 rows
2. Date range, daily distribution (bar chart)
3. Crime type distribution (top 10)
4. Arrest analysis (rate, domestic %, top districts)
5. Hour-of-day and day-of-week patterns
6. Bronze layer concept explanation

### Bronze Query Tool (interactive REPL)

```bash
PYTHONPATH=pipeline/src python scripts/explore/bronze_query.py
# On Windows: $env:PYTHONPATH='pipeline/src'; python scripts/explore/bronze_query.py
```

**Commands:**
- `head [n]` — show first n rows
- `count [column]` — count by column
- `filter <col> <val>` — filter rows
- `schema` — show column names
- `summary` — basic statistics
- `quit` — exit

**Example session:**
```
bronze> head 5
bronze> count primary_type
bronze> filter arrest 1
bronze> count district
bronze> schema
bronze> quit
```
