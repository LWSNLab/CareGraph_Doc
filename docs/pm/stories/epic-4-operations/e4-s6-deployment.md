# E4-S6 — Deployment & continuous delivery

|                  |                       |
| :--------------- | :-------------------- |
| **Epic**         | E4 — Operations & CI/CD |
| **Story Points** | 3                     |
| **Priority**     | High                  |
| **Status**       | ✅ Done                |

> ← [Epic 4](index.md) · [Backlog](../index.md)

## User Story

As an **operator**, I want a merge into `main` to reach the server on its own, so
that releasing is a decision rather than a procedure.

## Description

[E4-S2](e4-s2-ci-cd.md) covers build, lint, test and the docs deploy. It stops at
the repository — nothing put the software on a machine. This story is the rest:
TLS termination, a release that produces images, and a server that picks them up.

## Acceptance Criteria

- [x] TLS in front of the API, with certificates obtained and renewed automatically.
- [x] A merge into `main` builds and publishes both images.
- [x] The server applies a new release without anyone logging in.
- [x] Database backup and restore.
- [x] A runbook a stranger can follow — [`deploy/README.md`](https://github.com/LWSNLab/CareGraph/blob/main/deploy/README.md).

## Pull, not push

GitHub Actions never connects to the server. The alternative — a workflow that
opens an SSH session — needs a key for the machine stored as a repository secret
and SSH reachable from GitHub's runner ranges, which are broad enough that a
firewall cannot meaningfully narrow them. A compromised workflow would then be a
shell on the host.

Instead CI pushes images to GHCR and a systemd timer on the server runs
`deploy/update.sh`: `git pull`, `compose pull`, `up -d`. No inbound port beyond
80/443, no server credentials at GitHub. The cost is up to ten minutes of delay,
which for a project that releases occasionally is not a cost.

Images carry two tags: `latest`, which the server follows, and `sha-<commit>`,
which is immutable — so a rollback names a specific build rather than "whatever
was there before".

## The proxy broke rate limiting, quietly

Putting anything in front of the API makes it see the proxy's address as the
peer. `SetTrustedProxies` was hardcoded to `nil`, so every client would have
shared **one** rate-limit bucket and **one** failed-authentication budget: a
single abusive client would have locked out everybody.

It is now `CAREGRAPH_TRUSTED_PROXIES`, and both directions are wrong in their own
way — trusting nobody behind a proxy causes the above, trusting too widely lets a
client forge `X-Forwarded-For` and slip the per-address budget. The compose
network has a fixed subnet so the setting can name exactly it.

Four tests cover it. Reverted to the old hardcoded `nil`, the decisive one
reports `ClientIP = "172.28.0.5"` instead of the real address.

## Defects found while building it

- **An active health check on a single upstream made everything 503.** Caddy's
  `health_uri /readyz` marks the one upstream unhealthy on a database outage, and
  then answers 503 for *every* path. Measured: `/healthz` and `/openapi.yaml`
  became 503 through Caddy while the API served both with 200 — flattening
  exactly the distinction [E4-S3](e4-s3-observability.md) built. Removed; with
  one upstream there is nothing to fail over to.
- **Compression silently did not apply.** Caddy's default content-type list omits
  `application/yaml`, so the 21 KB contract went out uncompressed. With an
  explicit match: 21,595 → 6,394 bytes.
- **The overlay removed the database port entirely**, which would have broken
  `make apikeys` on the server — the one routine operator task there. Now bound
  to loopback: unreachable from off the machine, available to tools on it.
- **The backup filename did not expand its timestamp.** Every run would have
  overwritten the same file, leaving exactly one backup instead of a history, and
  it would have surfaced only when a restore was needed.

## Backups matter more than they look

The release archive contains `providers.csv`. The `api_key` table is in no
archive, so a lost volume invalidates every key ever issued — for a hosted
instance that means every client breaks at once.

`make backup` dumps the whole database, `make restore` puts it back. Verified by
restoring into an empty database: 9,192 rows, 93 insurers, and **7 API keys, 3 of
them active**.

## What was deliberately left out

- **A secret manager.** `.env` at mode 0600 on one host. A managed store earns
  its complexity with several hosts.
- **Alerting.** The container healthcheck reports; it wakes nobody. That is the
  open half of [E4-S3](e4-s3-observability.md).
- **Staging.** One environment. A second earns its keep when a change is risky
  enough that production is the wrong place to find out, and the release
  acceptance test covers that ground more cheaply today.

## Untested until there is a server

**Certificate issuance.** Everything else was verified locally against Caddy's
internal CA — proxying, compression, the client address surviving to the rate
limiter, graceful shutdown, the loopback binding. ACME needs a public domain
resolving to the host, so it can only be confirmed on the first real deployment.

## Dependencies

- **Depends on:** [E4-S1](e4-s1-containerization.md) (images and compose)
- **Blocks:** —

## Risks

- The first release is also the first ACME run. Let's Encrypt rate-limits failed
  issuance, so DNS should resolve before the stack starts.
- ~~GHCR is free for public repositories. While the repository is private, the
  ingestion image alone would nearly fill the free package quota — another reason
  the first merge to `main` belongs after [E5-S1](../epic-5-open-source/e5-s1-repo-licensing.md).~~
  **Resolved**: the repository went public on 2026-08-25 and the first release
  followed. One thing the ordering did not anticipate — a *new* GHCR package is
  created private even under a public repository, so both had to be switched by
  hand before a server could pull them anonymously.

## Definition of Done

- [x] Acceptance criteria fulfilled
- [x] Tests passing — four proxy-trust tests, plus a verified backup round trip
- [x] CI covers the new code — `release.yml`; workflows validated
- [x] Documentation updated
- [ ] Code reviewed

## References

- [System Overview](../../../architecture/system-overview.md) · [Security & Privacy](../../../architecture/security.md)
