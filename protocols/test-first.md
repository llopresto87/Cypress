---
name: test-first
description: The WORKFLOW that drives every production change through RED → GREEN → REFACTOR → COMMIT — entry conditions (spec, plan, wiki), characterize-first on untested code, the per-phase gates, the bug-fix and pure-refactor variants, the migration safety gate, recorded exceptions, and exit conditions. Use whenever you are about to write or change production code. How to SHAPE each test — level selection, contract naming, one outcome per test — is the test-first skill.
id: protocol.test-first
tier: 2
kind: protocol
origin: seed
title: test-first — the RED→GREEN→REFACTOR→COMMIT workflow that authorizes every production change
owns:
  - rule.test-first
  - test-first.cycle
  - test-first.characterize-first
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
est_tokens: 2300
command: true
---

# Protocol: test-first

Use this whenever you are about to write or change production code.
The deliverable is a sequence of RED → GREEN → REFACTOR → COMMIT
cycles, each tied to one or more contracts in a spec, with the
verification gates passing at the end.

This node owns **the test-first rule** — tests authorize code; you
integrate, not bolt on. No production code without a failing test
that authorizes it: RED → GREEN → REFACTOR → COMMIT, per increment.
The test encodes a named spec contract and must fail for the right
reason first; GREEN adds the minimum new behavior, integrated into
the file, not stapled to its edge; REFACTOR is not optional when you
touched existing code, and an additive-only diff is a red flag to
justify. The sections below are the rule's operational form; its
exceptions are explicit and recorded in grill.md §9.

## Entry conditions

- A spec exists in `docs/graph/specs/` for the behavior being added or
  changed.
- A plan exists in `docs/graph/plans/grill.md` §9 with the increments named.
- The relevant libraries are wikified in `docs/graph/libraries/`.

If any of these is missing, back up to the protocol that produces it
(`specify`, `grill`, `ingest-library`) rather than starting test-first.

## Existing code with no test — characterize first

The cycle below assumes a spec contract you can turn into a failing
test. On legacy or adopted code that has no spec and no test, you
cannot: nobody has written down what the code is *supposed* to do, so a
test asserting the "correct" answer would just encode your guess.

Before you change such code, write a **characterization test** that
pins what it does *today* — bug included. Run it; it passes (it
describes reality). Name it so no one mistakes it for a correctness
claim (`characterizes_…`, not `should_…`), and note in its docstring
any behavior you believe is wrong, linking the grill.md item that
tracks fixing it. Now you have a safety net: make your change, and the
characterization test fails in exactly the way you intended — that
failure is your RED, and the normal cycle resumes. Adopting a codebase
does not license editing untested code bare.

## The cycle

For each increment in the plan:

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
4. If you cannot get RED for the right reason, the test is wrong or
   the contract is wrong. Fix the test or revisit the spec.
5. Update the spec §10 (Test mapping) row: status `red`.

**Inherited suites — prove RED by mutation.** A suite you inherited
that was authored without test-first, and that is green the moment you
arrive, is untrusted: you have never watched it fail, so you do not
yet know it asserts anything. Before you rely on it, do the
adoption-time analog of RED — deliberately reintroduce in the
production code the historical defect a test claims to guard against,
confirm the suite fails for *that specific reason*, then revert. Only
a green you have seen turn red and back is a trusted green.

### GREEN — minimum behavior, integrated

1. Add the minimum *new behavior* that turns RED into GREEN. "Minimum"
   is about behavior, not diff size: no speculative generality, and no
   expansion into unrelated code (file that separately, per the scope
   rule). But integrate what you do add into the file's existing design
   — do not append a function at the bottom or special-case the new
   requirement around logic that should itself change.
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
4. On a pure-addition to green fields the refactor may be trivial. But
   **when you touched existing code, REFACTOR is not optional** — an
   additive-only diff that left duplication or dead code behind is an
   incomplete increment, not a small one. (The append-only artifacts —
   grill.md history, ADRs — are the deliberate exception; there you
   supersede, not rewrite.)

### COMMIT — record the increment

1. Append to grill.md §15 (Changelog): increment title, spec
   contracts covered, files touched, tests added, gates run, gates
   passed.
2. Update the spec's §10 (Test mapping) with the actual test names
   and file paths.
3. Name any library idiom this increment taught — and any durable
   tool it built — in your handback payload; the close-out librarian
   persists them (§3.7/§3.8). You do not edit the wiki or the tool
   catalog inline.
4. If using version control, commit. Commit message:
   `feat(<scope>): <contract slug> — implements SPEC-NNNN`
   or `fix(<scope>): <bug slug> — adds regression for SPEC-NNNN`.
5. Hand the diff to `reviewer`.

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
2. A bug confirmed but not yet fixable is not dropped from coverage:
   encode it as an explicitly-named, intentionally-failing test inside
   the regular suite, documenting the root cause — the debt stays
   mechanically visible on every run and the eventual fix inherits a
   ready acceptance check.
3. The regression test stays in the suite forever. Do not delete it
   when the bug is fixed; that's how regressions return.

## Refactoring (no behavior change)

A "pure refactor" — same behavior, different shape of code — is a
special case:
1. The existing tests must pass before you start.
2. You do not write a new test (no new behavior to author).
3. You change the code.
4. The existing tests must still pass.
5. If any existing test breaks, either: (a) you changed behavior
   accidentally and must roll back, or (b) the test was testing
   implementation rather than behavior, and either the test is
   wrong (fix it) or the refactor is changing the spec (back up
   to `specify`).

## Migration safety gate

Before any framework, ORM, or runtime **major-version** migration,
confirm the change is observable. "No migrations tool and no tests,
with the schema driven only by the ORM's auto-DDL" is itself a
**blocking** finding that must be closed first — characterization
tests especially (see the inherited-suites rule under RED). A
migration run against an unguarded schema is not an increment; it is
an unverified change waiting to surface in production.

## Exceptions to test-first

Explicit exceptions, recorded in grill.md §9 with a rationale and a
date:
- **Throwaway prototypes** to learn about a library or approach.
  Mark the code clearly; do not merge it.
- **Pure configuration changes** (raise a timeout, add a log
  scope) where there is no behavior change to verify.
- **Type-only changes** in a strongly typed language where the type
  checker is the verifier.
- **Generated code** where the generator itself is tested.

If you find yourself reaching for "exception" frequently, that is a
signal that test-first is not landing — surface this to the
orchestrator so the team can address it directly.

## Exit conditions

- Every spec contract for the increment has a passing test.
- The full suite is green.
- The verification gates from `verify` protocol have run.
- grill.md and the spec are updated.

## Anti-patterns

- **Writing tests after the code "to be safe".** That's not
  test-first; that's documentation. The whole point of RED is to
  make the next step's design pressure-test the spec.
- **Tests that pass without the code present.** Either the test
  is not exercising the contract, or the contract is met by some
  other code path. Investigate. Ask the same question of a whole
  gate phase before crediting it as coverage: if the phase that
  ran would have passed identically against the pre-change code,
  it proved zero coverage of the change, however green it is.
- **One giant test per increment.** Many small tests, each
  exercising one contract, with clear names. The reviewer should
  be able to read the test names and reconstruct the spec.
- **Testing through.** Don't write an end-to-end test for a pure
  function; write a unit test. Don't write a unit test that mocks
  three layers; promote it to integration.
- **Mocking everything.** Mocks for time, randomness, network, and
  external services are reasonable. Mocks for the object under
  test or its immediate collaborators are a smell — the design is
  probably too coupled.
- **Assuming dev-machine green means CI green.** Headless or
  browser-based tests that pass locally are not guaranteed in CI —
  minimal build images often lack a browser binary or another
  runtime the test needs. Verify the CI image actually contains it.
