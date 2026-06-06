# M4 Improvements

## Proposed enhancements for the Warehouse layer

### 1. Add FK constraints to warehouse tables
`pandas.to_sql(if_exists="replace")` drops FK/PK constraints. Need to restore them after data load via ALTER TABLE ADD CONSTRAINT. Alternatively, use `if_exists="append"` with explicit TRUNCATE before load.

### 2. Fix schema naming collision
dbt creates models under `warehouse_warehouse` schema (project_name + custom_schema). Change `dbt_project.yml` to use empty string or override in `profiles.yml` to just `warehouse`.

### 3. Add incremental dbt runs
Mart models use `table` materialization (full refresh each run). For production, switch to `incremental` with `unique_key` and `is_incremental()` macro for performance.

### 4. Partial partition-parquet loading
The warehouse loader reads ALL Parquet files for a table. Add support for partition pruning (e.g., loading only a specific year range) for partial refresh.

### 5. Parallel table loading
Current loader loads table-by-table sequentially. Use `ThreadPoolExecutor` or `asyncio` for concurrent reads/writes across tables.

### 6. Add `dbt docs generate` to the pipeline
dbt docs serve provides column-level lineage documentation. Add to the Makefile pipeline and mount the `target/` directory to be served by NGINX.

### 7. Add GE validation on warehouse tables
Great Expectations currently validates Bronze/Silver/Gold Parquet. Add a Postgres-backed GE suite for warehouse tables to catch data drift in Postgres.

### 8. Add composite indexes on fact_crime FK columns
`fact_crime(time_id)`, `fact_crime(location_id)`, etc. These are foreign keys to dimension tables and would benefit from B-tree indexes for join performance.

### 9. Add mart-level uniqueness tests
Currently dbt tests only check staging models (source tables). Add unique tests on mart models (e.g., `mart_kpi_daily(date_dow)` should be unique).

### 10. Support `_gold_ingest_ts` preservation
The current loader sets `_gold_ingest_ts` at load time rather than preserving the value from the Gold Parquet. Use the Gold-level timestamp for audit trails.

### 11. Add mart `mart_top_crimes_by_location`
A new mart model showing top-10 primary_types per district with geospatial context (center lat/lon, radius). Useful for the MapLibre choropleth layer (M6).
