# E1-S1 — GKV insurer list

|                  |                          |
| :--------------- | :----------------------- |
| **Epic**         | E1 — Ingestion & ETL     |
| **Story Points** | 5                        |
| **Priority**     | High                     |
| **Status**       | ✅ Done                  |

> ← [Epic 1](index.md) · [Backlog](../index.md)

## User Story

As a **data engineer**, I want the official GKV insurer PDF parsed and normalized, so that insurer data becomes machine-readable.

## Description

Parse the official GKV statutory-insurer list — a grid-less PDF whose rows wrap across several visual lines — into structured records: name, homepage, supplementary contribution rate (*Zusatzbeitrag*), and the regions the insurer is open in.

## Acceptance Criteria

- [x] All insurers extracted (coordinate-based parsing; handles wrapped rows).
- [x] Contribution rate parsed to a number; nationwide flag derived.
- [x] Regions normalized to the 16 federal states.
- [x] Manual overrides for bot-blocked insurers.

## Technical Notes

Coordinate-based `pdfplumber` extraction (column x-edges derived from the header row, with a fallback); address enrichment via impressum scraping; Bundesland normalization by longest-prefix match. Implemented in `pipelines/parsers/` and `pipelines/scrapers/`.

## Fixed after the fact — two insurers in one row (2026-08-10)

**The dataset held 92 insurers where the source lists 93.** One row stood for two
of them, with both names and both URLs concatenated:

```
name    = SKD BKK Sozialversicherung für Landwirtschaft, Forsten und Gartenbau (SVLFG)
website = skd-bkk.dewww.svlfg.de          ← does not resolve
ik      = 105508787
```

**Cause.** A new entry was detected by "the Zusatzbeitrag column contains a
digit". The SVLFG levies none — its cell reads *"wird nicht erhoben"* — so the
line looked like a wrapped continuation and was folded into the entry above.

**Why it was worse than a cosmetic defect.** `105508787` is the **SVLFG's** IK.
An official identifier was attached to a record presenting mostly as SKD BKK, so
a client resolving that IK got the wrong institution. The real numbers are
`108833505` (SKD BKK) and `105508787` (SVLFG), per Schlüsselverzeichnis 8a.

**Why nobody noticed.** The end-to-end test derived its expected count from
`\d,\d\d\s*%` occurrences in the PDF text — the same signal the parser used to
detect an entry. Test and parser agreed that an insurer is by definition
something with a numeric rate, so a merged row was invisible to both. The test
now counts **homepages** instead, and cross-checks that numeric plus
stated-in-words rates add up to that number.

**The fix.** `_starts_entry` requires the name column *and* the Zusatzbeitrag
column to be filled — presence of a value, not its numeric shape. Note that
position alone cannot decide this: wrapped name lines (`(SBK)`,
`Gartenbau (SVLFG)`) begin at exactly the same x-coordinate as a new entry.

Three supporting changes:

- **A missing rate is `NaN`, not `0.00 %`.** PostgreSQL `NUMERIC` accepts `'NaN'`
  and `NaN is None` is false, so the value had to be filtered explicitly or the
  SVLFG would have carried a stored rate of NaN.
- **A merge guard.** The parser now warns when a website contains a second
  `www.` or a name exceeds 80 characters. Both signals would have caught this on
  the first run; a warning rather than an exception, since it is a heuristic.
- **Migration `0005`** removes the stale merged row. The loader could not: the
  merged name no longer appears in the source so no upsert matches it, and
  `ik_nummer` is UNIQUE, so the SVLFG could not take its own IK while the old row
  held it.

**Result.** 93 insurers, 92 with an IK (only EY BKK has none anywhere), longest
name 68 characters, no concatenated URLs. Verified against the real PDF from
three independent directions: 92 numeric rates + 1 textual = 93 homepages.

## TLS downgrades are now the exception, not the retry (2026-08-10)

`AddressScraper._fetch` used to try every URL twice — once with certificate
verification, once **without** — and then over plain http. So for any host, a
certificate error was answered by ignoring the certificate.

That matters because the addresses this scraper extracts land in
`care_infrastructure`. Anyone able to intercept one of those connections could
supply a wrong postal address, and nothing in the data distinguished an address
read over verified TLS from one read over an unauthenticated connection. No
credentials were at risk; data integrity was.

**Relaxation is now allowlist-only — and the allowlist is empty.** That was the
surprise. Of the three hosts whose certificates fail validation:

| Host | With verification off | Verdict |
| :-- | :-- | :-- |
| `bkk-deutsche-bank.de` | HTTP 200 | has a manual override, so never reaches the fetch path |
| `bkk-miele.de` | ConnectionError either way | relaxing changes nothing; also overridden |
| `pflegeheim-michelberg.casa-reha.de` | HTTP 403 | server blocks the bot regardless |

So not one host gains anything from an unverified connection. The initial plan
assumed three entries were needed; measuring whether relaxation actually *yields
content* — rather than just whether the handshake fails — reduced it to none.

The mechanism is kept rather than deleted: it is the reviewed place to add a host
if one ever needs it, and a test asserts the shipped set is empty so an addition
has to be deliberate.

**Downgrades are recorded.** A host reachable only over plain http (two of them:
`suedzucker-bkk.de`, `seniorenheim-eggmuehl.brk.de`) is logged once at WARNING and
its address is stored as `Success (plaintext http)` instead of `Success`, following
the existing `Success (Override)` convention. An http first hop is
attacker-controllable even when it redirects to https, so the mark stays either way.

Verified against real endpoints: `expired.badssl.com` and `self-signed.badssl.com`
are now refused outright; a host with a valid certificate is unaffected.

## Dependencies

- **Depends on:** —
- **Blocks:** E1-S4 (the loader consumes this parsed dataset)

## Risks

- Yearly PDF layout changes can shift column positions — mitigated by header-derived edges + a positional fallback.

## Definition of Done

- [x] Acceptance criteria fulfilled
- [x] Tests passing (66 tests: parser, address scraper, exporter — incl. an integration test against the official PDF)
- [x] CI covers the new code (pipeline extended if needed)
- [x] Documentation updated
- [x] Code reviewed

## References

- [Data Schema](../../../architecture/data-schema.md)
