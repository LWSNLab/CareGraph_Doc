# E4-S7 — Secret recovery

|                  |                              |
| :--------------- | :--------------------------- |
| **Epic**         | E4 — Operations & CI/CD      |
| **Type**         | Story                        |
| **Story Points** | 2                            |
| **Priority**     | High                         |
| **Status**       | ⏳ Planned                   |

> ← [Epic 4](index.md) · [Backlog](../index.md)

## User Story

As an **operator whose server has just died**, I want the secrets back before the
data, so that the backup I restore is one I can still open.

## Description

[E4-S6](e4-s6-deployment.md) gave the database a backup and a restore, verified
against an empty database. `.env` got a sentence:

> Keep a copy somewhere safe. Losing `.env` means losing access to the database,
> and `make env-prod` cannot reconstruct it.

That is advice, not a mechanism, and it is the sentence the deployment currently
rests on. Five secrets live in that file — the Postgres password, the Typesense
key, and the two least-privilege role passwords, the last two repeated inside the
DSNs. All are generated; none is written down anywhere else.

**The failure is worse than losing a file.** The nightly dump is encrypted with
nothing and readable, but the roles it restores into are the ones whose passwords
were in `.env`. A restore onto a fresh host without them leaves a database nobody
can connect to — the data is there and unreachable. So the secrets are not a
second backup, they are a prerequisite for the first one being worth anything.

## Acceptance Criteria

- [ ] `.env` is backed up encrypted, to the same off-site destination as the
      database dumps, by the same schedule.
- [ ] Encrypted with a key that is not on the server. A copy encrypted with a key
      stored beside it protects against nothing this scenario contains.
- [ ] The runbook documents recovery in the order it actually happens: secrets
      first, then the dump, then the stack.
- [ ] **A restore is performed, not assumed** — onto a machine that never held the
      original, from the backup alone. A backup nobody has restored is a belief.
- [ ] The dump backup itself gets an off-site step. Today it writes to
      `backups/`, on the disk it protects against, and the runbook says to copy it
      off by hand.

## Technical Notes

`age` over `gpg`: one file, one recipient key, no keyring or trust model to
carry. The private key belongs somewhere the server cannot reach — a password
manager, or paper in a drawer. Which is a decision for whoever operates this, and
the runbook should say what the requirement is rather than pick for them.

The file is small enough that versioning it costs nothing. Worth keeping several:
a rotation that goes wrong is discovered later than it happens, and the useful
copy is the one from before.

## Why not a secret manager

Evaluated Infisical, self-hosted as a container, on 2026-09-05. Rejected for this
deployment — recorded here so the question is not re-opened without new facts.

**The bootstrap problem is unavoidable on a single host.** Infisical needs four
values to start, of which `ENCRYPTION_KEY` and `AUTH_SECRET` are themselves
secrets. On one machine those live in a `.env` file at mode 0600 — exactly where
the five secrets live now. The file does not disappear; it acquires a service in
front of it, and the outer secret is as exposed as the inner ones were.

**It couples availability without buying redundancy.** Today the file is present
and the API starts. With a secret manager the API starts only if that manager is
up — a new single point of failure on a host that has no second one to fail over
to.

**It changes the threat model less than it appears to.** An attacker with root
reads `.env`, or the manager's database, or `/proc/<pid>/environ` of the running
process, where the values sit either way.

**It does not solve this story.** A secret manager on the same disk is lost with
that disk, and takes its own database with it.

It becomes the right answer with a second host, a team rotating without
redeploying, or audit requirements from a hosted offering
([E6](../epic-6-commercial/index.md)) — none of which is true of one VPS with one
operator.

## Dependencies

- **Depends on:** [E4-S6](e4-s6-deployment.md) — the backup this extends
- **Blocks:** nothing, and that is the risk: it will feel unnecessary until the
  day it is the only thing that matters

## Risks

- **A restore drill is the whole story.** Every criterion above except the last is
  satisfiable by a script that produces an unopenable file. Only restoring proves
  otherwise.
- **The encryption key becomes the thing that is lost.** Moving the problem one
  level up is real, and the mitigation is that a key can live somewhere a server
  cannot — a password manager, on paper — which five generated passwords in a
  `.env` file cannot.

## References

- [Deployment runbook](https://github.com/LWSNLab/CareGraph/blob/main/deploy/README.md) · [Security & Privacy](../../../architecture/security.md)
