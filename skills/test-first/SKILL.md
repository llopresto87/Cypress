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
artifacts:
  - templates/spec.template.md
est_tokens: 350
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
  read the test names and reconstruct the spec.
- **The body is Given/When/Then.** Set up Given, perform When,
  assert Then.
- **One outcome per test** (or one assertion group about the same
  outcome). Many small tests beat one giant one.

## Reference files

- `docs/graph/protocols/test-first.md` — the workflow this technique serves.
- `docs/graph/templates/spec.template.md` — where contracts live (§4) and
  test mapping is recorded (§10).
- `docs/graph/agents/04-tester.md` — the agent that owns the cycle.
- `docs/graph/agents/02-implementer.md` — the agent that writes GREEN.
