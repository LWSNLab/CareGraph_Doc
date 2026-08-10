# E3-S6 — Uniform error contract & request correlation

|                  |                        |
| :--------------- | :--------------------- |
| **Epic**         | E3 — Public API Gateway |
| **Story Points** | 3                      |
| **Priority**     | Medium                 |
| **Status**       | ⏳ Planned             |

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

- [ ] Unknown routes and unsupported methods return the documented JSON error
      shape; method mismatch is `405` with `Allow`, not `404`.
- [ ] A panic is logged with its stack and answered in the same error shape as
      every other `5xx` — never an empty body.
- [ ] Every response carries `X-Request-Id`: taken from the request when the
      client supplies one, generated otherwise, echoed in the header, included
      in error bodies and attached to every log record for that request.
- [ ] Error bodies carry a stable `code` (e.g. `invalid_parameter`, `not_found`,
      `timeout`, `internal`) next to the human-readable `error`.
- [ ] A request-scoped timeout bounds the whole request, not just the single
      query that `queryTimeout` already covers.
- [ ] `openapi.yaml` defines one shared `Error` schema, and every endpoint
      references it for `4xx`/`5xx`.

## Technical Notes

Middleware in `internal/infrastructure` (or a new `internal/httpx`), applied in
`cmd/api/main.go` ahead of the route groups: `gin.NoRoute`, `gin.NoMethod` with
`HandleMethodNotAllowed = true`, a recovery handler that logs and writes the
contract shape, and a request-id middleware that puts the id into the
`slog.Logger` stored on the context.

**Do not break the existing shape.** `{"error": "<message>"}` is already
published in [openapi.yaml](../../../api/openapi-spec.md) and implemented. Adding
`code` and `request_id` is additive; renaming or removing `error` is not.

**Keep the prose useful.** The current messages name the offending parameter
(`parameter 'radius_km' must be greater than 0 and at most 100`). A `code` is
for branching, not a reason to make the message vaguer.

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

## Definition of Done

- [ ] Acceptance criteria fulfilled
- [ ] Tests passing (unit + integration where relevant)
- [ ] CI covers the new code (pipeline extended if needed)
- [ ] Documentation updated
- [ ] Code reviewed

## References

- [API Specification](../../../api/openapi-spec.md) · [Security & Privacy](../../../architecture/security.md)
