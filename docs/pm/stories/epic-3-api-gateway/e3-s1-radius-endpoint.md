# E3-S1 — Spatial radius endpoint

|                  |                        |
| :--------------- | :--------------------- |
| **Epic**         | E3 — Public API Gateway |
| **Story Points** | 5                      |
| **Priority**     | High                   |
| **Status**       | ⏳ Planned             |

> ← [Epic 3](index.md) · [Backlog](../index.md)

## User Story

As **Dana (app developer)**, I want `GET /infrastructure/near`, so that I can find providers around a location.

## Description

Return care providers within a radius of given coordinates, ordered by distance and optionally filtered by provider type.

## Acceptance Criteria

- [ ] Params `lat`, `lng`, `radius_km`, `type`, `limit` per the [OpenAPI spec](../../../api/openapi-spec.md).
- [ ] Backed by `ST_DWithin`, ordered by distance; p95 < 10 ms on indexed data.
- [ ] Validates coordinates → `400` on bad input.

## Technical Notes

Handler + repository already stubbed in the impl repo (`internal/provider`); this story implements the `ST_DWithin` query (reference: Data Schema §5) and wires it to the handler.

## Dependencies

- **Depends on:** E1-S4 (data), E2-S1 (schema + spatial index)
- **Blocks:** —

## Risks

- Missing/invalid geocodes reduce result quality — depends on E1-S3.

## Definition of Done

- [ ] Acceptance criteria fulfilled
- [ ] Tests passing (unit + integration where relevant)
- [ ] Documentation updated
- [ ] Code reviewed

## References

- [API Specification](../../../api/openapi-spec.md) · [Data Schema](../../../architecture/data-schema.md)
