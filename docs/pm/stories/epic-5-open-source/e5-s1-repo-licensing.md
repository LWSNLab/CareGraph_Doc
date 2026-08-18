# E5-S1 — Public repository & licensing

|                  |                              |
| :--------------- | :--------------------------- |
| **Epic**         | E5 — Open Source & Funding   |
| **Story Points** | 2                            |
| **Priority**     | Medium                       |
| **Status**       | ⏳ Planned                   |

> ← [Epic 5](index.md) · [Backlog](../index.md)

## User Story

As a **contributor**, I want a clearly licensed public repo, so that I can contribute confidently.

## Description

Make the project safe and welcoming to contribute to: clear licenses, contribution
guidelines, security policy, templates — and then actually make it public.

The earlier version of this story listed only the files. That left the step it is
named for outside its own acceptance criteria, and with it the question of what
has to be true first. Publishing is not formally irreversible — the switch flips
both ways — but in practice it is: a public repository gets forked, mirrored and
indexed within hours, and none of that comes back.

## Acceptance Criteria

- [x] Core licensed AGPLv3, docs CC BY-SA 4.0. *(Both `LICENSE` files are in
      place; nothing to do.)*
- [ ] `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, issue and PR templates.
      `SECURITY.md` already exists.
- [ ] A documented way to request an API key — see below.
- [ ] **The pre-publication checklist below is complete.**
- [ ] **Both repositories switched to public.**
- [ ] The steps that publication makes free are taken: GHCR image push, and
      GitHub Code Quality and Secret Protection switched back on.

## Before flipping the switch

Each of these is cheap to check and expensive to miss.

| Check | State as of 2026-08-18 |
| :-- | :-- |
| No secrets anywhere in history | ✅ `gitleaks git .` clean over the full history, and CI enforces it |
| The flagged commit `9695e7df` is gone | ⚠️ Not an ancestor of `develop` and deleted on origin, so it would not be published — but a **local** branch still holds it. Delete `feature/e3-s5-openapi-docs` locally, then `.gitleaksignore` can go with it |
| Negotiating drafts stay out | ✅ `CareGraph_Doc/internal/` is gitignored and nothing under it is tracked |
| No credentials in tracked files | ✅ Verified; the only DSNs are in `.env.example`, visibly examples, and in `make db-roles-dev`, whose purpose is throwaway dev passwords |
| Raw source data stays out | ✅ Only `ik_overrides.json`, `manual_overrides.json` and a `.gitkeep` are tracked under `pipelines/data/` |
| [Data Sources & Licensing](../../../legal/data-licensing.md) reviewed | ⏳ Named in this story's own risks; read it once against what is actually ingested |
| The quickstart works for a stranger | ✅ Walked verbatim against an empty database during the [E4-S1](../epic-4-operations/e4-s1-containerization.md) release acceptance test |

**The hospital caveat.** The Bundes-Klinik-Atlas records are ingested and the
redistribution question sent to the Standortverzeichnis on 2026-08-10 is still
unanswered. This does not block publishing the *code*: the release archive
already excludes hospitals by an allowlist rather than an exclusion. It does mean
nobody should add them to a published dataset before there is an answer.

## What publishing the repository is not

Publishing the code is not the same as running a public service, and only the
second carries the obligations:

- An **Impressum** with a summonable address, which for a project label rather
  than a legal entity means a private one.
- A **privacy notice**, because the API logs client IP addresses — they key the
  rate limiter and the failed-authentication budget.

Neither applies to a repository. Both apply the moment a hosted endpoint is
announced. Keeping the two apart lets the repository go public now while the
hosted instance stays a private test.

## Requesting an API key

Keys are issued by hand (`cmd/apikey issue`), and that stays true for now: ten
people you can talk to are worth more than a thousand anonymous keys, and
self-service means storing email addresses — so a privacy notice and abuse
handling before there is any demand.

What this story adds is only the *documented path*: an issue template or an
address, so a stranger knows how to ask. Fulfilment stays manual until it becomes
a chore, say more than one or two requests a week.

## After publication

| | |
| :-- | :-- |
| **GHCR image push** | Free for public repositories. Worth doing then, because the image CI tested becomes the image that runs — today the server builds its own copy that is only assumed to be identical |
| **Code Quality, Secret Protection** | Also free for public repositories; both were switched off for cost |

## Dependencies

- **Depends on:** —
- **Blocks:** E5-S2 (governance builds on templates), and the GHCR push that would
  otherwise cost money on a private repository

## Risks

- Data-licensing clarity is a prerequisite for a clean public launch — see
  [Data Sources & Licensing](../../../legal/data-licensing.md).
- Publication is practically one-way. The checklist above exists because a
  mistake in it cannot be withdrawn, only apologised for.

## Definition of Done

- [ ] Acceptance criteria fulfilled
- [ ] Tests passing (unit + integration where relevant)
- [ ] CI covers the new code (pipeline extended if needed)
- [ ] Documentation updated
- [ ] Code reviewed

## References

- [Open Source Strategy](../../open-source-strategy.md) · [Data Sources & Licensing](../../../legal/data-licensing.md)
