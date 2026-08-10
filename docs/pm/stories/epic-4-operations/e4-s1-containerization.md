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
- [ ] The ingestion image carries `ca-certificates`, so TLS verification against
      the OS trust store works (see the section below).
- [ ] **A database DSN without TLS is rejected outside local development.**
      `sslmode=disable` is the right default for `docker compose`, but a deployed
      service that is handed a DSN with TLS switched off — or omitted, which
      libpq treats as `prefer` — must refuse to start rather than connect in the
      clear. Applies wherever the DSN is read: `internal/infrastructure/config.go`
      and `pipelines/run_load.py`.
- [ ] **No credentials in default values.** `config.go` currently defaults to
      `postgres://caregraph:caregraph@localhost:5433/…`, which compiles a
      username and password into every built binary and image. Harmless against a
      throwaway local database, but it does not belong in a shipped artifact —
      and it is the value a misconfigured deployment would fall back to.

### Why this is *not* a `CAREGRAPH_ENV` story

Worth recording, because the question came up and the answer was not the obvious one.

The feared failure mode was "production starts with dev defaults and looks
healthy". It does not: `NewPostgresPool` pings with a 5 s timeout and `main`
calls `log.Fatalf` on failure, so a container without `DATABASE_URL` reaches for
`localhost:5433`, finds nothing, and crash-loops. That is loud, and an
orchestrator surfaces it immediately.

What genuinely remains is the four items above plus two that already belong
elsewhere — real API-key verification ([E3-S4](../epic-3-api-gateway/e3-s4-auth-rate-limiting.md))
and a `/healthz` that probes its dependencies ([E4-S3](e4-s3-observability.md)).
Introducing a named-environment switch to validate two values would be structure
without payoff. It becomes justified when QA arrives and there are real per-stage
differences to manage.

**Per-stage config files are deliberately not the plan.** Environment variables
stay the mechanism (12-factor). Committing `config/prod.yaml` or `.env.production`
invites secrets into the repository and drifts from what is actually deployed.

## Technical Notes

The compose stack + API Dockerfile are already scaffolded in the impl repo (infra services + an `app` profile). Remaining: an ingestion image and production-oriented image hardening.

### ⚠️ The ingestion image must carry `ca-certificates`

The pipelines verify TLS against the **OS trust store** rather than certifi
(`pipelines/common/trust.py` — see
[E1-S6](../epic-1-ingestion/e1-s6-ik-enrichment.md#resolved-the-sources-were-never-broken-2026-08-10)).
That means the base image has to have one. Debian/Ubuntu slim images and
`gcr.io/distroless/*` do; **Alpine does not** — `ca-certificates` is not installed
by default there, and an empty store would fail every outbound TLS call.

The code degrades loudly rather than silently: `use_system_trust_store()` counts
the CAs first and keeps certifi with a warning if the store is empty. So a wrong
base image costs the proxy-tolerance, not the whole pipeline. Still worth getting
right in the Dockerfile rather than relying on the fallback.

Nothing is at risk today: there is no Python image yet, and CI's `ubuntu-latest`
runner has a full store.

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
- **"Minimal base image" and "OS trust store" pull in opposite directions.** Alpine
  is the smallest option and the one that ships without `ca-certificates`. Picking
  it without installing them costs the pipelines their tolerance for TLS-inspecting
  proxies. The code degrades loudly rather than silently, so this is a papercut
  rather than an outage — but it is the kind that gets diagnosed as "the source is
  down".

## Definition of Done

- [ ] Acceptance criteria fulfilled
- [ ] Tests passing (unit + integration where relevant)
- [ ] CI covers the new code (pipeline extended if needed)
- [ ] Documentation updated
- [ ] Code reviewed

## References

- [System Overview](../../../architecture/system-overview.md)
