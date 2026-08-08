# E3-S2 — Fuzzy search endpoint

|                  |                        |
| :--------------- | :--------------------- |
| **Epic**         | E3 — Public API Gateway |
| **Story Points** | 5                      |
| **Priority**     | Medium                 |
| **Status**       | ⏳ Planned             |

> ← [Epic 3](index.md) · [Backlog](../index.md)

## User Story

As **Dana**, I want `GET /infrastructure/search`, so that users find providers despite typos.

## Description

Typo-tolerant full-text search over provider names, cities and services, optionally filtered by city, powered by the Typesense engine.

## Acceptance Criteria

- [ ] Typo-tolerant query via Typesense; optional `city` filter.
- [ ] `q` shorter than 2 characters → `400`.

## Technical Notes

Uses the Go Typesense client (`internal/search`) against the synced index; result IDs are hydrated from Postgres or returned directly from the index document.

## Dependencies

- **Depends on:** E2-S2 (Typesense sync)
- **Blocks:** —

## Risks

- Ranking quality needs tuning for German names/abbreviations.

## Definition of Done

- [ ] Acceptance criteria fulfilled
- [ ] Tests passing (unit + integration where relevant)
- [ ] CI covers the new code (pipeline extended if needed)
- [ ] Documentation updated
- [ ] Code reviewed

## References

- [API Specification](../../../api/openapi-spec.md)
