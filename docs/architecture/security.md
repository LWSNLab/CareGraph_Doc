# 🔒 Security, Compliance & Privacy Concept

> **Standard:** GDPR (DSGVO) Compliant by Design
> **Security Architecture:** Zero-Trust Internal Networking, Least Privilege DB Roles, Hashed Key Auth

---

## 1. Privacy & GDPR Compliance

Location queries often expose private user data (e.g., an exact home coordinate). CareGraph enforces strict data minimization principles:

* **Zero Coordinate Logging:** The Go API Gateway **never logs exact latitude and longitude queries** in plaintext access logs. Logs only record rounded coordinates or municipal IDs (e.g., postal-code level).
* **IP Anonymization:** Inbound client IP addresses are truncated/anonymized before being passed to internal logger middleware.
* **Public-Domain Data Focus:** CareGraph only processes official, publicly listed institution data (per § 7 SGB XI). No private health records or patient details are handled.

> The legal basis of the *ingested* data (source terms, database rights, republishing) is a separate concern — see [Data Sources & Licensing](../legal/data-licensing.md). This document covers the platform's runtime security.

---

## 2. API & Gateway Security

* **B2B API Key Authentication**
    * API keys are passed via HTTP header (`X-API-Key`).
    * Keys are stored in PostgreSQL as **Argon2id (or bcrypt) hashes** — never in plaintext.
* **Rate Limiting**
    * Redis-backed token-bucket algorithm prevents scraping abuse and denial-of-service (DoS).
    * Default tiers: Community (100 req/min/IP), B2B Enterprise (custom SLAs).
* **Transport Security**
    * Strict HTTPS enforcement via TLS 1.3.
    * Essential security headers: `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `Strict-Transport-Security`.

---

## 3. Database & Network Isolation

* **Least-Privilege Access Control**
    * **Python Ingestion Worker:** dedicated write-scoped DB role (`INSERT`/`UPDATE` only). It cannot serve public read queries.
    * **Go API Gateway:** `READ-ONLY` DB role. Even if the gateway were compromised, records cannot be dropped or corrupted.
    * **Caveat, `docker compose` only:** the compose stack connects both services
      as the database **owner**, not as these roles. `db/migrations` creates
      `caregraph_api` and `caregraph_ingest` without passwords, and
      `make db-roles-dev` assigns throwaway ones against a *running* container —
      which compose cannot depend on. The host-run path (`.env.example`) does use
      the least-privilege roles. A real deployment must set these passwords from a
      secret manager and point `DATABASE_URL` at `caregraph_api`.

* **Encrypted transport to the database**
    * The API and the pipelines **refuse to connect** with `sslmode=disable` to any
      host that is not loopback, `::1` or a Unix socket. An *unset* `sslmode` is
      refused as well: libpq treats it as `prefer`, which attempts TLS and then
      falls back to plaintext **silently**, so a connection encrypted in staging
      may not be in production. Only `require`, `verify-ca` and `verify-full` pass
      — an allowlist, so an unrecognised or absent value fails closed.
    * A Docker service name counts as remote: from inside a container there is no
      way to distinguish a private bridge network from the open internet. So
      `docker-compose.yml` sets `CAREGRAPH_ALLOW_INSECURE_DB=1` to say "one host,
      and the operator knows it". **A deployment spanning machines must not set it.**
    * Enforced in `internal/infrastructure/dsn.go` and `pipelines/common/dsn.py`.
      The Go side asks pgx what the DSN resolves to rather than matching on the
      sslmode string — which is what catches `prefer`'s plaintext fallback, and a
      multi-host DSN that is secure for the first host only.

* **Internal Docker Network**
    * PostgreSQL, Typesense, and Redis run inside an isolated internal Docker network without public port exposure.
    * Only the Go API Gateway (port 443) is exposed to the outside world.

```text
  [ PUBLIC INTERNET ]
          │
          ▼ (Port 443 / HTTPS)
┌─────────────────────────────────────────┐
│             Go API Gateway              │
└────────────────────┬────────────────────┘
                     │ (Internal Docker Network)
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
┌─────────────┐┌───────────┐┌──────────────┐
│ PostgreSQL  ││ Typesense ││    Redis     │
│  (PostGIS)  ││   (C++)   ││(Rate Limit)  │
└─────────────┘└───────────┘└──────────────┘
```

---

## 4. Managed-Platform Note (Supabase / PostgREST)

In the early phases CareGraph runs on **managed PostgreSQL (Supabase)** before the dedicated Go gateway exists. The same principles hold via platform primitives:

* **Row-Level Security (RLS)** is enabled on every table in the `public` schema, with an explicit read-only policy for the `anon` and `authenticated` roles — public reference data is world-readable, writes go only through `service_role`.
* Writes run exclusively through the ingestion pipeline (SQL editor / `service_role`), never through a public API key.

This keeps the posture consistent while the stack migrates from managed Postgres to the self-hosted, isolated deployment above.

---

## 5. Responsible Disclosure

Security issues are handled via coordinated disclosure (`SECURITY.md`, private vulnerability reporting). Automated dependency and container scanning (Dependabot, Trivy) run in CI. See [Open Source Strategy](../pm/open-source-strategy.md) for the full governance process.
