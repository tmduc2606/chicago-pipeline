# QA — contracts

## Consumes
| Artefact | From | Used for |
|---|---|---|
| `contracts/openapi.yaml` | Backend | Drift test |
| `contracts/dbt-manifest.json` | Data Engineer | Schema test |
| `contracts/api-types.ts` | Backend | Compile-time consistency |
| `contracts/event-catalog.md` | Data Engineer + Backend | Event schema test |
| `contracts/design-tokens.json` | Frontend | Token shape test |
| All code under test | All agents | Unit / integration / e2e |

## Produces
| Artefact | Consumed by | Format |
|---|---|---|
| `tests/**/test_*.py` | CI | Python |
| `web/tests/**/*.test.ts` | CI | TypeScript |
| `web/tests/e2e/*.spec.ts` | CI | Playwright |
| Coverage report | Docs (badge), Architect (gate) | HTML + JSON |
| Release sign-off comment | All | Markdown |

## Handoff: QA → Architect
On every release PR:

```markdown
## QA sign-off
- [ ] pytest: <N> passed, <M> skipped, 0 failed
- [ ] vitest: <N> passed, 0 failed
- [ ] Playwright: <N> flows passed, 0 failed
- [ ] Coverage: api <X>%, web <Y>%, pipeline <Z>%
- [ ] Contracts: 0 drift
- [ ] Trivy: 0 Critical, 0 High
- [ ] Smoke: `make up && make pipeline` green
```

## Handoff: QA → Docs
After every release, hand the badge SVGs and a one-paragraph "what was tested" blurb.
