# Contracts bus

This directory holds the **versioned artefacts** that flow between agents. They are the "wires" of the multi-agent system.

## Contents

| File | Producer | Consumers | Versioning | Update trigger |
|---|---|---|---|---|
| `openapi.yaml` | Backend | Frontend, QA, Docs, Architect | SemVer in `info.version` | Every API change |
| `dbt-manifest.json` | Data Engineer | Backend, Docs, QA, Architect | regen on `dbt run` | Every dbt run (CI) |
| `api-types.ts` | Backend (codegen) | Frontend | follows OpenAPI | Every API change |
| `event-catalog.md` | Data Engineer + Backend | SRE, Security, Architect | append-only | New event type |
| `design-tokens.json` | Frontend | Docs, self | semver | Token change |
| `CHANGELOG.md` | All | All | append-only | Every contract change |

## Rules

1. **Producer-owns.** The named producer is the only agent who can modify the file in a "regular" PR. Other agents may *suggest* changes via PR.
2. **Breaking = ADR.** Any change that breaks a downstream consumer requires an ADR in `docs/adr/` and a sign-off from at least one affected consumer.
3. **CI gates drift.** `make contracts-validate` runs in CI and fails on:
   - OpenAPI spec vs code drift (`api/app/main.py` must match `openapi.yaml`)
   - Missing or stale `dbt-manifest.json` (must be regenerated on every dbt PR)
   - Missing or empty agent files (`agents/<role>/{AGENTS,PROMPT,CONTRACTS}.md`)
   - Token shape changes without a version bump
4. **Append-only logs.** `CHANGELOG.md` and `event-catalog.md` are append-only; never edit history.

## Handoff pattern

When you change a contract, open a PR and include a **Handoff** block in the body (see root `AGENTS.md`). The PR is auto-routed via `CODEOWNERS` to:
- the producer of the file (for review)
- the architect (for sign-off on breaking changes)
- one representative consumer (for the "did this break me?" check)
