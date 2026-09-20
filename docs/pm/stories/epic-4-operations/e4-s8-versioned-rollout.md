# E4-S8 — One version per rollout

|                  |                              |
| :--------------- | :--------------------------- |
| **Epic**         | E4 — Operations & CI/CD      |
| **Type**         | Story                        |
| **Story Points** | 3                            |
| **Priority**     | Medium                       |
| **Status**       | ⏳ Planned                   |

> ← [Epic 4](index.md) · [Backlog](../index.md)

## User Story

As an **operator rolling back a bad release**, I want the schema to go back with
the binary, so that the recovery is not the outage.

## Description

[E4-S6](e4-s6-deployment.md) settled the right half of this: the server pulls
images built by CI and never builds its own. That part needs no change, and the
common advice to "only pull the image" is already the implemented design.

What it did not settle is what travels *beside* the image. Three things are
versioned independently today:

| | Source | Pinned by |
| :-- | :-- | :-- |
| Binary | GHCR | `CAREGRAPH_TAG` |
| Migrations, compose files, Caddyfile | git checkout | branch `main` |
| Configuration | `.env` | by hand |

While nothing is pinned, the first two move together and all is well. **They
diverge exactly when you pin one of them** — which is the rollback case:

> Set `CAREGRAPH_TAG=v0.1.1` to recover from a bad release, and `deploy/update.sh`
> still runs `git pull --ff-only` on `main` and then `make migrate`, applying the
> migrations of v0.2.0 against the binary of v0.1.1.

That is the hazard `update.sh` warns about in its own comment — an older image
against a newer schema — reachable through the documented recovery procedure.

## Acceptance Criteria

- [ ] A rollout names one version, and the checkout and image tag are derived
      from it rather than kept in step by discipline.
- [ ] Migrations are applied from the image that is being deployed, not from the
      checkout on the host.
- [ ] `deploy/update.sh` works on a tag. It currently does `git pull --ff-only`,
      which a detached checkout cannot do.
- [ ] The runbook drops `--build`. It is offered as the path for when nothing has
      been merged to `main` yet, a situation three releases old, and it invites
      someone to build an image CI never tested.
- [ ] **A rollback is performed and the schema checked afterwards** — deploy
      v0.2.0, roll back to v0.1.1, and show that the database is on v0.1.1's
      highest migration and not v0.2.0's. Every other criterion can be satisfied
      by a script that quietly does the wrong thing.

## Technical Notes

**Migrations from the image is not free.** `Dockerfile.ingest` already carries
`db/migrations/`, but there is no runner and the image has no `psql` — only
`psycopg`, through the pipelines. Two ways, and the choice belongs with whoever
writes it:

- Stream the files out of the image into the database container, the way
  `make migrate` already pipes into `docker compose exec -T db psql`. Smallest
  change, no new code.
- A `run_migrate` module in the pipelines using the connection it already has.
  More code, but it can report which migration it is on and refuse a database
  ahead of the image.

The second is the one that makes the rollback criterion cheap to verify, because
it can say what it found before it changes anything.

**Migrations are re-runnable** — CI applies them twice to keep that true — so
re-applying on every rollout stays safe. A rollback does not *undo* migrations;
it stops applying newer ones. Going back to an older schema is a restore from
backup ([E4-S7](e4-s7-secret-recovery.md)), not a deployment step, and the
runbook should say so rather than implying a rollback is symmetric.

## What this does not change

The server keeps its git checkout. The advice to leave only a `docker-compose.yml`
on the host trades a versioned carrier for a hand-maintained file that drifts from
the repository without anyone reviewing it. With one host and one operator, the
checkout *is* the configuration management — and since [E5-S1](../epic-5-open-source/e5-s1-repo-licensing.md)
made the repository public, it costs no deploy key and exposes no secret.

## Dependencies

- **Depends on:** [E4-S6](e4-s6-deployment.md)
- **Related:** [E4-S7](e4-s7-secret-recovery.md) — together they cover the two
  ways a recovery goes wrong: no secrets, or the wrong schema

## Risks

- **It looks finished before it is tested.** Deploying by tag is a few lines and
  feels complete; the rollback drill is what proves the schema followed.

## References

- [Deployment runbook](https://github.com/LWSNLab/CareGraph/blob/main/deploy/README.md) · [Versioning](../../../architecture/versioning.md)
