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

- [ ] `/healthz` reports DB/Redis/Typesense status.
- [ ] Ingestion run status is tracked and alertable.

## Technical Notes

`/healthz` handler is stubbed (returns `ok`); extend it to probe dependencies. Ingestion runs should persist a status record and emit alerts on failure.

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
together. Worth noting what the alignment is and is not:

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
