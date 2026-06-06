# M2 Improvements — Bronze → Silver

## Completed
1. **GE suites as proper JSON** — Converted from YAML format to standard GE JSON format for compatibility.
2. **Silver config in base.yaml** — Added `silver` section with prefix, partition config, dedup columns, Chicago bbox, date range.
3. **Makefile GE targets** — Added `ge-check`, `ge-bronze`, `ge-silver` targets for validation.
4. **M2 Extension EDA** — 100% full dataset inspection (57,931 rows) via `scripts/spike/m2_silver_eda.py`.
5. **Medallion Architecture alignment** — Revised proposal to keep Silver as "just-enough" conforming; deferred sin/cos, `is_downtown`, `distance_to_downtown_km` to Gold.
6. **M2 Extension implementation** — 11 conforming features (trim, boolean flags, date decomposition, hours_to_update). See `M2-extension-proposal.md` §3.
7. **GE Silver suite update** — 18 expectations (12 original + 6 `not_null` on boolean flags).
8. **GE suite versioning** (E7) — Added `version: 2` to both Bronze and Silver suite JSON files.
9. **Silver schema evolution tracking** (E8) — `run_validation.py` now checks for missing/extra columns in Silver output.
10. **Bronze partition pruning** (E4) — `to_silver.py` reads only latest `ingest_date` partition; `dropped=0` (was 57,931).
11. **`hours_to_update` edge case** (E5) — Explicit `.cast("timestamp")` for DateType compatibility.
12. **GE reports to S3A** (E6) — Reports written to `s3a://lake/reports/ge/{suite}/{date}/{ts}_report.json`.
13. **Bronze case_number regex** (E10) — Added `^[A-Z]{2}\d{6}$` expectation to Bronze suite.
14. **District drift detection** (Phase 1–4 of M2-realtime-district-proposal) — Config-driven district set from `base.yaml`, drift detector in `common/drift.py` + `run_validation.py`, Airflow DAG task via `SparkSubmitOperator`, Slack alerting + auto-remediation.

## TODO
1. **GE Spark integration** — Wire GE validation to use SparkDFExecutionEngine for real data validation (currently uses FileDataContext which may not work in all environments).
2. **GE reports dashboard** — Add Grafana dashboard for GE validation results.
3. **Silver idempotency test** — Add test that verifies running silver_transform twice produces same result.
4. **Dedup strategy** — Consider composite key deduplication vs. full row dedup.
5. **Null handling policy** — Document which nulls are acceptable vs. data quality failures.
6. **GE alerting** — Add Slack/email alerts on validation failures.
7. **Gold BCNF `dim_time`** — Build proper dimension table in dbt with `time_key`, `date`, `year`, `month`, `day_of_week`, `hour`, `is_weekend`.
8. **Gold ML features** — Sin/cos cyclical encoding, `is_downtown`, `distance_to_downtown_km` in dbt.

## Noted
- GE validation runs as part of Airflow DAG, not standalone CLI
- Silver transformation is idempotent by design (overwrite mode)
- Dedup columns are configurable via base.yaml
- `date` stays as `DateType` (no timestamp upcast) — avoids schema breakage
- `date_hour` deferred to Gold (requires timestamp source, project-specific granularity)
