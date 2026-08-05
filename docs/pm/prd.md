# 📋 Product Requirements Document (PRD)

> **Product:** CareGraph — Open Health & Care Infrastructure Graph for Germany
> **Version:** 0.1 (Draft) · **Status:** Living document · **Scope:** Full platform (all phases)
> **Related:** [Roadmap](roadmap.md) · [Epics & Stories](epics-and-stories.md) · [System Overview](../architecture/system-overview.md) · [Data Schema](../architecture/data-schema.md) · [Data Sources & Licensing](../legal/data-licensing.md)

---

## 1. Summary

CareGraph aggregates Germany's fragmented health- and long-term-care infrastructure data — statutory health insurers (GKV), outpatient care services (*Pflegedienste*), nursing homes (*Pflegeheime*), and care support centers (*Pflegestützpunkte*) — into a single, geocoded, high-performance **open REST API**. It combines an open-source core (AGPLv3) with a sustainable managed Data-as-a-Service.

---

## 2. Problem Statement

German care infrastructure data is trapped in isolated silos: insurance associations (AOK, vdek), quality institutes (ZQP), and municipal PDF directories. There is **no single, modern, machine-readable interface** to answer basic questions such as *"which care providers exist within 10 km of this address?"* or *"which health insurers can I join in Bayern, and at what contribution rate?"*.

Consequences:

- **Developers** rebuild the same scraping/cleaning stack for every care-related app.
- **Municipal planners** lack tooling for care-structure planning (*Pflegestrukturplanung*).
- **Researchers** cannot easily analyze accessibility or coverage gaps.
- **Citizens** (indirectly, via apps) get outdated or incomplete provider information.

---

## 3. Goals & Non-Goals

### 3.1 Goals

| # | Goal |
| :-- | :-- |
| G1 | Provide a unified, standardized dataset of German care infrastructure with official identifiers (IK-Nummer). |
| G2 | Serve it via a fast spatial + fuzzy-search REST API (radius search, text search, entity lookup). |
| G3 | Keep the data continuously fresh through automated, respectful ingestion pipelines. |
| G4 | Be open by default (AGPLv3 code, documented, self-hostable) while remaining financially sustainable. |
| G5 | Be GDPR-compliant and legally defensible regarding data provenance and licensing. |

### 3.2 Non-Goals

- **Not** a patient-facing medical records or appointment-booking system.
- **Not** a store of personal health data or private user profiles.
- **Not** a general-purpose German business directory — scope is health & care infrastructure.
- **Not** authoritative for real-time bed availability or live capacity (out of initial scope).

---

## 4. Target Users & Personas

| Persona | Role | Primary Need |
| :-- | :-- | :-- |
| **Dana — App Developer** | Builds care-finder / health apps | A reliable API for provider search by location & name, no scraping. |
| **Mara — Municipal Planner** | *Landkreis* digitalization office | Coverage & accessibility analysis for care-structure planning. |
| **Ravi — Researcher** | Public-health / health-economics | Bulk, well-documented, citable dataset with provenance. |
| **Bea — B2B Integrator** | Enterprise / insurer software | Stable, SLA-backed endpoints, higher throughput, custom exports. |
| **Citizen (indirect)** | End user via 3rd-party apps | Accurate, up-to-date provider and insurer information. |

---

## 5. Use Cases

- **UC1 — Nearby providers:** Given coordinates + radius, return care providers ordered by distance, filterable by type.
- **UC2 — Fuzzy search:** Typo-tolerant search by name/city (e.g. "Caritas Donauwörth").
- **UC3 — Entity lookup:** Fetch a single institution by IK-Nummer.
- **UC4 — Insurer selection:** List insurers available in a federal state with current & historical contribution rates.
- **UC5 — Planning export:** Bulk/regional export for municipal planning and research.

---

## 6. Product Scope & Pillars

CareGraph is delivered across four product pillars (mirroring the [roadmap](roadmap.md) phases):

1. **Ingestion & ETL** — scraping, PDF parsing, normalization, geocoding, deduplication.
2. **Data & Search** — PostGIS storage/indexing, Typesense in-memory search, validation.
3. **Public API** — Go gateway, spatial & text endpoints, auth, rate limiting, OpenAPI.
4. **Operations & Sustainability** — IaC/CI-CD, docs, governance, open-source launch, DaaS & funding.

---

## 7. Functional Requirements

| ID | Requirement | Pillar |
| :-- | :-- | :-- |
| FR1 | Ingest & normalize the official GKV insurer list (name, contribution rate, region). | Ingestion |
| FR2 | Scrape provider directories (Pflegedienste, Pflegeheime, Pflegestützpunkte) with IK-Nummer. | Ingestion |
| FR3 | Geocode addresses to WGS84 coordinates with a local cache. | Ingestion |
| FR4 | Deduplicate providers across sources (IK-Nummer, address & name similarity). | Data |
| FR5 | Store entities in `care_infrastructure` (+ regional & history satellites). | Data |
| FR6 | Keep an append-only history of insurer contribution rates. | Data |
| FR7 | Sync the dataset into Typesense for typo-tolerant search. | Data |
| FR8 | `GET /infrastructure/near` — spatial radius search. | API |
| FR9 | `GET /infrastructure/search` — fuzzy text search. | API |
| FR10 | `GET /infrastructure/{ik_nummer}` — entity lookup. | API |
| FR11 | API-key authentication + tiered rate limiting. | API |
| FR12 | Publish a versioned OpenAPI spec and generated docs. | API |
| FR13 | Provide a free Community tier and paid Enterprise tiers (DaaS). | Ops/DaaS |

---

## 8. Non-Functional Requirements

| ID | Category | Target |
| :-- | :-- | :-- |
| NFR1 | **Performance** | p95 < 10 ms for indexed spatial radius queries; < 2 ms typo-tolerant search. |
| NFR2 | **Availability** | 99.5%+ for the managed API (Enterprise SLAs higher). |
| NFR3 | **Security & Privacy** | GDPR by design; no raw coordinate logging; Argon2id-hashed keys; least-privilege DB roles. See [Security](../architecture/security.md). |
| NFR4 | **Openness** | Core AGPLv3, self-hostable, documented; dataset under an open-data license (TBD). |
| NFR5 | **Legal** | Defensible data provenance; respect source ToS/robots. See [Data Sources & Licensing](../legal/data-licensing.md). |
| NFR6 | **Scalability** | Modular monolith that can scale reads horizontally; ingestion decoupled from serving. |
| NFR7 | **Data Freshness** | Insurer list refreshed at least yearly (per publication); providers on a recurring schedule. |

---

## 9. Success Metrics (KPIs)

- **Coverage:** # insurers (target: 100% of GKV list) and # care providers ingested.
- **Freshness:** median age of records; successful scheduled ingestion runs.
- **Quality:** % records geocoded; % with IK-Nummer; deduplication precision/recall.
- **Performance:** p95 latency for `near` and `search`.
- **Adoption:** API keys issued, Community-tier signups, monthly active integrations.
- **Sustainability:** Enterprise subscriptions; grants secured (Prototype Fund / STF).

---

## 10. Business Model & Sustainability

Open Core + managed DaaS. The software is AGPLv3 and self-hostable; the paid service sells *operational value on top of free facts* — continuous re-collection, validation, hosting, SLAs, support. See [Open Source Strategy](open-source-strategy.md) and [Funding](funding-proposal.md).

---

## 11. Risks & Mitigations

| Risk | Impact | Mitigation |
| :-- | :-- | :-- |
| **Data-licensing / DB rights** on scraped sources | High | Re-collect facts from primary sources; provenance tracking; counsel. See [Data Sources & Licensing](../legal/data-licensing.md). |
| **Stack complexity** (polyglot, multi-store) | Medium | Modular monolith first; defer Go gateway / Typesense until load justifies; managed Postgres (Supabase) early. |
| **Source layout changes** break scrapers | Medium | Coordinate-based parsing, link-following, monitoring & alerts on ingestion failures. |
| **GDPR** for sole-trader providers | Medium | Data minimization; lawful-basis assessment (Art. 6(1)(f)); no personal profiles. |
| **Funding gap** | Medium | Dual track: grants + early Enterprise pilots. |

---

## 12. Milestones & Release Strategy

Phased delivery to a public **v1.0.0** (target Q1 2027), detailed in the [Roadmap](roadmap.md). Each phase maps to an epic in the [Epics & Stories](epics-and-stories.md) backlog. The first external release is a read-only Community API once Phases 1–3 are complete.

---

## 13. Open Questions

1. Dataset output license — CC BY 4.0 vs ODbL (share-alike from OSM geocodes)?
2. Which provider directories are legally safe primary sources vs. protected databases?
3. Managed-hosting target (Supabase vs. self-hosted Hetzner) for GA?
4. Scope & timing of live capacity data (currently a non-goal)?
