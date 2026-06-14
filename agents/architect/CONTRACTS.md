# Architect — contracts

## Consumes
| Artefact | From | Used for |
|---|---|---|
| `contracts/openapi.yaml` | Backend | Review contract drift, gate releases |
| `contracts/dbt-manifest.json` | Data Engineer | Verify marts shape |
| `contracts/api-types.ts` | Backend (codegen) | Spot-check that consumers match |
| `contracts/event-catalog.md` | Data Engineer + Backend | Verify lineage events align |
| `contracts/design-tokens.json` | Frontend | Spot-check tokens |
| `contracts/CHANGELOG.md` | All | Audit trail of contract changes |

## Produces
| Artefact | Consumed by | Format |
|---|---|---|
| `docs/adr/000X-*.md` | All | Markdown, ADR template |
| `docs/architecture.md` | All | Markdown + Mermaid |
| `agents/<role>/AGENTS.md` charter edits | The agent itself | PR + Architect reviewer |
| Release sign-off comment | QA, SRE, Docs | Inline on release PR |

## Handoff protocol
- Any contract change must include an ADR in the same PR (or a linked PR).
- All ADRs are written by the architect or co-authored with the affected agent.
- Release sign-off is a single comment on the release PR that ticks the DoD checklist.
