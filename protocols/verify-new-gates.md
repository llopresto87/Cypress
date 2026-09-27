---
name: verify-new-gates
description: What makes a lifecycle status of closed honest, and what a new gate owes when verification finds a bug no gate would have caught. Use when marking work closed or promoting a spec, or when adding a gate or verification script.
id: protocol.verify-new-gates
tier: 2
kind: protocol
origin: seed
title: verify new gates — closed means evidenced, and what a new gate owes
owns:
  - verify.status-evidence
  - verify.tool-faults
requires:
peers:
  - protocol.verify
  - protocol.verify-disagreement
load_when:
  - "mark it closed, what counts as status evidence"
  - "gate script left half-applied state, environment failure or repository failure"
  - "adding a new gate or check"
prevents: Work marked closed on a promise with no evidence a reader can open, and gate scripts that half-apply or read a broken environment as a clean tree.
est_tokens: 877
---

# Protocol: verify, new gates

## `closed` means evidenced

A lifecycle status is a gate on a record the way a test is a gate on
code, and it lies the same way. `closed` means *resolved with evidence*:
`status_evidence` names a path#anchor, a commit, or a gate-run id that a
reader can open — the same thing an `executed` runbook entry records.
When that evidence does not exist yet, the honest states are `hotfix`
(resolved improperly, a proper fix owed) and `deferred` (parked, with
the condition that reopens it), each with an owner, so nothing rests as
"done" on a promise. A `closed` without evidence is the green lie one
level up: a gate without an assertion says the check ran and proved
nothing; a `closed` without evidence says the work finished and proves
nothing, and is trusted just as readily.

Promotion is the same gate at the other end of a record's life. A
specification is not promoted to a live status until executable
assertions covering its contracts exist and pass, and the promotion
lands in the same change that adds them; a live status over an empty
assertion set is a false green.

The vocabulary and each status's required companions live in
`docs/graph/_schema.md` §"Lifecycle status" — read them there, never
restate them. The enforcement is the delivered
`docs/graph/status-register.py` in its lint role: a `closed` with no
companion fails the run with ``status 'closed' requires
`status_evidence` ``, exactly as a missing gate fails `protocol.verify`.
Reviewing what is still `open` or `hotfix` at close-out is `canonize`'s.

## Adding a new gate

If verification reveals a kind of bug that no existing gate would have
caught, add a gate. New gates:
- Pick the lowest level that catches the bug.
- Get a test case that reproduces the bug (RED).
- Get added to the verification runbook in the same increment.
- Get added to CI in the next reliability-owned increment.

A gate is a tool, and a tool that can fail halfway is a second thing to
verify. Any gate or verification script you author is **all-or-nothing**:
it validates everything it will touch before it writes anything, so a
failure never leaves a half-applied state; it runs under strict error
and unset-variable handling and resolves its own root from its location,
never from the working directory; and it keeps **environment failures
distinct from repository failures** in both remedy text and exit status
— a missing interpreter, an absent fixture, or a tool that could not
start never degrades into a skip or an empty success, or a broken
environment reads as a clean tree. Fixtures raise on an environment
fault and reserve the empty result for a genuine empty success. Fail
closed by default; a soft mode for local troubleshooting is an explicit,
documented switch. Whether a check deserves to become a cataloged tool
at all is `toolcraft`'s doctrine.

## Neighbours

- `protocol.verify`: load when running the gates for a change.
- `protocol.verify-disagreement`: load when a check and its subject
  disagree, a change must preserve behavior, or a known defect is
  tolerated.
