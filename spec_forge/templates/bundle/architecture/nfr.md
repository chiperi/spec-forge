# Non-Functional Requirements (in numbers)

> Every NFR is measurable and testable. Not "fast", but "p95 < 200 ms".

| ID | Attribute | Target (measurable) | How we verify |
|----|---------|-------------------|----------------|
| NFR-001 | Latency | p95 < 200 ms | load test / FF-002 |
| NFR-002 | Availability | 99.9% / month | SLO monitor |
| NFR-003 | Throughput | ≥ 1000 rps | load test |
| NFR-004 | Security | 0 critical vulns | SAST/SCA gate |
| NFR-005 | Scalability | horizontal up to N instances | load test |
