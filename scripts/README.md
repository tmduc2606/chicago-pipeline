# Scripts

## Operational (SRE-owned)
- `healthcheck.sh` — Docker health check
- `pipeline_init.sh` — Full pipeline initialization (7 steps)
- `rebuild_pipeline.sh` — Pipeline rebuild utility
- `seed.py` / `seed.sh` — Data seeding
- `pipeline.ps1` — PowerShell pipeline helper
- `urls.sh` — URL reference

## Agent Validation
- `validate_agents.sh` — Agent spec validation (used by `make agents-lint`)
- `validate_contracts.sh` — Contract validation

## Data Exploration
- `explore/bronze_explorer.py` — Bronze layer inspection
- `explore/bronze_query.py` — Bronze queries
- `explore/gold_explorer.py` — Gold layer inspection
- `explore/gold_query.py` — Gold queries
- `explore/warehouse_explorer.py` — Warehouse inspection

## Milestone Verification
- `spike/check_districts.py` — M2 district verification
- `spike/m2_silver_eda.py` — M2 Silver EDA
- `spike/verify_m2_extension.py` — M2 extension verification
- `spike/verify_m3_gold.py` — M3 Gold verification
- `spike/verify_m4_warehouse.py` — M4 Warehouse verification

## Initialization
- `initdb/01-schema.sql` — PostgreSQL schema initialization (used by Docker)

## One-off Tests
- `test_gold_query_batch.py` / `test_gold_query_batch.sh` — Gold query batch testing
- `gold_query_commands.txt` — Query reference notes
