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
| `GET` | `/healthz` | Liveness & readiness probe | ❌ |

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

> ¹ **Only insurers are addressable today.** Every Leistungserbringer has an IK,
> but no public source publishes those of care providers, so their `ik_nummer`
> is `null`. Reach them via `/infrastructure/near` or `/infrastructure/search`.
> Tracked in the backlog as *Provider IK numbers*.

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

- **Authentication:** send the B2B key in the `X-API-Key` header. Missing/invalid → `401`.
- **Validation:** malformed coordinates or parameters → `400`.
- **Rate limiting:** exceeding your tier → `429` (see [Security](../architecture/security.md#2-api-gateway-security)).

Error bodies follow `{ "error": "<message>" }`. Full response schemas are in [`openapi.yaml`](openapi.yaml).
