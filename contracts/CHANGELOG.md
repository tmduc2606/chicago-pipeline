# Changelog — Contracts bus

This log records every change to a contract file in `/contracts`. Append-only; never edit history.

Format:

```
## <YYYY-MM-DD> — <contract file>
- Agent: <role>
- Change: <one-line>
- ADR: <docs/adr/NNNN-*.md> (if any)
- Handoff: <link to PR or commit>
```

---

## 2026-06-04 — gold-schema.json (new)
- Agent: data-engineer
- Change: added Gold output schema contract defining fact_crime + 4 dimension tables (column names, types, descriptions)
- ADR: docs/adr/0002-spark-then-dbt.md
- Handoff: M3 Gold layer implementation
- File: `contracts/gold-schema.json`

## 2026-06-03 — bootstrap
- Agent: architect
- Change: initialised the contracts bus with placeholder / first-cut versions of all six files.
- ADR: docs/adr/0001-minio-over-seaweedfs.md, 0002-spark-then-dbt.md, 0003-fastapi-react.md, 0004-no-auth-public.md
- Handoff: M0 skeleton (this PR)
- Files:
  - `openapi.yaml` — full schema for 19 routes; producer backend will regenerate from FastAPI on first run
  - `dbt-manifest.json` — placeholder; data-engineer will regenerate on first `dbt run`
  - `api-types.ts` — placeholder; backend will regenerate from openapi.yaml
  - `event-catalog.md` — first version
  - `design-tokens.json` — first version
  - `CHANGELOG.md` — this file
