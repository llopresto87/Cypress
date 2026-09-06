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
  - design-posture.restrictive-policy
  - design-posture.anti-patterns
  - design-posture.seam-variation
  - design-posture.structural-invariants
  - design-posture.converge-on-drift
  - design-posture.generated-artifacts
  - design-posture.doc-code-precedence
  - design-posture.project-contract-outranks
  - design-posture.maintained-primitives
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
  - "adding a limit, filter, guard, or priority rule"
  - "do I need a factory, strategy, base class, extension point"
  - "port and adapter, keep the driver behind a seam"
  - "enforce an invariant with a database constraint, not an application check"
  - "idempotent converge, read compare write only on drift"
  - "generated artifact, regenerate not hand-edit, staleness check"
  - "documentation drift versus the implementation, precedence rule, which one wins"
  - "task brief conflicts with the project spec or constraint, which outranks"
  - "roll your own crypto or session primitive, maintained library"
  - "degraded dependency, silent fallback to a default, fail-open or fail-closed posture"
  - "destructive or stranding operation, describe-only default, explicit apply flag"
est_tokens: 4400
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
win (§14). Apply the rest of this node where it earns its keep and nowhere
it does not.

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

Where two artifacts or two representations *can* disagree, prefer removing
the possibility to shipping a check that notices the disagreement: nest one
inside the other, make the bad state unrepresentable in the type, give the
property a mechanism that is hard to omit. Discipline is not a mechanism —
a guard that depends on every author remembering to call it is a hole
waiting for the next handler, and a property that holds only because of an
incidental detail is not a guarantee until it has a cause.

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
whoever it breaks.

**A silent fallback is a fail-open.** Every degraded or optional path
has a decided posture — fail-open or fail-closed, chosen and written
down, never inherited from a library default — and emits a signal when
it degrades, even while nothing has visibly broken, because the damage
is invisible by construction. A degraded path is never a *less-filtered*
path: when the guarded component is unavailable, fail visibly rather
than falling back to something that skips the guard, and a protective
transform that errors internally drops or masks the value rather than
passing it through. (`method.engineering-posture` §5 holds the
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
proposes the destructive one and stops before executing. The explicit
human authorization naming the resource is the kernel's §4; this is its
design consequence — a tool built so that the human *can* stop it.
Whether the target is a real production system is a plant fact, read
from `plant.environment_class` in the router's frontmatter, never
re-guessed per run.

**Anti-patterns.** A default-deny rule with no audited allow set; a
priority that starves what it deprioritized; a scan or check that
blocks a path it was explicitly configured not to block; a limit tuned
against the peak case and never measured against the median; "it works
for the case I tested" as the acceptance evidence for a rule that
applies to everything; a fallback nobody decided; a `--force` that
means everything at once; an allowlist widened to fix a fault it was
not causing.

## 9. Keep variation at a seam; keep the core free of specifics

Isolate every infrastructural dependency — database, storage, queue,
transport, an outside API — behind a port at a named internal boundary,
with at least two adapters selected by configuration: a zero-dependency
in-process one that the default test gate runs against, and the
production one. Application code never imports a concrete driver; if it
does, the seam is a fiction. Interchangeability is proven, not assumed:
a gate runs the real suite against the production backing (owned by
`protocol.verify`), and the concrete production backing for each port is
named in the decision record.

The same rule governs a reusable core against its consumers. The core
carries no consumer-specific literal — no service name, hostname, port,
or alias scheme — and a new consumer onboards by adding a data package
with zero edits to shared code. When the core would need a consumer
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

## 12. A generated artifact carries its marker, its recipe, and its staleness gate

Calling an artifact *generated* obliges four things together, or the
word means nothing: an in-file marker, human- and machine-visible, at
the top, in whatever syntax the format allows (a first key where the
format has no comments), naming the command that regenerates it and
forbidding hand edits; deterministic, byte-reproducible regeneration; a
ban on hand edits — the artifact is rebuild output, not source, so an
upgrade regenerates it and counts none of it toward its change budget;
and a staleness gate that fails when the artifact no longer matches its
source. Record the input provenance — which revision of every input the
artifact was derived from — because a green regeneration proves nothing
without it. A committed, script-generated, hand-editable file with
nothing to catch the drift is a live defect, not a stylistic gap. Where
two tools need the same content, author it once and generate the second
view; the graft protocol's treatment of harness projections regenerated
from their graph node is this rule applied to the seed's own machinery
(`protocol.graft`).

## 13. Doc-versus-code drift is a defect with a stated precedence rule

Two artifacts that describe the same thing will disagree eventually; the
design decision is who loses. State the precedence once: **code decides
facts about itself** — what a module does, which command works, which
keys are read — and **the recorded contract decides contracts** — what
the code was required to do. A violation of a recorded contract is a bug
in the code, not a documentation update (`method.engineering-posture`
§1: when spec and code disagree, find out which is wrong and fix that one
deliberately; the kernel §4 forbids silently changing the spec to fit).
A roll-up index that disagrees with the artifact it summarizes loses,
the index is corrected, and the record names which copy drifted. A stale
operational document is worse than none, because it is trusted at the
moment it is used: every command in a runbook is expected to work, and a
change that stales it fixes it in the same increment — or marks it stale
where it can no longer be kept current. A citation to a decision record
that does not exist is a finding, sharpest where it authorized weakening
a control; label it inline-only provenance rather than following it as if
a review had happened. A mechanism that grew enforcement points and
dependents without a contract is contracted retroactively — a spec with
`status: back-written`, labelled as such — never left to accrete below
the documentation line.

## 14. The project's own contract outranks the brief, the expert, and the industry default

When a task brief, a general design principle (this node's included), an
outside expert's recommendation, or an industry-standard convention
conflicts with the project's signed specification or a recorded
constraint, the project's contract wins. Do the smaller thing that honors
the contract and escalate the conflict — a deliberate spec change,
re-signed — rather than resolving it by widening scope on your own
authority, which destroys the acceptance evidence the spec produced.
Record the rejection *by constraint*, not on merit, so a later reader
does not reopen it as a technical dispute. An industry default is not
automatically right: where the project has measured that the standard
shape re-opens a channel a hardening change closed, it is refused. A
chosen library's default that violates a committed constraint is
overridden *inside* the recorded decision — naming the library is not
enough. Duplication is not by itself authority to centralize an
owner-maintained literal; that refactor is requested or it does not
happen. And an implementer's off-spec invention is read as a spec
defect: the spec left the value unstated, so specify it and pin it with
a test. The goal-precedence order (safety, then explicit requirements and
binding contracts, then correctness…) is stated once in
`method.engineering-posture` §5; this section says what it means when
the *brief itself* is what conflicts. A standing, deliberate departure
from a standard is a `deviation` node with its `ends_when`, so a lapse is
never mistaken for a decision nor a decision re-litigated as a lapse.

## 15. Adopt maintained primitives for security-critical machinery

Never implement cryptographic, session, or trust-anchor primitives
yourself. Adopt a maintained component and treat rolling your own as a
declined risk, not a capability. Choose a trust anchor the environment
can actually validate: where a namespace is unreachable from a public
issuer, own the root and own a distribution path for every platform
family you manage — an anchor nobody can verify is decoration. Close a
vulnerability by replacing the vulnerable component with a maintained
equivalent that keeps the capability; removing the user-visible feature
is a regression disguised as a fix. Where the system lives on a few
hand-tuned queries or a few readable outputs, prefer the component whose
output you can read and control over the one with the nicer developer
experience. Where data sovereignty or cost predictability outranks
time-to-market, self-hostable open components are a priced trade: the
operational surface is the price, accepted in the decision record rather
than discovered later. `method.engineering-posture` §11 owns the general
boring-on-the-production-path rule; this is its sharpest instance — on
the path that handles identity, money, user data, or production traffic,
novel is a synonym for untested, and the maintained library is the boring
choice. Handling the secrets themselves — channel, recording, compromise,
lifetime — is `method.secrets-posture`.

## Neighbours

- `method.engineering-posture` — how much work and structure a task
  deserves — cross when the question is whether to build at all.
- `method.stewardship-posture` — recording the design decision — cross
  when a choice here is ADR-worthy.
- `method.secrets-posture` — secret channel, recording, compromise,
  lifetime — cross when §15's machinery handles a credential.
