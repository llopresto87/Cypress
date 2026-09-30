---
status: proposed
status_date: 2026-09-30
owner: seed steward
---

# ADR-0023: a declarative edit with nothing to get wrong is proved by a run, not a RED test

## Status

See frontmatter, which is the single home. Filed 2026-09-30 from an owner
report: a plant, asked to add a selector to a pipeline, set out to write a RED
test first. Revised the same day, while proposed, on the owner's follow-up that
the question belongs where increments are decided. It amends ADR-0006 in part. The contained lane still trades the
spec for proof plus a why-record; the proof is now the one the change earns.

## Date

2026-09-30

## Context

The kernel, `method.tiers` and `protocol.test-first` each said, with no
qualifier, that a production change starts from a failing test. The one
exception that came close, "pure configuration changes", applied only when
there was no *unit-testable* behavior. Almost any edit is unit-testable in the
weak sense: a test can load the pipeline file and check that the new selector
is there. So a worker reading the rules in order reached a RED test for a
one-line declarative edit, and nothing it read told it to stop.

That test proves nothing. It goes red because the line is absent and green
because it is present, so it restates the diff. It then stays in the suite and
breaks on the next rename. `test-first.proportionate-checks` already said a
check needs a named blast radius, but the absolute wording upstream won.

## Decision

`test-first.proportionate-checks` gains one criterion, and the upstream nodes
point at it instead of contradicting it:

- Before RED, name what the test could catch that the edit being present does
  not already guarantee. If the answer is nothing, write no new test.
- Prove such an edit by the run that shows its effect: an existing test or gate
  over the surface, or the cheapest real run (a dry-run, a validate command, one
  pipeline run), named with its result in the handback.
- A declaration that holds logic earns a test: a pattern (regex, glob,
  wildcard), a condition, an order or precedence that changes the output, or a
  computed value. The test feeds it inputs and asserts what it selects.

The question is asked first when the plan is sliced, not at RED: each §9
increment answers "does this need a test?" (`grill.increment-shape`), and a
`none — <why>; proved by <run>` row gets no RED spawn. The tester's hand-back
is the fallback for a row the planner could not call. `spec-lint.py` counts the
contracts such a row names as covered by its run; `none — consolidation` covers
nothing.

The kernel's §3.4 anchor, `method.tiers`' contained lane, the test-first
exceptions list, the canonize why-record, and the implementer and tester
charters carry the change.

## Consequences

- The tier does not move. A config or selector edit alters behavior, so it is
  T2 or above and keeps its reviewer audit and why-record. Only the RED test
  is replaced, by a recorded run.
- A tester briefed on such an edit hands back unwritten, naming the run.
- Risk: a worker calls logic "declarative" to skip a test. The logic list above
  is the check, and the reviewer audits the handback's claim.
