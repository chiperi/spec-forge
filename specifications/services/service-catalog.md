# Service Catalog

A registry of services: who's who, who owns what, contracts and SLOs.
(Required for microservices; recommended for a hybrid.)

| Service | Owner (team) | API type | Contracts | SLO | Depends on |
|--------|-----------------|---------|-----------|-----|--------------|
| example-service | <team> | REST + events | openapi.yaml, asyncapi.yaml | 99.9% · p95<200ms | <deps> |

> Rules: each service — a separate deployment and version · database-per-service ·
> contract changes — backward-compatible, both teams aware.
