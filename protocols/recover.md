---
name: recover
description: The failure discipline. When a worker, gate, or delegation fails, classify the failure FIRST (transient / deterministic / capability / ambiguity / systemic / unregistered), then take the one recovery move that class allows — never an identical retry of a deterministic failure, never an unbounded fallback chain, never a silent downgrade. Preserves partial work, keeps failures visible, and stops at three total attempts before escalating to the human with the evidence.
id: protocol.recover
tier: 2
kind: protocol
origin: seed
title: recover — classify a failure, take the one allowed move, stop at three attempts
owns:
  - recover.failure-classes
  - recover.three-attempt-boundary
requires:
peers:
  - protocol.deliver
  - protocol.grill
load_when:
  - "a worker or gate failed, what now"
  - "retry or re-route, flaky failure"
  - "delegation came back wrong or ambiguous"
  - "gate red twice on the same increment"
est_tokens: 1150
command: true
---

# Protocol: recover

Failure is a normal output of real work; waste comes from *unclassified*
reaction to it — hammering an identical retry at a deterministic error,
widening context because a brief was ambiguous, quietly swallowing a
red gate to keep momentum. Recover makes the response to failure as
disciplined as the work itself: **classify first, then take the single
move the class allows, bounded, with the partial work preserved.**

## Classify before you react

Diagnosis precedes classification and is only as good as its evidence:
before trusting any cross-process timing comparison, prove the two
clocks are aligned via a log line that carries both processes' own
timestamps, then anchor conclusions to absolute timestamps rather than
relative or elapsed ones.

| Class          | Recognize it by                                                          | The one allowed move                                                   |
|----------------|--------------------------------------------------------------------------|------------------------------------------------------------------------|
| **Transient**  | Environment flake: network, rate limit, race, resource exhaustion.       | Retry as-is, **max 2**, backing off. Third failure is not transient — reclassify. |
| **Deterministic** | Same input reliably produces the same failure: compile error, failing assertion, lint, schema rejection. | **Never retry unchanged.** Change the input (the code, the test, the config) and re-run. |
| **Capability** | The worker is the wrong instrument: wrong specialist, missing expertise, out-of-domain handback, LOW/NONE route band in hindsight. | Re-route: run `agent-lint --route` again with the *sharper* task statement, or commission the missing expert (kernel §1). Do not re-brief the same agent harder. |
| **Ambiguity**  | The worker asked the brief a question, guessed, or two artifacts contradict (spec vs code, plan vs node). | Fix the **cheapest upstream artifact that owns the confusion** — brief first, then plan (grill §), then spec — and re-delegate. Widening the worker's context is not the fix; the contradiction will still be there. |
| **Systemic**   | The harness or the system itself: wedged delegation, depth cap hit, missing tool, broken gate infrastructure. | Stop the line. Record in grill.md §12 and report to the human with the exact evidence. No workaround that hides it. |
| **Unregistered** | The specialist exists on disk but the host has no such type: the session predates the projection (install, graft roster delta, freshly commissioned expert), or it is rooted at the seed rather than the plant. Reads like Systemic — it is not. | Apply `delegation.harness-registration` (`docs/graph/method/delegation.md`): preflight, re-enter rooted at the plant, or role-emulate **and record it**. Do not stop the line, and do not "commission the missing expert" — the definition already exists; a second one is a duplicate home. |

An intermittent or probabilistic failure is confirmed **fixed** only on
mechanism-level evidence — a trace or observation proving the causal
path is now genuinely absent — never on a lower observed failure rate
after a change: any incidental change that reduces *exposure* to the
defect (an unrelated speedup of the racing path, say) buys a better rate
while fixing nothing. Corollary: sequence any change that would merely
reduce exposure to an open intermittent defect **after** the diagnostic
evidence is captured, never before — doing it first makes the defect
invisible rather than fixed.

## The three-attempt boundary

Across ALL strategies combined, a unit of work gets **three attempts**.
The fourth move is always escalation: record the failure class history
in grill.md §12, mark the increment WIP in the delivery, and hand the
decision to the human with the evidence — never a fourth quiet attempt,
never a fallback chain that consumes growing resources on a falling
probability of success.

**No-progress counts as failure.** An attempt that ends without
advancing its deliverable — no new artifact, no new evidence, no
narrowed hypothesis — is a **failed attempt** (usually `deterministic`
or `ambiguity`) even though nothing errored, and it consumes one of the
three. Spinning without progress is how a runaway loop evades every
error-shaped gate; this boundary is the seed's iteration cap, so it
must trip on futility, not only on failure.

## Gate-failure rule

A gate that fails **twice on the same increment** is not asking for a
third run — it is telling you the increment is wrong-sized or the plan
is wrong. Reopen `grill` (§3.3), split or rescope the increment, and
come back through `test-first`. Hammering a red gate is the
deterministic-retry anti-pattern wearing a uniform.

## Preserve the partial work

A failed attempt still produced evidence: the RED test that stands, the
node that was authored, the exact error, the classification itself.
The worker's handback carries it (`status: failed`, `failure_class`,
`in_domain_work_done` with what survives) so the next attempt — or the
human — starts from the frontier, not from zero. Discarding partial
work and rediscovering it is the rework this protocol exists to kill.

## Visibility doctrine

- A failure that changed the plan is recorded in grill.md §12 with its
  class — including the recoveries that *worked* (a transient retry
  that succeeded is telemetry; two of them are a reliability signal).
- The delivery's session metrics (`docs/graph/protocols/deliver.md`) count
  retries by class; `harvest` mines them for systemic seed lessons.
- No silent downgrades: substituting a weaker gate, a smaller scope, or
  a different specialist *is a plan change* and lands in grill.md, not
  in the gap between two attempts.

## What you do not do

- You do not retry a deterministic failure without changing the input.
- You do not exceed two as-is retries for a transient failure.
- You do not re-brief the same specialist harder when the class is
  capability — re-route or commission.
- You do not widen context to cure ambiguity — fix the owning artifact.
- You do not work around a systemic failure quietly.
- You do not make a fourth attempt.
