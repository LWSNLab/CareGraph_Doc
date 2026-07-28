# 🗄️ Database Schema & Spatial Engine (PostgreSQL / PostGIS)

> **Database Version:** PostgreSQL 16+ with PostGIS 3.4 Extension
> **Primary Identifier:** Institutionskennzeichen (`ik_nummer`, 9-digit official ID) or UUIDv4

---

# 1. Architectural Philosophy

CareGraph uses a **hybrid relational schema**:

1. **Core Attributes** (ID, IK Number, Name, Structured Address, Geolocation) are stored in strict, indexed SQL columns.
2. **Dynamic Metadata** (insurance supplementary contribution rates, specific care services, MDK quality ratings, etc.) are stored in PostgreSQL `JSONB` columns.

This design eliminates the need for schema migrations whenever external data sources introduce new attributes while still providing high query performance for structured data.

---

# 2. DDL Specification

```sql
-- Create ENUM for provider classifications
CREATE TYPE provider_type AS ENUM (
    'krankenkasse',
    'pflegedienst_ambulant',
    'pflegeheim_stationaer',
    'pflegestuetzpunkt'
);

-- Core Infrastructure Table
CREATE TABLE care_infrastructure (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ik_nummer VARCHAR(9) UNIQUE,                   -- Official 9-digit Institution Code
    type provider_type NOT NULL,
    name VARCHAR(255) NOT NULL,
    parent_organization VARCHAR(255),             -- e.g. "Caritas", "Diakonie", "AOK"
    website VARCHAR(255),

    -- Structured Address Data
    strasse VARCHAR(255),
    plz VARCHAR(10) NOT NULL,
    ort VARCHAR(100) NOT NULL,
    bundesland VARCHAR(50),

    -- PostGIS Spatial Data (WGS84 / SRID 4326)
    location GEOGRAPHY(Point, 4326),

    -- Dynamic Metadata Store
    details JSONB DEFAULT '{}'::jsonb,

    scraping_status VARCHAR(50) DEFAULT 'raw',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Spatial GIST Index for Sub-5ms Radius Queries
CREATE INDEX idx_care_infra_location
ON care_infrastructure
USING GIST (location);

-- Compound Index for Common Filtering
CREATE INDEX idx_care_infra_type_plz
ON care_infrastructure (type, plz);

-- JSONB GIN Index for Metadata Searches
CREATE INDEX idx_care_infra_details
ON care_infrastructure
USING GIN (details);
```

---

# 3. Key Spatial Queries

## Radius Distance Query (`ST_DWithin`)

Retrieves all care providers within a specified distance (in meters) from a coordinate point, sorted by proximity.

```sql
SELECT
    id,
    ik_nummer,
    name,
    type,
    strasse,
    plz,
    ort,
    ST_Distance(
        location,
        ST_MakePoint($1, $2)::geography
    ) / 1000.0 AS distance_km
FROM
    care_infrastructure
WHERE
    ST_DWithin(
        location,
        ST_MakePoint($1, $2)::geography,
        $3              -- Radius in meters
    )
    AND ($4::provider_type IS NULL OR type = $4)
ORDER BY
    distance_km ASC
LIMIT 50;
```

### Query Parameters

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `$1` | `float` | Longitude |
| `$2` | `float` | Latitude |
| `$3` | `integer` | Search radius in meters |
| `$4` | `provider_type` | Optional provider type filter |

---

# 4. Indexing Strategy

| Index | Type | Purpose |
| :--- | :--- | :--- |
| `idx_care_infra_location` | `GIST` | Accelerates spatial radius and nearest-neighbor searches. |
| `idx_care_infra_type_plz` | `B-Tree` | Optimizes filtering by provider type and postal code. |
| `idx_care_infra_details` | `GIN` | Enables fast lookups inside dynamic `JSONB` metadata. |

---

# 5. Design Decisions

- **UUIDv4** is used as the internal primary key for globally unique identifiers.
- **`ik_nummer`** serves as the official external identifier whenever available.
- **`GEOGRAPHY(Point, 4326)`** provides accurate geodesic distance calculations without manual projection handling.
- **`JSONB`** allows ingestion of heterogeneous provider metadata without frequent schema migrations.
- **PostGIS GIST indexes** enable radius searches with response times typically below 5 ms on indexed datasets.