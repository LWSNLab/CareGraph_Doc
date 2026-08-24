# E3-S2 — Fuzzy search endpoint

|                  |                        |
| :--------------- | :--------------------- |
| **Epic**         | E3 — Public API Gateway |
| **Story Points** | 5                      |
| **Priority**     | Medium                 |
| **Status**       | ✅ Done |

> ← [Epic 3](index.md) · [Backlog](../index.md)

## User Story

As **Dana**, I want `GET /infrastructure/search`, so that users find providers despite typos.

## Description

Typo-tolerant full-text search over provider names, cities and operators,
optionally narrowed by city or type, served by the Typesense index that
[E2-S2](../epic-2-data-and-search/e2-s2-typesense-sync.md) fills.

## Acceptance Criteria

- [x] Typo-tolerant query via Typesense; optional `city` filter — plus `type` and
      `limit`, so the two list endpoints narrow the same way.
- [x] `q` shorter than 2 characters → `400`.

## Technical Notes

### Two stages: the engine ranks, Postgres fills in

The story left this open ("hydrated from Postgres **or** returned directly from
the index document"). The index decided it: it holds eight fields and the API's
`CareProvider` has more. Answering from the index would have given `/search` a
**different response shape** from `/near` — no `ik_nummer`, no `website`, no
`details` — and two places for the same record to disagree.

So the engine returns ranked identifiers and the database returns the records.
One schema, one source of truth, and the index can stay lean: the query asks for
`include_fields=id` and nothing else.

### The ranking has to survive the hydration

`WHERE source_id = ANY($1)` returns rows in whatever order the planner likes,
which would throw away the ranking that was just computed — **a search that
returns results in arbitrary order is not a search.**
`ORDER BY array_position($1, source_id)` restores the input order exactly. There
is an integration test that passes identifiers deliberately out of insertion
order.

### An unreachable engine is `503`, not an empty result

Answering `200` with no hits would tell a user their search found nothing. That
is a different statement, and a false one. The failure modes are told apart:

| Situation | Answer |
| :-- | :-- |
| No engine configured on this deployment | `501 not_implemented` |
| Engine unreachable or refusing | `503 unavailable` |
| Engine too slow | `504 timeout` |
| Client hung up | `499` |

`unavailable` is a new code in the error contract — additive, like `code` and
`request_id` were.

### The city filter is attacker-controlled text

`q` and `type` are validated (length, enum) before they reach the engine, but
`city` is free text interpolated into Typesense filter syntax. A backtick would
close the quoted value and let the rest be read as expression. It is stripped,
and there is a test that a filter-injection attempt returns 0 results rather
than bypassing the filter.

### Search is optional

Without a configured engine the gateway still runs and `/search` answers `501`.
A self-hoster who does not want to operate Typesense keeps a working API.

## Verified against the live stack

| Query | Total | Top hit |
| :-- | --: | :-- |
| `Charite` | 4 | Charité Universitätsmedizin Berlin |
| `Krankenhaus Munster` | 1 | Herz-Jesu Krankenhaus Münster-Hiltrup |
| `Caritas Pflegediesnt` | 3 | Caritas Pflegedienst |

Filters narrow rather than decorate: `city=München` on the Charité query returns
0, as does `type=pflegestuetzpunkt`. Warm requests answer in 2–5 ms.

## A defect this surfaced

**The E2-S2 integration tests were overwriting the development index.** They
published to the production `providers` alias on the shared Typesense instance,
so a test run left the index holding five seeded rows — and `/search` then
returned `200` with no results, which looks exactly like a working search over
an empty world. It took reading `out_of: 5` in a raw engine response to see it.

`sync_index` now takes the alias as a parameter and the tests publish to
`providers_pytest`. The database had been namespaced and cleaned up from the
start; the index had not.

## Dependencies

- **Depends on:** E2-S2 (Typesense sync)
- **Blocks:** —

## Risks

- **Ranking weights are a guess.** `name` 8, `ort` 4, `parent_organization` 2,
  `strasse` 1 — chosen so a facility outranks a street that happens to share its
  name. It works on the queries tried; it has not been evaluated systematically.
- **The index ages between rebuilds.** Search reflects the last `make search-sync`,
  not the database.

## Definition of Done

- [x] Acceptance criteria fulfilled
- [x] Tests passing — 8 client cases (including filter escaping and that an
      engine error never becomes an empty result), 9 handler cases, and 3
      integration tests on the order-preserving hydration
- [x] CI covers the new code
- [x] Documentation updated — `openapi.yaml` gained `type`, `limit`, the `503`
      response and the `unavailable` code
- [x] Code reviewed

## References

- [API Specification](../../../api/openapi-spec.md)
