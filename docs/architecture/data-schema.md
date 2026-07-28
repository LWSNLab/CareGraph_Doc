### 3. `docs/architecture/security.md`

```markdown
# 🔒 Security, Compliance & Privacy Concept

> **Standard:** GDPR (DSGVO) Compliant by Design
> **Security Architecture:** Zero-Trust Internal Networking, Least Privilege DB Roles, Hashed Key Auth

---

## 1. Privacy & GDPR Compliance

Location queries often expose private user data (e.g., an exact home coordinate). CareGraph enforces strict data minimization principles:

* **Zero Coordinate Logging:** The Go API Gateway **never logs exact latitude and longitude queries** in plaintext access logs. Logs only record rounded coordinates or municipal IDs (e.g., Postal Code level).
* **IP Anonymization:** Inbound client IP addresses are truncated/anonymized before passing to internal logger middleware.
* **Public Domain Data Focus:** CareGraph only processes official, publicly listed institution data (according to § 7 SGB XI). No private health records or patient details are handled.

---

## 2. API & Gateway Security

* **B2B API Key Authentication:**
  * API Keys are passed via HTTP Header (`X-API-Key`).
  * API Keys are stored in PostgreSQL as **Argon2id or bcrypt hashes**—never in plaintext.
* **Rate Limiting:**
  * Redis-backed Token Bucket algorithm prevents scraping abuse and Denial of Service (DoS) attacks.
  * Default tiers: Free Tiers (100 req/min/IP), B2B Enterprise Tiers (Custom SLAs).
* **Transport Security:**
  * Strict HTTPS enforcement via TLS 1.3.
  * Essential Security Headers: `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `Strict-Transport-Security`.

---

## 3. Database & Network Isolation

* **Least Privilege Access Control:**
  * **Python Ingestion Worker:** Granted a dedicated `WRITE-ONLY` DB role (`INSERT/UPDATE`). It cannot serve public read queries.
  * **Go API Gateway:** Granted a `READ-ONLY` DB role. Even if the web gateway were compromised, database records cannot be dropped or corrupted.
* **Internal Docker Network:**
  * PostgreSQL, Typesense, and Redis instances run inside an isolated internal Docker network without public port exposure.
  * Only the Go API Gateway (Port 443) is exposed to the outside world.

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
´´´