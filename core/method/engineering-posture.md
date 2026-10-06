---
id: method.engineering-posture
tier: 2
kind: method
origin: seed
title: engineering posture — sources of truth, context economy, structure that earns its cost, integration
owns:
  - engineering-posture.sources-of-truth
  - engineering-posture.context-economy
  - engineering-posture.integration-over-patching
  - engineering-posture.production-boundaries
requires:
peers:
  - method.design-posture
  - method.stewardship-posture
  - method.minimum-sufficient-work
  - method.decision-economy
  - method.host-parity
  - method.bounded-execution
load_when:
  - "should I read more files first, how much context to load"
  - "how do I make this change cleanly, integrate not bolt on"
  - "which technology to pick, boring vs experimental"
  - "is this abstraction or extra worker worth its cost"
  - "sync queue starved by one item, requeue to the back, transient or permanent error"
prevents: Work with several sources of truth, context loaded in bulk, structure that does not earn its cost, and changes bolted on instead of integrated.
est_tokens: 2214
---

# Engineering posture

The general engineering principles: what is the source of truth, how
much work and context a task deserves, and how changes land in code.
Agents reference these; protocols enforce them.

## 1. Specs are the contract; code is the implementation

The artifact that survives every refactor, framework migration, and
team change is the spec. Code expresses intent; specs *are* intent. A
project's specs in `docs/graph/specs/` are read by every agent before code is
touched, and they are kept current by the same agents that touch the
code.

When spec and code disagree, one of them is wrong. The next move is to
find out which, fix that one deliberately, and bump the version of
whichever changed.

The rule reaches past the spec to every copy. Change an installed,
generated or deployed file in its source of record, and let the
project's own installer or deploy path carry it to the target in the
same sitting: an edit made only on the target is lost on the next
rebuild and is a second source of truth until then.

## 2. Tests authorize code

Production code is written only when a failing test asks for it. The
test is the most concrete possible restatement of a spec contract. The
test name names the contract; the test body exercises it; the test
failure message tells the next agent what broke and why.

The full statement (the RED → GREEN → REFACTOR → COMMIT cycle, what
"minimum" governs, the characterize-first move on untested code, and the
recorded exceptions) is owned by `docs/graph/protocols/test-first.md`.
Read it there; this posture fixes the stance: the discipline is
mandatory, and REFACTOR is where integration lands (§9).

## 3. Choose nothing until the goal forces the choice

Languages, frameworks, libraries, databases, deployment targets, and
architecture patterns are decisions, not defaults. They earn their
place by surviving an ADR against the alternative.

When nothing is yet chosen, write language-agnostic specs and tests of
behavior. When something is chosen, write it down in `docs/graph/decisions/`
so the next agent inherits the choice instead of re-litigating it.

## 4. Load the minimum context, and declare the rest

A large or multi-repo codebase does not fit in a context window, and an
agent that has read everything has no signal about what matters. Before
reading source, resolve the minimal set of knowledge-graph nodes the
task needs (the entry nodes and their required closure) and declare
both what you loaded and what you deliberately did not. Widen only when
you discover you must, and say so. The graph is the orientation;
bulk-reading a subsystem to "get oriented" is the failure this replaces.

Context is working memory, not archival storage. Before admitting
anything into it, name the unresolved decision it serves, check whether
it is already represented, and prefer the smallest representation that
preserves every decision-relevant distinction: identifiers, diffs,
line ranges, and excerpts before whole files; findings before the raw
output they came from. Keep exact wording only where fidelity is the
point: code, schemas, commands, identifiers, contract language, and
user-provided text being edited. Evict what can no longer change a
future decision: superseded plans, resolved questions, abandoned
branches, raw material already converted into findings.

In a long session, treat each new message as a delta against one
compact canonical state: objective, constraints, decisions taken,
verified facts, open questions, next operation. The transcript is history, not
working state. Reuse settled answers, user decisions, and verified
facts before re-asking, re-reading, or recomputing them; update only
the regions the delta invalidates, and re-verify only the behavior
that changed.

## 8. Structure, artifacts, and delegation earn their rent

Every abstraction, layer, agent, artifact, and instruction carries a
lifecycle cost (implementation, maintenance, coordination, latency,
comprehension, future compatibility) and is justified only by a
recurring problem whose cost exceeds that burden. Prefer a direct
function, a rule, a script, an existing component, until repeated
evidence forces the abstraction; remove structure whose ongoing burden
exceeds its value; design for the scale the evidence shows.

Delegation obeys the same economy. Spawn the minimal worker set the
tier authorizes: each additional worker contributes more than its
duplicated context, coordination, synthesis, and state transfer cost;
each receives only what its subtask needs and returns only what the
parent requires. Parallelism is for genuinely independent work: give
each worker only its own slice of context, add a critic or synthesizer
stage only for a named risk, and delegate only work larger than its own
coordination cost. Independent duplicate work is justified only where
independent verification materially reduces an important risk.

Create an intermediate artifact only when a tool requires it, it
prevents greater repeated work, it preserves state across a real
boundary, or it materially serves validation, rollback, or audit (the
growth evidence ledger is the model), and stop carrying it the moment
it can no longer affect future work. Offer alternatives only when
asked, when no option dominates, or when the trade-offs are material;
make them meaningfully distinct, eliminate the dominated ones, and
recommend one.

Instructions and prompts maximize behavioral effect per byte: one home
per rule, precedence stated once, an existing rule generalized instead
of a sibling appended, emphasis carried by structure instead of
repetition, and only rules the runtime does not already guarantee. State
the behaviour you want and its reason; a bounded role says what it ONLY
does; a prohibition is kept for a hard boundary (irreversible, security,
privacy or legal, user-sovereign, loop control) and names the right move
beside it; emphasis stays in plain case. An instruction surface whose
size obstructs the work it governs is defective: the kernel byte budget
is this rule, enforced. And use the cheapest competent method
throughout: deterministic code, rules, and templates before model calls;
the investigation class for bounded read-only work
(`method.delegation-model-classes`); fix scoping and context before
reaching for a stronger model. Weigh the future cost of output as part
of its cost: prefer results that are immediately usable, isolate
changes, and keep the next delta cheap, because local efficiency that
creates downstream burden is not efficiency.

## 9. Integrate the change into the whole file

When you change a file, your unit of work is the whole file: a change is
complete when the file reads as if the requirement had always existed,
and deleting and consolidating are first-class outcomes. Remove
duplicated *policy* and second sources of truth as you go, and keep apart
code that looks alike but changes for a different reason. Stay within
the file and the direct consequences of the request; unrelated issues
are their own increment. The method, the moves that break it, and the
append-only exception are `skill.holistic-editing`.

## 10. Build for the next maintainer, who is probably also you (or an LLM)

The next person to touch this code has less context than you do right
now. Optimize for their first ten minutes:

- A `README.md` they can read in under five minutes.
- A `docs/graph/index.md` that routes any task to its few relevant nodes.
- A `docs/graph/specs/index.md` that maps features to specs.
- A `docs/graph/plans/grill.md` that names the current phase and the next step.
- A `docs/graph/runbooks/local-development.md` with the exact commands.
- A `docs/graph/runbooks/verification.md` with the exact gates.
- A `docs/graph/libraries/` index of every non-trivial dependency.
- ADRs for every decision that wasn't obvious.

## 11. Boring on the production path, experimental at the edges

The path that handles user data, money, identity, or production traffic
uses well-understood, well-maintained, well-documented technology with
strong defaults. Experimental components live behind clear interfaces
and can be swapped out without rewriting the boring path.

## 12. Make side effects visible and testable

Every external effect (disk, network, database, model call, queue,
clock, randomness) is named at a boundary. Domain logic stays pure or
nearly so. Tests run without the boundaries by substituting fakes that
honor the same contract as the real adapter. This is dependency
inversion made concrete (`method.design-posture` §4): the boundary is
the stable contract; the adapter is the volatile detail the domain
refuses to import.

When a boundary persists state whose loss or corruption has a named
blast radius (`test-first.proportionate-checks`), write it so a crash
leaves the complete old value or the complete new one; when such state
reads back corrupt, quarantine it, recover to a safe state, and surface
the fault: report every failure and every discard, because silent loss
is the one kind nobody can trace.

A retry queue at a boundary orders work oldest-touched-first and puts a
failed item back at the end, parks an item after a bounded number of
attempts and reports it, and counts as transient only a failure that
would clear for every item (an expired session, an unreachable peer),
never one particular to the item (forbidden, not found). Random order or
an item-specific error classed transient lets one item that cannot be
served take every cycle. Classify by the innermost cause, because a
resilience library can wrap the cause in an exception of its own (a
retry that gave up, an open circuit).

## Neighbours

- `method.minimum-sufficient-work`: load when the question is how much work a task deserves, the owner's declared effort level, or how to cut increments.
- `method.decision-economy`: load when the question is whether an operation is worth running, when to stop, whether to ask or assume, or what an instruction's verb authorizes.
- `method.host-parity`: load when a result on the authoring host must stand for the target, inspection touches a shared host, or a loop is made to continue past a failure.
- `method.bounded-execution`: load when a command may hang or outlive its session, or a run must be judged running, stuck or finished.
- `method.design-posture`: load when the question is how to structure the code itself.
- `method.stewardship-posture`: load when the work is closing or knowledge must survive it.
