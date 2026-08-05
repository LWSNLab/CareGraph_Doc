# E1-S2 — Provider scrapers

|                  |                          |
| :--------------- | :----------------------- |
| **Epic**         | E1 — Ingestion & ETL     |
| **Story Points** | 8                        |
| **Priority**     | High                     |
| **Status**       | ⏳ Planned               |

> ← [Epic 1](index.md) · [Backlog](../index.md)

## User Story

As a **data engineer**, I want resilient scrapers for Pflegedienste, Pflegeheime and Pflegestützpunkte, so that provider records enter the pipeline.

## Description

Collect care-provider records (name, address, contact, IK-Nummer where available) from at least one primary source per provider type, in a way that tolerates layout changes and respects source policies.

## Acceptance Criteria

- [ ] Scrapers for at least one primary source per provider type.
- [ ] IK-Nummer captured where available.
- [ ] Respect `robots.txt`, rate limits, and source ToS.
- [ ] Ingestion failures are logged and alertable.

## Technical Notes

Playwright/BeautifulSoup under `pipelines/scrapers/`. Prefer legally-mandated public directories (§ 7 SGB XI) over third-party aggregators; re-collect facts rather than mirroring a protected database.

## Dependencies

- **Depends on:** —
- **Blocks:** E1-S3 (geocoding needs addresses), E1-S5 (dedup needs provider records)

## Risks

- Source ToS / database-right exposure — see [Data Sources & Licensing](../../../legal/data-licensing.md).
- Sites with heavy anti-bot measures may need manual fallbacks.

## Definition of Done

- [ ] Acceptance criteria fulfilled
- [ ] Tests passing (unit + integration where relevant)
- [ ] Documentation updated
- [ ] Code reviewed

## References

- [Data Sources & Licensing](../../../legal/data-licensing.md)
