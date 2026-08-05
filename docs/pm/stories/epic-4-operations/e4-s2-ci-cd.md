# E4-S2 — CI/CD

|                  |                       |
| :--------------- | :-------------------- |
| **Epic**         | E4 — Operations & CI/CD |
| **Story Points** | 3                     |
| **Priority**     | Medium                |
| **Status**       | ⏳ Planned            |

> ← [Epic 4](index.md) · [Backlog](../index.md)

## User Story

As a **maintainer**, I want automated CI, so that quality is enforced on every change.

## Description

Run build, lint, and tests for both the Go and Python codebases on every push/PR, and deploy the documentation automatically.

## Acceptance Criteria

- [ ] Build, lint, and test for Go and Python.
- [ ] Docs deploy (MkDocs → GitHub Pages) on change.

## Technical Notes

The docs-deploy workflow already exists in the documentation repo. Remaining: an implementation-repo pipeline (`go build/vet/test`, `ruff`/`pytest`, image build).

## Dependencies

- **Depends on:** E4-S1 (images to build)
- **Blocks:** —

## Risks

- Flaky integration tests (needing Postgres/Typesense) — use service containers.

## Definition of Done

- [ ] Acceptance criteria fulfilled
- [ ] Tests passing (unit + integration where relevant)
- [ ] Documentation updated
- [ ] Code reviewed

## References

- [Roadmap](../../roadmap.md)
