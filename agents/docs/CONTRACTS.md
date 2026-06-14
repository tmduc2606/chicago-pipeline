# Docs — contracts

## Consumes
| Artefact | From | Used for |
|---|---|---|
| `docs/adr/*` | Architect | Link from README + changelog |
| `contracts/openapi.yaml` | Backend | Link from README |
| Screenshots | Frontend | Embed in README |
| QA report | QA | "Tested by" line in changelog |
| Architecture diagram | Architect | Embed in `docs/architecture.md` |
| Runbook | SRE | Link from README |

## Produces
| Artefact | Consumed by | Format |
|---|---|---|
| `README.md` | Reviewers | Markdown |
| `docs/architecture.md` | Reviewers | Markdown + Mermaid |
| `CHANGELOG.md` | Reviewers | Markdown (Keep a Changelog) |
| `docs/adr/000X-*.md` (drafts) | Architect (sign-off), all | Markdown |
| `docs/spikes/<X>-*.md` | Architects / reviewers | Markdown |
| `docs/assets/*.png`, `*.gif` | README, blog | PNG/GIF |

## Handoff: Docs → All (release)
On every release:

```markdown
## Handoff
- **From agent:** docs
- **To agent(s):** all
- **Contract(s) touched:** `README.md`, `CHANGELOG.md`
- **Summary:** Release vX.Y.Z — see CHANGELOG for highlights.
- **Action required by receiver:** review the changelog entry for accuracy; thumbs-up on the PR.
```

## Handoff: Docs → Architect
On ADR draft:

```markdown
## Handoff
- **From agent:** docs
- **To agent(s):** architect
- **Contract(s) touched:** `docs/adr/000X-*.md`
- **Summary:** Draft ADR for <topic>; please review Context + Decision sections.
- **Action required by receiver:** sign off or request changes.
```
