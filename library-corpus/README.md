# Library corpus

**Project-agnostic, version-durable** surface notes for third-party libraries,
languages, and runtimes — folded back into the seed by the **harvest** protocol
(`protocols/harvest.md`, `HARVEST_PROMPT.md`).

## Purpose

Ingesting a dependency is expensive, but most of that cost is paid rediscovering
the same **surface** every time: what the library is for, its core API, how it
is idiomatically used. That surface barely moves between versions. Harvest folds
it into this corpus so the next project starts from an orientation instead of a
blank page — then ingests the version-specific delta fresh.

The next plant's `ingest-library` **checks this corpus first**: if a surface
page exists, it seeds the project's `docs/graph/libraries/<name>.md` from it as
the orientation layer, then fetches only the pinned facts it actually needs
(exact version, its advisories, its deprecations) against the project's real
lockfile.

## What belongs here (surface, durable)

- The capability the library provides; its ecosystem and canonical package name.
- Its core API shape and canonical usage — general, not project call-sites.
- Idioms and best practices that hold **across releases**.
- Conceptual pitfalls inherent to the tool.
- The upstream doc/repo home.

## What stays OUT (pinned, ephemeral)

These are the *project's* concern, rediscovered per project by `ingest-library`,
and wrong the moment the pin moves — they must never enter the corpus:

- CVEs / advisories tied to an exact version.
- "Version X.Y.Z is a breaking-change marker" notes.
- Deprecations introduced in a specific release.
- Upgrade / migration diffs between two pins.
- A resolved version number itself.

## Layout

```
library-corpus/<ecosystem>/<library>.md
```

- Keyed by **library, not version** — one page per library.
- `<ecosystem>` — one of `language`, `npm`, `nuget`, `pypi`, `maven`,
  `container` (add more as harvested: `cargo`, `go`, `gem`, …). `container`
  holds container-runtime tooling (engine, compose, and images serving as a
  runtime stage) rather than an installable package registry.
- `<library>` — the canonical id, lowercased, scope slash removed
  (`@microsoft/signalr` → `microsoft-signalr`).

## Rules

- **Agnostic or it does not belong here.** No project name, domain noun, path,
  credential, or dataset shape.
- **Durable or it does not belong here.** No version-pinned specific. If a fact
  reads like a security bulletin for one release, it fails — a page should read
  like the opening orientation of the library's own docs.
- **Orientation, not gospel.** A surface page ages slowly but an API redesign
  across a major line can outdate it. Confirm against upstream; never read a
  pinned fact from here (there are none to read).
- **Hosted-platform DSLs may earn a page without a package.** A hosted
  platform's declarative pipeline/config DSL (e.g. a CI platform's YAML schema,
  a deploy platform's manifest format) has no installable package and no
  version number, yet its surface — the schema shape, its idioms, its
  conceptual pitfalls — is just as reusable. Such a surface may get a
  library-wiki page under a platform ecosystem bucket, pinned by
  **retrieval-date** (when the surface was last confirmed against upstream)
  instead of a version number, since there is no version to pin.
