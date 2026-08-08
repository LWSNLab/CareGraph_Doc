# E2-S2 — Typesense sync worker

|                  |                          |
| :--------------- | :----------------------- |
| **Epic**         | E2 — Data Model & Search |
| **Story Points** | 5                        |
| **Priority**     | Medium                   |
| **Status**       | ⏳ Planned               |

> ← [Epic 2](index.md) · [Backlog](../index.md)

## User Story

As a **developer**, I want Postgres data synced into Typesense, so that search stays current.

## Description

Keep the Typesense in-memory index in sync with the `care_infrastructure` source of truth, so fuzzy search reflects the latest data.

## Acceptance Criteria

- [ ] Scheduled or near-real-time sync from Postgres → Typesense.
- [ ] German-language config, typo tolerance, and ranking tuned.
- [ ] Re-sync is safe to re-run (idempotent).

## Technical Notes

Typesense is the C++ search engine running as its own service; this worker only feeds it. A full re-index must be safe; consider incremental sync keyed on `updated_at`.

## Dependencies

- **Depends on:** E2-S1 (schema), E1-S4 (data loaded)
- **Blocks:** E3-S2 (fuzzy search endpoint)

## Risks

- Index/DB drift if sync fails silently — needs monitoring (see E4-S3).

## Definition of Done

- [ ] Acceptance criteria fulfilled
- [ ] Tests passing (unit + integration where relevant)
- [ ] CI covers the new code (pipeline extended if needed)
- [ ] Documentation updated
- [ ] Code reviewed

## References

- [System Overview](../../../architecture/system-overview.md)
