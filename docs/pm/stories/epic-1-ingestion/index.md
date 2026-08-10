# EPIC 1 — Ingestion & ETL 🚧

> Extract, normalize, geocode and load German care data. Roadmap Phase 1.
> ← [Backlog overview](../index.md) · [PRD](../../prd.md) · [Roadmap](../../roadmap.md)

| Story | Points | Priority | Status |
| :-- | :--: | :--: | :--: |
| [E1-S1 — GKV insurer list](e1-s1-gkv-insurer-list.md) | 5 | High | ✅ Done |
| [E1-S2 — Provider scrapers](e1-s2-provider-scrapers.md) | 8 | High | ✅ Done (pending review) |
| [E1-S3 — Address backfill (reverse geocoding)](e1-s3-geocoding.md) | 3 | Medium | ⏳ Planned |
| [E1-S4 — CareGraph-native loader](e1-s4-loader.md) | 5 | High | ✅ Done (pending review) |
| [E1-S5 — Deduplication](e1-s5-deduplication.md) | 5 | Medium | ⏳ Planned |
| [E1-S6 — IK-Nummer enrichment](e1-s6-ik-enrichment.md) | 3 | Medium | ✅ Done (pending review) |
| [E1-S7 — Official open-data supplement](e1-s7-official-open-data.md) | 5 | Medium | ⏳ Planned |
| [E1-S8 — Provider IK numbers](e1-s8-provider-ik.md) | 5 | High | ⏳ Planned |

_Story points & priorities are initial drafts — adjust as needed._

## Current data state

| | |
| :-- | :-- |
| Insurers (E1-S1) | 92 rows — 91 with an official Kassensitz-IK. ⚠️ **The real count is 93:** one row holds two merged insurers (see below) |
| Providers: IK coverage | **0 of 7,522** — no public source exists (→ E1-S8) |
| Providers (E1-S2) | 7,522 across 16/16 states — 100% coordinates, 68% full address |
| Loaded into Postgres | ✅ **7,614 rows** — 7,522 providers + 92 insurers, 185 state links, 92 history rows |
| Website URLs | ✅ absolute everywhere — 103 scheme-less values normalised (migration `0004`), scheme measured per host rather than guessed |

✅ **Resolved in E1-S4:** the `plz`/`ort` `NOT NULL` conflict and the missing upsert key are fixed by migration `0002_loader_prerequisites.sql` (columns nullable, `source_id` added).

✅ **Fixed 2026-08-10:** the insurer upsert key no longer flaps when IK enrichment
fails. It had silently produced duplicate insurers on two observed runs — details
and verification in [E1-S4](e1-s4-loader.md#fixed-after-the-fact-insurer-key-flapping-2026-08-10).

### ⚠️ Open defects

| Defect | Impact |
| :-- | :-- |
| **Two insurers merged into one row** — `SKD BKK` + `SVLFG`, name *and* website concatenated (`skd-bkk.dewww.svlfg.de`). Likely the parser's "a line without a `%` value is a continuation" heuristic. | The insurer count above is 92 but should be **93**, and SVLFG's IK was never looked up. Every "92" in these docs inherits the error. |
| **IK fallback sources unreachable** — `www.gkv-datenaustausch.de` serves a certificate chain that validates against the macOS system trust store but not against the certifi bundle `requests` uses. | IK coverage drops to 75/92 on a fresh resolve. The loader now refuses to write in that state (exit 2) instead of corrupting data. Must **not** be worked around by disabling certificate verification. |
