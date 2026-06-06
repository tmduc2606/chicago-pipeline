# M1 — Improvements

> Date: 2026-06-03 | Milestone: M1 Ingestion → Bronze

| # | Category | Description | Status | Milestone targeted |
|---|----------|-------------|--------|-------------------|
| 1 | Config | Make `conf/local.yaml` override env-vars via dotenv for local development | TODO | M2 |
| 2 | Testing | Add integration test that runs `download_kaggle.py` as a subprocess (smoke test) | TODO | M2 |
| 3 | Testing | Add Spark-in-local-mode unit test for `bronze_writer()` using `pyspark-test` | TODO | M2 |
| 4 | Pipeline | Add file-size check to `verify_checksum` in `ingest_dag.py` | TODO | M2 |
| 5 | Airflow | Add `spark_default` connection setup to Airflow init script or Docker entrypoint | TODO | M2 |
| 6 | Schema | Add `_ingest_ts` TimestampType to BRONZE_SCHEMA so it's typed on read | Noted | — |
| 7 | Config | Add env-based default for `spark.hadoop.fs.s3a.endpoint` in `to_bronze.py` | TODO | M2 |

## Notes

- All pipeline code runs inside Docker containers (target); local tests test the synthetic generator and config loader only.
- The `kagglehub` download path is a stub for M1; actual Kaggle integration requires a Kaggle API key in the Airflow environment.
- The Spark environment inside Docker (Bitnami Spark 3.5) already bundles the Hadoop AWS JAR — no extra Docker layer needed.
