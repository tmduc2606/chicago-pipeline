# Data Engineer — contracts

## Consumes
| Artefact | From | Used for |
|---|---|---|
| `data/*.csv` | Kaggle snapshot | Bronze ingest |
| `contracts/event-catalog.md` | Data Engineer + Backend | OpenLineage event names |
| `docs/data-model.md` | Architect | Source of truth for star schema |
| S3 / MinIO credentials | SRE (env) | Read/write lake |

## Produces
| Artefact | Consumed by | Format |
|---|---|---|
| `s3a://lake/bronze/chicago_crime/...` | Self (Silver) | Parquet + `_ingest_ts` |
| `s3a://lake/silver/chicago_crime/...` | Self (Gold) | Parquet partitioned by year/month, 29 columns |
| `s3a://lake/gold/chicago_crime/...` | `load_postgres.py`, dbt sources | Parquet: `fact_crime` + 4 dims, partitioned by year |
| `contracts/gold-schema.json` | Backend, QA, Architect | JSON — Gold output column contract |
| **M4 — Warehouse layer:** | | |
| `scripts/initdb/01-schema.sql` | Postgres container | SQL — PostGIS extension + `warehouse` schema |
| `pipeline/.../warehouse/load_postgres.py` | Airflow DAG | Python — reads Gold Parquet, writes to Postgres |
| `warehouse.fact_crime` + `warehouse.dim_*` | dbt staging models | PostgreSQL tables (5 tables, PostGIS geometry) |
| `dbt/models/marts/mart_*` | Backend API | PostgreSQL views/tables (5 marts) |
| `airflow/dags/dbt_build_dag.py` | SRE (deploy) | Python — `dbt run` + `dbt test` |
| `contracts/dbt-manifest.json` | Backend, Docs, QA, Architect | JSON |
| OpenLineage events | Marquez → SRE | HTTP POST |
| `airflow/dags/*.py` | SRE (deploy) | Python |

## Handoff: Data Engineer → Backend
Triggered when a new mart is ready.

```markdown
## Handoff
- **From agent:** data-engineer
- **To agent(s):** backend
- **Contract(s) touched:** `contracts/dbt-manifest.json`
- **ADR (if any):** `docs/adr/000X-*.md`
- **Summary:** New mart `mart_xxx` is now available; sample row and SELECT shown below.
- **Breaking?:** no
- **Action required by receiver:** wire a new `/api/xxx` endpoint or extend an existing one.
- **Checklist:**
  - [ ] Tests added/updated
  - [ ] Lint clean
  - [ ] `make pipeline` end-to-end
  - [ ] Docs agent notified
```

## Handoff: Data Engineer → Docs
Triggered when `README.md` or `docs/data-model.md` needs an update (new marts, schema changes, lineage additions).
