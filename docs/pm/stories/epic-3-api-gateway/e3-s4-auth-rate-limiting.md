# E3-S4 — Auth & rate limiting

|                  |                        |
| :--------------- | :--------------------- |
| **Epic**         | E3 — Public API Gateway |
| **Story Points** | 5                      |
| **Priority**     | High                   |
| **Status**       | ⏳ Planned             |

> ← [Epic 3](index.md) · [Backlog](../index.md)

## User Story

As the **platform operator**, I want API-key auth with tiered rate limits, so that usage is controlled and abuse is prevented.

## Description

Authenticate requests via an API key and enforce per-tier request quotas, protecting the service from scraping and denial-of-service.

## Acceptance Criteria

- [ ] `X-API-Key` verified against Argon2id hashes; missing/invalid → `401`.
- [ ] Redis token-bucket limits per tier; exceed → `429`.

## Technical Notes

Middleware stubbed in `internal/auth`; needs the hashed-key store (Postgres) and a Redis-backed limiter. See [Security §2](../../../architecture/security.md).

## Dependencies

- **Depends on:** E2-S1 (key store table), Redis available
- **Blocks:** E6-S1 (tiered access builds on this)

## Risks

- Key leakage — enforce hashing at rest and TLS in transit.

## Definition of Done

- [ ] Acceptance criteria fulfilled
- [ ] Tests passing (unit + integration where relevant)
- [ ] CI covers the new code (pipeline extended if needed)
- [ ] Documentation updated
- [ ] Code reviewed

## References

- [Security & Privacy](../../../architecture/security.md)
