# E1-S4 — CareGraph-native loader

|                  |                          |
| :--------------- | :----------------------- |
| **Epic**         | E1 — Ingestion & ETL     |
| **Story Points** | 5                        |
| **Priority**     | High                     |
| **Status**       | ⏳ Planned               |

> ← [Epic 1](index.md) · [Backlog](../index.md)

## User Story

As a **data engineer**, I want the enriched dataset loaded into `care_infrastructure`, so that it feeds the API instead of standalone files.

## Description

Replace the prototype file exporter with a loader that writes into CareGraph's unified schema: insurers become `care_infrastructure` rows (`type='krankenkasse'`), regional availability goes into `krankenkasse_bundesland`, and contribution rates are appended to `zusatzbeitrag_historie`.

## Acceptance Criteria

- [ ] Insurers mapped to `care_infrastructure` (`type='krankenkasse'`) + `krankenkasse_bundesland`.
- [ ] Contribution rates written to `zusatzbeitrag_historie` (append, no overwrite).
- [ ] Idempotent upsert keyed on IK-Nummer / a stable key.
- [ ] Runs against Postgres via a write-scoped role.

## Technical Notes

Under `pipelines/load/`. The current exporter targets a standalone `krankenkassen` schema — this story maps it onto `care_infrastructure` and moves from generated SQL files to a direct Postgres load (`psycopg`).

## Dependencies

- **Depends on:** E1-S1 (parsed dataset), E1-S3 (geocoded `location`), E2-S1 (schema deployed)
- **Blocks:** E3 (API serves from `care_infrastructure`)

## Risks

- Stable business key: name changes across yearly lists could fragment upserts — prefer IK-Nummer.

## Definition of Done

- [ ] Acceptance criteria fulfilled
- [ ] Tests passing (unit + integration where relevant)
- [ ] CI covers the new code (pipeline extended if needed)
- [ ] Documentation updated
- [ ] Code reviewed

## References

- [Data Schema](../../../architecture/data-schema.md)
