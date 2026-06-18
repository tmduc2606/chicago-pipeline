# Gate Results — 2026-06-18T03:26:41Z

| Gate | Status | Details | Severity |
|------|--------|---------|----------|
| api lint (ruff) | PASS | ruff check passed |  |
| api lint (mypy) | PASS | mypy check passed |  |
| api test | PASS | pytest |  |
| contracts validate | PASS | contracts valid |  |
| agents lint | PASS | agent files present |  |
| GE bronze | PASS | validation passed |  |
| dbt test | PASS | dbt tests passed |  |
| GE silver | PASS | validation passed |  |
| GE bronze | PASS | validation passed |  |
| GE gold | PASS | validation passed |  |
| gitleaks detect | PASS | 0 secrets |  |
| GE silver | PASS | validation passed |  |
| GE gold | PASS | validation passed |  |
| gitleaks detect | PASS | 0 secrets |  |
| playwright e2e | FAIL | see evidence/e2e/e2e.txt | S1 |
| MISTAKE-001: ::date cast | PASS | 0 violations |  |
| MISTAKE-002: hardcoded coords | PASS | 0 violations |  |
| MISTAKE-005: ErrorBoundary | FAIL | 2 pages lack ErrorBoundary | S2 |
| MISTAKE-008: param names | PASS | filtersToParams converts from→from_date, to→to_date |  |
