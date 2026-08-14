# 🔌 API Specification

> **Base URL (Production):** `https://api.caregraph.de/v1`
> **Base URL (Local Dev):** `http://localhost:8080/v1`
> **Authentication:** API key via HTTP header (`X-API-Key`)

---

## 1. Canonical Specification

The machine-readable contract lives in a single source of truth:

**➡️ [`openapi.yaml`](openapi.yaml)** (OpenAPI 3.1.0)

Use it directly — do not copy-paste from this page:

- **Explore / try it:** paste the file into [editor.swagger.io](https://editor.swagger.io/).
- **Generate Go DTOs & server stubs:** `oapi-codegen -package api docs/api/openapi.yaml`.
- **Generate clients:** any OpenAPI generator (TypeScript, Python, etc.).

This page is the human-readable summary; `openapi.yaml` always wins if the two ever disagree.

---

## 2. Endpoints

| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :---: |
| `GET` | `/infrastructure/near` | Spatial radius search via PostGIS `ST_DWithin` | ✅ |
| `GET` | `/infrastructure/search` | In-memory fuzzy text search via Typesense (C++) | ✅ |
| `GET` | `/infrastructure/{ik_nummer}` | Fetch a single institution by 9-digit IK number ¹ | ✅ |
| `GET` | `/healthz` | Liveness probe — does **not** yet check the database or Redis (E4-S3) | ❌ |

### `GET /infrastructure/near`

| Parameter | Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `lat` | `float` | ✅ | Latitude, WGS 84 (e.g. `48.7182`) |
| `lng` | `float` | ✅ | Longitude, WGS 84 (e.g. `10.7781`) |
| `radius_km` | `float` | ❌ | Search radius in km (default `10.0`, max `100.0`) |
| `type` | `enum` | ❌ | `krankenkasse`, `pflegedienst_ambulant`, `pflegeheim_stationaer`, `pflegestuetzpunkt` |
| `limit` | `int` | ❌ | Max results (default `20`, max `100`) |

### `GET /infrastructure/search`

| Parameter | Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `q` | `string` | ✅ | Query string, min length 2 (e.g. `"Caritas Pflegedienst"`) |
| `city` | `string` | ❌ | Optional city filter |

### `GET /infrastructure/{ik_nummer}`

Path parameter `ik_nummer` — the official 9-digit Institutionskennzeichen (`^[0-9]{9}$`).

> ¹ **Only insurers are addressable today** — 92 of 93 resolve. Every
> Leistungserbringer has an IK, but no public source publishes those of care
> providers, so their `ik_nummer` is `null`. Reach them via
> `/infrastructure/near` or `/infrastructure/search`. Tracked in the backlog as
> *Provider IK numbers*.

---

## 3. Example Response (`200 OK`)

```json
{
  "total": 1,
  "data": [
    {
      "id": "c3b9a12e-1234-5678-90ab-cdef12345678",
      "ik_nummer": "490123456",
      "type": "pflegedienst_ambulant",
      "name": "Ambulanter Pflegedienst Muster",
      "parent_organization": "Caritasverband",
      "website": "https://pflegedienst-muster.de",
      "address": {
        "street": "Bahnhofstraße 12",
        "postal_code": "86609",
        "city": "Donauwörth",
        "state": "Bayern"
      },
      "distance_km": 1.42,
      "details": {
        "phone": "+49 906 123456",
        "services": ["grundpflege", "behandlungspflege", "palliative"],
        "zusatzbeitrag": 2.90
      }
    }
  ]
}
```

---

## 4. Errors & Auth

- **Validation:** malformed coordinates or parameters → `400`.

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
| `not_implemented` | `501` | Endpoint is in this spec but not live yet. |
| `timeout` | `504` | Server-side query timeout. Retryable. |
| `internal` | `500` | Unexpected failure. The cause is in the server log, never in the response. |

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

Full response schemas are in [`openapi.yaml`](openapi.yaml).
