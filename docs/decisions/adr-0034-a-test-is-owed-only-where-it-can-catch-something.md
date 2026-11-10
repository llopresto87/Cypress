---
status: accepted
status_date: 2026-11-10
owner: seed steward
---

# ADR-0034: a test is owed only where it can catch something; the architect sets how each contract is checked

## Status

`accepted`. Recorded 2026-11-10 from four owner decisions given that day, which
this record transcribes and does not re-open. It amends ADR-0023 in part (the
rule it recorded now reaches the roles that decide and the gates that ask) and
amends the owner decision of 2026-11-02 that tests are planned with
intelligence before they are written, not deduped after: the first half stands
and gains OD3 below.

## Date

2026-11-10

## Context

The seed already had rules against tests that prove only that a change is
present (`test-first.proportionate-checks`). They did not reach the roles that
decide whether a test exists: after an install, the architect's, the tester's
and the reviewer's loaded prompts carried none of the rule's sentences, and the
tester's charter said every increment begins with a failing test and a test is
named after its contract. The gates asked for the opposite: the spec lint wanted
a test file naming every live contract, the plan lint kept a test on any row the
planner could not call, and the implementer stopped without a failing test. A
worker following the text it always loaded wrote the pointless test.

## Decision

The owner decided on 2026-11-10 that:

- **OD1.** The architect sets how each contract is checked (`test`, `run`,
  `review` or `covered`); the tester can challenge it.
- **OD2.** For low-risk logic off trust paths, the implementer writes the test
  and the code in one spawn.
- **OD3.** A test that catches nothing is removed: inside the unit of work that
  created it, automatically; anything older is flagged and removed in a batch
  the owner confirms. Graft and grow never remove a test.
- **OD4.** These amend two earlier decisions in part: the decision of
  2026-11-02 keeps its first half and gains OD3, and the rule that a RED writer
  adds, merges or drops no case is relaxed for dropping and merging only.

Delivery landed first, on its own: the rule is the first section of its node,
the architect, tester, reviewer and orchestrator carry it through
`always_loads:` by slug, and `tools/delivery_rules.py` fails a role whose loaded
prompt lacks it, in the seed and in a plant (`install.sh --check`). The gate
changes (kinds, a risk-based §10, evidence by kind, authorization by a declared
run or review, the worth check, removal) follow in later steps of the same
round; this record fixes the rules they implement and does not claim any of them
has landed.

## Consequences

- A contract with no kind stays readable as `test`; a plant's specs and plans in
  today's form keep linting. Conversion is a shape migration the steward
  ratifies.
- Trust paths (security, data-integrity, money) keep an independent tester, the
  adversarial controls, the security pass and its mutation pass.
- A bug reproduction is always written and stays; a security control is never
  removed automatically.
- Risk: `run` and `review` become a way to skip testing logic. The architect's
  doubt defaults to `test`, the tester challenges, and the reviewer's first
  review checks that code under a `run` or `review` contract holds no logic.
- The effect on the tests plants write and the tokens they spend is not
  measured here.

## Alternatives considered

- Copy the rule into each charter with no lint: rejected, the copies drift.
- Dedupe tests after they are written: rejected on 2026-11-02 and kept so.
- A tester spawn on every increment: rejected by OD2 for low-risk logic.

## Reversibility

Reversible. Each step is a text or lint change on the seed; a plant's records
are untouched.

## Amendment, 2026-11-10

The owner decided on 2026-11-10 that the lead carries a two-line pointer to the
restraint rule and not the rule itself, because the architect slices the plan
and the kinds are set at specify. The delivery paragraph above is amended so:
the architect, tester and reviewer carry the rule through `always_loads:`, the
lead carries the pointer, and the routing examples the first delivery had
removed from the lead's charter are restored. The owner also decided that, in
the same spirit, the effort-scale and green-self-test sentences that require a
separate RED and GREEN spawn are amended for the two lowest labels off trust
paths when step T9 lands, that a spec without a `Contract form: kinds` line
accepts a `Check:` label on individual contracts and reads unlabelled ones as
`test`, that a closed spec's baseline tests are listed for the owner's
confirmation when the spec is reopened, and that the §10 mapping, not the
contract name, links a test to its contracts in new-form specs.
