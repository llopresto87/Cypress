---
name: shared-line-qos-design
description: Design a queue tree that actually prioritizes traffic on a shared internet uplink, stated as invariants each of which names what breaks silently when violated (shape below the measured rate, one root per shared pool, borrowing classes, fast path off for shaped traffic, a marking rule behind every queue, a classifier on the address the queue sees). Invoke when building or fixing QoS on an API-managed edge router, or when a configured shaper is not engaging.
id: skill.shared-line-qos-design
tier: 2
kind: skill
title: shared-line-qos-design, the queue-tree invariants that make a shared-uplink shaper engage
owns:
  - shared-line-qos-design.invariants
requires:
load_when:
  - "set up QoS on a shared internet uplink, build a queue tree, prioritize traffic on the edge router"
  - "the shaper is configured but not engaging, QoS has no effect, queues show no drops under load"
stack:
  - library-corpus/galaxy/community.routeros
prevents: A queue tree is built that raises no error and prioritizes nothing, because one silently violated invariant keeps the shaper from engaging while every counter looks plausible.
est_tokens: 2040
---

# Suggested skill: shared-line-qos-design

> Optional procedure, keyed to the router OS the collection above manages:
> the design invariants of a queue tree that shapes a shared internet uplink.
> The tree is a hierarchical token bucket (HTB), so the general invariants are
> HTB's own, and the platform-specific ones come from the router OS's
> documentation; each is cited under Sources. The ordered read-only diagnosis
> that shows a shaper is not engaging is
> `skill-corpus/galaxy/managed-edge-read-only-triage.md`, and a change is made
> through `skill-corpus/add-infrastructure-object-safely.md`. Each invariant
> names what breaks **silently** when it is violated, because a mis-built queue
> tree raises no error: it fails to prioritize while every counter looks
> plausible.

## When to apply

- A shared internet uplink needs real prioritization (a saturating upload must
  not starve interactive traffic) and a queue tree is being built or revised.
- Diagnosis showed a configured shaper is not engaging (no queued or dropped
  packets under load, a measured rate below the shaper's ceiling) and the cause
  is the design, not the device.

## The invariants

1. **Shape slightly below the measured line rate.** Measure what the line
   delivers, not what the plan advertises, and set the shaper slightly below
   it; the CAKE shaper's own automatic mode does the same, setting itself
   slightly below the rate it estimates. The margin is tuned, not derived:
   grade each setting by latency under load (see "Validate the design" below).
   *Silently breaks:* a shaper set at or above what the line
   delivers is never the bottleneck, so the excess queues in a buffer upstream
   of the router (the latency under load called bufferbloat), the router's own
   queue stays empty, and nothing it prioritizes takes effect.

2. **One root class per shared capacity pool.** In HTB, classes under one root
   borrow each other's spare bandwidth, but one root class cannot borrow from
   another. Links that draw on one upstream pool therefore hang under one root.
   *Silently breaks:* with two roots, spare capacity under one is unavailable to
   the other, and two shapers each set to the pool's full rate together admit
   up to twice what the pool carries, so neither ever becomes the bottleneck.

3. **Let classes borrow.** An HTB class's `rate` is what it is guaranteed; its
   `ceil` is the most it may send when the parent has bandwidth to spare, and
   it defaults to `rate`, which means no borrowing. Give each leaf a `ceil`
   equal to its parent's, and keep a parent's `rate` equal to the sum of its
   children's rates (the HTB user guide's rule). On this router OS the
   guaranteed rate is `limit-at` and the maximum is `max-limit`. *Silently
   breaks:* a leaf left at the default `ceil` cannot use bandwidth the other
   classes leave idle, so the line runs under its rate while that class waits.

4. **Keep the fast path off for traffic the shaper governs.** On this router
   OS, packets of a FastTrack-marked connection bypass the firewall, connection
   tracking, simple queues and the queue tree with `parent=global`; the
   documentation leaves it to the administrator to keep FastTrack from
   interfering with such configuration. Tunnel interfaces with fast path
   allowed bypass the same queue tree for their encapsulated traffic. Exclude
   shaped traffic from the FastTrack rule (an accepting rule placed before it),
   or do not fast-track at all. *Silently breaks:* the usual FastTrack rule
   matches established and related connections, so the packets that open a
   connection take the normal path and are shaped, and the bulk of the
   connection then skips the tree; the documentation also notes that some
   packets of fast-tracked connections still take the slow path, so the queue
   shows a little traffic and looks alive.

5. **Put a marking rule behind every queue.** A queue-tree queue selects
   traffic by the packet mark a mangle rule set earlier in the packet flow.
   *Silently breaks:* a queue whose mark no rule sets stays empty, and traffic
   marked with a name no queue selects is not governed by that queue. Neither
   raises an error, so check each queue's counters under load.

6. **Classify per host on an address the queue actually sees.** Read where
   the queue sits in the platform's packet flow relative to address
   translation before choosing a per-host classifier: this router OS's
   packet-flow documentation runs the postrouting mangle chain, then source
   NAT, then the global queue tree. *Silently breaks:* a per-host classifier
   keyed on an address that translation has already replaced sees every host
   behind one public address as a single host. Confirm what the classifier
   keys on from the queue's live sub-queues, not from the design.

## Validate the design, do not trust the config

A queue tree that violates any invariant above still loads without error. Grade
it by latency: measure from a client with the line idle and again under a
saturating upload and download, before and after the change (bufferbloat.net
treats latency below 15 to 25 ms in such a test as bufferbloat under control), while
`skill-corpus/galaxy/managed-edge-read-only-triage.md` reads the queue counters.
Paths not yet tested under load (a second WAN, a tunnel, router-originated
traffic) are recorded as unverified, not assumed.

## Sources

- `tc-htb(8)`, Linux manual page: `rate` (guaranteed), `ceil` (maximum when
  the parent has spare bandwidth; defaults to `rate`, which implies no
  borrowing). https://man7.org/linux/man-pages/man8/tc-htb.8.html
- Martin Devera, *HTB Linux queuing discipline manual: user guide*: borrowing
  inside one root, no borrowing between roots, a parent's rate should be the
  sum of its children's rates. http://luxik.cdi.cz/~devik/qos/htb/manual/userg.htm
- `tc-cake(8)`, Linux manual page: `autorate-ingress` sets the shaper to a
  bandwidth slightly below the estimated rate.
  https://man7.org/linux/man-pages/man8/tc-cake.8.html
- Bufferbloat.net, *What can I do about Bufferbloat?*: measure latency idle and
  under upload or download traffic; under 15 to 25 ms means bufferbloat is under
  control. https://www.bufferbloat.net/projects/bloat/wiki/What_can_I_do_about_Bufferbloat/
- RouterOS documentation, *Packet Flow in RouterOS*: the postrouting order
  (mangle, source NAT, queue tree `parent=global`), FastTrack's bypass list,
  the established/related FastTrack rule, slow-path packets of fast-tracked
  connections, tunnel fast path.
- RouterOS documentation, *Queues*: FastTrack bypasses simple queues; queue-tree
  queues select traffic by packet marks set in mangle.

## Reference files

- `skill-corpus/galaxy/managed-edge-read-only-triage.md` (the read-only
  diagnosis that shows a non-engaging shaper, and the line-rate test that
  grades this design)
- `skill-corpus/add-infrastructure-object-safely.md` (the gated path for making
  the change)
