# Security & Compliance

> The Security agent owns this file. See [`agents/security/AGENTS.md`](./agents/security/AGENTS.md).

## Scope

This is a **portfolio-only** data platform running locally via Docker Compose. It does not handle PII, does not expose a public endpoint, and does not store user credentials.

## Secrets

- Never commit `.env` — only `.env.example` is tracked.
- All secrets are read from environment variables at runtime.
- The `AIRFLOW_FERNET_KEY` in `.env.example` contains a placeholder value that must be replaced before first use.

## Dependency scanning

- Trivy runs on every CI build and gates the release (0 Critical, 0 High).
- Dependabot is configured for weekly updates (grouped by ecosystem).
- `pip-licenses` (Python) and `npx license-checker` (Node) run in CI; only MIT / Apache-2.0 / BSD-3-Clause are whitelisted.

## Licence policy

| Acceptable | Not acceptable |
|---|---|
| MIT | AGPL |
| Apache-2.0 | SSPL |
| BSD-3-Clause | CC-BY-NC |
| BSD-2-Clause | |
| ISC | |
| 0BSD | |

## Secret rotation

Secrets in `.env` are rotated every **90 days** (tracked in `docs/runbook.md`). For a local-only demo this is a discipline exercise; for a cloud deployment it would be enforced via Vault or cloud secret store.

## Incident response

1. Triage a CVE within **24 h**.
2. Patch / pin within **7 d** (High) or **30 d** (Medium).
3. Post-mortem in `docs/postmortems/` for any Critical finding.
4. Notify the Docs agent for a `CHANGELOG.md` entry.
