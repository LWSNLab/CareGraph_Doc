# E4-S3 — Observability

|                  |                       |
| :--------------- | :-------------------- |
| **Epic**         | E4 — Operations & CI/CD |
| **Story Points** | 3                     |
| **Priority**     | Low                   |
| **Status**       | ⏳ Planned            |

> ← [Epic 4](index.md) · [Backlog](../index.md)

## User Story

As an **operator**, I want health checks and metrics, so that I can monitor the service and catch failures early.

## Description

Expose service health and track ingestion-run status, so operational problems are visible and alertable.

## Acceptance Criteria

- [x] ~~`/healthz` reports DB/Redis/Typesense status.~~ **Done as `/readyz`**
      *(2026-08-16, alongside E3-S5)* — see the correction below.
- [ ] Ingestion run status is tracked and alertable.

## The criterion was wrong, and doing it as written would have caused an outage

`/healthz` probing its dependencies is the obvious reading, and it is the
dangerous one. A failing **liveness** probe makes an orchestrator *restart* the
container. A restart cannot fix someone else's database, so a Postgres blip
would have restarted every replica in a loop — turning a recoverable dependency
failure into a total one, at the worst possible moment.

The two questions are different and now have separate endpoints:

| | Asks | On failure |
| :-- | :-- | :-- |
| `GET /healthz` | Is this process working? | The orchestrator restarts the container |
| `GET /readyz` | Should this instance get traffic? | The orchestrator removes it from the load balancer, and puts it back on recovery |

Dependencies belong in the second. `/healthz` is unchanged and answers as long
as the process can answer, which is the whole of what it claims.

### Severity follows how the API actually degrades

Not how important the dependency sounds:

| Dependency | Down means | Verdict |
| :-- | :-- | :-- |
| `postgres` | Every endpoint fails | `503` — take the instance out of rotation |
| `redis` | Quotas stop being enforced; requests still succeed (the limiter fails open by design) | `200`, `degraded` |
| `search` | `/search` answers `503`; `/near` and the IK lookup are unaffected | `200`, `degraded` |

Verified by stopping the containers: with Redis down `/readyz` reported
`degraded` at `200` and `/near` still answered `200`; with Postgres down it
reported `unavailable` at `503` while `/healthz` stayed `200`.

### Two things the endpoint deliberately does not do

- **It never puts the probe error in the body.** A driver error carries the DSN,
  the host and the port, and `/readyz` needs no credential. The body reports a
  state per dependency; the cause goes to the log under the request id, exactly
  as it does for a `500`. There is a test that greps the response for the host,
  the port and the driver's wording.
- **It does not re-probe on every request.** Results are cached for one second.
  An unauthenticated endpoint that issues a query per dependency is an
  amplification vector — cheap HTTP requests become database round trips. One
  second is far below any sensible probe interval, and a test covers both halves:
  twenty requests run the probe once, and the cache does expire.

Each probe is bounded at two seconds, because a probe that hangs is
indistinguishable from a dependency that is down and the orchestrator is waiting.

## Technical Notes

Ingestion runs should persist a status record and emit alerts on failure. That
is the remaining half of this story.

### Already done, so this story does not need to

Error handling in the pipelines was audited on 2026-08-10 and the gaps that were
*error handling* rather than *logging format* are closed:

| | |
| :-- | :-- |
| `run_gkv.py` had no exit code | `main()` returned `None`, so a failed run looked successful to a scheduler. Now returns 0/1 with a `log.exception` traceback. |
| Partial source failure read as success | `IKVerzeichnis.load_all()` returns a `DirectoryReport` naming every source and why it failed — see [E1-S6](../epic-1-ingestion/e1-s6-ik-enrichment.md#partial-failure-is-no-longer-reported-as-success). |
| No traceback anywhere | There were **zero** `log.exception` calls. Unexpected failures are now logged with `exc_info`. |
| The scraper had no logger at all | Only `print()`. It has one now; its broad fetch-loop `except` logs at DEBUG with a traceback instead of failing silently. |

Already sound before the audit, worth not re-litigating: all six `requests` calls
carry timeouts, the OSM scraper retries with exponential backoff and raises after
exhausting them, and `run_load`/`run_providers` already had meaningful exit codes.

### Still open here — the logging format

**Inherited from [E3-S6](../epic-3-api-gateway/e3-s6-error-contract.md): align the
Python pipelines on the same log schema.** The Go API now emits JSON to stderr
with a settled field set — `time`, `level`, `msg`, `service`, `request_id`,
`error` — via `slog`. The pipelines still call `logging.basicConfig` with a
plaintext format, so logs from the two halves of the system cannot be queried
together.

**The Go half is now consistent with itself** *(2026-08-16)*. It was not before:
the router used `gin.Logger()`, which wrote a plain-text line per request to its
own writer while everything else wrote JSON. That made the *highest-volume*
producer in the service the one an aggregator could not parse. `httpx.AccessLog`
replaces it — one `slog` record per request carrying `method`, `path`, `status`,
`duration_ms`, `bytes`, `client_ip` and the `request_id`, so an access record
joins to the handler's own records for the same request. The level carries the
meaning, so a filter alone separates the interesting ones: `4xx` is a warning,
`5xx` an error, and a client that hung up (`499`) is neither — it would otherwise
land in the same bucket as real server failures.

Worth noting what the remaining alignment is and is not:

- The valuable part is the **shared field schema**, not a shared configuration
  mechanism. A common YAML consumed by both was considered and rejected: Python
  has `dictConfig` and Go has nothing equivalent for `slog`, so it would mean
  hand-rolling a loader for three values that work as environment variables in
  both languages (`CAREGRAPH_LOG_LEVEL` already does).
- A `service` field is what makes records attributable once several producers are
  collected together. Without it, aggregated logs cannot be un-mixed.
- **Typesense cannot be brought into this.** It is a third-party binary
  (`typesense/typesense:0.25.2`) with its own flags and format; normalising it
  would happen at the collector, if at all.
- **Decide what happens to `print()`.** There are 20 calls in pipeline code
  writing progress and summaries to stdout while diagnostics go to stderr in a
  different format. That split is deliberate today — the summary is for a human
  running the command — so folding it into structured logging is a decision about
  the CLI's output, not a bug to fix silently.

## Dependencies

- **Depends on:** E1 (ingestion), E3-S1…S4 (API running)
- **Blocks:** —

## Risks

- Health checks that are too shallow give false confidence.

## Definition of Done

- [ ] Acceptance criteria fulfilled
- [ ] Tests passing (unit + integration where relevant)
- [ ] CI covers the new code (pipeline extended if needed)
- [ ] Documentation updated
- [ ] Code reviewed

## References

- [Security & Privacy](../../../architecture/security.md)
