# Service Catalog

A registry of services: who is who, who owns what, contracts and SLO.
(Required for microservices; desirable for a hybrid.)

| Service | Owner (team) | API type | Contracts | SLO | Depends on |
|--------|-----------------|---------|-----------|-----|--------------|
| example-service | <team> | REST + events | openapi.yaml, asyncapi.yaml | 99.9% · p95<200ms | <deps> |

> Rules: each service — its own deployment and version · database-per-service ·
> contract changes — backward-compatible, with both teams aware.
