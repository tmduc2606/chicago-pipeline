# ADR 0003 — FastAPI + React replacing Streamlit

- **Status:** Accepted (2026-06-03)
- **Author:** Architect agent
- **Reviewers:** Backend, Frontend, QA

## Context

The original design uses **Streamlit** for the presentation layer. Streamlit is excellent for quick internal dashboards and data-science proofs-of-concept, but it has significant weaknesses as a portfolio centerpiece:

1. **Not a SPA.** Streamlit reruns the entire Python script on every interaction. For a reviewer accustomed to React/Next.js, this looks like a prototype, not a product.
2. **No type-safe contract.** There is no OpenAPI spec, no pydantic schemas for the front-end, no TypeScript types. The front-end is "Python all the way down."
3. **No separation of concerns.** Business logic, queries, and rendering are all in the same file. No router, no services layer, no DI, no middleware.
4. **No real front-end story.** No component library, no design tokens, no accessibility testing, no Storybook, no Lighthouse. The portfolio signal is "I can use Streamlit" rather than "I can build a production web application."
5. **Hard to test.** No pytest routes, no Playwright e2e, no contract tests.

The overhaul replaces Streamlit with **FastAPI + React** (Vite/TS/Tailwind/shadcn/ui/Recharts/MapLibre).

## Decision

We will use:

- **FastAPI** (Python 3.11+, async, Pydantic v2) as the HTTP API layer.
- **React 18 + TypeScript** (Vite, TanStack Query, Zustand, Recharts, MapLibre GL) as the SPA.

The API reads from **dbt marts only** — never from raw fact tables. The SPA calls the API; it never touches the database directly.

## Consequences

**Positive**
- A clean, testable contract (`contracts/openapi.yaml`) that both agents can code against.
- The front-end can be developed independently of the back-end by using Swagger mock.
- Each layer has its own test pyramid (pytest, vitest, Playwright).
- The API can be consumed by any client (Jupyter, Grafana, another app).
- OpenAPI + Swagger UI = self-documenting.
- The portfolio shows a full-stack engineering story, not just a data story.

**Negative**
- More code and more services than Streamlit.
- API latency adds a hop (SPA → API → Postgres); mitigated by Redis caching (5 min TTL, SWR).
- Two dev environments (Python for API, Node for SPA) unless Dockerised (which it is).

## Alternatives considered

1. **Streamlit (keep)** — simpler, but weak portfolio signal. Rejected.
2. **Dash (Plotly)** — closer to Streamlit; same SPA weakness. Rejected.
3. **Next.js (full-stack)** — SSR/ISR overkill for a read-only dashboard. Rejected.
4. **Gradio** — designed for ML demos, not analytics dashboards. Rejected.

## Operational notes

- FastAPI runs on port `8000`; Swagger at `/docs`, ReDoc at `/redoc`.
- React dev server runs on port `5173` (Vite HMR); production build via `docker build`.
- CORS: in dev, `localhost:5173` is allowed; in prod, the SPA is served by Nginx alongside the API (future consideration).
- The SPA fetches typed data via `contracts/api-types.ts` (generated from `openapi.yaml`).
