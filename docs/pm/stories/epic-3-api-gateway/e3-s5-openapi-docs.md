# E3-S5 — OpenAPI & docs

|                  |                        |
| :--------------- | :--------------------- |
| **Epic**         | E3 — Public API Gateway |
| **Story Points** | 2                      |
| **Priority**     | Medium                 |
| **Status**       | ⏳ Planned             |

> ← [Epic 3](index.md) · [Backlog](../index.md)

## User Story

As a **developer**, I want a versioned OpenAPI spec, so that I can generate clients and trust the contract.

## Description

Maintain `openapi.yaml` as the single source of truth for the API and publish versioned, human-readable docs derived from it.

## Acceptance Criteria

- [ ] `openapi.yaml` is the single source of truth; kept in sync with the Go handlers.
- [ ] Published, versioned API documentation.

## Technical Notes

The spec already exists (`docs/api/openapi.yaml`). Consider generating Go DTOs via `oapi-codegen` and/or asserting handler↔spec parity in CI to prevent drift.

## Dependencies

- **Depends on:** E3-S1…S4 (endpoints exist)
- **Blocks:** —

## Risks

- Spec/handler drift if not enforced in CI.

## Definition of Done

- [ ] Acceptance criteria fulfilled
- [ ] Tests passing (unit + integration where relevant)
- [ ] CI covers the new code (pipeline extended if needed)
- [ ] Documentation updated
- [ ] Code reviewed

## References

- [API Specification](../../../api/openapi-spec.md)
