# E4-S4 — Security scanning & supply-chain hardening

|                  |                       |
| :--------------- | :-------------------- |
| **Epic**         | E4 — Operations & CI/CD |
| **Story Points** | 3                     |
| **Priority**     | High                  |
| **Status**       | ✅ Done |

> ← [Epic 4](index.md) · [Backlog](../index.md) · [Security & Privacy](../../../architecture/security.md)

## User Story

As a **maintainer**, I want automated security and supply-chain scanning, so that vulnerabilities are found by the pipeline rather than by users — and so the project can credibly claim a security posture to funders and integrators.

## Description

Establish continuous scanning across code, dependencies and secrets, plus a documented vulnerability-disclosure process. Pulled forward from Phase 4 alongside [E4-S2](e4-s2-ci-cd.md): a public-interest health-data project has to be able to answer "how do you handle security?" before it goes public, not after.

## Acceptance Criteria

- [x] Static analysis (CodeQL) configured for Go and Python.
- [x] Dependency updates automated (Dependabot) across all ecosystems in use.
- [x] Dependency vulnerability scanning in CI (`govulncheck`, `pip-audit`).
- [x] Secret scanning over the full git history.
- [x] A published `SECURITY.md` with a private reporting channel and response targets.
- [x] All workflows run with least-privilege permissions.

## Technical Notes

**Billing shaped the design, and then the design outlived the billing.** Both repos were private when this was written, and there CodeQL and Secret Protection require GitHub Advanced Security, billed per active committer, while Dependabot is free everywhere. So:

| Check | Tool | While private | Since [E5-S1](../epic-5-open-source/e5-s1-repo-licensing.md) |
| :-- | :-- | :-- | :-- |
| Static analysis | CodeQL (`security-extended`) | guarded — skipped | ✅ running |
| Dependency updates | Dependabot | ✅ active | ✅ |
| Go vulnerabilities | `govulncheck` | ✅ active | ✅ |
| Python vulnerabilities | `pip-audit` | ✅ active | ✅ |
| Secrets | `gitleaks` (full history) | ✅ active | ✅ |
| PR dependency review | `dependency-review-action` | guarded — skipped | ✅ running |

The CodeQL job carries `if: github.event.repository.visibility == 'public' || vars.ENABLE_CODEQL == 'true'`. Without that guard the workflow would have failed on every push while the repo was private, and a permanently red pipeline is worse than no pipeline. Both repositories went public on **2026-08-25**, so the condition is now satisfied by the first branch and the guard costs nothing — it stays because it is what makes a fork of this repository work either way.

**What CodeQL found once it ran.** Thirteen alerts, all `go/log-injection`, all false positives: the service logs through a JSON handler, which escapes every attribute value, so a newline cannot close a record and forge a second one. Dismissing them is only defensible while that holds, so `TestLogValuesCannotForgeARecord` asserts it — switch the handler to text and the build fails. The alerts did point at something real, though not what they claimed: the access log recorded the query string verbatim beside `client_ip`, filing an address together with a location. That is fixed separately, in [E4-S6](e4-s6-deployment.md).

**`govulncheck` over a generic scanner:** it reports only vulnerabilities *reachable from our code*, which keeps the noise down — it distinguished 1 reachable issue from 36 unreachable ones on the first run.

**`gitleaks` is not redundant** once Secret Protection is available: it also covers pull requests from forks and scans the complete history.

### Found on the very first run

`govulncheck` flagged **GO-2026-5970** — an infinite loop in `golang.org/x/text@v0.18.0`, reachable from `infrastructure.NewPostgresPool` via `pgxpool.New`. Fixed by upgrading to `v0.39.0`. A real, reachable vulnerability that existed in the repo before any of this tooling was in place.

## Dependencies

- **Depends on:** E4-S2 (the CI workflow this extends)
- **Blocks:** E5-S1 — a public launch should not happen without a disclosure policy

## Risks

- **Alert fatigue**: grouped Dependabot PRs and reachability-based scanning keep the volume manageable; revisit if it still becomes noisy.
- ~~**Guarded checks give a false sense of coverage** while the repo is private — CodeQL is configured but *not running*.~~ **Closed 2026-08-25**: both repositories are public and CodeQL runs on every push. The risk was real while it lasted — the first run produced thirteen alerts on code that had been in the repository for weeks.
- **Actions are pinned to tags, not commit SHAs.** SHA pinning is the stricter supply-chain practice; Dependabot can maintain it. Deliberately deferred for readability — revisit before the public launch.

## Definition of Done

- [x] Acceptance criteria fulfilled
- [x] Tests passing (all scanners run clean locally after the `x/text` fix)
- [x] CI covers the new code (pipeline extended if needed)
- [x] Documentation updated
- [x] Code reviewed

## References

- [Security & Privacy](../../../architecture/security.md) · [Open Source Strategy](../../open-source-strategy.md)
