# E2-S4 — Identifier durability

|                  |                              |
| :--------------- | :--------------------------- |
| **Epic**         | E2 — Data Model & Search     |
| **Type**         | Story                        |
| **Story Points** | 5                            |
| **Priority**     | Medium                       |
| **Status**       | ⏳ Planned                   |

> ← [Epic 2](index.md) · [Backlog](../index.md)

## User Story

As a **consumer who stored a CareGraph identifier**, I want to know what happens
when the record behind it changes, so that my reference either still resolves or
tells me why it does not.

## Description

[E3-S7](../epic-3-api-gateway/e3-s7-stable-record-identifier.md) publishes
`source_id` as the identifier to store. That fixes an untrue statement in the
contract, but it makes a new promise, and this story is what the promise costs.

`source_id` is stable, not permanent. It carries the source object's identity —
`osm:way/123456` — and therefore inherits OpenStreetMap's churn:

| What happens upstream | What a stored reference does today |
| :-- | :-- |
| A way is split in two | one id keeps resolving, the other half is a new record |
| A node is upgraded to a way | `osm:node/1` disappears, `osm:way/9` appears |
| An object is deleted and re-drawn | the id vanishes, an identical place gets a new one |
| Two records turn out to be one ([E1-S5](../epic-1-ingestion/e1-s5-deduplication.md)) | the merged-away id is simply gone |

In each case the row stops being returned. Nothing errors, nothing says why.
That is the same class of silent failure E3-S7 exists to remove — handing out a
key without a rule for its disappearance moves the problem rather than solving it.

## Acceptance Criteria

- [ ] A record that goes away leaves something behind: the identifier resolves to
      a statement that it is gone, and to its successor where there is one.
- [ ] Merges record which identifier survived and which was folded into it, so a
      client holding the loser can follow one hop.
- [ ] The published archive carries these too. An identifier that resolves through
      the API but silently vanishes from the dataset is only half an answer.
- [ ] The contract states the guarantee in words — what may change, what may not,
      and what a client should do when a reference stops resolving.
- [ ] A test asserts the guarantee: a record removed between two ingestion runs
      must remain resolvable as gone rather than absent.

## Technical Notes

**A tombstone, not a delete.** The loader upserts and never removes, so a record
vanishing from the source currently just stops being refreshed — it is still in
the table, silently stale. Deciding this properly means deciding both: when a row
is marked gone, and what `/near` and `/search` do with it. They should not return
it; a direct lookup by identifier should.

**One hop, not a chain.** `superseded_by` pointing at the survivor is enough. A
chain of redirects is a graph to walk and a cycle to guard against, for a case
that occurs rarely.

**This is where the reasoning of [E1-S6](../epic-1-ingestion/e1-s6-ik-enrichment.md)
already lives.** Insurer keys are rewritten in place when an IK arrives, precisely
so history stays attached to one row rather than splitting across two. The same
question for providers, without an IK to rekey on.

## What is deliberately not proposed

**A CareGraph-native identifier independent of the source.** It sounds like the
clean answer: mint an id at first sight and never let it change. It also means
maintaining a resolution table that is itself the deduplication problem — deciding
whether a re-drawn OSM object is the same place is exactly what
[E1-S5](../epic-1-ingestion/e1-s5-deduplication.md) has no strong key for. That
would buy a stable-looking identifier and pay for it with silent wrong identity,
which is worse than a visible break.

Revisit when E1-S5 has run against real data and its match quality is measured
rather than assumed.

## Dependencies

- **Depends on:** [E3-S7](../epic-3-api-gateway/e3-s7-stable-record-identifier.md)
  — there is no durability question until an identifier is published
- **Related:** [E1-S5](../epic-1-ingestion/e1-s5-deduplication.md) creates the
  merge case this has to describe

## Risks

- **The guarantee is easy to write and hard to keep.** Every future ingestion
  source has to honour it. Better a narrow promise that holds — "this identifier
  will not be reused for a different place" — than a broad one quietly broken.

## References

- [Data Schema](../../../architecture/data-schema.md) · [API Specification](../../../api/openapi-spec.md)
