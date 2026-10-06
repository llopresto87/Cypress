---
name: recover
description: The failure discipline. When a worker, gate, or delegation fails, classify the failure first (transient / deterministic / capability / ambiguity / systemic / unregistered), then take the one recovery move that class allows — never an identical retry of a deterministic failure, never an unbounded fallback chain, never a silent downgrade. Preserves partial work, keeps failures visible, and stops at three total attempts before escalating to the human with the evidence.
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
  - "permission guard refused an action the owner directed"
  - "failure cause unknown, cheapest probe first"
  - "same error every retry, is it impossible, refused or never reached"
prevents: Unclassified reaction to failure — identical retries of a deterministic error, unbounded fallback chains, and a red gate quietly swallowed to keep momentum.
est_tokens: 1948
command: true
---

# Protocol: recover

Failure is a normal output of real work; waste comes from *unclassified*
reaction to it: hammering an identical retry at a deterministic error,
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

When the evidence does not yet settle the class, the first move is the
cheapest probe that tells the classes apart, and it needs no code: one
unchanged re-run (it counts against the transient budget below), a
read-only reachability probe, or fetching the dependency ahead of the
step that needs it. Start the probes beside the fix work and record what
each one showed.

An error signature is not a class. One code or message can be deterministic for
one input and transient for another, so classify by varying the input and
seeing whether the failure follows it, never by the code alone; when the
message names a field, test that field first. A loop that exhausted its
retries shows that the attempts failed, not that the operation is impossible.
An "impossible" verdict stays an open question until a request is shown to
have reached the subject and been refused for the reason stated, because a
request that failed on the caller's side never asked it. This is the
refusal-side mirror of the positive control `protocol.verify` requires before
an empty result counts.

| Class          | Recognize it by                                                          | The one allowed move                                                   |
|----------------|--------------------------------------------------------------------------|------------------------------------------------------------------------|
| **Transient**  | Environment flake: network, rate limit, race, resource exhaustion.       | Retry as-is, **max 2**, backing off. Third failure is not transient: reclassify. |
| **Deterministic** | Same input reliably produces the same failure: compile error, failing assertion, lint, schema rejection. | **Change the input** (the code, the test, the config), then re-run. A second theory that failed is the signal to read the upstream documentation (the dependency's library page, or `protocol.ingest-library` when it has none) before trying a third. |
| **Capability** | The worker is the wrong instrument: wrong specialist, missing expertise, out-of-domain handback, LOW/NONE route band in hindsight. | Re-route: run `agent-lint --route` again with the *sharper* task statement, stated in the domain's own words, which also composes the expertise the worker lacked. A knowledge gap closes as an `expertise.*` node; commission an agent only when the work needs its own tools, model class, stance, or isolation (kernel §1). |
| **Ambiguity**  | The worker asked the brief a question, guessed, or two artifacts contradict (spec vs code, plan vs node). | Fix the **cheapest upstream artifact that owns the confusion** (brief first, then plan (grill §), then spec) and re-delegate. Widening the worker's context is not the fix; the contradiction will still be there. Inside a batch, the worker writes the question to the batch's question file and goes on with work it does not touch, or, for a reading inside a contract, on a provisional reading; the architect's one ruling pass per cycle answers it (`delegation.question-file`). |
| **Systemic**   | The harness or the system itself: wedged delegation, depth cap hit, missing tool, broken gate infrastructure. A permission guard that refuses an action the owner directed belongs here too, because neither a worker nor the session can clear it. | Stop the line. Record in grill.md §12 and report to the human with the exact evidence, visible rather than worked around. Permission refusals: see below. |
| **Unregistered** | The specialist exists on disk but the host has no such type: the session predates the projection (install, graft roster delta, freshly commissioned expert), or it is rooted at the seed rather than the plant. Reads like Systemic: it is not. | Apply `delegation.harness-registration` (`docs/graph/method/delegation-bounds.md`): preflight, re-enter rooted at the plant, or role-emulate **and record it**. Keep the line running and use the existing definition, because a second definition would be a second home for the same charter. |

**Permission refusals.** After a permission refusal, a retry claims the
refusal was transient and a re-route claims it was the worker's; before
either, show that something the guard reads has changed, since otherwise
the refusal repeats or merely moves. Hand the owner the exact step in a
form that survives a paste: one short command, or a script at a short,
stable path run by one command, with any credential read from the
environment and no secret printed, and nothing the shell reinterprets (a
long line that wraps, a leading `!`). A prompt the owner denied is a
different case: if the denial contradicts what they just asked for, say so
in one line and ask once.

An intermittent or probabilistic failure is confirmed **fixed** only on
mechanism-level evidence (a trace or observation proving the causal
path is now genuinely absent), never on a lower observed failure rate
after a change: any incidental change that reduces *exposure* to the
defect (an unrelated speedup of the racing path, say) buys a better rate
while fixing nothing. Corollary: sequence any change that would merely
reduce exposure to an open intermittent defect **after** the diagnostic
evidence is captured, never before, because doing it first makes the
defect invisible rather than fixed.

## The three-attempt boundary

Across all strategies combined, a unit of work gets **three attempts**.
The fourth move is always escalation: record the failure class history
in grill.md §12, mark the increment WIP in the delivery, and hand the
decision to the human with the evidence, because a fallback chain spends
growing resources on a falling probability of success.

**No-progress counts as failure.** An attempt that ends without
advancing its deliverable (no new artifact, no new evidence, no
narrowed hypothesis) is a **failed attempt** (usually `deterministic`
or `ambiguity`) even though nothing errored, and it consumes one of the
three. Spinning without progress is how a runaway loop evades every
error-shaped gate; this boundary is the seed's iteration cap, so it
must trip on futility, not only on failure.

## Gate-failure rule

A gate that fails **twice on the same increment** means the increment is
wrong-sized or the plan is wrong. Reopen `grill` (§3.3), split or rescope
the increment, and come back through `test-first`. A third run of the same
red gate is a deterministic retry.

## Preserve the partial work

A failed attempt still produced evidence: the RED test that stands, the
node that was authored, the exact error, the classification itself.
The worker's handback carries it (`status: failed`, `failure_class`,
`in_domain_work_done` with what survives) so the next attempt, or the
human, starts from the frontier, not from zero. Discarding partial
work and rediscovering it is the rework this protocol exists to kill.

## Visibility doctrine

- A failure that changed the plan is recorded in grill.md §12 with its
  class, including the recoveries that *worked* (a transient retry
  that succeeded is telemetry; two of them are a reliability signal).
- The delivery's session metrics (`docs/graph/protocols/deliver.md`) count
  retries by class; `harvest` mines them for systemic seed lessons.
- Every downgrade (a weaker gate, a smaller scope, a different specialist)
  *is a plan change* and lands in grill.md before the next attempt.
