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
est_tokens: 1401
---

## 8. A rule that restricts must not deny the default

Filters, limits, guards, quotas, priorities, and security rules are
written from the perspective of the case that motivated them, and they
are evaluated by every case that did not. The failure is systematic:
the rule serves its target path exactly as designed while the ordinary
path it never considered degrades or stops.

So a restrictive rule is designed against two sets, not one: what it
must catch, and **what must keep working**. Before it ships, enumerate
the traffic, callers, or inputs it will now deny, and check the common
ones — not only the one it was written for. Where the rule is
positional (an ordered chain, a first-match table, a priority queue),
the enumeration includes what its *placement* displaces.

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
has a decided posture — fail-open or fail-closed, chosen and written
down, never inherited from a library default — and emits a signal when
it degrades, even while nothing has visibly broken, because the damage
is invisible by construction. A degraded path is never a *less-filtered*
path: when the guarded component is unavailable, fail visibly rather
than falling back to something that skips the guard, and a protective
transform that errors internally drops or masks the value rather than
passing it through. (`method.minimum-sufficient-work` §5 holds the
corollary for optional side effects: they degrade to a logged warning
and never fail the required path.)

**Never weaken a control to clear a symptom.** Widening an allowlist,
granting the privilege, lengthening a lifetime, or disabling the
dependent control makes the error disappear and the protection with it.
Diagnose first — prove from evidence that the control is causing the
fault before touching it — and fix the controllable cause instead: the
transport, the file ownership, the missing configuration. Repair a
fail-open primary control before layering a compensating one over it; a
compensating control on top of a broken primary can protect less than
nothing. Removing the *need* for a control is not licence to delete it,
and a guard made redundant by an earlier one stays as defence in depth.
Where the weakening has been tried once already, pin the temptation with
a contract test.

**Stranding or destructive operations default to report-only.** A tool
that can delete state, strand its operator, or regenerate a set that
others trust runs by default in describe-only mode and mutates only when
an explicit per-operation flag is flipped — never a global force.
Classify destructive versus additive reconciliation per resource class,
in writing; do not infer one resource's deletion behaviour from
another's. Partial state halts rather than converges — half of a trust
anchor is an error, not a trigger to regenerate the pair. The reversible
path (stop, configuration rollback) and the destructive path (reset,
data restore) are separate operations behind separate gates, each
stating what it preserves and what it drops; automation prepares and
proposes the destructive one and stops before executing. A scoped
operation run inside a shared namespace has the namespace's reach: an
orphan cleanup under a shared project name removes whatever the scope
did not list. So the destructive flag on such an operation is honored
only when the declared scope covers the whole namespace. Otherwise it
is refused before the first destructive command, and the refusal names
what the scope does not cover. The cost is accepted in the open: a
genuine orphan then accumulates, and each run reports it and removes
nothing, so clearing it stays a deliberate full-scope decision, never a
silent side effect of a narrower run. The explicit human authorization naming the resource is the kernel's §4; this is its
design consequence — a tool built so that the human *can* stop it.
Whether the target is a real production system is a plant fact, read
from `plant.environment_class` in the router's frontmatter, never
re-guessed per run.

**An inert item announces itself.** An accepted-but-inert setting,
parameter or code path announces itself where it is accepted, or is
documented as dead; an inert item is indistinguishable from a working
one otherwise.

**Anti-patterns.** A default-deny rule with no audited allow set; a
priority that starves what it deprioritized; a scan or check that
blocks a path it was explicitly configured not to block; a limit tuned
against the peak case and never measured against the median; "it works
for the case I tested" as the acceptance evidence for a rule that
applies to everything; a fallback nobody decided; a `--force` that
means everything at once; an allowlist widened to fix a fault it was
not causing; a dependency added to make a symptom go away, when the
defect is that the component needs it at all.

## Neighbours

- `method.design-posture`: load when should I split this class, single
  responsibility.
