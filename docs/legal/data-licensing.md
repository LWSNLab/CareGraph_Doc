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

| Source | Content | Nature | Notes / Action |
| :--- | :--- | :--- | :--- |
| **GKV-Spitzenverband** – insurer list | Statutory insurers, contribution rate, region | Officially published list | Facts are public; re-derive from the official publication, cite `quelle` + `Stand`. |
| **Pflege-Transparenz / care directories (§ 7, § 115 SGB XI)** | Care providers, quality data | Legally mandated public transparency | Strongest legal footing — publication is required by law. |
| **vdek / AOK / ZQP directories** | Provider contact data | Provider directories on private sites | Check each site's ToS & `robots.txt`; treat their directory as a *protected DB* → re-collect facts, don't mirror. |
| **OpenStreetMap / Nominatim** (geocoding) | Coordinates | ODbL-licensed | ODbL is **share-alike for derived databases** — attribution required; understand ODbL obligations before storing geocodes at scale (self-host Nominatim to control usage). |

---

## 3. Operating Principles

To stay on the safe side of the *sui generis* right and source terms, the ingestion pipeline follows these rules:

* **Primary sources first.** Prefer official, legally-mandated publications over third-party aggregators.
* **Re-collect, don't mirror.** Extract and re-verify individual facts; never copy a substantial portion of a third party's database wholesale.
* **Respect `robots.txt` and ToS.** Honor crawl directives and rate limits; identify the crawler honestly via User-Agent.
* **Attribution & provenance.** Every record stores its source and date (`quelle`, `gueltig_ab`). OSM-derived geocodes carry the required ODbL attribution.
* **Politeness.** Conservative request rates and caching (the geocoding cache in the roadmap) minimize load on sources.
* **Takedown path.** A documented process to correct or remove any record on justified request.

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
- **Derived data (CareGraph dataset):** to be decided — a candidate is a permissive open-data license such as **CC BY 4.0** or **ODbL** for the aggregated dataset, with mandatory attribution. Note that OSM-derived geocodes may impose **ODbL share-alike** on the combined dataset; this must be resolved before choosing the dataset license.
- **Attribution string** (draft): *"Contains data from GKV-Spitzenverband and official § 7 SGB XI directories; geocoding © OpenStreetMap contributors (ODbL)."*

---

## 6. Open Questions (for counsel)

1. Does storing OSM/Nominatim geocodes at scale trigger ODbL share-alike on the *entire* CareGraph dataset, or can geocodes be isolated?
2. Which third-party provider directories qualify as protected databases, and where is the "substantial part" threshold?
3. Is a `CC BY` vs `ODbL` output license compatible with all upstream obligations?
4. GDPR: sole traders (*Einzelunternehmen*) as care providers may be natural persons — is any of the published contact data personal data under Art. 4 GDPR, and what is the lawful basis (Art. 6(1)(f))?

> These are tracked deliberately as open items. Resolving them **before** the commercial launch (not after) is part of the Phase 4 funding/legal milestone.
