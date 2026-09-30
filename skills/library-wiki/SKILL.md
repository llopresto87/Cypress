---
name: library-wiki
description: Maintain a project-local, version-pinned wiki of every external dependency. Use whenever a new library is being added, an existing one is being upgraded, an idiom for using a library is being adopted, a pitfall is being discovered, or a wiki page is missing for code that already uses a library. The wiki is the source of truth this project consults before writing code that touches a library; agent memory of library APIs is unreliable across versions, so always check or build the wiki first.
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
prevents: A dependency page nobody can tell is stale — no recorded version it was true of, so an upgrade silently turns every idiom and pitfall on it into folklore and a reader has no way to notice.
est_tokens: 1310
---

# library-wiki

The wiki at `docs/graph/libraries/` is this project's source of truth
for every external dependency. Each library used directly by the project
has a page; each page is local, version-pinned, sourced, and
compounding.

This skill is the discipline of building and maintaining those pages. It
is invoked from the `ingest-library` protocol and any time an agent uses
a library and realizes the page is missing or stale.

## When to apply this skill

- A new dependency is being added → create a page.
- A pinned version is bumped → refresh the page.
- A new idiom for using a library was just adopted → record it.
- An agent ran into a behavior the page doesn't cover → add a pitfall
  entry, dated.
- A security advisory affects a wikified library → update §7 and notify
  grill.md §11.
- The page is older than the project's review cadence → refresh.

## The discipline

### 1. The wiki is the project's distillation

A wiki page is the narrow slice of the library that *this project* uses,
plus the project-local idioms, pitfalls, and history. The whole upstream
goes in `docs/graph/sources/raw/` and `docs/graph/sources/normalized/`;
the page in `docs/graph/libraries/` is the project's distillation.

If a wiki page reads like a tutorial for someone who has never used the
library, it has drifted from the discipline: tutorials belong upstream.

### 2. Pin to a version

Every page pins the exact version the project depends on. "Latest" is
not a version. When the project upgrades, the page updates the pin and
adds an §8 (Upgrade path) entry summarizing what changed between the
previous and current pin.

A pin is not by itself a currency claim. Where the page says the
dependency is current, it names the version *and* the support phase of
the line that version belongs to. "On the latest release" and
"supported" are two claims: a line that has left active support
satisfies the first while failing the second, and a pin recorded without
its phase reads as currency to every later reader.

### 3. Cite every claim

Every claim on the page has a citation in §10 (References): a URL, a
retrieval date, and (when the source is paywalled or transient) a local
snapshot path in `docs/graph/sources/raw/`.

Use upstream text as a short quote, in quotes, with its citation, or
rewrite the idea in the project's own words; close paraphrase is
neither: it copies upstream text without attribution. Most pages need
very little upstream text.

### 4. Compound

§3 (Used API surface) lists the names the codebase actually uses, one
line added when a new file starts using a new name. §4 records idioms
once they are adopted, and §5 records pitfalls once they are hit, each
dated. Each section grows when the project meets the thing.

The page grows with the project. A bare page that says only "we use
library X for Y, install with Z" is a perfectly acceptable starting
point. A page left static diverges from the code within weeks: the
docs-librarian keeps each page current at close-out, and the implementer
and reviewer name wiki drift in their handback.

### 5. Validate before publishing

A wiki page becomes authoritative once a smoke test confirms the pinned
version works. The smoke test:
- Imports the library at the pin.
- Calls one or two of the names in §3.
- Runs in the project's normal test harness.

If the smoke test fails, the page is wrong (or the install is wrong);
fix one of them before promoting the page.

## Workflow

Creating and refreshing a page (which phase, which owner, which spawn
waits for which) are `ingest-library.flow` and `ingest-library.refresh`
in `docs/graph/protocols/ingest-library.md`. What this skill adds to the
scout's draft, section by section: §0 (Pin) and §1 (Role) from the
lockfile and the architect's brief; §2 (Install) from a command actually
run in a clean environment, recorded exactly as it worked; §3 (Used API
surface) from the *current* code that uses the library, or, when the
page precedes the code, the names from the brief marked "planned"; §10
(References) from the sources `research-scout` staged in
`docs/graph/sources/`. The smoke test that makes the page authoritative
is the tester's phase of the same pass.

## When to also create a `best-practices/` page

The library wiki is per-dependency. When a *concern* spans multiple
libraries and needs a cohesive guidance (e.g. "how this project handles
HTTP errors across our two HTTP clients"), that's a
`docs/graph/best-practices/<concern>.md`. It links to the relevant wiki
pages.

## Reference files

- `docs/graph/templates/library-page.template.md`: the page template.
- `docs/graph/protocols/ingest-library.md`: the ingest workflow.
- `docs/graph/agents/09-docs-librarian.md`: the agent that owns the
  wiki.
- `docs/graph/agents/10-research-scout.md`: the agent that fetches
  sources.
