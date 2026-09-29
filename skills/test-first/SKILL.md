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
  - test-first.proportionate-checks
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
  - "does this test, gate or runtime check earn its place, how much rigor"
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
  The same holds for a property of a factory, a table, or a loop: one
  case over the collection, never one per element.

## No test only to turn a lint green (`test-first.no-lint-only-tests`)

A coverage lint can report a contract that no test names. Never answer
it with a test that asserts nothing new just to turn the lint green. If
an existing test already asserts the contract, cite the contract's slug
in that test. If no test asserts it, the gap is real, and the contract
gets the test it needs.

## Proportionate checks (`test-first.proportionate-checks`)

The one home for when a check exists and what it may cost. A check is a
test, a gate, or a check inside delivered code (validation, a guard, a
fail-closed path). Other nodes link here; they do not restate it.

- **A check exists only for a named, real blast radius.** Name what
  breaks, and for whom, if the check is absent. No name, no check. Spec
  size does not set test count: one test may cover several failure
  modes, and a failure mode with no real blast radius gets none.
- **A test is cheaper than its subject.** It asserts one behavior and
  never re-implements the code under test. A long setup, a helper of its
  own, or a comment naming the load-bearing line marks it over budget,
  and the answer is a smaller test or none; one that would need more
  code than its subject means the level or the design is wrong: hand it
  back unwritten, with that finding.
- **No disjunctions, no wiring proofs.** A test that passes on either of
  two implementations asserts nothing: assert the one mechanism, and
  escalate a contract that permits two shapes as a spec ambiguity. Where
  a behavioral assertion is available, no test asserts that code calls a
  function, imports a module, or takes a path; a mock that only counts
  calls fails on a rename and passes on wrong behavior. Mocks for time,
  randomness, network, and external services stay fine.
- **Full rigor is for high blast radius only.** Mutation proof and
  planted violations re-run after a refactor belong to the classes
  `delegation.mutation-at-end` makes mandatory, once per batch. Elsewhere
  a RED seen failing for the right reason is the proof, plus any sample
  that rule records.
- **The owner adds checks to runs; the seed adds none.** A new check
  joins the project's automated runs, or the running product, only by
  a recorded owner decision. An escaped bug earns a regression test; a
  new gate is `protocol.verify-new-gates`'s call.
- **Shrink on purpose.** A suite only grows unless someone cuts it.
  Every deleted test names its survivor, the test that still fails when
  it would have; with no survivor the deletion is a recorded coverage
  loss. Consolidation is its own planned increment (`protocol.grill`).
  The tool corpus catalogs a lint for suite smells,
  `tool-corpus/testing/test-hygiene-lint.md`.

## Reference files

- `docs/graph/protocols/test-first.md` — the workflow this technique serves.
- `docs/graph/templates/spec.template.md` — where contracts live (§4) and
  test mapping is recorded (§10).
- `docs/graph/agents/04-tester.md` — the agent that owns the cycle.
- `docs/graph/agents/02-implementer.md` — the agent that writes GREEN.
