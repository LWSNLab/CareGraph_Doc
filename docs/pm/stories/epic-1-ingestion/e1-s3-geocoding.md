# E1-S3 — Address backfill (reverse geocoding)

|                  |                          |
| :--------------- | :----------------------- |
| **Epic**         | E1 — Ingestion & ETL     |
| **Story Points** | 3                        |
| **Priority**     | Medium                   |
| **Status**       | ⏳ Planned               |

> ← [Epic 1](index.md) · [Backlog](../index.md)

## User Story

As a **data engineer**, I want providers that have coordinates but no address to be filled in from those coordinates, so that records are complete enough to display, filter by postcode and deduplicate.

## Description

Roughly **2,300 of 7,522 providers (30%)** carry a name and coordinates but no street, postcode or city, because their OpenStreetMap objects have no `addr:*` tags. This story derives an address from the coordinates via Nominatim, with a local cache and retry handling.

> **Re-scoped.** The story originally read "addresses → coordinates" and was
> marked High. That was written before [E1-S2](e1-s2-provider-scrapers.md)
> established that OSM supplies coordinates directly: **100% of providers
> already have a `location`**, the spatial index is in use and radius queries
> run in ~2 ms. Nothing is blocked by this story, so the priority is Medium and
> the direction is reversed.

## Acceptance Criteria

- [ ] Coordinates → address (street, postcode, city) via Nominatim for providers missing one.
- [ ] Local cache avoids repeat lookups; failed jobs are retried and reported.
- [ ] Nominatim usage policy respected (rate limit, identifying User-Agent).
- [ ] ODbL attribution recorded per derived address.
- [ ] Derived addresses are marked as such, distinguishable from source-provided ones.

## Technical Notes

Under `pipelines/geocoding/`.

**Out of scope: forward geocoding the insurers.** All 92 have an address but no `location`, which looks like a gap and is not one. Per the [data schema](../../../architecture/data-schema.md), a statutory insurer is not a point provider: what matters is the **region it is open in**, modelled through `krankenkasse_bundesland`. A radius search around a head office would answer a question nobody asks. Adding those coordinates would cost requests and invite misuse of the data.

**Quality caveat, worth stating up front.** These coordinates come *from* OSM, so asking Nominatim about them is partly circular: where the facility object carries no `addr:*` tags, the answer describes the enclosing building or street — a good approximation of *where* it is, not an authoritative statement of its postal address. Derived values must therefore be flagged, so that:

- [E1-S5](e1-s5-deduplication.md) can weight them lower than source-provided addresses, and
- an authoritative address from [E1-S7](e1-s7-official-open-data.md) can overwrite them without ceremony.

**Volume and politeness.** ~2,300 lookups at the public Nominatim policy of 1 request/second is roughly 40 minutes for a full backfill — fine as a scheduled job, but the cache matters on re-runs. Self-hosting Nominatim is the lever if this grows.

## Dependencies

- **Depends on:** E1-S2 (the provider records), E1-S4 (they are in the database)
- **Blocks:** nothing. Improves E1-S5 (address similarity is a matching key) and the completeness of API responses.

## Risks

- **ODbL share-alike** could affect the output dataset licence — see [Data Sources & Licensing](../../../legal/data-licensing.md). Already true for the coordinates; this adds volume, not a new category of risk.
- **Public Nominatim rate limits**; a full backfill must not look like abuse.
- **Approximate addresses could be mistaken for authoritative ones** if the flag is missing — which is why marking them is an acceptance criterion, not a nicety.

## Definition of Done

- [ ] Acceptance criteria fulfilled
- [ ] Tests passing (unit + integration where relevant)
- [ ] CI covers the new code (pipeline extended if needed)
- [ ] Documentation updated
- [ ] Code reviewed

## References

- [Data Sources & Licensing](../../../legal/data-licensing.md) · [Data Schema](../../../architecture/data-schema.md)
