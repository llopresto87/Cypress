# Tool: tiered-validation-ladder

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). This page is a **BLUEPRINT**: the tier contract,
> the fail-never-downgrade rule and the file enumeration are portable; which
> checks fill each tier is the adopting project's.

## 0. Identity

- **Category:** testing
- **Name:** tiered-validation-ladder
- **Language / runtime:** any; typically one shell wrapper. The lowest tier
  needs only the language runtime the repository already requires.
- **Stability:** **blueprint**. The wrapper is short and project-shaped; the
  value is the contract between its tiers and the tests that pin it.

## 1. What it does

One entry point, `validate [--quick|--static|--full]`, that runs a named tier of
local checks. Each tier is a **strict superset** of the one below it:

| tier | runs | needs |
|---|---|---|
| quick | stdlib unit discovery, the project's own safety audits, whitespace/diff hygiene | the language runtime only |
| static | quick + linters and syntax checks of the declarative files | the project's lint toolchain |
| full | static + the slow or heavy analyzers | the full toolchain |

It exists for three reasons:

- **CI can run the lowest tier before installing anything.** A quick tier that
  needs only the runtime runs as the first CI step and on any machine an agent
  is handed, so the cheapest regression signal never waits on a dependency
  install.
- **A reader can pick the cheapest tier that covers a change** and trust that a
  higher tier never silently drops a check the lower one ran.
- **A tier either ran in full or failed.** A selected tier whose prerequisite is
  missing fails with the name of what is missing. It never falls back to a
  weaker tier and reports green, because a "static passed" that ran only quick
  is a false green with the stronger tier's name on it.

## 2. Interface & invocation

```
validate [--quick | --static | --full]     # default: the middle tier
```

- **Exit codes:** 0 the selected tier ran in full and passed; 1 a check failed or
  a prerequisite of the selected tier is missing; 2 usage.
- **Output:** each check's own output, then one line naming the tier that ran.
  A missing prerequisite prints `validate: <tool> is required for --<tier>`.
- **Enforcement surfaces say what they run.** A commit hook or CI job that wires
  only part of the ladder (only the safety audit, only quick) is documented as
  exactly that. The ladder's existence is not evidence that a surface enforces
  its higher tiers.

## 3. Approach / algorithm

```
parse tier (reject anything else: exit 2)
run quick checks                       # every tier
[ tier == quick ] && exit 0
require each static prerequisite       # missing -> exit 1, never downgrade
run static checks over ENUMERATED files
[ tier == static ] && exit 0
require each full prerequisite         # missing -> exit 1
run full checks
```

- **Enumerate the files a linter sees from the version-control CLI, not from
  the tracked set alone:** index plus untracked-but-not-ignored
  (`tool-corpus/testing/working-tree-snapshot.md` owns why the tracked-only
  listing is the bug). A new file the change under test adds is linted before
  it is staged.
- **Exclude secret-container files by name before linting**, so an encrypted
  file the linter cannot parse never makes the tier unrunnable and a plaintext
  one is never echoed into a lint report.
- **Resolve tool locations from the working tool, not from an assumed install
  prefix.** When two cooperating CLIs can live in separate environments (one
  installed by a system package manager, one by a per-user installer), ask the
  working CLI where its plugin or collection roots are and export that path
  before the next tool runs.
- **`set -euo pipefail` and no `|| true` around a check.** A check that may
  legitimately find nothing says so explicitly; swallowing its exit code is how
  a tier passes without running.

## 4. Portable vs blueprint

- **Portable:** the strict-superset rule; quick needs only the runtime; a
  missing prerequisite fails the selected tier; enumeration of tracked plus
  untracked-not-ignored files; enforcement surfaces documented by the tier they
  run.
- **Fill in per project:** the checks in each tier, the prerequisite list per
  tier, which files are secret containers, and which hook or CI job runs which
  tier.

## 5. Pitfalls and sharp edges

- **Sourcing a helper inherits the caller's positional arguments.** In bash,
  `source helper.sh` with no arguments gives the helper the wrapper's own `$@`,
  so `--static` can be read as the helper's first positional (a path, say).
  Pass an explicit empty argument (`source helper.sh ""`) or clear `$@` first.
- **A downgrade is quiet by construction.** `command -v linter || run_quick`
  reads as resilience and is the false green this page exists to forbid.
- **A tier that grew a check below it breaks the superset silently.** Adding a
  check to `static` that `full` skips (an early `exit 0` in the wrong branch)
  passes every run; only a contract test catches it.
- **"Quick passes in CI" says nothing about static or full.** Record which tier
  each surface ran; a delivery that cites a tier cites the one that ran.

## 6. Tests that cover it

The contract tests are **owed**: in the source practice the tiers ran green
while the tier contract itself had no test. Write these before trusting the
ladder:

- **QUICK_RUNS_BASELINE_ONLY:** with every linter shimmed to record its call,
  `--quick` calls the quick checks and none of the static or full ones.
- **STATIC_IS_STRICT_SUPERSET_OF_QUICK** and **FULL_IS_STRICT_SUPERSET_OF_STATIC:**
  the recorded call set of each tier contains the lower tier's set.
- **SELECTED_TIER_MISSING_DEPENDENCY_FAILS:** with a static prerequisite absent
  from `PATH`, `--static` exits 1 naming it and runs none of its checks; the
  same for `--full`.
- **NEW_FILE_IS_LINTED:** an untracked, unignored file with a lint error fails
  `--static`; an ignored one does not.
- **SURFACES_MATCH_THEIR_DOCS:** the hook and CI job invoke the tier their
  documentation names.

Shim the tools as stub executables first on `PATH` so the tests need no
toolchain and run inside the quick tier themselves.

- **How to run the tests:** `<the plant's test command for its wrapper>`

## 7. References & neighbours

- **Related tools:** `tool-corpus/testing/working-tree-snapshot.md` (the file
  enumeration); `tool-corpus/testing/static-config-contract-gate.md` (a
  config-contract check; one written without a parser runs in the quick
  tier); `tool-corpus/testing/touched-file-lint-hook.md` (per-edit linting,
  the cheaper sibling of a whole-tier run).
- **Sources:** distilled from practice; no external URL.

## 8. Changelog

- 2026-10-14 — created by docs-librarian.
