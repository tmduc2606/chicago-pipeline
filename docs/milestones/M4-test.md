# M4 Test Instructions — Gold → Postgres → dbt (Warehouse)

## Prerequisites
- Docker Compose stack is running: `minio`, `postgres`, `spark-master`, `spark-worker`
- Gold Parquet data exists in MinIO at `s3a://lake/gold/chicago_crime/{fact_crime,dim_time,dim_location,dim_offense,dim_case}/`
- `dbt-postgres==1.8.2`, `pandas`, `pyarrow`, `s3fs`, `psycopg2-binary` installed on `spark-master`
- dbt project at `/opt/dbt/`
- Warehouse loader at `/opt/pipeline/src/chicago_pipeline/warehouse/load_postgres.py`

## Step 1 — Run warehouse loader
```bash
docker compose exec spark-master bash -c "cd /opt/pipeline && PYTHONPATH=/opt/pipeline/src ENV=local python3 src/chicago_pipeline/warehouse/load_postgres.py"
```
**Expected:** All 5 tables loaded — dim_time (26,304), dim_location (57,931), dim_offense (900), dim_case (57,931), fact_crime (57,931), PostGIS SRID=4326.

## Step 2 — Run dbt models
```bash
docker compose exec spark-master bash -c "cd /opt/dbt && dbt run --profiles-dir ."
```
**Expected:** 12/12 models created (5 staging views, 2 intermediate views, 5 mart tables). Mart row counts: mart_kpi_daily (7), mart_arrest_summary (1,250), mart_crime_type_trend (900), mart_geo_choropleth (57,931), mart_temporal_heatmap (26,304).

## Step 3 — Run dbt tests
```bash
docker compose exec spark-master bash -c "cd /opt/dbt && dbt test --profiles-dir ."
```
**Expected:** 26/26 tests PASS (not_null + unique for all models).

## Step 4 — Verify PostGIS geometry
```bash
docker compose exec postgres psql -U chicago -d chicago -c "SELECT ST_SRID(geometry) AS srid, COUNT(*) FROM warehouse.dim_location WHERE geometry IS NOT NULL GROUP BY ST_SRID(geometry);"
```
**Expected:** SRID=4326, count=57,931.

## Step 5 — Verify dim_location quality
```bash
docker compose exec postgres psql -U chicago -d chicago -c "SELECT COUNT(*) AS total, COUNT(*) FILTER (WHERE is_downtown) AS downtown, MIN(distance_to_downtown_km) AS min_dist, MAX(distance_to_downtown_km) AS max_dist FROM warehouse.dim_location;"
```
**Expected:** total=57,931, downtown≥1, min_dist ≥ 0, max_dist > 0.

## Step 6 — Verify sin/cos encoding
```bash
docker compose exec postgres psql -U chicago -d chicago -c "SELECT month_sin, month_cos, hour_sin, hour_cos FROM warehouse_warehouse.int_time_enriched LIMIT 3;"
```
**Expected:** 3 rows with float values between -1 and 1. month_sin² + month_cos² ≈ 1 for every row.

## Step 7 — Verify mart data quality
```bash
docker compose exec postgres psql -U chicago -d chicago -c "
SELECT 'mart_kpi_daily' AS t, COUNT(*) FROM warehouse_warehouse.mart_kpi_daily
UNION ALL SELECT 'mart_arrest_summary', COUNT(*) FROM warehouse_warehouse.mart_arrest_summary
UNION ALL SELECT 'mart_crime_type_trend', COUNT(*) FROM warehouse_warehouse.mart_crime_type_trend
UNION ALL SELECT 'mart_geo_choropleth', COUNT(*) FROM warehouse_warehouse.mart_geo_choropleth
UNION ALL SELECT 'mart_temporal_heatmap', COUNT(*) FROM warehouse_warehouse.mart_temporal_heatmap;"
```
**Expected:** Row counts match Step 2.

## Step 8 — Run full verification script
```bash
docker compose exec spark-master bash -c "POSTGRES_HOST=postgres PYTHONPATH=/opt/pipeline/src python3 /opt/scripts/verify_m4_warehouse.py"
```
**Expected:** 46/46 PASS.

## Known Limitations
- All generated data is year 2024 only (synthetic_start=2024-01-01, 90 days)
- dbt schema is `warehouse_warehouse` instead of `warehouse` (dbt appends project name)
- `_gold_ingest_ts` uses the load timestamp, not the original Gold timestamp
- FK constraints in warehouse tables are dropped by pandas `to_sql` — referential integrity is enforced at the app level
