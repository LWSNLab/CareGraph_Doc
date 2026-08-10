# EPIC 3 — Public API Gateway 🚧

> Low-latency REST API, auth, and scalable request handling. Roadmap Phase 3.
> ← [Backlog overview](../index.md) · [PRD](../../prd.md) · [API Specification](../../../api/openapi-spec.md)

| Story | Points | Priority | Status |
| :-- | :--: | :--: | :--: |
| [E3-S1 — Spatial radius endpoint](e3-s1-radius-endpoint.md) | 5 | High | ✅ Done (pending review) |
| [E3-S2 — Fuzzy search endpoint](e3-s2-fuzzy-search.md) | 5 | Medium | ⏳ Planned |
| [E3-S3 — Entity lookup](e3-s3-entity-lookup.md) | 2 | High | ✅ Done (pending review) |
| [E3-S4 — Auth & rate limiting](e3-s4-auth-rate-limiting.md) | 5 | High | ⏳ Planned |
| [E3-S5 — OpenAPI & docs](e3-s5-openapi-docs.md) | 2 | Medium | ⏳ Planned |
| [E3-S6 — Uniform error contract & request correlation](e3-s6-error-contract.md) | 3 | Medium | ✅ Done (pending review) |

_Story points & priorities are initial drafts — adjust as needed._

## Current API state

| Endpoint | State |
| :-- | :-- |
| `GET /healthz` | ✅ live |
| `GET /v1/infrastructure/near` | ✅ live — query p95 6.8 ms, HTTP p95 9.1 ms over 7,614 rows |
| `GET /v1/infrastructure/search` | `501` until E3-S2 |
| `GET /v1/infrastructure/{ik_nummer}` | ✅ live — resolves 91 insurers; every provider is `404` until E1-S8 |
| `X-API-Key` | presence-only check until E3-S4 — **not** authentication |
| Error contract | ✅ one JSON shape for every `4xx`/`5xx` incl. unknown routes, `405` and panics; stable `code` field; causes logged, never leaked |
| `X-Request-Id` | ✅ on every response, echoed from the client when safe, in error bodies and log records |
