# M3 Test Instructions — Gold Layer (Star Schema)

## Prerequisites
- Docker stack running (`docker compose up -d`)
- M1 (Bronze) and M2 (Silver) successfully completed
- M3 Gold transform implemented

## Test Steps

### 1. Copy M3 files to the container
```bash
docker compose cp pipeline\src\chicago_pipeline\gold\__init__.py spark-master:/opt/pipeline/src/chicago_pipeline/gold/__init__.py
docker compose cp pipeline\src\chicago_pipeline\gold\to_gold.py spark-master:/opt/pipeline/src/chicago_pipeline/gold/to_gold.py
docker compose cp pipeline\src\chicago_pipeline\common\settings.py spark-master:/opt/pipeline/src/chicago_pipeline/common/settings.py
docker compose cp pipeline\conf\base.yaml spark-master:/opt/pipeline/conf/base.yaml
docker compose cp pipeline\src\chicago_pipeline\common\drift.py spark-master:/opt/pipeline/src/chicago_pipeline/common/drift.py
docker compose cp great_expectations\run_validation.py spark-master:/opt/great_expectations/run_validation.py
docker compose cp great_expectations\suites\chicago_crime_gold.json spark-master:/opt/great_expectations/suites/chicago_crime_gold.json
```

### 2. Run the Gold Transform
```bash
docker compose exec -T spark-master /opt/spark/bin/spark-submit --master spark://spark-master:7077 --py-files /opt/pipeline/src /opt/pipeline/src/chicago_pipeline/gold/to_gold.py s3a://lake/silver/chicago_crime s3a://lake/gold/chicago_crime
```
**Expected output:** `Gold transform complete: {'silver_input': 57931, 'fact_crime': 57931, 'dim_time': 26304, 'dim_location': 57931, 'dim_offense': 900, 'dim_case': 57931}`

### 3. Verify Gold Tables in MinIO
```bash
docker compose exec -T spark-master python3 -c "
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName('Verify').config('spark.hadoop.fs.s3a.impl', 'org.apache.hadoop.fs.s3a.S3AFileSystem').config('spark.hadoop.fs.s3a.endpoint', 'http://minio:9000').config('spark.hadoop.fs.s3a.access.key', 'minio').config('spark.hadoop.fs.s3a.secret.key', 'change_me_local').config('spark.hadoop.fs.s3a.path.style.access', 'true').config('spark.hadoop.fs.s3a.connection.ssl.enabled', 'false').getOrCreate()
for t in ['fact_crime', 'dim_time', 'dim_location', 'dim_offense', 'dim_case']:
    df = spark.read.parquet('s3a://lake/gold/chicago_crime/' + t)
    print(f'{t}: {df.count()} rows, {len(df.columns)} cols')
spark.stop()
"
```
**Expected output:**
```
fact_crime: 57931 rows, 19 cols
dim_time: 26304 rows, 9 cols
dim_location: 57931 rows, 11 cols
dim_offense: 900 rows, 5 cols
dim_case: 57931 rows, 3 cols
```

### 4. Verify Fact Crime Schema
```bash
docker compose exec -T spark-master /opt/spark/bin/spark-submit --master spark://spark-master:7077 /tmp/check_schema.py
```
**Expected columns:** `crime_id`, `time_id`, `offense_id`, `case_id`, `location_id`, `arrest`, `domestic`, `beat`, `fbi_code`, `is_arrested`, `is_domestic`, `is_domestic_arrest`, `is_unassigned_district`, `is_unassigned_community`, `is_unassigned_ward`, `hours_to_update`, `date_dow`, `_gold_ingest_ts`, `year`

### 5. Run GE Validation on Gold
```bash
docker compose exec -T spark-master /opt/spark/bin/spark-submit --master spark://spark-master:7077 --py-files /opt/pipeline/src /opt/great_expectations/run_validation.py s3a://lake/gold/chicago_crime/fact_crime chicago_crime_gold gold_checkpoint
```
**Expected output:** `VALIDATION PASSED: chicago_crime_gold`

### 6. Verify Fact Crime Uniqueness
```bash
docker compose exec -T spark-master python3 -c "
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.appName('UniqueCheck').config(...).getOrCreate()
df = spark.read.parquet('s3a://lake/gold/chicago_crime/fact_crime')
dupes = df.groupBy('crime_id').count().filter(F.col('count') > 1).count()
print(f'Duplicate crime_ids: {dupes}')
spark.stop()
"
```
**Expected output:** `Duplicate crime_ids: 0`

### 7. Run Full End-to-End Pipeline
```bash
make spark-bronze
make spark-silver
make spark-gold
make ge-check
```
**Expected output:** All 3 GE validations PASS (Bronze, Silver, Gold).

### 8. Verify FK Relationships (Cross-Layer Consistency)
```bash
docker compose exec -T spark-master python3 -c "
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.appName('FKCheck').config(...).getOrCreate()
fact = spark.read.parquet('s3a://lake/gold/chicago_crime/fact_crime')
silver = spark.read.parquet('s3a://lake/silver/chicago_crime')
print(f'Silver: {silver.count()}, Gold fact: {fact.count()}')
spark.stop()
"
```
**Expected output:** `Silver: 57931, Gold fact: 57931` (row counts must match)

## Pass/Fail Criteria
| Step | Check | Pass | Fail |
|------|-------|------|------|
| 2 | Gold transform completes | Counts shown, no errors | Spark exception or mismatch |
| 3 | All 5 tables exist | 5 tables with expected row counts | Missing tables or wrong counts |
| 4 | Schema correct | 19 columns with correct types | Missing/extra columns |
| 5 | GE validation | `VALIDATION PASSED` | `VALIDATION FAILED` |
| 6 | No PK collisions | 0 duplicate crime_ids | ≥1 duplicate |
| 7 | Pipeline green | 3/3 GE PASS | Any FAIL |
| 8 | FK consistency | Silver count == Fact count | Count mismatch |

## Known Limitations
- **dim_time joined at daily grain** (hour=0) since Silver `date` is DateType, not TimestampType
- **dim_location contains 57,931 rows** (almost 1:1 with fact) — most crime locations are unique
- **dim_case contains 57,931 rows** — all case numbers are unique
- **No dim_offense-to-fact cardinality check** (900 IUCR codes → 57,931 events is correct)
