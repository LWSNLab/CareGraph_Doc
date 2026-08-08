# E4-S3 — Observability

|                  |                       |
| :--------------- | :-------------------- |
| **Epic**         | E4 — Operations & CI/CD |
| **Story Points** | 3                     |
| **Priority**     | Low                   |
| **Status**       | ⏳ Planned            |

> ← [Epic 4](index.md) · [Backlog](../index.md)

## User Story

As an **operator**, I want health checks and metrics, so that I can monitor the service and catch failures early.

## Description

Expose service health and track ingestion-run status, so operational problems are visible and alertable.

## Acceptance Criteria

- [ ] `/healthz` reports DB/Redis/Typesense status.
- [ ] Ingestion run status is tracked and alertable.

## Technical Notes

`/healthz` handler is stubbed (returns `ok`); extend it to probe dependencies. Ingestion runs should persist a status record and emit alerts on failure.

## Dependencies

- **Depends on:** E1 (ingestion), E3-S1…S4 (API running)
- **Blocks:** —

## Risks

- Health checks that are too shallow give false confidence.

## Definition of Done

- [ ] Acceptance criteria fulfilled
- [ ] Tests passing (unit + integration where relevant)
- [ ] CI covers the new code (pipeline extended if needed)
- [ ] Documentation updated
- [ ] Code reviewed

## References

- [Security & Privacy](../../../architecture/security.md)
