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

**Two items handed over from [E3-S6](../epic-3-api-gateway/e3-s6-error-contract.md):**

1. **Graceful shutdown.** `cmd/api` now builds its `http.Server` explicitly (it
   needed the timeout settings), so adding signal handling and `srv.Shutdown` to
   drain in-flight requests on deploy is a small change — but it belongs to
   whatever supervises the process, which is this story.
2. **Where logs are collected — decide here, not earlier.** The API writes JSON
   to stderr and deliberately owns nothing beyond that. The open question is
   whether the target keeps per-service streams (`docker logs`, `journalctl -u`,
   each rotated and queryable on its own) or aggregates everything into one file.
   Per-service is the default recommendation: one file for several producers loses
   isolation and per-service retention, and a chatty pipeline run drowns the API.
   A single file only makes sense on a single host with no log stack, and then
   only because a `service` field is present in every record. **Writing an own
   supervisor process to capture children's stdout is explicitly not the plan** —
   restart policy, signal forwarding, zombie reaping and rotation are what
   systemd and Docker already do, and the pipelines are scheduled jobs rather
   than long-lived children of the API.

## Dependencies

- **Depends on:** —
- **Blocks:** E4-S2 (CI builds images)

## Risks

- Image bloat / slow builds — use multi-stage builds and minimal base images.

## Definition of Done

- [ ] Acceptance criteria fulfilled
- [ ] Tests passing (unit + integration where relevant)
- [ ] CI covers the new code (pipeline extended if needed)
- [ ] Documentation updated
- [ ] Code reviewed

## References

- [System Overview](../../../architecture/system-overview.md)
