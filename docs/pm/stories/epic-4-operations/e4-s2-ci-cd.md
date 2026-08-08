# E4-S2 — CI/CD

|                  |                       |
| :--------------- | :-------------------- |
| **Epic**         | E4 — Operations & CI/CD |
| **Story Points** | 3                     |
| **Priority**     | Medium                |
| **Status**       | ✅ Done (pending review) |

> ← [Epic 4](index.md) · [Backlog](../index.md)

## User Story

As a **maintainer**, I want automated CI, so that quality is enforced on every change.

## Description

Run build, lint, and tests for both the Go and Python codebases on every push/PR, and deploy the documentation automatically.

## Acceptance Criteria

- [x] Build, lint, and test for Go and Python.
- [x] Docs deploy (MkDocs → GitHub Pages) on change.

## Technical Notes

**Pulled forward out of Phase 4.** With 147 tests in the repo and the loader (E1-S4) about to touch schema and data, running the suite only by hand was the bigger risk. Deliberately scoped to CI only.

Two workflows now exist:

| Workflow | Repo | Does |
| :-- | :-- | :-- |
| `ci.yml` | CareGraph | Go: `gofmt` check, build, vet, test · Python: `ruff`, `pytest` |
| `deploy-docs.yml` | CareGraph_Doc | MkDocs `--strict` build → GitHub Pages |

Details worth knowing:

- **Ruff is configured explicitly** in `pipelines/pyproject.toml` (`select = E,F,I,UP,B`, line length 110). Without a committed config the ruleset depends on the local environment and CI results are not reproducible.
- **Tests requiring the official GKV PDF skip themselves** — the file is gitignored, so CI reports 146 passed / 1 skipped. That is expected, not a silent hole.
- `concurrency` cancels superseded runs on the same ref; permissions are read-only.
- All steps were run locally before committing the workflow.

> ⚠️ **Scope gap in this story, worth naming:** the title says CI/**CD**, but neither acceptance criterion covers *application* delivery — building and pushing container images or deploying the API. Only the docs are deployed. If application CD is wanted, it needs its own acceptance criteria (or a separate story) on top of E4-S1.

## Dependencies

- **Depends on:** — (CI needs no images; E4-S1 becomes a dependency only for image publishing)
- **Blocks:** —

## Risks

- Flaky integration tests (needing Postgres/Typesense) — use service containers when E1-S4 adds database tests.
- `uv sync --all-groups` installs the full dependency set including Playwright and Polars, which the current tests do not need; if CI time becomes a problem, split into a lighter test group.

## Definition of Done

- [x] Acceptance criteria fulfilled
- [x] Tests passing (147 locally; 146 + 1 skipped in CI)
- [x] CI covers the new code (pipeline extended if needed)
- [x] Documentation updated
- [ ] Code reviewed

## References

- [Roadmap](../../roadmap.md)
