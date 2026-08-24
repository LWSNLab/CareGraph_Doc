# Contributing to the CareGraph documentation

This repository is the documentation for
[CareGraph](https://github.com/LWSNLab/CareGraph) — architecture, the data model,
the legal groundwork and the story-level roadmap. It builds with MkDocs Material
and publishes to GitHub Pages.

Code changes belong in the [main repository](https://github.com/LWSNLab/CareGraph);
its [CONTRIBUTING.md](https://github.com/LWSNLab/CareGraph/blob/main/CONTRIBUTING.md)
covers those.

**Security problems do not belong in an issue.** See [SECURITY.md](./SECURITY.md).

## Building locally

```bash
pip install -r requirements.txt
mkdocs serve
```

Then open http://127.0.0.1:8000. Before opening a pull request, build the way CI
does — `--strict` turns a broken link or a page missing from the nav into a
failure:

```bash
mkdocs build --strict
```

A new page needs an entry in `nav:` in `mkdocs.yml`. Without one the strict build
fails, which is the intent: a page nobody can navigate to is a page nobody reads.

## Layout

| | |
| :-- | :-- |
| `docs/architecture/` | how the system works, and why it was built that way |
| `docs/api/` | the human-readable API documentation |
| `docs/legal/` | data sources, licensing, GDPR groundwork |
| `docs/pm/stories/` | epics and stories — the roadmap at working detail |
| `internal/` | **gitignored.** Negotiating drafts, contact details, working notes |

Nothing under `internal/` is tracked, and nothing from it may be moved into
`docs/` without reading it first. It exists because some material is useful to
the project and not fit to publish.

## What documentation here is for

The pages explain reasoning, not just behaviour. A decision that was made one way
rather than another says which way was rejected and what it cost — including the
ones that turned out wrong, which are the ones worth reading.

Two consequences for a pull request:

- **Stories record what was actually built**, including defects found on the way.
  A story that reads as if everything went smoothly is less useful than one that
  names what broke.
- **Documents age against the code.** If you change a page, check it still
  describes what the code does. The legal and architecture pages are the ones
  most likely to have drifted.

## Stories and issues

Stories are written here and mirrored into GitHub issues by hand
(`scripts/import_stories.py`). The document is the source; the issue is a copy.
Edit the document.

## Commits and branches

Pull requests go against `main`, which publishes on merge. Commit subjects follow
[Conventional Commits](https://www.conventionalcommits.org/):

```
docs(architecture): explain the trusted-proxy setting
docs(legal): correct the source table against what is ingested
```

## Licensing of contributions

This repository is **CC BY-SA 4.0**. By opening a pull request you agree that
your contribution is licensed the same way — attribution required, and
derivatives share alike.

The code repository is AGPLv3. There is no CLA in either.

## Code of Conduct

Participation is governed by the [Code of Conduct](./CODE_OF_CONDUCT.md).
