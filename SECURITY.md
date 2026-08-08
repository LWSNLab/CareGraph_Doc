# Security Policy

This repository contains **documentation only** — no application code.

## Reporting a Vulnerability

Report security issues for the CareGraph platform against the implementation
repository, so that everything stays in one place:

**➡️ [Report a vulnerability](https://github.com/LWSNLab/CareGraph/security/advisories/new)**

The full policy — scope, response targets, and the privacy considerations that
apply to health and care data — lives in
[CareGraph/SECURITY.md](https://github.com/LWSNLab/CareGraph/blob/main/SECURITY.md).

**Please do not open a public issue for security problems.**

## What Counts Here

Documentation can carry real security weight, so these are valid reports
against *this* repository:

- Guidance in the docs that would lead an implementer into an insecure setup
  (for example a wrong row-level-security example, or an auth flow described
  incorrectly).
- Leaked credentials, tokens or internal endpoints in documentation or history.
- A compromised dependency in the docs build (`requirements.txt`) or in the
  GitHub Actions workflows.
