# E1-S4 — CareGraph-native loader

|                  |                          |
| :--------------- | :----------------------- |
| **Epic**         | E1 — Ingestion & ETL     |
| **Story Points** | 5                        |
| **Priority**     | High                     |
| **Status**       | ✅ Done (pending review) |

> ← [Epic 1](index.md) · [Backlog](../index.md)

## User Story

As a **data engineer**, I want the enriched dataset loaded into `care_infrastructure`, so that it feeds the API instead of standalone files.

## Description

Replace the prototype file exporter with a loader that writes into CareGraph's unified schema: providers and insurers become `care_infrastructure` rows, regional availability goes into `krankenkasse_bundesland`, and contribution rates are appended to `zusatzbeitrag_historie`.

This is the step that makes the **database the source of truth**. Ingestion runs on a schedule; the API reads from Postgres and never scrapes on request.

## Acceptance Criteria

- [x] Insurers mapped to `care_infrastructure` (`type='krankenkasse'`) + `krankenkasse_bundesland`. *(Providers too.)*
- [x] Contribution rates written to `zusatzbeitrag_historie` (append, no overwrite).
- [x] Idempotent upsert keyed on IK-Nummer / a stable key. *(`source_id`; IK once [E1-S6](e1-s6-ik-enrichment.md) lands.)*
- [x] Runs against Postgres via a write-scoped role. *(`caregraph_ingest`; the gateway gets read-only `caregraph_api` — migration `0003`.)*

## Technical Notes

`pipelines/load/postgres_loader.py`, driven by `pipelines/run_load.py`.

### Two schema problems this story had to solve first

Both only surfaced when the loader met the real 7,522-record dataset; migration `0002_loader_prerequisites.sql` fixes them.

1. **`plz`/`ort` were `NOT NULL`, but 30% of providers have no address.** They do all have coordinates, and for a spatial API `location` is the load-bearing field — rejecting a third of the dataset over a missing postcode would have been the worse trade. Both columns are now nullable; E1-S3 backfills them by reverse geocoding.
2. **There was no upsert key.** Providers have no IK-Nummer and names are not unique, so a re-run could not recognise rows it had already written — the "idempotent" criterion was unimplementable as the schema stood. Added `source_id TEXT NOT NULL UNIQUE`, a source-namespaced external identifier (`osm:node/722542669`, `ik:108616568`).

### Design

- **Upsert:** a single `INSERT … ON CONFLICT (source_id) DO UPDATE`, using `RETURNING (xmax = 0)` to tell inserts from updates for the run report. `created_at` and `source_id` are deliberately excluded from the update set.
- **Geometry is built in SQL** (`ST_SetSRID(ST_MakePoint(lon, lat), 4326)::geography`) so PostGIS owns it; records without coordinates get `NULL`, not a phantom point at (0, 0).
- **State links are replaced, not merged**, so an insurer withdrawing from a state actually loses the link.
- **History is append-only** with `ON CONFLICT (krankenkasse_id, gueltig_ab) DO NOTHING`: re-running the same publication is a no-op, a new publication adds a row, and last year's rate is never destroyed.
- Bundesland normalisation moved to `pipelines/common/`, shared with the exporter and the OSM scraper so the copies cannot drift.

### Least-privilege roles (migration `0003`)

Privileges were derived from the statements the code actually executes, then negative-tested:

| Role | care_infrastructure | krankenkasse_bundesland | zusatzbeitrag_historie | bundeslaender |
| :-- | :-- | :-- | :-- | :-- |
| `caregraph_ingest` | SELECT, INSERT, UPDATE | SELECT, INSERT, DELETE | **SELECT, INSERT only** | SELECT |
| `caregraph_api` | SELECT | SELECT | SELECT | SELECT |

Two deliberate omissions: the pipeline gets **no DELETE on `care_infrastructure`**, so a bug cannot wipe the dataset; and **no UPDATE/DELETE on the history**, which makes the database enforce append-only rather than trusting the loader. Verified by running the real load under `caregraph_ingest` (works) and under `caregraph_api` (fails with *permission denied*).

**No passwords live in the migration** — it creates roles and grants only. `make db-roles-dev` sets throwaway local passwords; production sets them from a secret manager.

### Verified against real data

| | |
| :-- | :-- |
| Providers loaded | **7,522** in ~7 s; re-run: 0 inserted / 7,522 updated |
| Insurers loaded | **92**, plus 185 state links and 92 history rows |
| Re-run of the same publication | `history_rows=0` — append-only holds |
| A later publication | appends; `zusatzbeitrag_aktuell` returns the newer rate |
| Radius query (warm) | **1.7 ms** Bremen, **5.3 ms** Berlin — within the <10 ms target (NFR1), GIST index used |

A cold first query took ~90 ms; that is cache warm-up, not the steady state.

### One bug worth recording

Insurers carry no coordinates, so every coordinate parameter was `NULL` and Postgres refused the statement with *"could not determine data type of parameter"*. The provider path never hit it because those values were real floats. Fixed with explicit `::double precision` casts, and covered by a regression test.

## Dependencies

- **Depends on:** E1-S1 (parsed insurers), E1-S2 (providers), E2-S1 (schema)
- **Blocks:** E3 (the API serves from `care_infrastructure`)

## Risks

- **Insurers are keyed on `gkv:<name>` until [E1-S6](e1-s6-ik-enrichment.md) lands.** A renamed insurer would appear as a new row; the IK-based key removes that.
- **Owner credentials are still needed for migrations.** Only the two runtime roles are least-privilege; schema changes run as the owner, as they must.
- Per-row execution is fine at this size (7.5k in 7 s); a `COPY`-based path would be the lever if the dataset grows by an order of magnitude.

## Definition of Done

- [x] Acceptance criteria fulfilled
- [x] Tests passing (20 loader tests, 167 total; integration tests run against real PostGIS)
- [x] CI covers the new code (PostGIS service container + migrations added to the pipeline)
- [x] Documentation updated
- [x] Code reviewed

## References

- [Data Schema](../../../architecture/data-schema.md) · [Security & Privacy](../../../architecture/security.md)
