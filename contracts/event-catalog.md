# Event catalog

The lineage / observability event names used by the platform. This file is **append-only**; never edit history. Producers are the **Data Engineer** and **Backend** agents; consumers are **SRE** and **Security**.

## Format

```
<namespace>.<entity>.<verb>[.<modifier>]
```

- `namespace` — `pipeline`, `api`, `db`, `storage`
- `entity` — `dag`, `task`, `mart`, `endpoint`, `request`
- `verb` — `start`, `complete`, `fail`, `retry`, `skip`
- `modifier` — optional qualifier

---

## Pipeline events (Data Engineer producer)

| Event | Trigger | Payload (key fields) |
|---|---|---|
| `pipeline.dag.start` | Airflow DAG begins | `dag_id`, `run_id`, `logical_date` |
| `pipeline.dag.complete` | Airflow DAG succeeds | `dag_id`, `run_id`, `duration_s` |
| `pipeline.dag.fail` | Airflow DAG fails | `dag_id`, `run_id`, `failed_task_id`, `error` |
| `pipeline.task.start` | Task begins | `dag_id`, `run_id`, `task_id` |
| `pipeline.task.complete` | Task succeeds | `dag_id`, `run_id`, `task_id`, `duration_s` |
| `pipeline.task.fail` | Task fails | `dag_id`, `run_id`, `task_id`, `error`, `attempt` |
| `pipeline.spark.start` | PySpark job begins | `app_name`, `spark_version` |
| `pipeline.spark.complete` | PySpark job succeeds | `app_name`, `duration_s`, `rows_in`, `rows_out` |
| `pipeline.spark.fail` | PySpark job fails | `app_name`, `error`, `stage` |
| `pipeline.dbt.run` | dbt run completes | `invocation_id`, `models_run`, `models_warned`, `models_errored` |
| `pipeline.dbt.test` | dbt test completes | `invocation_id`, `passed`, `failed`, `warned` |
| `pipeline.ge.checkpoint.complete` | GE checkpoint finishes | `checkpoint_name`, `success_pct`, `failed_expectations[]` |
| `pipeline.mart.refresh` | dbt mart materialised | `mart_name`, `rows`, `duration_s` |

## API events (Backend producer)

| Event | Trigger | Payload (key fields) |
|---|---|---|
| `api.request.start` | Request received | `method`, `path`, `request_id` |
| `api.request.complete` | Response sent | `method`, `path`, `status`, `duration_ms`, `request_id` |
| `api.request.fail` | 5xx response | `method`, `path`, `status`, `error_code`, `request_id` |
| `api.cache.hit` | Redis cache hit | `key_prefix`, `ttl_remaining_s` |
| `api.cache.miss` | Redis cache miss | `key_prefix` |
| `api.db.query.slow` | Query > 500 ms | `query_hash`, `duration_ms`, `row_count` |

## Storage events (Data Engineer / SRE producer)

| Event | Trigger | Payload (key fields) |
|---|---|---|
| `storage.s3.put` | Object written to MinIO | `bucket`, `key`, `bytes`, `layer` (`bronze|silver|gold`) |
| `storage.s3.delete` | Object deleted | `bucket`, `key`, `bytes` |

## DB events (SRE producer)

| Event | Trigger | Payload (key fields) |
|---|---|---|
| `db.connection.ok` | Successful connect | `db`, `latency_ms` |
| `db.connection.fail` | Connect / query fail | `db`, `error` |
| `db.slow_query` | Query > 1 s | `db`, `query_hash`, `duration_ms` |

---

## Versioning

- **v1** (current): the events above.
- New event types: append a new section "## v2" or higher; do not rename or remove existing events.
- Renaming or removing an event = breaking change; requires an ADR.
