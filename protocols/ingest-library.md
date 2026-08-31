---
name: ingest-library
description: Add or refresh a project-local wiki page at docs/graph/libraries/<name>.md for an external dependency (library, framework, SDK, API, protocol, spec, model provider). Use BEFORE any code touches a new dependency, whenever a wiki page is missing for code that already uses one, whenever a version pin changes, and whenever an upstream security advisory affects a wikified library. The wiki is the project's source of truth; agent memory of library APIs is unreliable across versions, so always ingest first.
id: protocol.ingest-library
tier: 2
kind: protocol
origin: seed
title: ingest-library — building the version-pinned wiki page before any code touches a dependency
owns:
  - ingest-library.flow
  - ingest-library.corpus-first
requires:
peers:
  - protocol.harvest
  - skill.library-wiki
  - skill.research-and-ingest
artifacts:
  - templates/library-page.template.md
load_when:
  - "adding a new dependency, library, SDK, or API"
  - "no wiki page for a library the code uses"
  - "version pin changed, refresh the library page"
  - "security advisory on a dependency"
est_tokens: 1200
command: true
---

# Protocol: ingest-library

Use this whenever a new external dependency (library, framework, SDK,
API, protocol, spec, model provider, or significant tool) is being
introduced, OR whenever a wiki page for an existing dependency is
stale and needs to be refreshed.

This is the core wiki-building flow. The deliverable is a complete,
version-pinned page in `docs/graph/libraries/<name>.md`, registered in
`docs/graph/libraries/index.md`, with raw and normalized sources on disk.

## Entry conditions

One of:
- `architect` or `implementer` wants to use a dependency that has no
  page in `docs/graph/libraries/`.
- The version pin on an existing page no longer matches what the
  project uses.
- A behavior was encountered that the page does not cover (and that
  cost an agent debugging time).
- A security advisory affects a wikified library.

## Cast

- `research-scout` — does the retrieval and normalization.
- `docs-librarian` — finalizes the wiki page and updates indexes.
- `architect` (lightly) — confirms the dependency fits the architecture
  before the wiki page is committed as authoritative.

## Workflow

### 0. Withdraw from the seed corpus before re-downloading

Once you know the library's exact name, version, and ecosystem (Identify,
below), check the seed's library-documentation corpus **first** — the pages
`harvest` folded back from earlier plants
(`library-corpus/<ecosystem>/<library>.md`, keyed by library and **not by
version** — the corpus keeps the version-durable orientation layer; see
`docs/graph/protocols/harvest.md`). If the page exists, seed
`docs/graph/libraries/<name>.md` from it, then pin and validate the
version-specific layer (API deltas, deprecations, CVEs) against this
project's actual lockfile version from upstream — the corpus never
substitutes for the pin check. If the corpus page is absent, ingest from
upstream as usual; the fresh page's version-durable surface becomes a
harvest candidate for the next plant. Reuse the corpus, re-download only
the version-specific delta.

### 1. Identify

Name the library precisely:
- Canonical name.
- Version (the exact version the project will pin to; not "latest").
- Ecosystem (npm package, PyPI package, Go module, Maven artifact,
  OS package, container image, IETF RFC, etc.).
- Why this project needs it (one sentence; goes in section 2 of the
  wiki page).

### 2. Retrieve

`research-scout` fetches:
- The version's release notes / CHANGELOG entry.
- The official getting-started or quickstart page.
- The public API reference (or the canonical entry-point docs).
- The security policy page or recent advisories.
- The license file.
- For LLM/VLM libraries and SDKs: pricing-relevant behavior,
  rate-limit page, structured-output features, safety policies.

Snapshot the raw content to `docs/graph/sources/raw/` (when license
permits) and produce normalized clean Markdown in
`docs/graph/sources/normalized/`.

### 3. Inspect (read the code, not just the docs)

For libraries with public source code, briefly scan:
- The public API surface (exported names, top-level functions, key
  classes).
- The `examples/` directory or equivalent.
- The maintenance signal: recent commit dates, open-issue volume,
  the kind of issues that stay open.

This catches discrepancies between docs and code. Note any.

### 4. Compose the wiki page

Use `docs/graph/templates/library-page.template.md` to produce
`docs/graph/libraries/<name>.md` — the template owns the section list;
fill every section. Two constraints the template cannot enforce:

- The API-surface section covers only the slice this project actually
  uses — start small; it grows as the codebase grows.
- For a private dependency, record that resolution needs registry
  credentials in the build/CI environment (a fresh checkout without
  them looks like a broken build, not a missing secret).

The page is brutally specific to this project. The whole upstream
documentation does not go on the page; only the parts the project
uses or needs to be careful about.

### 5. Register

`docs-librarian` adds the page to `docs/graph/libraries/index.md` with:

| Library | Version | Page | Used by | Maintenance | License | Last reviewed |

And updates `docs/graph/sources/index.md` with the raw and normalized
sources just ingested.

### 6. Validate

Before the page is "authoritative":
- One of: `architect`, `implementer`, or `tester` writes a tiny
  smoke test that imports/uses the library at the version pinned,
  to confirm the snippet on the wiki page actually works.
- `security` skims for advisories that affect the pin and adds the
  watch.

If the smoke test fails, the wiki page is wrong — fix it before
calling the protocol done.

### 7. Notify grill.md

Add the wikified library to grill.md section 5 (Research Summary)
and section 6 (Decisions Made) as appropriate.

## Refresh (vs new ingest)

When refreshing an existing page:
- Update the version pin and the "Last reviewed" date.
- Diff the upstream CHANGELOG between the old and new version; record
  the behavior changes that affect this project.
- Update the API surface section if any used name changed.
- Update idioms if a recommended pattern changed.
- Update pitfalls if any were fixed upstream.
- Run the smoke test again at the new version.

## Exit conditions

- `docs/graph/libraries/<name>.md` exists, populated, dated, sourced.
- `docs/graph/libraries/index.md` has the row.
- `docs/graph/sources/index.md` has the source entries.
- A smoke test verified the pinned version of the library works.
- grill.md is updated.

## When *not* to use this protocol

- A trivial transitive dependency that the codebase doesn't directly
  use. (You don't wikify every package in `node_modules`.) Wikify
  what you import; the rest is implicit.
- A platform feature that's part of the runtime itself
  (`stdlib`, browser built-ins). Cover those in
  `docs/graph/best-practices/engineering.md` instead.
