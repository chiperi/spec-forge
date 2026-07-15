# Architecture Fitness Functions

Executable checks of architectural characteristics in CI (Neal Ford).
Governance = code in the pipeline, not a manual review.

| ID | Characteristic | Check | Type | Where |
|----|----------------|-----------|-----|----|
| FF-001 | Modularity | module A does not import internals of module B | atomic/triggered | CI (arch test) |
| FF-002 | Performance | p95 latency < NFR-001 | holistic/continual | load test in the pipeline |
| FF-003 | Dependencies | no forbidden/circular dependencies | atomic | CI |
| FF-004 | Security | no critical vuln in dependencies | atomic | CI (SCA) |
