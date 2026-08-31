---
name: library-wiki
description: Maintain a project-local, version-pinned wiki of every external dependency. Use whenever a new library is being added, an existing one is being upgraded, an idiom for using a library is being adopted, a pitfall is being discovered, or a wiki page is missing for code that already uses a library. The wiki is the source of truth this project consults BEFORE writing code that touches a library; agent memory of library APIs is unreliable across versions, so always check or build the wiki first.
id: skill.library-wiki
tier: 2
kind: skill
origin: seed
title: library-wiki — version-pinned, cited, compounding pages for every direct dependency
owns:
  - library-wiki.method
  - library-wiki.version-pinning
requires:
peers:
  - skill.research-and-ingest
  - protocol.ingest-library
load_when:
  - "add a new dependency"
  - "create or refresh a library wiki page"
  - "bump a pinned version"
  - "record a library pitfall or idiom"
  - "wiki page is stale or missing"
artifacts:
  - templates/library-page.template.md
est_tokens: 1200
---

# library-wiki

The wiki at `docs/graph/libraries/` is this project's source of truth for
every external dependency. Each library used directly by the project
has a page; each page is local, version-pinned, sourced, and
compounding.

This skill is the discipline of building and maintaining those pages.
It is invoked from the `ingest-library` protocol and any time an
agent uses a library and realizes the page is missing or stale.

## When to apply this skill

- A new dependency is being added → create a page.
- A pinned version is bumped → refresh the page.
- A new idiom for using a library was just adopted → record it.
- An agent ran into a behavior the page doesn't cover → add a pitfall
  entry, dated.
- A security advisory affects a wikified library → update §7 and
  notify grill.md §11.
- The page is older than the project's review cadence → refresh.

## The discipline

### 1. The wiki is local, not a mirror

A wiki page is **not** a copy of upstream documentation. It is the
narrow slice of the library that *this project* uses, plus the
project-local idioms, pitfalls, and history. The whole upstream goes
in `docs/graph/sources/raw/` and `docs/graph/sources/normalized/`; the page in
`docs/graph/libraries/` is the project's distillation.

If a wiki page reads like a tutorial for someone who has never used
the library, it has drifted from the discipline.

### 2. Pin to a version

Every page pins the exact version the project depends on. "Latest"
is not a version. When the project upgrades, the page updates the
pin and adds an §8 (Upgrade path) entry summarizing what changed
between the previous and current pin.

### 3. Cite, don't paraphrase

Every claim on the page has a citation in §10 (References) — a URL,
a retrieval date, and (when the source is paywalled or transient) a
local snapshot path in `docs/graph/sources/raw/`.

Do not paraphrase upstream text closely; either cite a quote (short,
in quotes, with citation) or rewrite the idea in the project's own
words. Most pages need very little upstream text.

### 4. Compound, don't restart

When a new file starts using a new name from the library, add a line
to §3 (Used API surface) — do not list the whole upstream API
preemptively. When a new idiom is adopted, add it to §4 — do not
predict idioms before they're real. When a pitfall is hit, add it
to §5 with a date — do not list theoretical pitfalls.

The page grows with the project. A bare page that says only "we use
library X for Y, install with Z" is a perfectly acceptable starting
point.

### 5. Validate before publishing

A wiki page is not authoritative until a smoke test confirms the
pinned version works. The smoke test:
- Imports the library at the pin.
- Calls one or two of the names in §3.
- Runs in the project's normal test harness.

If the smoke test fails, the page is wrong (or the install is wrong);
fix one of them before promoting the page.

## Workflow (creating a new page)

1. Use `docs/graph/templates/library-page.template.md` to create
   `docs/graph/libraries/<name>.md`.
2. Fill §0 (Pin) and §1 (Role) from the architect's brief.
3. Fill §2 (Install) by running the install command in a clean
   environment and recording exactly what worked.
4. Fill §3 (Used API surface) from the *current* code that uses the
   library. If no code uses it yet (the page is being created during
   architecture), leave §3 empty or list the names from the brief
   with a note "planned".
5. Fill §10 (References) with the sources used. `research-scout`
   stages raw and normalized copies in `docs/graph/sources/`.
6. Add a row to `docs/graph/libraries/index.md`.
7. Write the smoke test.
8. Run the smoke test; promote the page when it passes.

## Workflow (refreshing an existing page)

1. Read the page; note the current pin.
2. Diff the upstream CHANGELOG between the current pin and the new
   pin. Record the behavior changes that affect this project in §8.
3. Update §0 (Pin) with the new version and today's date.
4. Update §3 (Used API surface) for any name that changed.
5. Update §4 (Idioms) if the recommended pattern changed.
6. Update §6 (Deprecations) for the new pin.
7. Update §7 (Security) — re-check advisory feed.
8. Re-run the smoke test at the new pin.
9. Update `docs/graph/libraries/index.md`.

## When to also create a `best-practices/` page

The library wiki is per-dependency. When a *concern* spans multiple
libraries and needs a cohesive guidance (e.g. "how this project
handles HTTP errors across our two HTTP clients"), that's a
`docs/graph/best-practices/<concern>.md`. It links to the relevant wiki
pages; it does not duplicate them.

## Anti-patterns

- **Page is a tutorial.** Tutorials belong upstream; the page is the
  project's distillation.
- **Page covers names we don't use.** §3 lists what the codebase
  actually imports; not the whole upstream surface.
- **Page has no citations.** Cite or it didn't happen.
- **Page lists pitfalls we haven't hit.** Theoretical pitfalls aren't
  useful; real ones, with dates, are.
- **Page never updated after creation.** A static page diverges from
  the code within weeks. The implementer and reviewer keep it
  current.

## Reference files

- `docs/graph/templates/library-page.template.md` — the page template.
- `docs/graph/protocols/ingest-library.md` — the ingest workflow.
- `docs/graph/agents/09-docs-librarian.md` — the agent that owns the wiki.
- `docs/graph/agents/10-research-scout.md` — the agent that fetches sources.
