# E3-S3 — Entity lookup

|                  |                        |
| :--------------- | :--------------------- |
| **Epic**         | E3 — Public API Gateway |
| **Story Points** | 2                      |
| **Priority**     | High                   |
| **Status**       | ⏳ Planned             |

> ← [Epic 3](index.md) · [Backlog](../index.md)

## User Story

As **Bea (B2B integrator)**, I want `GET /infrastructure/{ik_nummer}`, so that I can resolve a known institution.

## Description

Fetch a single care-infrastructure entity by its official 9-digit Institutionskennzeichen.

## Acceptance Criteria

- [ ] Returns the full entity, or `404` when not found.
- [ ] IK-Nummer validated against `^[0-9]{9}$`.

## Technical Notes

Straightforward indexed lookup on `care_infrastructure.ik_nummer` (unique). Handler stubbed in `internal/provider`.

## Dependencies

- **Depends on:** E1-S4 (data), E2-S1 (schema)
- **Blocks:** —

## Risks

- Entities without an IK-Nummer are not addressable via this endpoint (by design).

## Definition of Done

- [ ] Acceptance criteria fulfilled
- [ ] Tests passing (unit + integration where relevant)
- [ ] Documentation updated
- [ ] Code reviewed

## References

- [API Specification](../../../api/openapi-spec.md)
