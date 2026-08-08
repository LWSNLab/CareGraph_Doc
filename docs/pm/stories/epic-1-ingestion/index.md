# EPIC 1 — Ingestion & ETL 🚧

> Extract, normalize, geocode and load German care data. Roadmap Phase 1.
> ← [Backlog overview](../index.md) · [PRD](../../prd.md) · [Roadmap](../../roadmap.md)

| Story | Points | Priority | Status |
| :-- | :--: | :--: | :--: |
| [E1-S1 — GKV insurer list](e1-s1-gkv-insurer-list.md) | 5 | High | ✅ Done |
| [E1-S2 — Provider scrapers](e1-s2-provider-scrapers.md) | 8 | High | ✅ Done (pending review) |
| [E1-S3 — Geocoding](e1-s3-geocoding.md) | 3 | High | ⏳ Planned |
| [E1-S4 — CareGraph-native loader](e1-s4-loader.md) | 5 | High | ⏳ **Next** |
| [E1-S5 — Deduplication](e1-s5-deduplication.md) | 5 | Medium | ⏳ Planned |
| [E1-S6 — IK-Nummer enrichment](e1-s6-ik-enrichment.md) | 3 | Medium | ⏳ Planned |
| [E1-S7 — Official open-data supplement](e1-s7-official-open-data.md) | 5 | Medium | ⏳ Planned |

_Story points & priorities are initial drafts — adjust as needed._

## Current data state

| | |
| :-- | :-- |
| Insurers (E1-S1) | 92 — complete, no IK yet (→ E1-S6) |
| Providers (E1-S2) | 7,522 across 16/16 states — 100% coordinates, 68% full address |
| Loaded into Postgres | **not yet** — output still lands in JSON (→ E1-S4) |

⚠️ **Known schema conflict for E1-S4:** `care_infrastructure` declares `plz`/`ort` as `NOT NULL`, but 30% of the provider records have no address (they do have coordinates). Recommendation: make both nullable and backfill via reverse geocoding in E1-S3 — dropping named, geocoded records would be the worse trade.
