---
id: method.design-posture
tier: 2
kind: method
origin: seed
title: design posture — right-sized separation, responsibilities, dependency direction, real abstraction
owns:
  - design-posture.right-sized-separation
  - design-posture.responsibilities
  - design-posture.cohesion-and-coupling
  - design-posture.dependency-direction
  - design-posture.state-and-policy
  - design-posture.anti-patterns
  - design-posture.seam-variation
  - design-posture.structural-invariants
  - design-posture.converge-on-drift
requires:
peers:
  - method.engineering-posture
  - method.stewardship-posture
  - method.restrictive-policy
  - method.maintenance-contracts
  - method.design-governance
load_when:
  - "should I split this class, single responsibility"
  - "is this abstraction warranted, SOLID"
  - "which way should this dependency point, interface or direct call"
  - "cohesion and coupling, is this module too big"
  - "where does validation or error handling live, policy vs orchestration"
  - "do I need a factory, strategy, base class, extension point"
  - "port and adapter, keep the driver behind a seam"
  - "enforce an invariant with a database constraint, not an application check"
  - "idempotent converge, read compare write only on drift"
prevents: Separation chosen by habit — layers with no responsibility, dependencies pointing whichever way was convenient, and abstractions with one implementation.
est_tokens: 2511
---

# Design posture

The SOLID/responsibility cluster: how to size, separate, and connect
components so the structure fits the problem and carries only what the
problem forces.

## 1. Design for the smallest structure that fits

Separation is a tool, not a quota. Give each part one coherent
responsibility, keep cohesive things together, and point dependencies at
stable contracts; the goal is *correct* separation, and more files is
not more separation. When these principles conflict with the project's
specs, idioms, ADRs, or a framework's conventions, those win
(`method.design-governance` §14). Apply the rest of this node only where
it earns its keep.

**Applying this to a change.** Before adding structure, ask: what
responsibility is this, and who owns it? Does anything here change for a
different reason than its neighbors? Is a dependency pointing at a volatile
detail it should not know? Does this abstraction remove coupling, or only
move it? Would the smallest version (a function, a parameter, deleting a
duplication) do? If a smaller change solves the real problem, it is the
better change. This posture governs *knowledge* as much as code: one home
per fact (kernel §3.2) is the single-responsibility rule for the graph, and
a node that owns unrelated facts has the same weak cohesion a class would.

## 2. Responsibilities are reasons to change

A responsibility is a coherent obligation: a policy, a capability, an owned
piece of state, a reason the code changes. Give a component one, keep
together what changes together, and split apart what changes for different
reasons, has different owners, or has different failure or security
semantics. Judge this by what forces the code to change, not by its size: a
large cohesive module is fine; a small one mixing unrelated policies is not.
Keep a unit whole when splitting would scatter one invariant across
components, obscure the main flow, or trade visible coupling for hidden
coupling.

## 3. Cohesion and coupling are the real metrics

Weak cohesion shows up as unrelated field groups, methods that share no
state, and consumers that use disjoint slices: signals to investigate, not
automatic verdicts. For coupling, the *count* of dependencies matters less
than their **direction** and **stability**: a few hidden dependencies are
worse than many explicit ones. Keep coupling explicit, keep mutable state
owned by one component, order steps only where the order is needed, and
break every dependency cycle. Prefer a direct call to indirection that only
relocates the same coupling. Two values that are equal only by coincidence
(a name derived one way that happens to match a key derived another) are a
hidden dependency of exactly this kind: record the coincidence or make it
explicit, because a later change to either side splits them silently and
nothing announces the split.

## 4. Depend on stable contracts, not volatile detail

High-level policy and implementation detail both depend on a stable
contract at a meaningful boundary. Invert the dependency when the detail is
external, nondeterministic, or likely to have more than one implementation,
using the smallest mechanism that does it: a parameter, a function, an
interface, an adapter. This is the side-effect-boundary principle
(`method.engineering-posture` §12) seen from the design side: the named
side-effect boundary *is* the inverted dependency. Dependency injection is
not dependency inversion. A stable, local, explicit direct dependency needs
no ceremony.

## 5. Honor contracts at type boundaries

Define an interface around what a consumer actually needs, so each consumer
depends only on operations it uses and each implementor provides only
behavior it really has. A subtype must keep the whole promise of its base —
no strengthened preconditions, no weakened guarantees, no
unsupported-operation holes, no forcing callers to check its concrete type.
Use inheritance only where that substitutability genuinely holds; otherwise
compose. Keep an interface whole when its operations form one capability,
and mint a one-method interface only for a real substitution, testing, or
domain boundary.

## 6. Own state; separate deciding from sequencing

Give every piece of stateful behavior one owner that guards its invariants,
and expose behavior rather than raw mutation where that keeps the invariant
true. Keep *policy* (what is allowed, how an outcome is computed, which
invariant must hold) separate from *orchestration* (sequence, retries,
transaction scope, error translation), so infrastructure mechanics do not
entangle domain decisions. Put validation and error handling where the
decision lives: validate a rule once, next to the rule, and handle a failure
at the layer that can actually decide, with a type that says what failed
(`method.contract-posture` §5). Keep coordination and policy together when
they are one simple, cohesive act.

Where two artifacts or two representations *can* disagree, prefer removing
the possibility to shipping a check that notices the disagreement: nest one
inside the other, make the bad state unrepresentable in the type, give the
property a mechanism that is hard to omit. Discipline is not a mechanism:
a guard that depends on every author remembering to call it is a hole
waiting for the next handler, and a property that holds only because of an
incidental detail is not a guarantee until it has a cause.

## 7. Abstract only where variation is real

Design an extension point where variation already exists and recurs, not for
a future you are guessing at. Before adding a plugin seam, base class,
factory, or strategy, ask whether the variation is here yet and whether
direct modification would simply be clearer; often it is. An abstraction
earns its place by *reducing* meaningful coupling; one that mirrors a single
implementation, forwards every call unchanged, or exists only to satisfy a
principle by name adds indirection without subtracting anything. Remove such
structure when you find it: over-abstraction is a defect, exactly as
under-abstraction is (`method.engineering-posture` §8: structure earns
its rent).

**Review scan** (`design-posture.anti-patterns`). Each shape fails the
section named beside it: one class per method, one interface per class, and
more files mistaken for more separation (§1); generic managers, helpers, or
processors with no owned responsibility (§2); an event bus replacing a clear
direct call (§3); dependency injection without inversion (§4); inheritance
for code reuse alone (§5); duplicated policy across layers (§6);
pass-through layers, factories for trivial construction, and strategies for
variation that does not exist (§7).

## 9. Keep variation at a seam; keep the core free of specifics

Isolate every infrastructural dependency (database, storage, queue,
transport, an outside API) behind a port at a named internal boundary,
with at least two adapters selected by configuration: a zero-dependency
in-process one that the default test gate runs against, and the
production one. Application code imports only the port; a concrete driver
import makes the seam a fiction. Interchangeability is proven, not assumed:
a gate runs the real suite against the production backing (owned by
`protocol.verify`), and the concrete production backing for each port is
named in the decision record.

The same rule governs a reusable core against its consumers. The core
holds only consumer-neutral values: service names, hostnames, ports and
alias schemes live in each consumer's data package, so a new consumer
onboards by adding one with zero edits to shared code. When the core would need a consumer
value, take the core out of that path rather than teaching it the
value, and enforce the absence with a gate. This is §7's test applied
at the infrastructure edge: the variation is real, it recurs, and here
the abstraction removes coupling instead of relocating it.

## 10. Enforce invariants where they are structural

A structural invariant on persisted state — uniqueness, no
self-reference, cross-row consistency, no identity collision — is
enforced at the storage layer with constraints and transactions. An
application-only check is a race; a UI-only check is nothing. A state
change spanning several rows commits as one transaction, all or none,
including the derived rows a re-parse replaces. A flow that writes to
two services in sequence defines its compensating action, or it drifts
into permanent disagreement at the first partial failure. A pending
transition — a timer, a scheduled flip — is persisted and re-armed at
boot, never held only in process memory, where every restart is silent
data loss. A cleanup sweep runs against a grace window and an ownership
predicate and is safe to re-run; one that can race legitimate work is a
data-loss bug. A fleet-wide identity-collision check is evaluated once
per run, before any resource is created, not per target afterwards.

Crash-safe persistence — a crash leaves the complete old value or the
complete new one — is stated at the side-effect boundary in
`method.engineering-posture` §12; this section is what the storage
layer itself must guarantee. It is §6 made mechanical: the owner of the
state guards its invariant with something the caller cannot forget.

## 11. Converge by read, compare, write only on drift

A convergence unit — a deploy step, a configuration push, a sync, a
generator — reads the current state, compares it against exactly one
desired-state source under normalization, and writes only on
difference. That shape makes runs idempotent and dry-run-safe by
construction rather than by discipline, and lets expensive or
disruptive follow-on actions (a rebuild, a restart, an upload) fire
only on a detected change. Idempotency rests on two things the design
must fix: the identity key each item is matched by, and the freshness
of the observed state — a loop deciding every item against one
pre-loop snapshot duplicates work whenever the desired set repeats an
identity. Expose the write count so "no drift" is observable rather
than asserted, and prove idempotency by re-running with a deliberately
different input and asserting the result's fingerprint is unchanged —
the gate itself belongs to `protocol.verify`. Confine any ad-hoc
command channel to what the structured interface cannot do — bootstrap,
export, transfer — and account for its credential and trust surface
separately.

## Neighbours

- `method.engineering-posture`: how much work and structure a task
  deserves; cross when the question is whether to build at all.
- `method.stewardship-posture`: recording the design decision; cross
  when a choice here is ADR-worthy.
- `method.restrictive-policy`: load when adding a limit, filter, guard,
  or priority rule.
- `method.maintenance-contracts`: load when generated artifact,
  regenerate not hand-edit, staleness check.
- `method.design-governance`: load when task brief conflicts with the
  project spec or constraint, which outranks.
