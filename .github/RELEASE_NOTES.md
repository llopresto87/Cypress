## 8.1.0 — the source index: what a change reaches, read from the code (2026-10-07)

A plant can now ask which code depends on a set of files, which tests a
change reaches, which graph pages cite a file, and where a name is defined,
and get the answer from the code without a model. The tool is
`docs/graph/source-index.py`. Verify, canonize, grow and adopt-existing each
call it once, at the step that needs it. It recommends; verify and tiering
still decide what runs and how much process a change gets.

A node's `repo:` value now decides what it claims on disk, the same way
everywhere the graph reads it. A folder or a file, named with or without a
trailing slash, claims the paths under it; a repository or the plant root
claims nothing. A plant that holds a `repo:` value naming a folder or file
without a slash, such as `src/` or a bare folder name, starts routing on
it after its next graft. A value that names nothing on disk is read as
before, and `anchors` now says so with a `repo-unresolved` note asking the
owner to correct it. The node template's comment states the rule: one
plant-relative path.

### Source index

- `tools/source-index.py` is placed at `docs/graph/source-index.py`. One
  reverse walk over file-to-file links answers three queries: `impact`, the
  code that depends on the inputs, nearest first; `affected-tests`, the same
  walk filtered to the plant's tests, plus an always-run set; and `anchors`,
  the graph pages that cite the inputs, with knowledge nodes kept apart from
  plans, specs and decisions. `build` forces a rebuild.
- `symbols <name>` lists every definition of a name, with path, line and
  kind, and never picks one when several files define it. A Python
  definition, read with `ast`, is `certain`. A shell function, or a
  TypeScript/JavaScript declaration at the top level of its file or
  exported, is read line by line and is `maybe`. A file the tool could not
  read makes the answer `incomplete`, with the action "search by hand".
- `--history` adds to `impact` and `affected-tests` the files that changed
  together with an input in past commits. Each is a `maybe` row in a
  `history` list of its own, with the number of commits the two files
  shared out of those that changed the input. History only adds rows. A
  shallow clone, or a repository with no history, makes the answer
  `incomplete`.
- `anchors --moved` takes its inputs from the moved list of
  `code-anchor.py`, the files changed since the anchor was recorded, so no
  paths are copied by hand. With no anchor, the answer is `incomplete`.
- Links come from Python imports, read with `ast` and never run; `python3`,
  `bash`, `sh` and `source` invocations; quoted path literals, whole or
  joined from segments; and TypeScript/JavaScript `import`, `export from`,
  `require()` and `import()`, resolved through `tsconfig` `paths` and
  `baseUrl`. A mention in Markdown is not a link.
- Each row is `certain` or `maybe`, and a `maybe` row names the reason and
  line of its weakest link. A file whose references cannot be pinned, such
  as a whole-tree walk or a dynamic import, gives `maybe` rows that every
  input reaches alike. These are the floor, listed once after the input's
  own rows. What the tool cannot answer makes the answer `incomplete`, with
  a reason and one action: check by hand, run the full suite, or review by
  hand. `affected-tests` never presents its list as the only tests to run.
- The tests are the plant's `TEST_GLOBS` in `docs/graph/spec-lint.py`. A
  plant can set `exclude`, `always_run` and `global_inputs` in
  `docs/graph/source-index.json`, which is its own file; the installer never
  places it.
- The index is derived scratch in `.cypress/source-index/`, beside an inner
  `.gitignore` of `*`. Any query rebuilds it when its key changes (a commit,
  an uncommitted code edit, a config edit, a graft that changes the tool,
  another Python version), and deleting it is safe. A graft rebuilds it and
  never carries it over.
  [ADR-0029](docs/decisions/adr-0029-source-index-is-derived-scratch.md)
  records the decision; the owner accepted it on 2026-10-07.
  [SPEC-0007](docs/specs/SPEC-0007-source-index.md) holds the contracts.
- The tool needs the Python standard library and `git`, nothing else.

### The protocols call it on demand

Each step below runs the tool once. No hook runs it, and nothing runs it
per prompt or per file access, the pattern ADR-0018 withdrew.

- `verify`: after GREEN and before the gates are chosen, `affected-tests`
  is the recommended floor of the focused tests. The session may run more,
  and never reads a test's absence from the list as proof that the change
  cannot reach it. An `incomplete` answer puts the change in the "affected
  scope genuinely uncertain" row.
- `canonize`: in flow step 1, before `code-anchor.py --record`, the session
  runs `anchors --moved` and hands the pages it names to the docs-librarian
  to re-check. Recording the anchor first would empty the list.
- `grow` and `adopt-existing`: before the scouts are briefed, the
  `inventory` from `build --json` is their file list. On a refresh,
  `impact` over the moved paths gives the blast radius.

### One home for the path rules

- `tools/source_paths.py`, placed at `docs/graph/source_paths.py`, holds the
  rules for what counts as code, which repositories a plant governs, where
  Git ends, the content hash, the atomic write under `.cypress/`, and how a
  page cites a path. `code-anchor.py` and `growth-audit.py` now use it; their
  behaviour is unchanged, and their existing tests prove it.
- `tools/plant_walk.py`, the walk over one plant's files that `graft-audit.py`
  already used, is now also placed, at `docs/graph/plant_walk.py`, because
  `source-index.py` loads it.

### Measured

The figures come from copies of each tree, at seed commit `17d4539`, before
the tool read paths joined from segments; nothing was written into a real
plant.

- On a temporary plant over a clone of the seed, `affected-tests` answered
  for 48 past commits that changed at most three source files, scored
  against the tests each commit edited, out of a set of 40. The full answer
  (tests, always-run and floor) found 0.989 of them, but named 38.0 of the
  40 tests on average: on the seed it suggests nearly the whole suite. The
  input rows alone (tests and always-run, no floor) found 0.880 at 21.7
  tests, and they are the useful part on the seed. The `certain` rows alone
  found 0.120, because most of the seed's links are path literals, which are
  `maybe`.
- A full build of the seed plant takes 0.67 to 0.76 s, and a cached query
  0.10 s. A TypeScript plant of 397 files builds in 0.66 s, and a llama.cpp
  clone of 4,320 files in 3.19 s.

### Checks

- The gate has 51 steps (`python3 tools/gate-registry.py --summary`).
- `tests/test-source-index.sh` holds the source index, on synthetic Git
  plants.

### Upgrade notes

- **New placed tools.** Every install now places
  `docs/graph/source-index.py`, `docs/graph/source_paths.py` and
  `docs/graph/plant_walk.py`, fast-forwarded like the other seed tools. The
  installer writes no index; the first query builds it.
- **Set `exclude` before reading an answer as a gate set.** A plant's
  `TEST_GLOBS` often match fixtures, helpers and a suite runner. List them
  under `exclude` in `docs/graph/source-index.json`.

### Known limits

- `symbols` says where a name is defined, not who uses it. A TS/JS class
  member, an indented declaration that is not exported, and a definition in
  a shell here-document are not read.
- History does not follow renames, and a CI checkout that holds one commit
  gives no history rows, so every `--history` answer there is
  `incomplete`.
- Hook commands written in host settings files, such as
  `.claude/settings.json`, are not read, so a hook script has no dependent
  in any answer.
