---
id: method.restrictive-policy
tier: 2
kind: method
origin: seed
title: restrictive policy — a rule that restricts must not deny the default; decided fallbacks, report-only destructive operations
owns:
  - design-posture.restrictive-policy
requires:
peers:
  - method.design-posture
load_when:
  - "adding a limit, filter, guard, or priority rule"
  - "degraded dependency, silent fallback to a default, fail-open or fail-closed posture"
  - "destructive or stranding operation, describe-only default, explicit apply flag"
  - "scoped cleanup or remove-orphans inside a shared namespace or project name"
prevents: A guard that serves the case it was written for and silently denies the ordinary path, a fallback nobody decided, and a destructive tool that acts without a per-operation flag.
est_tokens: 1297
---

## 8. A restrictive rule keeps the default path working

Filters, limits, guards, quotas, priorities, and security rules are
written from the perspective of the case that motivated them, and they
are evaluated by every case that did not. The failure is systematic:
the rule serves its target path exactly as designed while the ordinary
path it never considered degrades or stops.

So a restrictive rule is designed against two sets, not one: what it
must catch, and **what must keep working**. Before it ships, enumerate
the traffic, callers, or inputs it will now deny, and check the common
ones, not only the one it was written for: a default-deny rule has an
audited allow set, a limit is measured against the median case as well
as the peak, and a scan or check still passes every path it is
configured to allow. Where the rule is positional (an ordered chain, a
first-match table, a priority queue), the enumeration includes what its
*placement* displaces, such as the work a priority starves.

State the invariant the rule may not violate, in the same change that
introduces the rule. A guard whose baseline is written down can be
tested (see `protocol.verify`: a gate asserts something or it is not a
gate); one that lives only in the author's head is rediscovered by
whoever it breaks. An invariant can also be supplied by an absence
rather than by a rule, and the same change records that too: a safety
property holding only because some capability does not exist yet is
conditional, not structural, so name the property, the absence that
currently supplies it, and the change that would end it. Closing the gap
then closes both halves at once, instead of reintroducing the risk the
absence had been absorbing unnoticed.

**A silent fallback is a fail-open.** Every degraded or optional path
has a decided posture (fail-open or fail-closed, chosen and written
down, because a library default is a decision nobody made) and emits a
signal when it degrades, even while nothing has visibly broken, because
the damage is invisible by construction. A degraded path keeps every
guard: when the guarded component is unavailable, fail visibly rather
than falling back to something that skips the guard, and a protective
transform that errors internally drops or masks the value rather than
passing it through. (Optional side effects: `method.minimum-sufficient-work`
§5.)

**Clear a symptom by fixing its cause, never by weakening a control.**
Widening an allowlist, granting the privilege, lengthening a lifetime,
disabling the dependent control, or adding a dependency so the error
goes away removes the protection with it, or hides the defect that the
component needs it at all. Diagnose first (prove from evidence that the
control is causing the fault before touching it) and fix the
controllable cause instead: the transport, the file ownership, the
missing configuration. Repair a fail-open primary control before
layering a compensating one over it; a compensating control on top of a
broken primary can protect less than nothing. Deleting a control is its
own decision, even once its need is gone, and a guard made redundant by
an earlier one stays as defence in depth. Where the weakening has been
tried once already, pin the temptation with a contract test.

**Stranding or destructive operations default to report-only.** A tool
that can delete state, strand its operator, or regenerate a set that
others trust runs by default in describe-only mode and mutates only when
an explicit per-operation flag is flipped — never a global force.
Classify destructive versus additive reconciliation per resource class,
in writing, because deletion behaviour differs from class to class.
Partial state halts rather than converges: half of a trust anchor is an
error, not a trigger to regenerate the pair. The reversible path (stop,
configuration rollback) and the destructive path (reset, data restore)
are separate operations behind separate gates, each stating what it
preserves and what it drops; automation prepares and proposes the
destructive one and stops before executing. A scoped operation run
inside a shared namespace has the namespace's reach: an orphan cleanup
under a shared project name removes whatever the scope did not list. So
the destructive flag on such an operation is honored only when the
declared scope covers the whole namespace. Otherwise it is refused
before the first destructive command, and the refusal names what the
scope does not cover. The cost is accepted in the open: a genuine
orphan then accumulates, and each run reports it and removes nothing,
so clearing it stays a deliberate full-scope decision, never a silent
side effect of a narrower run. The explicit human authorization naming
the resource is the kernel's §4; this is its design consequence: a tool
built so that the human *can* stop it. Whether the target is a real
production system is `method.host-parity`'s plant fact.

**An inert item announces itself.** An accepted-but-inert setting,
parameter or code path announces itself where it is accepted, or is
documented as dead; an inert item is indistinguishable from a working
one otherwise.

## Neighbours

- `method.design-posture`: load when should I split this class, single
  responsibility.
