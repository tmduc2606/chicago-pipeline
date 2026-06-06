# ADR 0004 — Public dashboard (no authentication)

- **Status:** Accepted (2026-06-03)
- **Author:** Architect agent
- **Reviewers:** Backend, Security

## Context

The original design in `reports/End-to-end Chicago DBMS.docx` does not specify authentication. The dashboard is a portfolio piece that visualises **public crime data** (Kaggle, sourced from the City of Chicago). There is no PII in the data — every record is a non-personal aggregate of a reported incident. The target audience is **recruiters and hiring managers** who need to see the dashboard in < 5 minutes from a `make up && make demo` run.

Adding authentication (JWT, OAuth, RBAC) would:
- Add a login page that blocks the first impression.
- Require a user store, a token service, a refresh mechanism, and protected routes.
- Require the reviewer to create an account or use a shared credential (which leaks in demos).
- Add ~1–2 days of development time for a feature the dashboard does not need.

## Decision

The dashboard is **publicly accessible** with no authentication.

## Consequences

**Positive**
- A reviewer opens `http://localhost:5173` and sees the data immediately. No login friction.
- The API has no auth middleware, keeping the codebase simpler.
- No user store, no tokens, no refresh logic — less code to maintain and test.
- The README's "quick start" section is 3 steps, not 5.

**Negative**
- Anyone on the network can hit the dashboard and API. In a local Docker Compose context this is acceptable; in a production deployment it would not be.
- The API has no rate limiting (beyond basic nginx/uvicorn defaults). A future addition of `slowapi` would mitigate this.
- No audit trail of who viewed what (not required for a portfolio).

## Alternatives considered

1. **Basic HTTP auth (nginx)** — trivial to add, but blocks curl / Swagger testing without credentials. Rejected.
2. **JWT + role-based access** — adds a login page, a user table, a token refresh mechanism. Too much surface area for a read-only portfolio. Deferred to a future "v2" if needed.
3. **OAuth (GitHub)** — nice portfolio signal, but adds a third-party dependency and a redirect flow. Deferred.

## Future path

If a future version adds write operations (e.g. a user can submit an annotation or flag a false positive), authentication will be added via FastAPI's `Depends(get_current_user)` with a JWT bearer flow, plus a `/auth/login` and `/auth/refresh` pair. The current API is designed to make that addition straightforward (the `request_id` middleware is already in place).

## Operational notes

- The API is rate-limited to `60 rpm/IP` via `slowapi` (added in M5).
- The SPA sets `Cache-Control: no-store` on API responses in dev to avoid stale-data surprises.
- Grafana (which does have auth) is the one service in the stack that requires credentials — see `.env.example` for defaults.
