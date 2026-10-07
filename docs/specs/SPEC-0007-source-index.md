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
- **Last reviewed:** 2026-10-07 (review `reviewer-spec`, amended by `architect-amend`; joint-pass step-3 returns applied by `architect-fix`; devils-advocate verdicts applied by `architect-da`; the load by file path made `certain` by `architect-q5`; the code-review fixes stated in §6 and §7 by `architect-review-fixes`; the slice-1 final decisions after the measurement, path joins, the floor's depth and the unmapped specifier, by `architect-final`; slice 2, §1, §2 and §4 to §8, by `architect-slice2`; the slice-2 tester, security and devils-advocate findings by `architect-slice2-fix`; the slice-2 code review `reviewer-slice2` (fixes 5 and 6) and the measurement-2 decisions M2-1, M2-3 and M2-6 by `architect-slice2-m2`)
- **Related grill section:** docs/plans/grill-8.1.0-source-index.md §6 (the owner's rulings of 2026-10-07: one walk with three link kinds; the helper's scope; test roots and plant config; graph-lint keeps its tier-2 rule in slice 1; "slice 2 ok", with the slice-2 rows)
- **Related ADRs:** adr-0029-source-index-is-derived-scratch (proposed): the index is derived scratch, self-ignored, rebuilt on any key change, never committed and never canonical
- **Related specs:** SPEC-0001-install-placement (placement), SPEC-0003-per-prompt-injection (code anchor)
- **Related wiki pages:** none (stdlib Python and git only)
- **Design latitude:** balanced. The owner approved on 2026-10-07: "implement the plan so that it's integrated organically into the cypress seed and installed/grafted into the plants correctly." New structure is allowed where the change needs it (one shared helper module, one derived cache); no concept the plan did not name.
- **Supersedes:** none
- **Superseded by:** none
- **Sign-offs:** product [x] (2026-10-07: slice 1 signed, §3 and §9 reflect the owner's outcome; 2026-10-07, `product-slice2-fix`: slice 2, REPO_CLAIM pending owner ruling) · architect [x] (2026-10-07, `architect-da`: §4 to §8 coherent after the devils-advocate verdicts; the floor, the helper interface, the interpreter in the key and the TS/JS line join applied; 2026-10-07, `architect-slice2`: the slice-2 §4 to §8 coherent with slice 1; 2026-10-07, `architect-slice2-fix`: the slice-2 review findings applied, `REPO_CLAIM_READ_ALIKE_BY_ROUTER_AND_ANCHORS` left pending the owner's `repo:` ruling, grill §12 question 6) · tester [x] (2026-10-07: slice 1 signed; `tester-slice2-fix`: slice 2, REPO_CLAIM pending owner ruling) · security [x] (2026-10-07, `security-slice2-sign`: slice 2 signed; S1 to S8 and P1 to P10 applied in §5, §6, §7, §10 and the plan; accepted deviations: the `/%P` history marker that also skips a parentless commit, the depth-2 `file://` shallow clone, and a missing helper beside graph-lint degrading tier 2 with the `inference_skipped` notice instead of failing the route; REPO_CLAIM pending owner ruling. Slice 1 signed by `security-s5s7`: §5 Security requirements and seven §7 abuse cases added; four §6 constants, `FILE_MAX_BYTES`, `DIR_LINK_MAX`, `EXTENDS_MAX` and `CACHE_MAX_BYTES`, and the `outside-repository` `base` value are left to the architect)

## 1. Summary

A stdlib Python seed tool, `tools/source-index.py`, placed in every plant as `docs/graph/source-index.py`, derives the structure of a project's code, the code that does things and the tests that check it, without a model. It builds a file inventory (path, content hash, language, test class) and file-to-file links from Python imports (`ast`), shell and Python invocations, quoted path and directory literals (whole, or joined from segments as in `ROOT / "tools" / "x.py"`), and TypeScript/JavaScript import and require specifiers resolved through `tsconfig` paths. One reverse walk over those links answers three queries: `impact` (the files that depend on the inputs, `certain` rows first, each class nearest first), `affected-tests` (the same walk filtered to the test class, plus the always-run set) and `anchors` (graph pages that cite the inputs). Every row is `certain` or `maybe` (with the reason and line of its weakest link); the `maybe` rows every input reaches alike, the opaque holders and their dependents, are the floor, listed once and apart after the input's own rows; what the tool cannot answer makes the answer `incomplete`, with a reason and one action per query: "check by hand", "run the full suite", "review by hand". The index is derived, safe to delete, never committed, and rebuilt whenever its key changes, a graft or another Python version included (ADR-0029). The rules for "what is code", "where does the plant end" and "how a page cites a path" have one home each, shared with `code-anchor.py` and `growth-audit.py`. The tool recommends; verify, tiering and canonize keep every decision. Slice 2 adds a `symbols` query that says where a name is defined (a Python definition read by `ast` is `certain`, a shell function or a top-level or exported TS/JS declaration read a line at a time is `maybe`), Git change history as an opt-in `maybe` link source (`--history`), `anchors --moved` over code-anchor's moved list, the `repo:` claim and path-pattern rules in the helper that `graph-lint.py` now loads too, and protocol steps that call the tool on demand at verify, canonize, grow and adopt.

## 2. Scope

- **In scope:**
  - The seed tool and its placement by `install.sh` and `manifest.json`; graft rebuilds the cache through its key and never carries a stale one over.
  - One shared helper module, `tools/source_paths.py`, holding the code-path rule, governed repositories, the Git boundary, blob hashing, the clean-relative predicate `relative` and the atomic write (today in `code-anchor.py`, which moves onto the helper's interface of §6 "Helper"), and the citation grammar with the one citation-resolution function whose strict plant-relative mode is `cite_problem` (today in `growth-audit.py`); `plant_walk.py` stays the plant-edge owner. `graph-lint.py` kept its own tier-2 path rule in slice 1 (accepted debt, grill §6); slice 2 moves it onto the helper (below).
  - File inventory from `git ls-files` plus untracked non-ignored files, per governed repository, across repositories.
  - Links: Python `ast` imports and loads by file path anchored at `__file__`; `python3|python|bash|sh <path>`, `python3 -m <module>` and `source <path>` invocations; quoted path literals and directory literals, whole or joined from segments (a `/` chain, `os.path.join`, `path.join`, `path.resolve`), resolved by suffix; TS/JS `import`/`export from`/`require()`/`import()` with relative and `tsconfig` `paths`/`baseUrl` resolution (comment-tolerant JSON reader) and workspace package names. Each link is `certain` or `maybe` with its reason; files whose references cannot be pinned (non-literal dynamic paths, tree walks, unreadable files) are opaque. Markdown mentions are not dependency links; page citations are a separate relation read only by `anchors`.
  - Test class from the plant's `TEST_GLOBS` in `docs/graph/spec-lint.py`; an optional plant config `docs/graph/source-index.json` holding `exclude` (out of the test class), `always_run` and `global_inputs`, with seed defaults; a file may be both a test and a tool.
  - One walk and queries `impact`, `affected-tests` (default depth 3, cap 5), `anchors`, plus `build`; the floor listed apart; text and `--json`; the `incomplete` list with per-query actions.
  - A derived cache at `.cypress/source-index/` with an inner `.gitignore` of `*`, keyed as ADR-0029 decides (schema; the Python major.minor; digests of the tool and every sibling it loads; digest of the config and `TEST_GLOBS`; each governed repository's HEAD and uncommitted-code digest), written atomically.
  - Slice 2 (owner, 2026-10-07: "slice 2 ok"):
    - Definitions, built with the links into the cache, and the query `symbols`: Python functions, classes, module and class assignments and `type` aliases read by `ast` (`certain`); shell functions and top-level or exported TS/JS declarations read a line at a time after comments are blanked (`maybe`, reason `line-reading`); every definition of a name listed; a file the index could not read makes the answer incomplete.
    - Git change history as an opt-in link source for `impact` and `affected-tests` (`--history`): read per query from `git log` and never cached; its rows are `maybe`, labelled `history`, with how often each file changed together with an input, and listed apart; history only adds files no other list holds; shallow or missing history makes the answer incomplete.
    - `anchors --moved`: the moved list of `code-anchor.py`, read through the one function its `--compare` prints from, each repository-relative path joined to its repository (grill §12 question 3).
    - The `repo:` claim rule and the path-pattern rule move into the helper; `graph-lint.py` loads the helper from beside itself and its tier 2 calls both, with its messages and verdicts unchanged (grill §12 question 2); `anchors` and the plant config call the same two functions.
    - Protocol wiring, on demand and never per prompt or per file access (ADR-0018 withdrew a freshness tool called at each file access), as prose in the protocol and skill nodes: verify takes `affected-tests` as the recommended floor of its focused gates; canonize runs `anchors --moved` before the code anchor is recorded again; grow and adopt-existing give scouts the `build` inventory as their file list. The wiring adds no tool contract.
- **Out of scope:**
  - Later work, not slice 2: who references a name (a call graph stays out, below); TS/JS class members and indented declarations that are not exported (function locals), definitions inside shell here-documents and strings, and definitions in other languages; history across renames (`git log --follow`), history as a walk step, and a cached history; a text inventory view (`build --json` carries the inventory).
  - A separate later spec: read deduplication, symbol excerpts and context pointers (overlaps adr-0010).
  - This slice: commands written in host settings files, such as a hook entry in `.claude/settings.json` (`"command": "python3 \".../.claude/route-hook.py\""`). A `json` file is a link target only (§6 "Inventory record"), so such a hook script has no dependent in any answer. Reading them needs one parser per host settings shape, and links come from code by one rule; a later slice may add host settings readers (measurement D3, grill §10).
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
come from Python imports, shell and Python invocations, quoted paths (whole
or joined from segments), and TS/JS imports resolved through `tsconfig` or `jsconfig` aliases. Each row
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
as history and named with `--all`. The `--moved` input is in Slice 2 below.

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

### Slice 2

Slice 2 adds one query, one optional link source and the protocol
wiring. Every slice-2 answer keeps the three kinds: `certain` rows,
`maybe` rows with reason and line, and `incomplete` records with a reason
and the query's one action. Nothing is dropped without a record.

**Ask where a name is defined.** A worker that needs a function, class
or constant asks `symbols` for it by name instead of searching the tree.
The answer lists every definition of the name, each with path, line and
kind; a name defined in several files lists each one, and the tool never
chooses one for the user. A Python definition read by `ast` is
`certain`. A shell function, or a TS/JS declaration at the top level of
its file or exported, is `maybe`, found by line-reading, with that reason.
A function's local variables are not definitions; a nested Python
function is, qualified (`run.inner`); a nested TS/JS function is not. A
name with no definition gives an empty answer, and the answer names what
the tool does not read: files under `docs/graph/` and `.cypress/`, which
are not code, so a name defined only in a seed tool placed in
`docs/graph/` is `undefined` and the worker learns where else to look. A file the tool could not read makes the answer `incomplete`
with the action "search by hand", because that file may define the name.
The query says where a name is defined, not who uses it.

**Add change history as a link source.** With `--history`, `impact` and
`affected-tests` also use files that changed together in past commits.
Each such row is `maybe`, labelled as history, and says the two files
changed together in `count` of `of` commits (`of` is the number of read
commits that changed the input). History rows are listed apart, in their
own `history` list, never mixed with the code-linked rows. A history row
is never `certain`. History only adds rows; it never removes or moves a
row the code links give. If Git history is missing or shallow, the
answer is `incomplete` with that reason. In a shallow clone the oldest
commit it holds is not read, because Git shows that commit as changing
every file. A CI checkout that holds one commit therefore gives no
history rows, and every `--history` answer there is `incomplete` ("run
the full suite"). Without `--history`, no history is read.

**Take code-anchor's moved list.** `anchors --moved` reads the files
that `code-anchor.py` reports as moved since the anchor was recorded, so
the user copies no paths. The answer is the same as when the user names
those files. A missing anchor (or no `code-anchor.py`) gives an
`incomplete` answer with "review by hand"; so does a repository
code-anchor cannot verify, while the other repositories' moved files
are still answered. When nothing moved, the answer is empty and
complete.

**The protocols call the tool on demand.** The tool is never run per
prompt or per file access (ADR-0018); a protocol step runs it once, when
the step needs it.
- At verify, after GREEN and before it chooses its gates, the
  orchestrating session takes `affected-tests` as the recommended floor.
  It may run more tests, never fewer. An `incomplete` answer means it runs
  the full suite.
- At canonize, in flow step 1 and before `code-anchor.py --record`, the
  session runs `anchors --moved` and hands its pages to the docs-librarian
  as the pages whose facts it must re-check. Recording the anchor first
  would empty the list.
- At grow and adopt, before the scouts are briefed, the session gives them
  the `build` inventory (path, language, test class) as the mechanical
  file list, instead of walking the tree.
The tool recommends; the protocol rules decide.

**One citation rule for graph-lint and anchors.** `graph-lint.py` reads
page citations through the same helper as `anchors`. A plant owner sees
both tools agree on which file a page cites. graph-lint's messages and
verdicts do not change. If the helper is missing beside `graph-lint.py`,
the route does not fail: it skips the inferred tier and the session sees
the notice `inference skipped: HelperUnavailable`.

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
  plant in another directory answers from the copied cache unchanged: its
  cache status is `reused`, because the key names no absolute path

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
  outside `docs/graph/` that names `tools/t.py` in backticks. And path joins
  (§6 "Links"), with `tools/u.py`, `tools/v.py` and `src/hooks/h.py` in the
  inventory: `tools/j.py` holding `ROOT / "tools" / "u.py"`,
  `os.path.join(ROOT, "tools", "v.py")` and `ROOT / "templates" / "k" / name`
  over a variable `name`; `tools/w.py` holding
  `(ROOT / "templates" / "k").glob("*.json")`; `tests/j.sh` holding the
  here-document line `TOOL = SEED / "tools" / "u.py"` and the command
  `cp "$SEED"/tools/v.py "$TMP"`; and `src/ext/e.ts` holding
  `path.join(__dirname, "..", "hooks")` and `path.resolve(root, "tools", "u.py")`
- **When:** `build --json` runs
- **Then:** `tools/t.py` holds `maybe` `path-literal` links with reason
  `path-literal` to `tools/frontmatter.py` and `templates/k/lint.py`, and
  `maybe` `path-literal` links with reason `directory` to `templates/k/lint.py`
  and `templates/k/a.json`, each with its line
- **And:** `tools/j.py` and `tests/j.sh` each hold exactly two `maybe`
  `path-literal` links with reason `path-literal`, to `tools/u.py` and
  `tools/v.py`, and `tools/j.py` also the two with reason `directory` to
  `templates/k/lint.py` and `templates/k/a.json` (the literal segments before
  `name`); `tools/w.py` holds those two `directory` links and no `opaque`
  record (a walk whose root is a join that names a directory); `src/ext/e.ts`
  holds one with reason `directory` to `src/hooks/h.py` and one with reason
  `path-literal` to `tools/u.py`; each link's line is the line where its join
  starts
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
  lacks; `import "~/x"` under the paths of the contract above, which map no
  `~`, with no `baseUrl`; `import "./missing"`; `import "@/nope"` under the
  paths of the contract above; `import "./.next/types/routes.d.ts"` where Git
  ignores `.next/`; `import css from "./a.css?raw"`; a Python
  `import app.main` where two inventory files end in `/app/main.py`; and, in
  a file of their own, `import { test } from "bun:test"` and the Python join
  `WORK / "scratch" / name` over a variable `name`, with no `scratch`
  directory in the inventory
- **When:** `build --json` runs
- **Then:** the first five holders are `opaque` records with the reasons
  `dynamic-nonliteral`, `walks-tree`, `unreadable`,
  `alias-config-unavailable` and `unmapped-specifier`; the next four references are `unresolved`
  records with the reasons `relative-no-file`, `alias-no-file`, `generated`
  and `asset`, each with the base path it names; and the ambiguous import is
  two `maybe` links with reason `ambiguous`, one to each candidate
- **And:** none of them is a `certain` link, and the file of their own holds
  no link and no record (a scheme-led specifier is external; a join whose
  literal segments name nothing is no reference)

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
  and invoked by `d.sh` (`python3 b.py`), and `e.py` holding the path literal
  `"a.py"`
- **When:** `impact a.py --json` runs
- **Then:** `dependents` lists `b.py` and `c.py` at depth 1 and `d.sh` at
  depth 2, in that order, each `certain`, with the nearer file it was reached
  from and that link's kind, how it was found and its line (`import a` found
  `resolved` by the Python module search, `python3 b.py` found `exact`, §6
  "Links"), then `e.py` at depth 1, `maybe`, because `certain` rows come first
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
- **And:** `impact a.py --depth 1` lists the same `floor`, `o.py` and `p.py`,
  and its `incomplete` holds exactly one record, `depth-cap` naming `b.py`
  (whose dependent `d.py` the input part did not reach), because the floor
  part has no depth bound and only a cut in the input part makes an answer
  incomplete

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
  `no-test-files`), naming the subject §6 "Incomplete" gives that reason; the rows the walk did reach are still
  listed; and the text view ends with that query's action line (`impact`
  "check by hand", `affected-tests` "run the full suite", `anchors` "review by
  hand")
- **And:** the depth-cap record names the file at depth 3 whose dependent the
  input part did not reach, and the same chain with `--depth 5` is complete

### Affected tests

### Contract: AFFECTED_TESTS_ARE_THE_WALK_FILTERED
- **Given:** `lib.py` imported by `tool.py`, invoked by the test `tests/t.sh`;
  the test `tests/lint.py` importing `lib.py`, itself invoked by the test
  `tests/test-lint.sh`; the test `tests/u_test.py` named as an input beside
  `lib.py`; the test `tests/p_test.py` holding the path literal `"lib.py"`
- **When:** `affected-tests lib.py tests/u_test.py --json` runs
- **Then:** `tests` lists `tests/u_test.py` at depth 0, `tests/lint.py` at
  depth 1, `tests/t.sh` and `tests/test-lint.sh` at depth 2, each `certain`
  with its `via` path from an input, then `tests/p_test.py` at depth 1,
  `maybe`, and no non-test file
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
  line) and the leaf as `certain` `backtick` facts and the `repo: src/a.py`
  node as a `certain` `repo` fact (the `maybe` `repo-prefix` fact is
  `REPO_CLAIM_READ_ALIKE_BY_ROUTER_AND_ANCHORS`'s); it counts the plan, spec and decision pages
  in `history` without naming them
- **And:** the `repo: src/` and `repo: src` nodes claim nothing (a `repo:` that
  holds no `/` once its leading and trailing `/` are cut names a repository
  root: the helper's `repo_claim`, §6 "Helper"), and `src/b.py` is listed as
  `uncited`
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

### Slice 2

Slice-2 contracts run in the same synthetic plant. A `--history` fixture
commits with Git's author and committer dates fixed, so the order of its
commits is the order the fixture writes them; a `--moved` fixture records the
anchor with the placed `docs/graph/code-anchor.py`.

### Definitions

### Contract: SYMBOLS_PYTHON_DEFINITIONS_CERTAIN
- **Given:** `pkg/a.py` holding `TIMEOUT = 5`, `A, B = 1, 2`,
  `type Alias = int`, `from os import path`, `def run():` whose body holds a
  local `x = 1` and a nested `def inner():`, `async def fetch():`, and
  `class Store:` whose body holds `LIMIT = 3` and `def save(self):`; and
  `docs/graph/tool.py` holding `GRAPH_ONLY = 1`
- **When:** `symbols TIMEOUT A Alias run inner fetch Store LIMIT save Store.save x path GRAPH_ONLY --json` runs
- **Then:** each of the first ten names lists one `certain` definition, found
  `ast`, in `pkg/a.py` with its line, its kind (`variable` for `TIMEOUT`, `A`
  and `LIMIT`; `type` for `Alias`; `function` for `run`, `inner`, `fetch` and
  `save`; `class` for `Store`) and its qualified name (`run.inner`,
  `Store.LIMIT`, `Store.save`); `Store.save` lists the definition `save` lists
- **And:** `x` and `path` list no definition and are `undefined`, because a
  local binding and an import define nothing; `incomplete` is empty
- **And:** `GRAPH_ONLY` lists no definition and is `undefined`, the answer's
  `not_read` is `["docs/graph/", ".cypress/"]`, and the text view of
  `symbols GRAPH_ONLY` prints `UNDEFINED_LINE` naming both, because the
  code-path rule makes those trees not code (§6 "Definitions"): the answer
  states its scope instead of reading as "no such name"

### Contract: SYMBOLS_LINE_READ_DECLARATIONS_ARE_MAYBE
- **Given:** `install.sh` holding `place_file() {`, `function helper {` and
  the comment `# fake() {`; and `src/m.ts` holding `export function a(`,
  `export default class B {`, `export const c =`, `let d =`,
  `export interface E {`, `type F =`, `export enum G {`,
  `export async function h(`, `function i(` whose indented body holds
  `const local =` and `function nested(`, `namespace N {` holding an
  indented `export function ns(`, the comment `// function z() {}` and a
  `/* */` block holding `function y() {}`, every other line at column 0
- **When:** `symbols place_file helper fake a B c d E F G h i ns local nested z y --json` runs
- **Then:** each of `place_file`, `helper`, `a`, `B`, `c`, `d`, `E`, `F`,
  `G`, `h`, `i` and `ns` lists one `maybe` definition found `line-reading`,
  with its line and kind (`function` for `place_file`, `helper`, `a`, `h`,
  `i` and `ns`; `class` for `B`; `variable` for `c` and `d`; `type` for `E`,
  `F` and `G`)
- **And:** `local`, `nested`, `fake`, `z` and `y` are `undefined`, because a
  TS/JS declaration counts at column 0 or after `export`, so a function's
  locals define nothing, and the line reading skips comments as the slice-1
  readers do (§6 "Definitions")

### Contract: SYMBOLS_LIST_EVERY_DEFINITION
- **Given:** `def parse` in `tools/a.py` and in `tests/b.py`, `class Reader:`
  holding `def parse(self):` in `tools/c.py`, and `function parse(` in
  `src/p.ts`
- **When:** `symbols parse --json` runs, then `symbols Reader.parse --json`
- **Then:** `parse` lists four definitions, the three `certain` ones first by
  path, then the `maybe` one, and `incomplete` is empty, because a name
  defined in several places is answered by listing each, never by choosing one
- **And:** `Reader.parse` lists the method alone, because a dotted name
  matches a qualified name whole, and the text view of `symbols parse` prints
  one line per definition in the format of §6 "CLI"

### Contract: SYMBOLS_UNREADABLE_FILE_MAKES_IT_INCOMPLETE
- **Given:** `ok.py` holding `def run():`, `bad.py` holding a syntax error,
  and `big.js` larger than `FILE_MAX_BYTES`
- **When:** `symbols run --json` runs
- **Then:** `run` lists the definition in `ok.py`, and `incomplete` holds one
  `unreadable-file` record naming `bad.py` and one naming `big.js`, because a
  file the index could not read may define the name
- **And:** the text view ends with
  `Incomplete: search by hand (unreadable-file: bad.py, unreadable-file: big.js).`

### History

### Contract: HISTORY_ROWS_ARE_MAYBE_WITH_THEIR_COUNT
- **Given:** a plant whose commits, oldest first, change: `a.py` and
  `tests/t_b.sh`; `a.py`, `tests/t_b.sh` and `c.py`; `a.py` alone; and `a.py`
  with `HISTORY_MAX_FILES` other inventory files, `tests/t_wide.sh` among
  them; no link joins `a.py` to `tests/t_b.sh`, `c.py` or `tests/t_wide.sh`
- **When:** `affected-tests a.py --history --json` runs, then
  `impact a.py --history --json`
- **Then:** the first answer's `history` holds `tests/t_b.sh` at depth 1,
  `maybe`, kind `history`, found `history`, from `a.py`, with `together`
  `{count: 2, of: 3}`; the second's holds `tests/t_b.sh`, then `c.py` with
  `{count: 1, of: 3}`, the higher count first
- **And:** no history row is `certain`, and `tests/t_wide.sh` is in no list,
  because a commit that changes more than `HISTORY_MAX_FILES` inventory files
  is not read: it would pair every file it changed, and `of` does not count it

### Contract: HISTORY_ONLY_ADDS
- **Given:** `a.py` imported by `b.py`; `o.py` holding `os.walk(root)` over a
  variable; and commits that each change `a.py` together with `b.py`, `o.py`
  and `d.py`, where no link joins `d.py` to `a.py`
- **When:** `impact a.py --json` runs, then `impact a.py --history --json`
- **Then:** the second answer equals the first in every key but `history`
  and `cache` (the second query reuses the cache the first wrote), and
  the first holds no `history` key
- **And:** `history` holds `d.py` alone, because a file another list of the
  answer holds (`b.py` in `dependents`, `o.py` in `floor`) is never a history
  row: history adds files and never moves or removes a row

### Contract: HISTORY_SHALLOW_OR_MISSING_IS_INCOMPLETE
- **Given:** one of: a plant whose root repository is a clone made with
  `git clone --depth 2 file://<origin>` of an origin whose last three
  commits change, oldest first, `a.py` and `tests/t_old.sh`; `a.py` alone;
  `a.py` and `tests/t_new.sh`; and a plant whose root repository has no
  commit and holds an untracked `a.py`
- **When:** `affected-tests a.py --history --json` runs, then
  `affected-tests a.py --json`
- **Then:** with `--history`, `incomplete` holds one record naming the
  repository `.`: `history-shallow` for the clone, whose `history` still
  holds `tests/t_new.sh` with `together` `{count: 1, of: 1}` and holds no
  `tests/t_old.sh`, because the clone's boundary commit (`a.py` alone) has
  no parent it holds, so Git lists every file it holds and the commit is
  not read; and `history-unavailable` for the plant with no commit; the
  text view ends with `Incomplete: run the full suite (...)`
- **And:** without `--history` neither answer holds such a record, because
  history is read only when asked

### Moved list

### Contract: ANCHORS_MOVED_EQUALS_THE_NAMED_PATHS
- **Given:** a plant whose root repository holds `run.sh` and whose nested
  governed repository `Cypress/` holds `Cypress/tools/x.py`, with the anchor
  recorded by `docs/graph/code-anchor.py --record`; then a commit in
  `Cypress/` that changes `tools/x.py`, an uncommitted edit to `run.sh`, and
  a node citing each file
- **When:** `anchors --moved --json` runs, then
  `anchors Cypress/tools/x.py run.sh --json`
- **Then:** the two documents are equal in every key but `cache` (the second
  query reuses the cache the first wrote), and `inputs` lists
  `Cypress/tools/x.py` and `run.sh`, because each repository-relative path
  code-anchor reports is joined to its repository's plant-relative path
- **And:** after `code-anchor.py --record` runs again, `anchors --moved
  --json` lists no input and no file, `incomplete` is empty, and the text view
  prints `MOVED_NONE_LINE`

### Contract: ANCHORS_MOVED_WITHOUT_A_LIST_IS_INCOMPLETE
- **Given:** the plant of the contract above, then one of: no
  `.cypress/anchor.json`; an anchor whose recorded commit for `Cypress/` the
  clone lacks, with `run.sh` edited; no `docs/graph/code-anchor.py`; a placed
  `code-anchor.py` whose `moved_list` returns a pair whose `paths` is a
  string; a placed `code-anchor.py` whose `moved_list` raises its
  `Unrecorded` and which defines no `ANCHOR_NAME`
- **When:** `anchors --moved --json` runs
- **Then:** `incomplete` holds, in turn: `moved-unavailable` naming
  `.cypress/anchor.json`, with code-anchor's not-recorded reason as detail;
  `moved-unverified` naming `Cypress`, with code-anchor's label as detail,
  while `run.sh` is still an input and answered; `moved-unavailable` naming
  `docs/graph/code-anchor.py`; `moved-unavailable` naming
  `docs/graph/code-anchor.py` and no input (a malformed result, never one
  input per character); `moved-unavailable` naming `.cypress/anchor.json`
  (the subject read inside the guard, with that fallback), never a traceback
- **And:** each text view ends with `Incomplete: review by hand (...)`

### One claim rule

### Contract: REPO_CLAIM_READ_ALIKE_BY_ROUTER_AND_ANCHORS
- **Given:** a plant whose `docs/graph/` holds the seed's `graph-lint.py`
  beside the tool and its siblings, nodes with `repo: src/`,
  `repo: src/lib/` and `repo: src/lib/a.py`, and `src/lib/a.py`,
  `src/lib/c.py` and `src/b.py` in the inventory
- **When:** `anchors src/lib/a.py src/lib/c.py src/b.py --json` runs, and
  `graph-lint.py --plan-json` runs once on a task naming each of the three
  paths
- **Then:** `anchors` lists for `src/lib/a.py` the `repo: src/lib/a.py` node
  as a `certain` `repo` fact and the `repo: src/lib/` node as a `maybe` one
  found `repo-prefix`, for `src/lib/c.py` the `repo: src/lib/` node as a
  `maybe` one, and `src/b.py` as `uncited`; `graph-lint.py` loads by
  `named_path` the `repo: src/lib/a.py` node, then the `repo: src/lib/` node,
  then no node through a `repo:` claim
- **And:** neither tool reads `repo: src/` as a claim, because both call the
  helper's one `repo_claim`, which cuts the leading and trailing `/` and
  reads a value that then holds no `/` as a repository root

## 5. Non-functional requirements

- **Performance:** a full build over a repository of 5,000 inventoried files
  finishes within 5 s and 64 MB peak RSS on the owner's development machine.
  Evidence (the gap scouts' throwaway builds, 2026-10-07): 0.15 s and 15 MB
  RSS on Vivid; 3.8 s on a 4,865-file llama.cpp tree, with import extraction
  only. A query that reuses the cache answers within 1 s on the seed-sized
  plant. Measured once at verify, not gated (grill §10); the 2026-10-07
  measurement, every rule on: 0.67 s and 47 MB on a plant governing a seed
  clone (914 files), 0.66 s and 31 MB on Vivid (397), 3.19 s and 52 MB on a
  4,320-file llama.cpp clone; a cached query 0.10 s on the seed plant. The
  5,000-file figure, about 3.7 s and 55 MB, is inferred by linear scale.
  Slice 2, each measured once at verify (grill §10, increment 22): the build,
  definitions included, keeps the budgets above; a cached `symbols` query
  answers within 1 s on the seed-sized plant; `--history` adds at most 1 s
  there (one `git log` of at most `HISTORY_COMMITS` commits per repository
  holding an input); `graph-lint.py`'s load of the helper adds no measurable
  time to a `--plan` run, which the route hook makes on every prompt.
  Slice-2 measurement (grill §10, increment 22, spawn `measure-slice2`, seed
  `c456299`, Python 3.14): every time budget held (llama.cpp build 3.65 s,
  cached `symbols` 0.10 s on the seed plant, `--history` +0.01 s); peak RSS
  did not: 70 MB on the 4,320-file llama.cpp clone (M2-1). The cause,
  measured by `architect-slice2-m2` on the same clone: a cold build peaks at
  59 MB on 3.14 and 81 MB on 3.11, and a forced `build` over a usable cache at
  72 MB and 93 MB. Two holders, neither the definitions: the cache written
  with `indent` (on 3.11 Python's pure-Python encoder holds every chunk; the
  extract itself peaks at 42 MB on both), and `build` keeping the parsed old
  cache alive across the derive. The budget stays 64 MB, and the build must
  meet it on every supported Python by two reductions: the cache is written
  compact (§6 "Cache document"; the same extract then peaks at 44 MB on 3.14
  and 45 MB on 3.11), and `build` keeps no parsed cache while it derives (it
  needs only whether a cache existed, for the status `rebuilt`). File texts
  are already read one at a time and dropped; no streaming is needed. The
  5,000-file figure after the reductions is inferred at about 60 MB.
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
    citation text, every record's `detail`, code-anchor's labels and reasons
    included), and `--json` is written with
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
  Slice 2, held to the rules above:
  - A definition name is repository content: cut to `LITERAL_MAX`, shown
    with `?` in the text view and escaped in `--json`; a `symbols` input
    that `NAME_RE` does not match whole (`re.fullmatch`) is `USAGE_REFUSED`
    before anything is read. The text view shows an input name through the
    same `?` replacement. The definition reader walks statement bodies with
    an explicit stack and never descends into expressions, so a deep
    expression `ast` parses cannot exhaust it (§6 "Definitions").
  - History reads Git through the helper's one boundary: `git log` with
    `--no-merges`, `--no-renames`, `--no-show-signature`, `--no-color`,
    `-n HISTORY_COMMITS`, `--name-only -z`, a commit marker no Git path can
    equal and no path in argv, so no user or repository setting
    (`diff.renames`, `log.showSignature`, `color.ui`) changes what it reads;
    its output is decoded with `surrogateescape`; each path it names is text
    matched against the inventory, never opened. A `git log` that fails or
    passes `GIT_TIMEOUT` is `history-unavailable`, never a crash. Its output
    is buffered whole before the bulk-commit rule, so memory is bounded by
    `HISTORY_COMMITS` and `GIT_TIMEOUT` only (accepted).
  - `anchors --moved` loads `code-anchor.py` from beside the tool by file
    path, the seed's own placed tool, as the siblings are loaded; the load
    and the call run inside one guard (§6 "Moved list"), so no failure of
    code-anchor crashes the query; its moved list is data, each path joined
    to its repository and held to the helper's `relative` predicate before
    it becomes an input.
  - `graph-lint.py` loads the helper by file path from beside itself, as it
    loads `frontmatter.py`, with `sys.dont_write_bytecode` set first, so a
    routed prompt writes no `__pycache__` into `docs/graph/`; loading the
    helper runs no Git call and reads no file but `frontmatter.py`; its
    `repo_claim` and `path_matches` are string functions that open nothing.

- **Privacy:** the cache holds paths, hashes, link targets, reason codes and
  the names of definitions (identifiers), never a value or other file
  content: `TOKEN = "..."` stores the name `TOKEN` and its line, never the
  string. History is read per query and never stored.
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
  INDEX_SCHEMA: "cypress.source-index/2"      # cache document; /2 adds `symbols` (slice 2)
  ANSWER_SCHEMA: "cypress.source-index.answer/1"   # slice 2 adds a query and keys, removes none
  DEFAULT_DEPTH: 3
  MAX_DEPTH: 5
  TEXT_MAX_ROWS: 40              # rows per list in the text view; --all lifts it
  LITERAL_MAX: 255               # longest string read as a path literal
  JOIN_MAX: 3                    # most following lines a TS/JS line ending in an open call takes (§6 "Links")
  FILE_MAX_BYTES: 1048576        # 1 MiB; a larger link-bearing file is not parsed (INPUT_EXHAUSTS_A_PARSER)
  DIR_LINK_MAX: 200              # most inventory files one directory literal links (DIRECTORY_LITERAL_TOO_WIDE)
  EXTENDS_MAX: 16                # longest tsconfig `extends` chain (TSCONFIG_EXTENDS_CYCLE)
  CACHE_MAX_BYTES: 67108864      # 64 MiB; a larger index.json is neither read nor written
  HISTORY_COMMITS: 500           # most recent non-merge commits --history reads per repository
  HISTORY_MAX_FILES: 40          # a commit changing more inventory files is not read (HISTORY_BULK_COMMIT)
  NAME_RE: '[A-Za-z_$][A-Za-z0-9_$-]*(\.[A-Za-z_$][A-Za-z0-9_$-]*)*'   # a `symbols` input, matched whole (re.fullmatch); else USAGE_REFUSED
  CODE_ANCHOR: "code-anchor.py"  # loaded by file path beside the tool by `anchors --moved` alone; no SIBLING, it shapes no index
  CACHE_DIR: ".cypress/source-index"
  CACHE_NAME: "index.json"
  CACHE_IGNORE: "*\n"            # the inner .gitignore, byte for byte
  CONFIG_PATH: "docs/graph/source-index.json"
  TEST_DECLARATION: "docs/graph/spec-lint.py: TEST_GLOBS"
  SIBLINGS: ["source_paths.py", "plant_walk.py", "frontmatter.py"]   # loaded by file path; digested in the key
  TEST_SKIP_DIRS: fallback       # spec-lint's SKIP_DIRS, read from the placed spec-lint.py; this copy only when absent (§6 "Plant test declaration")
  NOT_CODE, NOISE_DIR, NOISE_NAME, GIT_LOCATORS, GIT_TIMEOUT: helper   # moved from code-anchor.py, unchanged
  DIR_FD_CALLS: helper           # moved from code-anchor.py, with `mkdir` added: {open, stat, unlink, rename, mkdir}
  CITATION_RE, MISSING_CITATION, MALFORMED_CITATION: helper             # moved from growth-audit.py, unchanged
  repo_claim, path_matches: helper   # moved from graph-lint.py's tier 2 (slice 2); graph-lint, anchors and the config call them
  TEMP_PREFIX: ".tmp-source-index-"   # the cache's exclusive temp files
  FLOOR_LINE: "Floor: {n} maybe row(s) every input reaches (opaque holders and their dependents):"
  RECOMMEND_LINE: "Recommendation only: the tests above and the always-run set, never only these; verify decides what runs."
  HISTORY_LINE: "History: {n} maybe row(s), files that changed together with an input (--history):"
  MOVED_NONE_LINE: "Moved: no code moved since the code anchor."
  UNDEFINED_LINE: "{name}: no definition (read: Python definitions, shell functions, TS/JS declarations; not read: {not_read}, which are not code)"   # {not_read}: NOT_CODE joined by ", "
  ACTION_LINE:                   # the closing text line of an incomplete answer
    build: "Incomplete: check by hand ({reasons})."
    impact: "Incomplete: check by hand ({reasons})."
    affected-tests: "Incomplete: run the full suite ({reasons})."
    anchors: "Incomplete: review by hand ({reasons})."
    symbols: "Incomplete: search by hand ({reasons})."
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
edited, because no code-anchor or growth-audit message or verdict changes (one
intended exception, a citation with trailing whitespace: §12, 2026-10-07 code review):
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

Slice 2 moves graph-lint's tier-2 path rule onto the helper, as two string
functions that open nothing, each moved from `graph-lint.py` unchanged:
- `repo_claim(value, path) -> "exact" | "prefix" | None`: the `repo:` value
  cut of its leading and trailing `/` (`str.strip("/")`, nothing else
  normalized); a value that then holds no `/` names a repository root and
  claims nothing (`src`, `src/`); otherwise `exact` when `path` equals it,
  `prefix` when `path` begins with it and `/`, else None. Graph-lint's
  `_named_paths` takes the longest `exact` or `prefix` claim (both sides
  lowercased by graph-lint before the call, as today); `anchors` lists every
  claim, `exact` as a `certain` fact and `prefix` as a `maybe` one found
  `repo-prefix`.
- `path_matches(path, pattern) -> bool`: graph-lint's `_path_matches` with its
  `.lower()` left to the caller: a pattern with no `/` matches the last path
  segment; one with `/` drops its leading `**/` and matches the whole path or
  any `*/`-prefixed tail. Graph-lint lowercases both sides, so its expertise
  inference reads as today; the tool's config patterns (`exclude`,
  `always_run`, `global_inputs`) call it case-sensitive (§6 "Plant test
  declaration and config").

`graph-lint.py` sets `sys.dont_write_bytecode` before it loads
`frontmatter.py`, so neither load writes a `__pycache__` into `docs/graph/`.
It loads the helper by file path from beside itself, in the anchored shape it
loads `frontmatter.py` with, lazily: once per run, the first time tier 2
reads a task path, so a lint run and a route that never reaches tier 2 never
load it. Loading the helper runs no Git call and reads no file but
`frontmatter.py`. A helper that is absent, fails to load, or lacks
`repo_claim` or `path_matches` (an older copy) raises `HelperUnavailable`
inside tier 2, which the router already catches, as it catches any other
exception there (a call whose signature changed raises `TypeError`): tier 2
claims nothing for that run, the route goes on to the next tier, and the
existing `inference_skipped` notice names the exception (`inference
skipped: HelperUnavailable`), which `--plan` prints and the route hook
passes to the session as a `!` line (SPEC-0003 §6 `notices`; no new notice
code). No second copy of the rule is kept for the fallback. In a plant both sit in
`docs/graph/` (the installer places `source_paths.py` with `place_file` on
every install and graft, and `graph-lint.py` with `place_if_missing`, which
only a graft reconciles, so a plain re-install can pair a newer helper with
an older engine: §7 `HELPER_ABSENT_BESIDE_GRAPH_LINT`); in the seed, `templates/knowledge-graph/source_paths.py`
is a byte-identical copy of `tools/source_paths.py`, held so by
`tests/seed-lint.py` as it holds the copies of `frontmatter.py`. The move is
proved by graph-lint's existing suites passing with no assertion edited and
by `REPO_CLAIM_READ_ALIKE_BY_ROUTER_AND_ANCHORS`. One intended change, in
`anchors` only: slice 1 read `repo: src/` as a prefix claim and normalized
the value with `posixpath.normpath`; graph-lint read `src/` as a repository
root and normalized nothing. The one rule is graph-lint's, so its routing is
unchanged and `anchors` stops reading `src/` (and `./src/lib`) as claims
(§12, 2026-10-07, slice 2).

### Inventory record

```yaml
inventory_record:
  path:     { type: string, plant-relative, posix }
  repo:     { type: string, governed repository path, "." for the root }
  hash:     { type: string, git blob sha1 of the content; a symlink hashes its link text;
              "" for a path `content_state` cannot hash (a FIFO, a socket, a failed open) }
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
from the plant root, and files under a `SKIP_DIRS` directory (today `.git`,
`node_modules`, `.venv`, `venv`, `__pycache__`, `dist`, `build`, `target`,
`.next`) or under the specs directory are never tests. Links are read from
`python`, `shell`, `typescript` and `javascript` files; `json` and `other`
files are targets only. A repository whose Git listing fails or times out is
left out of the inventory with a `repository-unreadable` record naming it;
every other repository is inventoried and answers (§7
`REPOSITORY_UNREADABLE`).

### Link, opaque and unresolved records

```yaml
link:                          # the holder depends on the target
  holder: { type: string, inventory path holding the reference }
  target: { type: string, inventory path }
  kind:   { enum: [import, invoke, path-literal] }   # a `directory` link's kind is `path-literal`
  link:   { enum: [certain, maybe] }
  found:  { enum: [exact, resolved,                                   # certain
                   path-literal, directory, ambiguous, workspace-package] }  # maybe: the reason
                   # `named` is never stored: it is the walk's step through an unresolved record
  line:   { type: int, 1-based line of the reference in the holder }
opaque:                        # a holder whose reference may name any file
  holder:    { type: string, inventory path }
  line:      { type: int, or null for unreadable }
  reference: { type: string, as written, cut to LITERAL_MAX }
  reason:    { enum: [dynamic-nonliteral, walks-tree, unreadable, alias-config-unavailable,
                          unmapped-specifier] }
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
  (`tools/code-anchor.py` 53-54, `tools/corpus-match.py` 53-54,
  `tools/graft-audit.py` 169-170). An anchored path held in a variable, a base
  other than `__file__`, or one that no load call takes is not a load: its
  strings stay `path-literal` references, and a load call whose argument is
  not anchored keeps the rules below. The link's line is the line where the
  argument starts.
- Line join (TS/JS only): a line whose code, comments stripped, ends in an
  open `import(`, `require(`, `vi.mock(`, `path.join(` or `path.resolve(` is read joined with the following
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
  link, or one record, and no second one; a quoted string that is a segment of
  a path join (below) is read as part of that join only.
- `path-literal`: any other quoted string (single, double, or a backtick
  string without `${`) of at most `LITERAL_MAX` characters with no
  whitespace and no `://`, in a Python, shell or TS/JS file. It is a `maybe`
  link with reason `path-literal` to the inventory file it resolves to, or,
  when it holds a `/` and resolves to a directory holding inventory files, a
  `maybe` link with reason `directory` to each of them; both are of kind
  `path-literal`, the one kind a quoted string that is no import or invoke
  takes. A string that resolves
  to nothing is not a reference and yields nothing: no `unresolved` or `opaque`
  record ever comes from a path literal.
  In a shell file, a word that joins quoted and unquoted parts with no space
  between them (`"$SEED"/tools/x.py`) is one string, read whole with its
  quotes removed, in place of its quoted parts. An assignment word
  `NAME=...` is read as the value after its `=`.
- Path join: an expression that builds one path from segments is one path
  literal written in pieces. Its forms:
  - Python (read by `ast`): a chain of the `/` operator, `B / s1 / … / sn`, or
    a call `os.path.join(B, s1, …, sn)`, with at least one `si` a string
    literal; `B` is the leftmost operand.
  - Shell and TS/JS (a line at a time, after the TS/JS line join, which also
    joins a line ending in an open `path.join(` or `path.resolve(`): a call
    written `path.join(`, `path.resolve(` or `os.path.join(`, its first
    argument `B` and the arguments after it, up to its `)`, the segments; and,
    in a shell file only, words joined by `/` words with a quoted string after
    the first word (`SEED / "tools" / "x.py"`, the form a Python
    here-document writes), `B` the first word.
  A segment is a literal when it is a string literal (in shell and TS/JS a
  quoted string; an f-string or template string with an interpolation is not
  one), and `B` also when it is `P("<literal>")`, `P` the name bound to
  `pathlib.Path`. The join is read as the string of its segments joined by
  `/`, each non-literal one written as a variable: `ROOT / "tools" / "x.py"`
  reads `$ROOT/tools/x.py`, `path.join(__dirname, "..", "hooks")` reads
  `$__dirname/../hooks`. That string is resolved by the shell-argument and
  path-literal order of "Resolution", in a TS/JS file too (a join names a file
  path, not a module specifier), and held to the `path-literal` bullet above:
  a `maybe` link with reason `path-literal` or `directory`, at the line where
  the join starts, or nothing. A join with no literal segment is not a
  reference. A `__file__` or `__dirname` base is a variable lead, tried from
  the holder's directory first, so a join anchored there is `maybe`: only a
  load call makes an anchored path `certain` ("Load by file path" reads its
  own argument; a load call whose argument is a join that rule does not take
  reads it by this one). A walk call whose root is a join takes it as the
  literal root of the `walks-tree` rule below.
- `certain` links: found `exact` when a relative import, a load by file path
  or an `invoke` argument names the target as written, relative to the holder
  or the repository root (a `path-literal` is never `certain`, wherever it
  resolves);
  found `resolved` when a lookup rule found it (Python module search, a
  `/`-suffix, extension or index probing, `.js` to `.ts`, tsconfig
  `paths`/`baseUrl`, a target in another governed repository). So `import a`
  beside `a.py` is `resolved` (no relative import: the module search found it)
  and `python3 b.py` beside `b.py` is `exact` (the whole string, from the
  holder's directory); a shell string that hits only after a shorter
  `/`-suffix is cut is `resolved`.
- `maybe` links: `path-literal` and `directory` as above; `ambiguous`, one
  link to each candidate of a Python module that several inventory files end
  in; `workspace-package`, one link to each inventory file under the directory
  of a tracked `package.json` whose `name` the bare TS/JS specifier names
  (TS/JS rule under "Resolution"), when no subpath of it probes to a file.
  A `directory` link goes to every inventory file below the directory, at any
  depth. A link set over `DIR_LINK_MAX` (a directory literal, a walk root or a
  workspace package) is no links and one `opaque` `walks-tree` record whose
  reference is the literal or the specifier (§7 `DIRECTORY_LITERAL_TOO_WIDE`).
- Opaque reasons: `dynamic-nonliteral`, an `import()`, `require()`,
  `import_module`, `spec_from_file_location`, `run_path` or `invoke` whose
  argument is no anchored path and neither is nor holds a literal or path
  join that resolves; `walks-tree`, a call of `os.walk`,
  `os.scandir`, `os.listdir`, `.rglob(`, `.glob(`, `glob.glob`, `readdirSync`
  or `readdir`, or a `find` or `git ls-files` command, whose root argument is
  neither a literal nor a path join, or is one that makes no `directory` link by the
  `path-literal` rule (it holds no `/`, is a glob such as `"tools/*.py"`, is
  `.` or a root, or names no directory of inventory files; a `find` root is
  read with a `/` appended): `glob.glob("tools/*.py")`, `os.walk("tools")`,
  `Path("tools").rglob("*.py")` and `find . -name '*.py'` are each `opaque`
  `walks-tree`, so no walk call is dropped in silence (a literal root that
  makes `directory` links is those links); `unreadable`, a file
  of a link-bearing language that cannot be read, decoded as UTF-8 or parsed
  (`ast` SyntaxError); `alias-config-unavailable`, a non-relative, non-package
  specifier under a tsconfig whose `extends` chain names a file the inventory
  lacks, or that the JSONC reader rejects; `unmapped-specifier`, a TS/JS
  specifier that is not relative, not led by `/`, no npm package name and not
  scheme-led, and that no `paths` pattern, `baseUrl` probe or workspace
  package resolves (`~/x` with no `~` alias, `#internal`): the config that maps it (a
  bundler alias, a package `imports` map) is one the tool does not read, so it
  may name any file. It has no base to probe, so an `unresolved` record could
  never reach an answer through a `named` step.
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
  (`GIT_PATH_ARGUMENT`). A base that a foreign directory (`plant_walk.is_foreign`)
  or a nested work tree no `repo:` governs holds is not asked, because Git
  answers such a path with exit 128 for the whole call; it keeps its other
  reason, so no base can cost the repository its `generated` answers.

**Resolution** (one order, tried top-down; the first hit wins; candidates are
plant-relative inventory paths of any governed repository):
- Python module `a.b`: relative imports from the holder's package; otherwise
  `<holder dir>/a/b.py`, `<holder dir>/a/b/__init__.py`, `<repo>/a/b.py`,
  `<repo>/a/b/__init__.py`; then the inventory files ending in `/a/b.py` or
  `/a/b/__init__.py`: one is `resolved`, several are `ambiguous`, none is
  external. `from a.b import c, d` links the module file it finds AND, at the
  same base, each of `…/a/b/c.py`, `…/a/b/c/__init__.py` (and so for `d`) the
  inventory holds, because an imported name may be a submodule: so
  `from pkg import sub` beside `pkg/__init__.py` and `pkg/sub.py` links both.
  The rule is the same in each branch: relative (`from . import sub` links the
  package's `__init__.py` and `sub.py`), the holder's directory, the
  repository root and the suffix fallback (each candidate's submodule files
  share its `ambiguous` or `resolved`). With no module file, the submodule
  files alone are the links (a namespace package).
- Python load by file path: the holder's directory, one directory up for each
  `.parent` or `dirname` after the first, joined with the literals in order and
  normalized; no probing and no suffix search. A target no inventory file
  holds is an `unresolved` record, `relative-no-file` (`outside-repository`
  past the plant root).
- Shell argument and path literal: holder-directory-relative, then each
  `/`-suffix of the string, longest first, as a path relative to the holder's
  repository and then to the plant root (`$ROOT/tools/x.py` tries
  `$ROOT/tools/x.py`, then `tools/x.py`, then `x.py`). When the string's
  leading segments are variables (`$DIR/lib.sh`, `$(dirname "$0")/lib.sh`,
  `${HERE}/a/b.sh`), each suffix after them is tried first from the holder's
  directory, then from the holder's repository and the plant root, so
  `source "$DIR/lib.sh"` in `tests/t.sh` reaches `tests/lib.sh`; a hit from
  the holder's directory is found `resolved`, never `exact`. When nothing
  resolves, the record's `base` is the suffix after the variables from the
  holder's repository (one base per record; under the other reading a deleted
  file is `input-not-found`, an incomplete answer, never a silent drop). A
  string that is only a variable (`"$x"`, `${x}`), or that holds a variable
  after its leading segments (`$A/x/$B`), is `dynamic-nonliteral` when it is
  an `invoke` argument. Otherwise a string that is only a variable is nothing,
  and one that holds a variable after a named segment reads the segments
  before that variable as a directory literal (`$A/x/$B` reads `$A/x/`;
  `ROOT / "tools" / name` reads `$ROOT/tools/`): its `directory` links, or
  nothing when it names no directory of inventory files, since then no base
  this order tries holds an inventory file below it.
- TS/JS specifier: `./` and `../` from the holder's directory; otherwise the
  nearest `tsconfig.json` or `jsconfig.json` up from the holder inside its
  repository, its `extends` chain followed through relative paths to
  inventory files, child keys over parent keys: each `paths` pattern (one
  `*`), then `baseUrl`. An `extends` entry (a string or a list of strings)
  that is not relative names a package config (`@tsconfig/node20`): it is
  skipped and adds no key, and is not `alias-config-unavailable`. A specifier
  that begins with `/` and that no alias matches is `outside-repository`
  (`base` null). A workspace package is matched by the longest `name` that
  equals the specifier or is followed in it by `/`: for `@acme/ui/button`
  under the package `@acme/ui` in `packages/ui/`, the subpath is probed under
  the package directory by the probe list below (`packages/ui/button.ts`), a
  hit being one `certain` `import` link found `resolved`; with no hit, and for
  the bare `name`, the `maybe` `workspace-package` links. A specifier that is
  a valid npm package name (including `@scope/name` and `node:` names; `~`
  begins no npm name, so `~/x` is read by the alias rules alone and, when an
  alias matches it with no file behind it, is `alias-no-file`), is not
  resolved and names no workspace package is external; so is a scheme-led
  specifier, a letter then letters, digits, `+`, `-` or `.` up to a `:`
  (`node:fs`, `bun:test`, `virtual:pwa`). Any other specifier that no rule
  above resolves or records makes its holder `opaque` `unmapped-specifier`. Each base path is probed as written, then
  with `.ts .tsx .d.ts .js .jsx .mjs .cjs .mts .cts .json`, then as
  `<base>/index` with the same list; a written `.js .jsx .mjs .cjs` also
  probes `.ts .tsx .mts .cts`. In a TS/JS file, a path literal resolves by
  these rules and only when it is relative or alias-prefixed, never as a bare
  name.
- The config reader is JSONC: `//` and `/* */` comments and trailing commas
  are removed outside string literals, so `"@/*"` survives.

### Definitions

```yaml
symbol:                        # one definition, read at build with the links (slice 2)
  name:  { type: string, the qualified name within its file, cut to LITERAL_MAX:
           Python joins the enclosing class and function names with "." (`Store.save`,
           `run.inner`); shell and TS/JS hold the declared name alone }
  path:  { type: string, inventory path }
  line:  { type: int, 1-based line of the `def`, `class`, assignment or declaration }
  kind:  { enum: [function, class, variable, type] }
  link:  { enum: [certain, maybe] }
  found: { enum: [ast, line-reading] }   # ast: certain; line-reading: maybe, the reason
```
- Python, read by `ast` from the parse the links already make (`certain`,
  found `ast`): every `def` and `async def` (`function`) and `class`
  (`class`) at any depth; every name an assignment or annotated assignment
  binds, alone or in a tuple or list target, whose nearest enclosing scope is
  the module or a class body, `if`, `try`, `with` and loop blocks included
  (`variable`); a `type X = ...` statement (`type`). An import, a parameter, a
  local binding inside a function, a `global` or `nonlocal` name, an
  attribute target (`self.x = 1`), a `for` or `async for` target, a
  `with ... as` or `except ... as` name, a `:=` target and an augmented
  assignment (`X += 1`; the name's first binding is its definition) define
  nothing: each is a temporary or a rebinding, not a name a worker looks up.
- The Python reader walks statement bodies (module, class, function, `if`,
  `try`, `with`, loop) with an explicit stack and never descends into
  expressions, so a file `ast` parses never fails the reader. A
  `RecursionError` or `MemoryError` in the reader makes the file
  `unreadable`, and the file's definitions are dropped with its links.
- Shell, a line at a time outside comments (`maybe`, found `line-reading`):
  a line whose first words, at any indentation, are `NAME()` or `NAME ()`
  (a `{` may follow) or `function NAME` (`function`). A here-document's
  lines are read like any other, so one that reads like a function is a
  `maybe` row (`LINE_READ_DECLARATION_IN_TEXT`). A shell variable
  assignment defines nothing, and a function name holding a `.`
  (`foo.bar()`, legal in bash) is not read.
- TS/JS, a line at a time after `strip_comments` blanks `//` and `/* */`
  comments (`maybe`, found `line-reading`): a line whose code begins at
  column 0, or after indentation with the word `export`, then any of the
  words `export`, `default`, `declare`, `abstract`, `async` in that order,
  with `function` or `function*` (`function`), `class` (`class`),
  `interface`, `type`, `enum` or `const enum` (`type`), or `const`, `let` or
  `var` (`variable`), then a name. An indented declaration without `export`
  defines nothing: it is a function's local (72 percent of the line-read
  declarations in Vivid were indented `const`, `let` or `var`), or a member
  of a block the reader cannot see, and Python's reader leaves locals out
  alike. The first declarator alone is read (`const a = 1, b = 2` defines
  `a`); a destructuring pattern, an anonymous default export,
  `export { a as b }`, a re-export and a class member define nothing (§2 out
  of scope).
- Each line-reading pattern is an extraction regex of §5 (one line,
  anchored at its start, no nested or overlapping quantifier); the name it
  reads is held to `NAME_RE` without dots, so a line-read name is ASCII.
- Definitions are read from inventory files alone, so the code-path rule
  bounds them: a file under `docs/graph/` or `.cypress/` (the helper's
  `NOT_CODE`), such as a seed tool placed in a plant's `docs/graph/`, holds
  none, and a name defined only there is `undefined`. The `symbols` answer
  states that scope in `not_read` and in `UNDEFINED_LINE`, read from
  `NOT_CODE`, never a copy; it reads no file there and adds no `incomplete`
  record, because the answer is complete for the code it names.
- `json` and `other` files hold no definitions. A link-bearing file with an
  `opaque` `unreadable` record has none either; `symbols` names it in an
  `unreadable-file` record (§6 "Incomplete").
- A name matches a definition when it equals the qualified name whole, or,
  holding no `.`, equals its last segment: `save` and `Store.save` match
  `Store.save`; `Store.save` does not match `save` in another class. Matching
  is case-sensitive and exact; no pattern is read.

### History links

`--history` (on `impact` and `affected-tests`) reads, per query and for each
governed repository holding a `walked` input, `git log --no-merges
--no-renames --no-show-signature --no-color -n HISTORY_COMMITS --name-only
-z --format=/%P` through the helper's `git`, from HEAD. The marker begins
with `/`, which no Git path does, so no file name splits a commit, and it
holds the commit's parents. A commit with no parent is not read: a root
commit, or a shallow clone's boundary commit, whose parent the clone lacks,
so Git lists every file it holds as changed. Each other commit's changed
paths are joined to the repository's plant-relative path and kept when they
are inventory paths. A commit that keeps more than `HISTORY_MAX_FILES`
paths is not read (`HISTORY_BULK_COMMIT`). For each walked input I and each other inventory
path P, `count` is the number of read commits that changed both, and `of` the
number of read commits that changed I. Every P with `count` 1 or more is a
history candidate, from the input with the highest `count` (then the
smaller `of`, then the smaller input path).

```yaml
history_row:                   # a row of the answer's `history` list; the `row` shape plus `together`
  path:     string
  depth:    1
  link:     maybe                # always: history is evidence of change, never of dependency
  from:     string               # the input it changed together with
  kind:     history
  found:    history
  line:     null
  maybe:    { reason: history, holder: <the input>, line: null }
  via:      [<the input>, path]
  together: { count: int, of: int }   # read commits that changed both; read commits that changed the input
```
The `history` list holds each candidate that no other list of the answer
holds (`dependents` or `tests`, `always_run`, `floor`); `affected-tests`
keeps only test-class candidates. It is sorted by `together.count`
(highest first), then path. History rows are never walked: no link step
starts from one, and they change no other list. Before reading, each such
repository is asked `git rev-parse --is-shallow-repository`: only the exact
output `false` reads as complete; any other output (`true`, or the flag
echoed back by a Git older than 2.15) adds a `history-shallow` record, and
the history it holds is still read; a repository
with no commit, or a `git log` that fails or passes `GIT_TIMEOUT`, adds a
`history-unavailable` record and no rows from it. History follows no rename.

### Moved list

`anchors --moved` takes no path. It loads `CODE_ANCHOR` from beside the
tool by file path and calls the one function its `--compare` prints from,
`moved_list(root)`, which returns, per recorded repository, its
plant-relative path and the `(label, paths)` pairs `moved()` gives today
(slice 2 adds the function to `code-anchor.py` and `--compare` calls it, its
output unchanged). Each moved path is joined to its repository's path
(`source_paths.plant_path`) and held to `relative`; the inputs are those
paths, normalized and answered as §6 "Inputs" answers named paths, so the
answer equals `anchors <those paths>`. A repository whose only label is
`unverified (...)` adds a `moved-unverified` record (the label is the
detail); code-anchor's `Unrecorded` (no anchor, unreadable, another version)
adds `moved-unavailable` naming `.cypress/anchor.json` (its reason is the
detail); code-anchor's `GitMissing` is the `git-unavailable` record the
answer already holds. The load and the call of `moved_list` run inside one
guard: any other exception, `SystemExit` included, a `CODE_ANCHOR` that is
absent, a missing `moved_list` (a placed code-anchor older than slice 2) or
a result not of the shape above (a `paths` that is not a list or tuple of
strings, a label that is not a string) adds `moved-unavailable` naming
`docs/graph/code-anchor.py`. The `.cypress/anchor.json` subject of an
`Unrecorded` record is read inside the guard, from code-anchor's
`ANCHOR_DIR` and `ANCHOR_NAME`, with `.cypress/anchor.json` the fallback. Code-anchor loads the helper as a module instance
of its own, so the tool catches code-anchor's classes (`Unrecorded`, and its helper's
`GitMissing` and `GitFailed`), never its own. `moved_list(root)` and the
anchor read it calls take the root as a parameter (code-anchor's `--compare`
passes its `ROOT`). An empty moved list is a complete answer with no input;
its text view prints `MOVED_NONE_LINE`.

### Plant test declaration and config

The tests are the plant's `TEST_GLOBS` (read with `ast.literal_eval` from the
top-level assignment in `docs/graph/spec-lint.py`; a list of strings or
nothing). `SKIP_DIRS` is read from the same file by the same reading (a set
or list of strings), so spec-lint stays its one home; the tool's
`TEST_SKIP_DIRS` copy serves only when that assignment is absent or not
strings. `SKIP_DIRS` is seed-owned and changes only by graft, which rebuilds
the cache (`GRAFT_REBUILDS_THE_CACHE`), so it is not in the key. The optional
plant-owned config, never placed by the installer:

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
  # with "/" (any leading "**/" dropped) the whole plant-relative path or any
  # "*/"-prefixed tail: the helper's `path_matches`, the rule graph-lint's
  # tier 2 calls. Case-sensitive by decision: these patterns name real files,
  # whose names Git keeps case-sensitive; graph-lint lowercases both sides
  # because it matches lowercased task text.
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
never stops at a test. The input part stops at `--depth`: a file it reaches
at that depth with a dependent that neither part lists is a `depth-cap`
record. The floor part has no depth bound: `--depth` bounds the distance from
an input, and the floor is the index's, not the input's; it runs until it
reaches no new file, one pass over the links, so no floor row is ever cut and
the floor adds no `incomplete` record. A floor row's depth counts from its
opaque holder (depth 1).

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
- With `--history`, `impact` and `affected-tests` add the `history` list of
  §6 "History links" after the input rows; no other list changes.
- `symbols`: the definitions of each name (§6 "Definitions"); it does not
  walk links.

### Incomplete

An answer is `incomplete` when `incomplete` holds a record; its text view
then ends with the query's `ACTION_LINE`.

```yaml
incomplete_record:
  reason:     { enum: [see table] }
  subject:    { type: string, never empty: the table's Subject column }
  candidates: { type: array of path, ambiguous-input and ambiguous-citation only, else [] }
  detail:     { type: string|null, e.g. the refused config's error or the citation text }
```
| Reason | Trigger | Subject | Queries |
|---|---|---|---|
| `git-unavailable` | no `git` on PATH | `git` | all |
| `no-repository` | no governed Git repository | `.` (the plant root) | all |
| `repository-unreadable` | a Git call for one repository failed or timed out | the repository's plant-relative path | all |
| `config-refused` | `docs/graph/source-index.json` refused | `docs/graph/source-index.json` (the error is the detail) | all |
| `global-input` | an input matches `global_inputs` | the input | all |
| `outside-plant` | an input outside the plant root | the input | all |
| `ambiguous-input` | a repository-relative input several repositories hold | the input | all |
| `input-not-found` | an input no rule of "Inputs" takes | the input | impact, affected-tests |
| `depth-cap` | a file the input part reaches at `--depth` has a dependent neither part lists | that file at the cut depth (`f4.py` for `f1.py`, `--depth 3` over `f1` to `f5`), one record each | impact, affected-tests |
| `no-test-declaration` | `TEST_GLOBS` absent, unparsable or not a list of strings | `docs/graph/spec-lint.py` | affected-tests |
| `no-test-files` | `TEST_GLOBS` matches no inventory file | `docs/graph/spec-lint.py` | affected-tests |
| `ambiguous-citation` | a bare-name citation several inventory files match, one an input | the page (the citation is the detail) | anchors |
| `unreadable-file` | a link-bearing inventory file with an `opaque` `unreadable` record | that file | symbols |
| `history-shallow` | a repository holding a walked input is a shallow clone | the repository's plant-relative path | impact, affected-tests, with `--history` |
| `history-unavailable` | that repository has no commit, or its `git log` failed or timed out | the repository's plant-relative path (the error is the detail) | impact, affected-tests, with `--history` |
| `moved-unavailable` | code-anchor has no usable anchor, or `code-anchor.py` is absent or fails to load | `.cypress/anchor.json`, or `docs/graph/code-anchor.py` (the reason is the detail) | anchors `--moved` |
| `moved-unverified` | code-anchor labels a recorded repository `unverified` | the repository's plant-relative path (the label is the detail) | anchors `--moved` |

"The input" is the input as `plant_relative` normalizes it (§6 "Inputs"), so
it equals the input given in its normal form; an input it cannot make
plant-relative (`outside-plant`) is named as written. "All" is every query
that takes paths; `symbols` takes names, so of the reasons above it gives
`git-unavailable`, `no-repository`, `repository-unreadable` and
`unreadable-file` alone.

### Cache document

```yaml
# .cypress/source-index/index.json, written sorted and compact (separators "," and ":", no indent), trailing newline
index:
  schema: "cypress.source-index/2"
  key:
    python: { the running interpreter's major.minor, e.g. "3.12": `ast` parses by its grammar }
    tool:   { sha256 of source-index.py bytes, then each SIBLINGS file's bytes in that order }
    config: { sha256 of the config file bytes (or ""), then of the TEST_GLOBS repr }
    repositories:
      - { path: string, head: sha1, dirty: sha256 over the sorted "path\0blob\n" lines of its uncommitted code paths }
        # the uncommitted paths the inventory keeps (`is_code`, no foreign directory on the way), so nothing
        # is hashed through a symlinked directory; blob is `content_state`'s, "" when it cannot hash
  inventory:  [inventory_record]   # sorted by path
  links:      [link]               # sorted by holder, target, kind, line
  opaque:     [opaque]             # sorted by holder, line
  unresolved: [unresolved]         # sorted by holder, line, reference
  symbols:    [symbol]             # sorted by path, line, name (slice 2)
```
A document whose `schema` or `key` differs from the current one, or which is
not this shape, is rebuilt: one that is not JSON, breaks this shape, holds
another `schema` or exceeds `CACHE_MAX_BYTES` is unreadable (reason
`cache unreadable`, §7 `CACHE_UNREADABLE`); one whose `key` alone differs is a
key change. The shape check holds each `symbols` record to: `path` an
inventory path, `line` an int of 1 or more, `name` a string of at most
`LITERAL_MAX` with no NUL, `kind`, `link` and `found` from their enums,
`found: ast` with `link: certain` and `line-reading` with `maybe`; a record
that breaks it makes the document unreadable. Anchors citations are read
from the pages on every query and never cached. The key leaves out Git's ignore sources outside
the work tree (`.git/info/exclude`, the user's `core.excludesFile`): an edit
there changes the inventory without a rebuild until the next key change or a
`build` (ADR-0029, accepted gap).

### Query answer

```yaml
answer:
  schema: "cypress.source-index.answer/1"
  query:  { enum: [build, impact, affected-tests, anchors, symbols] }
  inputs: [{ path, status: [walked, not-code, not-found] }]   # walked or answered inputs
  depth:  int                            # impact and affected-tests
  cache:  { status: [built, reused, rebuilt, not-written], reason: string|null }
          # reason: the cause for not-written (§7); "cache unreadable" for a
          # rebuild of a document CACHE_UNREADABLE names; "build forced" for a
          # `build` over a cache that existed, whose key held or not (status
          # rebuilt); else any text or null
  incomplete: [incomplete_record]
  # build
  inventory: [inventory_record]
  links: [link]
  opaque: [opaque]
  unresolved: [unresolved]
  symbols: [symbol]
  # impact (dependents) and affected-tests (tests); both list the floor apart
  dependents: [row]
  tests:      [row]
  always_run: [{ path, reason: [declared, no-code-edge] }]
  floor:      [row]                      # the rows every input reaches; see "Walk"
  history:    [history_row]              # with --history only; the key is absent without it
  # symbols (inputs is [] : the names are in `names`)
  not_read: [string]                     # the helper's NOT_CODE, in its order: what holds no definition
  names: [{ name,
            definitions: [symbol],       # sorted by link (certain first), then path, then line
            undefined: bool }]           # true when `definitions` is empty
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
  kind:  { enum: [import, invoke, path-literal, opaque, history], or null at depth 0 }
  found: { enum: [exact, resolved, path-literal, directory, ambiguous, workspace-package,   # a link's found
                   named, history,                                                        # a walk step; a history row
                   dynamic-nonliteral, walks-tree, unreadable, alias-config-unavailable,  # an opaque reason
                   unmapped-specifier],
           null at depth 0 }
  line:  int|null
  maybe: { reason, holder, line } | null      # the maybe link nearest the start of the chain
  via:   [path]                               # input (floor: opaque holder) first, this path last
```
Every list is sorted: `dependents` and `tests` by link (`certain` first),
then depth, then path, so the `certain` rows come first and the input's own
`maybe` rows after them; `floor` by depth, then path; facts by link (`certain`
first), then page, then line; `history` and `names` as their shapes say;
every other list by its fields in the order the shape names them. `inputs`
lists each input once, sorted.

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
mode: plant-relative only, line checked. Every node's `repo:` is read by the
helper's `repo_claim` (§6 "Helper"): it claims each input it equals
(`certain`) or is a directory prefix of (`maybe`, found `repo-prefix`), all
such nodes listed, longest claim first; a `repo:` that holds no `/` once its
leading and trailing `/` are cut claims nothing. Pages under `docs/graph/plans/`, `specs/` and
`decisions/` are `history`; every other page is a `fact`.

### CLI

```
python3 docs/graph/source-index.py --help
python3 docs/graph/source-index.py build [--json]
python3 docs/graph/source-index.py impact         [--depth N] [--history] [--all] [--json] <path>... | -
python3 docs/graph/source-index.py affected-tests [--depth N] [--history] [--all] [--json] <path>... | -
python3 docs/graph/source-index.py anchors                  [--all] [--json] <path>... | - | --moved
python3 docs/graph/source-index.py symbols                  [--all] [--json] <name>... | -
```
`--help` prints the usage and exits 0. `build` derives the whole index and
writes the cache whatever the key says (the forced rebuild of §3); the queries
build only on a missing, unreadable or mismatched cache. `-` reads one path
per stdin line (`git diff --name-only`), for `symbols` one name. `--depth`
takes 1 to `MAX_DEPTH`. `--history` reads Git history per query (§6 "History
links"). `--moved` takes no path; a path or `-` beside it is refused, as is a
`symbols` name `NAME_RE` does not match whole (`USAGE_REFUSED`).
`--all` lifts `TEXT_MAX_ROWS` and names history pages. The text view prints
the cache line (`Cache: <status>`, then ` (<reason>)` when there is one),
then for `build` one count line and nothing else (`Index: <n> file(s), <n>
test(s), <n> certain and <n> maybe link(s), <n> opaque and <n> unresolved
record(s), <n> definition(s)`; the records themselves are in `--json`), for the walks one row per line
(`<depth> <link> <path>  <- <from> [<kind> <found>:<line>]`, a `maybe` row
adding `maybe: <reason> at <holder>:<line>`), the `certain` rows first, then
the input's `maybe` rows, then, with `--history`, `HISTORY_LINE` and the
history rows (`1 maybe <path>  <- <from> [history <count>/<of>]`), for
`anchors` one block per file (`MOVED_NONE_LINE` alone when `--moved` finds
nothing moved), for `symbols` one block per name (`<name>: <n>
definition(s)`, then one line per definition, `  <link> <kind>
<path>:<line> <qualified name> (<found>)`, or `UNDEFINED_LINE`), then the
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
- **Contract:** WALK_INCOMPLETE_NAMES_REASON_AND_ACTION,
  SYMBOLS_LIST_EVERY_DEFINITION, ANCHORS_MOVED_EQUALS_THE_NAMED_PATHS
- **Trigger:** an unknown query or option (`--history` on `anchors` or
  `symbols`, `--moved` on any query but `anchors`), `--depth` outside 1 to
  `MAX_DEPTH`, no path and no `-` (and, for `anchors`, no `--moved`), a path
  or `-` beside `--moved`, or a `symbols` name `NAME_RE` refuses (`--help` is
  not refused: exit 0)
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
- **Trigger:** a directory literal (quoted, or read from a path join) or one of its `/`-suffixes is empty or names
  a root (`"/"`, `"./"`, `"$ROOT/"`), or resolves to a directory holding more
  than `DIR_LINK_MAX` inventory files at any depth; or a bare TS/JS specifier
  names a workspace package holding more than `DIR_LINK_MAX` inventory files;
  strings such as `"/"` in `split("/")` are common, so without a bound each
  holder would link to every file
- **Response:** the empty suffix and a string with no named segment never
  resolve; a directory over `DIR_LINK_MAX` yields no per-file links and makes
  the holder `opaque` with reason `walks-tree` and the literal (or the
  specifier) as its reference, so the link count stays linear
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

### Failure: DEFINITIONS_UNREADABLE
- **Contract:** SYMBOLS_UNREADABLE_FILE_MAKES_IT_INCOMPLETE
- **Trigger:** a link-bearing inventory file the build could not read,
  decode or parse (its `opaque` `unreadable` record: a syntax error, a file
  over `FILE_MAX_BYTES`, bytes that are not UTF-8, a FIFO)
- **Response:** exit 0; the definitions read elsewhere are listed; one
  `unreadable-file` record per such file; the text view ends with the
  `symbols` `ACTION_LINE`
- **Side effects:** none; nothing is read at query time
- **Recovery:** search that file by hand, or fix it

### Failure: LINE_READ_DECLARATION_IN_TEXT
- **Contract:** SYMBOLS_LINE_READ_DECLARATIONS_ARE_MAYBE
- **Trigger:** a shell here-document, or a TS/JS template literal spanning
  lines, holds a line that reads like a declaration (`function x() {` inside
  a test fixture written as a string)
- **Response:** a `maybe` definition found `line-reading`, which is why no
  line-read definition is `certain`; a declaration the line reading cannot
  see (a class member, a second declarator, an indented TS/JS declaration
  without `export`) is no definition (§2), never a `certain` absence
- **Side effects:** none
- **Recovery:** none needed; the reader opens the line

### Failure: HISTORY_SHALLOW
- **Contract:** HISTORY_SHALLOW_OR_MISSING_IS_INCOMPLETE
- **Trigger:** with `--history`, a repository holding a walked input is a
  shallow clone, as a CI checkout often is (`actions/checkout` fetches one
  commit unless told otherwise): `git rev-parse --is-shallow-repository`
  prints anything but `false`
- **Response:** the history it holds is read and its rows listed, the
  boundary commit left out (it has no parent the clone holds, so Git lists
  every file as changed); a `history-shallow` record names the repository;
  the text view ends with the query's `ACTION_LINE`, so an opt-in `maybe`
  source turns an otherwise complete answer into "run the full suite",
  which fails toward more
- **Side effects:** none; the tool never fetches
- **Recovery:** `git fetch --unshallow`, or read the answer without history

### Failure: HISTORY_UNAVAILABLE
- **Contract:** HISTORY_SHALLOW_OR_MISSING_IS_INCOMPLETE
- **Trigger:** with `--history`, a repository holding a walked input has no
  commit, or its `git log` fails or passes `GIT_TIMEOUT`
- **Response:** no history row from that repository; a
  `history-unavailable` record names it, with the error as detail; the other
  lists stand
- **Side effects:** none
- **Recovery:** commit, or repair the repository; the code links still answer

### Failure: HISTORY_BULK_COMMIT
- **Contract:** HISTORY_ROWS_ARE_MAYBE_WITH_THEIR_COUNT
- **Trigger:** a read commit changes more than `HISTORY_MAX_FILES` inventory
  files (a rename sweep, a vendored drop, a formatter run)
- **Response:** the commit is not read: it adds to no `count` and no `of`,
  so it cannot make every file it touched a history row of every other
- **Side effects:** none
- **Recovery:** none needed; the code links answer for such files

### Failure: MOVED_LIST_UNAVAILABLE
- **Contract:** ANCHORS_MOVED_WITHOUT_A_LIST_IS_INCOMPLETE
- **Trigger:** `anchors --moved` with no `.cypress/anchor.json`, one code-anchor
  refuses (unreadable, another version), or no `docs/graph/code-anchor.py`
  beside the tool, one that fails to load, one with no `moved_list` (placed
  before slice 2), or any other exception or malformed result from its load
  or call (§6 "Moved list")
- **Response:** exit 0; no input; a `moved-unavailable` record with the
  reason as detail; the text view ends with the `anchors` `ACTION_LINE`
- **Side effects:** nothing written; the tool never records an anchor
- **Recovery:** canonize records the anchor; an install places
  `code-anchor.py`

### Failure: MOVED_REPOSITORY_UNVERIFIED
- **Contract:** ANCHORS_MOVED_WITHOUT_A_LIST_IS_INCOMPLETE
- **Trigger:** code-anchor labels a recorded repository `unverified` (no Git
  work tree there now, a recorded commit the clone lacks, a Git failure)
- **Response:** that repository adds no input and one `moved-unverified`
  record with the label as detail; the other repositories' moved paths are
  answered
- **Side effects:** none
- **Recovery:** fetch the recorded commit, or review that repository's
  facts by hand

### Failure: HELPER_ABSENT_BESIDE_GRAPH_LINT
- **Contract:** REPO_CLAIM_READ_ALIKE_BY_ROUTER_AND_ANCHORS
- **Trigger:** `graph-lint.py` reaches tier 2 with no usable `source_paths.py`
  beside it: none (a hand-copied engine, a plant whose last install predates
  the helper), one that fails to load, or one whose `repo_claim` or
  `path_matches` is missing or no longer takes graph-lint's call. The likely
  form is the reverse skew: a plain re-install fast-forwards the helper
  (`place_file`) while the engine (`place_if_missing`) keeps its older calls
  until a graft reconciles it
- **Response:** `graph-lint.py` exits as it would otherwise; tier 2 claims
  nothing for that run, the route goes on to the next tier, and the notice
  `inference skipped: HelperUnavailable` (or the call's exception name) is
  printed by `--plan` and passed to the session by the route hook as a `!`
  line; lint runs never load the helper; nothing guesses a claim rule and
  no copy of it is kept
- **Side effects:** none
- **Recovery:** an install or graft places `source_paths.py` (`place_file`
  on every run); a graft reconciles the engine

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
    - { path: Cypress/tools/graft-audit.py,  depth: 1, link: certain, from: Cypress/tools/plant_walk.py, kind: import, found: exact, line: 170 }
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

Slice 2. Figures from a temp plant over a clone of the seed at
`experimental/source-index` (913 inventory files: 48 Python, 34 shell, 2
TypeScript; no `unreadable` record; 169 non-merge commits), a throwaway `ast`
and line scan standing in for the unbuilt query, and this plant's own
`code-anchor.py --compare` output, all on 2026-10-07; outputs abbreviated.

```yaml
# Happy: the seed, a Python definition (a `def cite_problem` search, discovery report class C)
input:  symbols cite_problem --json
output:
  names:
    - name: cite_problem
      definitions:
        - { name: cite_problem, path: tools/source_paths.py, line: 363, kind: function, link: certain, found: ast }
      undefined: false
  incomplete: []
```

```yaml
# Edge: the seed, a shell function (the discovery report's `place_file` searches)
input:  symbols place_file
output: |
  Cache: reused
  place_file: 1 definition(s)
    maybe function install.sh:389 place_file (line-reading)
```

```yaml
# Edge, many: the seed, one name in five files, three of them the byte-identical
# frontmatter.py copies; `symbols main` lists 29 definitions the same way
input:  symbols parse --json
output:
  names:
    - name: parse
      definitions:   # each certain, found ast, kind function
        - { path: integrations/claude-code/frontmatter.py, line: 69 }
        - { path: templates/knowledge-graph/frontmatter.py, line: 69 }
        - { path: tests/test_frontmatter_contract.py, line: 32 }
        - { path: tools/frontmatter.py, line: 69 }
        - { path: tools/source-index.py, line: 1943 }
  incomplete: []
```

```yaml
# Edge: the seed, history in a test-first repository. RED and GREEN land in
# separate commits: tools/source-index.py changed in 5 read commits and no
# test changed in any of them; install.sh changed in 25 read commits (at most
# 40 inventory files each), tests/test-full-install.sh in 12 of them
input:  affected-tests tools/source-index.py --history --json
output:
  tests: [ ... the code-linked rows, as without --history ... ]
  history: []        # no test changed together with it; the code links carry the answer
  incomplete: []
```

```yaml
# Happy: this plant; code-anchor --compare reported Cypress commit 00f8824..a36da40
# (three paths) and one uncommitted path
input:  anchors --moved --json
output:
  inputs:
    - { path: Cypress/docs/decisions/adr-0029-source-index-is-derived-scratch.md, status: walked }
    - { path: Cypress/docs/decisions/index.md, status: walked }
    - { path: Cypress/docs/plans/grill-8.1.0-source-index.md, status: walked }
    - { path: Cypress/docs/specs/SPEC-0007-source-index.md, status: walked }
  files: [ ... the pages citing each, as `anchors <those four paths>` lists them ... ]
  incomplete: []
```

```yaml
# Edge: this plant's repo: values (5 nodes `repo: Cypress`, 2 `repo: Cypress/tools`,
# 1 `repo: Cypress/templates/`); one rule in both tools
input:  anchors Cypress/tools/code-anchor.py; graph-lint.py --plan "edit Cypress/tools/code-anchor.py"
output:
  # anchors: the two `repo: Cypress/tools` nodes, maybe, repo-prefix; the
  #   `repo: Cypress` nodes claim nothing (a repository root)
  # graph-lint: a `repo: Cypress/tools` node by named_path, as before slice 2
```

```yaml
# Failure: a CI checkout (`git clone --depth 1`) asked for history
input:  affected-tests tools/code-anchor.py --history
output: |
  ...
  - incomplete: history-shallow: .
  Incomplete: run the full suite (history-shallow: .).
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

### Slice 2

- [ ] AC-13: `symbols NAME` lists each Python `def`, `async def`, `class`,
  module- or class-level assignment and `type` statement that defines NAME
  as a `certain` row found `ast`, with path, line, kind and qualified name;
  a dotted name such as `Store.save` matches the qualified name whole; an
  import, a parameter or a local binding inside a function defines nothing,
  so a name bound only that way is `undefined` with `incomplete` empty —
  maps to SYMBOLS_PYTHON_DEFINITIONS_CERTAIN
- [ ] AC-14: A shell function (`NAME()` or `function NAME`) or a TS/JS
  declaration (`function`, `class`, `interface`, `type`, `enum`, `const`,
  `let`, `var`, after any `export`/`default`/`declare`/`abstract`/`async`)
  is listed as a `maybe` row found `line-reading`, with path, line and kind,
  and is never `certain`; a TS/JS declaration counts only at column 0 or
  after `export`, so an indented declaration without `export` (a function's
  local) is no definition; a declaration inside a comment is no definition —
  maps to SYMBOLS_LINE_READ_DECLARATIONS_ARE_MAYBE
- [ ] AC-15: A name defined in N files lists N definitions, the `certain`
  ones first by path, then the `maybe` ones; the tool never picks one, and
  the text view prints one line per definition — maps to
  SYMBOLS_LIST_EVERY_DEFINITION
- [ ] AC-16: A link-bearing file the index could not read (a syntax error,
  a file over `FILE_MAX_BYTES`) adds one `unreadable-file` record naming
  it, the definitions read elsewhere are still listed, the exit code is 0,
  and the text view ends with `Incomplete: search by hand (...)` — maps to
  SYMBOLS_UNREADABLE_FILE_MAKES_IT_INCOMPLETE
- [ ] AC-17: With `--history`, a file that changed together with an input
  and that no other list holds is a row in the answer's separate `history`
  list: `maybe`, kind and found `history`, with `together` `{count, of}`
  equal to the number of read commits that changed both and the number that
  changed the input; rows are sorted by `count`, highest first; a commit
  that changes more than `HISTORY_MAX_FILES` inventory files adds to no
  `count` and no `of`; `affected-tests` keeps only test-class history rows —
  maps to HISTORY_ROWS_ARE_MAYBE_WITH_THEIR_COUNT
- [ ] AC-18: An answer with `--history` equals the same answer without it
  in every key but `history` and `cache`; a file already in `dependents`, `tests`,
  `always_run` or `floor` is never a history row; without `--history` the
  answer holds no `history` key — maps to HISTORY_ONLY_ADDS
- [ ] AC-19: With `--history`, a shallow clone (any
  `git rev-parse --is-shallow-repository` output but `false`) adds one
  `history-shallow` record naming the repository and still lists the
  history rows its commits give, except its boundary commit (the one whose
  parent the clone does not hold), which is not read; a repository with no commit (or a failing `git log`) adds
  one `history-unavailable` record and no history rows; each text view ends
  with the query's action line; without `--history` neither record appears —
  maps to HISTORY_SHALLOW_OR_MISSING_IS_INCOMPLETE
- [ ] AC-20: After a commit and an uncommitted edit since the anchor was
  recorded, `anchors --moved --json` equals `anchors <the moved paths>
  --json` in every key but `cache`, each repository-relative path joined
  to its repository's plant-relative path; after `code-anchor.py --record` runs again, it lists
  no input and no file, `incomplete` is empty, and the text view prints
  `MOVED_NONE_LINE` — maps to ANCHORS_MOVED_EQUALS_THE_NAMED_PATHS
- [ ] AC-21: `anchors --moved` exits 0 and holds one `moved-unavailable`
  record when `.cypress/anchor.json` is missing (naming it) or
  `docs/graph/code-anchor.py` is missing (naming it); a repository
  code-anchor labels unverified adds one `moved-unverified` record naming
  it while the other repositories' moved paths are still answered; each
  text view ends with `Incomplete: review by hand (...)` — maps to
  ANCHORS_MOVED_WITHOUT_A_LIST_IS_INCOMPLETE

REPO_CLAIM_READ_ALIKE_BY_ROUTER_AND_ANCHORS has no criterion yet: the
owner's `repo:` ruling is open (grill §12 question 6). Its criterion will
also hold HELPER_ABSENT_BESIDE_GRAPH_LINT: a missing helper costs tier 2
only, with the `inference_skipped` notice.

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

Slice 2 (`tester-slice2-s10`, 2026-10-07): labels `X450` to `X459`, one case
per slice-2 contract in the same suite, each slice-2 failure an arm of its
contract's case. The file cells read `(new case)` until RED lands (binding
below). Fixtures, all from §4 "Slice 2" and §6: history plants are synthetic
repositories with scripted commits, author and committer dates fixed, the
plant's own files committed first and apart from the counted commits; the
shallow plant is cloned with a `file://` URL, because Git ignores `--depth`
for a local path; the moved and claim cases also copy `code-anchor.py` and
`graph-lint.py` into `<plant>/docs/graph/`. X445 and X447 return to
`pending`: slice 2 turns one X445 arm and widens `USAGE_REFUSED`.

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
architect confirmed all of them on 2026-10-07 (`architect-readings`), and §4
and §6 now state each:
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
| BUILD_INVENTORIES_THE_CODE_OF_EVERY_GOVERNED_REPOSITORY | X425 case_build_inventory | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| BUILD_IS_DETERMINISTIC | X426 case_build_deterministic | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| CACHE_WRITTEN_SELF_IGNORED | X427 case_cache_self_ignored: arm (a) | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| CACHE_REUSED_WHILE_THE_KEY_HOLDS | X428 case_cache_reused; arm m4, a tracked `d/` replaced by a symlink to an outside directory: an edit there leaves the second query `reused` | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| CACHE_REBUILT_WHEN_THE_KEY_CHANGES | X429 case_cache_rebuilt: arms (a) to (d) and (f), one per key change, (f) another Python major.minor in the key | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| GRAFT_REBUILDS_THE_CACHE | X430 case_graft_rebuilds | tests/test-source-index.sh | integration (install.sh over a temp plant) | green |
| LINK_PYTHON_IMPORT_CERTAIN | X431 case_link_python_import: exactly seven certain import links, five found exact (three loads by file path) and two resolved; no path-literal link from a load argument | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| LINK_SHELL_INVOCATION_CERTAIN | X432 case_link_shell_invocation | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| LINK_PATH_LITERAL_AND_DIRECTORY_ARE_MAYBE | X433 case_link_path_literal: the anchored `frontmatter.py` path no load call takes is a maybe path-literal link; arm joins, the path joins of `tools/j.py`, `tools/w.py`, `tests/j.sh` and `src/ext/e.ts`, each link at the join's start line | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| LINK_TS_SPECIFIER_CERTAIN | X434 case_link_ts_specifier: six files, the sixth the line-join arm | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| UNPINNED_REFERENCE_RECORDED_WITH_ITS_REASON | X435 case_unpinned_reference; arm R1, `import "~/x"` is opaque `unmapped-specifier`, and `bun:test` and `WORK / "scratch" / name` hold no link and no record; arm baseUrl, under `baseUrl: "."` with no matching `paths`, `~/gone`, `#internal` and `Foo/bar` (no file) are each opaque `unmapped-specifier` | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| TESTS_ARE_THE_PLANTS_TEST_GLOBS | X436 case_test_globs | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| PLANT_CONFIG_REPLACES_EACH_DEFAULT_KEY | X437 case_plant_config_keys | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| WALK_NEAREST_FIRST_ONCE | X438 case_walk_nearest_first: certain rows first, then a maybe row | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| WALK_CHAIN_IS_ITS_WEAKEST_LINK | X439 case_walk_weakest_link | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| WALK_FLOOR_LISTED_APART_AFTER_THE_INPUT_ROWS | X449 case_walk_floor: `impact a.py` then `impact z.py`, JSON and the text view; arm D4, `impact a.py --depth 1` keeps the floor `o.py`, `p.py` and is incomplete by `depth-cap` `b.py` alone | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| WALK_DELETED_INPUT_REACHES_ITS_NAMERS | X440 case_walk_deleted_input | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| INPUT_FORMS_RESOLVED | X441 case_input_forms | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| WALK_INCOMPLETE_NAMES_REASON_AND_ACTION | X442 case_walk_incomplete: arms (a) to (h), one per reason the contract lists | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| AFFECTED_TESTS_ARE_THE_WALK_FILTERED | X443 case_affected_tests_filtered: certain rows first, then a maybe row | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| AFFECTED_ALWAYS_RUN_LISTED_APART | X444 case_affected_always_run: the opaque test in `floor`, the JSON and Markdown fixtures in no list | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| ANCHORS_NAME_CITING_PAGES_OR_UNCITED | X445 case_anchors_citing_pages: slice 2 turns the `repo: src/` arm, so `repo: src/` and `repo: src` each claim nothing; the slice-1 `maybe` `repo-prefix` fact the case still expects moves to X459; the `repo:` arm pending owner ruling (grill §12 question 6) | tests/test-source-index.sh | integration (synthetic Git plant) | pending |
| ANCHORS_BASENAME_IS_MAYBE_AMBIGUOUS_IS_INCOMPLETE | X446 case_anchors_basename | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| OUTPUT_CARRIES_NO_RAW_CONTROL | X448 case_output_no_raw_control: names holding ESC, U+202E and the byte 0xFF, text and `--json` | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| SOURCE_INDEX_IS_PLACED | E15 SOURCE_INDEX_IS_PLACED | tests/test-full-install.sh | integration (fresh install) | green |
| SYMBOLS_PYTHON_DEFINITIONS_CERTAIN | X450 case_symbols_python: the ten names each list one `certain` definition found `ast` in `pkg/a.py`, with line, kind and qualified name; `Store.save` lists what `save` lists; `x` and `path` `undefined`; `incomplete` empty; arm deep (§5 S1, the reader never descends into expressions), `deep.py` holding `x = a+a+...` (1,000 terms) then `def deep_ok():`: `deep_ok` lists one `certain` definition in `deep.py` and no `unreadable-file` record names it; arm GRAPH_ONLY, `docs/graph/tool.py` holding `GRAPH_ONLY = 1`: `GRAPH_ONLY` `undefined`, `not_read` `["docs/graph/", ".cypress/"]`, the text view of `symbols GRAPH_ONLY` prints `UNDEFINED_LINE` naming both | tests/test-source-index.sh | integration (synthetic Git plant) | red |
| SYMBOLS_LINE_READ_DECLARATIONS_ARE_MAYBE | X451 case_symbols_line_read: the twelve names in `install.sh` and `src/m.ts` each list one `maybe` definition found `line-reading`, with line and kind; `fake`, `z` and `y` `undefined`; arm indent, in `src/m.ts` `function i(` holds the indented `const local =` and `function nested(`, both `undefined`, and `namespace N {` holds the indented `export function ns(`, one `maybe` `function`; every other declaration line at column 0 | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| SYMBOLS_LIST_EVERY_DEFINITION | X452 case_symbols_every_definition: `parse` lists four definitions, the three `certain` ones by path, then the `maybe` one; `Reader.parse` lists the method alone; the text view of `symbols parse` prints one line per definition | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| SYMBOLS_UNREADABLE_FILE_MAKES_IT_INCOMPLETE | X453 case_symbols_unreadable: `run` lists `ok.py`; one `unreadable-file` record each for `bad.py` and `big.js`; the text view's last line is the `symbols` `ACTION_LINE` naming both | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| HISTORY_ROWS_ARE_MAYBE_WITH_THEIR_COUNT | X454 case_history_counts: `affected-tests` holds `tests/t_b.sh` `maybe` `history` `{count: 2, of: 3}`; `impact` holds it, then `c.py` `{count: 1, of: 3}`; no history row `certain`; `tests/t_wide.sh` in no list | tests/test-source-index.sh | integration (synthetic Git plant, scripted commits) | green |
| HISTORY_ONLY_ADDS | X455 case_history_only_adds: the `--history` answer equals the plain one in every key but `history` and `cache`, the plain one has no `history` key; `history` holds `d.py` alone (`b.py` stays in `dependents`, `o.py` in `floor`) | tests/test-source-index.sh | integration (synthetic Git plant, scripted commits) | green |
| HISTORY_SHALLOW_OR_MISSING_IS_INCOMPLETE | X456 case_history_incomplete: arm (a), `git clone --depth 2 file://<origin>`, the origin's last three commits `a.py` with `tests/t_old.sh`, `a.py` alone, `a.py` with `tests/t_new.sh`: one `history-shallow` record naming `.`, `history` holds `tests/t_new.sh` with `together` `{count: 1, of: 1}` and no `tests/t_old.sh` (the parentless boundary commit is not read); arm (b), no commit and an untracked `a.py`: one `history-unavailable` record naming `.`; each text view ends with the `affected-tests` `ACTION_LINE`; without `--history` neither record | tests/test-source-index.sh | integration (synthetic Git plant, scripted commits) | green |
| ANCHORS_MOVED_EQUALS_THE_NAMED_PATHS | X457 case_anchors_moved: anchor recorded by the placed `docs/graph/code-anchor.py`, then a commit in nested `Cypress/` and an uncommitted `run.sh` edit; `anchors --moved` equals `anchors Cypress/tools/x.py run.sh` in every key but `cache`; after a second `--record`, no input, no file, `incomplete` empty, `MOVED_NONE_LINE` | tests/test-source-index.sh | integration (synthetic Git plant, scripted commits) | green |
| ANCHORS_MOVED_WITHOUT_A_LIST_IS_INCOMPLETE | X458 case_anchors_moved_incomplete: arms (a) no `.cypress/anchor.json`, (b) the recorded `Cypress` commit replaced by one the clone lacks, `run.sh` edited, (c) no `docs/graph/code-anchor.py`, (d) a placed `code-anchor.py` with no `moved_list` (placed before slice 2), (e) a placed `code-anchor.py` whose `moved_list` returns a `paths` string, (f) a placed `code-anchor.py` whose `moved_list` raises `Unrecorded` with no `ANCHOR_NAME`; each text view ends with the `anchors` `ACTION_LINE` and prints no traceback | tests/test-source-index.sh | integration (synthetic Git plant, scripted commits) | red |
| REPO_CLAIM_READ_ALIKE_BY_ROUTER_AND_ANCHORS | X459 case_repo_claim, pending owner ruling on repo: (A/B/C): `anchors` lists `repo: src/lib/a.py` `certain` and `repo: src/lib/` `maybe` `repo-prefix` for `src/lib/a.py`, `repo: src/lib/` `maybe` for `src/lib/c.py`, `src/b.py` `uncited`; the seed's `graph-lint.py --plan-json` loads the same two nodes by `named_path` and none for `src/b.py` | (new case) | integration (synthetic plant, the seed's graph-lint.py placed) | pending |
| GIT_UNAVAILABLE | X442 case_walk_incomplete: arm (f), PATH holds python3 and no git; an existing cache left byte-identical | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| NO_GOVERNED_REPOSITORY | X442 case_walk_incomplete: arm (i), a plant root that is no Git work tree | tests/test-source-index.sh | integration (synthetic plant) | green |
| REPOSITORY_UNREADABLE | X442 case_walk_incomplete: arm (j), a nested governed repository with a corrupt index; the root repository still answers; arm (m3), a git that fails only `ls-files` in `vendor/lib` names `vendor/lib`, not `.` | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| CYPRESS_DIR_ABSENT | X427 case_cache_self_ignored: arm (b), no `.cypress/`; status `not-written`, `.cypress/` not created | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| CACHE_PATH_UNSAFE | X427 case_cache_self_ignored: arm (c), `.cypress/source-index` a symlink to a directory outside the plant; status `not-written`, the target untouched | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| CACHE_IGNORE_ALTERED | X427 case_cache_self_ignored: arm (d), an inner `.gitignore` holding `!index.json` is rewritten to `*` | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| CACHE_UNREADABLE | X429 case_cache_rebuilt: arm (e), `index.json` not JSON, then valid JSON of another schema | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| CACHE_WRITE_FAILED | (no test: the temp file and atomic replace are the helper's write, whose fault path tests/test-code-anchor.sh proves; a lost cache is rebuilt on the next query) | — | — | skipped |
| TSCONFIG_UNREADABLE | X435 case_unpinned_reference: the `extends` arm (`alias-config-unavailable`), whose holder's relative import still resolves | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| TEST_DECLARATION_UNAVAILABLE | X442 case_walk_incomplete: arms (g) `no-test-declaration` and (h) `no-test-files` | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| PLANT_CONFIG_REFUSED | X442 case_walk_incomplete: arm (e), an unknown key; `config-refused` with the error as detail | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| INPUT_NOT_IN_INDEX | X441 case_input_forms, and X442 case_walk_incomplete: arms (b) `input-not-found`, (c) `ambiguous-input`, (k) `outside-plant` | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| USAGE_REFUSED | X447 case_usage_refused: an unknown query or option, `--depth 0` and `--depth 6`, no path; `--help` exits 0; slice-2 arms: `--history` on `anchors` and on `symbols`, `--moved` on `impact`, `anchors` with no path and no `--moved`, `anchors --moved a.py` and `anchors --moved -`, and `symbols` names `NAME_RE` refuses whole (`a..b`, and a name ending in a newline); each writes no cache | tests/test-source-index.sh | integration (CLI) | pending |
| UNSAFE_PATH_TEXT | X448 case_output_no_raw_control: the ESC arm; the text view shows `?`, `--json` escapes it | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| FILE_NOT_REGULAR | X435 case_unpinned_reference: a tracked file replaced by a FIFO is opaque `unreadable`, line null, and the query does not block; X425 holds the symlink arm (a record, never a holder) | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| INPUT_EXHAUSTS_A_PARSER | X435 case_unpinned_reference: a Python file over `FILE_MAX_BYTES` (its blob hash still listed) and one holding a NUL byte are opaque `unreadable` | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| DIRECTORY_LITERAL_TOO_WIDE | X433 case_link_path_literal: `"/"`, `"./"` and `"$ROOT/"` link nothing; a directory over `DIR_LINK_MAX` makes its holder opaque `walks-tree` | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| TSCONFIG_EXTENDS_CYCLE | X434 case_link_ts_specifier: an `extends` cycle keeps the relative import and makes the alias holder opaque `alias-config-unavailable` | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| GIT_PATH_ARGUMENT | X435 case_unpinned_reference: `./--exec=x`, `./:(top)q`, `./*` stay `relative-no-file` records and a path past the root `outside-repository`, the `generated` record still found beside bases under a symlinked directory and an ungoverned nested work tree (arm m2), and the build complete | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| NON_UTF8_PATH | X448 case_output_no_raw_control: the 0xFF arm, decoded as U+DCFF in `--json` | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| DEFINITIONS_UNREADABLE | X453 case_symbols_unreadable: the `bad.py` (syntax error) and `big.js` (over `FILE_MAX_BYTES`) arms; the FIFO and non-UTF-8 forms reach `symbols` through the same `opaque` `unreadable` record X435 proves | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| LINE_READ_DECLARATION_IN_TEXT | X451 case_symbols_line_read: arm text, a here-document line `function hx() {` in `install.sh` and a template-literal line `function tx() {` at column 0 in `src/m.ts` each list one `maybe` definition; `const a1 = 1, b1 = 2` at column 0 defines `a1` and leaves `b1` `undefined` | tests/test-source-index.sh | integration (synthetic Git plant) | green |
| HISTORY_SHALLOW | X456 case_history_incomplete: arm (a) | tests/test-source-index.sh | integration (synthetic Git plant, scripted commits) | green |
| HISTORY_UNAVAILABLE | X456 case_history_incomplete: arm (b); the failing and timed-out `git log` triggers give the same record and are not separate arms | tests/test-source-index.sh | integration (synthetic Git plant, scripted commits) | green |
| HISTORY_BULK_COMMIT | X454 case_history_counts: the commit of `a.py` with `HISTORY_MAX_FILES` other inventory files adds to no `count` and no `of` | tests/test-source-index.sh | integration (synthetic Git plant, scripted commits) | green |
| MOVED_LIST_UNAVAILABLE | X458 case_anchors_moved_incomplete: arms (a), (c), (d), (e) and (f), `moved-unavailable` naming `.cypress/anchor.json`, then `docs/graph/code-anchor.py` three times (no input in (e)), then `.cypress/anchor.json` (the fallback subject, no traceback) | tests/test-source-index.sh | integration (synthetic Git plant, scripted commits) | red |
| MOVED_REPOSITORY_UNVERIFIED | X458 case_anchors_moved_incomplete: arm (b), `moved-unverified` naming `Cypress`, `run.sh` still an input and answered | tests/test-source-index.sh | integration (synthetic Git plant, scripted commits) | green |
| HELPER_ABSENT_BESIDE_GRAPH_LINT | X459 case_repo_claim: arm helper-absent, which does not wait on the owner's `repo:` ruling, no `source_paths.py` beside `graph-lint.py`: `--plan-json` exits 0, `notices` holds `{code: inference_skipped, text: "inference skipped: HelperUnavailable"}`, and no LOAD entry is `named_path` through a `repo:` claim | (new case) | integration (synthetic plant, the seed's graph-lint.py placed) | pending |

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
- 2026-10-07 — RED R1 readings ruled (`architect-readings`), all confirmed, none amended, no test change: a `directory` link's kind is `path-literal`; `import a` beside `a.py` is found `resolved` and `python3 b.py` beside `b.py` `exact`; §6 "Incomplete" gains a Subject column (an input as normalized, which equals the input given in its normal form; `config-refused` the config path; `depth-cap` the file at the cut depth; the four subject-less reasons named); the cache reason of a `CACHE_UNREADABLE` rebuild is `cache unreadable`, another `schema` included; a copied plant's cache status is `reused`; `WALK_NEAREST_FIRST_ONCE` and `AFFECTED_TESTS_ARE_THE_WALK_FILTERED` each gain the one `maybe` row (`e.py`, `tests/p_test.py`) that shows the `certain` rows come first.
- 2026-10-07 — code review `reviewer-code` (fix-list item 12) applied by `architect-review-fixes`, as clarifications inside the existing contracts, no new contract and no version bump: §6 "Resolution": `from a.b import c` links the module file and each submodule file `c` the inventory holds, in every branch (M1); variable-led shell strings (`$DIR/x`, `$(dirname "$0")/x`) try the holder's directory first, a hit there `resolved`, the unresolved `base` still repository-relative (M3); a workspace package matched by `name` or `name/`, the subpath probed to a `certain` `resolved` link, else the `maybe` package links (M6); a leading `/` with no alias match is `outside-repository` and `~` begins no npm name (m1); a non-relative tsconfig `extends` is skipped (m9e). §6 "Links": a walk call whose literal root makes no `directory` link is `opaque` `walks-tree` (M2); a `directory` link reaches every file below at any depth, and a workspace link set over `DIR_LINK_MAX` is `opaque` `walks-tree` with the specifier as reference (m9a, m9b; §7 `DIRECTORY_LITERAL_TOO_WIDE` widened to match); a foreign or ungoverned-work-tree base is not asked of `check-ignore` (m2). §6 inventory: `hash` "" when `content_state` cannot hash (m9c); a repository whose listing fails is left out with `repository-unreadable` and the others answer (m3); the key's dirty paths are those the inventory keeps (m4); `SKIP_DIRS` read from the placed spec-lint.py, the copy a fallback, not keyed because graft rebuilds (m8); `config_matches` case-sensitive by decision, the tail rule written out (m8). §6 answer and CLI: a forced `build` over an existing cache is `rebuilt` with reason `build forced` (m9d); the `build` text view is the cache line and one count line, formats given (m9 build text). Intended verdict change (m6): the helper's `split_citation` strips whitespace before it cuts the `:line` suffix, so growth-audit's `graph_leaf_filled` and grounding loop now read `x.md:3 ` (trailing space) as `x.md`, where before the raw `x.md:3` was never substantive; this corrects §6 "Helper" ("no growth-audit verdict changes") for that one input, because one parse is the point of the helper.
- 2026-10-07 — slice-1 final decisions after the measurement (grill §10), by `architect-final`, as clarifications inside the existing contracts, no new contract: §6 "Links" reads a path join (a Python `/` chain or `os.path.join`; a shell or TS/JS `path.join(`, `path.resolve(` or `os.path.join(`; a shell run of `/` words, the here-document form) as one path literal, non-literal segments written as variables, so it is a `maybe` `path-literal` or `directory` link and a `__file__` or `__dirname` base is a variable lead, never `certain` outside a load call (D1, D2); a shell word joining quoted and unquoted parts is one string (D1); a string or join holding a variable after a named segment reads the segments before it as a directory literal (D1); a walk root may be a join; the TS/JS line join also takes `path.join(` and `path.resolve(`. §6 "Resolution": a scheme-led specifier is external, and a specifier no rule resolves or records makes its holder `opaque` `unmapped-specifier`, a new opaque reason, because a base-less `unresolved` record never reaches an answer (R1). §6 "Walk": the floor part has no depth bound, and `depth-cap` comes from the input part alone (D4). §2 states host settings commands out of scope (D3). §4 `LINK_PATH_LITERAL_AND_DIRECTORY_ARE_MAYBE`, `UNPINNED_REFERENCE_RECORDED_WITH_ITS_REASON`, `WALK_FLOOR_LISTED_APART_AFTER_THE_INPUT_ROWS` and `WALK_INCOMPLETE_NAMES_REASON_AND_ACTION` gain the arms; §5 records the measured timings; §7 `DIRECTORY_LITERAL_TOO_WIDE` names joined directory literals. The §10 rows are the R3 tester's (grill §9).
- 2026-10-07 — second code review (`reviewer-code-2`): a specifier whose `baseUrl` probe misses is `unmapped-specifier` like any other unresolved specifier (the probe resolves, it does not map); an assignment word is read as its value. Applied in session from the reviewer's rulings.
- 2026-10-07 — `implemented`: every contract green and the full seed gate green at b70b0d9 (session, `verify.status-evidence`).
- 2026-10-07 — slice 2 added by `architect-slice2` (owner: "slice 2 ok"; `protocol.specify`, a spec may grow by slice), on product's §3 "Slice 2": §1 and §2 move the slice-2 items into scope (the Never list kept); §4 adds ten contracts, `SYMBOLS_PYTHON_DEFINITIONS_CERTAIN`, `SYMBOLS_LINE_READ_DECLARATIONS_ARE_MAYBE`, `SYMBOLS_LIST_EVERY_DEFINITION`, `SYMBOLS_UNREADABLE_FILE_MAKES_IT_INCOMPLETE`, `HISTORY_ROWS_ARE_MAYBE_WITH_THEIR_COUNT`, `HISTORY_ONLY_ADDS`, `HISTORY_SHALLOW_OR_MISSING_IS_INCOMPLETE`, `ANCHORS_MOVED_EQUALS_THE_NAMED_PATHS`, `ANCHORS_MOVED_WITHOUT_A_LIST_IS_INCOMPLETE` and `REPO_CLAIM_READ_ALIKE_BY_ROUTER_AND_ANCHORS`; §5 adds the slice-2 timings, security rules and the definition names to Privacy; §6 adds the `symbol` record and the definition rules, history links (`--history`, `history_row` with `together: {count, of}`), the moved list, the helper's `repo_claim` and `path_matches`, five `incomplete` reasons, `INDEX_SCHEMA` `/2` (the cache gains `symbols`; `ANSWER_SCHEMA` stays `/1`, the answer only gains keys) and the CLI; §7 adds eight failures and widens `USAGE_REFUSED`; §8 adds seven seed and plant examples. The protocol wiring is prose (grill §9 increment 21), no tool contract. One intended revision of a signed contract, recorded here as the slice-1 m6 change was: `ANCHORS_NAME_CITING_PAGES_OR_UNCITED` no longer reads `repo: src/` as a `maybe` prefix claim, because the helper's one `repo_claim` is graph-lint's rule (a value with no `/` once its leading and trailing `/` are cut is a repository root, and nothing is normalized beyond that cut), so graph-lint's routing stays as it is and the two tools agree; the `repo-prefix` arm moves to `REPO_CLAIM_READ_ALIKE_BY_ROUTER_AND_ANCHORS`. Sign-offs of product, tester and security cleared for slice 2.
- 2026-10-07 — slice 2 reopens the spec: status `active` (from `implemented`); slice 1's evidence stands as recorded: `tests/test-source-index.sh` (25 cases, X425 to X449) and `tests/test-full-install.sh` (E15), wired into `tests/run.sh`, every slice-1 §10 row green but `CACHE_WRITE_FAILED` (skipped: the helper's atomic write is proved by the code-anchor fault case), the full seed gate run-parallel OK, 51 of 51 steps, 38.6 s, at `b70b0d9`; the measurement in grill §10. `implemented` returns when every slice-2 row is green after G8.
- 2026-10-07 — slice-2 review findings applied by `architect-slice2-fix`, inside the slice-2 contracts, no contract added and none removed. Tester: `HISTORY_SHALLOW_OR_MISSING_IS_INCOMPLETE` clones `--depth 2` through `file://` (a plain local path clone is not shallow) and pins the held commits; §6 "History links" leaves out a commit with no parent (a root commit, or a shallow clone's boundary commit, which Git lists as changing every file); `HISTORY_ONLY_ADDS` and `ANCHORS_MOVED_EQUALS_THE_NAMED_PATHS` compare every key but `cache`. Security: the definition reader is iterative over statement bodies (S1); `--moved` guards the load and the call of `moved_list` and catches code-anchor's own classes, with the root a parameter (S2); `git log` takes `--no-renames --no-show-signature --no-color` and a `/`-led marker (S3); only `false` from the shallow probe reads as complete (S4); `NAME_RE` is matched whole (S5); the cache block is `/2` and the shape check covers `symbols` (S6); `graph-lint.py` sets `sys.dont_write_bytecode` before its loads (S7); §5 states the buffered `git log` and every `detail` through the `?` replacement. Devils-advocate: (b) a TS/JS declaration counts at column 0 or after `export`, so function locals define nothing (an arm of `SYMBOLS_LINE_READ_DECLARATIONS_ARE_MAYBE`); (d) `graph-lint.py` loads the helper lazily in tier 2 and a missing or skewed helper costs tier 2 alone, named by the existing `inference_skipped` notice, instead of failing every route (§7 `HELPER_ABSENT_BESIDE_GRAPH_LINT`); (a) and (c) are plan changes (grill §9, §10, §11); §2 cites ADR-0018's reason, a tool called at each file access. §6 and §8: the sibling-load line numbers corrected (`code-anchor.py` 53-54, `graft-audit.py` 169-170). `REPO_CLAIM_READ_ALIKE_BY_ROUTER_AND_ANCHORS` is unchanged, pending the owner's `repo:` ruling (grill §12 question 6).
- 2026-10-07 — slice-2 code review (`reviewer-slice2`, fixes 5 and 6) and measurement 2 (`measure-slice2`, defects M2-1, M2-3, M2-6) applied by `architect-slice2-m2`; the `repo:` claim (§12 question 6) untouched, pending the owner. §3: a nested Python function is a definition (qualified), a nested TS/JS function is not, as §4 and §6 already said; an `undefined` answer names what the tool does not read. §6 "Definitions": the define-nothing list names `for`/`async for` targets, `with`/`except ... as` names, `:=` targets and augmented assignments (reviewer ruling 1, upheld: the code is right, the spec was silent), shell variables and dotted shell function names; the code-path rule bounds definitions, stated in the new `symbols` answer key `not_read` (the helper's `NOT_CODE`) and in `UNDEFINED_LINE` (M2-3: a name defined only in a placed seed tool under `docs/graph/` is `undefined` and says why, with no `incomplete` record). §4 `SYMBOLS_PYTHON_DEFINITIONS_CERTAIN` gains the `GRAPH_ONLY` arm; `ANCHORS_MOVED_WITHOUT_A_LIST_IS_INCOMPLETE` gains two arms (a `paths` string; `Unrecorded` without `ANCHOR_NAME`), and §6 "Moved list" states the malformed shape and the subject read inside the guard. §5: the slice-2 figures and M2-1 decided as a reduction, not a restated budget: the cache is written compact and `build` holds no parsed cache while it derives; 64 MB stands. §6 "Cache document": compact layout (derived scratch, ADR-0029; the tool digest in the key rebuilds an indented cache; schema `/2` unchanged, the shape is the same). Reviewer ruling 2: the X447 newline arms stand as written.
