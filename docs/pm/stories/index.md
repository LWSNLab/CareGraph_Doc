# 🧩 Backlog — Epics & Stories

> Companion to the [PRD](../prd.md) and [Roadmap](../roadmap.md). Epics map to the
> product pillars/phases; each epic has its own page with stories and acceptance criteria.

**Story format:** *As a `<persona>`, I want `<capability>`, so that `<benefit>`.*
**Status legend:** ✅ done · 🚧 in progress · ⏳ planned
**ID scheme:** `E<epic>-S<story>`.

## Epics

| Epic | Area | Status |
| :-- | :-- | :--: |
| [E1 — Ingestion & ETL](epic-1-ingestion/index.md) | Scraping, PDF parsing, geocoding, loading, dedup | 🚧 |
| [E2 — Data Model & Search](epic-2-data-and-search/index.md) | PostGIS schema, Typesense sync, validation | 🚧 |
| [E3 — Public API Gateway](epic-3-api-gateway/index.md) | Endpoints, auth & rate limiting, OpenAPI | ✅ |
| [E4 — Operations & CI/CD](epic-4-operations/index.md) | Containerization, CI, observability | 🚧 |
| [E5 — Open Source & Funding](epic-5-open-source/index.md) | Licensing, governance, grants | ⏳ |
| [E6 — Commercial / DaaS](epic-6-commercial/index.md) | Tiers, managed dataset | ⏳ |

## Roll-up

| Epic | Stories | Σ Points | Priority (H / M / L) | Status |
| :-- | :--: | :--: | :--: | :-- |
| [E1 — Ingestion & ETL](epic-1-ingestion/index.md) | 9 | 42 | 5 / 4 / 0 | 🚧 (5 ✅) |
| [E2 — Data Model & Search](epic-2-data-and-search/index.md) | 3 | 11 | 1 / 2 / 0 | 🚧 (2 ✅) |
| [E3 — Public API Gateway](epic-3-api-gateway/index.md) | 6 | 22 | 3 / 3 / 0 | ✅ (6 ✅) |
| [E4 — Operations & CI/CD](epic-4-operations/index.md) | 6 | 18 | 3 / 2 / 1 | 🚧 (5 ✅) |
| [E5 — Open Source & Funding](epic-5-open-source/index.md) | 3 | 8 | 0 / 2 / 1 | ⏳ |
| [E6 — Commercial / DaaS](epic-6-commercial/index.md) | 2 | 13 | 0 / 0 / 2 | ⏳ |
| **Total** | **29** | **114** | **12 / 13 / 4** | **18 done · 11 planned** |

_Story points & priorities are initial drafts — adjust as the backlog is refined._
