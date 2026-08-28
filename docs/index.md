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

## Project Status

**The code is public.** [CareGraph](https://github.com/LWSNLab/CareGraph) is
released under **AGPLv3**, this documentation under **CC BY-SA 4.0**, both since
**2026-08-25**. The reasoning behind the licences is in the
[Open Source Strategy](pm/open-source-strategy.md).

Three things were settled before the switch was flipped, in this order:

1. **The data terms.** CareGraph republishes information collected from public
   sources, and which licence the resulting dataset can carry depends on the
   terms of those sources — see [Data Sources & Licensing](legal/data-licensing.md).
   The published archive ships under ODbL and contains care providers only.
   Hospitals are ingested but withheld from every published dataset while a
   redistribution question is unanswered, which is enforced by an allowlist in
   the exporter rather than by intention.
2. **The groundwork for contributors.** Contribution guidelines, a code of
   conduct, issue and pull-request templates and a documented way to ask for an
   API key ([E5-S1](pm/stories/epic-5-open-source/e5-s1-repo-licensing.md)). A
   repository nobody can contribute to helps no one.
3. **Maturity.** The platform is pre-1.0 and says so. The API surface is
   complete and tested, ingestion covers three sources, and one story is blocked
   on an answer from outside the project. The [backlog](pm/stories/index.md)
   shows exactly where each part stands.

The documentation was public from the start so this progress could be followed —
including what does **not** work yet, which sources were rejected and why, and
which questions are still open. That has not changed now that the code is out.

**Want to contribute?** Start with
[CONTRIBUTING.md](https://github.com/LWSNLab/CareGraph/blob/main/CONTRIBUTING.md).
Data corrections are as welcome as code, and need only one thing code does not: a
source.