# ⚖️ Data Sources & Licensing

> **Status:** Living document — informational, **not legal advice**. Obtain qualified counsel before the commercial launch.
> **Core distinction:** the *code* license (AGPLv3) and the *data* rights are two separate questions.

---

## 1. Why This Matters

AGPLv3 governs CareGraph's **source code**. It says nothing about the **data** CareGraph ingests and republishes. For a project that scrapes public directories and then offers a commercial Data-as-a-Service, the data's legal basis is the single biggest real-world risk — and it is the first question funders (Prototype Fund, STF) and enterprise customers will ask.

Two legal facts frame everything below:

1. **Individual facts are not copyrightable.** An address, an IK number, or a contribution rate is a fact. Anyone may state it.
2. **A structured collection can be protected.** German law grants a *sui generis* database right (§§ 87a–87e UrhG) to whoever made a substantial investment in compiling a database. Copying a *substantial part* of such a database can infringe that right — even though the individual facts are free.

> **Practical consequence:** CareGraph must **re-collect and re-verify facts from primary sources**, not bulk-copy another party's finished database. Provenance tracking (the `quelle` field, see [Data Schema §4](../architecture/data-schema.md#4-contribution-rate-historization-time-series)) is what makes this defensible and auditable.

---

## 2. Source-by-Source Assessment

Reviewed against the ingestion code on **2026-08-21**. Everything below is a
source the pipelines actually read; §2.1 lists what was considered and is not
used, which is a different and equally load-bearing statement.

| Source | Content | Nature | Notes / Action |
| :--- | :--- | :--- | :--- |
| **OpenStreetMap**, via the Overpass API | ~7,500 care providers — outpatient services, nursing homes, Pflegestützpunkte, with coordinates | ODbL-licensed database | The provider rows are **not merely geocoded with** OSM data, they **are** an OSM extract. That makes the table a Derivative Database: share-alike and attribution apply to the whole of it, not to a coordinate column. Settled in §5. |
| **GKV-Spitzenverband** — insurer list | 93 statutory insurers, contribution rate, region | Officially published list | Facts are public; re-derived from the official publication, `quelle` + `Stand` recorded. Redistribution terms of the publication itself are unresolved, so insurers are **excluded from the distributed archive**. |
| **ARGE·IK Schlüsselverzeichnis** (`institut-ba.de`) | Institutionskennzeichen, for enriching insurer records | Official key directory | Used to attach IKs to insurers already collected. Not bulk-copied — lookups against records the project holds. |
| **Bundes-Klinik-Atlas** open data | 1,577 hospital sites | Federal open-data publication | Ingested into the database, **withheld from every published archive** pending an answer from the Standortverzeichnis (asked 2026-08-10, § 2 Abs. 3). See the caveat in §5. |

### 2.1 Considered and not used

Naming these matters as much as naming the sources: the absence is a decision,
not an oversight.

| Not used | Why |
| :--- | :--- |
| **Pflege-Transparenz / care directories (§ 7, § 115 SGB XI)** | Legally mandated transparency would be the strongest possible footing, and remains the preferred future source for provider data. Not ingested today — the provider set comes from OpenStreetMap. |
| **vdek / AOK / ZQP directories** | Provider directories on private sites, protected as compiled databases under §§ 87a–87e UrhG. Not scraped, even where a narrow reading of `robots.txt` might allow it. The question is whom to ask, not how much may be taken — see §6. |
| **Nominatim** geocoding | Not used. Coordinates come with the OSM objects themselves, so no separate geocoding step exists and no geocoding cache is needed. |

---

## 3. Operating Principles

To stay on the safe side of the *sui generis* right and source terms, the ingestion pipeline follows these rules:

* **Primary sources first.** Prefer official, legally-mandated publications over third-party aggregators.
* **Re-collect, don't mirror.** Extract and re-verify individual facts; never copy a substantial portion of a third party's database wholesale.
* **Respect `robots.txt` and ToS.** Honor crawl directives and rate limits; identify the crawler honestly via User-Agent.
* **Attribution & provenance.** Every record stores its source and date (`quelle`, `gueltig_ab`), and OSM-derived records carry the required ODbL attribution.
* **Politeness.** Conservative request rates minimize load on sources — one Overpass query per ingestion run rather than per record.
* **Takedown path.** A documented process to correct or remove any record on justified request — the **Data correction** issue template, which handles a removal request on its own terms and without demanding a source.

---

## 4. What the Commercial Service Actually Sells

The Open-Core / DaaS model (see [Open Source Strategy](../pm/open-source-strategy.md)) does **not** sell exclusive rights to public data — nobody can. The paid offering sells **operational value on top of free facts**:

- continuous re-collection, validation, and deduplication,
- geocoding and normalization,
- guaranteed availability, SLAs, and a stable API,
- support and custom integrations.

This is the same model as OpenStreetMap-based commercial services: the data is open, the *maintained, hosted, reliable* service is the product.

---

## 5. Output Licensing

- **Software:** AGPLv3.
- **Derived data (CareGraph dataset): ODbL v1.0** — decided 2026-08-15 with
  [E4-S5](../pm/stories/epic-4-operations/e4-s5-distributable-dataset.md). The
  provider rows are not merely *geocoded* with OpenStreetMap data, they **are** an
  OpenStreetMap extract, which makes the table a Derivative Database and settles
  share-alike rather than leaving it open. The distributed archive therefore
  carries ODbL and the required attribution. Insurers are excluded from the
  archive: they are re-derived from a GKV publication whose redistribution terms
  are unresolved, and mixing sources would make the file inherit the strictest of
  them.
- **Attribution string**, as shipped in every archive's `LICENSE.txt` and
  `MANIFEST.json`:

  > © OpenStreetMap contributors (ODbL)

  An earlier draft here read *"Contains data from GKV-Spitzenverband and official
  § 7 SGB XI directories; geocoding © OpenStreetMap contributors"*. It was wrong
  in three ways at once — it credited sources that are not in the archive,
  described OSM as a geocoding step rather than the origin of the records, and
  contradicted the decision three lines above it. The string above is what
  `pipelines/dataset/export.py` actually writes; if the two ever disagree, the
  code is right and this page is stale.

- **What enforces this.** The exporter carries an **allowlist** of provider types
  rather than an exclusion list, because a licence is a property of the source,
  not of the table. Adding a type to it is a licensing decision. The first
  version excluded `krankenkasse` instead, which meant every type added later
  joined the archive silently — and one did: hospitals would have put 1,577
  Bundes-Klinik-Atlas rows into a file labelled ODbL.

---

## 6. Open Questions (for counsel)

1. ~~Does storing OSM geocodes at scale trigger ODbL share-alike on the *entire* dataset, or can geocodes be isolated?~~ **Closed 2026-08-15.** The question dissolved rather than being answered: the provider records *are* an OSM extract, not records geocoded with OSM, so there is no geocode to isolate. The archive ships ODbL — see §5.
2. Is a `CC BY` vs `ODbL` output licence compatible with all upstream obligations? *(Live for any future non-OSM source; settled for what ships today.)*
3. GDPR: sole traders (*Einzelunternehmen*) as care providers may be natural persons — is any of the published contact data personal data under Art. 4 GDPR, and what is the lawful basis (Art. 6(1)(f))?
4. For each third-party directory we might use: **who holds the rights, and what terms would they attach to a licensed export?**

> Note the framing of the last point. Where a directory is protected under the
> *sui generis* right, the question is not how much of it may be taken without
> asking — it is whom to ask. Our practice is to obtain permission and honour
> the terms that come with it, which is why the insurer portals are not scraped
> even where a narrow reading of their `robots.txt` might allow it.

> These are tracked deliberately as open items. Resolving them **before** the commercial launch (not after) is part of the Phase 4 funding/legal milestone.
