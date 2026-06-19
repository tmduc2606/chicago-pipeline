from __future__ import annotations

import io
import sys
from pathlib import Path

_src = Path(__file__).resolve().parents[2]
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

import boto3
import pandas as pd
from sqlalchemy import create_engine, text

from chicago_pipeline.common.logger import get_logger
from chicago_pipeline.common.settings import settings

log = get_logger(__name__)

# dimension tables first so FK constraints resolve
GOLD_TABLES = ["dim_time", "dim_location", "dim_offense", "dim_case", "fact_crime"]

SCHEMA_MAP: dict[str, dict[str, str]] = {
    "fact_crime": {
        "crime_id": "BIGINT", "time_id": "BIGINT", "offense_id": "BIGINT", "case_id": "BIGINT",
        "location_id": "BIGINT", "arrest": "BOOLEAN", "domestic": "BOOLEAN", "beat": "VARCHAR(16)",
        "fbi_code": "VARCHAR(8)", "is_arrested": "BOOLEAN", "is_domestic": "BOOLEAN",
        "is_domestic_arrest": "BOOLEAN", "is_unassigned_district": "BOOLEAN",
        "is_unassigned_community": "BOOLEAN", "is_unassigned_ward": "BOOLEAN",
        "hours_to_update": "INTEGER", "date_dow": "INTEGER", "year": "INTEGER",
        "_gold_ingest_ts": "TIMESTAMP",
    },
    "dim_time": {
        "time_id": "BIGINT", "date": "DATE", "year": "INTEGER", "month": "INTEGER", "day": "INTEGER",
        "hour": "INTEGER", "weekday": "VARCHAR(16)", "is_weekend": "BOOLEAN", "date_dow": "INTEGER",
    },
    "dim_location": {
        "location_id": "BIGINT", "block": "VARCHAR(64)", "location_description": "VARCHAR(128)",
        "district": "INTEGER", "ward": "INTEGER", "community_area": "INTEGER",
        "latitude": "FLOAT", "longitude": "FLOAT", "is_downtown": "BOOLEAN",
        "distance_to_downtown_km": "FLOAT", "geom_wkt": "VARCHAR(256)",
    },
    "dim_offense": {
        "offense_id": "BIGINT", "iucr": "VARCHAR(8)", "primary_type": "VARCHAR(64)",
        "description": "VARCHAR(128)", "fbi_code": "VARCHAR(8)",
    },
    "dim_case": {
        "case_id": "BIGINT", "case_number": "VARCHAR(16)", "updated_on": "VARCHAR(32)",
    },
}


def _infer_partitions(key: str) -> dict[str, str]:
    """Extract partition key=value pairs from an S3 key path.
    E.g. gold/chicago_crime/fact_crime/year=2024/part-000.parquet -> {"year": "2024"}
    Only extracts partition dirs that are parents of the final .parquet file.
    """
    segments = key.split("/")
    result: dict[str, str] = {}
    for i, seg in enumerate(segments):
        if "=" in seg and i < len(segments) - 1 and segments[-1].endswith(".parquet"):
            k, v = seg.split("=", 1)
            result[k] = v
    return result


def _read_gold_parquet(s3_client, bucket: str, prefix: str, table: str,
                       filters: dict[str, str] | None = None) -> pd.DataFrame:
    objects = s3_client.list_objects_v2(Bucket=bucket, Prefix=f"{prefix}/{table}")
    if "Contents" not in objects:
        raise FileNotFoundError(f"No objects found at {bucket}/{prefix}/{table}")

    parquet_files = [o["Key"] for o in objects["Contents"] if o["Key"].endswith(".parquet")]
    if not parquet_files:
        raise FileNotFoundError(f"No parquet files at {bucket}/{prefix}/{table}")

    frames: list[pd.DataFrame] = []
    for key in parquet_files:
        parts = _infer_partitions(key)
        # partition pruning: skip files not matching the requested filters
        if filters and not all(parts.get(k) == v for k, v in filters.items()):
            continue
        obj = s3_client.get_object(Bucket=bucket, Key=key)
        buf = io.BytesIO(obj["Body"].read())
        df = pd.read_parquet(buf)
        # inject partition columns (e.g. year) not stored in the parquet body
        for col, val in parts.items():
            df[col] = pd.to_numeric(val, errors="ignore")
        frames.append(df)

    return pd.concat(frames, ignore_index=True)


FK_DEFS = {
    "fact_crime": [
        "CONSTRAINT fk_time FOREIGN KEY (time_id) REFERENCES warehouse.dim_time(time_id)",
        "CONSTRAINT fk_location FOREIGN KEY (location_id) REFERENCES warehouse.dim_location(location_id)",
        "CONSTRAINT fk_offense FOREIGN KEY (offense_id) REFERENCES warehouse.dim_offense(offense_id)",
        "CONSTRAINT fk_case FOREIGN KEY (case_id) REFERENCES warehouse.dim_case(case_id)",
    ],
}


def _add_foreign_keys(engine, table: str) -> None:
    fks = FK_DEFS.get(table, [])
    with engine.begin() as conn:
        for fk in fks:
            conn.execute(text(f"ALTER TABLE warehouse.{table} ADD {fk}"))


def _add_pk(engine, table: str) -> None:
    pk_map = {"dim_time": "time_id", "dim_location": "location_id",
              "dim_offense": "offense_id", "dim_case": "case_id"}
    pk = pk_map.get(table)
    if pk:
        with engine.begin() as conn:
            # check if PK already exists (to_sql may have created it)
            result = conn.execute(text(
                f"SELECT 1 FROM pg_constraint WHERE conrelid = 'warehouse.{table}'::regclass AND contype = 'p'"
            ))
            if not result.fetchone():
                conn.execute(text(f"ALTER TABLE warehouse.{table} ADD PRIMARY KEY ({pk})"))


def _postgis_add_column(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE warehouse.dim_location ADD COLUMN IF NOT EXISTS geometry GEOMETRY(Point, 4326);"))
        conn.execute(text("""
            UPDATE warehouse.dim_location
            SET geometry = ST_GeomFromText(geom_wkt, 4326)
            WHERE geometry IS NULL AND geom_wkt IS NOT NULL;
        """))


def _add_indexes(engine) -> None:
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_fact_time_id ON warehouse.fact_crime(time_id)",
        "CREATE INDEX IF NOT EXISTS idx_fact_location_id ON warehouse.fact_crime(location_id)",
        "CREATE INDEX IF NOT EXISTS idx_fact_offense_id ON warehouse.fact_crime(offense_id)",
        "CREATE INDEX IF NOT EXISTS idx_fact_case_id ON warehouse.fact_crime(case_id)",
        "CREATE INDEX IF NOT EXISTS idx_dim_location_geometry ON warehouse.dim_location USING GIST(geometry)",
    ]
    with engine.begin() as conn:
        for idx in indexes:
            conn.execute(text(idx))


def load_gold_to_postgres(engine, s3_client, bucket: str, prefix: str) -> dict[str, int]:
    results: dict[str, int] = {}

    # Phase 0: drop existing tables (reverse FK order)
    with engine.begin() as conn:
        for table in reversed(GOLD_TABLES):
            conn.execute(text(f"DROP TABLE IF EXISTS warehouse.{table} CASCADE"))
    log.info("warehouse_tables_dropped")

    # Phase 1: load all tables via to_sql (sequential — parallel DDL causes race conditions)
    for table in GOLD_TABLES:
        df = _read_gold_parquet(s3_client, bucket, prefix, table)
        df.to_sql(table, engine, schema="warehouse", if_exists="append", index=False, method="multi")
        results[f"postgres_{table}"] = len(df)
        log.info("warehouse_load_complete", table=table, row_count=len(df))

    # Phase 2: add PKs to dimension tables (check to avoid duplicates from to_sql)
    for table in GOLD_TABLES:
        if table != "fact_crime":
            _add_pk(engine, table)
            log.info("warehouse_pk_added", table=table)

    # Phase 2b: deduplicate fact_crime by crime_id, then add UNIQUE constraint
    with engine.begin() as conn:
        dup_check = conn.execute(text(
            "SELECT crime_id, COUNT(*) AS n FROM warehouse.fact_crime GROUP BY crime_id HAVING COUNT(*) > 1 LIMIT 1"
        ))
        if dup_check.fetchone():
            log.warning("warehouse_fact_duplicates_found", msg="deduplicating fact_crime by crime_id")
            conn.execute(text("""
                DELETE FROM warehouse.fact_crime
                WHERE ctid NOT IN (
                    SELECT MIN(ctid) FROM warehouse.fact_crime GROUP BY crime_id
                )
            """))
        result = conn.execute(text(
            "SELECT 1 FROM pg_constraint WHERE conrelid = 'warehouse.fact_crime'::regclass "
            "AND contype = 'u' AND conname = 'uq_fact_crime_crime_id'"
        ))
        if not result.fetchone():
            conn.execute(text(
                "ALTER TABLE warehouse.fact_crime ADD CONSTRAINT uq_fact_crime_crime_id UNIQUE (crime_id)"
            ))
    log.info("warehouse_fact_unique_added")

    # Phase 3: add FK constraints to fact table (dimensions now have PKs)
    _add_foreign_keys(engine, "fact_crime")
    log.info("warehouse_fact_fks_added")

    # Phase 4: add PostGIS geometry (must precede GiST index)
    log.info("warehouse_postgis_cast")
    _postgis_add_column(engine)

    # Phase 5: add indexes for query performance
    _add_indexes(engine)
    log.info("warehouse_indexes_added")

    with engine.connect() as conn:
        result = conn.execute(text("SELECT ST_SRID(geometry) AS srid FROM warehouse.dim_location WHERE geometry IS NOT NULL LIMIT 1"))
        row = result.fetchone()
        srid = row[0] if row else 0
        results["postgis_srid"] = srid

    log.info("warehouse_postgis_srid", srid=srid)
    return results


if __name__ == "__main__":
    cfg = settings.gold
    db = settings.database
    bucket = settings.storage.get("bucket", "lake")
    prefix = cfg.get("prefix", "gold/chicago_crime")

    endpoint = settings.storage.get("endpoint", "http://minio:9000")

    engine_url = f"postgresql://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['name']}"
    engine = create_engine(engine_url)

    s3_client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=settings.storage.get("access_key", "minio"),
        aws_secret_access_key=settings.storage.get("secret_key", "change_me_local"),
        use_ssl=False,
        verify=False,
    )

    counts = load_gold_to_postgres(engine, s3_client, bucket, prefix)
    print(f"Warehouse load complete: {counts}")
