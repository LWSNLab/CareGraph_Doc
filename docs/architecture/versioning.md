# 🔢 Versioning

One version, set by hand, in `VERSION`. Two files decide a release; everything
else that carries a number already describes itself.

## Cutting a release

```bash
make set-version VERSION=0.2.0     # VERSION, pyproject.toml, openapi.yaml
$EDITOR CHANGELOG.md               # a `## [0.2.0]` section
```

Merge into `main`. The workflow publishes the images and creates the release,
which creates the tag `v0.2.0` with it, using your changelog section as the text.

A merge that leaves `VERSION` alone releases nothing — the tag already exists, so
an ordinary fix does not cut a release.

## Where the number lives

`VERSION` is the source. It is copied into two artefacts that ship with a
release, and a test fails the build if any of the three disagree:

| Copy | Why |
| :-- | :-- |
| `pipelines/pyproject.toml` | the ingestion image ships as part of the release and is tagged with it |
| `api/openapi.yaml` → `info.version` | so the served contract names the build behind it |

## What is *not* versioned separately, and why

**The API contract.** Its breaking version is the `/v1` in every path — that is
what a client pins to, and a breaking change arrives as `/v2`. A second semver
beside it would duplicate the major and describe additive changes that clients
are told to ignore anyway. `info.version` therefore just names the build.

This was briefly built the other way, with a contract version of its own and a
script policing the size of each release bump. It was removed: nobody outside
could act on the number, and the check compared one declaration against another
rather than against reality, so forgetting to bump it passed silently.

**The database schema** is the highest file in `db/migrations/` — monotonic, and
it names the change.

**The dataset** records `generated_at` and `schema_migration` in its manifest.
Two facts, because a snapshot is identified by when it was cut *and* which schema
it fits. An import refuses an archive whose schema does not match.

Neither needed a semver bolted on.

## What is enforced

Failing the build, on every pull request:

- the three copies of the version disagreeing;
- a version without a changelog entry, or with an empty one;
- `VERSION` not being `MAJOR.MINOR.PATCH`.

Not enforced, and known: the domain name appears in four prose files, the
human-readable API page is written beside the contract rather than generated from
it, and story documents are mirrored into GitHub issues by hand. These are prose,
and a test for them would cost more than the mistakes it would catch.

## References

- [API Specification](../api/openapi-spec.md) · [Data Schema](data-schema.md)
