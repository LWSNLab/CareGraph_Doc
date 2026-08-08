# E1-S2 — Provider scrapers

|                  |                          |
| :--------------- | :----------------------- |
| **Epic**         | E1 — Ingestion & ETL     |
| **Story Points** | 8                        |
| **Priority**     | High                     |
| **Status**       | ✅ Done (pending review) |

> ← [Epic 1](index.md) · [Backlog](../index.md)

## User Story

As a **data engineer**, I want resilient scrapers for Pflegedienste, Pflegeheime and Pflegestützpunkte, so that provider records enter the pipeline.

## Description

Collect care-provider records (name, address, contact, IK-Nummer where available) from at least one primary source per provider type, in a way that tolerates layout changes and respects source policies.

## Acceptance Criteria

- [x] Scrapers for at least one primary source per provider type. *(All three types return real records — `pflegestuetzpunkt` needed name-based detection, see below.)*
- [x] IK-Nummer captured where available. *(OSM carries none — `ik_nummer` stays `NULL`; an authoritative source is still needed, see below.)*
- [x] Respect `robots.txt`, rate limits, and source ToS.
- [x] Ingestion failures are logged and alertable. *(`RunReport` + non-zero exit code.)*

## Technical Notes

**Source decision.** The obvious insurer portals are deliberately **not** scraped:

| Source | Finding |
| :-- | :-- |
| `pflegelotse.de` (vdek) | `robots.txt` disallows `/presentation/pl_treffer_sta.aspx` (stationary result list) and `/berichte_a/`, `/berichte_s/` (quality reports) — exactly the pages needed. |
| `pflege.aok.de` (AOK) | `robots.txt` disallows `/*?*`, i.e. every query-string URL — which is the entire search. |

Both are additionally protected databases (§ 87a UrhG). Scraping them would contradict the third acceptance criterion, so a data-sharing agreement — not a scraper — would be the route to that data.

**Implemented instead:** `pipelines/scrapers/osm_provider_scraper.py` reads OpenStreetMap via the Overpass API, per federal state. OSM is ODbL-licensed and intended for programmatic bulk access, and it delivers coordinates directly (so these records need no geocoding in E1-S3).

Tag mapping, derived from the actual tag distribution in German OSM data:

| OSM | `provider_type` |
| :-- | :-- |
| `social_facility=nursing_home` | `pflegeheim_stationaer` |
| `social_facility=ambulatory_care`, `healthcare=nurse` | `pflegedienst_ambulant` |
| `social_facility=outreach` **+ `:for=senior`** | `pflegedienst_ambulant` |
| name matches *Pflegestützpunkt* | `pflegestuetzpunkt` |

`outreach`/`advice` require an explicit senior audience: without it they are generic social work and pull in unrelated services (early-childhood intervention, women's centres, addiction support). `social_facility:for` is multi-value (`senior;disabled`) and is split before matching.

**Pflegestützpunkte are detected by name, not by tag.** Only 9 of the ~64 in German OSM carry `social_facility=advice`; the rest appear as `ambulatory_care`, `outreach`, even `nursing_home`, and a third have no facility tag at all (so the query fetches by name too). The name rule excludes municipal groundskeeping depots — *Grün-/Garten-/Stadtpflegestützpunkt* — which are not care facilities.

**Nationwide run (all 16 states):** 7,522 providers — 4,880 `pflegeheim_stationaer`, 2,579 `pflegedienst_ambulant`, 63 `pflegestuetzpunkt`. 100% carry coordinates, 69% a complete street address. One region (Mecklenburg-Vorpommern) failed on Overpass load and succeeded on a re-run — the failure surfaced through the report and a non-zero exit code, which is the alerting path working as intended.

**Known limitations (deliberate, not oversights):**

- Coverage is partial — 7.5k of Germany's ~30k facilities (~25%), and 63 of ~500 Pflegestützpunkte.
- No IK-Nummer, so `E1-S5` deduplication cannot use the strongest key for these records.
- Precision was favoured over recall; the tightened rule dropped ~40% of raw candidates, nearly all of them false positives.

**Result of the nationwide run:** 7,522 providers across all 16 federal states — 4,880 `pflegeheim_stationaer`, 2,579 `pflegedienst_ambulant`, 63 `pflegestuetzpunkt`; 100% with coordinates, 68% with a complete address. One region initially failed on a transient TLS error and succeeded on re-run — the run-level resilience behaved as designed (the other 15 regions were kept, the failure was reported and the exit code was non-zero).

**Follow-ups, tracked separately:** coverage improvement via official open data ([E1-S7](e1-s7-official-open-data.md)) and IK enrichment ([E1-S6](e1-s6-ik-enrichment.md)).

## Dependencies

- **Depends on:** —
- **Blocks:** E1-S3 (geocoding needs addresses), E1-S5 (dedup needs provider records)

## Risks

- Source ToS / database-right exposure — see [Data Sources & Licensing](../../../legal/data-licensing.md).
- Sites with heavy anti-bot measures may need manual fallbacks.

## Definition of Done

- [x] Acceptance criteria fulfilled
- [x] Tests passing (29 unit tests on the pure mapping logic; verified against live Overpass for Bremen/Hamburg)
- [x] Documentation updated
- [ ] Code reviewed

## References

- [Data Sources & Licensing](../../../legal/data-licensing.md)
