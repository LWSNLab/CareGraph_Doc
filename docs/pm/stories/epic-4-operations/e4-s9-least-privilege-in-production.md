# E4-S9 — The API connects as the database owner

|                  |                              |
| :--------------- | :--------------------------- |
| **Epic**         | E4 — Operations & CI/CD      |
| **Type**         | Bug                          |
| **Story Points** | 2                            |
| **Priority**     | High                         |
| **Status**       | ⏳ Planned                   |

> ← [Epic 4](index.md) · [Backlog](../index.md)

## The defect

Migration `0003` creates two least-privilege roles: `caregraph_api` reads,
`caregraph_ingest` writes. `make env-prod` generates a password for each,
`make db-roles` applies them, and `.env` says in a comment:

> The API connects read-only, the pipelines write-scoped.

The containers use neither. `docker-compose.yml` gives both services a DSN built
from `POSTGRES_USER` and `POSTGRES_PASSWORD` — the **database owner**, which
holds `DROP TABLE` on everything.

So the least-privilege design exists in the schema, in the generated passwords
and in a comment, and nowhere in the running system.

## Why it is a missing override rather than an oversight

The dev default is deliberate and documented:

> Owner rather than the write-scoped role: `caregraph_ingest` has no password
> until `make db-roles-dev` runs, which compose cannot depend on.

That is sound for a laptop, where `docker compose up` has to work before anyone
has run a second command. The bug is that **production inherits it**:
`docker-compose.prod.yml` overrides ports, restart policy and trusted proxies —
and not the one setting whose dev-time justification does not apply, because the
runbook already runs `make db-roles` before the first deployment.

## What it costs

The API is the only component reachable from the internet. Any path from a
request to the database — a future dynamic query, a dependency with a flaw —
executes with rights to drop the schema. The roles that would have contained
that are sitting in the database, unused, with their passwords in `.env`.

Not theoretical in one specific way: `/v1/infrastructure/search` passes caller
text to Typesense and then queries Postgres by the ids it returns. The query is
parameterised today, which is why this is a bug about blast radius rather than
an open hole.

## Acceptance Criteria

- [ ] The production overlay sets the API's `DATABASE_URL` to `caregraph_api`
      with `CAREGRAPH_ROLE_PW_API`, and the ingest service's to `caregraph_ingest`
      with `CAREGRAPH_ROLE_PW_INGEST`.
- [ ] A check proves it rather than asserting it: with the production overlay,
      the API's connection must be refused when it attempts a write the role does
      not hold.
- [ ] `deploy/verify.sh` covers it, so the guarantee is re-checked on every
      deployment instead of once.
- [ ] The runbook states the ordering, because it stops being optional:
      `make db-roles` must run **before** the first deployment, or the container
      cannot log in at all.
- [ ] The `.env` comment becomes true.

## Technical Notes

**Ordering is the whole risk of the fix.** Today a wrong password means the API
runs with too many rights; afterwards it means the API does not start. That is
the better failure — loud instead of silent — but it turns `db-roles` from a
nicety into a step, and the first deployment is exactly when someone skips it.
The runbook already has `make up && make db-roles` before `deploy.sh`; this makes
that line load-bearing.

**Not the dev compose file.** Changing the base would break `docker compose up`
on a fresh checkout, which is the one thing the current default protects.

## Dependencies

- **Depends on:** —
- **Related:** [E4-S6](e4-s6-deployment.md) created the overlay this is missing
  from; [E4-S8](e4-s8-versioned-rollout.md) is where `verify.sh` gained the
  habit of asserting things that must *not* be possible

## Risks

- **It looks done once the DSN is changed.** The connection succeeding proves the
  password is right, not that the rights are narrower. Only an attempted write
  that gets refused proves that, which is why it is an acceptance criterion.

## References

- [Security & Privacy](../../../architecture/security.md) · [Data Schema](../../../architecture/data-schema.md)
