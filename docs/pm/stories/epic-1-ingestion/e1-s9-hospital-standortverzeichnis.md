# E1-S9 — Hospitals from the Standortverzeichnis

|                  |                          |
| :--------------- | :----------------------- |
| **Epic**         | E1 — Ingestion & ETL     |
| **Story Points** | 5                        |
| **Priority**     | Medium                   |
| **Status**       | ⛔ Blocked — licence question open |

> ← [Epic 1](index.md) · [Backlog](../index.md)

## User Story

As a **user looking for care**, I want hospitals in the graph alongside care
providers, so that a search covers the whole chain instead of stopping at the
boundary between SGB V and SGB XI.

## Description

Ingest the **Standortverzeichnis nach § 293 Abs. 6 SGB V** — the statutory
directory of every hospital location licensed under § 108 SGB V and its
outpatient clinics — as a new `care_infrastructure` type.

This is the directory layer only: who exists, where, under which identifiers.
Quality-report content (Fachabteilungen, Fallzahlen, indicators) is explicitly
not part of this story; see *Out of scope*.

## ⛔ Precondition: redistribution must be clarified first

**Do not start the ingest before this is answered.** Everything else can proceed.

The Verzeichnisvereinbarung says the contents are *published* in machine-readable
form (§ 2 Abs. 2) but that **"Voraussetzung für den Abruf ist eine Anmeldung bei
der Verzeichnisstelle"** (§ 2 Abs. 3). The site repeats this: public to search and
download, *registration required*.

Two things follow:

1. **Register first.** Self-service at `krankenhausstandorte.de/register`, free,
   no application form. This is the front door.
2. **Redistribution is nowhere addressed.** Publication in a statutory directory
   is not by itself permission to republish through a third-party API, and a
   compiled directory can attract protection under §§ 87a ff. UrhG even where
   each fact is public — the same reasoning already applied to the care data.

**The retrieval files are currently reachable without any login** (open directory
index, permissive `robots.txt`). That is an implementation gap, not a permission.
Building on it would be exactly the "it is public anyway" argument this project
deliberately does not make — see the tone guidance in the data-request template.

Contact: `info@krankenhausstandorte.de`. Unlike the [E1-S8](e1-s8-provider-ik.md)
request this is an enquiry about a running, routine process with a named desk,
not a cooperation decision — a materially better position.

## Acceptance Criteria

- [ ] Registered with the Verzeichnisstelle; redistribution terms answered in
      writing and recorded in [Data Sources & Licensing](../../../legal/data-licensing.md).
- [ ] Weekly complete XML parsed into provider records; the published XSD is used
      to validate rather than trusting the shape.
- [ ] Hospitals loaded as `care_infrastructure` with `type = 'krankenhaus'`,
      carrying **IK, Standortnummer, address and coordinates** from the source.
- [ ] Only currently valid entries are loaded (`Aktiv`, `GültigVon`/`GültigBis`).
- [ ] The load is idempotent on re-run, keyed on the Standortnummer.
- [ ] Attribution recorded per record, in whatever form the answer above requires.

## Technical Notes

**No scraping, no geocoding, no fuzzy matching.** The three problems that make the
care-provider pipeline expensive do not exist here — the source carries every
field already. Verified against the real file:

```xml
<ReferenzKrankenhaus><IK>260551132</IK></ReferenzKrankenhaus>
<StandortId>771077</StandortId>
<Bezeichnung>Josephs-Hospital Warendorf</Bezeichnung>
<Längengrad>8.002352893336</Längengrad>
<Breitengrad>51.960420529706</Breitengrad>
<Straße>Am Krankenhaus</Straße><Hausnummer>2</Hausnummer>
<PLZ>48231</PLZ><Ort>Warendorf</Ort>
<Gemeindeschlüssel>05570052</Gemeindeschlüssel>
<Einrichtung><Standortnummer>771077015</Standortnummer>
  <AbrechnungsIK>260551132</AbrechnungsIK></Einrichtung>
```

Measured on one of the two weekly files (2026-08-14, part 2 of 2):

| | |
| :-- | --: |
| Standorte | 15,685 |
| active | 15,678 |
| **with coordinates** | **100 %** |
| distinct hospital IKs | 1,765 |
| Einrichtungen (departments, clinics) | 107,101 |

**Two decisions the data forces.**

*What is a row?* A `Standort` has many `Einrichtung` children — 107,101 of them
against 15,685 locations. Loading every Einrichtung would swamp the 7,522 care
providers with hospital departments and make a radius search useless. **Load
`Standort`, not `Einrichtung`**, and keep the Einrichtungstyp list in `details`.

*What is the key?* The **Standortnummer**, not the IK. A hospital operator holds
one IK across many locations, so the IK is not unique per row; the Standortnummer
is, and it is mandatory in billing, which is why the directory exists at all.
`source_id` becomes `standort:<Standortnummer>`.

**`ik_nummer` finally gets used for providers.** Until now it was populated for
insurers only, and 0 of 7,522 care providers had one. Hospitals arrive with it —
the first Leistungserbringer in the dataset that do.

**Historisation is available.** `GültigVon`/`GültigBis`/`Aktiv` are per record, and
past validity periods are retrievable. Out of scope here (load the current state),
but it is the natural source for a future time series.

Implementation under `pipelines/parsers/standortverzeichnis.py`, loaded through
the existing `PostgresLoader` — the loader is source-agnostic and already carries
providers and insurers. A new `provider_type` enum value is needed.

## Out of scope

- **G-BA quality reports** (§ 136b SGB V) — Fachabteilungen, Fallzahlen,
  indicators. A different product question: a directory has no equivalent in
  Germany, whereas quality comparison already has the state-funded
  Bundes-Klinik-Atlas. Also a separate access process (order form, not
  self-service). Decide that on its merits, not as a side effect of this story.
- **Ambulanzen as separate rows** — they are Einrichtungen of a Standort here.
- **Rehabilitation and Vorsorge facilities** — not in this directory.

## Dependencies

- **Depends on:** E1-S4 (the loader), E2-S1 (schema — needs the new enum value)
- **Blocks:** nothing. Independent of [E1-S8](e1-s8-provider-ik.md), which is
  waiting on a different institution.

## Risks

- **Redistribution may be refused or restricted.** Then the story stops at the
  precondition, and the work is one unused parser rather than a wrong dataset.
- **Scope drift into quality data.** The quality reports are the interesting-looking
  part and the one that changes what the product is. Keeping them out is the point
  of the *Out of scope* section, not an oversight.
- **The two-part weekly file is a moving target.** It was split in January 2026 and
  could be split further; the parser must discover the parts rather than hardcode
  two.
- **15,685 locations against 7,522 care providers** shifts the dataset's centre of
  gravity. Worth checking how `type` filtering behaves in the API afterwards.

## Definition of Done

- [ ] Acceptance criteria fulfilled
- [ ] Tests passing (unit + integration where relevant)
- [ ] CI covers the new code (pipeline extended if needed)
- [ ] Documentation updated
- [ ] Code reviewed

## References

- [§ 293 Abs. 6 SGB V](https://www.gesetze-im-internet.de/sgb_5/__293.html) ·
  [§ 2a KHG](https://www.gesetze-im-internet.de/khg/__2a.html)
- [Verzeichnisvereinbarung](https://www.dkgev.de/fileadmin/default/Mediapool/2_Themen/2.1_Digitalisierung_Daten/2.1.2._Informationstechnik_im_Krankenhaus/2.1.2.1._Verzeichnisse_und_Register/2025-06-01_Verzeichnisvereinbarung_gemaess____293_Absatz_6_SGB_V_.pdf) ·
  [Standortverzeichnis](https://krankenhausstandorte.de/)
- [Data Sources & Licensing](../../../legal/data-licensing.md)
