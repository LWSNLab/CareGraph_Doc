# E1-S6 — IK-Nummer enrichment (insurers)

|                  |                          |
| :--------------- | :----------------------- |
| **Epic**         | E1 — Ingestion & ETL     |
| **Story Points** | 3                        |
| **Priority**     | Medium                   |
| **Status**       | ⏳ Planned               |

> ← [Epic 1](index.md) · [Backlog](../index.md)

## User Story

As a **data engineer**, I want the statutory health insurers enriched with their official Institutionskennzeichen, so that records carry a stable external identifier instead of being keyed on their name.

## Description

The GKV insurer list (E1-S1) has no IK-Nummer, so insurers are currently identified by name — which is fragile across yearly publications and useless for cross-source matching. This story resolves the IK for each insurer from the official *Kostenträgerdateien* and writes it to `care_infrastructure.ik_nummer`.

## Acceptance Criteria

- [ ] Current Kostenträgerdateien are discovered and downloaded from gkv-datenaustausch.de.
- [ ] `IDK` segments are parsed into an IK ↔ name directory.
- [ ] At least 95% of the insurers are matched to an IK.
- [ ] Unmatched insurers are reported explicitly, never silently dropped.
- [ ] `ik_nummer` is populated in `care_infrastructure` and stays stable across runs.

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

## Dependencies

- **Depends on:** E1-S1 (the insurer list to enrich)
- **Blocks:** nothing hard; materially improves E1-S5 (IK is the strongest dedup key)

## Risks

- **Name matching is ambiguous** for a handful of insurers — mitigate with an explicit alias table plus a report of unmatched entries, rather than fuzzy-matching aggressively and mis-assigning an IK.
- **Quarterly file rotation** breaks hardcoded URLs — discover filenames instead.
- **This does not solve provider IKs.** The Kostenträgerdateien list the *payers* (insurers), not the *Leistungserbringer*. Provider IKs live in the DCS data behind the insurer portals, which are not scrapeable (see [E1-S2](e1-s2-provider-scrapers.md)); obtaining them needs a data-sharing agreement or municipal open data.

## Definition of Done

- [ ] Acceptance criteria fulfilled
- [ ] Tests passing (unit + integration where relevant)
- [ ] CI covers the new code (pipeline extended if needed)
- [ ] Documentation updated
- [ ] Code reviewed

## References

- [Data Schema](../../../architecture/data-schema.md) · [Data Sources & Licensing](../../../legal/data-licensing.md)
