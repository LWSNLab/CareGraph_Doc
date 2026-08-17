# E2-S2 — Typesense sync worker

|                  |                          |
| :--------------- | :----------------------- |
| **Epic**         | E2 — Data Model & Search |
| **Story Points** | 5                        |
| **Priority**     | Medium                   |
| **Status**       | ✅ Done (pending review) |

> ← [Epic 2](index.md) · [Backlog](../index.md)

## User Story

As a **developer**, I want Postgres data synced into Typesense, so that search stays current.

## Description

Keep the Typesense index in step with the `care_infrastructure` source of truth,
so fuzzy search reflects the latest data.

## Acceptance Criteria

- [x] Sync from Postgres → Typesense, runnable on a schedule (`make search-sync`,
      and step 3 of `make bootstrap`).
- [x] German-language config and typo tolerance — verified against real queries.
- [x] Re-running is safe: the result depends on the database, not on what the
      index happened to contain.

## Technical Notes

### A full rebuild behind an alias, not an incremental sync

The story suggested "incremental sync keyed on `updated_at`". That was the wrong
call at this size, and the measurement is why: **a complete rebuild of all 9,099
documents takes 0.7–0.9 seconds.**

Incremental sync would buy nothing and cost the one failure this index must not
have — **silent drift**, where a deleted row lives on in search results because
nothing errored. It is the risk this story itself names, and a full rebuild
removes it by construction rather than by monitoring.

The rebuild writes into a fresh collection and only then moves the `providers`
alias:

- readers never see a half-built index, because the alias flips atomically;
- a failed rebuild leaves the **previous** index serving, not an empty one;
- one superseded collection is retained (`--keep`), so an operator can roll the
  alias back by hand.

### Refusing to publish an empty index

If the query returns nothing, the run **fails and leaves the alias alone**.
Swapping to an empty collection would take search down while reporting success —
the same "partial failure presenting as success" pattern that cost a day in
[E1-S4](../epic-1-ingestion/e1-s4-loader.md). A test asserts the alias does not
move.

### German locale is not optional

`locale: "de"` on the text fields is what makes umlauts fold. Verified against
the live index:

| Query | Top hit |
| :-- | :-- |
| `Krankenhaus Munster` | Herz-Jesu Krankenhaus **Münster**-Hiltrup |
| `Charite` | **Charité** Universitätsmedizin Berlin |
| `Caritas Pflegediesnt` | Caritas **Pflegedienst** |

The first two are folding, the third is typo tolerance.

### Insurers are not indexed

They carry no coordinates and are reached by IK. A hit for one would sit in the
same result list while behaving differently from every other entry.
`INDEXED_TYPES` names what goes in — an allowlist, for the same reason
[E4-S5](../epic-4-operations/e4-s5-distributable-dataset.md) uses one: a new type
should not join by default.

### Three defects the first run surfaced

1. **Duplicate `headers` argument.** The client passed `headers` both from the
   instance and from the caller, so every import raised a `TypeError`. Merged.
2. **Collection names collided.** A second-resolution timestamp is not unique
   enough for two runs in the same second — the second failed with a 409. A
   random suffix now disambiguates.
3. **A failed rebuild left an orphan collection.** Litter that accumulates on
   every retry until someone notices the disk. The build is now wrapped, and a
   collection that is never published is dropped.

The third is the one worth remembering: the failure path had never been walked
until an unrelated bug walked it.

## Out of scope

- **The Go search client and the `/search` endpoint** are
  [E3-S2](../epic-3-api-gateway/e3-s2-fuzzy-search.md). This story fills the
  index; that one reads it. `search.Client` already defines the port, so the
  engine stays swappable.
- **Monitoring index/DB drift** ([E4-S3](../epic-4-operations/e4-s3-observability.md)).
  Much less pressing now: with a full rebuild there is no drift to detect, only a
  rebuild that did not run.

## Dependencies

- **Depends on:** E2-S1 (schema), E1-S4 (data loaded)
- **Blocks:** E3-S2 (fuzzy search endpoint)

## Risks

- **The index ages between rebuilds.** Nothing triggers a sync automatically yet;
  it is a step in `make bootstrap` and a manual command otherwise. A scheduled
  run belongs with the ingestion schedule.
- **Typesense is unauthenticated on the dev key.** The compose service is bound
  to loopback for that reason; a deployment needs a real key.

## Definition of Done

- [x] Acceptance criteria fulfilled
- [x] Tests passing — 10 cases, including a guard that geopoints are `[lat, lng]`
      (Typesense's order is the reverse of PostGIS's, and getting it wrong is
      silent), that a failed rebuild leaves no orphan, and that an empty result
      never replaces a working index
- [x] CI covers the new code — the Python job gained a Typesense service **and an
      explicit readiness wait**, because the search tests skip when it is
      unreachable and would otherwise quietly not run
- [x] Documentation updated
- [ ] Code reviewed

## References

- [System Overview](../../../architecture/system-overview.md)
