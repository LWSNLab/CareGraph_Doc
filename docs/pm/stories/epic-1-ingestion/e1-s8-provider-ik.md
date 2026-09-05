# E1-S8 — Provider IK numbers (data-sharing route)

|                  |                          |
| :--------------- | :----------------------- |
| **Epic**         | E1 — Ingestion & ETL     |
| **Story Points** | 5                        |
| **Priority**     | High                     |
| **Status**       | ❌ Won't do — refused in writing 2026-09-04 |

> ← [Epic 1](index.md) · [Backlog](../index.md)

## User Story

As a **B2B integrator**, I want care providers to carry their Institutionskennzeichen, so that I can match CareGraph records against my own systems and address them through the API.

## Description

Every Leistungserbringer billing with German social insurance holds an IK — it is *the* identifier the sector matches on. [E1-S6](e1-s6-ik-enrichment.md) resolved them for the statutory insurers, where a public source exists. For care providers no such source does, so all 7,522 of them carry `ik_nummer: null`.

This story is mostly **not a coding task**: the work is obtaining lawful access to the data, then a comparatively small ingestion step.

## Outcome

**Closed without the data, 2026-09-04.** The access route this story set out to
find does not exist. It was not abandoned for cost or difficulty — it was walked
to its end and refused in writing by the body named as competent.

That makes this story documentation rather than a plan, and useful as such: the
absence of provider IKs in CareGraph is now an answered question with a paper
trail, not a gap someone will keep re-opening.

**What it costs is smaller than it looked.** The IK was never needed to *find* a
provider — that is name, region and coordinates, and it works. It was needed to
*match* one against a third party's records, which is the B2B integrator in the
user story below. That use case is closed; search and radius lookup are not
affected.

## Acceptance Criteria

*Not met, and no longer pursued — see Outcome.*

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

### The clarification worked

Answered the next day, 2026-08-25, and it settled three things.

The IK is in **neither** the DatenClearingStelle's data **nor** the price and
comparison lists under § 7 Abs. 3 — stated by the body best placed to know, which
closes both routes and retires the hope that access there would improve the
provider records as a side effect. It does not: those lists do not carry the
number.

The IK is a **contract datum**, so the holder is the contracting party. That is
the same conclusion § 72 SGB XI supports, now confirmed rather than inferred.

And the part that changes the plan: a **Verband der Pflegekassen auf Bundesebene**
— the vdek or the AOK-Bundesverband — can be approached *on behalf of* the
Landesverbände. Sixteen doors become one. That question was the reason for
clarifying instead of writing sixteen letters, and it paid for itself in a day.

The remaining obstacle is smaller and more ordinary: an earlier approach to the
vdek went unanswered, almost certainly because it reached a general address
rather than a desk. A third mail therefore asks the same contact for a named one,
offers to copy her in so the referral is visible to the recipient, and mentions
forwarding only as the softest option — a name costs her nothing, forwarding
spends her own standing.

The contacts that could be established, and the ones that deliberately could not,
are recorded in `internal/contacts-pflegekassen.md`.

### And then the answer, 2026-09-04

The GKV-Spitzenverband asked for consent and forwarded the whole thread to a
colleague — more than the name that had been requested. The vdek answered as a
Bundesverband, that is, on behalf of the Landesverbände, and declined:

- The IK is in neither the § 115 Abs. 1a quality data nor the § 7 Abs. 3 lists,
  and therefore **not among the data whose publication is legally provided for**.
- It exists to identify Leistungserbringer in administrative and billing
  procedures — not as a record made available for wider public use.
- ARGE·IK does not publish provider IKs either, which they cite as evidence of
  what kind of data it is rather than as a coincidence.

Three bodies, one conclusion, and no contradiction between them. The ARGE·IK
finding recorded in this story two months earlier — that the organisation issuing
every IK deliberately excludes Leistungserbringer — turns out to have been the
whole answer; the rest was confirmation.

**Not appealed, deliberately.** There is a soft spot in the reasoning: *no basis
to provide* conflates "not obliged to publish" with "not permitted to share",
and what was asked for was a discretionary release on their own terms. But a
rebuttal to a considered decision rarely reverses it, and the sector is small
enough that the same people reappear. The AOK-Bundesverband, the other body named,
was not asked either: the vdek answered on behalf of the Landesverbände, and
re-asking a sister association after a documented refusal is shopping for an
answer, not seeking one.

**What the correspondence is worth.** For a funding application, *"we asked the
competent bodies, here is their written answer"* carries further than *"the data
could not be found"*. It documents diligence, and it documents something about
German care-data infrastructure worth naming: the key the entire sector settles
accounts on is unavailable to anyone outside the settling. There is no list of sixteen
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
- **Blocked:** ~~the IK lookup endpoint for providers; materially improves
  [E1-S5](e1-s5-deduplication.md)~~ — both are now permanent. Providers cannot be
  addressed by IK, and deduplication has to work on name and address similarity
  without a strong key ever arriving. E1-S5's own rule carries more weight for
  it: **refuse rather than guess**, because a wrong merge is as silent as a wrong
  IK would have been.

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
