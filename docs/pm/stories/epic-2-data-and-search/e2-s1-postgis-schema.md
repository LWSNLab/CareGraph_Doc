# E2-S1 — PostGIS schema & migrations

|                  |                          |
| :--------------- | :----------------------- |
| **Epic**         | E2 — Data Model & Search |
| **Story Points** | 3                        |
| **Priority**     | High                     |
| **Status**       | ⏳ Planned               |

> ← [Epic 2](index.md) · [Backlog](../index.md)

## User Story

As a **developer**, I want the schema deployed via migrations, so that environments are reproducible.

## Description

Deploy and version CareGraph's PostGIS schema and indexes through a repeatable migration mechanism, so every environment (local, CI, production) converges to the same state.

## Acceptance Criteria

- [ ] `care_infrastructure` + `bundeslaender` + junction + `zusatzbeitrag_historie` created.
- [ ] GIST (spatial), GIN (JSONB), and compound indexes present.
- [ ] Migration is idempotent and version-controlled.

## Technical Notes

The initial DDL is already drafted (`db/migrations/0001_init.sql`, auto-applied via the Postgres image's `initdb.d`). This story adds an explicit migration runner and applies it in CI, rather than relying only on first-boot init.

## Dependencies

- **Depends on:** —
- **Blocks:** E1-S4 (loader needs tables), E3 (API reads from these tables)

## Risks

- PostGIS extension must be available in the target environment.

## Definition of Done

- [ ] Acceptance criteria fulfilled
- [ ] Tests passing (unit + integration where relevant)
- [ ] CI covers the new code (pipeline extended if needed)
- [ ] Documentation updated
- [ ] Code reviewed

## References

- [Data Schema](../../../architecture/data-schema.md)
