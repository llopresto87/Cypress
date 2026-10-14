# Tool: batched-mutant-runner

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). This page is a **BLUEPRINT**: the mutants-file
> shape, the apply/restore discipline, the control rule and the verdict table
> are stack-neutral; the test command and the startup-failure signature are
> the adopting project's, with one stack worked below.

## 0. Identity

- **Category:** testing
- **Name:** batched-mutant-runner
- **Language / runtime:** python3, standard library only, in the reference
  design; it shells out to the project's test command.
- **Stability:** **blueprint**. The core is small and stack-neutral; the test
  invocation and the report parsing are rewritten per build tool.

## 1. What it does

Runs a declared list of **hand-written mutants**, one at a time, against a
scratch copy of the tree, and records a verdict per mutant. It is the batched
end-of-spec pass of `delegation.mutation-at-end`
(`core/method/delegation-cycle-economy.md`) made repeatable;
`skill-corpus/mutation-verify.md` owns the procedure of choosing a mutant and
reading a survivor, and this page owns only the machine that runs a list of them.

Per mutant:

1. check every file it touches matches its recorded pristine hash;
2. apply the edit, whose `old` text must occur **exactly once**;
3. run the mutant's selected tests;
4. restore the files from the pristine copy and re-hash them;
5. record the verdict and rewrite the report.

Controls run first. A run whose controls misbehave is **UNTRUSTED** and stops,
because every later verdict would be read through a broken instrument.

## 2. Interface & invocation

```
mutant-run --run-dir RUN --mutants FILE [--only ID,ID] [--timeout SECS] [--heartbeat SECS]
```

- **`RUN`** holds `tree/` (a scratch copy, never a version-control working
  tree), `pristine/`, `logs/`, `state.json`, `report.md` and `runner.log`. Refuse
  a `RUN` outside a configured scratch root.
- **Mutants file:** a JSON list of
  `{id, file, old, new, tests, killer, control?: "dead"|"alive"}`, or
  `edits: [{file, old, new}, ...]` for a multi-site mutant. `tests` is the
  selector the build tool accepts; `killer` names the test expected to kill it
  (`-` when none is predicted).
- **Controls:** a `dead` control is a mutant that must be killed (a known-bad
  edit); an `alive` control must survive (a provably equivalent edit). A dead
  control that survives or an alive control that dies makes the run UNTRUSTED.
- **Verdicts:**

| verdict | when | counted as a kill |
|---|---|---|
| KILLED | a test failed or errored for a reason other than startup | yes |
| KILLED-BY-STARTUP | the run failed to compile, load its context or start, including a startup error carried inside an assertion message | **no** |
| SURVIVED | every selected test passed | no |
| INVALID | `old` not found exactly once, no test ran, a file missing, or the unmutated baseline of that selection is not green | withdrawn |
| TIMEOUT | the bound was hit; names the in-flight test | no |

  A KILLED by a test other than `killer` is still a kill, annotated.
- **Exit codes:** 0 done; 1 UNTRUSTED; 2 refused (usage, path, mutants file,
  busy lock); 3 integrity (a restore did not match its hash: the tree must not
  be used); 130 interrupted.
- **Outputs:** `runner.log` lines `BASELINE <sel> GREEN|RED|EMPTY|TIMEOUT`,
  `HEARTBEAT <id> <N>s ... idle=<s>`, `MUTANT <id> <VERDICT> <s>s by=<tests>
  expected=<killer>`; one log per mutant; `report.md` as a mutation-register
  table, with INVALID mutants listed apart as withdrawn.

## 3. Approach / algorithm

```
take lock on RUN (second runner: exit 2)
load state.json; load mutants; hash each mutant's definition
for each control, then each mutant:
    if state says done and definition hash unchanged: skip
    if state says applied (a killed runner left an edit): restore from pristine, verify hash
    count old in pristine content; != 1 -> INVALID
    baseline(selection) once per selection, cached; not green -> INVALID
    copy each touched file to pristine/ (first time), record its hash
    state[id] = applied; write state atomically
    write mutated content; run tests under timeout with heartbeat
    finally: restore every touched file; re-hash; mismatch -> exit 3
    classify; state[id] = done; write state and report atomically
    after the controls: any misbehaving -> report UNTRUSTED, exit 1
```

- **Exactly once, checked on pristine content before anything runs.** A
  pattern that matches twice mutates code nobody intended; one that matches
  nowhere is a no-op that would "survive".
- **A baseline per test selection.** A mutant run against a selection that is
  already red would read every failure as a kill.
- **Startup failures are not kills.** A mutant that breaks compilation or
  startup is killed by the build, not by an assertion about behaviour. Match the
  stack's startup signatures in every failure and error message, not only in
  the run's exit status.
- **State is written atomically after every step, and `applied` before the
  run.** Resume is rerunning the same command: done mutants with an unchanged
  definition are skipped, and a leaked edit is restored under a hash check.
- **Run it detached on the machine that executes the tests**, and drive it
  with absolute paths. A run stepped from a laptop over a link that can drop
  loses its place on every drop.

## 4. Portable vs blueprint

- **Portable:** the mutants-file shape, controls first, the verdict table,
  exactly-once, baseline per selection, pristine copies with hash-checked
  restore, atomic state with resume, the exit codes.
- **Fill in per project:** the test command and its selector syntax, the
  report parsing, the startup-failure signatures, the scratch root, and any
  derived artifact that a guard recomputes from the mutated file.
- **Per stack, Maven with Surefire (`library-corpus/cli/maven.md`):** run
  `-Dtest=<selection> -Dsurefire.failIfNoSpecifiedTests=false` in the build's
  pinned image; read `target/surefire-reports/TEST-*.xml` for failures and
  errors; an empty report set is INVALID ("no test ran"), never SURVIVED; treat
  a compilation error and a context-load failure (in Spring, "Failed to load
  ApplicationContext", `BeanCreationException`) as KILLED-BY-STARTUP; run
  offline against a warm local repository volume.

## 5. Pitfalls and sharp edges

- **A guard over a derived artifact kills every mutant of its inputs.** When a
  checksum, fingerprint or generated pin is recomputed from the files a mutant
  edits, the mutant dies to the guard, not to the behaviour test. Either
  regenerate the derived artifact inside the mutant's run (and restore it), or
  record that mutant as untestable this way. Never let a mutant regenerate the
  guard's own code or its pin: that tests nothing.
- **An alive control that starts failing usually means the harness changed**,
  not the code: the run is UNTRUSTED for a reason, and the fix is upstream of
  the mutants.
- **`cd dir && nohup cmd &` backgrounds the whole list**, and `$!` is the
  subshell, not the runner. Launch with absolute paths and nothing in front.
- **Do not edit the runner's own files while a run is live**
  (`tool-corpus/testing/long-stage-progress-runner.md` §5).

## 6. Tests that cover it

Cover, against stub test commands so no build runs
(`tool-corpus/testing/remote-stub-fixture.md`, whose runner stub hands the
test arguments to a scenario): each refusal (path outside
the root, busy lock, malformed mutants file); exactly-once (zero and two
matches are INVALID); a tampered pristine copy exits 3; each verdict path;
a startup error inside an assertion message is KILLED-BY-STARTUP; a multi-edit
mutant; controls trusted and untrusted (both directions); resume after the
runner is killed mid-mutant restores the leaked edit and skips done mutants;
a changed definition re-runs the mutant.

- **How to run the tests:** `<the plant's test command for its implementation>`

## 7. References & neighbours

- **Doctrine:** `core/method/delegation-cycle-economy.md`
  (`delegation.mutation-at-end`); `skill-corpus/mutation-verify.md` (choosing and
  reading mutants).
- **Related tools:** `tool-corpus/testing/long-stage-progress-runner.md` (the
  heartbeat and in-flight naming the runner reuses);
  `tool-corpus/testing/static-config-contract-gate.md` (its mutation register
  rules for a gate); `tool-corpus/testing/working-tree-snapshot.md` (producing
  the scratch copy).
- **Sources:** distilled from practice; no external URL.

## 8. Changelog

- 2026-10-14 — created by docs-librarian.
