# E1-S3 — Geocoding

|                  |                          |
| :--------------- | :----------------------- |
| **Epic**         | E1 — Ingestion & ETL     |
| **Story Points** | 3                        |
| **Priority**     | High                     |
| **Status**       | ⏳ Planned               |

> ← [Epic 1](index.md) · [Backlog](../index.md)

## User Story

As a **data engineer**, I want addresses resolved to coordinates with a cache, so that entities are spatially searchable.

## Description

Turn structured addresses into WGS84 coordinates for the `location` column, using OpenStreetMap/Nominatim, with a local cache to minimize repeated lookups and honor usage policy.

## Acceptance Criteria

- [ ] Address → WGS84 (SRID 4326) via OSM/Nominatim.
- [ ] Local cache avoids duplicate lookups; failed jobs retried.
- [ ] ODbL attribution recorded for geocodes.

## Technical Notes

Under `pipelines/geocoding/`. Consider self-hosting Nominatim to control rate/usage. Geocodes are ODbL-licensed — attribution obligations may affect the dataset license.

## Dependencies

- **Depends on:** E1-S2 (needs provider addresses)
- **Blocks:** E1-S4 (loader writes `location`)

## Risks

- ODbL share-alike could affect the output dataset license — see [Data Sources & Licensing](../../../legal/data-licensing.md).
- Public Nominatim rate limits.

## Definition of Done

- [ ] Acceptance criteria fulfilled
- [ ] Tests passing (unit + integration where relevant)
- [ ] Documentation updated
- [ ] Code reviewed

## References

- [Data Sources & Licensing](../../../legal/data-licensing.md)
