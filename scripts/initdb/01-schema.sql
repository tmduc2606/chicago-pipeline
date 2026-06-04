CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

CREATE SCHEMA IF NOT EXISTS warehouse;

COMMENT ON EXTENSION postgis IS 'PostGIS geometry support for Chicago crime locations';
COMMENT ON SCHEMA warehouse IS 'Gold warehouse schema — loaded from MinIO Parquet, consumed by dbt';
