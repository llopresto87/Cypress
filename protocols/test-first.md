---
name: test-first
description: The workflow that drives every production change through RED → GREEN → REFACTOR → COMMIT — entry conditions (signed spec, plan, wiki), the phase table that says who owns each phase and which spawn waits for which, characterize-first on untested code, the per-phase gates, the review inside COMMIT, the spec's promotion with its RED, the bug-fix and pure-refactor variants, the migration safety gate, recorded exceptions, and exit conditions. Use whenever you are about to write or change production code. How to shape each test — level selection, contract naming, one outcome per test — is the test-first skill.
id: protocol.test-first
tier: 2
kind: protocol
origin: seed
title: test-first — the RED→GREEN→REFACTOR→COMMIT workflow that authorizes every production change
owns:
  - rule.test-first
  - test-first.cycle
  - test-first.characterize-first
  - test-first.known-bug
requires:
peers:
  - protocol.verify
  - protocol.specify
  - skill.test-first
  - skill.holistic-editing
load_when:
  - "about to write or change production code"
  - "RED GREEN REFACTOR, failing test first, TDD"
  - "bug fix, regression test"
  - "legacy code with no tests, characterization test"
  - "pure refactor, migration safety"
prevents: Production changes with no failing test to authorize them, and after-the-fact tests that pass on first run and therefore prove nothing.
est_tokens: 3391
command: true
---

# Protocol: test-first

Use this whenever you are about to write or change production code.
The deliverable is a sequence of RED → GREEN → REFACTOR → COMMIT
cycles, each tied to one or more contracts in a spec, with the
verification gates passing at the end.

This node owns **the test-first rule**: tests authorize code; you
integrate, not bolt on. No production code without a failing test
that authorizes it: RED → GREEN → REFACTOR → COMMIT, per increment.
A change with nothing a test could get wrong, such as a declarative
selector or config entry, is authorized instead by the run that shows
it working (`test-first.proportionate-checks`).
The test encodes a named spec contract and must fail for the right
reason first; GREEN adds the minimum new behavior, integrated into
the file, not stapled to its edge; REFACTOR is not optional when you
touched existing code, and an additive-only diff is a red flag to
justify. The sections below are the rule's operational form; its
exceptions are explicit and recorded in grill.md §9.

## Entry conditions

- A spec in `docs/graph/specs/` covers the behavior being added or
  changed, signed in its §0 (`draft` with product ✓ architect ✓ tester ✓
  is enough to encode; the T2 covered lane needs it `active`, kernel §0).
- A plan exists in `docs/graph/plans/grill.md` §9 with the increments
  named, in dependency order, `grill-lint.py` green.
- The relevant libraries are wikified in `docs/graph/libraries/`.

If any of these is missing, back up to the protocol that produces it
(`specify`, `grill`, `ingest-library`) rather than starting test-first.

**The T2 contained lane substitutes, it does not waive.** A contained
change has no spec over its surface, so the first two conditions are
met differently: the *defect and its reproduction* stand in for the
contract text, and a grill.md entry line stands in for the §9 increment
row. Everything below this point (RED first, fails for the right
reason, GREEN, REFACTOR, the independent REVIEW) applies unchanged.
The lane buys its way out of `specify` and the grill pass, never out of
the cycle (`tiers.contained-lane`).

## Existing code with no test — characterize first

The cycle below assumes a spec contract you can turn into a failing
test. On legacy or adopted code that has no spec and no test, you
cannot: nobody has written down what the code is *supposed* to do, so a
test asserting the "correct" answer would just encode your guess.

Before you change such code, write a **characterization test** that
pins what it does *today*, bug included. Run it; it passes (it
describes reality). Name it so no one mistakes it for a correctness
claim (`characterizes_…`, not `should_…`), and note in its docstring
any behavior you believe is wrong, linking the grill.md item that
tracks fixing it. Now you have a safety net: make your change, and the
characterization test fails in exactly the way you intended: that
failure is your RED, and the normal cycle resumes. On adopted code,
characterize before every change.

## The cycle (`test-first.cycle`)

One cycle per increment, in grill.md §9 order. Each phase has an owner,
and **the table is the spawn order** (`delegation.sequencing`,
`docs/graph/method/delegation-sequencing.md`): the next increment's RED
waits for this increment's COMMIT unless §9's `Depends on:` rows say the
two are independent. How independent REDs run ahead
in a RED wave, and which GREENs follow them, is `delegation.waves` there.
One spawn may carry a batch of increments, sized by their effort labels
(`delegation.step-scope` and `delegation.effort-scale` in
`docs/graph/method/delegation-cycle-economy.md`).

| Phase | Owner | Needs | Hands back |
|---|---|---|---|
| RED | `tester` | the §9 row, the contract text, the target test paths | failing tests that fail for the right reason; spec §10 rows `red` |
| GREEN → REFACTOR | `implementer` | the RED handback (test paths, contract slugs, files) | a green, integrated diff; the RED tests run by the implementer itself, with no separate tester spawn and no test or fixture file edited, and a test that looks wrong written up as a question (`delegation.green-self-test`); affected gates run locally; spec §10 rows `green` |
| REVIEW | `reviewer` | the diff, the §9 row | severity-tagged findings; Critical/Major return to `implementer`, one more spawn, an attempt under `protocol.recover` |
| COMMIT | the session | a clean review | grill.md §15 entry with the `spawn_id`s in issue order; the commit; the spec's status advanced |

An increment whose §9 row reads `Tests to write (RED): none — …` was
judged at planning to need no test (`grill.increment-shape`): it has no
RED phase. `implementer` makes the change and runs the proof the row
names; REVIEW and COMMIT stand.

The one merge the tiers allow: a T2 increment covering a single
contract (or, on the contained lane, a single reproduced defect) whose
RED is mechanical is briefed whole to `implementer`, which writes the
failing test before making it pass (`tiers.execution-paths`); the
REVIEW spawn stays independent either way.

Only the session writes grill.md; workers report what they did in the
handback (`rule.grill`).

### RED — write the failing test

1. Identify the spec contract(s) this increment satisfies. Each
   contract is one Given/When/Then in the spec §4.
2. Write a test (or several tests) that exercise each contract.
   Names: `test_<spec_id>_<contract_slug>` or the equivalent in the
   target language. The test name names the contract.
3. Run the test. **Confirm it fails for the right reason.**
   - A test that fails because the import is missing has not yet
     achieved RED.
   - A test that fails because the function name is wrong has not
     yet achieved RED.
   - A test that fails because the *behavior* is missing has
     achieved RED.
   - A test that passes without the code present is not exercising the
     contract, or another code path already meets it: investigate. Ask
     the same of a whole gate phase before crediting it as coverage: a
     phase that would pass identically against the pre-change code proved
     zero coverage of the change, however green it is.
4. If you cannot get RED for the right reason, the test is wrong or
   the contract is wrong. Fix the test or revisit the spec.
5. Update the spec §10 (Test mapping) row: status `red`. A tester's RED
   spawn stops here and hands back (`tester.spawn-scope`).

**Inherited suites: prove RED by mutation.** A suite you inherited
green, authored without test-first, is untrusted: you have never
watched it fail. Before you rely on a test over high blast-radius code,
reintroduce in the production code the historical defect it claims to
guard against, confirm it fails for *that specific reason*, then
revert. Which code earns this, and when it runs (once per batch), is
`test-first.proportionate-checks`.

Two corollaries decide whether a mutation result can be read at all.
First, confirm the mutant actually rebuilt before believing it survived:
a toolchain that caches compiled artifacts on a cheap staleness check can
satisfy that check with an edit of the same size made in the same second,
and then runs the *old* artifact: a survived mutation that was never
executed. Second, a check that claims **exact** membership (an allow-list
of hosts, roles, scopes, media types, extensions, flags) needs a mutant
input that is a strict prefix-extension of an allowed value and one that
is a strict suffix-extension. Without both, the suite cannot tell an
exact comparison from a relaxed one, which is precisely the mutation an
attacker would make.

### GREEN — minimum behavior, integrated

1. Add the minimum *new behavior* that turns RED into GREEN, minimum in
   behavior rather than diff size, integrated into the file's existing
   design per `skill.holistic-editing`. Unrelated fixes are filed as their
   own increment (its scope rule).
2. Run the test. Confirm it passes.
3. Run the surrounding tests (or the affected module's tests).
   Confirm nothing else broke. A new green that turns another green
   red is a regression and must be addressed before proceeding.
4. Update the spec §10 row: status `green`.

### REFACTOR — integrate cleanly, with the suite green

1. Look at the code you just wrote and the code around it.
2. Remove the duplication your change introduced, delete the branch it
   made dead, fix the names and docstrings it made wrong, move code to
   the right module. This is the integration step: when it is done, the
   file should read as if the requirement had always existed, with no
   visible seam. See `docs/graph/skills/holistic-editing.md`.
3. Run the tests again after each refactor; the suite stays green.
4. On a pure addition to green fields the refactor may be trivial. When
   you touched existing code, an additive-only diff that left duplication
   or dead code behind is an incomplete increment, not a small one.

### COMMIT — record the increment

1. **Review first.** Hand the diff and the §9 row to `reviewer`. A
   Critical or Major finding goes back to `implementer` as one more
   spawn; a third red on the same increment is the gate-failure rule:
   reopen `grill` and re-slice (`protocol.recover`).
2. Run the increment's named gate from grill.md §9:
   `docs/graph/protocols/verify.md` owns that per-increment cadence, and
   the full verify pass still runs before close-out and deliver.
3. The session appends to grill.md §15 (Changelog): increment title,
   spec contracts covered, files touched, tests added, gates run with
   their outcomes, and the cycle's `spawn_id`s in the order issued.
4. The spec's §10 (Test mapping) carries the actual test names and
   file paths: the tester wrote the rows at RED, the implementer set
   them `green`. **The spec's status advances in this same change:**
   the first RED to land for a `draft` spec promotes it to `active`
   (the moment `spec-lint.py` starts counting it, and the one place a
   live status can be honest, `verify.status-evidence`); the last
   contract to turn green marks it `implemented`.
5. Library idioms this increment taught, and any durable tool it built,
   are named in the worker handbacks; the close-out librarian persists
   them (§3.7/§3.8).
6. If using version control, commit. Commit message:
   `feat(<scope>): <contract slug> — implements SPEC-NNNN`
   or `fix(<scope>): <bug slug> — adds regression for SPEC-NNNN`.

## Per-language choice of test framework

The first time test-first runs in a project, the framework is
chosen and wikified. Subsequent increments use the same framework.

Choice criteria:
- Official or near-official for the language's ecosystem.
- Fast feedback (unit tests in seconds, not minutes).
- Good failure messages (the test failure tells you *what*
  changed).
- Support for fakes, fixtures, parametrization, and the test
  levels in `docs/graph/agents/04-tester.md`.

The choice is recorded as an ADR.

## Bug fixes

A bug is, by definition, a spec the codebase failed to honor (or a
missing spec). The cycle:

1. Read the spec. Does the contract that was violated already exist?
   - If yes: write a regression test that exercises that contract
     against the buggy code, see it fail, fix the code, see it
     pass.
   - If no: the spec was incomplete. Run `specify` first to add or
     revise the contract, then write the regression.
2. **A bug a test uncovered** (`test-first.known-bug`) is marked for a fix
   and the owner is told: the session records it in grill.md §12 and names
   it in the delivery. The test that uncovered it is the bug's acceptance
   check and its ONLY test: it stays exactly as written, carries no marker
   that expects its failure, and no second test is written to assert the
   buggy behavior.
   The session dispatches `implementer` to fix the bug, then re-runs that
   same test. Until the fix lands, the red is declared in the delivery as
   WIP with its failure record (`protocol.deliver`), never hidden.
3. The regression test stays in the suite after the fix, because a
   deleted regression test is how regressions return. Consolidation may
   merge it ONLY into a named survivor that still fails if the bug returns
   (`skill.test-first`, Shrink on purpose).

## Refactoring (no behavior change)

A "pure refactor" (same behavior, different shape of code) is a
special case:
1. The existing tests must pass before you start.
2. You do not write a new test (no new behavior to author).
3. You change the code.
4. The existing tests must still pass.
5. If any existing test breaks, either: (a) you changed behavior
   accidentally and must roll back, or (b) the test was testing
   implementation rather than behavior, and either the test is
   wrong (a question for the next tester spawn; the implementer
   never edits it, `delegation.green-self-test`) or the refactor
   is changing the spec (back up to `specify`).

## Migration safety gate

Before any framework, ORM, or runtime **major-version** migration,
confirm the change is observable. "No migrations tool and no tests,
with the schema driven only by the ORM's auto-DDL" is itself a
**blocking** finding that must be closed first, characterization
tests especially (see the inherited-suites rule under RED), because a
migration run against an unguarded schema is an unverified change
waiting to surface in production.

## Exceptions to test-first

Explicit exceptions, recorded in grill.md §9 with a rationale and a
date (on the T2 contained lane, in the why-record instead):
- **Throwaway prototypes** to learn about a library or approach.
  Mark the code clearly and keep it out of the main branch: it has no
  test behind it.
- **Declarative edits with nothing to get wrong** (add a selector or a
  pipeline stage, raise a timeout, add a log scope), where the only test
  would read back the value just written. The run that shows the effect
  is the proof, named in the handback, and the operational risk goes to
  `docs/graph/protocols/verify.md`'s gates. A declaration that holds
  logic (a pattern, a condition, an order that changes the output) is
  not in this class (`test-first.proportionate-checks`). Such a change
  still tiers at T2 or above: a config value alters behavior, so it is
  never T1 (`docs/graph/method/tiers.md`).
- **Type-only changes** in a strongly typed language where the type
  checker is the verifier.
- **Generated code** where the generator itself is tested.

If you find yourself reaching for "exception" frequently on changes
that hold logic, that is a
signal that test-first is not landing: surface this to the
orchestrator so the team can address it directly.

## Exit conditions

- Every spec contract for the increment has a passing test, named for
  the contract; its targeted tests and every cross-cutting gate its
  files hit pass. The full suite runs once, at the batch tip
  (`delegation.tip-cadence`).
- The increment's named gate ran; the full `verify` pass ran before
  close-out, recorded in the runbook by the tester that ran it.
- The review is clean (no Critical or Major open).
- grill.md §15 carries the increment with its `spawn_id`s; spec §10
  carries the tests; the spec's status is `active` (or `implemented`
  when every contract is green); `spec-lint.py` and `grill-lint.py`
  exit 0.
