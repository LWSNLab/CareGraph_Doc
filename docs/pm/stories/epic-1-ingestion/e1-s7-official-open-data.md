# E1-S7 — Official open-data supplement

|                  |                          |
| :--------------- | :----------------------- |
| **Epic**         | E1 — Ingestion & ETL     |
| **Story Points** | 5                        |
| **Priority**     | Medium                   |
| **Status**       | ⏳ Planned               |

> ← [Epic 1](index.md) · [Backlog](../index.md)

## User Story

As a **data engineer**, I want provider coverage supplemented from official municipal and state open data, so that the dataset moves beyond what OpenStreetMap happens to contain.

## Description

[E1-S2](e1-s2-provider-scrapers.md) established OpenStreetMap as the nationwide base source, which yields roughly a third of Germany's ~30k facilities. This story adds **authoritative** records from public administration open data — better address quality, official provenance, and in some cases fields OSM never has.

Records are merged with the existing ones rather than replacing them; conflict resolution is [E1-S5](e1-s5-deduplication.md)'s job.

## Acceptance Criteria

- [ ] Datasets are discovered via the GovData API (not by crawling the portal).
- [ ] At least two publishers are ingested end-to-end into the provider pipeline.
- [ ] Each dataset's licence is verified and recorded per record before ingestion.
- [ ] Source and retrieval date are stored as provenance on every record.
- [ ] Adding a further publisher requires only a new adapter, no pipeline changes.

## Technical Notes

**Access route.** `govdata.de` disallows generic crawlers in `robots.txt` (`User-agent: * / Disallow: /`), so the HTML portal must **not** be scraped. It does expose a documented CKAN API, which is the intended machine route:

```text
https://ckan.govdata.de/api/3/action/package_search?q=Pflegeeinrichtungen
```

Verified during exploration:

- The API responds and reports **83 datasets** for `Pflegeeinrichtungen`.
- Available formats include **CSV, GeoJSON, GML, KML, XLSX** and **WFS** services — several already carry coordinates, so those records need no geocoding.
- A sampled query returned 16 datasets from **Open.NRW** (10), **Statistisches Bundesamt** (4), **GDI-DE** and **Transparenzportal Hamburg**; earlier searches also surfaced **Landeshauptstadt München** and **Metropolregion Rhein-Neckar**.

**Two caveats worth planning around:**

1. **Licences are not populated in the API search response** (`license_id` was empty for every sampled dataset). They must be read per dataset — from DCAT-AP.de fields or the publisher — *before* ingesting. Most administrative data is *Datenlizenz Deutschland – Namensnennung 2.0*, which is permissive but requires attribution. This is a legal precondition, not a formality; see [Data Sources & Licensing](../../../legal/data-licensing.md).
2. **Not every hit is a facility list.** The Statistisches Bundesamt datasets are most likely *aggregated statistics* (counts per region), which do not fit `care_infrastructure`. Each candidate must be inspected before an adapter is written.

**Design.** One adapter per publisher behind a common interface, mirroring the `OSMProviderScraper` shape (fetch → map to `ProviderRecord` → report). The mapping is the per-publisher cost: schemas, column names and provider-type vocabularies differ between authorities.

## Dependencies

- **Depends on:** E1-S2 (the `ProviderRecord` shape and run-report pattern to reuse)
- **Blocks:** nothing hard; materially improves E1-S5 (more overlap to reconcile) and overall coverage

## Risks

- **Fragmentation is the real cost** — no nationwide dataset exists, so coverage grows publisher by publisher with diminishing returns.
- **Licence heterogeneity**: a single incompatible dataset could constrain the licence of the combined output.
- **Schema drift** on the publisher side breaks individual adapters; failures must stay isolated per adapter, as regions already are in E1-S2.

## Definition of Done

- [ ] Acceptance criteria fulfilled
- [ ] Tests passing (unit + integration where relevant)
- [ ] CI covers the new code (pipeline extended if needed)
- [ ] Documentation updated
- [ ] Code reviewed

## References

- [Data Sources & Licensing](../../../legal/data-licensing.md) · [Data Schema](../../../architecture/data-schema.md)
