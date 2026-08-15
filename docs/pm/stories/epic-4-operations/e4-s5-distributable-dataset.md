# E4-S5 — Distributable dataset

|                  |                       |
| :--------------- | :-------------------- |
| **Epic**         | E4 — Operations & CI/CD |
| **Story Points** | 3                     |
| **Priority**     | High                  |
| **Status**       | ⏳ Planned            |

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

### 1. What ships

| Option | For | Against |
| :-- | :-- | :-- |
| **`pg_dump` artefact** | works immediately, no network, no rate limits | ~15 MB, goes stale, must be regenerated per release |
| **`make bootstrap`** | always current, nothing to maintain | ~40 min, needs Overpass; a rate-limit error on someone's first run looks like a broken project |

Both is also an option: a dump for the quick start, the bootstrap documented for
those who want fresh data.

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

- [ ] `docker compose up` followed by a documented one-liner yields a database
      with data in it — verified from a clean clone on a machine that has never
      run the pipelines.
- [ ] The shipped artefact carries its licence and attribution *inside* it (a
      `LICENSE`/`README` in the archive, not only on the release page).
- [ ] The output licence for the distributed dataset is decided and recorded in
      [Data Sources & Licensing](../../../legal/data-licensing.md), replacing the
      current "to be decided".
- [ ] The dump is reproducible: a documented command regenerates it, so it is not
      a hand-made file nobody can rebuild.
- [ ] The README states plainly what the data is, when it was cut, and what it is
      not (no provider IKs, ~32 % without a full address).

## Technical Notes

**Interaction with Typesense ([E2-S2](../epic-2-data-and-search/e2-s2-typesense-sync.md)).**
A `pg_dump` restores Postgres — it does **not** restore the search index, which
lives in a separate service. The sync worker therefore needs a first-run path
that detects an empty index and builds it from Postgres. That is a core part of
E2-S2, not an afterthought: the obvious implementation only handles incremental
updates and leaves a fresh self-hoster with a working API and an empty `/search`.

**Reproducibility over convenience.** `pg_dump --data-only` for
`care_infrastructure` plus the satellite tables, restored after `make migrate`,
keeps the schema owned by the migrations rather than baked into the artefact.

**Size.** 15 MB for 7,615 rows today; the hospitals ([E1-S9](../epic-1-ingestion/e1-s9-hospital-standortverzeichnis.md))
would roughly triple the row count. Compressed it stays well inside a release
asset, but it is a reason not to put it in git.

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

- [ ] Acceptance criteria fulfilled
- [ ] Tests passing (unit + integration where relevant)
- [ ] CI covers the new code (pipeline extended if needed)
- [ ] Documentation updated
- [ ] Code reviewed

## References

- [Data Sources & Licensing](../../../legal/data-licensing.md) ·
  [ODbL](https://opendatacommons.org/licenses/odbl/)
