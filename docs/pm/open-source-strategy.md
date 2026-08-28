# 👐 CareGraph — Open Source & Sustainability Strategy

> **Core Philosophy:** *Public Money, Public Code*
> **Primary License:** AGPLv3 (GNU Affero General Public License v3.0)
> **Business Model:** Open Core & Managed B2B Infrastructure Service

---

# 1. Executive Summary

Germany's healthcare and long-term care infrastructure data is a critical public asset. Today, this information is fragmented across numerous insurance associations, municipal directories, and proprietary systems.

**CareGraph** follows an **Open Source First** strategy to maximize transparency, interoperability, and long-term sustainability. The project aims to become the de facto open standard for healthcare and care infrastructure data in Germany while providing sustainable commercial services around hosting, data maintenance, and enterprise support.

The open-source core enables municipalities, researchers, healthcare providers, and software vendors to build interoperable solutions without vendor lock-in.

---

# 2. Licensing Model — AGPLv3

The core CareGraph codebase—including the Go API Gateway, Python ingestion pipelines, database schemas, and infrastructure tooling—is licensed under the **GNU Affero General Public License v3.0 (AGPLv3).**

> **Published 2026-08-25.** Both repositories are public:
> [CareGraph](https://github.com/LWSNLab/CareGraph) under AGPLv3, and
> [CareGraph_Doc](https://github.com/LWSNLab/CareGraph_Doc) under CC BY-SA 4.0.
> The groundwork that had to come first — contribution guidelines, a code of
> conduct, issue templates, and a pre-publication checklist walked line by line —
> is [E5-S1](stories/epic-5-open-source/e5-s1-repo-licensing.md).

## Why AGPLv3?

### Prevents Closed SaaS Forks

Unlike the standard GPL, the AGPL explicitly covers software delivered over a network. Organizations that modify CareGraph and operate it as a hosted service must publish their modifications under the same license.

### Protects the Open Ecosystem

The license prevents proprietary cloud providers from commercializing the project without contributing improvements back to the community.

### Enables Commercial Licensing

Organizations requiring proprietary integration or redistribution can obtain a commercial license without AGPL obligations.

---

# 3. Sustainability Model (Open Core)

Open Source does not imply an absence of funding. CareGraph follows a **dual-track sustainability strategy** combining an open core with commercial infrastructure services.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CareGraph Core Platform (AGPLv3)                         │
│                                                                             │
│ • Public GitHub Repository                                                  │
│ • Open Documentation                                                        │
│ • Free Self-Hosting                                                         │
│ • Community Contributions                                                   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                 ┌─────────────────────┴─────────────────────┐
                 ▼                                           ▼
┌──────────────────────────────────────┐ ┌──────────────────────────────────────┐
│ Managed Cloud API (Hosted DaaS)      │ │ Enterprise & Public Sector Services  │
│ • Live synchronized datasets         │ │ • Commercial licensing               │
│ • Automatic data maintenance         │ │ • Custom integrations                │
│ • Global API infrastructure          │ │ • Municipal planning tools           │
│ • Enterprise SLAs                    │ │ • Security audits & consulting       │
└──────────────────────────────────────┘ └──────────────────────────────────────┘
```

---

# 4. Hosted Data-as-a-Service (DaaS)

Although the software itself is open source, maintaining an accurate, deduplicated, and continuously updated nationwide healthcare dataset requires ongoing operational effort.

This includes:

- Continuous web scraping and data validation
- Geocoding and address normalization
- Duplicate detection
- Infrastructure hosting
- Monitoring and quality assurance

## Community Tier

Free access for:

- Open-source developers
- Universities
- Research institutions
- Non-profit organizations
- Civic technology projects

Features include:

- Rate-limited API access
- Public documentation
- Community support
- Self-service API keys

---

## Enterprise Tier

Paid subscriptions provide:

- Higher API throughput
- Dedicated API keys
- Service Level Agreements (SLAs)
- Priority support
- Stable production endpoints
- Custom export formats
- Early access to new datasets

---

# 5. Commercial Licensing

Organizations that need to embed CareGraph into proprietary or closed-source software without complying with AGPLv3 obligations may purchase a **Commercial Enterprise License**.

Typical use cases include:

- Closed-source healthcare platforms
- Proprietary municipal software
- OEM integrations
- On-premise enterprise deployments
- White-label solutions

---

# 6. Public Funding Strategy

CareGraph directly strengthens Germany's digital public infrastructure and therefore aligns well with national and European funding initiatives.

## Prototype Fund (BMBF / Open Knowledge Foundation Germany)

**Objective**

Support public-interest open-source software projects.

**Focus Areas**

- Digital infrastructure
- Open data
- Public health
- Civic technology

**Target Funding**

Approximately **47,500 €** per six-month development cycle.

---

## Sovereign Tech Fund (STF)

Long-term funding for critical open-source infrastructure within Europe.

Potential support areas include:

- Maintenance
- Security
- Documentation
- Community management
- Infrastructure reliability

---

## Municipal Digitalization Programs

Partnership opportunities with:

- Cities
- Districts (*Landkreise*)
- Municipal planning authorities

Potential applications include:

- Care infrastructure planning (*Pflegestrukturplanung*)
- Healthcare accessibility analysis
- Regional demographic planning
- Public data integration

---

# 7. Governance & Community

A transparent governance model is essential for long-term sustainability.

## Open Development

All development occurs publicly via GitHub:

- Issue tracking
- Discussions
- Pull Requests
- Architecture Decision Records (ADRs)
- RFC process for schema evolution

---

## Community Data Quality

Healthcare providers, municipalities, and users can contribute by:

- Reporting incorrect information
- Updating addresses
- Correcting contact details
- Suggesting new data sources
- Improving documentation

Structured GitHub Issue Templates simplify these workflows.

---

## Security Process

Security is handled through responsible disclosure.

Measures include:

- `SECURITY.md`
- Private vulnerability reporting
- Coordinated disclosure process
- Automated dependency scanning
- Continuous vulnerability monitoring

Recommended tooling:

- Dependabot
- Trivy
- GitHub Advanced Security (optional)

---

# 8. Long-Term Vision

CareGraph aims to become the **open digital infrastructure layer for healthcare and long-term care data in Germany**.

The project combines:

- Open-source software
- Public-interest digital infrastructure
- Sustainable commercial services
- Transparent governance
- High-performance spatial APIs
- Community-driven data quality

By balancing openness with sustainable funding, CareGraph can remain a reliable and independent platform for municipalities, healthcare providers, researchers, and software developers alike.