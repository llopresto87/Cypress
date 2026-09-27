---
name: test-first
description: The test-SHAPING technique applied inside the test-first protocol — pick the lowest test level that exercises the behavior (unit, integration, contract, e2e, golden, property-based, evaluation), name the test after the spec contract, and assert one outcome per test. The workflow itself (entry conditions, RED-GREEN-REFACTOR-COMMIT gates, variants, exceptions) is the test-first protocol.
id: skill.test-first
tier: 2
kind: skill
origin: seed
title: 'test-first — shape each test: lowest level, contract-named, one outcome'
owns:
  - test-first.shaping
  - test-first.level-selection
  - test-first.lean-suite
  - test-first.no-lint-only-tests
requires:
  - protocol.test-first
peers:
  - skill.spec-author
load_when:
  - "shape a new test"
  - "pick a test level"
  - "name a test after a spec contract"
  - "unit vs integration vs e2e choice"
  - "one outcome per test"
  - "consolidate or shrink a test suite, duplicate or expensive tests"
  - "project-specific test, generic or synthetic fixture"
  - "coverage lint wants a test for a contract"
artifacts:
  - templates/spec.template.md
prevents: Tests written at the highest level that happens to work, named after the function rather than the contract, asserting several outcomes at once so a failure names no cause.
est_tokens: 1286
---

# test-first (the test-shaping technique)

The cycle — RED → GREEN → REFACTOR → COMMIT, its per-phase gates, the
characterize-first rule, the bug-fix and refactor variants, the
migration safety gate, and the recorded exceptions — lives in
`docs/graph/protocols/test-first.md`, the one home for the workflow. This skill
owns the craft of shaping each test the cycle asks for.

## Test level selection

Pick the lowest level that exercises the behavior.

| Level             | Use when                                                |
|-------------------|---------------------------------------------------------|
| Unit              | Pure logic, transformations, parsers, validators.       |
| Integration       | Crossing an adapter (DB, file, network, SDK, model).    |
| Contract          | API endpoints, structured outputs, message schemas.     |
| End-to-end        | Critical flows — one or two per flow, no more.          |
| Golden / snapshot | Deterministic transforms, prompts, renderers.           |
| Property-based    | Algorithms where the property is clearer than examples. |
| Evaluation        | LLM/VLM behavior, with rubrics and pass thresholds.     |

## Test shape

- **The name names the contract.** The spec §4 contract slug,
  transformed for the language's convention
  (`test_submit_valid_form_returns_2xx`,
  `submitValidFormReturns2xx`, …). The reviewer should be able to
  read the test names and reconstruct the spec. A name that claims
  more than its body asserts is worse than an empty assertion: the
  standard way to ask "is this covered?" is to search test names, and
  a false name answers yes.
- **The body is Given/When/Then.** Set up Given, perform When,
  assert Then.
- **One outcome per test, or per named sub-case** (or one assertion
  group about the same outcome), so a failure names its cause. When
  several outcomes follow from one expensive action, the action runs
  once and each outcome is asserted as its own named sub-case; what
  must not happen is one giant test whose first failure hides the rest.
- **Reusable code is tested over its consumers, not for one of them.**
  When the code under test serves many consumers (plugins, packs,
  tenants, configurations, projects), the default test checks a
  property over every consumer on disk, or checks the behavior over
  one generic, synthetic fixture consumer (never production data,
  kernel §4). No test class is named for a real consumer, and no test
  asserts a real consumer's literal values: such a test pins the
  shared code to one customer and breaks when that customer changes.

## No test only to turn a lint green (`test-first.no-lint-only-tests`)

A coverage lint can report a contract that no test names. Never answer
it with a test that asserts nothing new just to turn the lint green. If
an existing test already asserts the contract, cite the contract's slug
in that test. If no test asserts it, the gap is real, and the contract
gets the test it needs.

## Keeping the suite lean (`test-first.lean-suite`)

Every increment adds its own tests, so a suite only grows unless
someone shrinks it on purpose. Duplicates and repeated expensive setup
pile up unseen until the whole suite is measured.

- **Consolidate by action, not by safe fold.** Where several tests pay
  for the same expensive action (a repository copy, a fresh
  environment, a full gate run), run the action once and assert each
  outcome under its own name. Per-stage happy-path tests that one
  end-to-end chain run already covers go; so do tests written for one
  real consumer (above) and tests that assert nothing a sibling does
  not. Merging only the folds that are obviously safe lowers the count
  and leaves the cost where it was.
- **A size target is an aspiration, never a quota.** A number chosen
  up front is a direction, not something to delete toward.
- **Every deleted test names its survivor**: the test that still fails
  when the deleted test would have (the one that still kills its
  mutants). With no survivor, the deletion is a coverage loss and is
  recorded as one. A reduction pass that ends with more tests than it
  started with owes an explanation for each addition.
- **Consolidation is planned work.** Schedule it once the spec's
  behavior has landed, as its own increment in the plan-of-record
  (`protocol.grill` owns increment order). Run mid-spec, beside the
  critical path, it competes with the work it should follow.
- **Review for the smells that inflate a suite**: byte-identical test
  bodies, several tests calling the same expensive helper with the same
  arguments, and expensive per-test setup. The seed's tool corpus
  catalogs a lint that flags them,
  `tool-corpus/testing/test-hygiene-lint.md`.

## Reference files

- `docs/graph/protocols/test-first.md` — the workflow this technique serves.
- `docs/graph/templates/spec.template.md` — where contracts live (§4) and
  test mapping is recorded (§10).
- `docs/graph/agents/04-tester.md` — the agent that owns the cycle.
- `docs/graph/agents/02-implementer.md` — the agent that writes GREEN.
