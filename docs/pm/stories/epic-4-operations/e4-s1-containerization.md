# E4-S1 — Containerization

|                  |                       |
| :--------------- | :-------------------- |
| **Epic**         | E4 — Operations & CI/CD |
| **Story Points** | 3                     |
| **Priority**     | Medium                |
| **Status**       | ⏳ Planned            |

> ← [Epic 4](index.md) · [Backlog](../index.md)

## User Story

As an **operator**, I want all components dockerized, so that the stack runs reproducibly anywhere.

## Description

Package every component and provide a one-command local stack, so contributors and deployments get an identical environment.

## Acceptance Criteria

- [ ] Images for Go API, Python ingestion, Postgres/PostGIS, Typesense, Redis.
- [ ] `docker compose` brings up the full local stack.

## Technical Notes

The compose stack + API Dockerfile are already scaffolded in the impl repo (infra services + an `app` profile). Remaining: an ingestion image and production-oriented image hardening.

## Dependencies

- **Depends on:** —
- **Blocks:** E4-S2 (CI builds images)

## Risks

- Image bloat / slow builds — use multi-stage builds and minimal base images.

## Definition of Done

- [ ] Acceptance criteria fulfilled
- [ ] Tests passing (unit + integration where relevant)
- [ ] Documentation updated
- [ ] Code reviewed

## References

- [System Overview](../../../architecture/system-overview.md)
