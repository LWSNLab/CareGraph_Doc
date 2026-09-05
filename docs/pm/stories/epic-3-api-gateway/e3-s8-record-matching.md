# E3-S8 — Record matching for integrators

|                  |                              |
| :--------------- | :--------------------------- |
| **Epic**         | E3 — Public API Gateway      |
| **Type**         | Story                        |
| **Story Points** | 5                            |
| **Priority**     | Medium                       |
| **Status**       | ⏳ Planned                   |

> ← [Epic 3](index.md) · [Backlog](../index.md)

## User Story

As an **integrator with my own list of care providers**, I want to map my records
onto CareGraph's in one pass, so that I can store a durable identifier and stop
matching on names.

## Description

This is what [E1-S8](../epic-1-ingestion/e1-s8-provider-ik.md) was meant to
enable, approached from the other side. That story assumed the join would be an
Institutionskennzeichen; the bodies holding provider IKs declined to share them,
and it is closed.

**The IK would not have solved this anyway.** A join on IK works only when *both*
sides carry it, correctly. An integrator with clean IKs does not need CareGraph to
find anything; one with a directory grown over years does not have them either.
The case that actually occurs is a list of names and addresses of varying quality
— a matching problem, not a lookup.

What CareGraph can offer instead suits it better: **coordinates on 100 % of
records**, a full address on 68 %, plus website and operator. Coordinates separate
exactly the case where name comparison fails — a nursing home and the outpatient
service run from the same building are two entities at one address.

## Acceptance Criteria

- [ ] An endpoint takes a name, and optionally an address or coordinates, and
      returns ranked candidates.
- [ ] Each candidate carries a score and the fields that produced it, so a human
      reviewing a borderline case can see *why*.
- [ ] A batch form, because the use case is thousands of records rather than one.
- [ ] Every candidate carries the identifier from
      [E3-S7](e3-s7-stable-record-identifier.md) — a match nobody can store is a
      match made twice.
- [ ] Confidence is banded, not merely numeric: certain, probable, needs review.
      A caller must be able to accept the top band unattended and queue the rest.
- [ ] The endpoint never merges or writes anything. It answers a question.

## Technical Notes

**Rank in Typesense, resolve in Postgres** — the shape [E3-S2](e3-s2-fuzzy-search.md)
already established, so a candidate has the same schema as a record from `/near`.
Typo and umlaut tolerance comes with it.

**Coordinates are the tiebreaker, not the filter.** An integrator's address may be
the operator's registered office rather than the site, so distance should lower a
score rather than exclude a candidate. Excluding on distance would silently drop
exactly the records worth reviewing.

**Refuse rather than guess**, as in [E1-S5](../epic-1-ingestion/e1-s5-deduplication.md).
A wrong match sits silently in the integrator's system for as long as they keep it
— worse than no match, which they can see. Two candidates of near-equal score are
a review case, not a decision.

**No fabricated IK.** A matched record still has no `ik_nummer`. Matching maps to
CareGraph identifiers and to nothing else.

## What this is not

Not deduplication. [E1-S5](../epic-1-ingestion/e1-s5-deduplication.md) finds
duplicates *inside* CareGraph and may merge them; this maps an outside record onto
one of ours and writes nothing. They share their similarity logic and should share
an implementation, which is the argument for building this after E1-S5 rather than
beside it.

## Dependencies

- **Depends on:** [E3-S7](e3-s7-stable-record-identifier.md) — the identifier this
  returns has to be storable
- **Related:** [E1-S5](../epic-1-ingestion/e1-s5-deduplication.md) shares the
  similarity logic; [E2-S3](../epic-2-data-and-search/e2-s3-data-validation.md)
  decides how clean the fields being matched are

## Risks

- **Match quality is a promise.** An endpoint that answers confidently and wrongly
  is worse than none, because the caller stops checking. Bands and visible reasons
  are the mitigation, and they are not optional.
- **This is the shape of a paid feature.** [Data Sources & Licensing](../../../legal/data-licensing.md)
  describes what a commercial offering may sell — operational value on top of free
  facts — and matching is exactly that. Deciding tiering here rather than in
  [E6](../epic-6-commercial/index.md) would be deciding it in the wrong place.

## References

- [API Specification](../../../api/openapi-spec.md) · [Open Source Strategy](../../open-source-strategy.md)
