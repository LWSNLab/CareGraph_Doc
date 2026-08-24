# E1-S9 — Hospitals from the Bundes-Klinik-Atlas

|                  |                          |
| :--------------- | :----------------------- |
| **Epic**         | E1 — Ingestion & ETL     |
| **Story Points** | 3                        |
| **Priority**     | High                     |
| **Status**       | ✅ Done |

> ← [Epic 1](index.md) · [Backlog](../index.md)

## User Story

As a **user looking for care**, I want hospitals in the graph alongside care
providers, so that a search covers the whole chain instead of stopping at the
boundary between SGB V and SGB XI.

## Description

Ingest the **Bundes-Klinik-Atlas** open-data export — the Federal Ministry of
Health's hospital transparency directory under § 135d SGB V, prepared by the
IQTIG — as a new `care_infrastructure` type.

This turns CareGraph from a care directory into a cross-sector one. Today the
dataset stops at the boundary a patient actually crosses: hospital → rehab →
outpatient care.

> **Rewritten 2026-08-15.** This story was originally built on the
> *Standortverzeichnis* (§ 293 Abs. 6 SGB V) and was blocked on a redistribution
> question. The Bundes-Klinik-Atlas turned out to be the better primary source:
> freely downloadable, statutorily public, and carrying quality data the
> Standortverzeichnis does not. The Standortverzeichnis is now an optional
> enrichment for the one field the Atlas lacks — see *Later*.

## Why this source

| | Bundes-Klinik-Atlas | Standortverzeichnis |
| :-- | :-- | :-- |
| Access | **open download, no registration** | registration required, redistribution unaddressed |
| Legal basis | § 135d Abs. 1 SGB V — a public **right** to the data in machine-readable form | § 293 Abs. 6 SGB V, retrieval after sign-up |
| Records | 1,577 hospitals | 15,685 locations incl. outpatient clinics |
| Coordinates | 100 % | 100 % |
| **IK** | ✗ | ✓ |
| Structure & quality data | ✓ beds, cases, nursing ratio, emergency level, certificates, departments | ✗ |

Both carry `STOID` / `StandortId`, so they join on it. That is what makes the
Atlas sufficient on its own and the Standortverzeichnis an optional top-up.

## Licence: ship the pipeline, not the data

The open-data page states the public right to the data but **names no licence**,
and says nothing about redistribution. Rather than wait on that:

**CareGraph distributes the parser, not the file.** A self-hoster downloads the
export themselves — they hold the same § 135d right — and runs the loader against
it. CareGraph redistributes nothing, so the question does not arise.

Concretely: **hospitals are not part of the dataset archive** from
[E4-S5](../epic-4-operations/e4-s5-distributable-dataset.md), which stays
providers-only under ODbL. If redistribution is clarified later, adding them is
an extension rather than a correction.

## Acceptance Criteria

- [x] The export is parsed with the root element checked, so a foreign XML fails
      with a readable error instead of loading nothing.
- [x] Hospitals load as `care_infrastructure` with `type = 'krankenhaus'`,
      carrying name, address, coordinates and `STOID` as the key — **1,577 rows,
      100 % with coordinates and Bundesland**.
- [x] Structure and quality attributes preserved in `details` — beds, cases,
      nursing-staff ratio, emergency level, certificates, departments, diseases.
- [x] Federal states map to the canonical `bundeslaender` names, asserted by test.
- [x] Idempotent: a second run reports `inserted=0 updated=1577`.
- [x] The download is **not** committed — `pipelines/data/raw/*` is now ignored
      wholesale, replacing a `*.pdf` rule that left a 5.4 MB export one
      `git add -A` from the history.

## Technical Notes

**No scraping, no geocoding, no fuzzy matching.** All three expensive problems of
the care-provider pipeline are absent — the source carries every field.

Measured on the 2026-07-28 export:

| | |
| :-- | --: |
| Hospitals | 1,577 |
| STOID unique | 1,577 / 1,577 |
| Name, address, coordinates | **100 %** |
| URL | 95 % |
| With departments / diseases | 1,575 / 1,483 |

**`Land` uses non-ISO codes.** Bayern is `BA`, not `BY`. A naive ISO mapping
would drop 277 hospitals or file them nowhere. The mapping is verified against
the distribution: `NW` 328 (largest state), `BA` 277, `HB` 12 (smallest) — all
consistent with reality.

**The key is `STOID`**, not the name: `source_id = "stoid:<STOID>"`. It is unique
across all 1,577, stable across publications, and the join key to the
Standortverzeichnis should the IK be added later.

**No IK, and that is expected.** Hospitals join the 7,522 care providers in
having `ik_nummer = NULL`. Unlike the providers, though, theirs *is* publicly
obtainable — see *Later*.

**A new `provider_type` enum value** is required (migration), plus the API's
`type` filter and the OpenAPI enum.

## Later — IK enrichment

The Standortverzeichnis supplies the IK per `StandortId`. It needs a free
self-service registration and its redistribution terms are unclear, so it stays
out of this story. Once clarified it is a join on a key both sides already carry
— an enrichment step in the shape of [E1-S6](e1-s6-ik-enrichment.md), not a
re-ingest.

## Out of scope

- **G-BA quality reports** (§ 136b SGB V). The Atlas already carries the quality
  layer that mattered; the full reports remain a separate product question with
  their own order process.
- **Rehabilitation and Vorsorge facilities** — not in this directory.
- **Shipping hospitals in the distributable dataset** — see *Licence* above.

## Dependencies

- **Depends on:** E1-S4 (the loader), E2-S1 (schema — needs the new enum value)
- **Blocks:** nothing. Independent of [E1-S8](e1-s8-provider-ik.md), which waits
  on a different institution.

## Risks

- **The schema is marked `Alpha_3`.** An alpha-stage export format can change
  without ceremony; validating against the XSD is what turns that into a clear
  failure instead of silently missing fields.
- **A snapshot, not a feed.** The export is published periodically; the loaded
  data ages until someone re-runs it. `details` records the export date.
- **1,577 hospitals against 7,522 providers** shifts what a radius search
  returns. Worth re-checking how `type` filtering behaves afterwards.
- **Case numbers invite over-reading.** `AnzahlFaelle` is a count, not a quality
  judgement. It is stored as given, and the API must not present it as a ranking.

## A defect this surfaced

**The dataset export would have shipped the hospitals.** E4-S5's filter read
`type <> 'krankenkasse'` — an exclusion, so every type added later joined the
ODbL-licensed archive silently, and this story added one whose redistribution
terms are unsettled. Changed to an allowlist: `EXPORTABLE_TYPES` names what may
go in, so extending it is a licence decision rather than a filter change.
Verified — with 9,192 rows in the database the export still writes 7,522.

## Definition of Done

- [x] Acceptance criteria fulfilled
- [x] Tests passing — 10 parser cases driven by literal XML (so the suite does
      not depend on a download that is deliberately absent), plus a guard that
      latitude and longitude are not transposed, plus two on the export allowlist
- [x] CI covers the new code
- [x] Documentation updated — `krankenhaus` added to the `ProviderType` enum in
      `openapi.yaml` and to the API page
- [x] Code reviewed

## References

- [Bundes-Klinik-Atlas Open Data](https://bundes-klinik-atlas.de/open-data/) ·
  [Datengrundlage](https://bundes-klinik-atlas.de/datengrundlage/)
- [§ 135d SGB V](https://www.gesetze-im-internet.de/sgb_5/__135d.html) ·
  [§ 293 SGB V](https://www.gesetze-im-internet.de/sgb_5/__293.html)
- [Data Sources & Licensing](../../../legal/data-licensing.md)
