# E6-S3 — Self-service API keys

|                  |                              |
| :--------------- | :--------------------------- |
| **Epic**         | E6 — Commercial / DaaS       |
| **Type**         | Idea                         |
| **Story Points** | 5                            |
| **Priority**     | Low                          |
| **Status**       | 💡 Idea — not scheduled      |

> ← [Epic 6](index.md) · [Backlog](../index.md)

## User Story

As a **developer who found CareGraph**, I want to get a key without waiting for a
person, so that I can try the API the same evening.

## Description

Recorded as an idea on 2026-09-24, deliberately not scheduled. It reverses a
decision [E5-S1](../epic-5-open-source/e5-s1-repo-licensing.md) took on purpose,
so it is written down with the reasons against it rather than only the reason for
it — the point of this page is that a later evaluation starts from what was
already known.

The prompt was "let people generate a key from the documentation site". Worth
saying early: **the documentation site cannot do it.** It is GitHub Pages, so
static. A form there would post to a new public endpoint on the API, which puts
the work in the gateway and in abuse handling, not in the docs.

## The decision this revisits

E5-S1 issues keys by hand, for three stated reasons. They have aged differently:

| Reason given | How it stands |
| :-- | :-- |
| *"Ten people you can talk to are worth more than a thousand anonymous keys"* | **Still holds.** There is no demand yet — and no running instance to hold demand. |
| *"Self-service means storing email addresses — so a privacy notice"* | **Weakened.** A privacy notice is owed the moment a hosted endpoint is announced, whether or not there is a signup form. This enlarges the obligation rather than creating it. |
| *Abuse handling* | **The real obstacle.** See below. |

## Why abuse is the hard part, not the form

Rate limiting assumes keys are scarce. Per-tier quotas and the separate
failed-authentication budget are both keyed on identity, and an identity anyone
can mint on demand is not one: a caller who exhausts a quota simply takes another
key.

So the question to answer before building anything is not how the form looks. It
is **what makes a key cost something**:

- an email that must be confirmed, which costs an inbox;
- a limit on issuance per address and per IP, which costs time;
- a domain check for anything above the free tier, which costs a domain;
- manual approval above the free tier, which costs a conversation.

Each is a trade against the reason for doing this at all, which is that nobody
should have to wait for a person.

## What would have to be true first

- [ ] The hosted service exists and is announced — with an Impressum and a
      privacy notice, which the runbook already names as the obligations that
      attach to announcing a URL.
- [ ] Manual issuance has become a chore. E5-S1 names the threshold: *more than
      one or two requests a week*. The count today is zero.
- [ ] The tiers in [E6-S1](e6-s1-tiered-access.md) are decided, because
      self-service and tiering are the same question: who may mint a key, and
      what separates a free one from a paid one.

## Acceptance Criteria

*Not written yet — an idea does not get criteria. Sketching them before the three
conditions above are met would make this look schedulable, which is exactly the
mistake this page exists to prevent.*

## Dependencies

- **Depends on:** [E6-S1](e6-s1-tiered-access.md) — tiers first, or self-service
  issues keys whose meaning is undecided
- **Related:** the documented request path in
  [E5-S1](../epic-5-open-source/e5-s1-repo-licensing.md), which is what serves
  this need today

## Risks

- **It looks like a small frontend task.** It is a public write endpoint,
  personal data, and a hole in the rate limiter. The form is the cheapest part.
- **Free keys at scale change the hosting bill**, which is E6's subject and not a
  detail to discover afterwards.

## References

- [Open Source Strategy](../../open-source-strategy.md) · [Security & Privacy](../../../architecture/security.md)
