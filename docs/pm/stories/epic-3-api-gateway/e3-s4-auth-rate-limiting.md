# E3-S4 — Auth & rate limiting

|                  |                        |
| :--------------- | :--------------------- |
| **Epic**         | E3 — Public API Gateway |
| **Story Points** | 5                      |
| **Priority**     | High                   |
| **Status**       | ✅ Done (pending review) |

> ← [Epic 3](index.md) · [Backlog](../index.md)

## User Story

As the **platform operator**, I want API-key auth with tiered rate limits, so that usage is controlled and abuse is prevented.

## Description

Authenticate requests via an API key and enforce per-tier request quotas, protecting the service from scraping and denial-of-service.

## Acceptance Criteria

- [x] `X-API-Key` verified against Argon2id hashes; missing/invalid → `401`.
- [x] Redis token-bucket limits per tier; exceed → `429`.

## Technical Notes

`internal/auth` (key format, store, middleware), `internal/ratelimit` (token
bucket), `cmd/apikey` (issue/list/revoke), migration `0006_api_keys.sql`.

### The key is two halves, because Argon2id cannot be a lookup

```
cg_<key_id>_<secret>
cg_337427fa47e2ab17_a1b2…                      (16 hex + 64 hex)
```

Argon2id is slow on purpose, and its per-key salt rules out indexing the hash —
so the presented key cannot be hashed against every stored row. `key_id` is a
public, indexed identifier that selects exactly one row; only that row's hash is
then verified. **One indexed lookup plus one verification, no matter how many
keys exist.** The `cg_` prefix exists so secret scanners can recognise a leaked
key.

Consequence: `key_id` is not a secret and may appear in logs. The secret half
never reaches the database in plaintext and is printed exactly once, by
`cmd/apikey issue`.

### Argon2id had to be kept off the hot path

At RFC 9106's 64 MiB / t=3 setting a verification costs **35–64 ms** — measured,
and enough to dominate the endpoint's 9 ms p95 several times over. A weaker KDF
was not the answer; a short-lived cache was. After a successful verification the
result is held for **60 seconds**, indexed by `sha256(presented key)` rather than
the key itself so a heap dump hands out nothing usable.

The price is stated plainly: **a revoked key keeps working for up to a minute.**
`cmd/apikey revoke` says so when it runs.

Measured effect: first request 258 ms (cold pool + Argon2id), subsequent
requests **8.3 ms p50 / 10.0 ms p95** — the same range as before authentication
existed.

### The middleware order is a security property

```
GuardAuthAttempts → APIKeyMiddleware → RateLimitByKey
```

**`GuardAuthAttempts` is not a quota.** It is the brake on Argon2id: anyone who
learns a valid `key_id` could otherwise saturate a core by replaying it with
varying wrong secrets. It allows **20 failed authentications per client address
per minute**, and — the important part — **charges nothing on success**, so
legitimate traffic never touches it.

That distinction was learned the hard way. The first version enforced the
community rate (100/min) per IP before authentication, which **silently capped an
enterprise key at 100 req/min instead of its 6000**: a pre-auth check cannot know
the tier yet, so it must not enforce a quota. Raising the pre-auth limit to cover
the highest tier would have removed the protection it existed for. Charging only
failures resolves both.

Verified: an enterprise key completes 150/150 requests with
`X-RateLimit-Limit: 6000`; a community key gets 101 through and then `429`.
Twenty wrong secrets cost 35–64 ms each, the twenty-first costs **0.5 ms** —
Argon2id ran 20 times instead of 40.

### A token bucket, not a counter

A Lua script, so the read-modify-write is atomic. A fixed window would let a
client spend its whole quota at the end of one window and again at the start of
the next — 200 requests in a couple of seconds under a "100 per minute" limit.

### Deliberate decisions worth arguing with

- **The limiter fails open.** If Redis is unreachable the request proceeds and an
  ERROR is logged. The limiter curbs abuse; making it a hard dependency of every
  request would turn a cache outage into a total outage. Reachability is reported
  once at startup, because a fail-open limiter is otherwise invisible when it is
  not working.
- **`401` is identical for every rejection reason.** Distinguishing "no such key
  id" from "wrong secret" would tell an attacker which ids exist.
- **A store failure is `500`, not `401`.** A database outage is ours; answering
  `401` would send a client chasing its own credentials.
- **No proxy headers are trusted** (`SetTrustedProxies(nil)`). With
  `X-Forwarded-For` trusted, anyone could spoof it and walk around the per-client
  failed-auth budget. A deployment behind a load balancer must set this to that
  balancer's address and nothing else.
- **Key issuance lives outside the gateway.** `caregraph_api` has `SELECT` on
  `api_key` and nothing more, so a compromised gateway cannot mint itself a key
  or erase an audit trail. `cmd/apikey` connects as the owner.
- **Revocation is a timestamp, not a `DELETE`.** Which key was valid when is
  exactly what an incident review needs.

### Security headers

Also from [Security §2](../../../architecture/security.md): `nosniff`,
`Content-Security-Policy: default-src 'none'`, `Referrer-Policy: no-referrer`, and
HSTS **only when the request actually arrived over TLS** — asserting it on a
plaintext request is ignored by clients anyway and only muddies whether TLS is in
play.

## Dependencies

- **Depends on:** E2-S1 (key store table), Redis available
- **Blocks:** E6-S1 (tiered access builds on this)

## Operating it

```bash
make apikey-dev      # issue a local key (printed once)
make apikeys         # list keys and their state
go run ./cmd/apikey revoke --key-id <id>
```

`cmd/apikey` defaults to `$ADMIN_DATABASE_URL`. `--name` is required on issue: an
unattributable key cannot be revoked with confidence.

## Risks

- Key leakage — hashed at rest, `cg_` prefix so scanners can spot a leak, and
  revocation is one command. TLS in transit is [E4-S1](../epic-4-operations/e4-s1-containerization.md).
- **The 60-second verification cache bounds how fast a revocation takes effect.**
  Acceptable for a quota key; it would not be for anything authorising a write.
- **Redis is bound to loopback in `docker-compose.yml`** because it runs without
  a password. Publishing it on `0.0.0.0` would hand the rate-limit state to
  anyone on the local network. A deployment needs `requirepass` or network
  isolation.

## Out of scope

- **Key usage tracking.** A `last_used_at` column was considered and left out:
  writing it on every request would put a write on the read path and break the
  read-only `caregraph_api` role that migration `0003` deliberately established.
  It belongs with quotas in [E6-S1](../epic-6-commercial/e6-s1-tiered-access.md).
- **Per-endpoint limits.** One bucket per key today, which is what the tiers describe.

## Definition of Done

- [x] Acceptance criteria fulfilled
- [x] Tests passing — 18 unit cases in `internal/auth` (key format, hash
      parameters, indistinguishable rejections, no secret in logs) plus 8
      integration tests in `internal/ratelimit` against real Redis
- [x] CI covers the new code — the Go job gained a Redis service, so the Lua
      token bucket is exercised instead of skipped
- [x] Documentation updated
- [ ] Code reviewed

## References

- [Security & Privacy](../../../architecture/security.md)
