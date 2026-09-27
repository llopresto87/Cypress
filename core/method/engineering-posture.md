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
prevents: Work with several sources of truth, context loaded in bulk, structure that does not earn its cost, and changes bolted on instead of integrated.
est_tokens: 2254
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

The rule reaches past the spec to every copy. An installed, generated
or deployed file is never edited in place: the change is made in the
source of record and reaches the target only through the project's own
installer or deploy path, in the same sitting. An edit made only on the
target is lost on the next rebuild and is a second source of truth
until then.

## 2. Tests authorize code

Production code does not exist until a failing test asks for it. The
test is the most concrete possible restatement of a spec contract. The
test name names the contract; the test body exercises it; the test
failure message tells the next agent what broke and why.

The full statement — the RED → GREEN → REFACTOR → COMMIT cycle, what
"minimum" governs, the characterize-first move on untested code, and the
recorded exceptions — is owned by `docs/graph/protocols/test-first.md`.
Read it there; this posture only fixes the stance: the discipline is not
optional, and REFACTOR is where integration lands (see §9).

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
task needs — the entry nodes and their required closure — and declare
both what you loaded and what you deliberately did not. Widen only when
you discover you must, and say so. The graph is the orientation;
bulk-reading a subsystem to "get oriented" is the failure this replaces.

Context is working memory, not archival storage. Before admitting
anything into it, name the unresolved decision it serves, check whether
it is already represented, and prefer the smallest representation that
preserves every decision-relevant distinction — identifiers, diffs,
line ranges, and excerpts before whole files; findings before the raw
output they came from. Keep exact wording only where fidelity is the
point: code, schemas, commands, identifiers, contract language, and
user-provided text being edited. Evict what can no longer change a
future decision — superseded plans, resolved questions, abandoned
branches, raw material already converted into findings.

In a long session, treat each new message as a delta against one
compact canonical state — objective, constraints, decisions taken,
verified facts, open questions, next operation — never as a reason to
re-derive the whole conversation. The transcript is history, not
working state. Reuse settled answers, user decisions, and verified
facts before re-asking, re-reading, or recomputing them; update only
the regions the delta invalidates, and re-verify only the behavior
that changed.

## 8. Structure, artifacts, and delegation earn their rent

Every abstraction, layer, agent, artifact, and instruction carries a
lifecycle cost — implementation, maintenance, coordination, latency,
comprehension, future compatibility — and is justified only by a
recurring problem whose cost exceeds that burden. Prefer a direct
function, a rule, a script, an existing component, until repeated
evidence forces the abstraction; remove structure whose ongoing burden
exceeds its value; never design for hypothetical scale.

Delegation obeys the same economy. Spawn the minimal worker set the
tier authorizes: each additional worker must contribute more than its
duplicated context, coordination, synthesis, and state transfer cost;
each receives only what its subtask needs and returns only what the
parent requires. Parallelism is for genuinely independent work — no
broadcasting the same full context to several workers, no default
critic or synthesizer stage, no delegation smaller than its own
coordination cost. Independent duplicate work is justified only where
independent verification materially reduces an important risk.

Create an intermediate artifact only when a tool requires it, it
prevents greater repeated work, it preserves state across a real
boundary, or it materially serves validation, rollback, or audit — the
growth evidence ledger is the model — and stop carrying it the moment
it can no longer affect future work. Offer alternatives only when
asked, when no option dominates, or when the trade-offs are material;
make them meaningfully distinct, eliminate the dominated ones, and
recommend one.

Instructions and prompts maximize behavioral effect per byte: one home
per rule, precedence stated once, generalize an existing rule instead of
appending a sibling, no repetition for emphasis, no rule the runtime
already guarantees. An instruction surface whose size obstructs the work
it governs is defective — the kernel byte budget is this rule, enforced.
And use the cheapest competent method throughout: deterministic code,
rules, and templates before model calls; the smaller model class for
bounded read-only work (`method.delegation-model-classes`); a stronger
model never compensates for poor scoping or unnecessary context. Weigh
the future cost of output as part of its cost: prefer results that are
immediately usable, isolate changes, and keep the next delta cheap —
local efficiency that creates downstream burden is not efficiency.

## 9. Integrate; do not patch

When you change a file, your unit of work is the whole file, not the
region near your edit. A change is complete only when the file reads as
if the requirement had always existed — no appended functions, no `_v2`
wrappers, no `if` special-casing the new case while the general logic
that should have changed sits untouched, no dead branch left "to be
safe." Deleting and consolidating are first-class outcomes — remove
duplicated *policy* and second sources of truth as you go, though code
that merely looks alike while meaning something different is left alone —
same shape, different reason to change. Stay within the file and the direct
consequences of the request; unrelated issues are their own increment.

The exception is deliberately append-only artifacts — the plan-of-record
history, ADRs, changelogs — where the audit trail *is* the value and
you supersede rather than delete.

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

Every external effect — disk, network, database, model call, queue,
clock, randomness — is named at a boundary. Domain logic stays pure or
nearly so. Tests run without the boundaries by substituting fakes that
honor the same contract as the real adapter. This is dependency
inversion made concrete (see `method.design-posture`): the boundary is
the stable contract; the adapter is the volatile detail the domain
refuses to import.

When a boundary persists durable state, write it so a crash leaves
either the complete old value or the complete new one, never a partial
write; and when persistent state is read back corrupt, quarantine the
bad artifact for inspection, recover to a safe empty or partial state,
and surface the fault — never fail silently, and never silently
discard.

## Neighbours

- `method.minimum-sufficient-work`: load when the question is how much work a task deserves, the owner's declared effort level, or how to cut increments.
- `method.decision-economy`: load when the question is whether an operation is worth running, when to stop, whether to ask or assume, or what an instruction's verb authorizes.
- `method.host-parity`: load when a result on the authoring host must stand for the target, inspection touches a shared host, or a loop is made to continue past a failure.
- `method.bounded-execution`: load when a command may hang or outlive its session, or a run must be judged running, stuck or finished.
- `method.design-posture`: load when the question is how to structure the code itself.
- `method.stewardship-posture`: load when the work is closing or knowledge must survive it.
