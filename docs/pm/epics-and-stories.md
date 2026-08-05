# 🧩 Epics & Stories (Backlog)

> Companion to the [PRD](prd.md) and [Roadmap](roadmap.md). Epics map to the four
> product pillars/phases; stories are the deliverable units with acceptance criteria.

**Story format:** *As a `<persona>`, I want `<capability>`, so that `<benefit>`.*
**Status legend:** ✅ done · 🚧 in progress · ⏳ planned
**ID scheme:** `E<epic>-S<story>`.

---

## EPIC 1 — Ingestion & ETL 🚧
*Extract, normalize, geocode and load German care data. Roadmap Phase 1.*

### E1-S1 — GKV insurer list ✅
*As a data engineer, I want the official GKV insurer PDF parsed and normalized, so that insurer data is machine-readable.*

- [x] All insurers extracted (coordinate-based parsing; handles wrapped rows).
- [x] Contribution rate parsed to a number; nationwide flag derived.
- [x] Regions normalized to the 16 federal states.
- [x] Manual overrides for bot-blocked insurers.

### E1-S2 — Provider scrapers ⏳
*As a data engineer, I want resilient scrapers for Pflegedienste/Pflegeheime/Pflegestützpunkte, so that provider records enter the pipeline.*

- [ ] Scrapers for at least one primary source per provider type.
- [ ] IK-Nummer captured where available.
- [ ] Respect `robots.txt`, rate limits, and source ToS (see [Data Sources & Licensing](../legal/data-licensing.md)).
- [ ] Ingestion failures are logged and alertable.

### E1-S3 — Geocoding ⏳
*As a data engineer, I want addresses resolved to coordinates with a cache, so that entities are spatially searchable.*

- [ ] Address → WGS84 via OSM/Nominatim.
- [ ] Local cache avoids duplicate lookups; failed jobs retried.
- [ ] ODbL attribution recorded for geocodes.

### E1-S4 — CareGraph-native loader ⏳
*As a data engineer, I want the enriched dataset loaded into `care_infrastructure`, so that it feeds the API instead of standalone files.*

- [ ] Insurers mapped to `care_infrastructure` (`type='krankenkasse'`) + `krankenkasse_bundesland`.
- [ ] Contribution rates written to `zusatzbeitrag_historie` (append, no overwrite).
- [ ] Idempotent upsert keyed on IK-Nummer / stable key.
- [ ] Runs against Postgres via a write-scoped role.

### E1-S5 — Deduplication ⏳
*As a data engineer, I want duplicate providers merged across sources, so that the dataset is clean.*

- [ ] Match on IK-Nummer, then address + name similarity.
- [ ] Merge strategy keeps provenance of each field.
- [ ] Validation report produced per run.

---

## EPIC 2 — Data Model & Search ⏳
*Reliable spatial storage, indexing, and ultra-fast search. Roadmap Phase 2.*

### E2-S1 — PostGIS schema & migrations ⏳
*As a developer, I want the schema deployed via migrations, so that environments are reproducible.*

- [ ] `care_infrastructure` + `bundeslaender` + junction + `zusatzbeitrag_historie` created.
- [ ] GIST (spatial), GIN (JSONB), and compound indexes present.
- [ ] Migration is idempotent and version-controlled.

### E2-S2 — Typesense sync worker ⏳
*As a developer, I want Postgres data synced into Typesense, so that search stays current.*

- [ ] Scheduled/near-real-time sync from Postgres → Typesense.
- [ ] German-language config, typo tolerance, ranking tuned.
- [ ] Re-sync is safe to re-run.

### E2-S3 — Data validation ⏳
*As a data steward, I want automated validation, so that bad records are caught before serving.*

- [ ] Required-field and format checks (PLZ, IK-Nummer, coordinates).
- [ ] Anomaly report (e.g., missing geocode, out-of-range values).

---

## EPIC 3 — Public API Gateway ⏳
*Low-latency REST API, auth, and scalable request handling. Roadmap Phase 3.*

### E3-S1 — Spatial radius endpoint ⏳
*As Dana (app developer), I want `GET /infrastructure/near`, so that I can find providers around a location.*

- [ ] Params `lat`, `lng`, `radius_km`, `type`, `limit` per the [OpenAPI spec](../api/openapi-spec.md).
- [ ] Backed by `ST_DWithin`, ordered by distance; p95 < 10 ms on indexed data.
- [ ] Validates coordinates → `400` on bad input.

### E3-S2 — Fuzzy search endpoint ⏳
*As Dana, I want `GET /infrastructure/search`, so that users find providers despite typos.*

- [ ] Typo-tolerant query via Typesense; optional `city` filter.
- [ ] `q` shorter than 2 chars → `400`.

### E3-S3 — Entity lookup ⏳
*As Bea (B2B integrator), I want `GET /infrastructure/{ik_nummer}`, so that I can resolve a known institution.*

- [ ] Returns full entity or `404`.
- [ ] IK-Nummer validated against `^[0-9]{9}$`.

### E3-S4 — Auth & rate limiting ⏳
*As the platform operator, I want API-key auth with tiered rate limits, so that usage is controlled and abuse prevented.*

- [ ] `X-API-Key` verified against Argon2id hashes; missing/invalid → `401`.
- [ ] Redis token-bucket limits per tier; exceed → `429`.

### E3-S5 — OpenAPI & docs ⏳
*As a developer, I want a versioned OpenAPI spec, so that I can generate clients.*

- [ ] `openapi.yaml` is the single source of truth; kept in sync with handlers.
- [ ] Published, versioned API docs.

---

## EPIC 4 — Operations & CI/CD ⏳
*Deployment, automation, reliability. Roadmap Phase 4.*

### E4-S1 — Containerization ⏳
*As an operator, I want all components dockerized, so that the stack runs reproducibly.*

- [ ] Images for Go API, Python ingestion, Postgres/PostGIS, Typesense, Redis.
- [ ] `docker compose` brings up the full local stack.

### E4-S2 — CI/CD ⏳
*As a maintainer, I want automated CI, so that quality is enforced on every change.*

- [ ] Build, lint, and test for Go and Python.
- [ ] Docs deploy (MkDocs → GitHub Pages) on change.

### E4-S3 — Observability ⏳
*As an operator, I want health checks and metrics, so that I can monitor the service.*

- [ ] `/healthz` reports DB/Redis/Typesense status.
- [ ] Ingestion run status is tracked and alertable.

---

## EPIC 5 — Open Source, Governance & Funding ⏳
*Sustainable community project. Roadmap Phase 4.*

### E5-S1 — Public repository & licensing ⏳
*As a contributor, I want a clearly licensed public repo, so that I can contribute confidently.*

- [ ] Core published under AGPLv3; docs under CC BY-SA 4.0.
- [ ] `CONTRIBUTING.md`, `SECURITY.md`, issue/PR templates.

### E5-S2 — Governance & data quality ⏳
*As a community member, I want to report data issues, so that quality improves over time.*

- [ ] Structured issue templates for corrections/new sources.
- [ ] RFC/ADR process for schema evolution.

### E5-S3 — Funding applications ⏳
*As the maintainer, I want grant applications prepared, so that development is sustainable.*

- [ ] Prototype Fund / STF drafts completed (see [Funding](funding-proposal.md)).

---

## EPIC 6 — Commercial / DaaS ⏳
*Managed service and enterprise offering. Roadmap Phase 4+.*

### E6-S1 — Tiered API access ⏳
*As Bea, I want Community and Enterprise tiers, so that I can choose the right SLA.*

- [ ] Self-service Community keys (rate-limited).
- [ ] Enterprise tier: higher throughput, dedicated keys, SLA.

### E6-S2 — Managed dataset service ⏳
*As Bea, I want a continuously maintained hosted dataset, so that I don't run ingestion myself.*

- [ ] Live, deduplicated, geocoded dataset kept fresh.
- [ ] Custom export formats and early dataset access for Enterprise.
