# 🔌 API Specification

> **Base URL (production):** `https://api.caregraph.de`
> **Base URL (local dev):** `http://localhost:8080`
> **Authentication:** API key in the `X-API-Key` header
> The query endpoints live under `/v1`; `/healthz`, `/readyz` and `/openapi.yaml` do not.

---

## 1. Canonical specification

The machine-readable contract is **`api/openapi.yaml` in the implementation
repository**, and every running instance serves the copy compiled into it:

```bash
curl https://api.caregraph.de/openapi.yaml
```

No API key is needed — a contract you must authenticate to read cannot be used
to decide whether to ask for a key.

It used to live in this repository as well. It no longer does, and the duplicate
was deleted rather than synchronised: two copies of a contract are two contracts.
The one that ships with the binary wins, because it is the only one a test can
compare against the handlers.

Use it directly rather than copying from this page:

- **Explore / try it:** paste the file into [editor.swagger.io](https://editor.swagger.io/).
- **Generate clients:** any OpenAPI generator (TypeScript, Python, Go, …).

This page is the human-readable summary; `openapi.yaml` wins if the two ever
disagree.

### Why you can trust it

Hand-maintained specifications drift, and a drifted specification is worse than
none — a generated client compiles, runs, and is quietly wrong. The document is
therefore not a description of the API, it is a **build gate**. `api/spec_test.go`,
`api/contract_test.go` and `api/schema_test.go` fail the build on:

| Drift | How it is caught |
| :-- | :-- |
| A route served but not documented, or documented but not served | The real Gin route table is compared with the document's paths, both ways |
| A new `code` value that nobody documented | The `ErrorCode` constants are read out of the Go source with `go/ast`, not from a list in the test |
| A new `provider_type` | Same, from `provider.Type` |
| A renamed or added JSON field | Struct tags are compared with the schema properties, both ways |
| `omitempty` on a `required` field | Struct tags are compared with the `required` list — response validation alone missed this, because every fixture happened to set the field |
| A status code a handler returns but the spec denies | Real responses are validated with `kin-openapi`, with `IncludeResponseStatus` |
| Request rules that disagree | Every request the handler answers with `400` must also be rejected by the spec's own constraints, and every other one accepted |

Twelve deliberate mutations were introduced to confirm each guard actually turns
red. Three of them initially did not — which is why the struct-tag checks exist.

**Declared OpenAPI 3.0.3, not 3.1.** The document uses `nullable` and boolean
`exclusiveMinimum`, both of which 3.1 removed. A 3.1 header over 3.0 keywords
does not fail loudly — generators drop what they do not recognise.

---

## 2. Endpoints

| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :---: |
| `GET` | `/v1/infrastructure/near` | Spatial radius search via PostGIS `ST_DWithin` | ✅ |
| `GET` | `/v1/infrastructure/search` | Typo-tolerant text search via Typesense | ✅ |
| `GET` | `/v1/infrastructure/{ik_nummer}` | One institution by 9-digit IK number ¹ | ✅ |
| `GET` | `/healthz` | Liveness — is the process working? | ❌ |
| `GET` | `/readyz` | Readiness — should this instance get traffic, and what state is each dependency in? | ❌ |
| `GET` | `/openapi.yaml` | The contract this instance implements | ❌ |

### `GET /healthz` vs `GET /readyz`

Two different questions, and conflating them causes outages. A failing
**liveness** probe makes an orchestrator *restart* the container, so it must only
fail for conditions a restart can fix. If `/healthz` checked the database, a
database blip would restart every replica in a loop. It therefore answers as long
as the process can answer, and nothing more.

**Readiness** may fail transiently: the orchestrator takes the instance out of
the load balancer and puts it back when it recovers. That is where dependencies
belong.

```json
{
  "status": "degraded",
  "checks": {
    "postgres": { "status": "ok",          "latency_ms": 1.161 },
    "redis":    { "status": "unavailable", "latency_ms": 2000.0 },
    "search":   { "status": "ok",          "latency_ms": 8.869 }
  }
}
```

Severity follows how the API actually degrades, not how important a dependency
sounds:

| Dependency | Down means | Verdict |
| :-- | :-- | :-- |
| `postgres` | Every endpoint fails | `503` — take the instance out of rotation |
| `redis` | Rate limits stop being enforced; requests still succeed | `200`, `degraded` |
| `search` | `/search` answers `503`; `/near` and the IK lookup are unaffected | `200`, `degraded` |

The body never contains the underlying error — a driver error carries the DSN,
and this endpoint needs no credential. Causes go to the server log. Results are
cached for one second, so a flood of cheap requests cannot become a flood of
database round trips.

### `GET /v1/infrastructure/near`

| Parameter | Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `lat` | `float` | ✅ | Latitude, WGS 84 (e.g. `48.7182`) |
| `lng` | `float` | ✅ | Longitude, WGS 84 (e.g. `10.7781`) |
| `radius_km` | `float` | ❌ | Search radius in km (default `10.0`, max `100.0`) |
| `type` | `enum` | ❌ | `krankenkasse`, `pflegedienst_ambulant`, `pflegeheim_stationaer`, `pflegestuetzpunkt`, `krankenhaus` |
| `limit` | `int` | ❌ | Max results (default `20`, max `100`) |

### `GET /v1/infrastructure/search`

| Parameter | Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `q` | `string` | ✅ | Query string, 2–128 characters |
| `city` | `string` | ❌ | Exact city filter, on top of the text query |
| `type` | `enum` | ❌ | Same values as `/near` |
| `limit` | `int` | ❌ | Max results (default `20`, max `100`) |

Tolerant of typos and of umlauts written plainly:

| Query | Top hit |
| :--- | :--- |
| `Charite` | **Charité** Universitätsmedizin Berlin |
| `Krankenhaus Munster` | Herz-Jesu Krankenhaus **Münster**-Hiltrup |
| `Caritas Pflegediesnt` | Caritas **Pflegedienst** |

**`total` is the number of matches, not the number returned.** Compare it with
`limit` to know whether there is more.

Results have the same shape as `/near` (without `distance_km`): the engine
ranks, and the records come from the database, so there is one schema and one
source of truth.

If a deployment runs without a search engine the endpoint answers `501`; if the
engine is down it answers `503`. Neither is an empty result — that would say
"nothing matched", which is a different and wrong statement.

### `GET /v1/infrastructure/{ik_nummer}`

Path parameter `ik_nummer` — the official 9-digit Institutionskennzeichen
(`^[0-9]{9}$`).

> ¹ **Only insurers are addressable today** — 92 of 93 resolve *on a fully
> ingested instance*. The published release archive contains care providers only,
> so on a fresh self-hosted install this endpoint answers `404` for everything
> until `make load-insurers` has run against the GKV publication. Every
> Leistungserbringer has an IK, but no public source publishes those of care
> providers or hospitals. Reach them via `/v1/infrastructure/near` or
> `/v1/infrastructure/search`. Tracked in the backlog as *Provider IK numbers*.

---

## 3. Example response (`200 OK`)

```json
{
  "total": 1,
  "data": [
    {
      "source_id": "osm:way/123456789",
      "id": "f3467c0f-7956-4483-aacb-6c0be233ff82",
      "type": "pflegedienst_ambulant",
      "name": "Ambulanter Pflegedienst",
      "parent_organization": "Pflegewelt Berlin Mitte GmbH",
      "website": "http://www.pflegewelt-berlin.de",
      "address": {
        "street": "Gertraudenstraße 19",
        "postal_code": "10178",
        "city": "Berlin",
        "state": "Berlin"
      },
      "distance_km": 0.752,
      "details": {
        "source": "openstreetmap",
        "opening_hours": "Mo-Th 08:00-17:00; Fr 08:00-16:00",
        "attribution": "© OpenStreetMap contributors (ODbL)"
      }
    }
  ]
}
```

**Optional fields are omitted, never `null`.** The record above has no
`ik_nummer` — the key is absent, not set to `null`. Test for the key's presence;
`data[0].ik_nummer === null` will not do what you want.

Required in every record: `source_id`, `id`, `type`, `name`, `address` (and
within it `street`, `postal_code`, `city`). Everything else may be missing.
`details` is source-specific and deliberately outside the stable contract — treat
every key in it as optional.

### Which identifier to store

**`source_id`.** It is derived from the source object — `osm:way/123456789` — and
it travels: it is a column in the published dataset, so every instance that
imported the same archive answers with the same value. A reference stored here
still resolves against somebody else's deployment.

**Not `id`.** That is a database primary key, minted by whichever instance wrote
the row. Two deployments give the same provider different values, and re-importing
the dataset into an empty database changes them again. It is useful for talking to
one deployment about one row, and for nothing that outlives that conversation.

This is easy to get wrong in the direction that costs most, because nothing fails
when a stored `id` stops matching. The row is simply not found, and the gap looks
like a provider that closed down.

One honest limit: `source_id` is stable, not eternal. It follows the source
object, so an OpenStreetMap way that is split or re-drawn takes a new one. What
happens to the old value is not promised yet — until it is, treat a reference that
stops resolving as a record to look up again rather than as an error.

---

## 4. Errors & auth

### Authentication

Send your key in the `X-API-Key` header:

```
X-API-Key: cg_337427fa47e2ab17_a1b2c3…
```

A key has two halves. The first (`337427fa47e2ab17`) is a **public identifier** —
quote it in a support request, it is not a secret. The second is the secret and is
shown **once**, at issuance; it is stored only as an Argon2id hash and cannot be
recovered. A lost key is revoked and reissued.

Missing, malformed and unknown keys all return the same `401` with the same
message. That is deliberate: a different answer per reason would reveal which key
ids exist.

### Rate limiting

| Tier | Requests per minute |
| :-- | --: |
| Community | 100 |
| Enterprise | 6,000 (custom SLAs available) |

Every response carries the current budget:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 98
```

Exceeding it returns `429` with `code: rate_limited` and a **`Retry-After`**
header in seconds. Limits are a continuously refilling token bucket, not a fixed
window — a short burst is smoothed out rather than resetting on the minute.

**Repeated authentication failures are limited separately** (20 per minute per
client address) and also answer `429`. Successful requests never count towards
that budget, so it only affects a client presenting bad credentials.

### One error shape, everywhere

Every `4xx` and `5xx` uses the same body — including the responses the framework
generates rather than a handler, such as an unknown path, a wrong method or a
panic. You can parse any failure the same way:

```json
{
  "error": "parameter 'lat' must be between -90 and 90",
  "code": "invalid_parameter",
  "request_id": "0dfba0529a78773f16320ab786c125f9"
}
```

**Branch on `code`, not on `error`.** The message is written for humans and may
be reworded; the code will not change.

| `code` | Status | Meaning |
| :-- | :--: | :-- |
| `invalid_parameter` | `400` | Missing, malformed or out-of-range parameter. The message names it. |
| `unauthorized` | `401` | Missing or invalid API key. |
| `not_found` | `404` | No such resource — or no such endpoint. |
| `method_not_allowed` | `405` | Path exists, method does not. `Allow` lists what does. |
| `rate_limited` | `429` | Tier limit exceeded. |
| `not_implemented` | `501` | Endpoint is in this spec but not enabled on this deployment. |
| `unavailable` | `503` | A dependency is temporarily unreachable. Retryable. |
| `timeout` | `504` | Server-side query timeout. Retryable. |
| `internal` | `500` | Unexpected failure. The cause is in the server log, never in the response. |

There is also a bodyless **`499`** — the caller disconnected before the response
was written. Nothing failed server-side; it is documented because it shows up in
proxy logs and metrics, not because a client can observe it.

An **unparseable optional parameter is rejected, not defaulted.** `radius_km=abc`
returns `400` rather than silently searching 10 km — otherwise you would get
results that look authoritative while answering a different question.

### Request correlation

Every response carries an **`X-Request-Id`** header, and every error body repeats
it as `request_id`. It is the join key to the server's logs.

Send your own `X-Request-Id` to stitch our logs to yours. It is echoed back when
it is at most 64 characters of `A–Z a–z 0–9 . _ -`, and replaced by a generated
id otherwise. When reporting a problem, quote the id — it is the difference
between "a request failed" and a specific log record.

---

## 5. Versioning

`info.version` in the document tracks the contract; the URL carries the major
version. A breaking change arrives as `/v2` and never as a changed meaning of an
existing field. Additive changes — a new optional field, a new `details` key, a
new provider type — happen within `/v1`, so parse defensively and ignore what
you do not recognise.

Fetch `/openapi.yaml` from the instance you are talking to when you need to know
exactly what it implements, rather than trusting a published copy to match the
deployment.
