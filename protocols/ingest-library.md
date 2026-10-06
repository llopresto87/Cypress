---
name: ingest-library
description: Add or refresh a project-local wiki page at docs/graph/libraries/<name>.md for an external dependency (library, framework, SDK, API, protocol, spec, model provider) through a phased pass — corpus check (a page the installer placed from the seed's corpus skips the scout and pins only the version delta), then research-scout retrieves and drafts, tester smoke-tests the pin, the librarian finalizes and registers at close-out. Use before any code touches a new dependency, whenever a wiki page is missing for code that already uses one, whenever a version pin changes, and whenever an upstream security advisory affects a wikified library. The wiki is the project's source of truth; agent memory of library APIs is unreliable across versions, so always ingest first.
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
prevents: Code written against a dependency from model memory — an unpinned version, an idiom that was correct two majors ago, and a pitfall rediscovered as a bug.
est_tokens: 2428
command: true
---

# Protocol: ingest-library

Use this whenever a new external dependency (library, framework, SDK,
API, protocol, spec, model provider, or significant tool) is being
introduced, or whenever a wiki page for an existing dependency is
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
the spawn order** (`delegation.sequencing`,
`docs/graph/method/delegation-sequencing.md`). Two callers hold it: the
orchestrator inside grill phase 3 (one scout spawn per dependency
without a page), and the `docs-librarian` during a close-out or a docs
audit (its one `delegates_to` entry). In both, the scout drafts and the
librarian finalizes: an investigation-class worker's writes are mechanical
normalization, and the authoring-class librarian owns the page
(`delegation.model-classes`).

| Phase | Does | Owner | Needs | Parallel with |
|---|---|---|---|---|
| 0 | Identify: canonical name, exact version (never "latest"), ecosystem (`cli` for a tool the host or a base image supplies, whose pin is the version on the machine that runs it), why this project needs it | the caller, in-session | the lockfile or the architect's brief | — |
| 1 | Corpus check (`ingest-library.corpus-first`, below) | the caller, in-session | phase 0 | — |
| 2 | Retrieve, snapshot, normalize, register sources; inspect the code; **draft** `docs/graph/libraries/<name>.md` §0–§3 and §10 from the template. Not spawned for a page phase 1 found placed: that page gets the version delta instead (below) | `research-scout` (`skill.research-and-ingest` for the sources, `skill.library-wiki` for the page) | phases 0–1 | other dependencies' phase 2 |
| 3 | Smoke test: import at the pin, call one or two names from §3, run in the project's harness | `tester` | phase 2 (the page's §2 install and §3 names) | — |
| 4 | grill.md §5 row (and §6 where the choice was a decision) | the session | phase 3 | — |
| 5 | Finalize the page; the `libraries/index.md` and `sources/index.md` rows; graph-lint | `docs-librarian`, in the close-out spawn (`protocol.canonize`) | phases 2–3 | — |

What the table cannot hold:

- **Phase 2 fetches**: the version's release notes, the quickstart, the
  public API reference, the security policy and recent advisories, the
  license, and for LLM/VLM SDKs, pricing-relevant behavior, rate
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
  deprecation, or upgrade, never a fabricated "none" row. The API
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

Phase 1 runs before any scout is spawned. Once the library's exact name,
version and ecosystem are known, look for the library-documentation corpus's
page for it in two places, in this order, and stop at the first hit. The
corpus keeps the version-durable orientation layer that `harvest` folded back
from earlier plants, keyed by library and **not by version**
(`docs/graph/protocols/harvest.md`), so a page found here replaces the
scout's surface retrieval and never the pin check.

1. **A placed page.** `docs/graph/libraries/<name>.md` exists and its first
   line is the installer's provenance line,
   `<!-- origin: corpus@<seed version> id: library-corpus/<ecosystem>/<name> -->`.
   The installer wrote it from the seed's corpus when the owner listed that id
   (`install.sh <host> --expertise <id>`, which `grow` proposes and graft
   refreshes), and `.cypress/seed.json` records it under `expertise`. Read the
   id on that line before trusting the page: its ecosystem must be the one
   phase 0 identified, because two ecosystems can carry one name (a `pypi`
   client and a `container` image), and a page placed for the other one is a
   different dependency. A page with no provenance line is the plant's own,
   and a page that already carries a filled §0 pin is an existing page: the
   refresh below applies to both.
2. **The seed's corpus, on disk.** When the session can read a seed checkout
   (the seed repo itself, or a plant whose session has the seed beside it),
   look for `<seed>/library-corpus/<ecosystem>/<name>.md`. A page found there
   is best placed through the installer, on the owner's word, so the stamp
   records it and every later install refreshes it while the plant leaves it
   untouched. A page copied by hand is the plant's own from the first byte,
   and the installer never replaces it (SPEC-0001
   PLANT_OWNED_PAGE_IS_NEVER_REPLACED).

**A placed page skips the scout.** Phase 2 is not spawned for it: its surface
is already on disk, and retrieving it again is the cost the corpus exists to
save. The caller pins only the version-specific delta against this project's
lockfile: the exact version, its release notes for the behavior this project
uses, its deprecations and its advisories, each retrieved from upstream and
registered under `docs/graph/sources/` as any retrieved source is
(`skill.research-and-ingest`). The delta lands on the placed page: the §0 pin
table of `templates/library-page.template.md` under the provenance line, which
stays the first line, and the template's §6 and §7 for that version. A caller
that only orchestrates (grow's orchestration chat) does not pin in its own
context: it batches the deltas of every placed page into one bounded
`research-scout` brief scoped to pins, deprecations and advisories, in place
of one surface scout per library. Phases 3 to 5 then run as for any page; the
smoke test still proves the pin.

Writing the delta is an edit, and the installer reads it as one. The page's
bytes no longer match the hash the stamp recorded, so a later install leaves
the page as it is and names it for graft Phase 4, which merges the corpus's
newer layer into it and keeps the pin (SPEC-0001
PLANT_EDITED_PAGE_IS_LEFT_AND_NAMED). That is the intended path: from the
first pin on, the page is the plant's, refreshed by merge and never replaced.

A placed page that falls short of the corpus's withdraw-ready bar (the seed's
`library-corpus/README.md`, "The admission bar") is orientation only: the
scout runs for the sections it leaves empty, and for those alone. A page whose
own-package list (SPEC-0001 §6) names the library is its page in both lookups
above. It is adopted when the lockfile declares any listed package: the pin
names only those, its parts on the rest are not this project's, and the scout
runs for none of them. With no page in either place, ingest from upstream as usual; the fresh page's
version-durable surface becomes a harvest candidate for the next plant. Reuse
the corpus, re-download only the version-specific delta.

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
`skill.research-and-ingest`'s drift check, which ONLY decides *whether* a
refresh is due.

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

## Scope

Wikify what the code imports directly; trivial transitive dependencies
(every package in `node_modules`) stay implicit. A platform feature that is
part of the runtime itself (`stdlib`, browser built-ins) is covered in
`docs/graph/best-practices/engineering.md`.
