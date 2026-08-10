# E3-S3 — Entity lookup

|                  |                        |
| :--------------- | :--------------------- |
| **Epic**         | E3 — Public API Gateway |
| **Story Points** | 2                      |
| **Priority**     | High                   |
| **Status**       | ✅ Done (pending review) |

> ← [Epic 3](index.md) · [Backlog](../index.md)

## User Story

As **Bea (B2B integrator)**, I want `GET /infrastructure/{ik_nummer}`, so that I can resolve a known institution.

## Description

Fetch a single care-infrastructure entity by its official 9-digit Institutionskennzeichen.

## Acceptance Criteria

- [x] Returns the full entity, or `404` when not found.
- [x] IK-Nummer validated against `^[0-9]{9}$`.

## Technical Notes

Indexed lookup on the unique `care_infrastructure.ik_nummer`, implemented in
`internal/provider` alongside the radius search. Verified against the loaded
database: `100171007` → HEK, `999999999` → `404`, `10017100` → `400`.

**Malformed and unknown are different answers.** A wrong-length or non-numeric
IK is a client mistake (`400`) and never reaches the database; a well-formed IK
with no row is a legitimate negative result (`404`). Collapsing the two would
make a typo indistinguishable from a genuine miss.

**`^[0-9]{9}$`, not `^\d{9}$`.** Go's `\d` is Unicode-aware and matches
Devanagari and other non-ASCII digit ranges, which are not IK numbers. There is
a test for this.

**A missing row is `(nil, nil)`, not an error.** `pgx.ErrNoRows` is translated in
the repository, so absence never travels as a failure and cannot surface as a
`500`.

**Distance is absent by design.** A direct lookup has no reference point, so
`distance_km` is omitted rather than sent as `0` — which would read as "at your
location". The shared row scanner takes the distance as an optional extra
column, which is why `Near` and this lookup can share it.

## Error handling (extended in this story)

The repository error surface was tightened while this endpoint went in, since a
lookup is where a bad mapping shows up first:

- **A `5xx` cause is always logged and never returned.** Driver errors can carry
  the DSN, host, user and column names, so the client gets `internal error`;
  the cause goes to `slog` at ERROR with method, path and query. Previously a
  `500` was returned with the cause discarded — a status code and nothing else
  to go on. There is a test asserting both halves.
- **Timeouts are their own answer.** A `queryTimeout` (5 s) bounds each database
  round trip, and `context.DeadlineExceeded` maps to `504` rather than `500`,
  because it is retryable and points at the database, not the request. Without
  the timeout a stalled database holds requests open and keeps pool connections
  checked out until the pool is exhausted for everyone.
- **A client that hangs up is not a server error.** `context.Canceled` on an
  already-cancelled request context logs at DEBUG and answers `499`
  (nginx's "Client Closed Request"), so flaky mobile clients do not inflate the
  error rate.
- **Structured logging is wired up.** `cmd/api` installs a JSON `slog` handler
  on stderr, level via `CAREGRAPH_LOG_LEVEL`.

What is *not* covered here — unknown routes and wrong methods still answer
`text/plain`, panics still produce an empty body, and there is no request
correlation id — is specified in [E3-S6](e3-s6-error-contract.md).

## Dependencies

- **Depends on:** E1-S4 (data), E2-S1 (schema)
- **Blocks:** —

## Risks

- Entities without an IK-Nummer are not addressable via this endpoint (by design).
  **In practice that is 7,523 of 7,614 rows** — every Leistungserbringer plus
  EY BKK. The endpoint is therefore useful for 91 insurers today and only becomes
  broadly useful with [E1-S8](../epic-1-ingestion/e1-s8-provider-ik.md), which is
  waiting on a data-sharing reply. The coverage caveat is already stated in the
  published spec so this does not read as a bug.

## Definition of Done

- [x] Acceptance criteria fulfilled
- [x] Tests passing — 8 new unit cases (validation, 400/404/500/504/499 mapping,
      log-not-leak) plus 3 integration subtests against real PostGIS
- [x] CI covers the new code — the Go job already runs against a PostGIS service
      container, so the new integration tests run there too
- [x] Documentation updated — `openapi.yaml` gained the `400`, `401` and `504`
      responses this endpoint can actually return
- [ ] Code reviewed

## References

- [API Specification](../../../api/openapi-spec.md)
