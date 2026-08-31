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
requires:
peers:
  - method.engineering-posture
  - method.stewardship-posture
load_when:
  - "should I split this class, single responsibility"
  - "is this abstraction warranted, SOLID"
  - "which way should this dependency point, interface or direct call"
  - "cohesion and coupling, is this module too big"
  - "where does validation or error handling live, policy vs orchestration"
  - "do I need a factory, strategy, base class, extension point"
est_tokens: 1300
---

# Design posture

The SOLID/responsibility cluster: how to size, separate, and connect
components so the structure fits the problem — never more structure
than the problem forces.

## 1. Design for the smallest structure that fits

Separation is a tool, not a quota. Give each part one coherent
responsibility, keep cohesive things together, and point dependencies at
stable contracts — but the goal is *correct* separation, never *maximum*.
A design is not better for holding more classes, interfaces, layers, or
files; more files is not more separation. When these principles conflict
with the project's specs, idioms, ADRs, or a framework's conventions, those
win. Apply the rest of this node where it earns its keep and nowhere it
does not.

## 2. Responsibilities are reasons to change

A responsibility is a coherent obligation — a policy, a capability, an owned
piece of state, a reason the code changes. Give a component one, keep
together what changes together, and split apart what changes for different
reasons, has different owners, or has different failure or security
semantics. Judge this by what forces the code to change, not by its size: a
large cohesive module is fine; a small one mixing unrelated policies is not.
Do not split when splitting would scatter one invariant across components,
obscure the main flow, or trade visible coupling for hidden coupling.

## 3. Cohesion and coupling are the real metrics

Weak cohesion shows up as unrelated field groups, methods that share no
state, and consumers that use disjoint slices — signals to investigate, not
automatic verdicts. For coupling, the *count* of dependencies matters less
than their **direction** and **stability**: a few hidden dependencies are
worse than many explicit ones. Keep coupling explicit, avoid shared mutable
state and needless temporal ordering, and never let a dependency cycle
stand. Prefer a direct call to indirection that only relocates the same
coupling.

## 4. Depend on stable contracts, not volatile detail

High-level policy does not depend on volatile implementation detail; both
depend on a stable contract at a meaningful boundary. Invert the dependency
when the detail is external, nondeterministic, or likely to have more than
one implementation — using the smallest mechanism that does it: a
parameter, a function, an interface, an adapter. This is the
side-effect-boundary principle (see `method.engineering-posture`) seen
from the design side — the named side-effect boundary *is* the inverted
dependency. Passing a collaborator through a constructor is not
inversion; dependency injection is not dependency inversion. A stable,
local, explicit direct dependency needs no ceremony.

## 5. Honor contracts at type boundaries

Define an interface around what a consumer actually needs: no consumer
should depend on operations it does not use, and no implementor should have
to fake behavior it cannot provide. A subtype must keep the whole promise of
its base — no strengthened preconditions, no weakened guarantees, no
unsupported-operation holes, no forcing callers to check its concrete type.
Use inheritance only where that substitutability genuinely holds; otherwise
compose. Do not split an interface whose operations form one capability, and
do not mint one-method interfaces without a real substitution, testing, or
domain boundary behind them.

## 6. Own state; separate deciding from sequencing

Give every piece of stateful behavior one owner that guards its invariants,
and expose behavior rather than raw mutation where that keeps the invariant
true. Keep *policy* — what is allowed, how an outcome is computed, which
invariant must hold — separate from *orchestration* — sequence, retries,
transaction scope, error translation — so infrastructure mechanics do not
entangle domain decisions. Put validation and error handling where the
decision lives: validate a rule next to the rule, handle a failure at the
layer that can actually decide, and neither dilute one rule across every
layer nor funnel every error into one generic type. Do not split
coordination from policy when they are one simple, cohesive act.

## 7. Abstract only where variation is real

Design an extension point where variation already exists and recurs, not for
a future you are guessing at. Before adding a plugin seam, base class,
factory, or strategy, ask whether the variation is here yet and whether
direct modification would simply be clearer — often it is. An abstraction
earns its place by *reducing* meaningful coupling; one that mirrors a single
implementation, forwards every call unchanged, or exists only to satisfy a
principle by name adds indirection without subtracting anything. Remove such
structure when you find it — over-abstraction is a defect, exactly as
under-abstraction is (see `method.engineering-posture`: structure earns
its rent).

**Applying this to a change.** Before adding structure, ask: what
responsibility is this, and who owns it? Does anything here change for a
different reason than its neighbors? Is a dependency pointing at a volatile
detail it should not know? Does this abstraction remove coupling, or only
move it? Would the smallest version — a function, a parameter, deleting a
duplication — do? If a smaller change solves the real problem, it is the
better change. This posture governs *knowledge* as much as code: one home
per fact (kernel §3.2) is the single-responsibility rule for the graph, and
a node that owns unrelated facts has the same weak cohesion a class would.

**Anti-patterns.** One class per method; one interface per class;
pass-through layers; dependency injection without inversion; generic
managers, helpers, or processors with no owned responsibility; factories for
trivial construction; strategies for variation that does not exist;
inheritance for code reuse alone; an event bus replacing a clear direct
call; duplicated policy across layers; more files mistaken for more
separation.

## Neighbours

- `method.engineering-posture` — how much work and structure a task
  deserves — cross when the question is whether to build at all.
- `method.stewardship-posture` — recording the design decision — cross
  when a choice here is ADR-worthy.
