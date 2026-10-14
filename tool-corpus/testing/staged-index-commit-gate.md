# Tool: staged-index-commit-gate

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). This page is a **BLUEPRINT**: the index export,
> the moved-index refusal, the selection rules and the lane model are
> stack-neutral; the test runner, the reference search and the remote
> transport are the adopting project's, with one stack worked below.

## 0. Identity

- **Category:** testing
- **Name:** staged-index-commit-gate
- **Language / runtime:** a shell driver (version-control CLI, a file-sync
  tool, optionally a remote shell) plus a stdlib selector module in any
  scripting language.
- **Stability:** **blueprint**.

## 1. What it does

The per-increment commit gate of `delegation.tip-cadence`
(`core/method/delegation-cycle-economy.md` owns the cadence: targeted tests and
cross-cutting gates per increment, the full suite once at the batch tip). It
gates **what will be committed**, not what is on disk:

1. export the staged index into a persistent per-lane directory;
2. select the tests the staged paths reach, plus the cross-cutting gates those
   paths trigger;
3. sync only the changed files into the lane's persistent run directory (local
   or on a build host);
4. run the selection; with `--tip`, run the full suite instead;
5. check that no test infrastructure (containers, processes) outlived the run.

It exists because a working-tree gate is wrong twice under parallel workers:
another worker's untracked or unstaged files change its result, and a file the
increment forgot to stage passes the gate and is missing from the commit. And a
full suite per commit is slow enough that workers stop running it.

## 2. Interface & invocation

```
gate --label LANE                 # targeted, derived from the index
gate --label LANE --tests LIST    # explicit selection, passed through
gate --label LANE --tip           # full suite at the batch tip
gate --label LANE --dry-run       # export + selection only
GIT_INDEX_FILE=<private index> gate ...   # gate a private index
```

- **`--label`** names the lane; restrict it to `[A-Za-z0-9._-]+`. One lane per
  concurrent worker. A second gate on a busy lane is refused (exit 2); a stale
  lock from a dead process is detected and cleared.
- **`--tests`** passes an explicit selection through, restricted to the
  characters the runner's selector syntax needs; `--tip` and `--tests` are
  exclusive.
- **Outputs:** `select: <test> <- <reason>` per selected test, then one
  `STAGE <name> PASS|FAIL|SKIPPED|TIMEOUT <s>s <detail>` line per stage
  (`export` with the index tree id, `select`, `sync` with the count of files
  moved, `run`, `leak`), failing test ids, and `GATE PASS|FAIL exit=<n>`. Logs
  go to an announced per-lane directory.
- **Exit codes:** 0 green; 1 a stage failed; 2 usage, environment, busy lane or
  moved index.

## 3. Approach / algorithm

**Export.** Record the index's tree id (`git write-tree`), list the staged
paths, export the index (`git checkout-index -a --prefix=<lane>/`, deletions
removed from the lane tree), then take the tree id again. **If it moved,
refuse and ask for a rerun**: another lane committed between the listing and
the export, and the gate would test a tree that matches neither commit. Honour
`GIT_INDEX_FILE` without touching the shared index.

**Select** (a pure function from staged paths to a plan, so it is unit-tested
without a build):

- a staged test file selects itself by its fully qualified name;
- a staged production file, helper, fixture or resource selects every test
  that references it: a source file by its simple type name as a **whole word**;
  any other file by the first hit among its repository path, its
  resource-relative path, its parent directory and its basename;
- references are followed **transitively through test helpers**: a staged
  production type reached by a helper selects the tests that use the helper;
- **cross-cutting gates are path-keyed**: the build manifest selects the
  dependency/compatibility gates; schema migrations select the migration lint
  and any schema-fingerprint test; any production source selects the
  module-dependency rules; deployment files switch on integration and
  deployment-smoke stages;
- tests the default run excludes by tag (a browser group, say) are moved out
  of the selection and named in a notice, rather than selected and silently
  run as nothing;
- only docs or unreferenced non-build files staged: the run is skipped and the
  line says so.

**Sync** only changed files into the persistent lane directory, so a warm lane
keeps its build caches and compiled output.

**Leak check.** Record the test-infrastructure containers that exist before
the run; afterwards, a container is an orphan only when it is new **and** no
live reaper of its own session remains. Other lanes' live sessions and
pre-existing containers are never blamed on this run.

## 4. Portable vs blueprint

- **Portable:** gate the index, not the working tree; refuse a moved index;
  path-keyed selection with transitive helpers and whole-word references;
  cross-cutting gates keyed by path; one persistent lane per worker with a busy
  lock; the full suite at the tip; the leak check scoped to the run's own
  session.
- **Fill in per project:** the runner and its selector syntax, which paths key
  which cross-cutting gates, the reference search for the project's languages,
  local versus remote lanes, and the infrastructure the leak check inspects.
- **Per stack, Maven with Surefire and Testcontainers
  (`library-corpus/cli/maven.md`, `library-corpus/maven/testcontainers.md`):**
  select by Surefire's default test-class name patterns; pass
  `-Dtest=<list> -Dsurefire.failIfNoSpecifiedTests=false`; run offline against
  a warm repository volume and retry online once on an offline-resolution
  failure, saying so in the stage line; a staged `*IT` switches on Failsafe.
  Observed in practice on Testcontainers 2.x, and not stated in its docs: the
  reaper (Ryuk) container carries its session in its container name
  (`testcontainers-ryuk-<sessionId>`) and has no session label, so the leak
  check reads the session from the name. Re-check on the version in use.

## 5. Pitfalls and sharp edges

- **Selection by name misses tests reached by no name.** A test that reaches
  the changed code only through framework wiring (dependency injection,
  classpath scanning, reflection) is not selected. That is what `--tip` is for;
  a targeted green never stands in for the tip.
- **Concurrent forks of one runner share the machine's temp directory.** A test
  that asserts "no temporary file was left" sees a sibling fork's files: a
  latent flake that grows with the fork count.
- **The tip's floor is its slowest serial class.** More forks cannot cut below
  it; the fix is test-side concurrency of that class, which is a tester's
  investigation, never a gate flag.
- **A "balanced" run-order statistics file keyed by the whole build
  configuration** is reset whenever the configuration carries a per-build value
  (a timestamp property), so the ordering silently does nothing. Measure before
  relying on it.
- **Do not edit the driver while it runs**: a mid-run edit makes the gate
  report nonsense (`tool-corpus/testing/long-stage-progress-runner.md` §5).
- **`set -e` with a grep that matches nothing** ends the script before its
  stage line; guard every "find the failing ids" grep.

## 6. Tests that cover it

- **Selection (pure):** staged paths to plan, covering FQN selection,
  whole-word references, transitive helpers, fixtures by path and directory,
  each cross-cutting key, tag-excluded tests moved to a notice, deletions, and
  the no-run cases.
- **Driver on a throwaway repository with `--dry-run`:** usage errors; the lane
  root guard; an unstaged edit and an untracked test are never exported; an
  index deletion leaves the lane tree; `GIT_INDEX_FILE` is honoured without
  touching the shared index; busy and stale lane locks; a moved index refuses.
- **Past the dry run, against the stubs of
  `tool-corpus/testing/remote-stub-fixture.md`:** announced logs, heartbeat
  naming the running test, reports copied back, TIMEOUT distinct from FAIL.
- **Planted control:** a private index carrying an always-failing test while the
  working tree equals HEAD; the gate must select it, name it and exit 1.

- **How to run the tests:** `<the plant's test command for its implementation>`

## 7. References & neighbours

- **Doctrine:** `core/method/delegation-cycle-economy.md` (`delegation.tip-cadence`).
- **Related tools:** `tool-corpus/testing/long-stage-progress-runner.md` (the
  streamed log, heartbeat and TIMEOUT status of the run stage);
  `tool-corpus/testing/working-tree-snapshot.md` (the opposite choice: a copy of
  the working tree, right when the working tree is the subject);
  `tool-corpus/testing/parallel-suite-runner.md` (the full run's failures judged
  by test id against a baseline); `tool-corpus/testing/sandboxed-browser-test-runner.md`
  (the tag-excluded browser group, run in its own lane);
  `tool-corpus/testing/ci-runner-local-simulator.md` (reconstructing the CI
  environment the gate's results are compared with).
- **Sources:** distilled from practice; no external URL.

## 8. Changelog

- 2026-10-14 — created by docs-librarian.
