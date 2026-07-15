# Threat Model (STRIDE)

## Scope & trust boundaries
<data-flow diagram; where the trust boundaries run>

## Assets
<what we protect: PII, funds, tokens, secrets>

## Threats (STRIDE)
| ID | Category | Threat | Mitigation | Status |
|----|-----------|---------|-----------|--------|
| T-001 | Spoofing | <identity spoofing> | <auth/mTLS> | open |
| T-002 | Tampering | <data tampering> | <signatures/validation> | open |
| T-003 | Repudiation | <denial of actions> | <audit log> | open |
| T-004 | Information disclosure | <leak> | <encryption/PII masking> | open |
| T-005 | Denial of Service | <overload> | <rate limit/autoscale> | open |
| T-006 | Elevation of privilege | <privilege escalation> | <RBAC/least privilege> | open |

## Data classification
<PII/PHI · retention · encryption at rest/in transit · right to erasure (GDPR)>
