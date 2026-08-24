# E1-S6 — IK-Nummer enrichment (insurers)

|                  |                          |
| :--------------- | :----------------------- |
| **Epic**         | E1 — Ingestion & ETL     |
| **Story Points** | 3                        |
| **Priority**     | Medium                   |
| **Status**       | ✅ Done |

> ← [Epic 1](index.md) · [Backlog](../index.md)

## User Story

As a **data engineer**, I want the statutory health insurers enriched with their official Institutionskennzeichen, so that records carry a stable external identifier instead of being keyed on their name.

## Description

The GKV insurer list (E1-S1) has no IK-Nummer, so insurers are currently identified by name — which is fragile across yearly publications and useless for cross-source matching. This story resolves the IK for each insurer from the official *Kostenträgerdateien* and writes it to `care_infrastructure.ik_nummer`.

## Acceptance Criteria

- [x] Current Kostenträgerdateien are discovered and downloaded from gkv-datenaustausch.de.
- [x] `IDK` segments are parsed into an IK ↔ name directory; the authoritative Kassensitz list is parsed on top of it.
- [x] At least 95% of the insurers are matched to an IK. *(**99% — 92/93.** Only EY Betriebskrankenkasse appears in no official source.)*
- [x] Unmatched insurers are reported explicitly, never silently dropped.
- [x] `ik_nummer` is populated in `care_infrastructure` and stays stable across runs.

> **The figures below say "92 insurers" and are left as recorded.** They were
> accurate when measured; the total became **93** on 2026-08-10, when a parser
> defect that had merged two insurers into one row was fixed
> ([E1-S1](e1-s1-gkv-insurer-list.md#fixed-after-the-fact-two-insurers-in-one-row-2026-08-10)).
> That correction also revealed a **wrong IK mapping**: the merged row carried
> `105508787`, which belongs to the SVLFG, under a name presenting as SKD BKK.
> Both now hold their own — SKD BKK `108833505`, SVLFG `105508787`.

## Technical Notes

**Source:** [Kostenträgerdateien Pflege](https://www.gkv-datenaustausch.de/leistungserbringer/pflege/kostentraegerdateien_pflege/kostentraegerdateien.jsp) (GKV-Spitzenverband). Official, machine-readable, updated on the 1st of each calendar quarter, and not disallowed by `robots.txt`.

### ✅ Resolved: the sources were never broken (2026-08-10)

For a while these sources looked unreachable and coverage sat at 76/93:

```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed:
unable to get local issuer certificate
```

**The first diagnosis recorded here was wrong.** It said the server serves an
incomplete certificate chain. Inspecting what the server actually presents showed
something else:

```
0 s:CN=gkv-spitzenverband.de, O=Zscaler Inc.
1 s:CN=Zscaler Intermediate Root CA (zscalerthree.net)
2 s:CN=Zscaler Intermediate Root CA (zscalerthree.net)
```

That is not the GKV's certificate. A **Zscaler appliance was inspecting TLS** on
the development machine and re-signing these connections. Selectively, too —
`pypi.org` was untouched, the `gkv-*` domains were not. The Zscaler root sits in
the macOS system keychain, which is why `openssl s_client` reported
`Verify return code: 0 (ok)` while `requests` failed: requests validates against
certifi's bundle of *public* roots, which cannot contain a private corporate one.

So there was no defect in the GKV's infrastructure, and none in CareGraph. The
symptom was local, and it pointed away from its cause — which is why the guard
described below matters more than the outage did.

**Fix:** `pipelines/common/trust.py` routes verification through the OS trust
store via `truststore`, called from each entry point before any network work.
Verification stays fully on; only the *set of trusted roots* changes to the one
the machine's administrator configured. On a machine without interception (CI,
production) the OS store validates the genuine certificate exactly as certifi
would, so it is safe unconditionally.

| | before | after |
| :-- | --: | --: |
| Sources loaded | 1 of 3 | **3 of 3** |
| Directory entries | 93 | **1,241** |
| IK coverage | 76/93 (82%) | **92/93 (99%)** |

`verify=False` was never an option: these are requests to institutions in the
statutory health system, and accepting any certificate would trade
authentication for convenience. A test asserts no literal `verify=False` is
introduced.

> **Caveat on that test.** It catches a literal only. `AddressScraper._fetch`
> relaxes verification through a variable and predates this work; it exists for
> the three insurer hosts whose certificates are genuinely invalid. An
> unverified Impressum can feed a wrong address into the dataset, so narrowing
> that fallback to an explicit per-host allowlist is worth doing — tracked
> separately, not silently fixed.

### Partial failure is no longer reported as success

`load_all()` used to return only an entry count. A caller could not distinguish
a complete directory from one built on a third of its inputs — the directory was
simply thinner and every number downstream quietly worse. That is exactly what
happened on 2026-08-10: both exchange-file sources were unreachable, coverage
fell from 91 to 75, and the only trace was a warning several screens up the log.

It now returns a **`DirectoryReport`** listing every source with `ok`, `rows` and,
on failure, the reason:

```
📚 IK directory: 93 entries from 1/3 sources (INCOMPLETE)
   ⚠️  unavailable: Kostenträgerdateien SGB V — SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
       certificate verify failed: unable to get local issuer certificate
```

The same reason is repeated in the regression guard's abort message, so the
operator sees *why* coverage is low next to the number rather than having to
correlate the two.

Two details worth keeping:

- **A sector with one unavailable file is not `ok`.** One missing file must not
  lose the rest of the directory — that behaviour stays — but the sector reports
  `1 of 2 files failed` rather than silent partial success.
- **The cause is unwrapped, not truncated.** `requests` reports a TLS failure as
  `SSLError(MaxRetryError(SSLError(…)))`, where the outer message is ~260
  characters of connection-pool boilerplate and the actionable sentence sits at
  the very end. Cutting the front kept the noise and discarded the diagnosis, so
  the chain is followed first — through `args[0].reason`, since urllib3 does not
  set `__cause__`.

Format is EDIFACT-like; the relevant segment carries IK and name directly:

```text
IDK+100820488+99+Brandenburgische BKK'
```

Findings from the exploratory pass:

- One file per association: `AO*` (AOK), `BK*` (BKK), `IK*` (IKK), `BN*` (Knappschaft), `LK*` (landwirtschaftlich), `EK*` (Ersatzkassen); extensions `.ke0`/`.ke1`/`.ke4`.
- Encoding is **ISO-8859-1**, not UTF-8.
- 787 distinct IK numbers across the files.
- Naive normalised matching already resolves **81 of 92** insurers (88%). The misses are abbreviation cases — *Techniker Krankenkasse* → `TK`, *Siemens-Betriebskrankenkasse (SBK)* → `SBK`, *Kaufmännische Krankenkasse* → `KKH` — so a small alias table should clear the 95% bar.
- **Filenames embed the quarter** (`BK06Q326.ke0`), so the current files must be discovered from the page; hardcoding a URL would silently go stale.

### What was actually built

`pipelines/parsers/ik_verzeichnis.py`, wired into `pipelines/run_load.py`.

**Two sectors are required, and neither suffices alone.** The first attempt used only the SGB XI (Pflege) files and reached 83%. Those list an insurer's *Pflegekasse* — a different institution with a different IK. The SGB V files carry the *Krankenkasse*. Measured: Pflege alone misses VIACTIV, SECURVITA, SBK and AOK Schwarzwald-Baar-Heuberg; SGB V alone misses TK and hkk. Loading both, SGB V first, yields 93%.

**Matching is on token sets, not strings.** The directory routinely reverses word order (`Merck BKK` ↔ `BKK Merck`), abbreviates (`Seidensticker` → `Seidenst.`, `Saarland` → `SL`) and appends annotations (`BKK mkk (ehem. BKK VBU)`). A concatenated key survives none of that; comparing sets of identifying tokens survives all of it.

**Three precision guards**, each added after a wrong match was observed in the real data:

| Guard | The wrong match it prevents |
| :-- | :-- |
| Care-fund and `/Ost` entries are never indexed | attaching a *Pflegekasse* IK to a Krankenkasse |
| Entries reducing to a category token only | `BKK S-H` → `{bkk}` matched every other BKK (hit `EY BKK`) |
| The same guard on the query side | `R+V BKK` → `{bkk}` matched `BKK DEMAG KRAUSS-MAFFEI` |

No edit-distance fuzziness anywhere: a wrong IK looks entirely plausible in the data and nothing downstream would flag it, whereas a missing one is in the run report.

**Existing rows are rekeyed, not duplicated.** The 92 insurers were already stored under `gkv:<name>`. Switching the key to `ik:<number>` would have inserted 92 second rows, so the loader rewrites the old key in place first. Verified: 86 rekeyed, total unchanged at 92, and a second run reports `rekeyed=0`.

### Which IK? — the decision that mattered most

An insurer holds **several** IKs: one *Kassensitz-IK* identifying the institution, and several *Abrechnungs-IKs* for billing. The Kostenträgerdateien list billing IKs, so a first version of this story stored whichever one happened to be read first — 26 of 86 values were an arbitrary pick. For a field meant to be *the* stable external identifier that is not good enough: two consumers matching on `ik_nummer` could disagree.

The primary source is therefore **Schlüsselverzeichnis 8a of the Bewertungsausschuss** (§ 87 SGB V), which lists exactly one Kassensitz-IK per insurer (93 rows). The Kostenträgerdateien remain as a fallback for insurers it does not cover.

Two independent confirmations that the source is right: R+V's own Impressum states `105823040`, matching the list exactly; and BKK24's value agreed with an unrelated third-party directory.

**Discovery, again.** The document is versioned in its filename (`S_8a_ABRIK_035.PDF`) and the server answers unknown versions with an **HTML page under HTTP 200** — so versions are probed upward and validated by PDF magic bytes, never by status code.

**PDF extraction glues words** (`AOKNordost`, `BKKSchwarzwald-Baar-Heuberg`), which no token set can match. A second, order-preserving concatenated key handles it; the token index still handles the opposite problem of reversed word order. Both are needed.

### The one without an IK

`EY Betriebskrankenkasse` — checked against the Kassensitz list and all four Kostenträgerdatei sectors (SGB V, Pflege, Krankenhäuser, Apotheken), plus its own Impressum. It keeps its `gkv:<name>` key and is listed on every run. `pipelines/data/ik_overrides.json` is ready for a curated value and intentionally empty: an invented IK would be worse than none.

### Rekeying without duplicates

Rows may carry an older key — the name key from before IKs existed, or a superseded IK (the official list corrects these between versions; AOK Nordost changed between v011 and v035). The loader rewrites the key in place before upserting, matched on name. Verified: 13 rows rekeyed on the switch to Kassensitz-IKs, 92 insurers before and after, `rekeyed=0` on the next run.

## Dependencies

- **Depends on:** E1-S1 (the insurer list to enrich)
- **Blocks:** nothing hard; materially improves E1-S5 (IK is the strongest dedup key)

## Risks

- **Name matching is ambiguous** for a handful of insurers — mitigate with an explicit alias table plus a report of unmatched entries, rather than fuzzy-matching aggressively and mis-assigning an IK.
- **Quarterly file rotation** breaks hardcoded URLs — discover filenames instead.
- **This does not solve provider IKs.** The Kostenträgerdateien list the *payers* (insurers), not the *Leistungserbringer*. Provider IKs live in the DCS data behind the insurer portals, which are not scrapeable (see [E1-S2](e1-s2-provider-scrapers.md)); obtaining them needs a data-sharing agreement or municipal open data.

## Definition of Done

- [x] Acceptance criteria fulfilled
- [x] Tests passing (38 for this module, 205 total; all matcher tests run offline)
- [x] CI covers the new code
- [x] Documentation updated
- [x] Code reviewed

## References

- [Data Schema](../../../architecture/data-schema.md) · [Data Sources & Licensing](../../../legal/data-licensing.md)
