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