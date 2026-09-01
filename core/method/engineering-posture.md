---
id: method.engineering-posture
tier: 2
kind: method
origin: seed
title: engineering posture — sources of truth, minimum sufficient work, decision economy, integration
owns:
  - engineering-posture.sources-of-truth
  - engineering-posture.context-economy
  - engineering-posture.minimum-sufficient-work
  - engineering-posture.decision-economy
  - engineering-posture.integration-over-patching
  - engineering-posture.production-boundaries
requires:
peers:
  - method.design-posture
  - method.stewardship-posture
load_when:
  - "how much work does this task actually need, minimum sufficient work"
  - "should I read more files first, how much context to load"
  - "am I done yet, when to stop investigating or validating"
  - "how do I make this change cleanly, integrate not bolt on"
  - "which technology to pick, boring vs experimental"
  - "is this abstraction or extra worker worth its cost"
est_tokens: 2950
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

## 5. Do the minimum sufficient work

The governing objective of every task is the smallest body of work
that reliably delivers the required result. Efficiency means
eliminating work that does not materially improve correctness, safety,
required completeness, user-intent alignment, maintainability,
recoverability, or trust — it is never brevity for its own sake. A
short wrong answer is waste, and so is a long process that does not
change the result; optimize the whole path from request to validated
outcome.

Precedence when goals conflict: safety, security, privacy, and
authorization first; then explicit requirements and binding contracts;
then correctness, data integrity, and compatibility; then reliable
completion; then the validation needed to trust the result; then
efficiency; and only then optional completeness, exploration, and
polish. Efficiency may strip optional work. It may never justify
inventing information, concealing uncertainty, skipping a required
check, weakening a security boundary, suppressing a material failure,
claiming an action that did not occur, discarding evidence needed for
recovery or audit, or omitting a requirement because it is expensive.
An optional side effect — notification, telemetry, a non-critical
integration — that fails must degrade to a logged warning; it may
never fail the required path.

The execution shape: define the smallest deliverable that fully
satisfies the request; identify the decisions it needs and the minimum
evidence for them; reuse what is already established; acquire only the
missing decision-relevant evidence with the cheapest reliable
operation; act once uncertainty is below the risk threshold; validate
the assumptions capable of invalidating the result; stop. Effort
scales with uncertainty and consequence — never with apparent
complexity, input size, or the capability that happens to be
available. The task tiers (`method.tiers`) are this rule's instrument:
the tier authorizes the maximum process, and this principle selects the
minimum within it. Do not solve a larger problem than the one asked,
and do not investigate broadly before proving broad investigation
necessary.

## 6. Every operation serves a decision

Before any read, search, tool call, or spawn, name the unresolved
decision its result can change. An operation is justified when it
resolves a material ambiguity, confirms or rejects a consequential
assumption, produces part of the deliverable, detects a meaningful
failure, satisfies a mandatory requirement, or unblocks the next step
— never because it is related, interesting, conventional, reassuring,
or part of a habitual workflow. The marginal-value rule governs
continuation: another action is worth taking only while its expected
improvement exceeds its total cost, counting latency, added failure
modes, review burden, and the weight it leaves in future turns.

Retrieve progressively: indexes, metadata, headings, symbols, and
diffs before regions; regions before excerpts; a complete source only
when exactness demands it. Query in order of precision — exact
identifier, exact phrase, constrained keyword, scoped filters,
semantic search, broad exploration last. One authoritative source
decides a question unless corroboration is genuinely required:
conflicting evidence, a source that may be incomplete, or a
consequence of error that justifies confirmation.

Prefer direct execution over speculation when the action is
authorized, bounded, reversible, and cheap: a targeted test over a
predicted behavior, a measurement over an estimate, compilation over
imagined correctness. Batch operations that are independently
required; do not batch when an early result can eliminate the later
work. Never repeat a failed operation unchanged — a retry needs a
changed theory of failure or a changed condition (the recover
discipline holds the classification).

## 7. Stop when the result is sufficiently trusted

Stop investigating, executing, validating, and explaining when the
mandatory requirements are satisfied, the deliverable is complete, the
critical assumptions are validated, and the remaining uncertainty
cannot materially change the result — when the next check would test a
property already tested and the next revision would be cosmetic. Do
not add a final review, summary, alternative, source, or agent merely
because one remains possible.

Escalate — more retrieval, deeper reasoning, another worker, broader
gates — only in service of a named unresolved decision: a material
ambiguity, conflicting evidence, an unverified mandatory requirement,
an error that could cause real harm, an irreversible action, a
security or authorization boundary, or missing information that blocks
the next step. Never for curiosity, reassurance, or completeness
theater. Before finalizing substantial work, run one bounded audit —
any operation that served no decision? any dead branch, duplicated
validation, unused artifact? has the stopping condition already been
reached? — apply only the clear, material improvements, and do not
audit the audit.

Make bounded assumptions rather than asking when the detail is
low-consequence, a reasonable default exists, and the action stays
reversible — and state the assumption. Ask only when interpretations
diverge materially, the operation is irreversible, authorization is
unclear, or no safe default exists. Do not ask to avoid an ordinary
decision, and do not fabricate certainty where an assumption remains
material.

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
per rule, precedence stated once, generalize an existing rule instead
of appending a sibling, no repetition for emphasis, no rule the
runtime already guarantees. An instruction surface whose size
obstructs the work it governs is defective — the kernel byte budget is
this rule, enforced. And use the cheapest competent method throughout:
deterministic code, rules, and templates before model calls; the
smaller model class for bounded read-only work (`method.delegation`);
a stronger model never compensates for poor scoping or unnecessary
context. Weigh the future cost of output as part of its cost: prefer
results that are immediately usable, isolate changes, and keep the
next delta cheap — local efficiency that creates downstream burden is
not efficiency.

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

- `method.design-posture` — the SOLID/responsibility design cluster —
  cross when the question is how to structure the code itself.
- `method.stewardship-posture` — record, verify, persist, and hand
  off — cross when the work is closing or knowledge must survive it.
