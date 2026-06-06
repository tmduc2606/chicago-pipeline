# ADR 0001 — MinIO over SeaweedFS for the data lake

- **Status:** Accepted (2026-06-03)
- **Author:** Architect agent
- **Reviewers:** Data Engineer, SRE

## Context

The original design in `reports/End-to-end Chicago DBMS.docx` calls for **SeaweedFS** as the S3-compatible object store for the Bronze / Silver / Gold data lake. SeaweedFS is a legitimate choice — it is fast and lightweight — but it is significantly less common in the data-engineering ecosystem than MinIO.

For a portfolio piece reviewed by senior data engineers, the choice of object store signals "how production-shaped is this?". MinIO is the de-facto S3-compatible store used in:
- dbt-Labs' reference pipelines
- The reference project at `references/data-engineering/End-to-End-Data-Pipeline-master`
- Most modern lakehouse architectures (Databricks, Snowflake, AWS, GCP)

## Decision

We will use **MinIO** (`minio/minio:RELEASE.2024-09-13T20-26-02Z`) as the S3-compatible data lake.

## Consequences

**Positive**
- Reviewer familiarity. MinIO is mentioned in the majority of "data lakehouse" reference architectures.
- Better tooling: `mc` (MinIO Client) is well-documented; S3A works out of the box.
- Better Healthcheck and Prometheus metrics endpoints.
- Console UI is more polished (`localhost:9001`).

**Negative**
- Slightly heavier image than SeaweedFS (~250 MB vs ~50 MB).
- A few less common tuning knobs in older documentation, but the modern MinIO docs are excellent.

## Alternatives considered

1. **SeaweedFS** — kept the design closer to the original docx, but lost portfolio signal. Rejected.
2. **AWS S3 / GCS / Azure Blob** — would have introduced cloud credentials and a billing footprint. Out of scope for a self-contained local demo. Rejected.
3. **Local filesystem** — defeats the purpose of demonstrating a "lake" pattern. Rejected.

## Operational notes

- Buckets: `lake/bronze`, `lake/silver`, `lake/gold` (created by `minio-init` service).
- Spark reads/writes use `s3a://lake/...` with `fs.s3a.endpoint=http://minio:9000`, `fs.s3a.path.style.access=true`.
- Credentials live in `.env` (`MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`); only `.env.example` is committed.
