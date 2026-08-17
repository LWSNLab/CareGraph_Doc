# E3-S5 — OpenAPI & docs

|                  |                        |
| :--------------- | :--------------------- |
| **Epic**         | E3 — Public API Gateway |
| **Story Points** | 2                      |
| **Priority**     | Medium                 |
| **Status**       | ✅ Done (pending review) |

> ← [Epic 3](index.md) · [Backlog](../index.md)

## User Story

As a **developer**, I want a versioned OpenAPI spec, so that I can generate clients and trust the contract.

## Description

Maintain `openapi.yaml` as the single source of truth for the API and publish
versioned, human-readable docs derived from it.

The word doing the work is **trust**. A specification that merely exists is easy;
one a stranger can generate a client from without reading the Go code is a
different thing, and the only difference between them is whether anything stops
the two from drifting apart.

## Acceptance Criteria

- [x] `openapi.yaml` is the single source of truth; kept in sync with the Go handlers.
- [x] Published, versioned API documentation.

## Implementation

### The spec moved into the implementation repository

`api/openapi.yaml`, embedded with `go:embed`. The copy in this repository was
**deleted**, not synchronised — two copies of a contract are two contracts, and
the one that can be tested against the handlers is the one that should survive.

Being in the same module is what makes the rest possible: a single test process
can see both the document and the route table.

### The spec is served

`GET /openapi.yaml`, unauthenticated, byte-identical to the embedded document. A
deployment therefore hands out the contract it actually implements, rather than
leaving a client to trust that a published copy matches. Requiring a key would
be circular — you would need the contract to know how to ask for one.

### Drift is a build failure, not a review comment

Three test files, nine tests, 22 table cases:

| File | What it holds to the document |
| :-- | :-- |
| `api/spec_test.go` | The document is valid 3.0; every served route is documented and every documented route is served; the `code` and `provider_type` enums match the Go constants |
| `api/schema_test.go` | Struct tags versus schema properties and `required` lists, both directions |
| `api/contract_test.go` | Real responses from the real router validated against the schemas; the framework's own `404`/`405` against the `Error` schema |

The enum checks read the constants **out of the Go source with `go/ast`** rather
than from a list in the test. A hand-kept list in a test drifts exactly like the
document it is meant to guard — that is how `unavailable` reached the API before
it reached the spec in E3-S2.

### The guards were checked by breaking things

Twelve deliberate mutations, each reverted afterwards:

| # | Mutation | Caught |
| :-: | :-- | :-: |
| 1 | Route served, not documented | ✅ |
| 2 | Route documented, not served | ✅ |
| 3 | New Go `ErrorCode` constant | ✅ |
| 4 | Enum value with no Go constant | ✅ |
| 5 | New `provider.Type` | ✅ |
| 6 | JSON field renamed | ✅ |
| 7 | `omitempty` on a required field | ❌ → ✅ |
| 8 | Handler returns an undocumented status | ✅ |
| 9 | Spec drops a field from `required` | ❌ → ✅ |
| 10 | Error body loses `code` | ❌ → ✅ |
| 11 | New Go field, undocumented | ✅ |
| 12 | Documented property with no Go field | ✅ |

**Three initially passed.** Validating example responses only catches what the
fixtures happen to trigger: giving `name` an `omitempty` stayed green because
every fixture set a name — the field would have vanished only for thin records,
which are the ones nobody checks by hand. `api/schema_test.go` was written in
response, comparing struct tags with the schema structurally rather than through
sample data.

## Defects found and fixed

- **`/healthz` was documented at the wrong URL.** The spec put `/v1` in the
  server URL, so the probe — served at the origin — was described as
  `/v1/healthz`. A generated client would have called a 404. Fixed by moving
  `/v1` into the paths, which also makes each path map 1:1 onto a Gin route.
- **The document claimed OpenAPI 3.1 while using 3.0 keywords.** `nullable` and
  boolean `exclusiveMinimum` were both removed in 3.1. Nothing fails loudly —
  generators drop what they do not recognise, so a client would have treated
  optional fields as mandatory. Now declared `3.0.3`, which is what it is.
- **The docs said `ik_nummer` is `null` for care providers.** It is *absent*:
  the Go field is a `*string` with `omitempty`. `x.ik_nummer === null` is false
  for every record. Corrected, and the distinction is now stated in the schema.
- **An invented IK number was used as the example.** Replaced with a real one
  (`101576623`, Techniker Krankenkasse) — an example IK gets copied into a
  request, and a wrong one fails silently.

## Refactors this required

- **`internal/httpapi`** — the route table moved out of `cmd/api/main.go` so it
  can be built without a database, Redis or a search engine. `main.go` is now
  wiring only. The parity test constructs the *real* router; there is no second
  list of routes to keep in step.
- **`provider.ListResponse`** — both list endpoints built their body as a
  `gin.H` map literal. An untyped map cannot be checked against a schema, and
  the two copies could drift from each other as well as from the document.

## Deliberately not done

- **`oapi-codegen`.** Generating DTOs would mean rewriting handlers that are
  already tested and in use, to prevent a class of drift the tests now catch
  directly. Cost without the benefit.
- **Swagger UI rendered on this site.** It needs a URL the browser can fetch,
  and the repository is still private — the page would render an error. It
  belongs with [E5-S1](../epic-5-open-source/e5-s1-repo-licensing.md), when the
  raw URL resolves. Until then `editor.swagger.io` and the served endpoint
  cover it.

## Dependencies

- **Depends on:** E3-S1…S4 (endpoints exist)
- **Blocks:** —

## Risks

- ~~Spec/handler drift if not enforced in CI.~~ Enforced: the checks are
  ordinary Go tests, so `go test ./...` in the existing CI job runs them. No new
  pipeline step, and no way to merge past them.

## Definition of Done

- [x] Acceptance criteria fulfilled
- [x] Tests passing (unit + integration where relevant) — nine tests, 22 table cases
- [x] CI covers the new code (pipeline extended if needed) — covered by the existing `go test ./...`
- [x] Documentation updated
- [ ] Code reviewed

## References

- [API Specification](../../../api/openapi-spec.md)
