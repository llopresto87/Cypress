---
status: accepted
status_date: 2026-10-07
owner: architect
---

# ADR-0029: the source index is derived scratch: self-ignored, rebuilt on any key change, never committed, never canonical

## Status

See frontmatter (single home). Proposed with SPEC-0007 for 8.1.0 and
ratified by the owner (see Ratification).

## Date

2026-10-07

## Context

SPEC-0007 adds `source-index.py`, which derives a repository's file
inventory, its file-to-file links and the records of what it could not
pin, and answers `impact`, `affected-tests` and `anchors` from that. A
full derivation costs 0.66 s on a 397-file TypeScript plant and 3.19 s on a
4,320-file tree (the tool, measured 2026-10-07), so a session that asks several questions wants the
result kept between queries. Where it is kept, and what it is allowed to be,
decides four things:

- The graph is the one home of knowledge (kernel §3.2). A derived file that
  sits in `docs/graph/`, or is committed beside it, reads as a fact some
  author vouched for. `graph-lint.py` walks `docs/graph/`, and `code-anchor.py`
  treats it as the graph, not code.
- The plants disagree about `.cypress/`. The seed's and Vivid's `.gitignore`
  ignore all of it; this plant tracks `anchor.json`, `coverage.json`,
  `recreated-nodes.txt` and `seed.json` and ignores only `growth/` and
  `session/`. The installer writes no `.gitignore` entry for `.cypress/`, and
  a plant's `.gitignore` is the plant's file.
- Graft copies the whole plant byte for byte, `.cypress/` included
  (`tools/graft-run.py` `copy_tree`), classes every `.cypress/` path as
  machinery (`is_machinery`), and no code sweeps unknown `.cypress/` files. A
  cache therefore survives a graft into a seed whose tool reads it
  differently.
- CodeGraph, the reference tool studied on 2026-10-07, keeps its index fresh
  by incremental sync, and its own benchmark found the synced edge set
  4.3 percent away from a full rebuild while the node sets matched.

Doing nothing (no cache) is viable but repeats a 3 s derivation per question
on the larger plants; a committed index is not, for the reasons above.

## Decision

The index is derived scratch: it lives at `.cypress/source-index/index.json`
beside an inner `.gitignore` of `*` that the tool writes itself; it is keyed
on the schema, the running Python's major.minor, the digest of the tool and of every sibling it loads by file
path (`source_paths.py`, `plant_walk.py`, `frontmatter.py`), the digest of the
plant's test declaration and config, and each governed repository's HEAD and
uncommitted-code digest; any mismatch or any unreadable document is a full
rebuild; it holds plant-relative paths, never absolute ones, and no tool,
protocol or node ever treats it as a source of truth.

The central trade: a full rebuild on every key change spends up to a few
seconds where an incremental update would spend milliseconds, and in return
the cache can never drift from what a rebuild by the same interpreter would
say.

## Consequences

- The index is safe to delete at any time; the next query rebuilds it and
  says so. `install.sh` never deletes it and writes no byte of it itself;
  since 8.1.2 it runs the placed tool's `build` as its last step, so the tool,
  through its own atomic write, writes it on every install and every graft's
  apply (Amendment below). Graft needs no preserve rule and no ignore edit: a
  graft that changes the tool changes the key, and its install rebuilds the
  cache at once; a cache carried over unchanged equals a rebuild, because the
  build is deterministic.
- The interpreter is part of the key because `ast` parses by the running
  Python's grammar: the seed's own `templates/knowledge-graph/graph-lint.py`
  does not parse on 3.11 (a backslash inside an f-string expression, legal
  from 3.12), so one tree is `unreadable` under one interpreter and linked
  under another. A cache built by one Python and read by another rebuilds.
- Accepted gap: Git's ignore sources outside the work tree
  (`.git/info/exclude`, the user's `core.excludesFile`) change the inventory
  but are not in the key; an edit there shows at the next key change or a
  forced `build`. Hashing them would add per-user state to a key the plant
  shares for little gain.
- The tool never creates `.cypress/`; without it a query answers from memory
  and writes nothing (SPEC-0007 `CYPRESS_DIR_ABSENT`).
- Writes follow `code-anchor.py`'s discipline, which moves into the shared
  helper `tools/source_paths.py`: descriptor-relative, no symlink followed,
  exclusive temp file, atomic replace. The helper's write takes its target
  name, temp prefix and refusal name as parameters, so code-anchor's messages
  stay as they are (SPEC-0007 §6 "Helper").
- The self-written inner `.gitignore` of `*` then has two writers: the
  helper, and route-hook for `.cypress/session/`. Route-hook is placed outside
  `docs/graph/` and cannot load the helper, so the helper's docstring names
  route-hook's writer as the other home of the rule; a change to the rule
  changes both.
- Anchors citations are read from the pages on every query, never cached, so
  an uncommitted node edit is seen at once without widening the key to
  `docs/graph/`.
- Reversal cost: none for data (the cache is scratch); a change of shape is a
  schema bump, and the old cache is rebuilt on first read.
- The tests that fail if this decision is reversed silently:
  SPEC-0007 `CACHE_WRITTEN_SELF_IGNORED` (a committed or unignored cache),
  `CACHE_REBUILT_WHEN_THE_KEY_CHANGES` (a key part dropped, the interpreter
  included),
  `GRAFT_REBUILDS_THE_CACHE` (a cache carried across a tool change) and
  `BUILD_IS_DETERMINISTIC` (an absolute path or unstable order inside it).
- Wiki: no library page; stdlib `json`, `hashlib`, `os` and Git only.

## Alternatives considered

- **Commit the index beside the graph:** reviewable in a diff, but every
  commit that touches code changes it, two branches conflict on it, a
  checkout leaves it stale until someone rebuilds and commits, and a reader
  of `docs/graph/` takes it for authored knowledge — rejected because it
  makes derived structure look canonical (kernel §3.2).
- **Incremental update keyed on changed files:** fast, but cross-file
  resolution changes answers in files that did not change (a module added
  next to an ambiguous import, a tsconfig edit), which is the drift
  CodeGraph measured at 4.3 percent of edges; a full rebuild costs at most a
  few seconds here — rejected.
- **No cache, derive on every query:** simplest and never stale, but repeats
  up to 3.2 s per question on the larger plants and gives no shared result to
  the queries of one session — rejected for slice 1; it stays the fallback
  whenever the cache cannot be written.
- **Add `.cypress/source-index/` to the plant's `.gitignore` at install:** the
  `.gitignore` is a plant file the installer does not own, and a fresh clone
  of a plant that ignores `.cypress/` wholesale would gain a redundant line —
  rejected in favour of the self-written inner `.gitignore`, the pattern
  route-hook's `.cypress/session/` already uses.
- **A `sqlite3` database:** stdlib, but the owner ruled SQLite out on
  2026-10-07, and a sorted JSON document at these sizes (53 KB of edges on
  Vivid) needs no query engine — rejected.
- **Install deletes the cache on every run:** would make "graft rebuilds"
  literal, but it is a deletion the installer has no other reason to make,
  and the tool-digest key already forces the rebuild — rejected.

## Reversibility

`reversible`: the cache is scratch, nothing reads it but the tool, and a
change of location or shape is a constant and a schema bump in one file.

## References

- Spec: `docs/specs/SPEC-0007-source-index.md` (§2, §6 "Helper" and "Cache document", §7)
- Grill: `docs/plans/grill-8.1.0-source-index.md` §6
- Related: ADR-0018 (the code anchor; no per-file or per-prompt staleness
  tool), ADR-0010 and ADR-0024 (context residency; the route hook stores node
  ids only)
- External sources: CodeGraph `docs/benchmarks/index-drift-cg33.md` at
  31c3328, read 2026-10-07 by the reference scout (not kept in the seed)

## Ratification

Ratified by the owner, 2026-10-07: "adr accepted". Two corrections made at ratification: the Status line no longer ties acceptance to the spec's signing, and the cost figures quote the tool's measurement (3.19 s on 4,320 files) in place of the pre-build estimate (3.8 s on 4,865 files).

## Amendment, 8.1.2 (2026-10-07), ratified

Ratified by the owner, 2026-10-07: "1 ok 2 ok 3 go", item 2 of which is this
amendment (question 8 of `docs/plans/grill-8.1.2-tool-surfacing.md` §12). It
amends this accepted record in place, not by a superseding record, because
the decision stands and one consequence changes. SPEC-0001 states the write
against its own rules (`SINGLE_WRITER`, `IDENTICAL_RERUN_IS_INERT`, its
8.1.2 entry in §12).


The owner ruled on question 2 of `docs/plans/grill-8.1.2-tool-surfacing.md`
§12: "ACTUALLY BUILD IT. a user cannot be expected to know that it needs to
do things if it executes a graft/install/growth. the plant needs to be ready
to go from te get-go after executing the protocols". The decision above is
unchanged: the index stays derived scratch, self-ignored, keyed, never
committed and never canonical. One consequence changes: the installer no
longer leaves the first build to a query. It runs
`python3 docs/graph/source-index.py build` from the plant root as its last
step and prints the report, never failing on it (SPEC-0007
`INSTALL_RUNS_THE_BUILD`, `INSTALL_BUILD_FAILED`). The write is the tool's,
under this record's rules; `install.sh` gains no write site of its own, so
SPEC-0001 `SINGLE_WRITER`'s census of the installer's writes is unchanged. What this costs: every install
spends the build's time (0.66 s to 3.19 s measured, bounded at 120 s), and an
identical re-install replaces the cache with equal bytes. The rejected
alternative "Install deletes the cache on every run" stays rejected: the
build replaces the cache, it never deletes it.
