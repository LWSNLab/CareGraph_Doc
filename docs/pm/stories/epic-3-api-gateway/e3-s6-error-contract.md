# E3-S6 — Uniform error contract & request correlation

|                  |                        |
| :--------------- | :--------------------- |
| **Epic**         | E3 — Public API Gateway |
| **Story Points** | 3                      |
| **Priority**     | Medium                 |
| **Status**       | ✅ Done (pending review) |

> **Sequencing.** Pulled ahead of [E3-S4](e3-s4-auth-rate-limiting.md) despite the
> lower priority: E3-S4 introduces `401` and `429` bodies, and those should be
> written once, in the shape defined here, rather than written and then migrated.
> Priority describes importance; this is an ordering constraint.

> ← [Epic 3](index.md) · [Backlog](../index.md)

## User Story

As **Bea (B2B integrator)**, I want every failure to arrive in the same shape and
carry an identifier I can quote, so that I can handle errors programmatically and
report a problem precisely enough for someone to find it.

## Description

Handler-level error mapping landed with [E3-S1](e3-s1-radius-endpoint.md) and
[E3-S3](e3-s3-entity-lookup.md): causes are logged, driver detail never reaches
the client, and timeouts, client disconnects and genuine failures are told apart.
What is missing is everything *around* the handlers — the parts the router and
the framework answer on their own, plus the ability to correlate a client's
report with a log line.

**Verified gaps** (measured against the running service, 2026-08-10):

| Case | Today | Should be |
| :-- | :-- | :-- |
| Unknown route `GET /v1/nonsense` | `404` · `text/plain` · `404 page not found` | `404` · `application/json` · the error shape |
| Wrong method `POST /v1/infrastructure/near` | `404` · `text/plain` | `405` with an `Allow` header |
| Panic in a handler | `gin.Recovery()` writes an empty `500` body | logged, plus the error shape |
| Any response | no correlation id | `X-Request-Id`, echoed and logged |
| Error body | `{"error": "<prose>"}` only | stable machine-readable `code` alongside the prose |

The first two matter most: a client that parses every response as JSON gets a
parse failure instead of an error it can read. That is the sort of thing an
integrator hits in the first hour and remembers.

## Acceptance Criteria

- [x] Unknown routes and unsupported methods return the documented JSON error
      shape; method mismatch is `405` with `Allow`, not `404`.
- [x] A panic is logged with its stack and answered in the same error shape as
      every other `5xx` — never an empty body.
- [x] Every response carries `X-Request-Id`: taken from the request when the
      client supplies one, generated otherwise, echoed in the header, included
      in error bodies and attached to every log record for that request.
- [x] Error bodies carry a stable `code` (e.g. `invalid_parameter`, `not_found`,
      `timeout`, `internal`) next to the human-readable `error`.
- [x] A request-scoped timeout bounds the whole request, not just the single
      query that `queryTimeout` already covers.
- [x] `openapi.yaml` defines one shared `Error` schema, and every endpoint
      references it for `4xx`/`5xx`.

## Technical Notes

Implemented as a new package `internal/httpx`, wired in `cmd/api/main.go` ahead
of the route groups. `error` kept its meaning, so `code` and `request_id` are
purely additive and existing clients are unaffected.

**Middleware order is load-bearing.** `RequestID` runs first so everything
downstream — including the recovery handler — can label its output with the
correlation id. A panic that happens before the id is assigned would be the one
incident nobody can correlate.

**Client-supplied ids are untrusted.** They land in a response header *and* in
every log record for the request, which makes them a header-injection and
log-forging vector. Anything outside `[A-Za-z0-9._-]` or longer than 64 bytes is
**discarded in favour of a generated id**, not repaired — sanitising attacker
input by rewriting it invites the next bypass. `crypto/rand` for generation, so
ids cannot be guessed and replayed to pollute another request's trail.

**Two panic cases, not one.** If the headers are already flushed
(`c.Writer.Written()`), appending a JSON error body would produce a response
that is neither the success nor the failure — so the connection is cut instead.
A broken pipe is logged at DEBUG, not ERROR: the client is gone and nothing is
wrong with the service.

**The request timeout is cooperative, and that is deliberate.** It cancels the
request context, which stops everything that honours it — every database call
does. It cannot interrupt a handler that ignores its context. A hard cut would
mean writing a response from another goroutine while the handler may still be
writing its own, which is a worse failure than the gap it closes. Server-level
`WriteTimeout` is the backstop.

**Server-level timeouts were missing entirely.** `gin.Engine.Run()` builds an
`http.Server` with no timeouts at all, so a client could hold a connection open
by trickling a request forever. `cmd/api` now constructs the server explicitly
with `ReadHeaderTimeout`, `ReadTimeout`, `WriteTimeout` and `IdleTimeout`.

**Keep the prose useful.** The messages still name the offending parameter
(`parameter 'radius_km' must be greater than 0 and at most 100`). A `code` is for
branching, not a licence to make the message vaguer.

### Verified end to end

Against the running service with the database paused mid-request:

```json
{"error":"the query took too long, please retry","code":"timeout","request_id":"fehler-trace-7"}
```

and the matching log record:

```json
{"time":"2026-08-10T10:44:54Z","level":"ERROR","msg":"database query timed out",
 "service":"caregraph-api","request_id":"fehler-trace-7","method":"GET",
 "path":"/v1/infrastructure/near","query":"lat=52.52&lng=13.405",
 "error":"near query: context deadline exceeded"}
```

## Dependencies

- **Depends on:** E3-S1, E3-S3 (the handler-level mapping this builds on)
- **Blocks:** nothing, but it should land before the first external integrator
  is invited, because the error shape is the hardest thing to change afterwards.
- **Related:** [E3-S4](e3-s4-auth-rate-limiting.md) adds `401`/`429`, which must
  use the same shape; [E4-S3](../epic-4-operations/e4-s3-observability.md) covers
  health probes and metrics, not the HTTP error surface.

## Risks

- **Request ids from clients are untrusted input.** An echoed
  `X-Request-Id` must be length-capped and sanitised, or it becomes a log
  injection and response-header vector.
- **Over-standardising too early.** Codes are a public contract; a short honest
  list beats an invented taxonomy that has to be deprecated.

## Out of scope — deliberately

- **Graceful shutdown.** Now that the server is constructed explicitly it is a
  small addition, but draining in-flight requests on deploy is a deployment
  concern → [E4-S1](../epic-4-operations/e4-s1-containerization.md).
- **JSON logging for the Python pipelines.** They still use
  `logging.basicConfig` with a plaintext format, so the field schema settled here
  (`time`, `level`, `msg`, `service`, `request_id`, `error`) is not yet shared
  across producers → [E4-S3](../epic-4-operations/e4-s3-observability.md).
- **Where logs are collected.** Deciding between per-service streams and one
  aggregated file is a deployment decision and should not be made before the
  target platform is chosen → [E4-S1](../epic-4-operations/e4-s1-containerization.md).

## Definition of Done

- [x] Acceptance criteria fulfilled
- [x] Tests passing — 19 cases in `internal/httpx`, including 8 hostile
      request-id inputs and both panic paths; the provider suite still green
- [x] CI covers the new code — the existing Go job runs `go test ./...`, which
      now includes the new package
- [x] Documentation updated — shared `Error` schema in `openapi.yaml`, `405`/`500`
      added to both live endpoints, and a code table plus correlation section on
      the API page
- [ ] Code reviewed

## References

- [API Specification](../../../api/openapi-spec.md) · [Security & Privacy](../../../architecture/security.md)
