---
name: ingest-library
description: Add or refresh a project-local wiki page at docs/graph/libraries/<name>.md for an external dependency (library, framework, SDK, API, protocol, spec, model provider) through a phased pass — corpus check, then research-scout retrieves and drafts, tester smoke-tests the pin, the librarian finalizes and registers at close-out. Use BEFORE any code touches a new dependency, whenever a wiki page is missing for code that already uses one, whenever a version pin changes, and whenever an upstream security advisory affects a wikified library. The wiki is the project's source of truth; agent memory of library APIs is unreliable across versions, so always ingest first.
id: protocol.ingest-library
tier: 2
kind: protocol
origin: seed
title: ingest-library — building the version-pinned wiki page before any code touches a dependency
owns:
  - ingest-library.flow
  - ingest-library.refresh
  - ingest-library.corpus-first
requires:
peers:
  - protocol.harvest
  - skill.library-wiki
  - skill.research-and-ingest
artifacts:
  - templates/library-page.template.md
  - templates/knowledge-graph/graph-lint.py
load_when:
  - "adding a new dependency, library, SDK, or API"
  - "no wiki page for a library the code uses"
  - "version pin changed, refresh the library page"
  - "security advisory on a dependency"
est_tokens: 1500
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

## The pass (`ingest-library.flow`)

The pass is a sequence of phases with a named owner each. **The table is
the spawn order**: a phase's spawn is issued only after the handback it
needs has returned (`delegation.sequencing`,
`docs/graph/method/delegation.md`). Two callers hold it: the
orchestrator inside grill phase 3 (one scout spawn per dependency
without a page), and the `docs-librarian` during a close-out or a docs
audit (its one `delegates_to` entry). In both, the scout drafts and the
librarian finalizes — a sonnet-class worker's writes are mechanical
normalization, and the opus-class librarian owns the page
(`delegation.model-classes`).

| Phase | Does | Owner | Needs | Parallel with |
|---|---|---|---|---|
| 0 | Identify: canonical name, exact version (never "latest"), ecosystem, why this project needs it | the caller, in-session | the lockfile or the architect's brief | — |
| 1 | Corpus check (`ingest-library.corpus-first`, below) | the caller, in-session | phase 0 | — |
| 2 | Retrieve, snapshot, normalize, register sources; inspect the code; **draft** `docs/graph/libraries/<name>.md` §0–§3 and §10 from the template | `research-scout` (`skill.research-and-ingest` for the sources, `skill.library-wiki` for the page) | phases 0–1 | other dependencies' phase 2 |
| 3 | Smoke test: import at the pin, call one or two names from §3, run in the project's harness | `tester` | phase 2 (the page's §2 install and §3 names) | — |
| 4 | grill.md §5 row (and §6 where the choice was a decision) | the session | phase 3 | — |
| 5 | Finalize the page; the `libraries/index.md` and `sources/index.md` rows; graph-lint | `docs-librarian`, in the close-out spawn (`protocol.canonize`) | phases 2–3 | — |

What the table cannot hold:

- **Phase 2 fetches**: the version's release notes, the quickstart, the
  public API reference, the security policy and recent advisories, the
  license — and for LLM/VLM SDKs, pricing-relevant behavior, rate
  limits, structured-output features, safety policies. Raw snapshots
  go to `docs/graph/sources/raw/` (license permitting), normalized
  Markdown to `docs/graph/sources/normalized/`. Where the source is
  public code, the scout scans the exported surface, `examples/`, and
  the maintenance signal (commit recency, open-issue volume) and notes
  discrepancies between docs and code on the page. Advisories the scout
  found land in the page's §7; `security` weighs them at grill §11, it
  is not a separate spawn here.
- **The draft page is brutally specific.** §0–§3 and §10 on creation;
  §4–§12 demand-grown as the project meets each idiom, pitfall,
  deprecation, or upgrade — never a fabricated "none" row. The API
  surface covers only the slice this project uses. A private dependency
  records that resolution needs registry credentials in the build/CI
  environment.
- **A failed smoke test means the page is wrong** (or the install is):
  it returns to phase 2 as an attempt under `protocol.recover`'s
  three-attempt boundary. The page is not authoritative until the test
  passes.
- **The librarian's finalization** dedupes against what the graph
  already owns, adds the index rows (`| Library | Version | Page | Used
  by | Maintenance | License | Last reviewed |`, and the sources index),
  and runs `graph-lint.py`, whose library check reads the page's §0 pin
  and the index row. One spawn for every page this task drafted.

## Corpus first (`ingest-library.corpus-first`)

Once the library's exact name, version, and ecosystem are known, and
**when you are working in the seed repo or the plant has harvested the
library corpus** (otherwise phase 1 is a no-op), check the
library-documentation corpus before re-downloading — the pages
`harvest` folded back from earlier plants
(`library-corpus/<ecosystem>/<library>.md`, keyed by library and **not
by version**; the corpus keeps the version-durable orientation layer,
`docs/graph/protocols/harvest.md`). If the page exists, seed
`docs/graph/libraries/<name>.md` from it, then pin and validate the
version-specific layer (API deltas, deprecations, CVEs) against this
project's actual lockfile version from upstream — the corpus never
substitutes for the pin check. If it is absent, ingest from upstream as
usual; the fresh page's version-durable surface becomes a harvest
candidate for the next plant. Reuse the corpus, re-download only the
version-specific delta.

## Refresh (`ingest-library.refresh`)

The same pass over an existing page, entered when the pin no longer
matches the lockfile, upstream released a major, an advisory landed, or
the page's "Last reviewed" is past the project's cadence. Phase 2 diffs
the upstream CHANGELOG between the old and new pin and records in §8
the behavior changes that affect this project, updates §0 (pin, date),
§3 for any used name that changed, §4 if a recommended pattern
changed, §6 for the new pin's deprecations, §7 from the advisory feed;
phase 3 re-runs the smoke test at the new pin; phase 5 updates the
index row. Between full passes, the cheap reconciliation of resolved
versions against recorded pins is
`skill.research-and-ingest`'s drift check — it decides *whether* a
refresh is due, it does not perform one.

## Exit conditions

- `docs/graph/libraries/<name>.md` exists with its §0 pin table filled
  (exact version, not a placeholder), `Last reviewed` dated, §10
  citing the sources used; §1–§3 populated, §4–§12 present and
  demand-grown.
- `docs/graph/sources/` holds the raw (where allowed) and normalized
  copies, with their `sources/index.md` rows.
- A smoke test verified the pinned version of the library works, run
  by `tester` and recorded in its handback.
- grill.md §5 names the page (grill-lint checks it against §9).
- `docs/graph/libraries/index.md` has the row, written in the close-out;
  `python3 docs/graph/graph-lint.py` exits 0.

## When *not* to use this protocol

- A trivial transitive dependency that the codebase doesn't directly
  use. (You don't wikify every package in `node_modules`.) Wikify
  what you import; the rest is implicit.
- A platform feature that's part of the runtime itself
  (`stdlib`, browser built-ins). Cover those in
  `docs/graph/best-practices/engineering.md` instead.
