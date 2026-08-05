# E2-S3 — Data validation

|                  |                          |
| :--------------- | :----------------------- |
| **Epic**         | E2 — Data Model & Search |
| **Story Points** | 3                        |
| **Priority**     | Medium                   |
| **Status**       | ⏳ Planned               |

> ← [Epic 2](index.md) · [Backlog](../index.md)

## User Story

As a **data steward**, I want automated validation, so that bad records are caught before serving.

## Description

Run structural and semantic checks over ingested records and produce a report of anomalies, so quality issues surface before the data reaches the API.

## Acceptance Criteria

- [ ] Required-field and format checks (PLZ, IK-Nummer, coordinates).
- [ ] Anomaly report (e.g., missing geocode, out-of-range values).

## Technical Notes

Runs as a pipeline step after loading; can gate publication (fail the run on critical anomalies). Reuses provenance recorded during ingestion.

## Dependencies

- **Depends on:** E1-S4 (loaded data)
- **Blocks:** —

## Risks

- Overly strict rules could block legitimate but unusual records — keep thresholds tunable.

## Definition of Done

- [ ] Acceptance criteria fulfilled
- [ ] Tests passing (unit + integration where relevant)
- [ ] Documentation updated
- [ ] Code reviewed

## References

- [Data Schema](../../../architecture/data-schema.md)
