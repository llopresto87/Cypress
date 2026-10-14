---
name: managed-edge-read-only-triage
description: Triage a slow or misbehaving shared uplink on an API-managed edge router using only read-only observation, in a fixed order that ends in a real line-rate test, and separate a local-data problem from upstream filtering by comparing answers per resolver. Invoke when "the line is slow / someone is hogging the internet" on a managed edge, or when a name resolves wrongly through the router.
id: skill.managed-edge-read-only-triage
tier: 2
kind: skill
title: managed-edge-read-only-triage, ordered read-only diagnosis of a shared uplink on an API-managed edge router
owns:
  - managed-edge-read-only-triage.saturation-order
  - managed-edge-read-only-triage.line-rate-test
  - managed-edge-read-only-triage.resolver-comparison
requires:
load_when:
  - "the internet is slow, someone is saturating the shared line, who is hogging the uplink"
  - "a hostname resolves to the wrong answer through the router, wrong DNS answer on the LAN"
  - "diagnose a managed edge router without changing anything"
stack:
  - library-corpus/galaxy/community.routeros
prevents: A slow shared uplink or a wrong DNS answer is met with configuration changes on the edge router before a read-only diagnosis has named the cause, so the change can make it worse.
est_tokens: 1256
---

# Suggested skill: managed-edge-read-only-triage

> Optional procedure, keyed to the router OS the collection above manages: when
> a shared uplink is slow or a name resolves wrongly, diagnose with read-only
> observation only, in a fixed order, before changing anything. Composes
> `core/method/incident-posture.md` (the hypothesis ledger each step adds to or
> rules out) by reference. The configuration changes a diagnosis motivates are
> out of scope here; they go through `skill-corpus/add-infrastructure-object-safely.md`.

## When to apply

- A shared uplink is slow and the question is whether the line is saturated,
  by whom, and whether the shaper that should be managing it is engaging.
- A hostname resolves to an unexpected answer through the router (a block page,
  a stale record, a `SERVFAIL`) and the question is whether the cause is local
  or upstream.

Every step below reads state; none changes it. A read-only pass is the whole
procedure: it ends by naming the cause, and the change is a separate, gated
move.

## Saturation triage, in order, ending in a line-rate test

Run these in order; each narrows the next, and the record carries each answer
as a hypothesis confirmed or ruled out:

1. **Is the uplink actually busy?** Read the WAN interface's current rate. If it
   is nowhere near the line's capacity, the slowness is not saturation and the
   rest of this list does not apply.
2. **Who is sending?** Read the connection tracking sorted by bytes per upstream
   peer. One connection carrying most of the traffic is the usual answer.
3. **Which device and port?** Map the busy address back through the lease table
   to a MAC and through the bridge host table to a physical port, so the
   talker is a device, not just an address.
4. **What are its live flows?** Read the active flows on that port to see what
   the device is doing, not only that it is busy.
5. **Is the shaper engaging?** Read the queue counters and drops. A shaper with
   zero drops under saturation is not engaging (see the trap below).
6. **What is the real line rate?** Run an actual rate test from a client. This
   is the step that distinguishes a saturated line from a slow one, and it is
   why the procedure ends here rather than at the queue counters.

**Zero drops plus a measured rate below the shaper's ceiling is the signature
of a shaper set above what the line delivers** (step 5 paired with step 6). Why
it never engages, and the fix, are invariant 1 of
`skill-corpus/galaxy/shared-line-qos-design.md`; this pass only names it.

## Resolver comparison, to separate local data from upstream filtering

When a name resolves wrongly, do not guess whether the cause is a local static
record, a cache, or the upstream resolver filtering it. Resolve the name against
each upstream resolver separately and compare the answers:

- Answers that agree across upstreams, but differ from what the router hands
  clients, point at **local** data: a static entry, a cache, or a local zone.
- An answer that differs **per upstream** points at upstream-side filtering (a
  block page, a `SERVFAIL`, a provider-rewritten record), which is not something
  a local change fixes.

A static override records one name only; it does not cure an upstream that
rewrites a whole zone, and the durable remedy (a different upstream, a local
resolver) is the owner's call recorded in the ledger.

## Reference files

- `core/method/incident-posture.md` (the hypothesis ledger each step confirms
  or rules out)
- `skill-corpus/galaxy/shared-line-qos-design.md` (the design question a
  non-engaging shaper raises)
- `skill-corpus/add-infrastructure-object-safely.md` (the gated path for any
  change a diagnosis motivates)
