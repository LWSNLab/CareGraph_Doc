# EPIC 3 — Public API Gateway ✅

> Low-latency REST API, auth, and scalable request handling. Roadmap Phase 3.
> ← [Backlog overview](../index.md) · [PRD](../../prd.md) · [API Specification](../../../api/openapi-spec.md)

| Story | Points | Priority | Status |
| :-- | :--: | :--: | :--: |
| [E3-S1 — Spatial radius endpoint](e3-s1-radius-endpoint.md) | 5 | High | ✅ Done (pending review) |
| [E3-S2 — Fuzzy search endpoint](e3-s2-fuzzy-search.md) | 5 | Medium | ✅ Done (pending review) |
| [E3-S3 — Entity lookup](e3-s3-entity-lookup.md) | 2 | High | ✅ Done (pending review) |
| [E3-S4 — Auth & rate limiting](e3-s4-auth-rate-limiting.md) | 5 | High | ✅ Done (pending review) |
| [E3-S5 — OpenAPI & docs](e3-s5-openapi-docs.md) | 2 | Medium | ✅ Done (pending review) |
| [E3-S6 — Uniform error contract & request correlation](e3-s6-error-contract.md) | 3 | Medium | ✅ Done (pending review) |

_Story points & priorities are initial drafts — adjust as needed._

## Current API state

| Endpoint | State |
| :-- | :-- |
| `GET /healthz` | ✅ live — liveness only, by design: a probe that failed on a database outage would make the orchestrator restart every replica |
| `GET /readyz` | ✅ live — probes Postgres, Redis and Typesense; `503` only when Postgres is down, `200 degraded` for the two the API survives without |
| `GET /openapi.yaml` | ✅ live — the contract this instance implements, unauthenticated, embedded in the binary |
| `GET /v1/infrastructure/near` | ✅ live — query p95 6.8 ms, HTTP p95 10.0 ms incl. auth, over 7,615 rows |
| `GET /v1/infrastructure/search` | ✅ live — typo- and umlaut-tolerant over 9,099 documents, 2–5 ms warm |
| `GET /v1/infrastructure/{ik_nummer}` | ✅ live — resolves 92 of 93 insurers; every provider is `404` until E1-S8 |
| `X-API-Key` | ✅ real authentication — Argon2id, 60 s verification cache; issue keys with `make apikey-dev` |
| Rate limiting | ✅ Redis token bucket — community 100/min, enterprise 6000/min, plus a 20/min failed-auth brake in front of Argon2id |
| Error contract | ✅ one JSON shape for every `4xx`/`5xx` incl. unknown routes, `405` and panics; stable `code` field; causes logged, never leaked |
| `X-Request-Id` | ✅ on every response, echoed from the client when safe, in error bodies and log records |
| Contract ↔ code | ✅ drift is a build failure — routes, `code` and `provider_type` enums, struct tags and real responses are all checked against `api/openapi.yaml` by `go test` |
