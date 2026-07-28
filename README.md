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

---

## 📄 License

This **documentation** (everything in this repository) is licensed under
**[Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](./LICENSE)**
— SPDX: `CC-BY-SA-4.0`.

You may share and adapt the material, provided you give appropriate credit and
license your derivatives under the same terms.

> © 2026 CareGraph (LWSNLab). Suggested attribution: *"CareGraph Documentation (LWSNLab), CC BY-SA 4.0"*.

The CareGraph **source code** (in the separate implementation repository) is
licensed under **AGPLv3** — see [Open Source Strategy](./docs/pm/open-source-strategy.md).
The **datasets** carry their own terms — see [Data Sources & Licensing](./docs/legal/data-licensing.md).