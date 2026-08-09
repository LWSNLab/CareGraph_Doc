# E1-S6 — IK-Nummer enrichment (insurers)

|                  |                          |
| :--------------- | :----------------------- |
| **Epic**         | E1 — Ingestion & ETL     |
| **Story Points** | 3                        |
| **Priority**     | Medium                   |
| **Status**       | ✅ Done (pending review) |

> ← [Epic 1](index.md) · [Backlog](../index.md)

## User Story

As a **data engineer**, I want the statutory health insurers enriched with their official Institutionskennzeichen, so that records carry a stable external identifier instead of being keyed on their name.

## Description

The GKV insurer list (E1-S1) has no IK-Nummer, so insurers are currently identified by name — which is fragile across yearly publications and useless for cross-source matching. This story resolves the IK for each insurer from the official *Kostenträgerdateien* and writes it to `care_infrastructure.ik_nummer`.

## Acceptance Criteria

- [x] Current Kostenträgerdateien are discovered and downloaded from gkv-datenaustausch.de.
- [x] `IDK` segments are parsed into an IK ↔ name directory; the authoritative Kassensitz list is parsed on top of it.
- [x] At least 95% of the insurers are matched to an IK. *(**99% — 91/92.** Only EY Betriebskrankenkasse appears in no official source.)*
- [x] Unmatched insurers are reported explicitly, never silently dropped.
- [x] `ik_nummer` is populated in `care_infrastructure` and stays stable across runs.

## Technical Notes

**Source:** [Kostenträgerdateien Pflege](https://www.gkv-datenaustausch.de/leistungserbringer/pflege/kostentraegerdateien_pflege/kostentraegerdateien.jsp) (GKV-Spitzenverband). Official, machine-readable, updated on the 1st of each calendar quarter, and not disallowed by `robots.txt`.

Format is EDIFACT-like; the relevant segment carries IK and name directly:

```text
IDK+100820488+99+Brandenburgische BKK'
```

Findings from the exploratory pass:

- One file per association: `AO*` (AOK), `BK*` (BKK), `IK*` (IKK), `BN*` (Knappschaft), `LK*` (landwirtschaftlich), `EK*` (Ersatzkassen); extensions `.ke0`/`.ke1`/`.ke4`.
- Encoding is **ISO-8859-1**, not UTF-8.
- 787 distinct IK numbers across the files.
- Naive normalised matching already resolves **81 of 92** insurers (88%). The misses are abbreviation cases — *Techniker Krankenkasse* → `TK`, *Siemens-Betriebskrankenkasse (SBK)* → `SBK`, *Kaufmännische Krankenkasse* → `KKH` — so a small alias table should clear the 95% bar.
- **Filenames embed the quarter** (`BK06Q326.ke0`), so the current files must be discovered from the page; hardcoding a URL would silently go stale.

### What was actually built

`pipelines/parsers/ik_verzeichnis.py`, wired into `pipelines/run_load.py`.

**Two sectors are required, and neither suffices alone.** The first attempt used only the SGB XI (Pflege) files and reached 83%. Those list an insurer's *Pflegekasse* — a different institution with a different IK. The SGB V files carry the *Krankenkasse*. Measured: Pflege alone misses VIACTIV, SECURVITA, SBK and AOK Schwarzwald-Baar-Heuberg; SGB V alone misses TK and hkk. Loading both, SGB V first, yields 93%.

**Matching is on token sets, not strings.** The directory routinely reverses word order (`Merck BKK` ↔ `BKK Merck`), abbreviates (`Seidensticker` → `Seidenst.`, `Saarland` → `SL`) and appends annotations (`BKK mkk (ehem. BKK VBU)`). A concatenated key survives none of that; comparing sets of identifying tokens survives all of it.

**Three precision guards**, each added after a wrong match was observed in the real data:

| Guard | The wrong match it prevents |
| :-- | :-- |
| Care-fund and `/Ost` entries are never indexed | attaching a *Pflegekasse* IK to a Krankenkasse |
| Entries reducing to a category token only | `BKK S-H` → `{bkk}` matched every other BKK (hit `EY BKK`) |
| The same guard on the query side | `R+V BKK` → `{bkk}` matched `BKK DEMAG KRAUSS-MAFFEI` |

No edit-distance fuzziness anywhere: a wrong IK looks entirely plausible in the data and nothing downstream would flag it, whereas a missing one is in the run report.

**Existing rows are rekeyed, not duplicated.** The 92 insurers were already stored under `gkv:<name>`. Switching the key to `ik:<number>` would have inserted 92 second rows, so the loader rewrites the old key in place first. Verified: 86 rekeyed, total unchanged at 92, and a second run reports `rekeyed=0`.

### Which IK? — the decision that mattered most

An insurer holds **several** IKs: one *Kassensitz-IK* identifying the institution, and several *Abrechnungs-IKs* for billing. The Kostenträgerdateien list billing IKs, so a first version of this story stored whichever one happened to be read first — 26 of 86 values were an arbitrary pick. For a field meant to be *the* stable external identifier that is not good enough: two consumers matching on `ik_nummer` could disagree.

The primary source is therefore **Schlüsselverzeichnis 8a of the Bewertungsausschuss** (§ 87 SGB V), which lists exactly one Kassensitz-IK per insurer (93 rows). The Kostenträgerdateien remain as a fallback for insurers it does not cover.

Two independent confirmations that the source is right: R+V's own Impressum states `105823040`, matching the list exactly; and BKK24's value agreed with an unrelated third-party directory.

**Discovery, again.** The document is versioned in its filename (`S_8a_ABRIK_035.PDF`) and the server answers unknown versions with an **HTML page under HTTP 200** — so versions are probed upward and validated by PDF magic bytes, never by status code.

**PDF extraction glues words** (`AOKNordost`, `BKKSchwarzwald-Baar-Heuberg`), which no token set can match. A second, order-preserving concatenated key handles it; the token index still handles the opposite problem of reversed word order. Both are needed.

### The one without an IK

`EY Betriebskrankenkasse` — checked against the Kassensitz list and all four Kostenträgerdatei sectors (SGB V, Pflege, Krankenhäuser, Apotheken), plus its own Impressum. It keeps its `gkv:<name>` key and is listed on every run. `pipelines/data/ik_overrides.json` is ready for a curated value and intentionally empty: an invented IK would be worse than none.

### Rekeying without duplicates

Rows may carry an older key — the name key from before IKs existed, or a superseded IK (the official list corrects these between versions; AOK Nordost changed between v011 and v035). The loader rewrites the key in place before upserting, matched on name. Verified: 13 rows rekeyed on the switch to Kassensitz-IKs, 92 insurers before and after, `rekeyed=0` on the next run.

## Dependencies

- **Depends on:** E1-S1 (the insurer list to enrich)
- **Blocks:** nothing hard; materially improves E1-S5 (IK is the strongest dedup key)

## Risks

- **Name matching is ambiguous** for a handful of insurers — mitigate with an explicit alias table plus a report of unmatched entries, rather than fuzzy-matching aggressively and mis-assigning an IK.
- **Quarterly file rotation** breaks hardcoded URLs — discover filenames instead.
- **This does not solve provider IKs.** The Kostenträgerdateien list the *payers* (insurers), not the *Leistungserbringer*. Provider IKs live in the DCS data behind the insurer portals, which are not scrapeable (see [E1-S2](e1-s2-provider-scrapers.md)); obtaining them needs a data-sharing agreement or municipal open data.

## Definition of Done

- [x] Acceptance criteria fulfilled
- [x] Tests passing (38 for this module, 205 total; all matcher tests run offline)
- [x] CI covers the new code
- [x] Documentation updated
- [ ] Code reviewed

## References

- [Data Schema](../../../architecture/data-schema.md) · [Data Sources & Licensing](../../../legal/data-licensing.md)
