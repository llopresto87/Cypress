---
id: method.incident-posture
tier: 2
kind: method
origin: seed
title: incident posture — smallest reversible containment, forensic trail kept intact, remediation sequenced by exposure, residuals owned
owns:
  - incident-posture.containment
  - incident-posture.closure
  - incident-posture.evidence
  - incident-posture.sequencing
  - incident-posture.residuals
  - incident-posture.register-closure
requires:
peers:
  - method.secrets-posture
  - method.release-posture
  - method.contract-posture
  - protocol.recover
  - protocol.canonize
load_when:
  - "production is broken, fix forward or roll back, restore the database"
  - "incident postmortem, what actually closes the incident"
  - "contain an outage without wiping what explains it, forensic trail"
  - "prioritize the remediation backlog, which vulnerability or exposure first"
  - "out of scope finding, park it as a residual with an owner and a trigger"
  - "risk register row, accepted risk, can this risk be closed"
est_tokens: 1750
---

# Incident posture

What to do while something is broken, what makes it closed, and how the
leftovers are carried. Six facts. `protocol.recover` owns the failure
classes and the three-attempt boundary for a failed worker or gate; this
node owns the operational choice once a failure has reached a running
system, and the register discipline that outlives the incident.

## 1. Prefer the smallest reversible containment or forward fix

Fix-forward is the default. On a failure the first move is the smallest
forward fix or the smallest reversible containment — not a reversal.
Classify the failure before reversing it (`protocol.recover`): a
configuration fault takes the non-destructive path; the destructive
data-restore path is a separate, separately approved last resort; never
reach for the lossy path when a lossless one recovers the fault ("do not
restore a database to fix a configuration problem"). Reversal is a
considered choice measured against fixing forward, never the reflex
response to a failed change, and it is never autonomous — a tool
proposes and stops, and the explicit confirmation names the resource and
the intent (kernel §4). Record why reversal was chosen and who approved
it: how often reversal was needed is process telemetry for the plan of
record, not just recovery history. When a later problem surfaces in
earlier work that still serves the goal, build on top rather than
revert. A cheap containment ships ahead of the structural mechanism only
if it demonstrably closes the exposure and makes the mechanism cheaper
to land; shape a tactical fix so the structural one becomes a deletion
of call sites, and schedule the root-cause lever in the same plan so
relief never becomes the whole fix. Under `real-production` a
containment that leaves the improper state standing is `status: hotfix`
with an owner, never `closed`.

## 2. An incident closes with a test, a gate, and a durable rule

Incident follow-up produces three artifacts: a regression test
(`protocol.test-first`, the bug-fix path), a new gate where one would
have caught it (`protocol.verify`, adding a gate), and a generalized
prevention rule promoted into the system's durable invariants through
`protocol.canonize` — a graph fact or a spec contract, never the
narrative as a one-off. The story is the least durable part of the
record and is never the closure. When the same accident recurs, the
one-off note becomes a documented invariant of the system: twice is why
a hazard is a fact. The incident's status row reads `closed` only with
`status_evidence` — the test name, the gate run, the node it landed in —
which `docs/graph/status-register.py` checks; a closure without evidence
is `hotfix` wearing a green badge.

## 3. Contain without destroying the evidence

Stop the unsafe process; do not wipe the state that explains what
happened. Capture time, environment, build or artifact reference,
correlation identifiers, and redacted logs — never credentials, tokens,
or sensitive payloads (`method.secrets-posture` names-only;
`method.contract-posture` for what a log may carry). Facts the record
does not carry — contacts, notification thresholds, regulatory timelines
— are marked not recorded rather than implied. Recovery is declared
against the automated gate that owns the property (the smoke or contract
gate re-run), never by inspection: eyeballing a dashboard is not a
recovery claim.

## 4. Sequence remediation by live exposure and by what it unblocks

Order a backlog of known problems by confirmed reachability and risk
concentration, not by effort or by how untidy something looks: an exposed
credential outranks everything; a working-but-untidy configuration
outranks nothing. For a confirmed-reachable critical vulnerability, ship
the fastest fully reversible override immediately and pursue the durable
upstream fix in parallel — a layered schedule (stopgap, durable, estate-
wide), not a set of ranked alternatives — and sequence within the exploit
chain so each fix makes the next one meaningful. Also rank by what
unblocks the most downstream work, and say explicitly when a ranking is
blocking-rank rather than execution order, so a reader does not serialize
parallelizable items. Run each item as its own reviewable increment;
batching hides priority differences and enlarges the reversible unit.
Recurrence is a scheduling signal: a deferred fix whose failure mode
happens a third time is promoted ahead of its batch.

## 5. Carry an out-of-scope finding as a named residual with an owner

Work discovered outside the current scope is neither silently fixed nor
dropped. It is filed as a named residual or forward risk with its blast
radius, the trigger that restarts it, and the owner who carries it — in
frontmatter as `status: deferred` with `owner` and `reopen_when` (schema
§Lifecycle status), so `status-register.py --deferred` can list it and
the plan's open-questions section (`protocol.grill` §12) can point at it
rather than restate it. Dropping a capability from scope is an explicit
decision with an owner's confirmation; the same outcome reached by
omission is a defect. A legitimate-but-unneeded option is recorded
deferred with its trigger, not rejected on principle, so the case is not
re-argued later; a deferral records the condition that changed, the
evidence that makes deferring safe, and the trigger that restarts the
work. After a remediation pass, publish the residual: each item with why
it remains, what would close it, and the cost, so the remaining exposure
is a decision rather than an oversight. A transitional contract carries a
retirement trigger and is deleted when its premise ends, never relaxed
to keep a suite green (`protocol.verify`'s self-expiring exception is the
mechanism); a contested version or configuration choice records a named
fallback and the exact gate result that triggers it. Known hazards live
as dated, individually titled sharp edges on the owning node, linked and
never restated. Scope a work group by what it can finish; every excluded
item is a named, owned residual.

## 6. A risk register row is closed only by evidence

Every row carries its severity, an explicit disposition, an owner, and
the specific check that would prove the mitigation worked; a register is
done when no row lacks one of those. A risk closes against a quotable,
written human attestation held in the repository — `closed` with
`status_evidence`, never by assertion, and never by age: an open risk
does not become an accepted one because nobody looked. Resolved rows
stay visible with what closed them; corrections are appended, not
deleted; a fix that changed the shape of a problem without removing it
is recorded as "still open, different shape". An owner's declined fix is
an accepted residual: dated, with its reachability argument and the
escalation that fires if the reason stops holding — and where the
acceptance is standing, it is a `deviation` node with `ends_when`, so a
later reader sees a decision rather than an oversight. A list of settled
decisions that reviews may not re-raise is legitimate, bounded by its
counter-rule: you cannot accept a risk you were never shown. A control
gap that has not yet caused harm is a latent gap with its confirmed
negative, closed before the next event rather than after. Once
remediation SLAs are published they bind the team; a change to
remediation capacity is a compliance decision, not only an engineering
one. `status-register.py --open --hotfix` at close-out (`protocol.canonize`)
is the mechanical ask.

## Neighbours

- `method.release-posture` — the rehearsed reversal and restore point
  this node's containment relies on — cross when the reversal path itself
  is in doubt.
- `method.secrets-posture` — the remediation order for an exposed
  credential — cross when the incident is a leak.
- `method.contract-posture` — honest errors and payload-free logs that
  make evidence usable — cross when the trace is the problem.
- `protocol.recover` — classify the failure before any move — cross
  first, always.
- `protocol.canonize` — the close-out that persists the durable rule and
  runs the register ask — cross when the incident is ending.
