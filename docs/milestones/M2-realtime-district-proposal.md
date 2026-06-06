# M2 Extension — Real-Time Feature Updates for District Features

> Status: **IMPLEMENTED** — 2026-06-04
> Context: M2 Extension Enhancement, district set validation revealed 3 unexpected values (13, 21, 23)
>
> All 4 phases implemented as part of pre-M3 preparation.

---

## Problem Statement

The current pipeline uses a **static Kaggle CSV snapshot** (2024–2026). District features are hardcoded:

| Layer | District handling | Risk |
|---|---|---|
| Bronze | Ingested as-is from CSV | No validation |
| Silver | Cast to `IntegerType()`, filtered by bbox | No set membership check |
| GE suite | `be_in_set: [1-25]` hardcoded | Fails if source adds new districts |

**If the Chicago PD renumbers districts, merges precincts, or the Kaggle dataset updates with new values, the pipeline breaks silently.**

---

## Current Architecture

```
Kaggle CSV (static) → Bronze (partition by ingest_date) → Silver (cast + filter + dedup)
                                                                ↓
                                                          GE validation (hardcoded set)
```

**No real-time fetching. No schema drift detection. No dynamic set validation.**

---

## Proposed Solutions

### Solution 1: Scheduled Polling + Schema Drift Detection

**Mechanism:** Airflow DAG polls Kaggle API daily, detects new columns/values, alerts on drift.

```
Kaggle API → ingest_dag (daily) → Bronze (new partition) → Silver (cast + validate)
                                        ↓
                                  Schema drift detector
                                        ↓
                              Alert if new district values detected
```

| Component | Implementation |
|---|---|
| **Polling** | Airflow DAG with `KaggleDatasetOperator` or `SimpleHttpOperator` → Kaggle API |
| **Drift detection** | Compare new data's `district` distinct values against `dim_district` table |
| **Alerting** | Slack/email alert if `new_districts = actual - allowed` is non-empty |
| **Auto-update** | Optionally: append new districts to `dim_district` table (Gold) |

**Pros:** Simple, well-understood, works with Kaggle's update schedule.
**Cons:** Not truly real-time (Kaggle updates are weekly/monthly).

---

### Solution 2: Dynamic Set Validation (Silver-level)

**Mechanism:** Instead of hardcoded `be_in_set`, derive allowed values from a config table or the data itself.

```python
# In Silver GE suite — dynamic set from config
allowed_districts = spark.read.parquet("s3a://lake/gold/dim_district").select("district_id").distinct()
df.filter(~F.col("district").isin(allowed_districts)).count() == 0
```

| Approach | How | Tradeoff |
|---|---|---|
| **Config-driven** | Read allowed values from `base.yaml` or S3A config file | Manual update needed |
| **Data-driven** | Derive from `dim_district` in Gold | Requires Gold to exist first |
| **Hybrid** | Config with auto-update from data drift detection | Best of both worlds |

**Pros:** No hardcoded values; validation adapts to data changes.
**Cons:** Requires Gold layer or config management.

---

### Solution 3: Event-Driven Ingestion (Future State)

**Mechanism:** Chicago PD publishes crime data via an API or webhook. Pipeline subscribes to updates.

```
Chicago PD API → webhook/Kafka → Bronze (real-time) → Silver (streaming) → Gold
```

| Component | Implementation |
|---|---|
| **Ingestion** | Kafka topic or webhook receiver |
| **Bronze** | Structured Streaming to S3A (append mode) |
| **Silver** | Structured Streaming with watermark + dedup |
| **GE** | Micro-batch validation after each window |

**Pros:** True real-time (minutes latency).
**Cons:** Requires Chicago PD to expose an API; complex infrastructure.

---

## Recommendation

For our project scope (Kaggle snapshot), **Solution 1 (Scheduled Polling) + Solution 2 (Dynamic Set Validation)** is the right fit:

1. **Scheduled polling** — Airflow DAG runs daily, fetches latest Kaggle dataset
2. **Schema drift detector** — compares new data's categorical values against expected sets
3. **Dynamic GE validation** — `be_in_set` reads from config, not hardcoded
4. **Alerting** — Slack notification if new district values detected
5. **Auto-remediation** — optionally: append new values to `dim_district` table

This gives us:
- **Zero-downtime** when source data changes
- **Audit trail** of all schema changes (logged to S3A)
- **Self-healing** pipeline (auto-update allowed sets after human approval)

---

## Implementation Plan (✅ COMPLETE)

| Phase | Deliverable | Status |
|---|---|---|
| **Phase 1** (M2 Extension) | Config-driven `be_in_set` from `base.yaml` | ✅ `pipeline/conf/base.yaml` + `settings.validation` + `run_validation._apply_config_overrides()` |
| **Phase 2** (M7 → pulled forward) | Schema drift detector in `run_validation.py` / `common/drift.py` | ✅ `pipeline.src.chicago_pipeline.common.drift._detect_district_drift()` called from `run_validation()` |
| **Phase 3** (M7 → pulled forward) | Airflow DAG drift detection task | ✅ `bronze_to_silver_dag.py` with `detect_district_drift` task via `SparkSubmitOperator`; standalone `run_drift_detection.py` entrypoint |
| **Phase 4** (M8 → pulled forward) | Slack alerting + auto-remediation | ✅ Slack webhook + auto-remediation in `common/drift.py` (`_send_slack_alert`, `_auto_remediate_districts`)

---

## Appendix: District Feature Analysis

### Synthetic vs Real Chicago Districts

| District | Synthetic | Real Chicago | Notes |
|---|---|---|---|
| 1–12 | ✅ | ✅ | Active districts |
| 13 | ✅ | ❌ | Merged into District 12 (2019) |
| 14–20 | ✅ | ✅ | Active districts |
| 21 | ✅ | ❌ | Merged into District 14 (2019) |
| 22 | ✅ | ✅ | Active district |
| 23 | ✅ | ❌ | Merged into District 10 (2019) |
| 24–25 | ✅ | ✅ | Active districts |

**Synthetic data includes all 25 (1–25).** Real Chicago has 22 active districts (13, 21, 23 merged).

### Impact on GE Validation

- Current GE set: 22 values (real Chicago)
- Synthetic data: 25 values (all 1–25)
- **6,937 rows fail** `be_in_set` with original set
- **Fix applied:** Updated set to 25 values (E3 in enhancement catalogue)

### Future-Proofing

When real data is used:
- Districts 13, 21, 23 should be `NULL` or mapped to their merged districts
- `is_unassigned_district` flag captures NULLs
- `dim_district` table in Gold handles the mapping
