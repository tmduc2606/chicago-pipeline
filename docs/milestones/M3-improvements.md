# M3 Improvements — Gold Layer

## Implemented (M3 baseline)
1. **Star schema design** — fact_crime + 4 dim tables with hash-based surrogate keys
2. **dim_time BCNF** — 9 columns: `time_id, date, year, quarter, month, day, weekday_name, is_weekend, hour`
3. **dim_offense BCNF** — 5 columns: `offense_id, iucr, primary_type, description, fbi_code` (unique by IUCR)
4. **dim_location BCNF** — `location_id, location_description, latitude, longitude, is_downtown, distance_to_downtown_km, beat, district, ward, community_area, geom_wkt`
   - `is_downtown` via bbox check
   - `distance_to_downtown_km` via Haversine formula
   - `geom_wkt` as WKT string placeholder for M4 PostGIS cast
5. **dim_case BCNF** — `case_id, case_number, block`
6. **Hash-based surrogate keys** — Deterministic via `F.xxhash64(...)`, idempotent re-runs
7. **Hash collision fixed** — Changed from `IntegerType` (32-bit, 4 collisions) to 64-bit `bigint` (0 collisions)
8. **fact_crime partitioned by `year`** — Scales to multi-year datasets
9. **`_gold_ingest_ts`** — Timestamp added to fact_crime for pipeline observability
10. **12 GE expectations** — PK not-null + unique, FK not-null, row count > 1000 (all PASS)
11. **Gold GE suite validated** — 12/12 PASS including uniqueness (no hash collisions)
12. **Drift detection Gold-safe** — `_detect_district_drift` checks `"district" in df.columns` (SKIPPED for fact_crime)
13. **DAG integration** — `silver_to_gold_dag.py` with 3 tasks: GE Silver → Spark Gold → GE Gold
14. **Schema contract** — `contracts/gold-schema.json` v1.0.0 with FK relationships

## Proposed Improvements (non-blocking, polish pass M8)
1. **`dim_time` joined at hourly grain** — Currently joined at `hour=0` because Silver exposes `date` as DateType, not TimestampType. Could add `date_hour` to Silver (M2 Extension candidate) for true hourly joins.

2. **`dim_location` near 1:1 with fact** — 57,931 rows for 57,931 facts. A more realistic location dimension would share common locations (e.g., "100 N STATE ST"). This requires a different dedup strategy — perhaps grouping by `(latitude, longitude)` rounded to 4 decimal places (~11m precision), keeping first-seen beat/district/ward/community_area per cluster.

3. **`dim_case` near 1:1 with fact** — All case numbers are unique (~57,931). This is expected for crime data (one case = one crime event). Not an issue — dim_case serves as a metadata lookup even at 1:1 cardinality.

4. **Slowly Changing Dimensions (SCD)** — Currently type-0 (no history). If location descriptions change or IUCR descriptions are updated, dim tables would need SCD Type 2 handling. Deferred to M8.

5. **`geom_wkt` placeholder** — Currently stored as WKT string in dim_location. In M4 (Postgres), this should be cast to PostGIS geometry using `ST_GeomFromText`. Consider adding a PostGIS-specific column in the load step.

6. **Sin/cos cyclical encoding** — `month_sin`, `month_cos`, `hour_sin`, `hour_cos` deferred to dbt intermediate models (M4). Would improve ML feature readiness.

7. **GE coverage expansion** — Current 12 expectations cover only fact_crime. Future: add expectations for dim table cardinality (e.g., `expect_column_distinct_values_to_be_in_set` for dim_offense IUCR), null checks on dim key columns, row count ranges per dim table.

8. **dim_time pre-generation** — 26,304 rows (2024-01-01 to 2026-12-31, hourly) is hardcoded. Could be made config-driven via `base.yaml` `gold.date_range`.

9. **Cross-layer drift from Silver to Gold** — Current drift detection covers only district changes at Bronze/Silver. Add Gold-specific drift checks: new IUCR codes, new primary_types, new beat values.

10. **Fact-to-silver row count consistency in Airflow** — The DAG does not assert `fact.count == silver.count`. Add a task-level check with alert on mismatch.

11. **Airflow task logging for Gold** — `silver_to_gold_dag.py` could use `print("counts")` → captured by Airflow task logs. Currently must exec into container to see `to_gold.py` output.
