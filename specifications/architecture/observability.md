# Observability & SLO

## Metrics
<RED (rate/errors/duration) for services; USE (utilization/saturation/errors) for resources>

## Logs
<structured (JSON); audit trail of significant events; NO PII in logs>

## Traces
<distributed tracing; end-to-end trace-id across services>

## SLO / SLA / error budget
| SLI | Target (SLO) | Window | Error budget |
|-----|------------|-------|--------------|
| availability | 99.9% | 30 days | ~43 min/month |
| latency p95 | < 200 ms | 30 days | — |

## Alerts & runbooks
<which alerts; a link to the runbook for each failure mode>
