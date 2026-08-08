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

- [ ] Match on IK-Nummer, then address + name similarity.
- [ ] Merge strategy keeps provenance of each field.
- [ ] Validation report produced per run.

## Technical Notes

Blocking on PLZ/city to keep pairwise comparisons cheap; fuzzy name/address matching for the residual. IK-Nummer is the strongest key when present.

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
