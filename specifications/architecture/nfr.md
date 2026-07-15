# Non-Functional Requirements — spec-forge (in numbers)

> Every NFR is measurable and testable. For a CLI tool (not a service), the metrics are about determinism,
> portability and quality, not latency/throughput.

| ID | Attribute | Target (measurable) | How we verify |
|----|---------|-------------------|----------------|
| NFR-001 | Performance (scaffold) | deterministic `init` < 5 s on a typical project | timing test |
| NFR-002 | Portability | byte-for-byte identical output on ubuntu/macos/windows | golden test in CI matrix |
| NFR-003 | Determinism | identical inputs → identical output (without `now()`/random) | golden / repeat test |
| NFR-004 | Reliability | a repeat run is idempotent; blockers halt the gate | unit + e2e |
| NFR-005 | Extensibility | a new stack-profile / backend without core changes | contract test on interfaces |
| NFR-006 | Code quality | Ruff clean; core coverage ≥ 85% | quality-gates CI |
| NFR-007 | Security | 0 critical vulns; secrets are not logged or committed | SCA + secret-scan |
| NFR-008 | Observability | structured logs; `--verbose`; clear exit codes | e2e / manual |

> Links: NFR-001/002 ← spec NFR-001/002; NFR-002/003 ← SC-005; NFR-005 ← SC-004; NFR-006/007 ← quality gates.
