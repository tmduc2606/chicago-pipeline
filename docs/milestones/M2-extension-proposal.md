# M2 Extension — Silver Layer "Just-Enough" Feature Engineering

**Status:** Revised proposal after Phase A EDA + Medallion Architecture alignment
**Date:** 2026-06-03 (revised 2026-06-04 with 100% EDA + Medallion architecture alignment)
**Reference notebooks:** `references/notebooks/01_eda_and_inspection.ipynb`, `02_preprocessing_and_feature_engineering.ipynb`
**EDA script:** `scripts/spike/m2_silver_eda.py` (run on spark-master)
**Architecture reference:** [Databricks — What is Medallion Architecture](https://www.databricks.com/blog/what-is-medallion-architecture)

---

## 0. EDA Verification — What the Data Actually Looks Like

The Phase A inspection ran on **100% of the synthetic data (57,931 rows)** from `/tmp/chicago_synthetic.csv`. Findings that changed the original proposal:

| Observation | Impact on proposal |
|---|---|
| `primary_type` is already ALL-CAPS (`"WEAPONS VIOLATION"`) in the synthetic data | **Reverse** Stage 1.1 recommendation: keep `primary_type` as-is, do NOT `lower()` it. The synthetic generator mimics the real Chicago feed format (Title Case) only for the 3 non-cap fields, so the `lower()` rule would destroy information in the real feed too. |
| `description` is already ALL-CAPS (`"Unlawful use - other than firearm"` in the head, but `"SIMPLE"` for assault) | **Mixed** — keep as-is, no normalization. The DS pattern of `lower()` assumes free-text with case variation. |
| `location_description` is already Title Case (`"STREET"`, `"RESIDENCE"`, `"BAR OR TAVERN"`) | No-op. Keep as-is. |
| `block` is Title Case + ALL-CAPS street suffix (`"4741 N EXAMPLE ST"`) | No transformation needed; current state is already correct. |
| `fbi_code` is **numeric** (`"06"`, `"15"`) not letters | The `upper()` rule is a no-op. Remove from Stage 1. |
| `date` format is uniformly `2024-01-01T16:56:55` (ISO) in synthetic | Date fallback chain is still correct (real data uses `MM/dd/yyyy hh:mm:ss a`). |
| `updated_on == date` for ~99.9% of rows in synthetic | The `hours_to_update` feature will be **always 0** in synthetic, but is real-data meaningful. Keep the feature. |
| All columns read as `string` from CSV | Confirms cast is needed in Silver. |
| **Zero nulls** in sample | The 6 "is_unassigned_*" flags I proposed will be uniformly `False` in synthetic. They remain useful for **real** Chicago data (which has 5–12% nulls on ward/community_area per the public dataset). Keep them; gate on real-data validation. |
| `primary_type`: only 10 unique (vs ~35 in real) | Confirms synthetic is a low-cardinality subset. Low-cardinality `primary_type` is still good for `dim_offense` (1 row per type in Gold). |
| `description`: only 10 unique (vs ~500+ in real) | Same comment. |
| `iucr`: 900 unique — **medium-high** cardinality | This is the **real** Chicago cardinality. Good `dim_iucr` candidate. |
| `ward`: 50 unique (Chicago has 50 wards) | Exact match to real city structure. Confirms `dim_ward` is safe. |
| `community_area`: 77 unique (Chicago has 77 community areas) | Exact match. Confirms `dim_community_area` is safe. |
| `district`: 25 unique (Chicago has 25 police districts) | Exact match. Confirms `dim_district` is safe. |
| `latitude`/`longitude`: ~98% unique per row | They are *de facto* per-row geo. The `lat_rounded_3/lon_rounded_3` idea is **wrong** — that just gives you per-row values with lower precision. Drop it; the bbox filter is enough. |

**Net effect on the proposal:**
- Stage 1 collapses to **just one rule**: `trim()` whitespace on all string cols. No case-flipping.
- `date` stays as `DateType` (no timestamp upcast) — no schema breakage.
- `date_hour` removed from Silver (requires timestamp; belongs in Gold).
- `date_year`, `date_month`, `date_dow` derived from `DateType` (3NF-like decomposition).
- Sin/cos, `is_downtown`, `distance_to_downtown_km` deferred to Gold per Medallion Architecture.
- The 6 `is_unassigned_*` flags stay (real-data utility).
- `updated_on_ts` and `hours_to_update` stay (conforming arithmetic).

---

## 1. Motivation & Medallion Architecture Alignment

### What the Medallion Architecture says about Silver

> *"In the Silver layer of the lakehouse, the data from the Bronze layer is matched, merged, conformed and cleansed ("just-enough") so that the Silver layer can provide an "Enterprise view" of all its key business entities, concepts and transactions."*
>
> *"Only minimal or "just-enough" transformations and data cleansing rules are applied while loading the Silver layer. Speed and agility to ingest and deliver the data in the data lake is prioritized, and a lot of project-specific complex transformations and business rules are applied while loading the data from the Silver to Gold layer."*
>
> — [Databricks, What is Medallion Architecture](https://www.databricks.com/blog/what-is-medallion-architecture)

### What this means for our Silver

The current Silver does schema enforcement + cleaning (cast, bbox filter, date range, dedup, partition). This extension adds **"just-enough" conforming transformations** — the minimum feature engineering that makes Silver enterprise-ready for dbt-Gold consumption:

| Layer | Allowed transformations | Our scope |
|---|---|---|
| **Bronze** | Raw ingestion, format preservation | ✅ M1 complete |
| **Silver** | Conform, dedup, clean, light decomposition (3NF-like) | ✅ M2 current + extension |
| **Gold** | Complex business rules, ML features, joins, aggregations | dbt scope (M4+) |

### What stays in Silver (per Medallion)

- **Conforming**: `trim()` whitespace normalization
- **Conforming**: Boolean flag derivation (`is_arrested`, `is_domestic`, `is_unassigned_*`)
- **Conforming**: Date decomposition (`date_year`, `date_month`, `date_dow`, `date_hour`) — 3NF-like columnar decomposition
- **Conforming**: `hours_to_update` — derived from two existing timestamps, pure arithmetic

### What moves to Gold (deferred from Silver)

These are **complex transformations / business rules / ML features** — not "just-enough" conforming:

- ❌ Sin/cos cyclical encoding → Gold/dbt (ML feature, project-specific)
- ❌ `is_downtown` bbox classification → Gold/dbt (business rule)
- ❌ `distance_to_downtown_km` → Gold/dbt (derived metric)
- ❌ Cardinality report → Gold/dbt (analysis artifact, not a row-level transform)

This keeps Silver as a **1:1 row-preserving, enterprise-view transformation** — no aggregations, no joins, no row drops beyond dedup/bbox/date-range, no project-specific logic.

---

## 2. Two-Phase Workflow (unchanged)

### Phase A — EDA on Full Dataset ✓ DONE

1. **Load 100% of the Bronze data** — done. Used `spark.read.csv(path, header=True, inferSchema=False)` → 57,931 rows.
2. **Structural inspection** (`inspect_df()` mirror from reference notebook) — done. See `scripts/spike/m2_silver_eda.py` for the runnable.
3. **Cardinality check** — done. See the table in §0.
4. **Outcome:** inspection findings written to §0 of this doc; original proposal revised to align with Medallion Architecture.

### Phase B — Layered Silver Transformations (next)

Apply the four-stage approach, translated to PySpark. Each stage is a **separate function** in `to_silver.py` for testability; `silver_transform()` is a thin pipeline.

---

## 3. Refined Stage-by-Stage Design

### Stage 1 — Standardize (REVISED — minimal)

**Reference pattern:** `standardize_columns()` and `normalize_text()` in the reference notebooks.

**Refined rule:** the only standardization that survives is `trim()` whitespace. No case-flipping. No letter-case normalization. Evidence: §0.

| Column | Action | Why |
|---|---|---|
| All string cols | `F.trim(F.col(c))` | Synthetic data has no leading/trailing whitespace, but real Chicago CSV often does (Excel exports). Defensive. |

That's it. **One line per column.** Stage 1 is now ~5 lines of code instead of ~30.

**Implementation sketch:**
```python
def _standardize_text(df):
    for c in ["primary_type", "description", "location_description", "block", "fbi_code", "case_number", "beat"]:
        df = df.withColumn(c, F.trim(F.col(c)))
    return df
```

---

### Stage 2 — Convert Date Columns (REVISED — keep DateType)

**Reference pattern:** `pd.to_datetime(..., errors="coerce")` + clip + recency features.

| Column | Current dtype | Proposed dtype | Extra features derived |
|---|---|---|---|
| `date` | `StringType` | `DateType` (keep, no upcast) | `date_year`, `date_month`, `date_dow` (3 ints) |
| `updated_on` | `StringType` | `TimestampType` → `updated_on_ts` | `hours_to_update` = `(updated_on_ts - date)`, clipped to `[0, 365*24]` |

**Decision:** `date` stays as `DateType` — no schema breakage. `date_hour` is deferred to Gold (requires timestamp source, project-specific granularity decision).

---

### Stage 3 — Conforming (lightweight, Medallion-aligned)

All features are **additive** — no existing column is overwritten. All are "just-enough" conforming transformations per Medallion Architecture.

#### 3.1 — Boolean flags (conforming)

| Source | Proposed flag | Rationale |
|---|---|---|
| `arrest` (bool) | `is_arrested` | rename for analyst clarity |
| `domestic` (bool) | `is_domestic` | same |
| `arrest & domestic` | `is_domestic_arrest` | high-priority subset |
| `district IS NULL` | `is_unassigned_district` | data quality flag (synthetic: always False; real: ~5%) |
| `community_area IS NULL` | `is_unassigned_community` | data quality flag (real: ~8%) |
| `ward IS NULL` | `is_unassigned_ward` | data quality flag (real: ~12%) |

#### 3.2 — hours_to_update (conforming)

| Source | Feature | Rationale |
|---|---|---|
| `updated_on_ts - date` | `hours_to_update` | Pure arithmetic on two existing timestamps, clipped to [0, 365*24]. Conforming, not a business rule. |

**Note:** `updated_on_ts` is already computed in Stage 2 as a byproduct of casting `updated_on` to timestamp.

---

### What Moves to Gold (deferred from Silver)

Per Medallion Architecture, the following are **project-specific complex transformations / ML features** — not "just-enough" conforming. They belong in dbt-Gold:

| Feature | Why it's Gold, not Silver |
|---|---|
| Sin/cos cyclical encoding (`hour_sin/cos`, `dow_sin/cos`, `month_sin/cos`) | ML feature engineering — project-specific, not enterprise conforming |
| `is_downtown` (bbox classification) | Business rule — "downtown" is a project-specific definition |
| `distance_to_downtown_km` | Derived metric — requires domain-specific reference point |
| Cardinality report | Analysis artifact — not a row-level transform; dbt can recompute |

---

## 4. Refined Feature Summary Table

| Column | Type | Source | Stage |
|---|---|---|---|
| `id` | int | bronze | 0 (cast) |
| `case_number` | string (trimmed) | bronze | 0/1 |
| `date` | date (kept, no upcast) | bronze | 2 |
| `block` | string (trimmed) | bronze | 0/1 |
| `iucr` | string | bronze | 0 |
| `primary_type` | string (trimmed, case preserved) | bronze | 0/1 |
| `description` | string (trimmed) | bronze | 0/1 |
| `location_description` | string (trimmed) | bronze | 0/1 |
| `arrest` | bool | bronze | 0 |
| `domestic` | bool | bronze | 0 |
| `beat` | string (trimmed) | bronze | 0/1 |
| `district` | int | bronze | 0 |
| `ward` | int | bronze | 0 |
| `community_area` | int | bronze | 0 |
| `fbi_code` | string (trimmed) | bronze | 0/1 |
| `latitude` | float | bronze | 0 |
| `longitude` | float | bronze | 0 |
| `updated_on` | string (kept) | bronze | 0 |
| **`is_arrested`** | bool | arrest | 3.1 |
| **`is_domestic`** | bool | domestic | 3.1 |
| **`is_domestic_arrest`** | bool | arrest & domestic | 3.1 |
| **`is_unassigned_district`** | bool | district is null | 3.1 |
| **`is_unassigned_community`** | bool | community_area is null | 3.1 |
| **`is_unassigned_ward`** | bool | ward is null | 3.1 |
| **`date_year`** | int | date | 2 |
| **`date_month`** | int | date | 2 |
| **`date_dow`** | int | date | 2 |
| **`updated_on_ts`** | timestamp | updated_on | 2 |
| **`hours_to_update`** | int | updated_on_ts - date | 3.2 |

**Total: 29 columns** (was 18). Net new: 11 conforming features. (`date_hour` deferred to Gold; sin/cos, `is_downtown`, `distance_to_downtown_km` also deferred.)

---

## 5. What Stays Out of Silver (Defer to dbt-Gold)

- **Joins** to external dimension tables (PostGIS community areas, FBI code → offense hierarchy).
- **Aggregations** (count by ward × month, etc.) — strictly Gold.
- **TF-IDF / embeddings** on `description` text.
- **Missing-value imputation** beyond null-flagging.
- **Train/test splits**.
- **`block` split** into address components (defer to a `dim_address` mart in Gold if needed).
- **Sin/cos cyclical encoding** — ML feature, project-specific, not enterprise conforming.
- **`is_downtown`** — business rule, project-specific definition of "downtown".
- **`distance_to_downtown_km`** — derived metric, domain-specific reference point.
- **Cardinality report** — analysis artifact, dbt can recompute.

---

## 6. Risks & Open Questions (REVISED)

1. **Schema breakage** — Gold models need to re-select columns. Mitigation: keep all **original** column names; only add new ones. `date` stays as `DateType` — no schema break.
2. **Cardinality report** moved to Gold — dbt can recompute if needed. No Silver impact.
3. **No `block` split, no `lat_rounded_3`** — both dropped from proposal after EDA. See §0.
4. **All null-flags will be `False` in synthetic data** — but they're real-data meaningful. Gate the acceptance test on both synthetic AND a real-data sanity check (if available).
5. **Sin/cos, `is_downtown`, `distance_to_downtown_km`** — moved to Gold per Medallion Architecture. They are project-specific complex transforms, not "just-enough" conforming.
6. **`date_hour` deferred to Gold** — requires timestamp source, project-specific granularity decision.

---

## 7. Acceptance Criteria (REVISED)

- [ ] `pipeline/tests/test_silver.py` extended to assert the 11 new columns exist and have correct dtypes.
- [ ] GE Silver suite (`great_expectations/suites/chicago_crime_silver.json`) updated with `not_null` expectations on the 6 boolean flags.
- [ ] `make spark-silver` still passes `make ge-silver` validation.
- [ ] No row drops beyond current behaviour (57,931 → 57,931 if all synthetic rows are in bbox+date range).
- [ ] Spark write time stays under 90s (currently ~70s for 57k rows; 11 added columns should add < 3s).
- [ ] Re-run `scripts/spike/m2_silver_eda.py` on the new Silver output and confirm new columns have the expected distributions (e.g. `is_arrested` mean ≈ `arrest` mean ≈ 0.177).

---

## 8. Resolved Decisions (formerly Open Questions)

| Question | Decision | Rationale |
|---|---|---|
| `date` → timestamp upcast? | **No** — keep `DateType` | Avoids schema breakage; `date_hour` deferred to Gold |
| Defensive `trim()`? | **Yes** — keep it | Zero cost, real-data safety |
| Sin/cos encoding in Silver? | **No** — deferred to Gold | ML feature engineering, project-specific |
| `is_downtown` in Silver? | **No** — deferred to Gold | Business rule, project-specific |
| `distance_to_downtown_km` in Silver? | **No** — deferred to Gold | Derived metric, domain-specific |
| Cardinality report in Silver? | **No** — deferred to Gold | Analysis artifact, dbt can recompute |

---

## 9. EDA Reproduction Commands

```bash
# Copy the EDA script to the spark container
docker compose exec -T spark-master mkdir -p /tmp/spike
docker compose cp scripts/spike/m2_silver_eda.py spark-master:/tmp/spike/m2_silver_eda.py

# Run on the synthetic CSV (100% proportion)
docker compose exec -T spark-master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  /tmp/spike/m2_silver_eda.py /tmp/chicago_synthetic.csv 1.0 42
```

Expected output: 57,931-row full dataset, all-null-zero, no duplicates, cardinality table as in §0.
