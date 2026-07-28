# 🗄️ Database Schema & Spatial Engine (PostgreSQL / PostGIS)

> **Database Version:** PostgreSQL 16+ with PostGIS 3.4 Extension
> **Primary Identifier:** Institutionskennzeichen (`ik_nummer`, 9-digit official ID) or UUIDv4

---

# 1. Architectural Philosophy

CareGraph uses a **hybrid relational schema**:

1. **Core attributes** (ID, IK number, name, structured address, geolocation) live in strict, indexed SQL columns.
2. **Dynamic metadata** (specific care services, MDK quality ratings, contact details, etc.) live in a PostgreSQL `JSONB` column.
3. **Relational satellites** model the things that are genuinely relational and are queried on their own — **regional availability** of health insurers and the **time series** of supplementary contribution rates. These do *not* belong in `JSONB` because they are many-to-many or temporal.

This keeps schema migrations rare (new provider attributes just extend `JSONB`) while preserving referential integrity and index performance where it matters.

---

# 2. Core DDL — `care_infrastructure`

```sql
-- Provider classifications
CREATE TYPE provider_type AS ENUM (
    'krankenkasse',
    'pflegedienst_ambulant',
    'pflegeheim_stationaer',
    'pflegestuetzpunkt'
);

-- Core infrastructure table (one row per institution)
CREATE TABLE care_infrastructure (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ik_nummer VARCHAR(9) UNIQUE,                   -- Official 9-digit Institution Code
    type provider_type NOT NULL,
    name VARCHAR(255) NOT NULL,
    parent_organization VARCHAR(255),              -- e.g. "Caritas", "Diakonie", "AOK"
    website VARCHAR(255),

    -- Structured address data
    strasse VARCHAR(255),
    plz VARCHAR(10) NOT NULL,
    ort VARCHAR(100) NOT NULL,
    bundesland VARCHAR(50),                        -- location of the HQ / site

    -- PostGIS spatial data (WGS84 / SRID 4326)
    location GEOGRAPHY(Point, 4326),

    -- Dynamic metadata store
    details JSONB NOT NULL DEFAULT '{}'::jsonb,

    scraping_status VARCHAR(50) DEFAULT 'raw',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Spatial GIST index for sub-5ms radius queries
CREATE INDEX idx_care_infra_location ON care_infrastructure USING GIST (location);

-- Compound index for common filtering
CREATE INDEX idx_care_infra_type_plz ON care_infrastructure (type, plz);

-- JSONB GIN index for metadata searches
CREATE INDEX idx_care_infra_details ON care_infrastructure USING GIN (details);
```

> **Modeling note — insurers vs. point providers.**
> For a *point provider* (`pflegedienst_ambulant`, `pflegeheim_stationaer`, `pflegestuetzpunkt`) the `location` point is the entity you search by radius. For a `krankenkasse`, `location` is only the **headquarters** — a radius around it is not meaningful, because a statutory insurer's relevance is its **regional availability** (which federal states you can join it in). That availability is a many-to-many relation and is modeled explicitly in §3, not via `location`. Spatial radius queries therefore apply to point providers; insurer lookups go through the regional-availability tables.

---

# 3. Insurer Regional Availability (n:m)

The official GKV list expresses availability as free text (`"Berlin, Brandenburg, Mecklenburg-Vorpommern"`, `"bundesweit"`, `"betriebsbezogen …"`). We normalize this into a **federal-state dimension** and a **junction table** so that *"which insurers can I join in Bayern?"* is a single indexed query.

```sql
-- 16 German federal states (master data)
CREATE TABLE bundeslaender (
    id   SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- n:m link between an insurer and the states it is open in
CREATE TABLE krankenkasse_bundesland (
    krankenkasse_id UUID     NOT NULL REFERENCES care_infrastructure(id) ON DELETE CASCADE,
    bundesland_id   SMALLINT NOT NULL REFERENCES bundeslaender(id)       ON DELETE CASCADE,
    PRIMARY KEY (krankenkasse_id, bundesland_id)
);

CREATE INDEX idx_kk_bl_bundesland ON krankenkasse_bundesland (bundesland_id);
```

**Conventions**

* `bundesweit` insurers carry a boolean flag in `details` (`{"is_bundesweit": true}`) rather than 16 synthetic link rows — the ingestion pipeline can optionally expand them to all 16 for query convenience.
* `betriebsbezogen` (company) insurers have no state links (not publicly selectable).
* Suffixes like `"Schleswig-Holstein branchenbezogen"` still map to the state via longest-prefix matching in the pipeline.

### Query — insurers selectable in a given state

```sql
SELECT k.name, (k.details->>'zusatzbeitrag')::numeric AS zusatzbeitrag
FROM care_infrastructure k
JOIN krankenkasse_bundesland kb ON kb.krankenkasse_id = k.id
JOIN bundeslaender b            ON b.id = kb.bundesland_id
WHERE k.type = 'krankenkasse'
  AND b.name = 'Bayern'
ORDER BY zusatzbeitrag NULLS LAST;
```

---

# 4. Contribution-Rate Historization (time series)

The *Zusatzbeitrag* changes over time and is one of CareGraph's key differentiators versus a static PDF list. Storing only the current value (in `details`) throws away history, and backfilling later is expensive. We therefore keep an append-only history table.

```sql
CREATE TABLE zusatzbeitrag_historie (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    krankenkasse_id UUID NOT NULL REFERENCES care_infrastructure(id) ON DELETE CASCADE,
    gueltig_ab      DATE NOT NULL,                    -- "Stand" / valid-from date of the list
    zusatzbeitrag   NUMERIC(4,2) NOT NULL,
    quelle          TEXT,                             -- e.g. 'GKV-Spitzenverband, Liste 2026-07-26'
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (krankenkasse_id, gueltig_ab)              -- one value per insurer per publication
);

CREATE INDEX idx_zb_hist_kk_datum ON zusatzbeitrag_historie (krankenkasse_id, gueltig_ab DESC);
```

The **current** rate is simply the latest row; a view keeps consumers simple:

```sql
CREATE VIEW zusatzbeitrag_aktuell AS
SELECT DISTINCT ON (krankenkasse_id)
       krankenkasse_id, gueltig_ab, zusatzbeitrag
FROM   zusatzbeitrag_historie
ORDER  BY krankenkasse_id, gueltig_ab DESC;
```

This makes each yearly ingestion an **append** (`ON CONFLICT (krankenkasse_id, gueltig_ab) DO NOTHING`) instead of an overwrite, enabling trend endpoints (`/insurers/{id}/history`) later.

---

# 5. Key Spatial Query (`ST_DWithin`)

Retrieves point providers within a given distance (meters) of a coordinate, sorted by proximity.

```sql
SELECT
    id, ik_nummer, name, type, strasse, plz, ort,
    ST_Distance(location, ST_MakePoint($1, $2)::geography) / 1000.0 AS distance_km
FROM care_infrastructure
WHERE ST_DWithin(location, ST_MakePoint($1, $2)::geography, $3)   -- $3 = radius in meters
  AND ($4::provider_type IS NULL OR type = $4)
ORDER BY distance_km ASC
LIMIT 50;
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `$1` | `float` | Longitude |
| `$2` | `float` | Latitude |
| `$3` | `integer` | Search radius in meters |
| `$4` | `provider_type` | Optional provider-type filter |

---

# 6. Indexing Strategy

| Index | Type | Purpose |
| :--- | :--- | :--- |
| `idx_care_infra_location` | `GIST` | Spatial radius and nearest-neighbor searches. |
| `idx_care_infra_type_plz` | `B-Tree` | Filtering by provider type and postal code. |
| `idx_care_infra_details` | `GIN` | Lookups inside dynamic `JSONB` metadata. |
| `idx_kk_bl_bundesland` | `B-Tree` | Reverse lookup: all insurers in a state. |
| `idx_zb_hist_kk_datum` | `B-Tree` | Latest / time-ranged contribution-rate reads. |

---

# 7. Design Decisions

- **UUIDv4** internal primary key → globally unique identifiers, safe to expose.
- **`ik_nummer`** is the official external identifier whenever available (natural upsert key across sources).
- **`GEOGRAPHY(Point, 4326)`** gives accurate geodesic distances without manual projection handling.
- **`JSONB`** absorbs heterogeneous provider metadata without frequent migrations.
- **Relational satellites** (`bundeslaender`, `krankenkasse_bundesland`, `zusatzbeitrag_historie`) hold the many-to-many and temporal facts that `JSONB` cannot query efficiently.
- **PostGIS GIST indexes** keep radius searches typically below 5 ms on indexed datasets.
