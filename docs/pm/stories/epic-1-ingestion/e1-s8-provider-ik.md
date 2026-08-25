# E1-S8 — Provider IK numbers (data-sharing route)

|                  |                          |
| :--------------- | :----------------------- |
| **Epic**         | E1 — Ingestion & ETL     |
| **Story Points** | 5                        |
| **Priority**     | High                     |
| **Status**       | 🔄 In Progress — referred onward, see below |

> ← [Epic 1](index.md) · [Backlog](../index.md)

## User Story

As a **B2B integrator**, I want care providers to carry their Institutionskennzeichen, so that I can match CareGraph records against my own systems and address them through the API.

## Description

Every Leistungserbringer billing with German social insurance holds an IK — it is *the* identifier the sector matches on. [E1-S6](e1-s6-ik-enrichment.md) resolved them for the statutory insurers, where a public source exists. For care providers no such source does, so all 7,522 of them carry `ik_nummer: null`.

This story is mostly **not a coding task**: the work is obtaining lawful access to the data, then a comparatively small ingestion step.

## Acceptance Criteria

- [ ] A lawful access route to provider IKs is established (agreement, official export, or a source that turns out to publish them).
- [ ] IKs are loaded into `care_infrastructure.ik_nummer` for the covered providers.
- [ ] Providers are rekeyed from `osm:…` to `ik:…` without creating duplicates, as insurers were.
- [ ] Coverage and provenance are reported per run; gaps stay visible.
- [ ] `GET /infrastructure/{ik_nummer}` resolves providers, and its documented caveat is removed.

## Technical Notes

**Why this is blocked on access, not on code.** Checked and ruled out:

| Source | Result |
| :-- | :-- |
| Kostenträgerdateien (4 sectors) | list *Kostenträger* (payers), not Leistungserbringer |
| Schlüsselverzeichnis 8a | insurers only |
| GovData / municipal open data | sampled datasets carry coordinates, address, operator, capacity — **no IK column** |
| Pflegelotse / AOK Pflegenavigator | hold the data, but `robots.txt` disallows the pages and they are protected databases (see [E1-S2](e1-s2-provider-scrapers.md)) |
| **ARGE·IK IK-/Adress-Suche** (the body that *issues* IKs) | states it plainly: *"Die Daten der Leistungserbringer sind in der Datenbank nicht enthalten."* Its address pool is payers only — KV/RV/UV-Träger, Sozialhilfeträger, Versorgungs- und Gesundheitsämter, Pflegekassen. |

The ARGE·IK finding is the most decisive of these: the organisation that assigns every IK deliberately does not publish those of Leistungserbringer. Provider IKs are therefore not "public data that merely needs collecting" — they are not published anywhere.

**The route is to ask the bodies that hold the data — not ARGE·IK.** ARGE·IK issues the numbers but excludes providers from its published database, so an enquiry there concerns a product that does not exist. The pairing of provider and IK sits with the **DatenClearingStelle Pflege (DCS)** and the **Landesverbände der Pflegekassen**, who operate the § 7 SGB XI transparency portals, coordinated by the GKV-Spitzenverband.

We would like to work **with** these bodies rather than around them. The § 7 SGB XI data is legally intended for publication, and the portals exist to discharge that transparency duty; a machine-readable export would serve the same purpose for municipalities, researchers and application developers who today cannot use the data programmatically. Corrections we find during processing — outdated addresses, duplicates — we would gladly return.

Whether and on what terms such an export is possible is theirs to decide, and any conditions attached would be adopted in full. A draft enquiry is kept outside the published documentation (`internal/`).

## What came back

Asked the GKV-Spitzenverband on **2026-08-10**; answered **2026-08-24**. Not a
refusal — a referral to the **zuständiger Landesverband der Pflegekassen**, which
is one of the two holders this story had already identified. The analysis above
was right about where the data sits.

It does not answer the question that was asked. The reply speaks about § 115
Abs. 1a/1b and § 7 Abs. 3 SGB XI — quality reporting, care information, price and
comparison lists — and never mentions Institutionskennzeichen. Either the
enquiry was read as one about quality data, or it was written ambiguously enough
to be. Sending sixteen letters on that footing would have produced sixteen
answers about the wrong dataset.

Two things follow, and they run in sequence rather than in parallel — decided
2026-08-25, against the first plan. Parallel would have saved waiting; sequential
saves guessing, and guessing is the expensive part. Nobody publishes which body
leads the working group for a given task, so a letter sent before the referral is
clarified is addressed partly by inference. If the reply names the
DatenClearingStelle or a specific Landesverband, that inference disappears:

- **A clarification back to the same desk**, saying plainly that this is about one
  field per facility, and asking whether the DatenClearingStelle Pflege is the
  central route or whether each Landesverband really must be asked separately.
  Only the coordinating body can answer that one.
- **Then one** Landesverband as a pilot, to learn the procedure — whether it is
  possible at all, in what form, on what terms, and whether there is a form or an
  agreement. Whatever comes back applies to the other fifteen. A first contact can
  only be made once per body, which is the argument against fanning out early: if
  the pilot turns out to name a regular application process, the remaining fifteen
  are paperwork rather than introductions and can go out together.

The contacts that could be established, and the ones that deliberately could not,
are recorded in `internal/contacts-pflegekassen.md`. There is no list of sixteen
addresses, and that is a finding rather than a gap: the Landesverbände are working
groups that divide tasks among themselves, so the leading fund depends on the
subject as well as the state. The reliable anchor is § 72 SGB XI — whoever
administers the Versorgungsvertrag holds the register.

Both drafts are in `internal/`, and both now link the public repository. That is
worth more than the prose around it: `db/migrations/0001_init.sql` shows
`ik_nummer` already modelled and unique, so the ask is concrete rather than
speculative, and `pipelines/dataset/export.py` shows Bundes-Klinik-Atlas records
ingested but withheld from every published archive while a redistribution
question is open. A data holder asking "what would you do with it" can read the
answer instead of being told.

The letters therefore offer two routes explicitly — internal use only, or
inclusion in the published dataset under their licence and attribution — and the
first is enforceable rather than promised, because the exporter carries an
allowlist.

**A side benefit if this route holds.** The reply itself names the § 7 Abs. 3
price and comparison lists. [Data Sources & Licensing](../../../legal/data-licensing.md)
records those directories as the strongest legal footing available and also
records that they are *not* ingested — providers come from OpenStreetMap. Access
through this route would improve the provider records themselves, not only add a
column.

⚠️ **"It is already public" is not a licence.** Individual facts are free, but a compiled directory can be protected under the *sui generis* database right (§§ 87a ff. UrhG), and aggregating a substantial part centrally is precisely the case that right addresses. The request should therefore ask for **permission and terms**, not assert that none are needed — see [Data Sources & Licensing](../../../legal/data-licensing.md).

**Once access exists, the loading is small.** The rekeying mechanism already exists from E1-S6 (`source_id` rewritten in place before the upsert), and `ik_nummer` is already modelled and indexed as unique. The main new work is matching provider records to IK records, which will be harder than for insurers: 7,522 rows, no clean directory, and names far less standardised. Expect [E1-S5](e1-s5-deduplication.md)-style address and name similarity, with the same rule as E1-S6 — **refuse rather than guess**, because a wrong IK is silent.

## Dependencies

- **Depends on:** E1-S2 (the provider records to enrich)
- **Blocks:** the IK lookup endpoint for providers; materially improves [E1-S5](e1-s5-deduplication.md), which currently has no strong key for providers

## Risks

- **Not fully in our control.** A data-sharing request can be refused or take months; the story should not block Phase 1 from completing.
- **Licence terms may come attached** to a negotiated export and could constrain redistribution — exactly the question raised in [Data Sources & Licensing](../../../legal/data-licensing.md). Clarify before ingesting, not after.
- **Partial coverage is likely** even with access; the API caveat may need to become "most providers" rather than disappear.

## Definition of Done

- [ ] Acceptance criteria fulfilled
- [ ] Tests passing (unit + integration where relevant)
- [ ] CI covers the new code (pipeline extended if needed)
- [ ] Documentation updated
- [ ] Code reviewed

## References

- [E1-S6 — IK enrichment (insurers)](e1-s6-ik-enrichment.md) · [Data Sources & Licensing](../../../legal/data-licensing.md) · [API Specification](../../../api/openapi-spec.md)
