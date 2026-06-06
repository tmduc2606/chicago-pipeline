# ADR 0002 — Spark for Silver, dbt for Gold / marts

- **Status:** Accepted (2026-06-03)
- **Author:** Architect agent
- **Reviewers:** Data Engineer, Backend

## Context

The original design uses a single transformation engine (Spark) for everything from raw ingest to "Gold". It does not use dbt. This causes two problems for a portfolio piece:

1. **Business logic ends up in Python / Scala**, hidden inside Spark jobs, without tests, with no lineage, with no documentation. Reviewers cannot `git diff` the SQL that powers the dashboard.
2. **The dimensional model + marts get baked into Spark**, which means dbt's best-in-class test ecosystem (`not_null`, `unique`, `relationships`, `accepted_values`, singular tests, source freshness) is unused.

## Decision

We split the transformation layer by **engine fit**:

- **Spark (PySpark)** owns the **Silver** layer. Heavy data wrangling (deduplication, type coercion, partitioning 5M+ rows) is what Spark is for. One job, one checkpoint.
- **dbt (dbt-core + dbt-postgres)** owns the **Gold** layer and the **marts** — i.e. the dimensional model (`fact_crime`, `dim_*`) and the analytics marts (`mart_kpi_daily`, `mart_arrest_by_district`, etc.). dbt gives us SQL-first transformations, `schema.yml` tests, lineage, and docs.
- **Great Expectations** owns the **boundary checks** between Bronze→Silver and Silver→Gold. dbt tests own the **in-warehouse** tests.

The data flow becomes:

```
Bronze (MinIO) → [GE checkpoint] → Silver (MinIO, Spark)
                                          │
                                          ▼
                                   Gold (MinIO, Spark)
                                          │
                                          ▼
                            [spark-load-staging] → warehouse.* tables
                                          │
                                          ▼
                       [dbt run] → dbt marts (`mart_*`)
                                          │
                                          ▼
                                   FastAPI (reads marts only)
```

## Consequences

**Positive**
- dbt `schema.yml` is the **single source of truth** for column types, tests, and descriptions of the warehouse.
- `dbt docs generate` produces navigable documentation for the entire warehouse.
- Reviewers can `git log -p` the SQL that drives the dashboard.
- dbt's source freshness tests gate the warehouse behind a clean contract.

**Negative**
- Two engines means two sets of dependencies (PySpark in `pipeline/`, dbt in `dbt/`).
- The "load Gold into warehouse" step is a hand-written Spark job; we could use dbt's `seed` + `source` for it, but a staging table from Parquet is clearer for portfolio purposes.
- One more skill required: SQL + dbt for everyone touching marts.

## Alternatives considered

1. **Spark-only** — single engine, but no dbt tests / docs / lineage. Rejected.
2. **dbt-only** (with `dbt-duckdb`) — cleanest, but loses the "Spark at scale" narrative. Rejected.
3. **Spark + dbt + Soda** — adds Soda Core for additional DQ rules. Nice-to-have, deferred to M7.

## Operational notes

- dbt runs from inside the `airflow-webserver` container (`cd /opt/dbt && dbt run --profiles-dir .`).
- `contracts/dbt-manifest.json` is regenerated on every `dbt run` and committed in the same PR.
- `dbt_project.yml` sets `materializations: { marts: { +materialized: table } }` for marts.
