# E2-S1 — PostGIS schema & migrations

|                  |                          |
| :--------------- | :----------------------- |
| **Epic**         | E2 — Data Model & Search |
| **Story Points** | 3                        |
| **Priority**     | High                     |
| **Status**       | ✅ Done |

> ← [Epic 2](index.md) · [Backlog](../index.md)

## User Story

As a **developer**, I want the schema deployed via migrations, so that environments are reproducible.

## Description

Deploy and version CareGraph's PostGIS schema and indexes through a repeatable migration mechanism, so every environment (local, CI, production) converges to the same state.

## Acceptance Criteria

- [x] `care_infrastructure` + `bundeslaender` + junction + `zusatzbeitrag_historie` created.
- [x] GIST (spatial), GIN (JSONB), and compound indexes present.
- [x] Migration is idempotent and version-controlled.

## Technical Notes

**Completed as a by-product of [E1-S4](../epic-1-ingestion/e1-s4-loader.md)**, which could not load anything until the schema was real.

Three migrations exist: `0001_init` (tables, enum, indexes), `0002_loader_prerequisites` (nullable address columns, `source_id` upsert key) and `0003_least_privilege_roles`. `make migrate` applies them all in order, and CI runs the same sequence against a PostGIS service container — so the from-scratch path is exercised on every push, not just on a developer's first boot.

Verified in the running database: GIST on `location`, GIN on `details`, compound B-Tree on `(type, plz)`, plus unique indexes on `source_id` and `ik_nummer`.

## Dependencies

- **Depends on:** —
- **Blocks:** E1-S4 (loader needs tables), E3 (API reads from these tables)

## Risks

- PostGIS extension must be available in the target environment.

## Definition of Done

- [x] Acceptance criteria fulfilled
- [x] Tests passing (loader integration tests exercise the schema)
- [x] CI covers the new code (migrations applied against a PostGIS service container)
- [x] Documentation updated
- [x] Code reviewed

## References

- [Data Schema](../../../architecture/data-schema.md)
