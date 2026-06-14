# SRE — contracts

## Consumes
| Artefact | From | Used for |
|---|---|---|
| `contracts/event-catalog.md` | Data Engineer + Backend | Metric / log fields |
| All service code | All agents | Healthcheck design |
| Alert rules in dashboards | Self | Runbook links |

## Produces
| Artefact | Consumed by | Format |
|---|---|---|
| `observability/prometheus/prometheus.yml` | Prometheus | YAML |
| `observability/grafana/dashboards/*.json` | Grafana | JSON |
| `observability/prometheus/rules/*.rules.yml` | Prometheus | YAML |
| `docs/runbook.md` | All | Markdown |
| `docker-compose.yaml` healthchecks | SRE, All | YAML |
| OpenLineage receiver | Marquez | HTTP |

## Handoff: SRE → All
On new alert rule:

```markdown
## Handoff
- **From agent:** sre
- **To agent(s):** all
- **Contract(s) touched:** `observability/prometheus/rules/*.rules.yml`
- **ADR (if any):** `docs/adr/000X-*.md`
- **Summary:** New alert `PipelineDown` fires if `airflow_dag_run_failed_total` > 0 for 5 m.
- **Action required by receiver:** see `docs/runbook.md#pipeline-down`.
```

## Handoff: SRE → Docs
On new dashboard: provide a screenshot and a one-paragraph "what to look at" blurb.
