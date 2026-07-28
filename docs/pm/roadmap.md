# 🗺️ CareGraph — Product & Engineering Roadmap

> **Version:** 1.0.0
> **Target Release:** Q1 2027
> **Strategy:** Incremental Development (Modular Monolith) & Open Source Funding

---

# 🎯 Executive Roadmap Summary

The CareGraph platform is developed across **four distinct phases**. The objective is to transform fragmented German healthcare and long-term care data into a high-performance, production-ready spatial REST API while simultaneously establishing the foundation for public funding initiatives (e.g. Prototype Fund, BMBF, Sovereign Tech Fund).

```text
┌────────────────┐     ┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│    PHASE 1     │ ──► │    PHASE 2     │ ──► │    PHASE 3     │ ──► │    PHASE 4     │
│ Ingestion & ETL│     │ Data & Search  │     │ High-Speed API │     │ Operations & OS│
└────────────────┘     └────────────────┘     └────────────────┘     └────────────────┘
```

---

# 🟢 Phase 1 — Ingestion Engine & Scraping Pipelines

**Primary Stack**

- Python 3.12
- Playwright
- BeautifulSoup
- pdfplumber
- Polars

**Focus**

Data extraction, normalization, validation, and automated geocoding.

## Milestone 1.1 — GKV Insurer Pipeline

- [x] Extract and normalize statutory health insurance data from official PDF tables.
- [x] Implement dynamic fallback and override mechanisms for missing contact information.
- [x] Normalize insurer identifiers and metadata.

---

## Milestone 1.2 — Care Provider Scraping Engine

- [ ] Build resilient web scrapers for:
  - Outpatient care services (*Pflegedienste*)
  - Care support centers (*Pflegestützpunkte*)
- [ ] Integrate public data sources:
  - vdek
  - AOK
  - ZQP
- [ ] Standardize Institution Codes (IK-Nummern).

---

## Milestone 1.3 — Geocoding Pipeline

- [ ] Implement automated address-to-coordinate resolution using OpenStreetMap/Nominatim.
- [ ] Introduce local geocoding cache to minimize redundant requests.
- [ ] Detect and retry failed geocoding jobs.

---

# 🟡 Phase 2 — Database Schema & Search Layer

**Primary Stack**

- PostgreSQL 16
- PostGIS
- Typesense (C++)
- Redis

**Focus**

Reliable spatial storage, indexing, and ultra-fast search.

## Milestone 2.1 — PostGIS Setup & Migration Engine

- [ ] Deploy PostgreSQL with PostGIS extensions.
- [ ] Apply the `care_infrastructure` schema.
- [ ] Create:
  - Spatial GIST indexes
  - JSONB GIN indexes
  - Compound filtering indexes

---

## Milestone 2.2 — Typesense Synchronization Worker

- [ ] Implement scheduled or real-time synchronization from PostgreSQL to Typesense.
- [ ] Configure:
  - Fuzzy search
  - Typo tolerance
  - German language optimization
  - Ranking strategy

---

## Milestone 2.3 — Data Validation & Deduplication

- [ ] Detect duplicate providers across multiple insurance datasets.
- [ ] Merge equivalent entities using:
  - IK Number
  - Address similarity
  - Name similarity
- [ ] Generate validation reports.

---

# 🔵 Phase 3 — High-Speed API Gateway

**Primary Stack**

- Go (Golang)
- Gin or Fiber
- Redis

**Focus**

Low-latency REST API, authentication, and scalable request handling.

## Milestone 3.1 — Core REST Endpoints

- [ ] `GET /v1/infrastructure/near`
  - Geospatial radius search via `ST_DWithin`
- [ ] `GET /v1/infrastructure/search`
  - Full-text and fuzzy search via Typesense
- [ ] `GET /v1/infrastructure/{ik_nummer}`
  - Direct provider lookup

---

## Milestone 3.2 — Security & Rate Limiting

- [ ] Implement Argon2id-hashed B2B API Keys.
- [ ] Add Redis-backed Token Bucket rate limiting.
- [ ] Introduce request logging and audit trails.

---

## Milestone 3.3 — OpenAPI Documentation

- [ ] Automatically generate Swagger/OpenAPI documentation.
- [ ] Derive API specification directly from Go handlers and DTOs.
- [ ] Publish versioned API documentation.

---

# 🔴 Phase 4 — Operations, Funding & Open Source Launch

**Primary Stack**

- Docker Compose
- GitHub Actions
- Hetzner Cloud
- MkDocs

**Focus**

Deployment, CI/CD, public documentation, governance, and sustainable funding.

## Milestone 4.1 — Infrastructure as Code (IaC)

- [ ] Dockerize:
  - Python ingestion workers
  - Go API Gateway
  - PostgreSQL/PostGIS
  - Typesense
  - Redis
- [ ] Configure GitHub Actions for:
  - Automated testing
  - Linting
  - Build verification
  - MkDocs deployment

---

## Milestone 4.2 — Open Source Governance & Funding

- [ ] Publish the core codebase under the **AGPLv3** license.
- [ ] Prepare grant applications for:
  - BMBF Prototype Fund
  - Sovereign Tech Fund
- [ ] Define contribution guidelines and governance model.

---

## Milestone 4.3 — Public Launch

- [ ] Publish production API documentation at:

```text
https://api.caregraph.de
```

- [ ] Launch a free Community Tier for:
  - Open-source developers
  - Researchers
  - Universities
  - Civic technology initiatives

- [ ] Prepare the first stable public release (**v1.0.0**).

---

# 📅 Release Overview

| Phase | Focus | Status |
| :--- | :--- | :--- |
| 🟢 Phase 1 | Data Ingestion & ETL | 🚧 In Progress |
| 🟡 Phase 2 | Database & Search | ⏳ Planned |
| 🔵 Phase 3 | REST API & Security | ⏳ Planned |
| 🔴 Phase 4 | Operations & Open Source | ⏳ Planned |