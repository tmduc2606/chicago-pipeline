# Frontend — contracts

## Consumes
| Artefact | From | Used for |
|---|---|---|
| `contracts/api-types.ts` | Backend | Type-safe fetch |
| `contracts/openapi.yaml` | Backend | Reference, codegen backup |
| `contracts/design-tokens.json` | Self | Theming |
| Backend HTTP at `/api/*` | Backend | Live data |

## Produces
| Artefact | Consumed by | Format |
|---|---|---|
| `web/src/pages/*.tsx` | QA (e2e) | TSX |
| `web/src/components/{charts,layout,filters}/*` | Self, Docs (screenshots) | TSX |
| `web/src/lib/{api,format,queryKeys,theme}.ts` | Self | TypeScript |
| `contracts/design-tokens.json` (updates) | Docs, Self | JSON |
| `web/.storybook/` | All agents for visual reference | Storybook |
| Playwright e2e reports | QA | HTML/JSON |

## Handoff: Frontend → QA

```markdown
## Handoff
- **From agent:** frontend
- **To agent(s):** qa
- **Contract(s) touched:** `contracts/design-tokens.json` (if applicable)
- **ADR (if any):** `docs/adr/000X-*.md`
- **Summary:** New page `/xxx` renders charts A, B, C against endpoints /api/x, /api/y.
- **Breaking?:** no
- **Action required by receiver:** add e2e flow + visual regression baseline.
- **Checklist:**
  - [ ] Tests added/updated
  - [ ] Lint clean
  - [ ] Lighthouse ≥ 90/95/95
  - [ ] Docs agent notified
```

## Handoff: Frontend → Docs
Triggered when screenshots or a new visual are needed in the README or `docs/`.
