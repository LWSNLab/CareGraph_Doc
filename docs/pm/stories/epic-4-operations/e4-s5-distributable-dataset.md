# E4-S5 — Distributable dataset

|                  |                       |
| :--------------- | :-------------------- |
| **Epic**         | E4 — Operations & CI/CD |
| **Story Points** | 3                     |
| **Priority**     | High                  |
| **Status**       | ✅ Done |

> ← [Epic 4](index.md) · [Backlog](../index.md)

## User Story

As someone **self-hosting CareGraph**, I want the release to come with usable
data, so that starting the stack gives me a working API instead of an empty
database.

## Description

Today a self-hoster gets this:

```
docker compose up   →  services running
make migrate        →  schema in place
                    →  0 rows
```

Both data sources are **gitignored**: `pipelines/data/processed/providers.json`
(4.1 MB) and `pipelines/data/raw/gkv_liste_2026.pdf` (236 KB). To get any data,
someone would have to run the OSM scraper across all 16 federal states — minutes
of Overpass calls with rate limits — and source the GKV PDF themselves.

**A self-hostable release with an empty database is not a release.** This story
decides what ships with it, and under which licence.

Not covered anywhere else: [E5-S1](../epic-5-open-source/e5-s1-repo-licensing.md)
publishes the *code*, [E4-S1](e4-s1-containerization.md) builds the *images*, and
[E6-S2](../epic-6-commercial/e6-s2-managed-dataset.md) is the *commercial* hosted
dataset — explicitly for people who do **not** want to self-host.

## Three decisions

### 1. What ships — decided: a CSV archive, plus the bootstrap path

**Not `pg_dump`.** A CSV is inspectable, loadable outside Postgres, and does not
carry a server version with it — which matters for data published under an open
licence, where the point is that someone else can use it in their own tools.

The archive holds `providers.csv`, `MANIFEST.json`, `LICENSE.txt` and `README.md`.
**0.5 MB compressed**, not the ~15 MB estimated: CSV of 7,522 rows compresses far
better than a binary dump.

`make bootstrap` covers the other path, and `make bootstrap FILE=…` combines
migrations and import in one step.

### 2. What *may* ship — the actual constraint

**The provider records are not "OSM-geocoded", they *are* OSM.** All 7,522 came
out of Overpass ([E1-S2](../epic-1-ingestion/e1-s2-provider-scrapers.md)). That
makes the table a Derivative Database under ODbL, and share-alike applies
squarely — which is clearer, not murkier: **distributing it under ODbL with
attribution is permitted.**

This corrects the framing in [Data Sources & Licensing](../../../legal/data-licensing.md),
whose open question asks whether "storing OSM/Nominatim *geocodes* at scale"
triggers share-alike. For the provider table the question does not arise; the
rows are the OSM data.

The insurers are the unclear part. They are re-derived from an official GKV
publication, and the same document records the output licence as *"to be
decided"*.

**Recommended path:** ship a **providers-only dump** (ODbL, attribution
included), and let the bootstrap load the insurers from the official PDF. That
avoids mixing sources with different rights in one file — where the file would
otherwise inherit the most restrictive of them — and it is not blocked on a
decision that is still open.

### 3. Where it lives

**GitHub Releases**, not the repository. A 15 MB binary in git grows with every
version and can never be removed from history. A release asset is versioned,
described, and replaceable.

## Acceptance Criteria

- [x] `docker compose up` followed by a documented one-liner yields a database
      with data in it — verified against a **freshly created database** built
      only from the migrations: 7,522 rows, 100 % with coordinates.
- [x] The shipped artefact carries its licence and attribution *inside* it —
      `LICENSE.txt` and `README.md` travel in the archive, not only on a release
      page.
- [x] The output licence is decided and recorded: **ODbL v1.0** with attribution,
      in [Data Sources & Licensing](../../../legal/data-licensing.md).
- [x] Reproducible: `make dataset-export` regenerates it, and CI performs a full
      export/import round trip on every run.
- [x] The README states what the data is, when it was cut, and what it is not
      (no provider IKs, ~28 % without a full address, insurers excluded).

## Technical Notes

**Interaction with Typesense ([E2-S2](../epic-2-data-and-search/e2-s2-typesense-sync.md)).**
A `pg_dump` restores Postgres — it does **not** restore the search index, which
lives in a separate service. The sync worker therefore needs a first-run path
that detects an empty index and builds it from Postgres. That is a core part of
E2-S2, not an afterthought: the obvious implementation only handles incremental
updates and leaves a fresh self-hoster with a working API and an empty `/search`.

**The import goes through the ordinary loader**, not a direct `COPY`. That keeps
idempotency, website normalisation and key resolution identical to ingestion —
a second way into the database would be a second set of rules to keep in step.
Verified: a second import reports `inserted=0 updated=7522`.

**A defect this surfaced.** `_provider_params` derived `osm:<type>/<id>` for
*every* dict record and ignored an explicit `source_id`, hardcoding one source
into a source-agnostic loader. Harmless until now — the scraper's records carry
no `source_id` — but it made re-importing an export impossible without rekeying
every row as if it came from OpenStreetMap, and it would have mis-keyed the
hospital directory ([E1-S9](../epic-1-ingestion/e1-s9-hospital-standortverzeichnis.md))
the same way. An explicit `source_id` now wins; the OSM derivation is the
fallback.

**The manifest records the schema migration** the archive was cut against, and
an import refuses a mismatch rather than failing obscurely halfway through.
`--allow-schema-mismatch` overrides it deliberately.

**Size.** 0.5 MB compressed for 7,522 rows. The hospitals would roughly triple
that — still small, but a reason to keep it in releases rather than in git.

## Dependencies

- **Depends on:** E1-S2, E1-S4 (there has to be a dataset to distribute)
- **Blocks:** [E4-S1](e4-s1-containerization.md) — the container's start-up path
  differs depending on whether it restores a dump or runs a pipeline.
  [E5-S1](../epic-5-open-source/e5-s1-repo-licensing.md) is not usefully done
  before this either: a public repo whose stack starts empty invites the same
  question from every visitor.

## Risks

- **Mixing sources in one artefact makes it inherit the strictest licence.**
  The reason for the providers-only recommendation.
- **A stale dump is worse than no dump** if nothing states when it was cut. Hence
  the acceptance criterion about the cut date.
- **Republishing insurer data is not yet cleared.** If it stays that way, the
  bootstrap path is the only route for that half — which is fine, but the README
  must say so rather than leaving someone to discover it.
- **The dump embeds a schema version.** Restoring an old artefact against newer
  migrations will break; the release notes must name the migration it was cut at.

## Definition of Done

- [x] Acceptance criteria fulfilled
- [x] Tests passing — 16 cases covering archive validation, CSV type coercion
      (empty cell ≠ empty string, missing coordinate ≠ Null Island), the schema
      guard and the loader keying fix. Verified against **both** a populated and
      an empty database, because the first version of the integration tests
      asserted against ambient data: they passed locally and failed in CI, where
      the schema is built from migrations and holds nothing. They now seed their
      own rows and clean up after themselves.
- [x] CI covers the new code — the Python job now performs an export/import round
      trip against a schema built purely from migrations, which is the situation a
      self-hoster is in
- [x] Documentation updated — README rewritten: the Quick Start led to an empty
      database and a `401`, and the Status section still claimed the domain
      methods were stubs
- [x] Code reviewed

## References

- [Data Sources & Licensing](../../../legal/data-licensing.md) ·
  [ODbL](https://opendatacommons.org/licenses/odbl/)
