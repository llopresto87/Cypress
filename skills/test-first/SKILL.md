---
name: test-first
description: Decide whether a test is owed (a named victim; logic that can be wrong while the code is present) and shape the tests that are, at the lowest level that exercises the behavior, one outcome each. The workflow itself (entry conditions, RED-GREEN-REFACTOR-COMMIT gates, variants, exceptions) is the test-first protocol.
id: skill.test-first
tier: 2
kind: skill
origin: seed
title: 'test-first — decide whether a test is owed, then shape it: lowest level, one outcome'
owns:
  - test-first.shaping
  - test-first.level-selection
  - test-first.proportionate-checks
  - test-first.no-lint-only-tests
requires:
peers:
  - protocol.test-first
  - skill.spec-author
load_when:
  - "is a test owed for this contract, increment or change"
  - "does this test earn its place, or only read back what was just written"
  - "shape a new test"
  - "pick a test level"
  - "name a test after a spec contract"
  - "unit vs integration vs e2e choice"
  - "one outcome per test"
  - "consolidate or shrink a test suite, duplicate or expensive tests"
  - "plan the tests for a whole spec, which existing tests already cover it"
  - "review finding needs a test, which test class owns the contract"
  - "does this test, gate or runtime check earn its place, how much rigor"
  - "project-specific test, generic or synthetic fixture"
  - "coverage lint wants a test for a contract"
artifacts:
  - templates/spec.template.md
prevents: Tests written at the highest level that happens to work, named after the function rather than the contract, asserting several outcomes at once so a failure names no cause.
est_tokens: 1719
---

# test-first (whether a test is owed, and its shape)

The cycle (RED → GREEN → REFACTOR → COMMIT, its per-phase gates, the
characterize-first rule, the bug-fix and refactor variants, the
migration safety gate, and the recorded exceptions) lives in
`docs/graph/protocols/test-first.md`, the one home for the workflow.
This skill decides whether a test is owed, then shapes each one the
cycle asks for.

## A test is owed only where it can catch something (`test-first.proportionate-checks`)

The one home for when a check exists (a test, a gate, a guard in
delivered code) and what it may cost. Other nodes link here.

- **Name the victim.** A check exists for what breaks, and for whom, if
  it is absent. No name, no check. Spec size does not set test count:
  one test may cover several contracts, and a failure mode with no
  victim gets none.
- **Nothing to get wrong, no new test.** A declarative edit (a selector,
  route, flag, config key, mapping entry, label) has a test that reads
  back the value just written: red because the line is absent, green
  because it is present, so it proves only the diff. Prove it by an
  existing test or gate that exercises it, or the cheapest real run
  (against live infrastructure a dry run is structural evidence only,
  `method.host-parity`), named with its result in the handback. It earns
  a test when it holds logic that can be wrong while present: a pattern,
  a condition, an order or precedence that changes the output, or a
  computed value; that test feeds inputs and asserts what is selected.
- **A test is cheaper than its subject.** It asserts one behavior and
  never re-implements the code under test. A long setup, a helper of its
  own, or a comment naming the load-bearing line marks it over budget:
  write a smaller test or none, and hand back what would need more code
  than its subject, unwritten, as a level or design finding.

## Test level selection

Pick the lowest level that exercises the behavior.

| Level             | Use when                                                |
|-------------------|---------------------------------------------------------|
| Unit              | Pure logic, transformations, parsers, validators.       |
| Integration       | Crossing an adapter (DB, file, network, SDK, model).    |
| Contract          | API endpoints, structured outputs, message schemas.     |
| End-to-end        | Critical flows, one or two per flow.                    |
| Golden / snapshot | Deterministic transforms, prompts, renderers.           |
| Property-based    | Algorithms where the property is clearer than examples. |
| Evaluation        | LLM/VLM behavior, with rubrics and pass thresholds.     |

## Test shape

- **The name serves the reader of a failure.** It says what broke, in
  the language's convention (`test_submit_valid_form_returns_2xx`,
  `submitValidFormReturns2xx`), and carries the spec §4 contract slug of
  each contract it covers where the slug is the link from test to
  contract. A name that claims more than its body asserts is worse than
  an empty assertion: the standard way to ask "is this covered?" is to
  search test names, and a false name answers yes.
- **The body is Given/When/Then.** Set up Given, perform When, assert
  Then.
- **One outcome per test, or per named sub-case** (or one assertion
  group about the same outcome), so a failure names its cause. When
  several outcomes follow from one expensive action, the action runs
  once and each outcome is asserted as its own named sub-case, so no
  first failure hides the rest.
- **Reusable code is tested over its consumers, not for one of them.**
  When the code under test serves many consumers (plugins, packs,
  tenants, configurations, projects), the default test checks a property
  over every consumer on disk, or checks the behavior over one generic,
  synthetic fixture consumer (never production data, kernel §4). Name
  tests generically and assert generic values: a test that pins a real
  consumer's literals ties the shared code to one customer and breaks
  when that customer changes. The same holds for a property of a
  factory, a table, or a loop: one case over the whole collection.
- **A test holds its evidence.** Each path to an effect is tested, not
  one entry point; an assertion fails when its evidence is missing;
  assertions target the component under test, not a neighbour; stateful
  behaviour is tested again after rebuilding the component that holds
  the state.
- **A test joins the class that owns its contract.** A RED born from a
  review finding extends the test class (file, fixture group, suite)
  that already asserts the contract the finding is about, so the
  contract's tests stay in one place and share their setup. Starting a
  new class is a choice with a stated reason, such as a
  setup the owning class cannot give, written in the handback and in
  the spec's §10 beside the setup-sharing lines; without one, the contract's
  coverage splits across classes that drift apart.

## Answer a coverage lint with a real test (`test-first.no-lint-only-tests`)

A coverage lint can report a contract that no test names. Answer it
by what the contract holds. A contract that holds logic is covered by the
existing test that already asserts it (cite the slug there) or, when none
does, by the test it needs, because the gap is real. A declarative
contract (the first section's test) is answered by the run or the review
that proves it, named in the spec, and gets no test. A test that asserts
nothing new only turns the lint green.

## Designing the set, rigor and shrinking

The rule for whether a test exists at all is the first section of this
node; this section is how the set is designed once it does.

- **Tests are defined once, in the spec's test design, and never by an
  increment.** The tester designs a spec's whole test set in §10 while
  the spec is specified (`protocol.specify` phase 4), before any test
  code and before any increment exists. First survey what exists: the
  tests already in the suite, the contracts they cover, the setup they
  share. Then design each case for one mechanism that can fail
  differently, with its blast radius named, give one case every
  contract it can assert, extend the class that owns a behaviour
  instead of starting one, and merge every overlap on paper. The design
  is the only place a case is added, merged or dropped. Increments are
  cut from it: an increment cites, by name, the §10 tests it turns red,
  so a test may serve several increments and an increment several
  contracts. A RED writer writes the tests its increment cites, exactly
  as designed; a case that looks missing, redundant or untestable is a
  question back to the design (`delegation.question-file`), never a new
  or dropped test on the spot. A test written to be merged or deleted
  later is a design failure, and no plan schedules a pass to shrink the
  tests the design produced: the owner decided on 2026-11-02 that tests
  are planned with intelligence before they are written, not deduped
  after. Planned whole, the set is written whole:
  the owner decided on 2026-10-14 that a spec's failing tests are
  written in one RED wave and its mutation pass runs once, batched at
  the end. The plan gives a spec's RED increments no `Depends on:` among
  one another, so `grill-lint.py --waves` puts them in one wave
  (`delegation.waves`) and the tester writes them together, not one
  increment at a time; a RED that cannot fail for the right reason until
  another increment's behaviour exists is the exception, named with its
  reason in the plan. Mutation follows `delegation.mutation-at-end`.
- **Assert one mechanism, by its behavior.** A test that passes on
  either of two implementations asserts nothing: assert the one
  mechanism, and escalate a contract that permits two shapes as a spec
  ambiguity. Where a behavioral assertion is available, assert the
  behavior rather than that code calls a function, imports a module, or
  takes a path; a mock that only counts calls fails on a rename and
  passes on wrong behavior. Mocks for time, randomness, network, and
  external services stay fine.
- **Full rigor is for high blast radius only.** Mutation proof and
  planted violations re-run after a refactor belong to the classes
  `delegation.mutation-at-end` makes mandatory, once per batch.
  Elsewhere a RED seen failing for the right reason is the proof, plus
  any sample that rule records.
- **The owner adds checks to runs; the seed adds none.** A new check
  joins the project's automated runs, or the running product, only by a
  recorded owner decision. An escaped bug earns a regression test; a new
  gate is `protocol.verify-new-gates`'s call.
- **Shrink on purpose, and only what no design produced.** An inherited
  suite, or one written before this design existed, is cut by its own
  increment (`protocol.grill`). Every deleted test names its survivor,
  the test that still fails when it would have; with no survivor the
  deletion is a recorded coverage loss. A regression test merges only
  into a named survivor (the regression rule in `protocol.test-first`). The tool corpus catalogs a lint
  for suite smells, `tool-corpus/testing/test-hygiene-lint.md`.

## Reference files

- `docs/graph/protocols/test-first.md` : the workflow this technique
  serves.
- `docs/graph/templates/spec.template.md` : where contracts live (§4)
  and test mapping is recorded (§10).
- `docs/graph/agents/04-tester.md` : the agent that owns the cycle.
- `docs/graph/agents/02-implementer.md` : the agent that writes GREEN.
