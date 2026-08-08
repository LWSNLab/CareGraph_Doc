# E1-S1 — GKV insurer list

|                  |                          |
| :--------------- | :----------------------- |
| **Epic**         | E1 — Ingestion & ETL     |
| **Story Points** | 5                        |
| **Priority**     | High                     |
| **Status**       | ✅ Done                  |

> ← [Epic 1](index.md) · [Backlog](../index.md)

## User Story

As a **data engineer**, I want the official GKV insurer PDF parsed and normalized, so that insurer data becomes machine-readable.

## Description

Parse the official GKV statutory-insurer list — a grid-less PDF whose rows wrap across several visual lines — into structured records: name, homepage, supplementary contribution rate (*Zusatzbeitrag*), and the regions the insurer is open in.

## Acceptance Criteria

- [x] All insurers extracted (coordinate-based parsing; handles wrapped rows).
- [x] Contribution rate parsed to a number; nationwide flag derived.
- [x] Regions normalized to the 16 federal states.
- [x] Manual overrides for bot-blocked insurers.

## Technical Notes

Coordinate-based `pdfplumber` extraction (column x-edges derived from the header row, with a fallback); address enrichment via impressum scraping; Bundesland normalization by longest-prefix match. Implemented in `pipelines/parsers/` and `pipelines/scrapers/`.

## Dependencies

- **Depends on:** —
- **Blocks:** E1-S4 (the loader consumes this parsed dataset)

## Risks

- Yearly PDF layout changes can shift column positions — mitigated by header-derived edges + a positional fallback.

## Definition of Done

- [x] Acceptance criteria fulfilled
- [x] Tests passing (66 tests: parser, address scraper, exporter — incl. an integration test against the official PDF)
- [x] CI covers the new code (pipeline extended if needed)
- [x] Documentation updated
- [ ] Code reviewed

## References

- [Data Schema](../../../architecture/data-schema.md)
