# E1-S5 — Deduplication

|                  |                          |
| :--------------- | :----------------------- |
| **Epic**         | E1 — Ingestion & ETL     |
| **Story Points** | 5                        |
| **Priority**     | Medium                   |
| **Status**       | ⏳ Planned               |

> ← [Epic 1](index.md) · [Backlog](../index.md)

## User Story

As a **data engineer**, I want duplicate providers merged across sources, so that the dataset is clean and each institution appears once.

## Description

Detect and merge records that refer to the same institution across multiple source datasets, keeping the provenance of each merged field.

## Acceptance Criteria

- [ ] Match on address + name similarity. (IK where present — insurers only.)
- [ ] Merge strategy keeps provenance of each field.
- [ ] Validation report produced per run.

## Technical Notes

Blocking on PLZ/city to keep pairwise comparisons cheap; fuzzy name/address matching for the residual.

**There is no strong key for providers, and there will not be one.** IK-Nummer is the strongest key when present, but it is present only for statutory insurers: the bodies holding the provider pairing declined to share it in writing, and [E1-S8](e1-s8-provider-ik.md) is closed as a result. Deduplication therefore rests on name and address similarity alone, permanently rather than until the key arrives.

That raises the cost of a wrong merge and lowers the acceptable threshold. Two providers at one address with similar names are commonplace in this data — a nursing home and the outpatient service run from the same building are distinct entities, not a duplicate. **Refuse rather than guess:** an unmerged pair is visible in the record count, a wrongly merged one is silent.

## Dependencies

- **Depends on:** E1-S2 (provider records from multiple sources)
- **Blocks:** —

## Risks

- Over-merging distinct nearby providers (false positives) — tune thresholds, keep a review report.

## Definition of Done

- [ ] Acceptance criteria fulfilled
- [ ] Tests passing (unit + integration where relevant)
- [ ] CI covers the new code (pipeline extended if needed)
- [ ] Documentation updated
- [ ] Code reviewed

## References

- [Data Schema](../../../architecture/data-schema.md)
