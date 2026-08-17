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
| [E1-S9 — Hospitals from the Bundes-Klinik-Atlas](e1-s9-hospital-standortverzeichnis.md) | 3 | High | ✅ Done (pending review) |

_Story points & priorities are initial drafts — adjust as needed._

## Current data state

| | |
| :-- | :-- |
| Insurers (E1-S1) | **93** — 92 with an official Kassensitz-IK; only EY BKK appears in no source |
| Providers: IK coverage | **0 of 7,522** — no public source exists (→ E1-S8) |
| Providers (E1-S2) | 7,522 across 16/16 states — 100% coordinates, 68% full address |
| Hospitals (E1-S9) | **1,577** from the Bundes-Klinik-Atlas — 100 % coordinates, with beds, cases and emergency level |
| Loaded into Postgres | ✅ **9,192 rows** — 7,522 providers + 1,577 hospitals + 93 insurers, 185 state links |
| Website URLs | ✅ absolute everywhere — 103 scheme-less values normalised (migration `0004`), scheme measured per host rather than guessed |

✅ **Resolved in E1-S4:** the `plz`/`ort` `NOT NULL` conflict and the missing upsert key are fixed by migration `0002_loader_prerequisites.sql` (columns nullable, `source_id` added).

✅ **Fixed 2026-08-10:** the insurer upsert key no longer flaps when IK enrichment
fails. It had silently produced duplicate insurers on two observed runs — details
and verification in [E1-S4](e1-s4-loader.md#fixed-after-the-fact-insurer-key-flapping-2026-08-10).

✅ **Fixed 2026-08-10:** two insurers were merged into a single row — details in
[E1-S1](e1-s1-gkv-insurer-list.md#fixed-after-the-fact-two-insurers-in-one-row-2026-08-10).
The insurer count changed from 92 to **93** as a result, and IK coverage improved
from 91/92 to **92/93**.

✅ **Fixed 2026-08-10:** the IK sources are reachable again — 3/3 sources, 1,241
directory entries, coverage back to **92/93**. The cause was *not* a broken
server: a TLS-inspecting proxy on the development machine re-signed those
connections with a root certifi cannot know about. Verification now goes through
the OS trust store, still fully enabled —
[details and the corrected diagnosis](e1-s6-ik-enrichment.md#resolved-the-sources-were-never-broken-2026-08-10).

✅ **Fixed 2026-08-10:** the scraper no longer retries every host with
certificate verification disabled. It turned out **no host needs it at all**, so
the allowlist ships empty and a certificate error is now a real error —
[details in E1-S1](e1-s1-gkv-insurer-list.md#tls-downgrades-are-now-the-exception-not-the-retry-2026-08-10).
