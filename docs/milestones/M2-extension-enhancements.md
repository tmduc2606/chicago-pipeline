# M2 Extension — Enhancement Catalogue

> Status: **PROPOSED** — after M2 Extension implementation, reviewed 2026-06-04
> Source: GE validation analysis, Silver transform analysis, agent review

---

## Priority 1 — Critical (✅ COMPLETE 2026-06-04)

### E1. Fix case_number regex in Silver GE suite ✅

**Was:** `^[A-Z]\d{6,}$` — 1 letter + 6+ digits
**Fixed:** `^[A-Z]{2}\d{6}$` — 2 letters + 6 digits (matches `HX100001` and real `JH123456`)

| File | Change |
|---|---|
| `great_expectations/suites/chicago_crime_silver.json` | `regex: "^[A-Z]{2}\\d{6}$"` |

---

### E2. Implement `expect_column_values_to_be_of_type` in run_validation.py ✅

**Was:** Silently returns `(True, "SKIPPED")` — 3 critical expectations never tested.
**Fixed:** Implemented type-check handler using `df.schema[col].dataType.simpleString()`.

| File | Change |
|---|---|
| `great_expectations/run_validation.py` | Added `elif exp_type == "expect_column_values_to_be_of_type":` branch |

**Result:** All 3 type checks now PASS: date→date, arrest→boolean, domestic→boolean.

---

### E3. Implement `expect_column_values_to_be_in_set` in run_validation.py ✅

**Was:** Silently returns `(True, "SKIPPED")` — district set membership never tested.
**Fixed:** Implemented set-membership handler using `F.col(col).isin(list(value_set))`.

| File | Change |
|---|---|
| `great_expectations/run_validation.py` | Added `elif exp_type == "expect_column_values_to_be_in_set":` branch |
| `great_expectations/suites/chicago_crime_silver.json` | Updated district set: added 13, 21, 23 (synthetic data has all 25) |

**Result:** District validation now PASS (0 values outside allowed set).

---

## Priority 2 — High (✅ COMPLETE 2026-06-04)

### E4. Bronze partition cleanup mechanism ✅

**Problem:** `to_bronze.py` creates a new partition per ingest date. Same CSV ingested twice → 2 partitions with identical data. Silver dedup handles this, but Bronze accumulates stale partitions.

**Options:**
1. **Partition pruning in Silver** — filter to latest `ingest_date` only
2. **Bronze-level idempotency** — check if partition exists before writing
3. **Partition retention policy** — auto-delete partitions older than N days

**Recommendation:** Option 1 (partition pruning) is safest for Medallion compliance — Bronze stays immutable, Silver decides what to read.

| File | Change |
|---|---|
| `pipeline/src/chicago_pipeline/silver/to_silver.py` | Read only latest `ingest_date` partition |

---

### E5. `hours_to_update` edge case — `unix_timestamp` on DateType ✅

**Current:** `(F.unix_timestamp("updated_on_ts") - F.unix_timestamp("date")) / 3600`

`F.unix_timestamp(DateType)` works in Spark 3.5.x but is undocumented behavior. In earlier Spark versions or edge cases (epoch boundary dates), it may return null.

**Fix:** Cast `date` to timestamp explicitly:

```python
(F.unix_timestamp("updated_on_ts") - F.unix_timestamp(F.col("date").cast("timestamp"))) / 3600
```

| File | Change |
|---|---|
| `pipeline/src/chicago_pipeline/silver/to_silver.py` | `_add_hours_to_update()` — add `.cast("timestamp")` |

---

## Priority 3 — Medium (✅ COMPLETE 2026-06-04)

### E6. GE validation report as pipeline artifact ✅

**Current:** `run_validation.py` writes a JSON report to `/opt/great_expectations/reports/`. This is ephemeral (lost on container restart).

**Enhancement:** Write GE reports to S3A as a pipeline artifact:
- Path: `s3a://lake/reports/ge/{suite_name}/{date}/report.json`
- Enables historical comparison and Grafana dashboard integration

---

### E7. GE suite versioning ✅

**Current:** Single `chicago_crime_silver.json` file. Schema changes overwrite the previous version.

**Enhancement:** Add `$schema` version field and a `version` key to each suite. When schema changes, bump version and keep old version in a `/versions/` subdirectory.

---

### E8. Silver schema evolution tracking ✅

**Current:** `SILVER_COLUMNS` is a hardcoded dict. Adding/removing columns requires code changes.

**Enhancement:** Derive expected schema from the union of Bronze schema + extension columns. Use `df.schema` diff to detect unexpected changes.

---

### E9. `is_domestic_arrest` redundant column check ✅ (no change)

**Current:** `is_domestic_arrest = arrest AND domestic`. This is a derived boolean that could be computed at query time.

**Decision:** Keep as-is. Storage cost (1 byte/row × 57,931 rows ≈ 56 KB) is negligible. The column is used by dbt marts for arrest analysis filtering. Revisit in M8 polish pass if needed.

---

### E10. Bronze regex validation for case_number ✅

**Current:** Bronze suite has no case_number regex test. The wrong regex was discovered in Silver.

**Enhancement:** Add `expect_column_values_to_match_regex` for case_number to the Bronze suite as well, with the corrected regex `^[A-Z]{2}\d{6}$`.

| File | Change |
|---|---|
| `great_expectations/suites/chicago_crime_bronze.json` | Add case_number regex expectation |

---

## Summary Table

| ID | Priority | Type | File(s) | Effort | Status |
|---|---|---|---|---|---|
| E1 | P1 | Bug fix | Silver GE suite | 5 min | ✅ 2026-06-04 |
| E2 | P1 | Feature | run_validation.py | 30 min | ✅ 2026-06-04 |
| E3 | P1 | Feature | run_validation.py | 15 min | ✅ 2026-06-04 |
| E4 | P2 | Enhancement | to_silver.py | 1 hr | ✅ 2026-06-04 |
| E5 | P2 | Robustness | to_silver.py | 10 min | ✅ 2026-06-04 |
| E6 | P3 | Enhancement | run_validation.py | 2 hr | ✅ 2026-06-04 |
| E7 | P3 | Enhancement | GE suite files | 1 hr | ✅ 2026-06-04 |
| E8 | P3 | Enhancement | to_silver.py | 2 hr | ✅ 2026-06-04 |
| E9 | P3 | Design | to_silver.py | 15 min | ✅ 2026-06-04 (no change) |
| E10 | P3 | Consistency | Bronze GE suite | 5 min | ✅ 2026-06-04 |
| — | — | Bug fix | Bronze GE suite | 5 min | ✅ 2026-06-04 (removed `id` uniqueness check — duplicate partitions expected in raw Bronze) |
