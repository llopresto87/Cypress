# CYPRESS: the source index

The source index answers four questions about a plant's code without a
model: which code depends on a set of files, which tests a change reaches,
which graph pages cite a file, and where a name is defined. It is one
tool, `docs/graph/source-index.py`, placed in every plant since 8.1.0. It
recommends. Verify, tiering and canonize still decide what runs and how
much process a change gets.

Every command and output below comes from `python3 tools/source-index.py
--help` and from runs on a temporary plant installed over a clone of the
seed at `efd75fe`. The contracts are
[SPEC-0007](../docs/specs/SPEC-0007-source-index.md); the decision that
the index is scratch is
[ADR-0029](../docs/decisions/adr-0029-source-index-is-derived-scratch.md).

---

## What it reads

The tool inventories the code of every governed repository: the plant root
when it is a Git work tree, plus each nested work tree a node names in
`repo:`. From that code it reads file-to-file links:

- Python imports and loads by file path, read with `ast` and never imported
  or run;
- `python3`, `python`, `bash`, `sh` and `source` invocations;
- quoted path and directory literals, whole or joined from segments, as in
  `ROOT / "tools" / "x.py"`, `os.path.join(...)` or a TS/JS `path.join(`;
- TypeScript and JavaScript `import`, `export from`, `require()` and
  `import()`, resolved through the `paths` and `baseUrl` of `tsconfig` or
  `jsconfig`.

A mention in Markdown is not a link. A hook command written in a host
settings file, such as `.claude/settings.json`, is not read either, so a
hook script has no dependent in any answer.

The same pass reads each file's definitions for `symbols`: Python
definitions by `ast`, shell functions and top-level or exported TS/JS
declarations by reading lines.

The tool needs the Python standard library and `git`, nothing else. It
loads `source_paths.py`, `plant_walk.py` and `frontmatter.py` from beside
itself, and `code-anchor.py` for `anchors --moved` only. The installer
places all of them.

## The commands

Run every query from the plant root:

```
python3 docs/graph/source-index.py build [--json]
python3 docs/graph/source-index.py impact         [--depth N] [--history] [--all] [--json] <path>... | -
python3 docs/graph/source-index.py affected-tests [--depth N] [--history] [--all] [--json] <path>... | -
python3 docs/graph/source-index.py anchors                  [--all] [--json] <path>... | - | --moved
python3 docs/graph/source-index.py symbols                  [--all] [--json] <name>... | -
```

| Flag | What it does |
|---|---|
| `-` | read the inputs from stdin, one per line |
| `--depth N` | how far the reverse walk goes, 1 to 5; the default is 3 |
| `--history` | add the files that changed together with an input in past commits |
| `--all` | print every row; the text view otherwise cuts each list at 40 rows and says how many more there are |
| `--json` | print the answer as JSON (schema `cypress.source-index.answer/1`) |
| `--moved` | `anchors` only: take the inputs from the moved list of `code-anchor.py` |

Every query exits 0 with an answer. What the tool cannot answer is listed
in the answer as `incomplete`. A malformed command line, such as
`--depth 9`, exits 2 with a usage line.

### build

`build` derives the whole index and writes the cache, even when the cached
copy is current. Any other query builds the index itself when it needs to,
so `build` is rarely needed by hand.

```
$ python3 docs/graph/source-index.py build
Cache: rebuilt (build forced)
Index: 916 file(s), 184 test(s), 118 certain and 9463 maybe link(s), 170 opaque and 33 unresolved record(s), 2510 definition(s)
```

`build --json` prints the index itself, with the keys `inventory`, `links`,
`opaque`, `unresolved` and `symbols`. Each `inventory` row holds a file's
path, repository, content hash, language and test class. `grow` and
`adopt-existing` hand this list to their scouts as the file list.

### impact

`impact` lists the code that depends on the inputs. `certain` rows come
first, and inside each class the nearest rows come first. Each row starts
with its depth, then its link class, the dependent, the file it depends on,
the kind of link with its line, and, for a `maybe` row, the reason and line
of the weakest link on its path.

```
$ python3 docs/graph/source-index.py impact tools/source_paths.py
Cache: reused
Input: tools/source_paths.py (walked)
1 certain tools/code-anchor.py  <- tools/source_paths.py [import exact:57]
1 certain tools/growth-audit.py  <- tools/source_paths.py [import exact:166]
1 certain tools/source-index.py  <- tools/source_paths.py [import exact:72]
1 maybe install.sh  <- tools/source_paths.py [path-literal path-literal:1571] maybe: path-literal at install.sh:1571
1 maybe tests/seed-lint.py  <- tools/source_paths.py [path-literal directory:205] maybe: directory at tests/seed-lint.py:205
...
2 maybe tests/run.sh  <- tests/seed-lint.py [invoke resolved:126] maybe: directory at tests/seed-lint.py:205
...
```

### affected-tests

`affected-tests` runs the same walk and keeps only the plant's tests. It
then lists the always-run set and the floor (both explained below), and it
ends with a reminder that the list is a recommendation.

```
$ python3 docs/graph/source-index.py affected-tests tools/source_paths.py
Cache: reused
Input: tools/source_paths.py (walked)
1 maybe tests/seed-lint.py  <- tools/source_paths.py [path-literal directory:205] maybe: directory at tests/seed-lint.py:205
1 maybe tests/test-code-anchor.sh  <- tools/source_paths.py [path-literal path-literal:31] maybe: path-literal at tests/test-code-anchor.sh:31
...
Always run: tests/gate_pool.py (no-code-edge)
Always run: tests/test-tier-lanes.sh (no-code-edge)
...
Floor: 14 maybe row(s) every input reaches (opaque holders and their dependents):
1 maybe tests/legal-lint.py  <- - [opaque walks-tree:255] maybe: walks-tree at tests/legal-lint.py:255
...
Recommendation only: the tests above and the always-run set, never only these; verify decides what runs.
```

The always-run set holds the tests the plant lists under `always_run`
(reason `declared`) and every test that links to no code at all (reason
`no-code-edge`), because nothing says what such a test covers.

### anchors

`anchors` lists the graph pages that cite each input, with the form of the
citation and how it matched. Knowledge nodes are listed as facts. Pages
under `docs/graph/plans/`, `docs/graph/specs/` and `docs/graph/decisions/`
are history: they are counted, and `--all` names them.

```
$ python3 docs/graph/source-index.py anchors docs/graph/graph-lint.py templates/knowledge-graph/graph-lint.py
Cache: reused
Input: docs/graph/graph-lint.py (walked)
Input: templates/knowledge-graph/graph-lint.py (walked)
docs/graph/graph-lint.py: 13 fact(s), 0 history page(s)
  certain backtick docs/graph/README.md (exact)
  certain backtick docs/graph/_schema.md (exact)
...
templates/knowledge-graph/graph-lint.py: uncited
```

A node also claims the paths under the folder or file its `repo:` value
names. See [The `repo:` rule](#the-repo-rule) below.

### anchors --moved

`anchors --moved` takes its inputs from the moved list of `code-anchor.py`:
the code files changed since canonize last recorded the anchor. Nobody
copies paths by hand.

```
$ python3 docs/graph/code-anchor.py --record
Code anchor recorded 2026-10-07T21:00:12Z: . main@efd75fe (3 uncommitted)
$ echo "# x" >> tools/plant_walk.py
$ python3 docs/graph/source-index.py anchors --moved
Cache: rebuilt (key changed)
Input: tools/plant_walk.py (walked)
tools/plant_walk.py: uncited
```

When nothing moved, the answer says `Moved: no code moved since the code
anchor.` With no anchor recorded, the answer is `incomplete`:

```
$ python3 docs/graph/source-index.py anchors --moved
Cache: reused
- incomplete: moved-unavailable: .cypress/anchor.json (no .cypress/anchor.json)
Incomplete: review by hand (moved-unavailable: .cypress/anchor.json).
```

### symbols

`symbols <name>` lists every definition of a name, with its link class,
kind, path, line and how it was read. When several files define a name,
the tool lists them all and never picks one. A dotted name matches a
qualified name whole.

```
$ python3 docs/graph/source-index.py symbols repo_kind main
Cache: reused
main: 30 definition(s)
  certain function integrations/claude-code/agent-lint.py:1330 main (ast)
  ...
  maybe function tests/test-full-install.sh:755 main (line-reading)
repo_kind: 2 definition(s)
  certain function templates/knowledge-graph/source_paths.py:237 repo_kind (ast)
  certain function tools/source_paths.py:237 repo_kind (ast)
```

A Python definition, read with `ast`, is `certain`. A shell function, or a
TS/JS declaration at the top level of its file or exported, is read line by
line and is `maybe`. The kinds are `function`, `class`, `variable` and
`type`. A name with no definition says what was read and what was not:

```
$ python3 docs/graph/source-index.py symbols no_such_name
Cache: reused
no_such_name: no definition (read: Python definitions, shell functions, TS/JS declarations; not read: docs/graph/, .cypress/, which are not code)
```

A file the tool could not read makes the answer `incomplete`, with the
action "search by hand".

### --history

`--history` adds to `impact` and `affected-tests` the files that changed
together with an input in past commits. Each one is a `maybe` row in a
`History` list of its own, with the number of commits the two files shared
out of those that changed the input. A file another list already holds is
not repeated, so history only adds rows.

```
$ python3 docs/graph/source-index.py impact --history tools/code-anchor.py
...
History: 4 maybe row(s), files that changed together with an input (--history):
1 maybe docs/specs/SPEC-0007-source-index.md  <- tools/code-anchor.py [history 2/6]
1 maybe integrations/prime-agent/status-extension.ts  <- tools/code-anchor.py [history 2/6]
1 maybe docs/specs/SPEC-0003-per-prompt-injection.md  <- tools/code-anchor.py [history 1/6]
1 maybe manifest.json  <- tools/code-anchor.py [history 1/6]
...
```

The tool reads the newest 500 commits that are not merges, and skips a
commit that changed more than 40 indexed files. It does not follow renames,
and history is never cached. A shallow clone, or a repository with no
history, makes the answer `incomplete`:

```
- incomplete: history-shallow: . (a shallow clone: its oldest commit is not read)
Incomplete: check by hand (history-shallow: .).
```

## Reading an answer

### certain and maybe

Each row is `certain` or `maybe`. A `certain` row rests only on links the
tool pinned exactly, such as a Python import. A `maybe` row names the
reason and line of its weakest link: a path literal, a directory, an
ambiguous match, a line-read definition, or a co-change.

On the seed most links are path literals, so most rows are `maybe`. Read
the `maybe` rows; the `certain` rows alone miss most tests (see
[Measured](#measured)).

### The floor

Some files hold references the tool cannot pin: a walk over a whole tree,
a dynamic import, an unreadable file, a specifier no alias maps. Such a
file is an `opaque` holder. It might reach any file, so every input reaches
it and its dependents alike. These rows are the floor. They are listed once,
after the input's own rows, under a `Floor:` line, and the floor walk has
no depth limit.

### incomplete

When the tool cannot answer part of a query, the answer is `incomplete`.
Each gap is a line `- incomplete: <reason>: <subject>`, and the answer ends
with one action:

| Query | Action |
|---|---|
| `build`, `impact` | check by hand |
| `affected-tests` | run the full suite |
| `anchors` | review by hand |
| `symbols` | search by hand |

Common reasons, all printed by the tool:

| Reason | Meaning |
|---|---|
| `input-not-found` | the input is not a file in the index |
| `global-input` | the input matches `global_inputs` |
| `depth-cap` | the walk stopped at `--depth` with more to go |
| `moved-unavailable` | `anchors --moved` found no recorded anchor |
| `history-shallow`, `history-unavailable` | `--history` could not read the commit history |
| `repo-unresolved` | a node's `repo:` names nothing on disk |
| `config-refused` | `docs/graph/source-index.json` was refused; the defaults apply |
| `git-unavailable`, `no-repository` | there is no `git`, or no governed Git repository |

For example:

```
$ python3 docs/graph/source-index.py impact tools/nope.py pyproject.toml
Cache: reused
- incomplete: global-input: pyproject.toml
- incomplete: input-not-found: pyproject.toml
- incomplete: input-not-found: tools/nope.py
Incomplete: check by hand (global-input: pyproject.toml, input-not-found: pyproject.toml, input-not-found: tools/nope.py).
```

`affected-tests` never presents its list as the only tests to run, even
when the answer is complete.

## The cache

The index is derived scratch in `.cypress/source-index/index.json`, beside
an inner `.gitignore` that holds `*`, so Git never tracks it. Any query
rebuilds it when its key changes, and the first line of each answer says
what happened: `built`, `reused`, `rebuilt (key changed)` or
`rebuilt (build forced)`. The key holds:

- the Python major and minor version;
- the tool and the files it loads beside it, so a graft that changes the
  tool rebuilds the index;
- the plant config and the plant's `TEST_GLOBS`;
- each repository's HEAD and its uncommitted code.

Deleting the directory is safe. The installer never writes it, and a graft
rebuilds it instead of carrying it over
([ADR-0029](../docs/decisions/adr-0029-source-index-is-derived-scratch.md)).

## Plant configuration

The tests are the files that match the plant's `TEST_GLOBS` in
`docs/graph/spec-lint.py`. A plant can add `docs/graph/source-index.json`,
which is its own file; the installer never places it. It may set three
keys, each a list of path patterns:

| Key | Effect |
|---|---|
| `exclude` | files removed from the test class; an excluded file keeps its links |
| `always_run` | tests listed in the always-run set of every `affected-tests` answer |
| `global_inputs` | files whose change can reach every file; naming one as an input makes the answer incomplete |

A key the file sets replaces that key's default whole. `global_inputs`
defaults to common build and test configuration: `package.json`,
lockfiles, `tsconfig*.json`, `pyproject.toml`, `conftest.py`,
`requirements*.txt` and similar. A file that is not JSON, or that holds an
unknown key or a value that is not a list of strings, is refused whole,
and the answer carries `config-refused`.

```json
{
  "exclude": ["tests/fixtures/**", "tests/helpers/**", "tests/run.sh"],
  "always_run": ["tests/test-smoke.sh"]
}
```

Set `exclude` before you read an answer as a gate set. A plant's
`TEST_GLOBS` often match fixtures, helpers and the suite runner; on the
seed, the test class held 184 files, fixtures and helpers among them.

## The `repo:` rule

A node's `repo:` value decides what the node claims on disk, the same way
for the router in `graph-lint.py --plan` and for `anchors`. What the value
names on disk decides, with or without a trailing slash:

| The value names | The node claims |
|---|---|
| a folder (with at least one entry) or a file | that path and every path under it |
| the plant root, or a directory holding `.git` | nothing |
| a path outside the plant | nothing |
| nothing on disk | what it claimed before 8.1.0, and `anchors` adds a note |

The note is an `incomplete` record that names the page and the value:

```
- incomplete: repo-unresolved: docs/graph/nodes/demo.md (repo: srcx names nothing on disk; correct the node's repo:)
Incomplete: review by hand (repo-unresolved: docs/graph/nodes/demo.md).
```

Fix it by writing one plant-relative path in the node's `repo:`: a
repository, a folder or a file. A plant that holds a value naming a folder
or file without a slash, such as a bare folder name, starts routing on it
after its next graft. The rule lives in `source_paths.py`, which the
router and `anchors` share; the same module decides which repositories a
plant governs.

## When the protocols call it

Each step runs the tool once, on demand. No hook runs it, and nothing runs
it per prompt or per file access.

| Protocol | Step | Query |
|---|---|---|
| [verify](protocols-reference.md#risk-proportional-gate-depth-verifyrisk-depth) | after GREEN, before the gates are chosen | `affected-tests <changed paths>`: the recommended floor of the focused tests; an `incomplete` answer puts the change in the "affected scope genuinely uncertain" row |
| [canonize](protocols-reference.md#the-flow--one-spawn-canonizeclose-out-flow) | flow step 1, before `code-anchor.py --record` | `anchors --moved`: the pages the docs-librarian re-checks; recording the anchor first would empty the list |
| [grow](protocols-reference.md#the-growth-flow-growgrowth-flow--six-phases) | before the scouts are briefed | `build --json`: the `inventory` is the scouts' file list |
| [adopt-existing](skills-and-templates-reference.md#a1-adopt-existing) | scout pass, and on a refresh | `build --json` for the file list; `impact` over the moved paths for the blast radius |

The session may run more tests than `affected-tests` lists. It never reads
a test's absence from the list as proof that the change cannot reach it.

## Measured

These figures come from the 8.1.0 release notes. They were taken on copies
of each tree, at seed commit `17d4539`, before the tool read paths joined
from segments.

- On a temporary plant over a clone of the seed, `affected-tests` answered
  for 48 past commits that changed at most three source files, scored
  against the tests each commit edited, out of a set of 40. The full answer
  (tests, always-run and floor) found 0.989 of them but named 38.0 of the
  40 tests on average. The input rows alone (tests and always-run, no
  floor) found 0.880 at 21.7 tests. The `certain` rows alone found 0.120.
- A full build of the seed plant takes 0.67 to 0.76 s, and a cached query
  0.10 s. A TypeScript plant of 397 files builds in 0.66 s, and a llama.cpp
  clone of 4,320 files in 3.19 s.

## Limits

- `symbols` says where a name is defined, not who uses it. It does not read
  a TS/JS class member, an indented declaration that is not exported, or a
  definition inside a shell here-document.
- `--history` does not follow renames. A CI checkout that holds one commit
  gives no history rows, so every `--history` answer there is `incomplete`.
- Hook commands in host settings files are not read, so a hook script has
  no dependent in any answer.
- Only Python, shell, TypeScript and JavaScript files carry links.
- The tool recommends. It never decides which gates run or how a change is
  tiered.

## See also

- [skills-and-templates-reference.md](skills-and-templates-reference.md#summary-table--seed-tools-placed-beside-the-contract-files):
  the placed seed tools, `source_paths.py` and `plant_walk.py` among them.
- [What's new in 8.0 and 8.1](whats-new-8.md).
