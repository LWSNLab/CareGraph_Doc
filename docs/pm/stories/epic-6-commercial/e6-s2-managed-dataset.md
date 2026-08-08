# E6-S2 — Managed dataset service

|                  |                       |
| :--------------- | :-------------------- |
| **Epic**         | E6 — Commercial / DaaS |
| **Story Points** | 8                     |
| **Priority**     | Low                   |
| **Status**       | ⏳ Planned            |

> ← [Epic 6](index.md) · [Backlog](../index.md)

## User Story

As **Bea**, I want a continuously maintained hosted dataset, so that I don't have to run ingestion myself.

## Description

Operate a managed, always-fresh, deduplicated and geocoded dataset with custom export formats and early access — the core value of the DaaS offering.

## Acceptance Criteria

- [ ] Live, deduplicated, geocoded dataset kept fresh on a schedule.
- [ ] Custom export formats and early dataset access for Enterprise.

## Technical Notes

Depends on the full ingestion pipeline (E1) running reliably on a schedule with monitoring (E4-S3). The paid product is operational value on top of open facts, not exclusive data rights — see [Data Sources & Licensing](../../../legal/data-licensing.md).

## Dependencies

- **Depends on:** E1 (full pipeline), E4-S3 (monitoring)
- **Blocks:** —

## Risks

- Operational cost of continuous maintenance; data-licensing compliance for redistribution.

## Definition of Done

- [ ] Acceptance criteria fulfilled
- [ ] Tests passing (unit + integration where relevant)
- [ ] CI covers the new code (pipeline extended if needed)
- [ ] Documentation updated
- [ ] Code reviewed

## References

- [Data Sources & Licensing](../../../legal/data-licensing.md)
