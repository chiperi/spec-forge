# Non-Functional Requirements (у числах)

> Кожен NFR — вимірюваний і тестований. Не «швидко», а «p95 < 200 мс».

| ID | Атрибут | Ціль (вимірювана) | Як перевіряємо |
|----|---------|-------------------|----------------|
| NFR-001 | Latency | p95 < 200 ms | load test / FF-002 |
| NFR-002 | Availability | 99.9% / міс | SLO monitor |
| NFR-003 | Throughput | ≥ 1000 rps | load test |
| NFR-004 | Security | 0 critical vulns | SAST/SCA gate |
| NFR-005 | Scalability | horizontal до N інстансів | load test |
