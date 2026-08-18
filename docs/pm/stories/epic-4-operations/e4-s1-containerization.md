# E4-S1 — Containerization

|                  |                       |
| :--------------- | :-------------------- |
| **Epic**         | E4 — Operations & CI/CD |
| **Story Points** | 3                     |
| **Priority**     | Medium                |
| **Status**       | ✅ Done (pending review) |

> ← [Epic 4](index.md) · [Backlog](../index.md)

## User Story

As an **operator**, I want all components dockerized, so that the stack runs reproducibly anywhere.

## Description

Package every component and provide a one-command local stack, so contributors
and deployments get an identical environment.

## Acceptance Criteria

- [x] Images for Go API, Python ingestion, Postgres/PostGIS, Typesense, Redis.
- [x] `docker compose` brings up the full local stack.
- [x] The ingestion image carries `ca-certificates`, so TLS verification against
      the OS trust store works — and the build **fails** if it ever stops doing so.
- [x] **A database DSN without TLS is rejected outside local development.**
- [x] **No credentials in default values.**

## Implementation

### The ingestion image, and why it is Debian and not Alpine

`Dockerfile.ingest`, `python:3.12-slim-bookworm`, dependencies installed by `uv`
from the lockfile, running as an unprivileged user.

Alpine is the smaller base and the wrong one here. The pipelines verify TLS
against the **OS trust store** rather than certifi's bundle
(`pipelines/common/trust.py`), so the image must have one — and Alpine does not
install `ca-certificates` by default. The failure would not be loud: the code
counts the CAs and falls back to certifi with a warning, so a wrong base image
costs the tolerance for TLS-inspecting proxies rather than the whole run. That is
the fault which gets diagnosed as "the source is down" — on 2026-08-10 a Zscaler
appliance re-signing `gkv-datenaustausch.de` took IK coverage from 92/93 to
76/93 for exactly this reason.

So the image **asserts its own trust store at build time**: fewer than 100
certificates in the bundle fails the build. A base-image change that drops them
breaks CI rather than a quarterly ingestion run. Currently 150.

### Refusing plaintext to a remote database

`sslmode=disable` is correct on loopback and wrong across a network, and nothing
complains either way — the queries simply travel readable. The default is worse
than `disable`: an **unset** `sslmode` is libpq's `prefer`, which attempts TLS
and then falls back to plaintext *silently*.

Both halves of the system now refuse it: `internal/infrastructure/dsn.go` and
`pipelines/common/dsn.py`, with one override name between them,
`CAREGRAPH_ALLOW_INSECURE_DB`.

**No `CAREGRAPH_ENV` was introduced**, as this story argued. The decision is
keyed off the DSN itself — loopback, `::1` and a Unix socket are local, and
everything else is not. A Docker service name counts as remote, because from
inside a container a private bridge network is indistinguishable from the open
internet; compose therefore sets the override explicitly, with a comment saying
a multi-host deployment must not.

The Go side asks pgx what the DSN *resolves* to rather than comparing the
sslmode string, which catches the case a string comparison cannot: `prefer` is
represented as a TLS attempt plus a **plaintext fallback**, and a DSN listing
several hosts can be secure for the first and not the second.

### Graceful shutdown

SIGTERM is what an orchestrator sends on deploy, scale-down and rollback — the
routine cases. `cmd/api` drains in-flight requests for up to 20 s, comfortably
above the 15 s per-request cap, and compose sets `stop_grace_period: 30s` so
Docker does not SIGKILL mid-drain. A second signal kills immediately rather than
being swallowed.

This required `main` to return an exit code instead of calling `log.Fatal`:
`os.Exit` skips deferred calls, so the pool and the Redis client were never
closed on any fatal path.

### The healthcheck the distroless image made awkward

The runtime image has no shell, no curl and no wget — `/api` is the only
executable in it. So the binary probes itself: `/api -healthcheck` fetches
`/readyz` and exits 0 only on `200`.

Declared as `HEALTHCHECK` in the Dockerfile rather than in compose, so it travels
with the image and there is one definition. It probes **readiness**, not
liveness, because that is what gates `depends_on: service_healthy` and
load-balancer membership.

### Image sizes

| Image | Size |
| :-- | --: |
| API (`distroless/static`, static binary) | 29 MB |
| Ingestion | 377 MB |

Two declared dependencies were **unused** and are gone: `playwright` (imported
nowhere; the README told people to run `playwright install`, which downloads
browser binaries) and `polars` (zero references).

The larger win was a mistake in the first draft of `Dockerfile.ingest`, found by
reading `docker history` rather than guessing: `RUN useradd … && chown -R
ingest:ingest /app` showed up as a **227 MB layer**. `chown -R` rewrites the
metadata of every file, and a layer stores the whole of each changed file, so it
duplicated the entire application tree. Creating the user before the copy and
letting `COPY --chown` set ownership took the image from **604 MB to 377 MB** with
no change to any dependency.

That change had a side effect I first wrote down as a feature and it was a bug.
`COPY --chown` sets ownership on the copied *contents*, while `WORKDIR` had
already created `/app` itself as root — so the working directory was not writable
by the process. I documented that as deliberate hardening after checking the two
bind mounts, and the two bind mounts were the wrong thing to check: the insurer
load creates `data/raw` relative to the working directory, so it died with
`PermissionError: Permission denied: 'data'`. `RUN install -d -o ingest -g ingest
/app` before the copy fixes it, at the cost of a few bytes rather than the
duplicate tree.

**Verified afterwards with the real PDF, in the container: 93 insurers parsed** —
the count that distinguishes a correct run from the merged-row bug.

What remains is 150 MB of Debian and CPython — the floor for this base — plus
227 MB of application tree, of which pandas (76 MB), numpy (67 MB) and the PDF
stack (~57 MB) are the bulk. Those stay, deliberately; see the next section.

### Splitting the image was tried and declined

Only one command needs pandas and pdfplumber: the insurer list arrives as a PDF.
Verified by tracing the import graph — `run_dataset`, `run_search` and
`run_load providers|hospitals` import **no pandas at all**; it is reached only by
`run_load insurers`, through a lazy import inside `load_insurers()`, and by
`run_gkv`.

So they were moved into an optional extra and the result was built and measured
rather than projected:

| Image | Size |
| :-- | --: |
| without the extra | **181 MB** |
| with it | 377 MB |

196 MB, and the lean image ran the entire self-hosting path — dataset export,
dataset import, search sync, provider load — all verified against the live
database.

**It was reverted anyway, on the product owner's call.** The saving costs a single
image that can do everything: `caregraph-ingest:latest` would no longer load the
insurer PDF, and full capability would depend on a second tag existing, being
built, being published and being reached for at the right moment. For a project
whose point is that other people can self-host it, one image that does the whole
job is worth more than 196 MB — the number is not a constraint on any target
being considered.

Recorded here with the measurement so the idea does not get re-proposed as
free. What it would cost is documented; what it would save is 196 MB.

The two pieces of the attempt worth remembering:

- `--all-groups` does **not** install `project.optional-dependencies`. CI would
  have needed `--all-extras --all-groups`, or the GKV parser and exporter tests
  would have silently stopped running.
- A missing extra surfaces as `ModuleNotFoundError: No module named 'pandas'`,
  which reads as a broken image rather than a deliberate build. Any future split
  has to explain itself at the point of failure.

## Defects found and fixed

- **The Typesense healthcheck had never once passed.** It called `curl`, and the
  image has no curl — nor wget, nc or python3. The container had been
  `unhealthy` for 46 hours while `/health` answered `{"ok":true}` the whole time.
  It went unnoticed because `api` only waited for `service_started`. The probe now
  uses `bash`'s `/dev/tcp` (the only thing in the image that can reach a socket)
  and greps the response body, and `api` waits for `service_healthy`.
- **`db/migrations` was excluded from the ingestion build context**, which is my
  own mistake from earlier in this story. `dataset export` stamps the newest
  migration name into `MANIFEST.json`; without the directory it stamped
  `"unknown"`, and `dataset import` refuses an archive whose stamp does not match
  the schema in front of it. Every archive cut inside the container would have
  been unimportable anywhere else — on the self-hosting path this release exists
  for. Verified both directions round-trip now: container→host and host→container.
- **The Python runners still carried `caregraph_ingest:devingest`.** The
  "no credentials in defaults" criterion was marked done last week when only the
  two Go binaries had been fixed; three `DEFAULT_DSN` constants were still there.
  That tick was premature and is now actually true.
- **A denylist where an allowlist was needed.** The first version of the Python
  guard tested `sslmode` against `{disable, allow, prefer}`, so a DSN with no
  `sslmode` at all passed — the exact case that matters most, since it is libpq's
  silent-fallback default. Both implementations now allow only
  `{require, verify-ca, verify-full}`, so an unrecognised or absent value fails
  closed.
- **`pipelines/uv.lock` was in `.gitignore`.** Found because
  `Dockerfile.ingest` installs with `uv sync --locked` and copies the lockfile:
  the build passed locally, where the ignored file exists, and **failed on a
  clean checkout** — verified by building from a fresh clone. An ignored lockfile
  is a defect on its own terms as well, since it means every build resolves
  dependencies afresh, which is the opposite of this story's user story. Now
  tracked, and `ci.yml` syncs with `--locked` so a dependency change without a
  lockfile update fails there rather than in an image build.
- **The chown fix silently broke the insurer path**, and the note claiming
  otherwise was worse than the bug. Detail above; the lesson is that "verified"
  meant "verified the paths I thought of" — the export path and the bind mounts —
  while the failing path wrote to a relative directory neither of them covered.
- **`GKVParser` created its download directory whether or not it downloaded.**
  Surfaced by the container and fixed here: `download_if_url` called
  `mkdir(parents=True)` before checking whether the source was a URL, so parsing
  a local PDF needed write access to a directory it never wrote to. Two
  consequences, both silent. Every parse — including every test run — left an
  empty `data/raw` behind, at the repository root rather than next to the real
  inputs, because the default was cwd-relative. And in the container that path
  resolved to `/app/data/raw`, outside the bind mount, so a URL download would
  have been discarded with the container.

  The `mkdir` now happens only in the download branch, and the defaults come from
  `pipelines/common/paths.py`, derived from the package location instead of the
  working directory: `RAW_DIR` is the same directory whether the caller starts in
  the repository root, in `pipelines/`, or in the image — where it is now the
  mount. Two regression tests cover both halves. Re-verified after the change:
  93 insurers, SKD BKK and SVLFG one row each.
- **Six `make` targets lost their database connection**, and this one was the
  release blocker. Removing the `DEFAULT_DSN` constants from the Python runners
  was right, but only `api`, `apikey-dev` and `apikeys` were switched to read
  `.env` — `dataset-import`, `dataset-export`, `load-providers`, `load-insurers`,
  `load-hospitals` and `search-sync` had been relying on those compiled-in
  defaults. So `make dataset-import FILE=…`, which the README gives a self-hoster
  as step 2, failed with "no database DSN" *even with a correct `.env` present*.
  Found by walking the quickstart from an empty database rather than by running
  the test suite, which never invokes the Makefile. All Python targets now go
  through `with_env`, and `test-db` lost its hardcoded fallback DSN with them.
- **Typesense and Redis had hardcoded host ports.** `6379` is occupied on any
  machine that already runs a Redis, and the stack was simply unstartable there —
  the only fix being to edit a file the user did not write. Now
  `${TYPESENSE_PORT:-8108}` and `${REDIS_PORT:-6379}`, still bound to loopback.
- **The host port was hardcoded.** `8080` is busy on a developer machine, as it
  was on mine. Now `${CAREGRAPH_PORT:-8080}`, matching what `POSTGRES_PORT`
  already did — a self-hoster should not have to edit the compose file.

## Release acceptance test

Run before the first release, in an isolated compose project on separate ports so
nothing touched the development stack or its data — verified afterwards: 9,192
rows and 93 insurers still there, no leftover containers or volumes.

Against a database created **only** by the migrations on an empty volume, seeded
**only** from the published archive:

| | |
| :-- | :-- |
| `make up` | 9 tables, PostGIS 3.4, 0 rows; db, redis and typesense all healthy |
| `make db-roles-dev` | least-privilege roles get their throwaway passwords |
| `make dataset-import` | 7,522 rows inserted from the release archive |
| `make search-sync` | 7,522 documents indexed |
| `make bootstrap FILE=…` | all three steps, and the no-FILE branch prints usable instructions |
| `make tidy && make stack` | four healthy containers, API included |
| `make apikey-dev` | key issued and accepted |
| `/healthz`, `/readyz`, `/openapi.yaml` | 200 without a key |
| `/near` | real hits with distances, nearest first |
| `/search` | typo- and umlaut-tolerant (`Pflegediesnt` → 727, `Munster` → Örtzetal) |
| Auth | missing, wrong and malformed keys all `401` |
| Rate limiting | 130 requests → 103× `200`, 27× `429` with `Retry-After` and `code: rate_limited` |
| Error contract | `400`/`404`/`405` all in the one JSON shape, stable `code` |
| Degradation | Typesense down → `/search` `503` while `/near` stays `200`, `/readyz` `degraded` |
| | Postgres down → `/readyz` `503`, `/healthz` stays `200`, container turns **unhealthy after 51 s** and recovers 12 s after Postgres returns |
| Graceful shutdown | drain logged and completed |
| Dataset round trip | export and re-import inside the container; manifest carries schema, ODbL licence, attribution and "insurers excluded" |
| Both images | built from a clean checkout; trust-store assertion and both CI image checks pass |

**A self-hoster's IK lookup answers `404` for everything**, and that is correct
rather than broken: the archive is providers only, so insurers are absent until
`make load-insurers` runs against the GKV PDF. The archive's own manifest says so.
The API page's "92 of 93 insurers resolve" describes a fully ingested instance,
not what the release archive gives you — worth a sentence there.

**What CI does not cover, honestly:** four tests skip because their source files
are deliberately not in the repository — the GKV PDF and the Bundes-Klinik-Atlas
export. With the integration environment set, 329 pass and those 4 skip. The
parser logic is covered by synthetic fixtures; it is the real-file integration
that is unverified in CI.

## Decisions recorded

**Per-stage config files are deliberately not the plan.** Environment variables
stay the mechanism (12-factor). Committing `config/prod.yaml` or
`.env.production` invites secrets into the repository and drifts from what is
deployed.

**Where logs are collected: per-service streams.** The API writes JSON to stderr
and owns nothing beyond that. One file for several producers loses isolation and
per-service retention, and a chatty pipeline run drowns the API. `docker logs` /
`journalctl -u` per service is the recommendation; a single file only makes sense
on a single host with no log stack, and then only because every record carries a
`service` field. **Writing an own supervisor to capture children's stdout is
explicitly not the plan** — restart policy, signal forwarding, zombie reaping and
rotation are what systemd and Docker already do, and the pipelines are scheduled
jobs rather than long-lived children of the API.

**Image builds live in their own workflow** (`.github/workflows/images.yml`) with
a paths filter, not in `ci.yml`. The ingestion image takes minutes to build and
this repository is private, so every run consumes billed Actions minutes; it runs
when something that goes *into* an image changes. Two of its steps guard the
mistakes above: the API healthcheck must fail with no server running, and the
ingestion image must be able to read `db/migrations`.

**The compose stack still connects the API as the database owner.** `.env.example`
points the host-run API at the read-only `caregraph_api` role, but that role has
no password until `make db-roles-dev` has run against a live container, which
compose cannot depend on. Left as is and written down rather than papered over.

## Dependencies

- **Depends on:** —
- **Blocks:** E4-S2 (CI builds images)

## Risks

- ~~Image bloat / slow builds~~ — mitigated by multi-stage builds, `distroless`
  for the API, removing two unused dependencies, and eliminating a duplicated
  227 MB `chown` layer. The ingestion image is 377 MB, of which 150 MB is the
  base image.

  **Shrinking it further was measured, built and then rejected** — see
  "Splitting the image was tried and declined" above.
- ~~"Minimal base image" and "OS trust store" pull in opposite directions.~~
  Resolved by choosing Debian slim *and* asserting the store at build time, so
  the trade-off cannot be silently lost later.

## Definition of Done

- [x] Acceptance criteria fulfilled
- [x] Tests passing — Go 8 packages, Python 310 passed / 21 skipped, new: 12 Go
      DSN cases and 25 Python DSN cases
- [x] CI covers the new code — `images.yml`, plus the DSN guards under `go test` / `pytest`
- [x] Documentation updated
- [ ] Code reviewed

## References

- [System Overview](../../../architecture/system-overview.md) · [Security & Privacy](../../../architecture/security.md)
