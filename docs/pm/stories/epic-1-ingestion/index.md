# EPIC 1 — Ingestion & ETL 🚧

> Extract, normalize, geocode and load German care data. Roadmap Phase 1.
> ← [Backlog overview](../index.md) · [PRD](../../prd.md) · [Roadmap](../../roadmap.md)

| Story | Points | Priority | Status |
| :-- | :--: | :--: | :--: |
| [E1-S1 — GKV insurer list](e1-s1-gkv-insurer-list.md) | 5 | High | ✅ Done |
| [E1-S2 — Provider scrapers](e1-s2-provider-scrapers.md) | 8 | High | ✅ Done (pending review) |
| [E1-S3 — Geocoding](e1-s3-geocoding.md) | 3 | High | ⏳ Planned |
| [E1-S4 — CareGraph-native loader](e1-s4-loader.md) | 5 | High | ✅ Done (pending review) |
| [E1-S5 — Deduplication](e1-s5-deduplication.md) | 5 | Medium | ⏳ Planned |
| [E1-S6 — IK-Nummer enrichment](e1-s6-ik-enrichment.md) | 3 | Medium | ✅ Done (pending review) |
| [E1-S7 — Official open-data supplement](e1-s7-official-open-data.md) | 5 | Medium | ⏳ Planned |
| [E1-S8 — Provider IK numbers](e1-s8-provider-ik.md) | 5 | High | ⏳ Planned |

_Story points & priorities are initial drafts — adjust as needed._

## Current data state

| | |
| :-- | :-- |
| Insurers (E1-S1) | 92 — 91 with an official Kassensitz-IK; only EY BKK absent from every source |
| Providers: IK coverage | **0 of 7,522** — no public source exists (→ E1-S8) |
| Providers (E1-S2) | 7,522 across 16/16 states — 100% coordinates, 68% full address |
| Loaded into Postgres | ✅ **7,614 rows** — 7,522 providers + 92 insurers, 185 state links, 92 history rows |

✅ **Resolved in E1-S4:** the `plz`/`ort` `NOT NULL` conflict and the missing upsert key are fixed by migration `0002_loader_prerequisites.sql` (columns nullable, `source_id` added).
