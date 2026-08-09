# Welcome to CareGraph 🏥🗺️

**CareGraph** is an open-source, high-performance infrastructure API providing access to standardized data on health insurance companies, care providers (*Pflegedienste*), nursing homes, and support centers (*Pflegestützpunkte*) across Germany.

## Why CareGraph?
Currently, Germany's care infrastructure data is trapped in isolated silos (AOK, vdek, ZQP, municipal PDFs). Developers building care management apps or municipal decision-makers lack a single, modern REST/FHIR interface.

CareGraph solves this by automatically aggregating, geocoding, and serving this data via a unified spatial graph API.

## Tech Stack at a Glance
* **Ingestion Pipelines:** Python (Playwright, pdfplumber, Polars)
* **Core Storage & Spatial Indexing:** PostgreSQL 16 + PostGIS
* **In-Memory Search Engine:** C++ (Typesense)
* **High-Speed API Gateway:** Go (Golang)

---

## Project Status — and why the code is not public yet

This documentation is open; the source repositories are **not yet**. That is a
deliberate sequence, not a change of heart about the licence — the core will be
released under **AGPLv3**, as described in the
[Open Source Strategy](pm/open-source-strategy.md).

Three things are being settled first:

1. **The data terms.** CareGraph republishes information collected from public
   sources. Which licence the resulting dataset can carry depends on the terms
   of those sources, and some are still being clarified — see
   [Data Sources & Licensing](legal/data-licensing.md). Publishing a dataset
   before its terms are settled would put that burden on whoever reuses it.
2. **The groundwork for contributors.** A security policy exists; contribution
   guidelines, issue templates and a governance process do not yet
   ([E5-S1](pm/stories/epic-5-open-source/e5-s1-repo-licensing.md)). Opening a
   repository nobody can contribute to helps no one.
3. **Maturity.** The platform is pre-1.0. Ingestion works end to end and the
   spatial core is in place; the API gateway is still a skeleton. The
   [backlog](pm/stories/index.md) shows exactly where each part stands.

The documentation is public from the start precisely so this progress can be
followed — including what does **not** work yet, which sources were rejected
and why, and which questions are still open.

**Interested in the code before the public release?** Get in touch — access can
be arranged for reviewers, funders and prospective partners.