# AGENTS.md — chicago-pipeline multi-agent charter

This repository is built and maintained by a team of specialised LLM agents.
Each agent has its own rules, prompt, and contract under `agents/<role>/`.

## The team
- **Architect** (coordinator) — [`agents/architect/`](./agents/architect/AGENTS.md)
- **Data Engineer** — [`agents/data-engineer/`](./agents/data-engineer/AGENTS.md)
- **Backend Engineer** — [`agents/backend/`](./agents/backend/AGENTS.md)
- **Frontend Engineer** — [`agents/frontend/`](./agents/frontend/AGENTS.md)
- **QA** (assessment + EDA) — [`agents/qa/`](./agents/qa/AGENTS.md)
- **SRE / Observability** — [`agents/sre/`](./agents/sre/AGENTS.md)
- **Docs / Storyteller** — [`agents/docs/`](./agents/docs/AGENTS.md)
- **Security & Compliance** — [`agents/security/`](./agents/security/AGENTS.md)
- **Future:** LLM Integration (M8)

## How we work
1. Every agent works **inside its owned sub-tree** (see [`docs/architecture.md`](./docs/architecture.md)).
2. Cross-tree changes go through **contracts** under [`/contracts`](./contracts/README.md) and require **Architect** sign-off.
3. Before writing code, check [`docs/implementation_mistakes.md`](./docs/implementation_mistakes.md) for known anti-patterns.

## Global gate
`make lint && make test && make pipeline` must be green before any PR merges.

## Definition of Done (release-level)
- [ ] All agent-owned tests pass
- [ ] OpenAPI snapshot updated and diff reviewed
- [ ] dbt manifest committed and dbt docs published
- [ ] README + CHANGELOG updated by Docs agent
- [ ] `gitleaks` scan clean (no secrets)
- [ ] Architect sign-off recorded in PR description

## Handoff template
Every cross-agent PR uses this body:

```markdown
## Handoff
- **From agent:** <role>
- **To agent(s):** <roles>
- **Contract(s) touched:** `contracts/<file>`
- **ADR (if any):** `docs/adr/000X-*.md`
- **Summary:** <1–3 sentences>
- **Breaking?:** yes/no
- **Action required by receiver:** <test the endpoint / run dbt / rebuild the page / …>
- **Checklist:**
  - [ ] Tests added/updated
  - [ ] Lint clean
  - [ ] `make pipeline` end-to-end
  - [ ] Docs agent notified
```

## Conflict resolution
1. Most-specific agent wins (Frontend beats Architect on a button colour).
2. Cross-cutting conflicts escalate to Architect.
3. If Architect is unavailable, the **most-blocked** agent proposes; the others vote within 24 h.

## Collaboration patterns
- **Vertical slice (default):** Architect issues a slice → Data Engineer exposes a mart → Backend wraps an endpoint → Frontend renders a chart → QA verifies → Docs publishes.
- **Contract-first:** Producer proposes a contract → Architect reviews → all consumers ack → implementation follows.

## Milestone evaluation protocol

Every milestone (M0–M8) follows the same four-phase cycle. **No milestone is considered complete until all four phases pass.**

### Phase 1 — Implement
The owning agent(s) produce the artefacts for the milestone. See `docs/IMPLEMENTATION_PLAN.md` for the deliverable list per milestone.

### Phase 2 — Evaluate & debug
After implementation, the **QA agent** performs an all-rounded evaluation:

1. **Structural check** — every file listed in the milestone deliverables exists and is non-empty.
2. **Contract check** — `make contracts-validate` passes; no drift between code and contracts.
3. **Lint** — `make lint` (ruff + mypy + eslint + tsc) is green.
4. **Unit tests** — `make test` (pytest + vitest) is green; coverage meets thresholds.
5. **Integration smoke** — where applicable, `make up-lite && make <milestone-command>` completes without error.
6. **Agent spec** — `make agents-lint` passes; every agent has 3 files.
7. **Security scan** — `gitleaks detect` on new files; no secrets committed.
8. **Cross-reference** — every contract referenced by an agent file actually exists; every `make` target referenced in an agent file exists in the Makefile.

If any check fails, the QA agent opens a bug-fix PR (label `bugfix/milestone-N`) with the fix. The owning agent reviews.

### Phase 3 — User test instructions
For every milestone, the QA agent publishes a **User test** section in `docs/milestones/MN-test.md` with:

- A numbered list of commands the user runs.
- Expected output / visual for each command.
- Pass/fail criteria (what to look for).
- Known limitations (what is not yet implemented).

The user verifies the milestone by following these instructions before the next milestone begins.

### Phase 4 — Improvements
After the user approves, the Architect and QA agents propose **improvements** (label `improvement/milestone-N`). These are non-blocking but documented in `docs/milestones/MN-improvements.md`. They are tackled opportunistically in later milestones or M8 polish.

### Gate rule
**M(N+1) does not start until the M(N) user test instructions have been executed and the user has confirmed the milestone.**
