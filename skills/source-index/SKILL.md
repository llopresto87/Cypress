---
name: source-index
description: Answers impact, affected-tests, anchors and symbols queries on a plant's code via docs/graph/source-index.py, without a model.
id: skill.source-index
tier: 2
kind: skill
origin: seed
title: source-index - what depends on a file, which tests it reaches, which pages cite it, where a name is defined
owns:
  - source-index.usage
  - source-index.limit
  - source-index.report
requires:
peers:
  - protocol.verify
  - protocol.canonize
  - protocol.grow
  - protocol.graft
  - skill.adopt-existing
load_when:
  - "what depends on this file, depends on before changing, dependents of a file"
  - "impact of a change to a file, blast radius of a change, what breaks if I change this file"
  - "which tests does a change reach, tests a change reaches, affected tests"
  - "which tests to run for a file, tests cover this file"
  - "graph pages cite, pages cite a file, which nodes cite, stale graph facts after a code move"
  - "where is the function defined, where is a name defined, find the definition of a name"
  - "source index, source-index build report, repo-unresolved record"
prevents: A placed tool nobody reaches for - sessions grep for dependents, guess the tests a change reaches, miss the graph pages a code move made stale, and read a missing row as proof that nothing is affected.
est_tokens: 1900
---

# source-index - the plant's code questions, answered without a model

`docs/graph/source-index.py` reads the code of every repository the plant
governs and answers four questions from a derived cache. It recommends;
verify, the tier and canonize still decide what runs. Its contracts are the
seed's SPEC-0007; this page is how a session uses it.

## 0. Identity

- **Name:** source-index
- **Path:** `docs/graph/source-index.py`, placed by the installer with the
  siblings it loads by file path (`source_paths.py`, `plant_walk.py`,
  `frontmatter.py`, and `code-anchor.py` for `anchors --moved`)
- **Language / runtime:** python3 (standard library) and `git`
- **Owner:** the seed; a plant never edits the placed copy, an install or
  graft replaces it
- **Stability:** stable

## 1. What it does

It inventories the code of the plant root (when it is a Git work tree) and
of each nested work tree a node's `repo:` names, and reads file-to-file
links: Python imports and loads by file path (read with `ast`, never run),
`python3`/`bash`/`sh`/`source` invocations, quoted path literals, and
TS/JS `import`/`export from`/`require()`/`import()` through `tsconfig` or
`jsconfig` `paths`. A Markdown mention is not a link. The same pass reads
definitions for `symbols`.

## 2. Interface & invocation

Run every command from the plant root:

```sh
python3 docs/graph/source-index.py --help
python3 docs/graph/source-index.py build [--json]
python3 docs/graph/source-index.py impact         [--depth N] [--history] [--all] [--json] <path>... | -
python3 docs/graph/source-index.py affected-tests [--depth N] [--history] [--all] [--json] <path>... | -
python3 docs/graph/source-index.py anchors                  [--all] [--json] <path>... | - | --moved
python3 docs/graph/source-index.py symbols                  [--all] [--json] <name>... | -
```

- **Inputs:** plant-relative paths (or names for `symbols`), or `-` to
  read them from stdin; `--depth` 1 to 5 (default 3); `--history` adds
  files that changed together in past commits; `--moved` takes the inputs
  from `code-anchor.py`'s moved list.
- **Outputs:** a text view (`--all` prints every row) or `--json`. Rows are
  `certain` or `maybe`; what the tool could not answer is listed as
  `incomplete`, and the closing line says what to do instead. Every query
  exits 0 with an answer; a malformed command line exits 2.
- **Writes:** only the self-ignored cache under `.cypress/source-index/`,
  rebuilt by any query whose key moved (a commit, an uncommitted code edit,
  the config, `TEST_GLOBS`, the tool). It is scratch, never committed.

**Configuration the plant owns** (no tool writes it):

- `TEST_GLOBS` in `docs/graph/spec-lint.py`: the test class.
- `docs/graph/source-index.json`, optional: `exclude` (out of the test
  class), `always_run` (tests every change runs), `global_inputs` (files
  such as `package.json` whose change makes every answer incomplete).
- each node's `repo:` value: which repository or folder the node owns.

After changing any of the three, rerun `build` and read its report.

## 3. Where the code lives

- **Entry point:** `docs/graph/source-index.py` (seed `tools/source-index.py`)
- **Supporting files:** the siblings named in section 0
- **Dependencies:** none beyond the standard library and `git`

## 4. When to use it (and when not)

- **Use when:** before changing a file, run `impact` to see what depends on
  it; when choosing tests, run `affected-tests` and add the always-run set
  it prints; at canonize, run `anchors --moved` to find the graph pages
  that cite code that moved; to find where a name is defined, run `symbols`.
- **Do not use when:** the question is about prose, Markdown or graph
  structure (the router and `graph-lint.py` own those), or about callers of
  a function (the index holds file links, not a call graph).
- **The limit, in one line:** an answer is a recommendation over cooperative
  code, and a file's absence from `dependents` or `tests` is never proof
  that it is unaffected.

## 5. The build report

The installer runs `build` as its last step on every install and graft
apply, and `growth-audit.py` prints the same report after its verdicts. The
report is advice and never fails either. It holds the cache line, the
counts, the time, and one record per setup gap, each followed by its
`fix:` line: `no-repository`, `no-test-declaration`, `repo-unresolved` (a
`repo:` value that names nothing on disk), and the rest. Hints name test
files outside `TEST_GLOBS`, non-test files inside it, and config patterns
that match nothing. A session acts on each record by its fix line, through
the protocol that owns it, then reruns `build`.

## 6. Pitfalls and sharp edges

- **A missing row is not a clean bill:** dynamic imports, generated paths
  and hook commands in host settings files are not read; the floor and the
  `incomplete` list say where the answer stops.
- **`affected-tests` is never "only these":** run the listed tests, the
  always-run set, and the full suite whenever the answer is incomplete.
- **A wrong `repo:` silently narrows `anchors`:** fix every
  `repo-unresolved` record before trusting the anchors answer.
- **No Git, no index:** a plant root that is not a work tree and names no
  repository gets the `no-repository` record and no cache.

## 7. References & neighbours

- **Protocols that call it:** `protocol.verify` (affected tests, never the
  whole decision), `protocol.canonize` (`anchors --moved`, then correct a
  `repo:` value it names), `protocol.grow` and `skill.adopt-existing`
  (`build --json` gives scouts the file list; grow's delivery records the
  report of its last growth-audit run), `protocol.graft` (the apply install
  prints the report; Phase 6 corrects the `repo:` values it names, Phase 7
  records each line and what was done with it).
- **Related tools:** `docs/graph/code-anchor.py` (the moved list),
  `docs/graph/graph-lint.py` (routing; owns no code facts).
- **Decisions:** the cache is derived scratch, rebuilt and never canonical;
  a seed tool is surfaced by a seed skill, not a card in `docs/graph/tools/`.

## 8. Changelog

The seed's CHANGELOG records each change to the tool and this page.
