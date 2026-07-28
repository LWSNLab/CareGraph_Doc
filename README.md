# 🗺️ CareGraph — Documentation & Project Management

> **Official Documentation Repository for the CareGraph Platform**
> *The Open Health & Care Infrastructure Graph for Germany.*

Welcome to the central documentation and architecture repository for **CareGraph**. This repository contains all architectural decisions, database schemas, security concepts, funding proposals, and roadmaps.

## 🔗 Quick Links
* **Target Implementation Repo:** `github.com/LWSNLab/caregraph` *(Coming Soon)*
* **Live API Specification:** [OpenAPI Docs](./docs/api/openapi-spec.md)
* **Architecture Blueprint:** [System Overview](./docs/architecture/system-overview.md)
* **Data Sources & Licensing:** [Legal Concept](./docs/legal/data-licensing.md)
* **Funding Proposal:** [BMBF / Prototype Fund Draft](./docs/pm/funding-proposal.md)

---

## 🚀 Project Vision
CareGraph connects fragmented public health and care data (GKV health insurers, outpatient care services, nursing homes, advice centers) into a unified, high-performance **PostGIS · Go · Typesense API**.

### Key Principles
1. **Open Source Core (AGPLv3):** Public Money, Public Code.
2. **Security & Privacy by Design:** GDPR-compliant geocoding without storing raw user locations.
3. **High-Performance:** Sub-10ms geospatial & fuzzy search latencies.