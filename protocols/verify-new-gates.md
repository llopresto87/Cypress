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
est_tokens: 920
---

# Protocol: verify, new gates

## `closed` means evidenced

A lifecycle status is a gate on a record the way a test is a gate on
code, and it lies the same way. `closed` means *resolved with evidence*:
`status_evidence` names a path#anchor, a commit, or a gate-run id that a
reader can open, the same thing an `executed` runbook entry records.
When that evidence does not exist yet, the honest states are `hotfix`
(resolved improperly, a proper fix owed) and `deferred` (parked, with
the condition that reopens it), each with an owner, so nothing rests as
"done" on a promise. A `closed` without evidence is the green lie one
level up: a gate without an assertion says the check ran and proved
nothing; a `closed` without evidence says the work finished and proves
nothing, and is trusted just as readily.

An increment whose deliverable is an operational act (a rotation, a
migration, a hardening) has two things to close, and each takes its own
evidence: the mechanism built and tested, and the act executed against
the real systems. A green tool gate closes the first and says nothing
about the second, so until the act has run, the act stays `open` (or `deferred`, with the
condition that reopens it), its record says "mechanism done, act not
executed", and its `closed` cites evidence of the act on the real
systems, never the tool gate's run. A throwaway fixture standing in for
a real destination is labelled as not satisfying the act; otherwise a
tested rotation script reads as a completed rotation.

Promotion is the same gate at the other end of a record's life. A
specification is promoted to a live status in the change that adds
passing executable assertions for its contracts; a live status over an
empty assertion set is a false green.

The vocabulary and each status's required companions live in
`docs/graph/_schema.md` §"Lifecycle status"; read them there. The enforcement is the delivered
`docs/graph/status-register.py` in its lint role: a `closed` with no
companion fails the run with ``status 'closed' requires
`status_evidence` ``, exactly as a missing gate fails `protocol.verify`.
Reviewing what is still `open` or `hotfix` at close-out is `canonize`'s.

## Adding a new gate

If verification reveals a kind of bug that no existing gate would have
caught, write the test that reproduces it (RED). A new gate is owed only
when that kind of bug recurs or its blast radius is high
(`test-first.proportionate-checks`). A new gate takes the lowest level
that catches the bug, is recorded in the verification runbook in the
same increment, and joins the project's automated runs only by owner
decision.

A gate or verification script that writes leaves either the full change
or the prior state, and it keeps **environment failures distinct from
repository failures**: it reports a missing interpreter, an absent
fixture, or a tool that could not start as its own outcome, never as a
skip, an empty success, or a clean tree. Further hardening is sized by
`test-first.proportionate-checks`. Whether a
check deserves to become a cataloged tool at all is `toolcraft`'s
doctrine.

## Neighbours

- `protocol.verify`: load when running the gates for a change.
- `protocol.verify-disagreement`: load when a check and its subject
  disagree, a change must preserve behavior, or a known defect is
  tolerated.
