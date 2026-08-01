# 🏛️ System Overview & High-Level Architecture

> **Project:** CareGraph — Open Health & Care Infrastructure Graph for Germany
> **Status:** Active Design / Proof of Concept

---

# 1. Vision & Core Objectives

The health and care infrastructure landscape in Germany is highly fragmented across different insurance associations, municipal directories, and PDFs. **CareGraph** unifies these data silos into a single, high-performance, open-source REST and FHIR-compatible spatial API.

## Core Architecture Goals

- **Sub-10ms Latency:** Instant response times for geospatial radius queries and fuzzy searches.
- **Modular Monolith First:** Maintainable single-binary deployment with strict domain boundaries.
- **Polyglot Stack Strategy:** Leveraging the best language for each specific domain (Python, Go, C++, SQL).
- **Data Privacy by Design:** Full GDPR compliance without storing raw user location data.

---

# 2. Polyglot Technology Stack

We deliberately select tools based on performance, ecosystem maturity, and domain suitability:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. PYTHON (Data Ingestion & Processing)                                     │
│    • Tech: Python 3.12, Playwright, BeautifulSoup, pdfplumber, Polars       │
│    • Role: Scraping, PDF-Parsing, Data Cleaning, Geocoding Pipelines        │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Writes Ingested Data
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. POSTGRESQL 16 + POSTGIS (Primary Data Store & Spatial Engine)            │
│    • Tech: PostgreSQL, PostGIS, JSONB                                       │
│    • Role: Single Source of Truth, Spatial Indexing (GIST), Core Schema     │
└───────────────────┬─────────────────────────────────────┬───────────────────┘
                    │                                     │
                    │ Syncs RAM Index                     │ Reads Spatial Data
                    ▼                                     ▼
┌──────────────────────────────────────┐ ┌────────────────────────────────────┐
│ 3. C++ / TYPESENSE (Search Engine)   │ │ 4. GO (High-Speed API Gateway)     │
│    • Tech: Typesense (C++ Core)      │ │    • Tech: Go (Golang), Gin/Fiber  │
│    • Role: In-Memory Fuzzy Search    │ │    • Role: Public REST API, Auth,  │
│      with Typo Tolerance (< 2 ms)    │ │      Rate Limiting, JSON Serving   │
└──────────────────────────────────────┘ └────────────────────────────────────┘
```

## Component Responsibility Matrix

| Component | Technology | Primary Responsibility |
| :--- | :--- | :--- |
| **Ingestion Engine** | **Python 3.12** | PDF extraction (`pdfplumber`), web scraping (`Playwright`, `BeautifulSoup`), data transformations (`Polars`). |
| **Primary Database** | **PostgreSQL + PostGIS** | Spatial calculations (`ST_DWithin`), relational constraints, and flexible metadata storage (`JSONB`). |
| **Search Engine** | **Typesense (C++)** | Sub-2ms in-memory full-text search with automatic typo tolerance. |
| **API Gateway** | **Go (Golang)** | High-throughput, low-memory HTTP gateway handling routing, authentication, and rate limiting. |

---

# 3. Repository Layout (Modular Monolith)

To avoid premature microservice overhead (network latency, distributed tracing, service mesh complexity), CareGraph starts as a **Modular Monolith**.

```text
caregraph/
├── cmd/
│   └── api/
│       └── main.go                 # Go: API Entry Point
├── internal/                       # Go: Core Business Logic (Modular)
│   ├── infrastructure/             # Database & PostGIS Connections
│   ├── provider/                   # Care Provider & Spatial Domains
│   ├── search/                     # Typesense Integration
│   └── auth/                       # B2B API Key Management & Rate Limiting
├── pipelines/                      # Python: Ingestion & Scraping Engine
│   ├── scrapers/                   # Web Scrapers (vdek, AOK, ZQP)
│   ├── parsers/                    # PDF Parsers (GKV Insurer Lists)
│   └── geocoding/                  # OSM / Nominatim Integration
├── docker-compose.yml              # Dev Setup (Postgres+PostGIS, Typesense, Redis)
└── README.md
```

---

# 4. API Specification Preview

## `GET /v1/infrastructure/near`

Retrieves providers within a given radius around spatial coordinates.

### Query Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `lat` | `float` | ✅ | Latitude (e.g. `48.7182`) |
| `lng` | `float` | ✅ | Longitude (e.g. `10.7781`) |
| `radius_km` | `float` | ❌ | Search radius in kilometers (default: `10.0`) |
| `type` | `string` | ❌ | Filter by provider type (`pflegedienst_ambulant`, `krankenkasse`, etc.) |

### Example Response (`200 OK`)

```json
{
  "total": 1,
  "data": [
    {
      "id": "c3b9a12e-1234-5678-90ab-cdef12345678",
      "ik_nummer": "490123456",
      "type": "pflegedienst_ambulant",
      "name": "Ambulanter Pflegedienst Muster",
      "address": {
        "street": "Bahnhofstraße 12",
        "postal_code": "12345",
        "city": "Musterstadt"
      },
      "distance_km": 1.42,
      "details": {
        "services": [
          "grundpflege",
          "behandlungspflege",
          "palliative"
        ],
        "phone": "+49 906 123456"
      }
    }
  ]
}
```
