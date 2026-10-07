---
status: active
status_date: 2026-10-07
owner: architect
---

# SPEC-0007: source-index

## 0. Metadata

- **Identifier:** SPEC-0007-source-index
- **Status:** see frontmatter (single home)
- **Owner:** architect
- **Date:** 2026-10-07
- **Last reviewed:** 2026-10-07 (review `reviewer-spec`, amended by `architect-amend`; joint-pass step-3 returns applied by `architect-fix`; devils-advocate verdicts applied by `architect-da`; the load by file path made `certain` by `architect-q5`)
- **Related grill section:** docs/plans/grill-8.1.0-source-index.md §6 (the owner's rulings of 2026-10-07: one walk with three link kinds; the helper's scope; test roots and plant config; graph-lint keeps its tier-2 rule)
- **Related ADRs:** adr-0029-source-index-is-derived-scratch (proposed): the index is derived scratch, self-ignored, rebuilt on any key change, never committed and never canonical
- **Related specs:** SPEC-0001-install-placement (placement), SPEC-0003-per-prompt-injection (code anchor)
- **Related wiki pages:** none (stdlib Python and git only)
- **Design latitude:** balanced. The owner approved on 2026-10-07: "implement the plan so that it's integrated organically into the cypress seed and installed/grafted into the plants correctly." New structure is allowed where the change needs it (one shared helper module, one derived cache); no concept the plan did not name.
- **Supersedes:** none
- **Superseded by:** none
- **Sign-offs:** product [x] (2026-10-07: §3 and §9 reflect the owner's outcome) · architect [x] (2026-10-07, `architect-da`: §4 to §8 coherent after the devils-advocate verdicts; the floor, the helper interface, the interpreter in the key and the TS/JS line join applied) · tester [x] · security [x] (2026-10-07, `security-s5s7`: §5 Security requirements and seven §7 abuse cases added; four §6 constants, `FILE_MAX_BYTES`, `DIR_LINK_MAX`, `EXTENDS_MAX` and `CACHE_MAX_BYTES`, and the `outside-repository` `base` value are left to the architect)

## 1. Summary

A stdlib Python seed tool, `tools/source-index.py`, placed in every plant as `docs/graph/source-index.py`, derives the structure of a project's code, the code that does things and the tests that check it, without a model. It builds a file inventory (path, content hash, language, test class) and file-to-file links from Python imports (`ast`), shell and Python invocations, quoted path and directory literals, and TypeScript/JavaScript import and require specifiers resolved through `tsconfig` paths. One reverse walk over those links answers three queries: `impact` (the files that depend on the inputs, `certain` rows first, each class nearest first), `affected-tests` (the same walk filtered to the test class, plus the always-run set) and `anchors` (graph pages that cite the inputs). Every row is `certain` or `maybe` (with the reason and line of its weakest link); the `maybe` rows every input reaches alike, the opaque holders and their dependents, are the floor, listed once and apart after the input's own rows; what the tool cannot answer makes the answer `incomplete`, with a reason and one action per query: "check by hand", "run the full suite", "review by hand". The index is derived, safe to delete, never committed, and rebuilt whenever its key changes, a graft or another Python version included (ADR-0029). The rules for "what is code", "where does the plant end" and "how a page cites a path" have one home each, shared with `code-anchor.py` and `growth-audit.py`. The tool recommends; verify, tiering and canonize keep every decision.

## 2. Scope

- **In scope:**
  - The seed tool and its placement by `install.sh` and `manifest.json`; graft rebuilds the cache through its key and never carries a stale one over.
  - One shared helper module, `tools/source_paths.py`, holding the code-path rule, governed repositories, the Git boundary, blob hashing, the clean-relative predicate `relative` and the atomic write (today in `code-anchor.py`, which moves onto the helper's interface of §6 "Helper"), and the citation grammar with the one citation-resolution function whose strict plant-relative mode is `cite_problem` (today in `growth-audit.py`); `plant_walk.py` stays the plant-edge owner. `graph-lint.py` keeps its own tier-2 path rule this slice (accepted debt, grill §6 and §12 question 2).
  - File inventory from `git ls-files` plus untracked non-ignored files, per governed repository, across repositories.
  - Links: Python `ast` imports and loads by file path anchored at `__file__`; `python3|python|bash|sh <path>`, `python3 -m <module>` and `source <path>` invocations; quoted path literals and directory literals resolved by suffix; TS/JS `import`/`export from`/`require()`/`import()` with relative and `tsconfig` `paths`/`baseUrl` resolution (comment-tolerant JSON reader) and workspace package names. Each link is `certain` or `maybe` with its reason; files whose references cannot be pinned (non-literal dynamic paths, tree walks, unreadable files) are opaque. Markdown mentions are not dependency links; page citations are a separate relation read only by `anchors`.
  - Test class from the plant's `TEST_GLOBS` in `docs/graph/spec-lint.py`; an optional plant config `docs/graph/source-index.json` holding `exclude` (out of the test class), `always_run` and `global_inputs`, with seed defaults; a file may be both a test and a tool.
  - One walk and queries `impact`, `affected-tests` (default depth 3, cap 5), `anchors`, plus `build`; the floor listed apart; text and `--json`; the `incomplete` list with per-query actions.
  - A derived cache at `.cypress/source-index/` with an inner `.gitignore` of `*`, keyed as ADR-0029 decides (schema; the Python major.minor; digests of the tool and every sibling it loads; digest of the config and `TEST_GLOBS`; each governed repository's HEAD and uncommitted-code digest), written atomically.
- **Out of scope:**
  - Slice 2 of this spec, after slice 1 is measured: a symbol-definition index; git co-change history as an optional link source; a `--moved` input taking code-anchor's report (grill §12 question 3); wiring into verify, canonize, grow; `graph-lint.py` loading the helper.
  - A separate later spec: read deduplication and context pointers (overlaps adr-0010).
  - Never: tree-sitter, SQLite, a daemon, MCP, a CodeGraph integration, Svelte, Vue or other languages, a call graph, per-prompt hook use (ADR-0018), any automatic tier decision, test omission or knowledge rewrite.

## 3. User-facing behavior

Three people use the tool: an orchestrating session that plans and
verifies a change, a worker that edits code inside a brief, and a plant
owner who runs it by hand. Each calls `source-index.py` from a shell and
reads plain text, or JSON with `--json`. The tool is about the project's
code that does things, not only its tests: it says what depends on what,
which tests a change reaches, and which knowledge notes cite a file. It
writes nothing outside its own cache and makes no decision for the user.

**Ask what depends on these files.** The user names changed files, or
pipes in `git diff --name-only`, and asks `impact`. They see the code that
depends on those files, nearest first, each row with its depth, the
nearer file it was reached from, and how that last link was found. Links
come from Python imports, shell and Python invocations, quoted paths, and
TS/JS imports resolved through `tsconfig` or `jsconfig` aliases. Each row
is `certain` or `maybe`; a `maybe` row names the reason, holder and line
of its weakest link. A file whose references cannot be pinned (a dynamic
import, a whole-tree walk) is opaque and appears as a `maybe` row in every
answer. A deleted file that some reference still names is walked: its
namers are its dependents. An input under `docs/graph/` or `.cypress/` is
answered (no code depends on it) and does not make the answer incomplete.

**Ask which tests a change reaches.** `affected-tests` is the same walk
filtered to the plant's test class, plus the always-run set. Each test is
listed once, with its `via` path from an input; a changed test is listed
at depth 0. The walk never stops at a test, so a suite runner that
matches `TEST_GLOBS` (such as `run.sh`) is reached whenever any test is;
the plant moves it out of the test class with `exclude`. The always-run
set holds the tests the plant declares and the tests with no link to
code. The list is a recommendation; the session decides what runs.

**See which knowledge notes cite a file.** `anchors` lists, for each
input, the graph pages that cite it, so the user knows which facts to
re-check; a file no page cites is listed as uncited. `code-anchor.py`
prints repository-relative paths: such an input resolves under each
governed repository, or the user prefixes the repository path; one that
two repositories hold makes the answer incomplete. A citation by bare
name, and a `repo:` prefix claim, are `maybe` facts; an ambiguous bare
name makes the answer incomplete. Plans, specs and decisions are counted
as history and named with `--all`. A `--moved` input is slice 2.

**Configure the plant.** The optional `docs/graph/source-index.json`
sets `exclude` (out of the test class only), `always_run`, and
`global_inputs`. A change to a global input, such as `package.json` or
`tsconfig.json`, may affect every file, so every query is incomplete.

**Rebuild the index.** The user builds nothing first. Any query builds
the cache under `.cypress/source-index/` when it is missing, corrupt or
stale, and says so. It is rebuilt whenever its key changes: a commit, an
uncommitted code edit, a config or `TEST_GLOBS` edit, or a graft that
changes the tool. `build` forces a rebuild; deleting the cache is safe.

**When the tool cannot decide.** The tool never shows a missing link as
a missing dependency. Each answer lists its `incomplete` records (reason
and subject), for example no Git, an unknown input, or a depth cap that
cut the walk short. Then the text ends with one action: `impact` "check
by hand", `affected-tests` "run the full suite", `anchors` "review by
hand". The tool still exits normally, so a hook or brief that calls it
does not break.

## 4. Functional contracts

(Authored by `architect`. Reviewed by `tester` for testability.)

Every contract runs `python3 docs/graph/source-index.py` from the root of a
synthetic plant: a Git work tree built from synthetic files, with the tool and
the files the installer places beside it (`source_paths.py`, `plant_walk.py`,
`frontmatter.py`) in `docs/graph/`, and a `docs/graph/spec-lint.py` whose only
content of interest is its `TEST_GLOBS` list. Paths in every answer are
plant-relative, as §6 "Inputs" normalizes them. "The answer" is the
`--json` document of §6; the text view renders the same document. A row is
`certain` or `maybe` and an answer is complete or `incomplete` by §6 "Walk".
Every query exits 0 (`USAGE_REFUSED` is the one exit 2).

### Index and cache

### Contract: BUILD_INVENTORIES_THE_CODE_OF_EVERY_GOVERNED_REPOSITORY
- **Given:** a plant work tree holding a tracked file, an untracked file that
  is not ignored, an ignored file, a node under `docs/graph/`, a file under
  `.cypress/`, a `__pycache__/x.pyc` and a `y.py.bak-20261001-091322`, a
  directory holding its own `.cypress/seed.json` (a nested plant) with a file
  in it, and a nested Git work tree that one node names in `repo:`
- **When:** `source-index.py build --json` runs
- **Then:** the inventory lists exactly the tracked and the untracked
  non-ignored code files of both repositories, as plant-relative paths, each
  with its Git blob hash, its language and its test class (§6)
- **And:** no ignored file, no path under `docs/graph/` or `.cypress/`, no
  build or backup file and no file of the nested plant is listed, because the
  code-path rule is the one `code-anchor.py` applies and the plant edge is the
  one `plant_walk.py` applies

### Contract: BUILD_IS_DETERMINISTIC
- **Given:** the plant of the contract above
- **When:** `source-index.py build` runs twice, with the cache removed between
  the runs
- **Then:** the two `.cypress/source-index/index.json` files are byte-identical
- **And:** neither holds the absolute path of the plant root, so a copy of the
  plant in another directory answers from the copied cache unchanged

### Contract: CACHE_WRITTEN_SELF_IGNORED
- **Given:** a plant that holds `.cypress/` and no `.cypress/source-index/`,
  and whose `.gitignore` does not name `.cypress/`
- **When:** any query runs
- **Then:** `.cypress/source-index/index.json` exists, and
  `.cypress/source-index/.gitignore` holds exactly `*` and a newline
- **And:** `git status --porcelain` shows nothing under `.cypress/source-index/`,
  and the answer's cache status is `built`

### Contract: CACHE_REUSED_WHILE_THE_KEY_HOLDS
- **Given:** a cache built by a query, and no commit, checkout, file edit or
  config edit since
- **When:** a second query runs
- **Then:** the answer's cache status is `reused`, and the cache file's bytes
  and modification time are unchanged

### Contract: CACHE_REBUILT_WHEN_THE_KEY_CHANGES
- **Given:** a cache built by a query, then one of: a new commit in a governed
  repository; an edit to an uncommitted code file; an edit to
  `docs/graph/source-index.json`; an edit to the `TEST_GLOBS` list of
  `docs/graph/spec-lint.py`; a cache whose key names another Python
  major.minor than the interpreter that runs the query
- **When:** the next query runs
- **Then:** the answer's cache status is `rebuilt`, and its result equals the
  result a query gives after the cache directory is deleted

### Contract: GRAFT_REBUILDS_THE_CACHE
- **Given:** a plant whose cache was built by a `docs/graph/source-index.py`
  holding other bytes than the seed's `tools/source-index.py` (an older seed)
- **When:** `install.sh` runs over the plant, as graft runs it in its copy,
  and then a query runs
- **Then:** the answer's cache status is `rebuilt`, because the key holds the
  digest of the tool and every sibling it loads, and the installer neither
  deletes nor rewrites the cache

### Links

### Contract: LINK_PYTHON_IMPORT_CERTAIN
- **Given:** `pkg/a.py` holding `from . import b`, `from .sub import c`,
  `import pkg.d`, `import json`, `importlib.import_module("pkg.e")`, and three
  loads by file path (§6 "Links"): `_ilu.spec_from_file_location("f",
  Path(__file__).resolve().parent / "f.py")` after `import importlib.util as
  _ilu`, `importlib.util.spec_from_file_location("h", Path(__file__).parent.parent
  / "tools" / "h.py")`, and `runpy.run_path(os.path.join(os.path.dirname(
  os.path.abspath(__file__)), "g.py"))`, with `pkg/b.py`, `pkg/sub/c.py`,
  `pkg/d.py`, `pkg/e.py`, `pkg/f.py`, `pkg/g.py` and `tools/h.py` in the
  inventory
- **When:** `build --json` runs
- **Then:** the links held by `pkg/a.py` are exactly seven `certain` `import`
  links, found `exact` to `pkg/b.py`, `pkg/sub/c.py`, `pkg/f.py`, `pkg/g.py`
  and `tools/h.py` and `resolved` to `pkg/d.py` and `pkg/e.py`, each with its
  line
- **And:** `json` yields no link and no record (an import that names no
  inventory file is external), and no load argument's string yields a second,
  `path-literal` link

### Contract: LINK_SHELL_INVOCATION_CERTAIN
- **Given:** `tests/test-x.sh` holding `python3 -B "$ROOT/tools/x.py"`,
  `bash tests/helpers/plant.sh`, `source "$ROOT/tests/lib.sh"`,
  `. ./common.sh` and `python3 -m pkg.mod`, each target in the inventory; and,
  in a plant whose root repository holds `run.sh` and whose nested governed
  repository `Cypress/` holds `Cypress/tools/y.py`, `run.sh` holding
  `python3 Cypress/tools/y.py`
- **When:** `build --json` runs
- **Then:** `tests/test-x.sh` holds one `certain` `invoke` link to each of
  the five targets (`pkg.mod` resolved as a Python module), and `run.sh` holds
  one to `Cypress/tools/y.py`, found by the order of §6 "Resolution"

### Contract: LINK_PATH_LITERAL_AND_DIRECTORY_ARE_MAYBE
- **Given:** `tools/t.py` holding `(Path(__file__).resolve().parent /
  "frontmatter.py").read_text()` beside `tools/frontmatter.py` (an anchored
  path that no load call takes), the string
  `"$SEED_ROOT/templates/k/lint.py"` with `templates/k/lint.py` in the
  inventory, and the string `"templates/k/"` with `templates/k/lint.py` and
  `templates/k/a.json` the inventory files under it; and a Markdown file
  outside `docs/graph/` that names `tools/t.py` in backticks
- **When:** `build --json` runs
- **Then:** `tools/t.py` holds `maybe` `path-literal` links with reason
  `path-literal` to `tools/frontmatter.py` and `templates/k/lint.py`, and
  `maybe` links with reason `directory` to `templates/k/lint.py` and
  `templates/k/a.json`, each with its line
- **And:** the Markdown file holds no link

### Contract: LINK_TS_SPECIFIER_CERTAIN
- **Given:** a `tsconfig.json` holding `//` and `/* */` comments, a trailing
  comma and `"paths": {"@/*": ["./src/*"]}`, and `src/app/x.ts` holding
  `import { a } from "./a"`, `import type { D } from "@/lib/db"`,
  `export * from "../util/u.js"`, `const r = require("./r")`,
  `await import("./lazy")`, an `await import(` that ends its line with the
  specifier `"@/lib/late"` on the next line and `)` on the line after,
  `import "node:fs"` and `import React from "react"`, with `src/app/a.ts`,
  `src/lib/db/index.ts`, `src/util/u.ts`, `src/app/r.js`, `src/app/lazy.tsx`
  and `src/lib/late.ts` in the inventory
- **When:** `build --json` runs
- **Then:** `src/app/x.ts` holds one `certain` `import` link, found
  `resolved`, to each of the six files, and no `opaque` record (the line join
  of §6 "Links")
- **And:** `node:fs` and `react` yield no link and no record (a bare package
  specifier that names no workspace package is external)

### Contract: UNPINNED_REFERENCE_RECORDED_WITH_ITS_REASON
- **Given:** source files holding, one each: `import(name)` with a non-literal
  argument; `os.walk(root)` over a variable; a `.py` file that does not parse;
  an alias import under a tsconfig whose `extends` names a file the inventory
  lacks; `import "./missing"`; `import "@/nope"` under the paths of the
  contract above; `import "./.next/types/routes.d.ts"` where Git ignores
  `.next/`; `import css from "./a.css?raw"`; and a Python `import app.main`
  where two inventory files end in `/app/main.py`
- **When:** `build --json` runs
- **Then:** the first four holders are `opaque` records with the reasons
  `dynamic-nonliteral`, `walks-tree`, `unreadable` and
  `alias-config-unavailable`; the next four references are `unresolved`
  records with the reasons `relative-no-file`, `alias-no-file`, `generated`
  and `asset`, each with the base path it names; and the ambiguous import is
  two `maybe` links with reason `ambiguous`, one to each candidate
- **And:** none of them is a `certain` link

### Test class

### Contract: TESTS_ARE_THE_PLANTS_TEST_GLOBS
- **Given:** a plant whose `docs/graph/spec-lint.py` sets `TEST_GLOBS =
  ["checks/**/*.*"]` and that holds `checks/c.sh`, `tests/t_test.py` and
  `src/s.py`
- **When:** `build --json` runs
- **Then:** `checks/c.sh` is the one inventory record whose test class is
  `test`, because the plant's `TEST_GLOBS` (the owner fact spec-lint already
  reads) is the one declaration of where tests are

### Contract: PLANT_CONFIG_REPLACES_EACH_DEFAULT_KEY
- **Given:** `docs/graph/source-index.json` holding `exclude:
  ["tests/experimental/**"]` and `always_run: ["checks/walk-*.sh"]` and no
  `global_inputs` key, under `TEST_GLOBS = ["tests/**/*.*", "checks/**/*.*"]`,
  and a plant holding `tests/experimental/e.ts`, `checks/walk-tree.sh` and
  `package.json`
- **When:** `affected-tests package.json --json` runs
- **Then:** `tests/experimental/e.ts` is in the inventory with test class
  `code`, `checks/walk-tree.sh` is in `always_run` with reason `declared`, and
  `incomplete` holds a `global-input` record for `package.json`, because a key
  the file sets replaces that key's default and a key it omits keeps it

### Walk

### Contract: WALK_NEAREST_FIRST_ONCE
- **Given:** `a.py` imported by `b.py` and by `c.py`, `b.py` imported by `c.py`
  and invoked by `d.sh`
- **When:** `impact a.py --json` runs
- **Then:** `dependents` lists `b.py` and `c.py` at depth 1 and `d.sh` at
  depth 2, in that order, each `certain`, with the nearer file it was reached
  from and that link's kind, how it was found and its line
- **And:** `c.py` appears once, at its nearest depth, and the answer is
  complete (`incomplete` is empty)

### Contract: WALK_CHAIN_IS_ITS_WEAKEST_LINK
- **Given:** `a.py`; `b.py` holding the path literal `"a.py"`; and `c.py`
  importing `b.py`
- **When:** `impact a.py --json` runs
- **Then:** `b.py` is a depth-1 `maybe` row with reason `path-literal` at
  `b.py` and its line, and `c.py` a depth-2 `maybe` row carrying that same
  reason, holder and line
- **And:** no row is `certain`, because a chain is as strong as its weakest
  link

### Contract: WALK_FLOOR_LISTED_APART_AFTER_THE_INPUT_ROWS
- **Given:** `a.py` imported by `b.py` and named by the path literal `"a.py"`
  in `c.py`, with `d.py` importing `b.py`; `o.py` holding `os.walk(root)` over
  a variable, imported by `p.py`; `q.py` holding `import_module(name)` over a
  variable and itself importing `a.py`; and `z.py`, which no file depends on
- **When:** `impact a.py --json` runs, then `impact z.py --json`
- **Then:** for `a.py`, `dependents` lists `b.py` and `q.py` (depth 1) and
  `d.py` (depth 2), each `certain`, then `c.py` (depth 1), `maybe`; and
  `floor` lists `o.py` at depth 1, `maybe` with reason `walks-tree` at
  `o.py` and its line, then `p.py` at depth 2 carrying that same reason,
  holder and line
- **And:** `q.py` is in `dependents` only, because a file the input part of the
  walk reaches is never a floor row; the `floor` of `z.py` equals the `floor`
  of `a.py` with `q.py` added and `dependents` empty; and the text view prints
  the `dependents` rows, then `FLOOR_LINE`, then the `floor` rows

### Contract: WALK_DELETED_INPUT_REACHES_ITS_NAMERS
- **Given:** `src/x.ts` holding `import { v } from "@/lib/gone"` under
  `"paths": {"@/*": ["./src/*"]}`, no `src/lib/gone.ts` in the plant, and a
  test `tests/x.test.ts` importing `src/x.ts`
- **When:** `affected-tests src/lib/gone.ts --json` runs
- **Then:** `tests` lists `tests/x.test.ts` at depth 2, `certain`, via
  `src/lib/gone.ts`, `src/x.ts`, because the stored `alias-no-file` reference
  of `src/x.ts` names the input
- **And:** `incomplete` is empty

### Contract: INPUT_FORMS_RESOLVED
- **Given:** a plant whose nested governed repository `Cypress/` holds
  `Cypress/tools/x.py`, imported by `Cypress/tools/y.py`; and the inputs
  `tools/x.py` (repository-relative), `<plant root>/Cypress/tools/x.py`
  (absolute), `./Cypress/tools/x.py` and `docs/graph/nodes/n.md`
- **When:** `impact <those four> --json` runs
- **Then:** `inputs` lists `Cypress/tools/x.py` and `docs/graph/nodes/n.md`,
  the first with status `walked`, the second with status `not-code`;
  `dependents` lists `Cypress/tools/y.py`; and `incomplete` is empty, because a
  `not-code` input is answered (no code depends on it) and a
  repository-relative input that one governed repository holds is that file

### Contract: WALK_INCOMPLETE_NAMES_REASON_AND_ACTION
- **Given:** one of: an input matching `global_inputs` (§6 default or the
  plant's); an input that no repository holds and no stored reference names; a
  repository-relative input that two governed repositories hold; a chain of
  five files queried with `--depth 3`; a plant config the tool refused; no
  `git` on PATH; and, for `affected-tests` only, a `TEST_GLOBS` that is absent
  or matches no inventory file
- **When:** each query that §6 "Incomplete" lists for that reason runs on it
- **Then:** `incomplete` holds one record whose reason is the one §6
  "Incomplete" assigns (`global-input`, `input-not-found`, `ambiguous-input`,
  `depth-cap`, `config-refused`, `git-unavailable`, `no-test-declaration`,
  `no-test-files`), naming its subject; the rows the walk did reach are still
  listed; and the text view ends with that query's action line (`impact`
  "check by hand", `affected-tests` "run the full suite", `anchors` "review by
  hand")
- **And:** the depth-cap record names the file at depth 3 whose dependent the
  walk did not reach, and the same chain with `--depth 5` is complete

### Affected tests

### Contract: AFFECTED_TESTS_ARE_THE_WALK_FILTERED
- **Given:** `lib.py` imported by `tool.py`, invoked by the test `tests/t.sh`;
  the test `tests/lint.py` importing `lib.py`, itself invoked by the test
  `tests/test-lint.sh`; the test `tests/u_test.py` named as an input beside
  `lib.py`
- **When:** `affected-tests lib.py tests/u_test.py --json` runs
- **Then:** `tests` lists `tests/u_test.py` at depth 0, `tests/lint.py` at
  depth 1, `tests/t.sh` and `tests/test-lint.sh` at depth 2, each `certain`
  with its `via` path from an input, and no non-test file
- **And:** the text view ends with the recommendation line of §6, never a
  claim that only these tests are affected

### Contract: AFFECTED_ALWAYS_RUN_LISTED_APART
- **Given:** a shell test with no link to any `code` file, a test matched by
  the plant's `always_run`, a test holding a `dynamic-nonliteral` reference
  and no other link, a JSON fixture and a Markdown fixture in the test class,
  and an input that no link of the first two reaches
- **When:** `affected-tests <input> --json` runs
- **Then:** the first two tests are in `always_run` with the reasons
  `no-code-edge` and `declared`, the opaque test is in `floor` as a depth-1
  `maybe` row with reason `dynamic-nonliteral`, and neither fixture is in any
  list, because `no-code-edge` takes only files of a link-bearing language
- **And:** a test that is both reached and declared is in `tests` only

### Anchors

### Contract: ANCHORS_NAME_CITING_PAGES_OR_UNCITED
- **Given:** a node `docs/graph/nodes/n.md` citing `` `src/a.py:12` `` and
  `` `src/a.py#run` ``, a leaf citing `` `../../src/a.py` `` page-relatively,
  a node with `repo: src/a.py`, a node with `repo: src/` and one with
  `repo: src`, a plan, a spec and a decision page each citing
  `` `src/a.py` ``, and a file `src/b.py` no page cites
- **When:** `anchors src/a.py src/b.py --json` runs
- **Then:** `src/a.py` lists in `facts` the node (with line 12 and with no
  line) and the leaf as `certain` `backtick` facts, the `repo: src/a.py` node
  as a `certain` `repo` fact and the `repo: src/` node as a `maybe` `repo`
  fact with reason `repo-prefix`; it counts the plan, spec and decision pages
  in `history` without naming them
- **And:** the `repo: src` node claims nothing (a `repo:` with no `/` names a
  repository root), and `src/b.py` is listed as `uncited`
- **And:** with `--all`, `history` names its three pages

### Contract: ANCHORS_BASENAME_IS_MAYBE_AMBIGUOUS_IS_INCOMPLETE
- **Given:** a node citing the bare name `` `run.py` `` with `a/run.py` the one
  inventory file of that name, and a node citing the bare name `` `lint.py` ``
  with `a/lint.py` and `b/lint.py` in the inventory
- **When:** `anchors a/run.py a/lint.py --json` runs
- **Then:** `a/run.py` lists the first node as a `maybe` fact with reason
  `basename`; `a/lint.py` does not list the second node; and `incomplete`
  holds one `ambiguous-citation` record naming the page, the citation and
  both candidates

### Output

### Contract: OUTPUT_CARRIES_NO_RAW_CONTROL
- **Given:** `a.py` and three tracked Python files that each hold `import a`,
  whose names hold, one each, an ESC character (U+001B), a U+202E right-to-left
  override and the byte 0xFF (not valid UTF-8)
- **When:** `impact a.py` runs, once as text and once with `--json`
- **Then:** the exit is 0 both times, and every byte of the text view is
  printable ASCII or a newline, each of the three characters shown as `?`
- **And:** the `--json` document is ASCII, and its `dependents` list the three
  files, whose paths decode to the names Git reports (0xFF as the
  `surrogateescape` code point U+DCFF), because the text view replaces and the
  JSON view escapes every character outside printable ASCII (§5 Security)

### Integration

### Contract: SOURCE_INDEX_IS_PLACED
- **Given:** a fresh target directory
- **When:** `install.sh all --project-dir <target>` runs
- **Then:** `docs/graph/source-index.py`, `docs/graph/source_paths.py` and
  `docs/graph/plant_walk.py` exist, each byte-identical to its seed source in
  `tools/`
- **And:** before any query runs, neither `.cypress/source-index/` nor
  `docs/graph/source-index.json` exists, because the installer writes neither:
  only a query builds the cache and only the plant writes its config
- **And:** `python3 docs/graph/source-index.py build` then exits 0 in the fresh
  plant

## 5. Non-functional requirements

- **Performance:** a full build over a repository of 5,000 inventoried files
  finishes within 5 s and 64 MB peak RSS on the owner's development machine.
  Evidence (the gap scouts' throwaway builds, 2026-10-07): 0.15 s and 15 MB
  RSS on Vivid; 3.8 s on a 4,865-file llama.cpp tree, with import extraction
  only. The 5 s budget is unverified for path-literal, directory and shell
  extraction at 5,000 files. A query that reuses the cache answers within 1 s
  on the seed-sized plant. Measured once at verify, not gated (grill §10).
- **Security:** read-only over the repositories: the tool parses Python with
  `ast` and never imports, executes or `exec`s repository code; it reads a
  symlink as its link text, never its target; Git runs through the helper's
  one boundary (locator variables dropped, optional locks and fsmonitor off,
  no lazy fetch, a timeout per call). It writes only under
  `.cypress/source-index/`, relative to a descriptor opened without following
  a symlink, through an exclusive temp file and an atomic replace, and never
  creates `.cypress/`. The cache is untrusted input: a document that breaks
  the §6 shape is rebuilt, never trusted. The text view replaces every
  character outside printable ASCII and the path alphabet with `?`, so a path
  cannot inject terminal control sequences into a hook or brief.
  Added by `security` (2026-10-07), each tied to a §7 row:
  - Paths are text. A path from repository content (an import, invoke or
    path literal, a tsconfig `paths`, `baseUrl` or `extends` entry), from an
    input, a page citation or the cache is normalized lexically and matched
    against the inventory; `..` past a root makes it `outside-repository` or
    `outside-plant`. The tool never opens, stats or hands to Git a path built
    from such text, so none of them can make it read outside the governed
    repositories.
  - Reads are bounded. The tool reads only inventory files, `docs/graph/`
    pages, the plant config and `spec-lint.py`, each opened with
    `O_NOFOLLOW | O_NONBLOCK` and read only when `fstat` shows a regular file
    whose real path lies inside its repository (`FILE_NOT_REGULAR`). A
    link-bearing file above `FILE_MAX_BYTES` is not parsed, and every parse of
    untrusted bytes (`ast`, the JSONC reader, `json`, `ast.literal_eval`)
    treats `RecursionError`, `MemoryError` and `ValueError` as a named
    failure, never a crash (`INPUT_EXHAUSTS_A_PARSER`). Every extraction
    regex runs on one line at a time, or on one TS/JS line joined with at
    most `JOIN_MAX` following lines (§6 "Links"), and has no nested or
    overlapping quantifier, so its time is linear in the text it reads. Links stay linear in the
    references (`DIRECTORY_LITERAL_TOO_WIDE`); a tsconfig `extends` chain is
    bounded (`TSCONFIG_EXTENDS_CYCLE`).
  - Git gets no path in argv from file content. Paths go through
    `--stdin -z`, each written as `./<path>` so none reads as pathspec magic,
    or after `--`; a Git exit code that
    is an answer (`check-ignore` exits 1 when nothing is ignored) is not a
    failure (`GIT_PATH_ARGUMENT`). Git output is read with `-z` and decoded
    with `surrogateescape`.
  - The cache directory is created by `mkdir` relative to the `.cypress/`
    descriptor (`mkdir` joins the descriptor-relative calls the platform must
    offer) and opened `O_NOFOLLOW | O_DIRECTORY`; the inner `.gitignore` is
    written before `index.json` (`CACHE_IGNORE_ALTERED`).
  - The cache shape check covers content as well as form: every path a clean
    relative path with no NUL, every link and record endpoint an inventory
    path, every enum one §6 lists, and the file at most `CACHE_MAX_BYTES`.
    Whoever can write `.cypress/` can already change the code, so a forged
    cache that passes is an observation, not a finding; the cache is still
    never a path source.
  - Output carries no raw control. The `?` replacement covers every string
    the text view takes from repository content (paths, references,
    citation text, a refused config's detail), and `--json` is written with
    `ensure_ascii`, so neither view emits a raw control, bidi-override or
    lone-surrogate character (`NON_UTF8_PATH`).
  - No file content is echoed. A record's `reference` holds the specifier or
    the script argument only, never the rest of its line, so a token beside a
    reference (`--token "$T"`, a key in the same string list) never reaches
    the cache or an answer.
  - The answer is a recommendation over cooperative code. An author who
    wants to hide a link can (`getattr(importlib, "import_" + "module")`),
    so no gate may read a file's absence from `dependents` or `tests` as
    proof that it is unaffected.

- **Privacy:** the cache holds paths, hashes, link targets and reason codes,
  never file content.
- **Reliability:** every query and `build` exits 0 with an answer, including
  when Git is absent (`USAGE_REFUSED` excepted); a failed write leaves the old
  cache whole; a full rebuild is the oracle, so no incremental update exists.
- **Cost:** no model call. The text view lists at most `TEXT_MAX_ROWS` rows
  per list and counts the rest on a more-line; `--all` lifts the cap; `--json`
  lists every row.
- **Compatibility:** stdlib Python 3.12 or newer, the version the seed's
  gate pins (`.github/workflows/gate.yml` line 38) and the one the placed
  `graph-lint.py` already needs (a backslash inside an f-string expression,
  line 341, parses from 3.12), and Git; no third-party package, no `sqlite3`, no
  tree-sitter. A platform without descriptor-relative file calls gets
  answers and no cache, never a path-string fallback.

Cross-link: the seed's operating constraints are grill §4 of
`docs/plans/grill-8.1.0-source-index.md`.

## 6. Data shapes

`tools/source-index.py` is the one home of every constant below except those
marked "helper", whose home is `tools/source_paths.py`.

```yaml
constants:
  INDEX_SCHEMA: "cypress.source-index/1"      # cache document
  ANSWER_SCHEMA: "cypress.source-index.answer/1"
  DEFAULT_DEPTH: 3
  MAX_DEPTH: 5
  TEXT_MAX_ROWS: 40              # rows per list in the text view; --all lifts it
  LITERAL_MAX: 255               # longest string read as a path literal
  JOIN_MAX: 3                    # most following lines a TS/JS line ending in an open call takes (§6 "Links")
  FILE_MAX_BYTES: 1048576        # 1 MiB; a larger link-bearing file is not parsed (INPUT_EXHAUSTS_A_PARSER)
  DIR_LINK_MAX: 200              # most inventory files one directory literal links (DIRECTORY_LITERAL_TOO_WIDE)
  EXTENDS_MAX: 16                # longest tsconfig `extends` chain (TSCONFIG_EXTENDS_CYCLE)
  CACHE_MAX_BYTES: 67108864      # 64 MiB; a larger index.json is neither read nor written
  CACHE_DIR: ".cypress/source-index"
  CACHE_NAME: "index.json"
  CACHE_IGNORE: "*\n"            # the inner .gitignore, byte for byte
  CONFIG_PATH: "docs/graph/source-index.json"
  TEST_DECLARATION: "docs/graph/spec-lint.py: TEST_GLOBS"
  SIBLINGS: ["source_paths.py", "plant_walk.py", "frontmatter.py"]   # loaded by file path; digested in the key
  NOT_CODE, NOISE_DIR, NOISE_NAME, GIT_LOCATORS, GIT_TIMEOUT: helper   # moved from code-anchor.py, unchanged
  DIR_FD_CALLS: helper           # moved from code-anchor.py, with `mkdir` added: {open, stat, unlink, rename, mkdir}
  CITATION_RE, MISSING_CITATION, MALFORMED_CITATION: helper             # moved from growth-audit.py, unchanged
  TEMP_PREFIX: ".tmp-source-index-"   # the cache's exclusive temp files
  FLOOR_LINE: "Floor: {n} maybe row(s) every input reaches (opaque holders and their dependents):"
  RECOMMEND_LINE: "Recommendation only: the tests above and the always-run set, never only these; verify decides what runs."
  ACTION_LINE:                   # the closing text line of an incomplete answer
    build: "Incomplete: check by hand ({reasons})."
    impact: "Incomplete: check by hand ({reasons})."
    affected-tests: "Incomplete: run the full suite ({reasons})."
    anchors: "Incomplete: review by hand ({reasons})."
```

### Helper

`tools/source_paths.py` is a library module with no CLI, loaded by file path
like `frontmatter.py`. It takes from `code-anchor.py` the Git boundary, the
code-path rule, governed repositories, `content_state`, the clean-relative
predicate `relative` and the atomic write, and from `growth-audit.py` the
citation grammar and its one resolution function (§2). The move changes the
interface in the four places below and moves `relative` unchanged (plan
increments 2, 8 and 9); each is proved by
`tests/test-code-anchor.sh` and `tests/test-growth-audit.sh` with no assertion
edited, because no code-anchor or growth-audit message or verdict changes:
- `git(repo, *args, input=None, ok=(0,))` takes optional stdin bytes
  (`DEVNULL` when none) and the exit codes that are answers; any other exit
  raises as today. Code-anchor's calls keep the defaults.
- `content_state(repo, path)` still hashes a symlink's link text (`lstat`,
  `readlink`). Any other path is opened `O_RDONLY | O_NOFOLLOW | O_NONBLOCK`,
  nothing is read unless `fstat` shows a regular file, and the content is
  hashed as a stream under the blob header of the `fstat` size, so a file
  above `FILE_MAX_BYTES` is hashed without being held whole. The hashes equal
  those of today's whole-file read; a failed open, or a read whose length
  differs from that size, is None (cannot be hashed), which code-anchor
  already counts as moved. One hashing path serves both tools.
- The directory opener and the atomic write take the root, the directory
  parts, the target name, the temp prefix and the name a refusal shows as
  parameters. The opener opens each part `O_NOFOLLOW | O_DIRECTORY` relative
  to the one before and, when asked, creates the last with `mkdir`
  (`DIR_FD_CALLS` gains `mkdir`). Code-anchor passes `.cypress`,
  `anchor.json` and `.tmp-anchor-`, so its messages read as today; the tool
  passes `.cypress` then `source-index` (created), `.gitignore` or
  `index.json`, and `TEMP_PREFIX`.
- No helper function reads a module-global root; each takes the root as a
  parameter (code-anchor passes its `ROOT`, `Path.cwd()`).
- `relative(path) -> bool` moves unchanged: true for a clean path inside the
  directory it is relative to. Code-anchor's `anchor_problem` and the tool's
  cache shape check use it. The tool's input normalizer is another function,
  `plant_relative`, in `source-index.py` (§6 "Inputs").

### Inventory record

```yaml
inventory_record:
  path:     { type: string, plant-relative, posix }
  repo:     { type: string, governed repository path, "." for the root }
  hash:     { type: string, git blob sha1 of the content; a symlink hashes its link text }
  language: { enum: [python, shell, typescript, javascript, json, other] }
            # by extension: .py; .sh .bash; .ts .tsx .mts .cts; .js .jsx .mjs .cjs; .json;
            # an extensionless file by its shebang (python*, bash, sh); else other
  test:     { enum: [test, code] }
```
The inventory is the set of paths each governed repository lists in
`git ls-files` plus `git status --untracked-files=all` (ignored files left
out), kept when `source_paths.is_code` holds, and dropped when any directory
on the way is foreign by `plant_walk.is_foreign`. A record's test class is
`test` when a `TEST_GLOBS` pattern matches it and no `exclude` pattern does;
`exclude` changes only the test class, so an excluded file keeps its links.
The `TEST_GLOBS` match uses spec-lint's `test_files` semantics, whose home
stays `templates/knowledge-graph/spec-lint.py`: patterns are `pathlib` globs
from the plant root, and files under a `SKIP_DIRS` directory (`.git`,
`node_modules`, `.venv`, `venv`, `__pycache__`, `dist`, `build`, `target`,
`.next`) or under the specs directory are never tests. Links are read from
`python`, `shell`, `typescript` and `javascript` files; `json` and `other`
files are targets only.

### Link, opaque and unresolved records

```yaml
link:                          # the holder depends on the target
  holder: { type: string, inventory path holding the reference }
  target: { type: string, inventory path }
  kind:   { enum: [import, invoke, path-literal] }
  link:   { enum: [certain, maybe] }
  found:  { enum: [exact, resolved,                                   # certain
                   path-literal, directory, ambiguous, workspace-package] }  # maybe: the reason
                   # `named` is never stored: it is the walk's step through an unresolved record
  line:   { type: int, 1-based line of the reference in the holder }
opaque:                        # a holder whose reference may name any file
  holder:    { type: string, inventory path }
  line:      { type: int, or null for unreadable }
  reference: { type: string, as written, cut to LITERAL_MAX }
  reason:    { enum: [dynamic-nonliteral, walks-tree, unreadable, alias-config-unavailable] }
unresolved:                    # an import or invoke reference that names a path no inventory file holds
  holder:    { type: string, inventory path }
  line:      { type: int }
  kind:      { enum: [import, invoke] }
  reference: { type: string, as written, cut to LITERAL_MAX }
  reason:    { enum: [relative-no-file, alias-no-file, outside-repository, generated, asset] }
  base:      { type: string|null, plant-relative path the reference names before probing,
               any `?` query cut; null for outside-repository, so no host path enters the cache }
```
- `import`: Python `import` / `from … import` / `importlib.import_module("<literal>")`
  and a load by file path (below);
  TS/JS `import … from`, side-effect `import`, `export … from`, `require("…")`,
  `import("…")`. Type-only imports and `vi.mock("…")` are ordinary imports.
- Load by file path (Python, read by `ast`): a call whose callee's last name
  is `spec_from_file_location` (its second positional argument or `location=`)
  or `run_path` (its first positional argument or `path_name=`), whose
  argument is an anchored path, written in one of two shapes, exactly:
  - `P(__file__)`, then at most one `.resolve()` or `.absolute()`, then one or
    more `.parent`, then one or more `/ "<literal>"` operands; `P` is the name
    the module binds to `pathlib.Path` (`Path`, `pathlib.Path`, or an
    `import … as` alias such as `_Path`).
  - `os.path.join(D, "<literal>", …)` with every argument after `D` a literal,
    where `D` is `os.path.dirname(…)` nested one or more times around
    `__file__`, `os.path.abspath(__file__)` or `os.path.realpath(__file__)`.
  The seed's tools load their siblings in the first shape
  (`tools/code-anchor.py` 54-55, `tools/corpus-match.py` 53-54,
  `tools/graft-audit.py` 168-169). An anchored path held in a variable, a base
  other than `__file__`, or one that no load call takes is not a load: its
  strings stay `path-literal` references, and a load call whose argument is
  not anchored keeps the rules below. The link's line is the line where the
  argument starts.
- Line join (TS/JS only): a line whose code, comments stripped, ends in an
  open `import(`, `require(` or `vi.mock(` is read joined with the following
  lines, up to `JOIN_MAX` of them, until one holds the closing `)`; blank lines
  are skipped and not counted. The joined text is read once, as one line at
  the line of the call, and its lines are not read again on their own. A call
  whose argument is still open after `JOIN_MAX` lines is read as written, so a
  non-literal argument stays `dynamic-nonliteral`. Python needs no join (`ast`
  reads the whole file); shell has no such form.
- `invoke`: in a shell file, a word `python3`, `python`, `bash` or `sh` outside
  a comment (a command word or an argument, as in `add_step python3 X`), after
  any `-X` option words, followed by a script argument; `python3 -m <module>`,
  whose module resolves by the Python module rule; and `source X` / `. X`.
  `-c` and `-` arguments are inline code, not links.
- A quoted string that is an `import` specifier or an `invoke` argument is
  read as that reference only, never also as a `path-literal`, so it yields one
  link, or one record, and no second one.
- `path-literal`: any other quoted string (single, double, or a backtick
  string without `${`) of at most `LITERAL_MAX` characters with no
  whitespace and no `://`, in a Python, shell or TS/JS file. It is a `maybe`
  link with reason `path-literal` to the inventory file it resolves to, or,
  when it holds a `/` and resolves to a directory holding inventory files, a
  `maybe` link with reason `directory` to each of them. A string that resolves
  to nothing is not a reference and yields nothing: no `unresolved` or `opaque`
  record ever comes from a path literal.
- `certain` links: found `exact` when a relative import, a load by file path
  or an `invoke` argument names the target as written, relative to the holder
  or the repository root (a `path-literal` is never `certain`, wherever it
  resolves);
  found `resolved` when a lookup rule found it (Python module search, a
  `/`-suffix, extension or index probing, `.js` to `.ts`, tsconfig
  `paths`/`baseUrl`, a target in another governed repository).
- `maybe` links: `path-literal` and `directory` as above; `ambiguous`, one
  link to each candidate of a Python module that several inventory files end
  in; `workspace-package`, one link to each inventory file under the directory
  of a tracked `package.json` whose `name` equals a bare TS/JS specifier.
- Opaque reasons: `dynamic-nonliteral`, an `import()`, `require()`,
  `import_module`, `spec_from_file_location`, `run_path` or `invoke` whose
  argument is no anchored path and holds no literal that resolves; `walks-tree`, a call of `os.walk`,
  `os.scandir`, `os.listdir`, `.rglob(`, `.glob(`, `glob.glob`, `readdirSync`
  or `readdir`, or a `find` or `git ls-files` command, whose root argument is
  not a literal (a literal root is a `directory` link); `unreadable`, a file
  of a link-bearing language that cannot be read, decoded as UTF-8 or parsed
  (`ast` SyntaxError); `alias-config-unavailable`, a non-relative, non-package
  specifier under a tsconfig whose `extends` chain names a file the inventory
  lacks, or that the JSONC reader rejects.
- Unresolved records come only from `import` and `invoke` references.
  Reasons: `relative-no-file`, a relative specifier, a load by file path or an
  `invoke` path that resolves to no file; `alias-no-file`, a specifier an alias matched
  with no file behind it; `outside-repository`, a target outside every
  governed repository (absolute, or `..` past the plant root); `generated`, a
  target Git ignores (`git check-ignore`); `asset`, a relative or alias
  specifier with a `?` query or a `.css .scss .sass .less .svg .png .jpg .jpeg
  .gif .webp .ico .woff .woff2 .html .md` extension (the extension read after
  the query is cut). The asset's `base` is the path it names with the query
  cut (`"./a.css?raw"` in `src/app/x.ts` is `src/app/a.css`). An asset is
  never probed: when its base is an inventory path it is a `certain` `import`
  link found `exact`, otherwise an `asset` record.
- Git reads: the helper's `git` takes the set of exit codes that are answers
  (`{0}` by default; `{0, 1}` for `check-ignore`, whose exit 1 means nothing
  is ignored) and optional stdin bytes. `generated` is asked of Git once per
  repository with `check-ignore --stdin -z`, after every path outside that
  repository has become `outside-repository`, each path written as `./<path>`
  (`GIT_PATH_ARGUMENT`).

**Resolution** (one order, tried top-down; the first hit wins; candidates are
plant-relative inventory paths of any governed repository):
- Python module `a.b`: relative imports from the holder's package; otherwise
  `<holder dir>/a/b.py`, `<holder dir>/a/b/__init__.py`, `<repo>/a/b.py`,
  `<repo>/a/b/__init__.py`; for `from a.b import c` also `…/a/b/c.py`; then
  the inventory files ending in `/a/b.py` or `/a/b/__init__.py`: one is
  `resolved`, several are `ambiguous`, none is external.
- Python load by file path: the holder's directory, one directory up for each
  `.parent` or `dirname` after the first, joined with the literals in order and
  normalized; no probing and no suffix search. A target no inventory file
  holds is an `unresolved` record, `relative-no-file` (`outside-repository`
  past the plant root).
- Shell argument and path literal: holder-directory-relative, then each
  `/`-suffix of the string, longest first, as a path relative to the holder's
  repository and then to the plant root (`$ROOT/tools/x.py` tries
  `$ROOT/tools/x.py`, then `tools/x.py`, then `x.py`). A string that is only a
  variable (`"$x"`, `${x}`) is `dynamic-nonliteral` when it is an `invoke`
  argument and nothing otherwise.
- TS/JS specifier: `./` and `../` from the holder's directory; otherwise the
  nearest `tsconfig.json` or `jsconfig.json` up from the holder inside its
  repository, its `extends` chain followed through relative paths to
  inventory files, child keys over parent keys: each `paths` pattern (one
  `*`), then `baseUrl`. A specifier that is a valid npm package name
  (including `@scope/name` and `node:` names), is not resolved and names no
  workspace package is external. Each base path is probed as written, then
  with `.ts .tsx .d.ts .js .jsx .mjs .cjs .mts .cts .json`, then as
  `<base>/index` with the same list; a written `.js .jsx .mjs .cjs` also
  probes `.ts .tsx .mts .cts`. In a TS/JS file, a path literal resolves by
  these rules and only when it is relative or alias-prefixed, never as a bare
  name.
- The config reader is JSONC: `//` and `/* */` comments and trailing commas
  are removed outside string literals, so `"@/*"` survives.

### Plant test declaration and config

The tests are the plant's `TEST_GLOBS` (read with `ast.literal_eval` from the
top-level assignment in `docs/graph/spec-lint.py`; a list of strings or
nothing). The optional plant-owned config, never placed by the installer:

```yaml
# docs/graph/source-index.json
source_index_config:
  exclude:       { type: array of glob, default: [] }   # out of the test class; still inventoried and linked
  always_run:    { type: array of glob, default: [] }   # tests always listed
  global_inputs: { type: array of glob, default: [      # a change may affect every file
      "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
      "tsconfig*.json", "jsconfig*.json", "vitest.config.*", "vite.config.*",
      "jest.config.*", "playwright.config.*", "next.config.*", "pytest.ini",
      "pyproject.toml", "setup.cfg", "tox.ini", "conftest.py",
      "requirements*.txt", "uv.lock" ] }
  # no other key; a pattern with no "/" matches the last path segment, one
  # with "/" the whole plant-relative path (graph-lint's _path_matches rule)
```
Each key the file sets replaces that key's default whole; unknown keys,
non-list values and non-string items refuse the whole file
(`PLANT_CONFIG_REFUSED`).

### Inputs

Each input is normalized lexically by the tool's `plant_relative` (posix;
`./` dropped; an absolute path inside the plant made plant-relative; the
result held to the helper's `relative` predicate) and deduplicated. It is,
in this order:
- `walked`: an inventory path; or a path that is no inventory path and that
  the probe rule of one `unresolved` record's `base` hits (a deleted file a
  reference still names);
- `not-code`: a path `source_paths.is_code` refuses (under `docs/graph/` or
  `.cypress/`, a build or backup file). It is answered: no code depends on it,
  so it adds no row and never makes the answer incomplete; `anchors` still
  reads its citations;
- a path no rule above takes and that is not plant-relative: tried under each
  governed repository root; one hit takes that path and its status, several
  are `incomplete` (`ambiguous-input`);
- otherwise `incomplete`: `outside-plant`, or `input-not-found`. `anchors`
  answers a `not-found` input from the citations alone and makes no record.

### Walk

One reverse breadth-first walk serves every query. A step goes from a reached
file F to every file holding a link whose target is F, and to every holder of
an `unresolved` record that names F (a `certain` step whose `found` is `named`
and whose `kind` is the record's). The walk has two parts over the same steps:

- The input part starts from the `walked` inputs at depth 0. Its rows are the
  input rows.
- The floor part runs when at least one input is walked. It starts from every
  `opaque` holder at depth 1, as a `maybe` row whose `kind` is `opaque`, whose
  `found` and `maybe` carry the opaque reason, the holder and its line, whose
  `from` is null and whose `via` begins at the holder; it takes the same steps
  from there. A file it reaches that the input part does not reach is a floor
  row. The floor is a function of the index alone, never of the inputs, so it
  is the same for every input of one index (less the files the input part
  takes); it is listed once, apart, after the input rows.

In each part, each file is reached once, at its nearest depth; at equal depth a
`certain` chain wins over a `maybe` one, then the smaller `from`. A row's
`link` is the weakest link on its chain (`certain` only when every link is),
and a `maybe` row carries the reason, holder and line of the `maybe` link
nearest the start of its chain (the input, or the opaque holder). The walk
never stops at a test. Both parts stop at `--depth`; a file at that depth with
a dependent the walk did not reach is a `depth-cap` record.

- `impact`: `dependents`, the input rows at depth 1 and more; `floor`, the
  floor rows.
- `affected-tests`: `tests`, the input rows of test class `test`, depth 0
  included; then `always_run`: every other test that `always_run` matches
  (`declared`), or that is a file of a link-bearing language (`python`,
  `shell`, `typescript`, `javascript`) holding no link to a `code` file and no
  `opaque` record (`no-code-edge`); a test that both rules take is
  `declared`, the rule the plant wrote; then `floor`, the floor rows of test
  class `test`. Each test is listed once, in the first of the three lists that
  takes it, so a test in `json` or `other` (a fixture) is never always-run by
  `no-code-edge`, only by `declared`.
- `anchors`: the citation join below; it does not walk links.

### Incomplete

An answer is `incomplete` when `incomplete` holds a record; its text view
then ends with the query's `ACTION_LINE`.

```yaml
incomplete_record:
  reason:     { enum: [see table] }
  subject:    { type: string, the input, repository, file or page concerned }
  candidates: { type: array of path, ambiguous-input and ambiguous-citation only, else [] }
  detail:     { type: string|null, e.g. the refused config's error or the citation text }
```
| Reason | Trigger | Queries |
|---|---|---|
| `git-unavailable` | no `git` on PATH | all |
| `no-repository` | no governed Git repository | all |
| `repository-unreadable` | a Git call for one repository failed or timed out | all |
| `config-refused` | `docs/graph/source-index.json` refused | all |
| `global-input` | an input matches `global_inputs` | all |
| `outside-plant` | an input outside the plant root | all |
| `ambiguous-input` | a repository-relative input several repositories hold | all |
| `input-not-found` | an input no rule of "Inputs" takes | impact, affected-tests |
| `depth-cap` | a file at `--depth` has an unreached dependent | impact, affected-tests |
| `no-test-declaration` | `TEST_GLOBS` absent, unparsable or not a list of strings | affected-tests |
| `no-test-files` | `TEST_GLOBS` matches no inventory file | affected-tests |
| `ambiguous-citation` | a bare-name citation several inventory files match, one an input | anchors |

### Cache document

```yaml
# .cypress/source-index/index.json, written sorted, indent 1, trailing newline
index:
  schema: "cypress.source-index/1"
  key:
    python: { the running interpreter's major.minor, e.g. "3.12": `ast` parses by its grammar }
    tool:   { sha256 of source-index.py bytes, then each SIBLINGS file's bytes in that order }
    config: { sha256 of the config file bytes (or ""), then of the TEST_GLOBS repr }
    repositories:
      - { path: string, head: sha1, dirty: sha256 over the sorted "path\0blob\n" lines of its uncommitted code paths }
  inventory:  [inventory_record]   # sorted by path
  links:      [link]               # sorted by holder, target, kind, line
  opaque:     [opaque]             # sorted by holder, line
  unresolved: [unresolved]         # sorted by holder, line, reference
```
A document whose `schema` or `key` differs from the current one, or which is
not this shape, is rebuilt. Anchors citations are read from the pages on
every query and never cached. The key leaves out Git's ignore sources outside
the work tree (`.git/info/exclude`, the user's `core.excludesFile`): an edit
there changes the inventory without a rebuild until the next key change or a
`build` (ADR-0029, accepted gap).

### Query answer

```yaml
answer:
  schema: "cypress.source-index.answer/1"
  query:  { enum: [build, impact, affected-tests, anchors] }
  inputs: [{ path, status: [walked, not-code, not-found] }]   # walked or answered inputs
  depth:  int                            # impact and affected-tests
  cache:  { status: [built, reused, rebuilt, not-written], reason: string|null }
  incomplete: [incomplete_record]
  # build
  inventory: [inventory_record]
  links: [link]
  opaque: [opaque]
  unresolved: [unresolved]
  # impact (dependents) and affected-tests (tests); both list the floor apart
  dependents: [row]
  tests:      [row]
  always_run: [{ path, reason: [declared, no-code-edge] }]
  floor:      [row]                      # the rows every input reaches; see "Walk"
  # anchors
  files: [{ path,
            facts:   [{ page, line: int|null, form: [backtick, repo], link: [certain, maybe],
                        found: [exact, basename, repo-prefix] }],
            history: { count: int, pages: [string] },   # pages empty unless --all
            uncited: bool }]
row:
  path:  string
  depth: int                                  # 0: the input itself
  link:  { enum: [certain, maybe] }           # the weakest link on the chain; certain at depth 0
  from:  string|null                          # the nearer file; null at depth 0 and for an opaque holder
  kind:  { enum: [import, invoke, path-literal, opaque], or null at depth 0 }
  found: { enum: [exact, resolved, path-literal, directory, ambiguous, workspace-package,   # a link's found
                   named,                                                                 # a walk step
                   dynamic-nonliteral, walks-tree, unreadable, alias-config-unavailable], # an opaque reason
           null at depth 0 }
  line:  int|null
  maybe: { reason, holder, line } | null      # the maybe link nearest the start of the chain
  via:   [path]                               # input (floor: opaque holder) first, this path last
```
Every list is sorted: `dependents` and `tests` by link (`certain` first),
then depth, then path, so the `certain` rows come first and the input's own
`maybe` rows after them; `floor` by depth, then path; facts by link (`certain`
first), then page, then line; every other list by its fields in the order the
shape names them. `inputs` lists each input once, sorted.

Citation reading for `anchors`: every `.md` page under `docs/graph/`, walked
with `plant_walk.files`; inline backtick spans outside fenced blocks; a span
that parses whole under the helper's citation grammar, else each of its
whitespace-separated tokens that holds a `/`. `#fragment` and
`:line[:col][-line]` are stripped and the line reported, never checked. Each
citation resolves through the helper's one citation-resolution function
against the inventory plus the inputs (so a deleted file still matches), in
order: plant-relative, `docs/graph/`-relative, page-relative, under each
nested governed repository (each a `certain` fact, found `exact`); then, for a
citation holding no `/`, the one inventory file of that basename (a `maybe`
fact, found `basename`); several such files make an `ambiguous-citation`
record when one is an input. `cite_problem` is the same function's strict
mode: plant-relative only, line checked. Every node whose `repo:` holds a `/`
claims each input it equals (`certain`) or is a directory prefix of (`maybe`,
found `repo-prefix`), all such nodes listed, longest claim first; a `repo:`
with no `/` claims nothing. Pages under `docs/graph/plans/`, `specs/` and
`decisions/` are `history`; every other page is a `fact`.

### CLI

```
python3 docs/graph/source-index.py --help
python3 docs/graph/source-index.py build [--json]
python3 docs/graph/source-index.py impact         [--depth N] [--all] [--json] <path>... | -
python3 docs/graph/source-index.py affected-tests [--depth N] [--all] [--json] <path>... | -
python3 docs/graph/source-index.py anchors                  [--all] [--json] <path>... | -
```
`--help` prints the usage and exits 0. `build` derives the whole index and
writes the cache whatever the key says (the forced rebuild of §3); the queries
build only on a missing, unreadable or mismatched cache. `-` reads one path
per stdin line (`git diff --name-only`). `--depth` takes 1 to `MAX_DEPTH`.
`--all` lifts `TEXT_MAX_ROWS` and names history pages. The text view prints
the cache line, then for `build` one count line (files, tests, `certain` and
`maybe` links, opaque and unresolved records), for the walks one row per line
(`<depth> <link> <path>  <- <from> [<kind> <found>:<line>]`, a `maybe` row
adding `maybe: <reason> at <holder>:<line>`), the `certain` rows first, then
the input's `maybe` rows, for `anchors` one block per file, then the
`always_run` list, then `FLOOR_LINE` and the floor rows, then the
`incomplete` list, each list capped on its own with a more-line, so the floor
never pushes an input row out of the view; it closes with the query's `ACTION_LINE` when the answer is
incomplete, else, for `affected-tests`, with `RECOMMEND_LINE`.

## 7. Failure modes

(Authored by `architect`. Security adds adversarial cases.)

### Failure: GIT_UNAVAILABLE
- **Contract:** BUILD_INVENTORIES_THE_CODE_OF_EVERY_GOVERNED_REPOSITORY,
  WALK_INCOMPLETE_NAMES_REASON_AND_ACTION
- **Trigger:** no `git` on PATH
- **Response:** exit 0; every result empty; `incomplete` holds
  `git-unavailable`; cache status `not-written`; the text view ends with the
  query's `ACTION_LINE`
- **Side effects:** nothing written; an existing cache is left as it is
- **Recovery:** install Git, or check the source by hand

### Failure: NO_GOVERNED_REPOSITORY
- **Contract:** BUILD_INVENTORIES_THE_CODE_OF_EVERY_GOVERNED_REPOSITORY
- **Trigger:** the plant root is not a Git work tree and no `repo:` resolves to
  one
- **Response:** as `GIT_UNAVAILABLE`, reason `no-repository`
- **Side effects:** none
- **Recovery:** run from the plant root, or name the repository in a node's
  `repo:`

### Failure: REPOSITORY_UNREADABLE
- **Contract:** WALK_INCOMPLETE_NAMES_REASON_AND_ACTION
- **Trigger:** a Git call for one governed repository fails or exceeds
  `GIT_TIMEOUT`
- **Response:** that repository contributes no inventory; `incomplete` holds
  `repository-unreadable` naming it; the other repositories answer
- **Side effects:** no cache written for this build
- **Recovery:** repair the repository; the next query rebuilds

### Failure: CYPRESS_DIR_ABSENT
- **Contract:** CACHE_WRITTEN_SELF_IGNORED
- **Trigger:** the plant root holds no `.cypress/`, or it is a symlink or not a
  directory, or the platform lacks descriptor-relative calls
- **Response:** the answer is built in memory; cache status `not-written` with
  the reason
- **Side effects:** `.cypress/` is never created; nothing is written
- **Recovery:** none needed; an install creates `.cypress/`

### Failure: CACHE_PATH_UNSAFE
- **Contract:** CACHE_WRITTEN_SELF_IGNORED
- **Trigger:** `.cypress/source-index`, its `.gitignore` or `index.json` is a
  symlink or another non-regular entry
- **Response:** cache status `not-written`, reason names the entry; the answer
  is built in memory
- **Side effects:** no symlink is followed, replaced or deleted
- **Recovery:** the owner removes the entry

### Failure: CACHE_UNREADABLE
- **Contract:** CACHE_REBUILT_WHEN_THE_KEY_CHANGES
- **Trigger:** `index.json` is not JSON, breaks the §6 shape, holds another
  schema, or is larger than `CACHE_MAX_BYTES` (never read whole)
- **Response:** cache status `rebuilt`, reason "cache unreadable"
- **Side effects:** the file is replaced atomically
- **Recovery:** none needed

### Failure: CACHE_WRITE_FAILED
- **Contract:** CACHE_WRITTEN_SELF_IGNORED
- **Trigger:** the temp write or the replace fails (disk full, permissions), or
  the document would be larger than `CACHE_MAX_BYTES`, which a later read would
  refuse
- **Response:** cache status `not-written` with the error; the answer stands
- **Side effects:** the temp file is removed; the old cache, if any, is intact
- **Recovery:** fix the cause; the next query rebuilds

### Failure: TSCONFIG_UNREADABLE
- **Contract:** LINK_TS_SPECIFIER_CERTAIN, UNPINNED_REFERENCE_RECORDED_WITH_ITS_REASON
- **Trigger:** the nearest tsconfig is not JSONC, or its `extends` chain names
  a file the inventory lacks
- **Response:** relative specifiers still resolve; a holder of any other
  non-package specifier under that config is opaque
  (`alias-config-unavailable`), so it joins every walk as a `maybe` floor row
- **Side effects:** none
- **Recovery:** fix or commit the config

### Failure: TEST_DECLARATION_UNAVAILABLE
- **Contract:** TESTS_ARE_THE_PLANTS_TEST_GLOBS,
  WALK_INCOMPLETE_NAMES_REASON_AND_ACTION
- **Trigger:** `docs/graph/spec-lint.py` is absent, does not parse, or holds no
  top-level `TEST_GLOBS` list of strings (`no-test-declaration`); or its
  `TEST_GLOBS` matches no inventory file (`no-test-files`)
- **Response:** no file is a test; `impact` and `anchors` answer as usual;
  `affected-tests` is incomplete with that reason
- **Side effects:** none
- **Recovery:** restore the engine (an install places it) or fix `TEST_GLOBS`

### Failure: PLANT_CONFIG_REFUSED
- **Contract:** PLANT_CONFIG_REPLACES_EACH_DEFAULT_KEY,
  WALK_INCOMPLETE_NAMES_REASON_AND_ACTION
- **Trigger:** `docs/graph/source-index.json` is not JSON, holds an unknown
  key, a non-list value or a non-string item
- **Response:** the whole file is ignored and the defaults apply; every query
  is incomplete with `config-refused` and the error as detail, because a
  refused `always_run` or `global_inputs` would otherwise drop rows silently
- **Side effects:** none
- **Recovery:** fix the file

### Failure: INPUT_NOT_IN_INDEX
- **Contract:** INPUT_FORMS_RESOLVED, WALK_DELETED_INPUT_REACHES_ITS_NAMERS,
  WALK_INCOMPLETE_NAMES_REASON_AND_ACTION
- **Trigger:** an input is no inventory path
- **Response:** by §6 "Inputs": a deleted file a reference names is walked; a
  `not-code` input is answered; a repository-relative input one repository
  holds is that file; otherwise `ambiguous-input`, `outside-plant` or
  `input-not-found` makes the answer incomplete; the other inputs answer
- **Side effects:** none
- **Recovery:** check the source for that path

### Failure: USAGE_REFUSED
- **Contract:** WALK_INCOMPLETE_NAMES_REASON_AND_ACTION
- **Trigger:** an unknown query or option, `--depth` outside 1 to
  `MAX_DEPTH`, or no path and no `-` (`--help` is not refused: exit 0)
- **Response:** exit 2, one stderr usage line, empty stdout
- **Side effects:** nothing read or written
- **Recovery:** correct the command line

### Failure: UNSAFE_PATH_TEXT
- **Contract:** OUTPUT_CARRIES_NO_RAW_CONTROL
- **Trigger:** an inventory path or a reference holds a control character or
  another character outside printable ASCII
- **Response:** the text view shows each such character as `?`; `--json`
  escapes it as JSON does
- **Side effects:** none
- **Recovery:** none needed

### Failure: FILE_NOT_REGULAR
- **Contract:** BUILD_INVENTORIES_THE_CODE_OF_EVERY_GOVERNED_REPOSITORY,
  UNPINNED_REFERENCE_RECORDED_WITH_ITS_REASON,
  ANCHORS_NAME_CITING_PAGES_OR_UNCITED
- **Trigger:** at read time an inventory path or a `docs/graph/` page is a
  symlink, a FIFO, a socket, a device or a directory (a tracked `a.py` replaced
  by a FIFO; a page committed as a symlink to a file outside the plant), or its
  real path leaves its repository through a symlinked parent directory
- **Response:** a symlink stays an inventory record hashed from its link text
  and is a link target only, never a holder; any other such inventory path is
  an `opaque` record with reason `unreadable` and line null; such a page is
  skipped by `anchors`. The open uses `O_NOFOLLOW | O_NONBLOCK` and nothing is
  read before `fstat` shows a regular file, so a FIFO never blocks the query
- **Side effects:** no symlink target is read; nothing outside the governed
  repositories is opened
- **Recovery:** none needed; the owner replaces the entry with a regular file

### Failure: INPUT_EXHAUSTS_A_PARSER
- **Contract:** UNPINNED_REFERENCE_RECORDED_WITH_ITS_REASON,
  PLANT_CONFIG_REPLACES_EACH_DEFAULT_KEY, CACHE_REBUILT_WHEN_THE_KEY_CHANGES
- **Trigger:** a link-bearing file larger than `FILE_MAX_BYTES` (a vendored
  minified bundle); or a parse that raises `RecursionError`, `MemoryError` or
  `ValueError` (deeply nested Python or JSON, a NUL byte in Python source, an
  integer literal past Python's digit limit) in a source file, a tsconfig or
  `package.json`, the plant config, `spec-lint.py` or `index.json`
- **Response:** exit 0 with an answer. A source file is `opaque` `unreadable`
  (its blob hash is still computed, by streaming); a tsconfig makes its holders
  `alias-config-unavailable`; a `package.json` names no workspace package; the
  plant config is `config-refused`; `spec-lint.py` is `no-test-declaration`;
  `index.json` is rebuilt
- **Side effects:** memory stays bounded by `FILE_MAX_BYTES` per file
- **Recovery:** none needed

### Failure: DIRECTORY_LITERAL_TOO_WIDE
- **Contract:** LINK_PATH_LITERAL_AND_DIRECTORY_ARE_MAYBE
- **Trigger:** a directory literal or one of its `/`-suffixes is empty or names
  a root (`"/"`, `"./"`, `"$ROOT/"`), or resolves to a directory holding more
  than `DIR_LINK_MAX` inventory files; strings such as `"/"` in `split("/")`
  are common, so without a bound each holder would link to every file
- **Response:** the empty suffix and a string with no named segment never
  resolve; a directory over `DIR_LINK_MAX` yields no per-file links and makes
  the holder `opaque` with reason `walks-tree`, so the link count stays linear
  in the number of references and the dependency is still reported, as a
  `maybe` floor row
- **Side effects:** none
- **Recovery:** none needed

### Failure: TSCONFIG_EXTENDS_CYCLE
- **Contract:** LINK_TS_SPECIFIER_CERTAIN
- **Trigger:** a tsconfig `extends` chain revisits a config (`a` extends `b`
  extends `a`) or is longer than `EXTENDS_MAX`
- **Response:** as `TSCONFIG_UNREADABLE`: relative specifiers resolve; the
  holders of other non-package specifiers under that config are `opaque`
  `alias-config-unavailable`
- **Side effects:** none; the chain is followed with a visited set, never
  recursively without bound
- **Recovery:** fix the config

### Failure: GIT_PATH_ARGUMENT
- **Contract:** UNPINNED_REFERENCE_RECORDED_WITH_ITS_REASON,
  BUILD_INVENTORIES_THE_CODE_OF_EVERY_GOVERNED_REPOSITORY
- **Trigger:** a reference whose path begins with `-` (`import "./--exec=x"`
  normalized to `--exec=x`), holds pathspec magic or glob characters
  (`:(top)`, `*`, `[`), or leaves its repository, when the tool asks Git
  whether the path is ignored (`generated`)
- **Response:** a path outside its repository is `outside-repository` before
  Git sees it; the rest go to one `git check-ignore --stdin -z` call per
  repository, never as argv, each written as `./<path>`, because Git parses
  pathspec magic in stdin paths too and one `:(exclude)` path or one path
  outside the repository makes the whole call exit 128 (both checked with Git
  on 2026-10-07; `GIT_LITERAL_PATHSPECS=1` is refused by `check-ignore`, so it
  is not the control). Exit 1 (nothing ignored) is an answer, so no reference
  can make a repository `repository-unreadable` or change which paths Git
  reports
- **Side effects:** none; Git reads, never writes
- **Recovery:** none needed

### Failure: CACHE_IGNORE_ALTERED
- **Contract:** CACHE_WRITTEN_SELF_IGNORED
- **Trigger:** `.cypress/source-index/.gitignore` is a regular file whose bytes
  differ from `CACHE_IGNORE` (a `!index.json` line added), or the process stops
  between the two writes
- **Response:** the `.gitignore` is rewritten to `CACHE_IGNORE` by the same
  exclusive-temp and atomic-replace write, before `index.json`; when that write
  fails, `index.json` is not written and the cache status is `not-written`
- **Side effects:** an `index.json` is never present without the `*` ignore
  beside it
- **Recovery:** none needed

### Failure: NON_UTF8_PATH
- **Contract:** OUTPUT_CARRIES_NO_RAW_CONTROL,
  BUILD_INVENTORIES_THE_CODE_OF_EVERY_GOVERNED_REPOSITORY,
  BUILD_IS_DETERMINISTIC
- **Trigger:** a file name that is not valid UTF-8, or that holds a bidi
  override or another format character (U+202E)
- **Response:** exit 0 with an answer: the name is decoded with
  `surrogateescape`, `--json` and the cache are written with `ensure_ascii`,
  so a lone surrogate or format character is a `\u` escape, and the text view
  shows `?`; a write never raises `UnicodeEncodeError`
- **Side effects:** none
- **Recovery:** none needed

## 8. Examples

Real figures from the seed, this plant and Vivid as measured on 2026-10-07
(the gap reports, consolidated in the session record); outputs abbreviated.

```yaml
# Happy: Vivid, an alias import (tsconfig.json "paths": {"@/*": ["./src/*"]})
input:  impact src/lib/db/index.ts --json
output:
  cache: { status: built }
  dependents:
    - { path: src/lib/feed/service.ts,         depth: 1, link: certain, from: src/lib/db/index.ts, kind: import, found: resolved, line: 10 }  # import type { Database } from "@/lib/db"
    - { path: src/lib/jobs/register.ts,        depth: 1, link: certain, from: src/lib/db/index.ts, kind: import, found: resolved }
    - { path: src/lib/jobs/retention-sweep.ts, depth: 1, link: certain, from: src/lib/db/index.ts, kind: import, found: resolved }
    # ... src/lib/db/index.ts is a hub; the list continues
  incomplete: []
```

```yaml
# Edge: this plant (TEST_GLOBS "Cypress/tests/**/*.*", "Cypress/tests/*.*"),
# a file that is both a test step and the tool another test drives
input:  affected-tests Cypress/tests/legal-lint.py --json
output:
  tests:
    - { path: Cypress/tests/legal-lint.py,      depth: 0, link: certain, via: [Cypress/tests/legal-lint.py] }
    - { path: Cypress/tests/run.sh,             depth: 1, link: certain, kind: invoke, found: resolved, via: [Cypress/tests/legal-lint.py, Cypress/tests/run.sh] }            # add_step python3 "$ROOT/tests/legal-lint.py"
    - { path: Cypress/tests/test-legal-lint.sh, depth: 1, link: certain, kind: invoke, found: resolved, via: [Cypress/tests/legal-lint.py, Cypress/tests/test-legal-lint.sh] }  # line 18: python3 "$TMP/tests/legal-lint.py"
  floor:
    # each opaque test (a whole-tree walk: `find "$ROOT"`, `rglob`) at depth 1, maybe, reason walks-tree,
    # listed once after the input's rows, the same for every input
  incomplete: []
  # last text line: RECOMMEND_LINE. The walk never stops at a test, so
  # test-legal-lint.sh is found (a test-stop rule lost it in the co-change study,
  # 8 of 9 pairs). run.sh matches TEST_GLOBS and invokes every test, so it is
  # reached whenever any test is: a suite runner in `tests` is the full suite in
  # disguise; the plant moves it out of the test class with exclude.
```

```yaml
# Edge, large: this plant, the most-cited file (73 pages cite Cypress/install.sh)
input:  anchors Cypress/install.sh
output: |
  Cypress/install.sh: <n> fact pages, history <h> pages counted
  ... 40 fact rows ...
  - and <k> more row(s): --all lists every row and names the history pages
  # --json lists every fact page; history pages only with --all
```

```yaml
# Edge: this plant, a sibling loaded by file path (§6 "Load by file path")
input:  impact Cypress/tools/plant_walk.py --json
output:
  dependents:
    - { path: Cypress/tools/corpus-match.py, depth: 1, link: certain, from: Cypress/tools/plant_walk.py, kind: import, found: exact, line: 54 }   # spec_from_file_location("cypress_plant_walk", Path(__file__).resolve().parent / "plant_walk.py")
    - { path: Cypress/tools/graft-audit.py,  depth: 1, link: certain, from: Cypress/tools/plant_walk.py, kind: import, found: exact, line: 169 }
    - { path: Cypress/tools/growth-audit.py, depth: 1, link: certain, from: Cypress/tools/plant_walk.py, kind: import, found: exact, line: 160 }
    - { path: Cypress/tools/graft-ledger.py, depth: 2, link: certain, from: Cypress/tools/graft-audit.py, kind: import, found: exact, line: 79 }
    - { path: Cypress/tools/graft-run.py,    depth: 2, link: certain, from: Cypress/tools/graft-audit.py, kind: import, found: exact, line: 79 }
    # ... then the tests that drive these tools, and the input's maybe rows
  # as path literals these five were maybe rows, and plant_walk.py had no certain dependent
```

```yaml
# Edge: Vivid, a deleted file a reference still names (the gap scout found
# the specifier @/lib/posts/validate unresolved at HEAD; its holder is not recorded)
input:  affected-tests src/lib/posts/validate.ts --json
output:
  inputs: [ { path: src/lib/posts/validate.ts, status: walked } ]
  tests:
    # the tests that reach <holder of "@/lib/posts/validate">, each certain,
    # via [src/lib/posts/validate.ts, <holder>, ...]; the holder's row is
    # depth 1, found named, from the stored alias-no-file reference
  incomplete: []
```

```yaml
# Failure, global input: Vivid, a tsconfig edit changes every alias resolution
input:  impact tsconfig.json; affected-tests tsconfig.json; anchors tsconfig.json
output:
  incomplete: [ { reason: global-input, subject: tsconfig.json } ]
  # last text lines, one per query:
  #   Incomplete: check by hand (global-input: tsconfig.json).
  #   Incomplete: run the full suite (global-input: tsconfig.json).
  #   Incomplete: review by hand (global-input: tsconfig.json).
```

## 9. Acceptance criteria

(Authored by `product`. Each criterion maps to one or more contracts
in §4.)

Each criterion is measurable. A tester can write a test for it
without further clarification.

- [ ] AC-1: In a fresh install, `python3 docs/graph/source-index.py build`
  exits 0, and the inventory lists exactly the tracked and untracked
  non-ignored code files of every governed repository, never a graph page,
  a `.cypress/` file, a build or backup file, or a nested plant's file —
  maps to SOURCE_INDEX_IS_PLACED, BUILD_INVENTORIES_THE_CODE_OF_EVERY_GOVERNED_REPOSITORY
- [ ] AC-2: `impact` lists every file that depends on an input through a
  Python import, a shell or Python invocation, or a TS/JS import (relative
  or through a `tsconfig` alias) as a `certain` row, nearest first, each
  file once at its nearest depth, with its `from`, kind, found value and
  line — maps to LINK_PYTHON_IMPORT_CERTAIN, LINK_SHELL_INVOCATION_CERTAIN,
  LINK_TS_SPECIFIER_CERTAIN, WALK_NEAREST_FIRST_ONCE
- [ ] AC-3: A dependency found only through a quoted path, a directory
  literal, an ambiguous module name or an unpinned reference is a `maybe`
  row naming the reason, holder and line of the weakest link; no such
  chain is ever `certain`. In `dependents`, the `certain` rows come first
  and the input's own `maybe` rows after them. An opaque file and its
  dependents are `maybe` rows in `floor`, listed once, apart, after the
  input rows, in every walk that has a walked input; a file the input
  part reaches is never a floor row — maps to
  LINK_PATH_LITERAL_AND_DIRECTORY_ARE_MAYBE,
  UNPINNED_REFERENCE_RECORDED_WITH_ITS_REASON, WALK_CHAIN_IS_ITS_WEAKEST_LINK,
  WALK_FLOOR_LISTED_APART_AFTER_THE_INPUT_ROWS

- [ ] AC-4: An input given repository-relative, absolute or with `./`
  names the same file; a deleted file a stored reference still names is
  walked to its namers; a `docs/graph/` input is answered `not-code` and
  adds no `incomplete` record — maps to INPUT_FORMS_RESOLVED,
  WALK_DELETED_INPUT_REACHES_ITS_NAMERS
- [ ] AC-5: `affected-tests` lists in `tests` the rows of the input
  walk whose file is in the plant's test class (depth 0 included), each
  with its `via` path; then `always_run` (`declared`, `no-code-edge`);
  then `floor`, the floor rows of test class `test`. Each test is listed
  once, in the first of the three lists that takes it, so a test reached
  and declared is in `tests` only; the text view ends with
  `RECOMMEND_LINE` — maps to AFFECTED_TESTS_ARE_THE_WALK_FILTERED,
  AFFECTED_ALWAYS_RUN_LISTED_APART

- [ ] AC-6: The test class is the plant's `TEST_GLOBS`; a
  `docs/graph/source-index.json` key replaces only its own default, and
  `exclude` changes only the test class — maps to
  TESTS_ARE_THE_PLANTS_TEST_GLOBS, PLANT_CONFIG_REPLACES_EACH_DEFAULT_KEY
- [ ] AC-7: `anchors` lists, for each input, the citing knowledge pages
  as facts (`certain` for an exact citation or `repo:` match, `maybe` for
  a bare name or a `repo:` prefix), counts plans, specs and decisions as
  history (named with `--all`), marks an uncited file `uncited`, and makes
  an ambiguous bare-name citation an `ambiguous-citation` record — maps to
  ANCHORS_NAME_CITING_PAGES_OR_UNCITED,
  ANCHORS_BASENAME_IS_MAYBE_AMBIGUOUS_IS_INCOMPLETE
- [ ] AC-8: Every answer the walk cannot give in full exits 0, still
  lists the rows it reached, holds one `incomplete` record with the §6
  reason and subject, and ends its text view with the query's action line
  (`impact` "check by hand", `affected-tests` "run the full suite",
  `anchors` "review by hand"); `--depth 5` completes a chain that
  `--depth 3` cuts — maps to WALK_INCOMPLETE_NAMES_REASON_AND_ACTION,
  PLANT_CONFIG_REPLACES_EACH_DEFAULT_KEY
- [ ] AC-9: The first query writes `.cypress/source-index/index.json` and
  an inner `.gitignore` of exactly `*`, and `git status --porcelain` shows
  nothing there; a second query with no change reuses the cache byte for
  byte; a commit, an uncommitted code edit, a config edit, a `TEST_GLOBS`
  edit or a graft that changes the tool rebuilds it, with a result equal
  to a build from an empty cache — maps to CACHE_WRITTEN_SELF_IGNORED,
  CACHE_REUSED_WHILE_THE_KEY_HOLDS, CACHE_REBUILT_WHEN_THE_KEY_CHANGES,
  GRAFT_REBUILDS_THE_CACHE
- [ ] AC-10: Two builds of the same plant produce byte-identical caches
  that hold no absolute plant path — maps to BUILD_IS_DETERMINISTIC
- [ ] AC-11 (accessibility): The text view is plain line-oriented ASCII
  that carries every status in words (`certain`, `maybe`, the reason, the
  action line), never in color or layout alone; a path with a control or
  non-ASCII character prints as `?`, so a hook or brief reading the output
  cannot receive terminal control sequences — maps to
  OUTPUT_CARRIES_NO_RAW_CONTROL (failure UNSAFE_PATH_TEXT)
- [ ] AC-12 (non-functional): A full build over a 5,000-file repository
  finishes within 5 s and 64 MB peak RSS, and a cache-reusing query on the
  seed-sized plant within 1 s, measured once at verify and recorded, not
  gated (§5) — maps to BUILD_INVENTORIES_THE_CODE_OF_EVERY_GOVERNED_REPOSITORY,
  CACHE_REUSED_WHILE_THE_KEY_HOLDS

Acceptance criteria are checked off when the increment that
implements them passes its gates.

## 10. Test mapping

(Authored by `tester`, 2026-10-07, review `tester-s10`.) One case per contract
in one new suite, `tests/test-source-index.sh`, a gate step in `tests/run.sh`;
the placement contract is one E case in its owner suite,
`tests/test-full-install.sh`. A failure mode is an arm of the case whose
fixture already sets it up, never a case of its own, except `USAGE_REFUSED`,
which no contract fixture reaches. Cases follow the
code-anchor suite: synthetic Git plants built under a temp directory, Git with
a HOME of its own, the tool and its siblings copied to `<plant>/docs/graph/`,
run from the plant root; each case carries its label and the slugs it asserts,
its OK line reads `X4NN <SLUG>: … — OK`, and `SOURCE_INDEX_ONLY=X425,X431`
runs a subset. Labels `X425` to `X449` and `E15` are reserved here.

Binding (`tests/seed-lint.py` `check_spec_test_mapping`): a row's file cell
carries the bare path only once the case exists in that file; until RED lands
the cell reads `(new)` or `(new case)`, which neither the file check nor the
label check binds. RED replaces it with the bare path.

Not tested here, by design: the helper extraction (`tools/source_paths.py`),
proved by the code-anchor, growth-audit, tool-help and full-install suites
with no assertion edited (grill §10); placement mechanics of `install.sh`
(SPEC-0001); the §5 timings (measured once at verify, not gated).
AC-12 is that measurement (grill §10), recorded at verify, so no row maps it.

Readings the tests take where §4 leaves a detail to §6 (each confirmed by
`architect-fix`, 2026-10-07; §4 and §6 now state it):
- `SOURCE_INDEX_IS_PLACED`: the "neither … exists" check runs after the
  install and before the `build`, since `build` writes the cache.
- `UNPINNED_REFERENCE_RECORDED_WITH_ITS_REASON`: the `asset` record's `base`
  is the plant-relative path with the `?raw` query cut, ending in `a.css`
  (§6 "Unresolved records").
- `LINK_SHELL_INVOCATION_CERTAIN`: "one link to each target" is exactly one
  link per holder and target; a quoted `invoke` argument is not also a
  `path-literal` link (§6 "any other quoted string").
- `PLANT_CONFIG_REPLACES_EACH_DEFAULT_KEY`: a test that is both declared and
  has no code link reports `declared` (§6 lists it first).

Readings RED R1 (`tester-R1`) takes where §4 and §6 name no value; the
architect confirms or amends each before GREEN:
- `LINK_PATH_LITERAL_AND_DIRECTORY_ARE_MAYBE`: a `directory` link has kind
  `path-literal` (the one kind a quoted string that is no import or invoke
  takes).
- `WALK_NEAREST_FIRST_ONCE`: `import a` beside `a.py` is found `resolved` (the
  Python module search), `python3 b.py` beside `b.py` is found `exact`.
- `WALK_INCOMPLETE_NAMES_REASON_AND_ACTION`: the subject of `global-input`,
  `input-not-found`, `ambiguous-input` and `outside-plant` is the input as
  given; of `depth-cap` the file at the cut depth; of `config-refused`
  `docs/graph/source-index.json`; of `repository-unreadable` the repository
  path; the text view's last line starts with the query's `ACTION_LINE` and
  names the reason.
- `CACHE_UNREADABLE`: the cache reason holds the word `unreadable`.
- `BUILD_IS_DETERMINISTIC`: "answers from the copied cache unchanged" is cache
  status `reused` in the copy.

| Contract / Failure | Test name | Test file | Level | Status |
|---|---|---|---|---|
| BUILD_INVENTORIES_THE_CODE_OF_EVERY_GOVERNED_REPOSITORY | X425 case_build_inventory | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| BUILD_IS_DETERMINISTIC | X426 case_build_deterministic | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| CACHE_WRITTEN_SELF_IGNORED | X427 case_cache_self_ignored: arm (a) | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| CACHE_REUSED_WHILE_THE_KEY_HOLDS | X428 case_cache_reused | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| CACHE_REBUILT_WHEN_THE_KEY_CHANGES | X429 case_cache_rebuilt: arms (a) to (d) and (f), one per key change, (f) another Python major.minor in the key | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| GRAFT_REBUILDS_THE_CACHE | X430 case_graft_rebuilds | tests/test-source-index.sh | integration (install.sh over a temp plant) | red |
| LINK_PYTHON_IMPORT_CERTAIN | X431 case_link_python_import: exactly seven certain import links, five found exact (three loads by file path) and two resolved; no path-literal link from a load argument | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| LINK_SHELL_INVOCATION_CERTAIN | X432 case_link_shell_invocation | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| LINK_PATH_LITERAL_AND_DIRECTORY_ARE_MAYBE | X433 case_link_path_literal: the anchored `frontmatter.py` path no load call takes is a maybe path-literal link | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| LINK_TS_SPECIFIER_CERTAIN | X434 case_link_ts_specifier: six files, the sixth the line-join arm | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| UNPINNED_REFERENCE_RECORDED_WITH_ITS_REASON | X435 case_unpinned_reference | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| TESTS_ARE_THE_PLANTS_TEST_GLOBS | X436 case_test_globs | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| PLANT_CONFIG_REPLACES_EACH_DEFAULT_KEY | X437 case_plant_config_keys | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| WALK_NEAREST_FIRST_ONCE | X438 case_walk_nearest_first: certain rows first, then a maybe row | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| WALK_CHAIN_IS_ITS_WEAKEST_LINK | X439 case_walk_weakest_link | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| WALK_FLOOR_LISTED_APART_AFTER_THE_INPUT_ROWS | X449 case_walk_floor: `impact a.py` then `impact z.py`, JSON and the text view | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| WALK_DELETED_INPUT_REACHES_ITS_NAMERS | X440 case_walk_deleted_input | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| INPUT_FORMS_RESOLVED | X441 case_input_forms | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| WALK_INCOMPLETE_NAMES_REASON_AND_ACTION | X442 case_walk_incomplete: arms (a) to (h), one per reason the contract lists | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| AFFECTED_TESTS_ARE_THE_WALK_FILTERED | X443 case_affected_tests_filtered: certain rows first, then a maybe row | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| AFFECTED_ALWAYS_RUN_LISTED_APART | X444 case_affected_always_run: the opaque test in `floor`, the JSON and Markdown fixtures in no list | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| ANCHORS_NAME_CITING_PAGES_OR_UNCITED | X445 case_anchors_citing_pages | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| ANCHORS_BASENAME_IS_MAYBE_AMBIGUOUS_IS_INCOMPLETE | X446 case_anchors_basename | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| OUTPUT_CARRIES_NO_RAW_CONTROL | X448 case_output_no_raw_control: names holding ESC, U+202E and the byte 0xFF, text and `--json` | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| SOURCE_INDEX_IS_PLACED | E15 SOURCE_INDEX_IS_PLACED | tests/test-full-install.sh | integration (fresh install) | red |
| GIT_UNAVAILABLE | X442 case_walk_incomplete: arm (f), PATH holds python3 and no git; an existing cache left byte-identical | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| NO_GOVERNED_REPOSITORY | X442 case_walk_incomplete: arm (i), a plant root that is no Git work tree | tests/test-source-index.sh | integration (synthetic plant) | red |
| REPOSITORY_UNREADABLE | X442 case_walk_incomplete: arm (j), a nested governed repository with a corrupt index; the root repository still answers | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| CYPRESS_DIR_ABSENT | X427 case_cache_self_ignored: arm (b), no `.cypress/`; status `not-written`, `.cypress/` not created | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| CACHE_PATH_UNSAFE | X427 case_cache_self_ignored: arm (c), `.cypress/source-index` a symlink to a directory outside the plant; status `not-written`, the target untouched | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| CACHE_IGNORE_ALTERED | X427 case_cache_self_ignored: arm (d), an inner `.gitignore` holding `!index.json` is rewritten to `*` | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| CACHE_UNREADABLE | X429 case_cache_rebuilt: arm (e), `index.json` not JSON, then valid JSON of another schema | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| CACHE_WRITE_FAILED | (no test: the temp file and atomic replace are the helper's write, whose fault path tests/test-code-anchor.sh proves; a lost cache is rebuilt on the next query) | — | — | skipped |
| TSCONFIG_UNREADABLE | X435 case_unpinned_reference: the `extends` arm (`alias-config-unavailable`), whose holder's relative import still resolves | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| TEST_DECLARATION_UNAVAILABLE | X442 case_walk_incomplete: arms (g) `no-test-declaration` and (h) `no-test-files` | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| PLANT_CONFIG_REFUSED | X442 case_walk_incomplete: arm (e), an unknown key; `config-refused` with the error as detail | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| INPUT_NOT_IN_INDEX | X441 case_input_forms, and X442 case_walk_incomplete: arms (b) `input-not-found`, (c) `ambiguous-input`, (k) `outside-plant` | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| USAGE_REFUSED | X447 case_usage_refused: an unknown query or option, `--depth 0` and `--depth 6`, no path; `--help` exits 0 | tests/test-source-index.sh | integration (CLI) | red |
| UNSAFE_PATH_TEXT | X448 case_output_no_raw_control: the ESC arm; the text view shows `?`, `--json` escapes it | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| FILE_NOT_REGULAR | X435 case_unpinned_reference: a tracked file replaced by a FIFO is opaque `unreadable`, line null, and the query does not block; X425 holds the symlink arm (a record, never a holder) | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| INPUT_EXHAUSTS_A_PARSER | X435 case_unpinned_reference: a Python file over `FILE_MAX_BYTES` (its blob hash still listed) and one holding a NUL byte are opaque `unreadable` | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| DIRECTORY_LITERAL_TOO_WIDE | X433 case_link_path_literal: `"/"`, `"./"` and `"$ROOT/"` link nothing; a directory over `DIR_LINK_MAX` makes its holder opaque `walks-tree` | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| TSCONFIG_EXTENDS_CYCLE | X434 case_link_ts_specifier: an `extends` cycle keeps the relative import and makes the alias holder opaque `alias-config-unavailable` | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| GIT_PATH_ARGUMENT | X435 case_unpinned_reference: `./--exec=x`, `./:(top)q`, `./*` stay `relative-no-file` records and a path past the root `outside-repository`, the `generated` record still found and the build complete | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| NON_UTF8_PATH | X448 case_output_no_raw_control: the 0xFF arm, decoded as U+DCFF in `--json` | tests/test-source-index.sh | integration (synthetic Git plant) | red |

Status values: `red` (test exists, fails), `green` (test exists,
passes), `pending` (test not yet written), `skipped` (with reason).

## 11. Open questions

| Question | Why it matters | Current assumption | Owner | Resolves by |
|---|---|---|---|---|

A spec with open questions is unsigned. Sign off (§0) only when the
table is empty or every row's "current assumption" is recorded as a
flagged assumption in grill.md §12. Sign-off keeps the status `draft`;
`active` lands with the spec's first RED tests (test-first COMMIT),
`implemented` when every contract is green.

## 12. Changelog

- 2026-10-07 — created in `draft` (`architect-s4b`): §4 to §8.
- 2026-10-07 — amended after review `reviewer-spec` (`architect-amend`): one walk with three link kinds.
- 2026-10-07 — joint-pass step 3: §3 and §9 (`product-s3s9`), §10 (`tester-s10`), §5 and seven §7 abuse cases (`security-s5s7`).
- 2026-10-07 — step-3 returns applied (`architect-fix`): placement checked before any query; asset `base` with the query cut; an import or invoke string is never also a path literal; `declared` before `no-code-edge`; contract `OUTPUT_CARRIES_NO_RAW_CONTROL` added; `named` defined as a walk step; the four bounds `FILE_MAX_BYTES`, `DIR_LINK_MAX`, `EXTENDS_MAX`, `CACHE_MAX_BYTES`; `mkdir` in `DIR_FD_CALLS`; `unresolved` gains `kind` and a null `base` for `outside-repository`, and comes only from import and invoke references; the helper's `git` takes an answer exit set and stdin.
- 2026-10-07 — devils-advocate verdicts applied (`architect-da`): the floor (the `maybe` rows every input reaches: opaque holders and their dependents) listed once and apart after the input rows, `certain` rows first, contract `WALK_FLOOR_LISTED_APART_AFTER_THE_INPUT_ROWS` added and `WALK_CHAIN_IS_ITS_WEAKEST_LINK` and `AFFECTED_ALWAYS_RUN_LISTED_APART` amended; `no-code-edge` only for link-bearing languages; `exact` no longer claimed for path literals; §6 "Helper" names the four interface changes code-anchor gets; the input normalizer is `plant_relative`, the helper's `relative` stays a predicate; the Python major.minor joins the cache key (an arm of `CACHE_REBUILT_WHEN_THE_KEY_CHANGES`); the Python floor corrected to 3.12; the TS/JS line join (`JOIN_MAX`, an arm of `LINK_TS_SPECIFIER_CERTAIN`); AC-11 remapped to `OUTPUT_CARRIES_NO_RAW_CONTROL` at product's request (mapping only).
- 2026-10-07 — section 9 aligned with the floor (`product-ac5`): AC-3 and AC-5 state the `floor` list and the one-list precedence tests, always_run, floor.
- 2026-10-07 — plan §12 question 5 closed (`architect-q5`), the owner accepting recommendation (b): a Python load by file path (`spec_from_file_location` or `run_path` over a path anchored at `__file__`, the two shapes of §6 "Links") is a `certain` `import` link found `exact`, an arm of `LINK_PYTHON_IMPORT_CERTAIN`; a missing target is `relative-no-file`; `LINK_PATH_LITERAL_AND_DIRECTORY_ARE_MAYBE` now takes an anchored path no load call takes; §2 links line and a §8 example (`plant_walk.py`) added.
- 2026-10-07 — RED for plan increments 3 to 7 (`tester-R1`): §10 bound to `tests/test-source-index.sh` (X425 to X449) and `tests/test-full-install.sh` E15, every row `red`; rows added for `OUTPUT_CARRIES_NO_RAW_CONTROL` (X448), `WALK_FLOOR_LISTED_APART_AFTER_THE_INPUT_ROWS` (X449) and the security failures, each an arm of its contract's case; status `active` with the first RED tests (§11).
