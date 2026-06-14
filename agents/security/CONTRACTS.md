# Security — contracts

## Consumes
| Artefact | From | Used for |
|---|---|---|
| `requirements.txt`, `package.json`, `pyproject.toml` | All | Dep inventory |
| `.github/dependabot.yml` | Self | Update cadence |
| Trivy / CodeQL / gitleaks output | CI | Gate |
| ADRs that touch trust boundaries | Architect | Review |

## Produces
| Artefact | Consumed by | Format |
|---|---|---|
| `.env.example` | All | dotenv |
| `SECURITY.md` | Reviewers, researchers | Markdown |
| `CODEOWNERS` | GitHub | Git ignore-style |
| `.github/dependabot.yml` | GitHub | YAML |
| Trivy report | CI, release PR | JSON / SARIF |
| License report | Docs, release | Markdown table |

## Handoff: Security → Architect (vuln)

```markdown
## Handoff
- **From agent:** security
- **To agent(s):** architect
- **Contract(s) touched:** `docs/adr/000X-*.md`
- **Summary:** CVE-XXXX-XXXX in <dep> affects <service>; severity High.
- **Action required by receiver:** decide patch vs pin vs accept; release gate.
- **Checklist:**
  - [ ] Fix scheduled
  - [ ] Post-mortem filed (if Critical)
  - [ ] Docs agent notified (CHANGELOG)
```

## Handoff: Security → All
On new policy:

```markdown
## Handoff
- **From agent:** security
- **To agent(s):** all
- **Summary:** New license whitelist effective immediately. Direct deps must be MIT / Apache-2.0 / BSD-3.
- **Action required by receiver:** audit your sub-tree; remove any non-whitelisted dep.
```
