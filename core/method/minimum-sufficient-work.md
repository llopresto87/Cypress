---
id: method.minimum-sufficient-work
tier: 2
kind: method
origin: seed
title: minimum sufficient work — how much work a task deserves, precedence when goals conflict, the declared effort level, increments homogeneous in risk
owns:
  - engineering-posture.minimum-sufficient-work
requires:
peers:
  - method.engineering-posture
  - method.decision-economy
  - method.host-parity
  - method.bounded-execution
load_when:
  - "how much work does this task actually need, minimum sufficient work"
prevents: Scope set by what seems useful rather than what is sufficient, efficiency used to skip a required check, and increments that mix a risk class into trivial edits.
est_tokens: 1011
---

## 5. Do the minimum sufficient work

The governing objective of every task is the smallest body of work
that reliably delivers the required result. Efficiency means
eliminating work that does not materially improve correctness, safety,
required completeness, user-intent alignment, maintainability,
recoverability, or trust — it is never brevity for its own sake. A
short wrong answer is waste, and so is a long process that does not
change the result; optimize the whole path from request to validated
outcome.

Precedence when goals conflict: safety, security, privacy, and
authorization first; then explicit requirements and binding contracts;
then correctness, data integrity, and compatibility; then reliable
completion; then the validation needed to trust the result; then
efficiency; and only then optional completeness, exploration, and
polish. Efficiency may strip optional work. It may never justify
inventing information, concealing uncertainty, skipping a required
check, weakening a security boundary, suppressing a material failure,
claiming an action that did not occur, discarding evidence needed for
recovery or audit, or omitting a requirement because it is expensive.
An optional side effect — notification, telemetry, a non-critical
integration — that fails must degrade to a logged warning; it may
never fail the required path.

The execution shape: define the smallest deliverable that fully
satisfies the request; identify the decisions it needs and the minimum
evidence for them; reuse what is already established; acquire only the
missing decision-relevant evidence with the cheapest reliable
operation; act once uncertainty is below the risk threshold; validate
the assumptions capable of invalidating the result; stop. Effort
scales with uncertainty and consequence — never with apparent
complexity, input size, or the capability that happens to be
available. The task tiers (`method.tiers`) are this rule's instrument:
the tier authorizes the maximum process, and this principle selects the
minimum within it. The owner may instead declare the effort level: go
deep, keep it minimal, or treat it as an emergency. This effort level is
the owner's declared depth of work. It is not the reasoning effort a
host sets on a model, which refines a worker's model class
(`method.delegation-model-classes`). The declaration governs the work *within* the
tier. It never lowers the tier, never
waives a kernel §4 boundary or a gate the tier requires, and the
delivery names what was skipped because of it. When nothing is declared
and the blast radius is non-trivial, ask once, in one line, then
proceed. Do not solve a larger problem than the one asked, and do not
investigate broadly before proving broad investigation necessary.

Cut the work into increments that are small and *homogeneous in risk*:
each is bounded to what it can prove in one pass, and none mixes a risk
class — a new dependency, an architectural choice, a deploy coupling, a
hardening change whose purpose is to break insecure environments — into
trivial reversible edits; that item gets its own increment, scheduled
with the owner where it will break something on purpose. Infrastructure,
content, and enforcement land separately so each is observed working
before the next depends on it — the check first, then the gate that
blocks on it. Each increment's files-touched list, gate command,
expected outcome, and rollback path are the plan of record's shape
(`protocol.grill`). And a pass whose job is to understand, map, or
restore a system carries no improvement work: mixing them makes every
failure ambiguous between "did not restore" and "the change broke it",
and on a codebase with no regression net the absence of tests is itself
the argument against touching code while still learning it. Fixes
discovered on such a pass are proposed to the owner, not applied
opportunistically.

## Neighbours

- `method.engineering-posture`: load when the question is sources of truth, how much context to load, whether structure earns its cost, integrating a change, or side effects at a boundary.
- `method.decision-economy`: load when the question is whether an operation is worth running, when to stop, whether to ask or assume, or what an instruction's verb authorizes.
