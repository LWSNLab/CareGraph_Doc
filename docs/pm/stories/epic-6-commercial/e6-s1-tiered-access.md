# E6-S1 — Tiered API access

|                  |                       |
| :--------------- | :-------------------- |
| **Epic**         | E6 — Commercial / DaaS |
| **Story Points** | 5                     |
| **Priority**     | Low                   |
| **Status**       | ⏳ Planned            |

> ← [Epic 6](index.md) · [Backlog](../index.md)

## User Story

As **Bea (B2B integrator)**, I want Community and Enterprise tiers, so that I can choose the right SLA.

## Description

Offer a free, rate-limited Community tier for open-source/research use and paid Enterprise tiers with higher throughput and support.

## Acceptance Criteria

- [ ] Self-service Community keys (rate-limited).
- [ ] Enterprise tier: higher throughput, dedicated keys, SLA.

## Technical Notes

Builds directly on E3-S4 (auth & rate limiting): tiers are rate-limit policies attached to keys. Billing/self-service signup is out of scope for the first iteration.

## Dependencies

- **Depends on:** E3-S4 (auth & rate limiting)
- **Blocks:** —

## Risks

- Pricing/tier design is a business decision, not just technical.

## Definition of Done

- [ ] Acceptance criteria fulfilled
- [ ] Tests passing (unit + integration where relevant)
- [ ] Documentation updated
- [ ] Code reviewed

## References

- [Open Source Strategy](../../open-source-strategy.md)
