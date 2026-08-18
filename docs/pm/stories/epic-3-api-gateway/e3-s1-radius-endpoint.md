# E3-S1 — Spatial radius endpoint

|                  |                        |
| :--------------- | :--------------------- |
| **Epic**         | E3 — Public API Gateway |
| **Story Points** | 5                      |
| **Priority**     | High                   |
| **Status**       | ✅ Done |

> ← [Epic 3](index.md) · [Backlog](../index.md)

## User Story

As **Dana (app developer)**, I want `GET /infrastructure/near`, so that I can find providers around a location.

## Description

Return care providers within a radius of given coordinates, ordered by distance and optionally filtered by provider type.

## Acceptance Criteria

- [x] Params `lat`, `lng`, `radius_km`, `type`, `limit` per the [OpenAPI spec](../../../api/openapi-spec.md).
- [x] Backed by `ST_DWithin`, ordered by distance; p95 < 10 ms on indexed data.
- [x] Validates coordinates → `400` on bad input.

## Technical Notes

Implemented in `internal/provider`: `params.go` (validation), `repository.go`
(the PostGIS query), `handler.go` (transport).

**Measured performance** against the loaded database as it stood then (7,614
rows; 7,615 since the merged-insurer fix), dev machine, database in Docker:

| Layer | p50 | p95 | Method |
| :-- | --: | --: | :-- |
| SQL query | 2.9 ms | **6.8 ms** | 800 samples, 4 cities, 10 km, limit 20 |
| HTTP, connection reused | 7.9 ms | **9.1 ms** | 300 samples, keep-alive, 9.7 KB body |
| HTTP, new connection each time | — | 11.6 ms | 20 samples, fresh `curl` per request |

The acceptance criterion is met at the query layer and over a reused
connection. The third row is above 10 ms, and it is recorded here rather than
dropped: the extra ~2.5 ms is TCP setup and client process spawn, not the
query — but a client that opens a fresh connection per call will see it.

`EXPLAIN ANALYZE` confirms a Bitmap Index Scan on `idx_care_infra_location`.
The *first* query in a fresh backend costs ~100 ms because PostGIS is loaded
into the process on demand — worth knowing before someone reads a cold
measurement as a regression.

**Validation rejects rather than falls back.** An unparseable optional
parameter is a `400`, not a silent default: turning `radius_km=abc` into 10 km
returns results that look authoritative while answering a different question.
`NaN` and `Inf` are rejected explicitly — `ParseFloat` accepts both, and every
range check against `NaN` evaluates false, so without a guard they reach
PostGIS as coordinates.

**Distance is rounded to metres.** The raw value carries eleven decimal places;
publishing it would advertise sub-nanometre accuracy for coordinates good to
about ten metres.

**The repository port takes a `NearParams` struct** rather than five positional
arguments. Transposing `lat` and `lng` stays syntactically valid and surfaces
only as wrong results, which is the single most common defect in this kind of
endpoint.

Rows with a `NULL` location are excluded — relevant because all 93 insurers
have no coordinates by design (see [E1-S3](../epic-1-ingestion/e1-s3-geocoding.md)),
so `type=krankenkasse` correctly returns an empty set here.

## Out of Scope

_Both have since been delivered; kept to record what this story did and did not
cover._

- **`GET /infrastructure/:ik_nummer`** returned `501` when this story landed —
  that was [E3-S3](e3-s3-entity-lookup.md), which reused the row-scanning helper
  built here. ✅ done.
- **Real API-key verification and rate limiting** were left to
  [E3-S4](e3-s4-auth-rate-limiting.md); at the time the middleware only checked
  that a key was present. ✅ done.

## Dependencies

- **Depends on:** E1-S4 (data), E2-S1 (schema + spatial index)
- **Blocks:** —

## Risks

- Missing/invalid geocodes reduce result quality — depends on E1-S3.

## Definition of Done

- [x] Acceptance criteria fulfilled
- [x] Tests passing (unit + integration where relevant) — 33 unit cases plus 8
      integration subtests against real PostGIS
- [x] CI covers the new code — the Go job gained a PostGIS service container and
      applies the migrations, so the integration tests actually run instead of
      skipping
- [x] Documentation updated — `openapi.yaml` now carries the bounds the code
      enforces (`lat` ±90, `lng` ±180, `radius_km` 0 < r ≤ 100, `limit` 1–100)
- [x] Code reviewed

## References

- [API Specification](../../../api/openapi-spec.md) · [Data Schema](../../../architecture/data-schema.md)
