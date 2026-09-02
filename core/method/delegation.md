---
id: method.delegation
tier: 2
kind: method
origin: seed
title: delegation — the specialist roster, mechanical routing, model classes, bounds, briefs
owns:
  - delegation.roster
  - delegation.routing
  - delegation.model-classes
  - delegation.bounds
  - delegation.harness-registration
  - delegation.briefs
  - delegation.step-scope
  - delegation.turn
  - delegation.tracing
  - delegation.spec-authoring
requires:
peers:
  - method.tiers
artifacts:
  - templates/prompts/graph-session-bootstrap.md
  - templates/prompts/handback-payload.md
  - templates/agent.template.md
load_when:
  - "who should do this, which specialist, which agent"
  - "spawn a worker, write a delegation brief"
  - "route the task, agent routing, roster"
  - "delegation depth, allowlist, can this agent spawn"
  - "sonnet or opus, which model class"
  - "unknown agent type, specialist not registered, no such subagent"
  - "the roster was just installed, can I spawn it yet"
est_tokens: 2000
---

# Delegation — the team, routing, and bounds

The host session is the **orchestrator**: it routes, plans, briefs,
verifies, communicates, and accepts. Whether it also *does* is decided
by the task's tier (`method.tiers`). Specialists live in
`docs/graph/agents/` — each a fully-formed system prompt, projected
into the host tool's agent directory at install time. Invoke one by
spawning a clean-context worker with a purpose-made brief; persona
simulation in the chat is not delegation.

## The roster

| Specialist            | When to call                                                      |
|-----------------------|-------------------------------------------------------------------|
| `orchestrator`        | First contact; any request spanning more than one specialist.     |
| `architect`           | System boundaries, ADR-worthy decisions, contracts between modules. |
| `implementer`         | GREEN-phase code once a spec and failing tests exist.             |
| `reviewer`            | Auditing a diff against spec, plan, tests, graph.                 |
| `tester`              | Spec→test translation, RED phase, gates, regression corpus.       |
| `security`            | Threat models, auth, secrets, supply chain, AI abuse.             |
| `pentest`             | Hands-on authorized penetration testing; reproduce → fix → re-verify. |
| `reliability`         | Deploy, observability, rollback, capacity, cost; infra from scratch. |
| `data-ml`             | Datasets, pipelines, model selection, evaluation, synthetic data. |
| `product`             | User outcome, UX, acceptance criteria, accessibility.             |
| `ui-ux-designer`      | Interface/interaction design: flows, states, tokens, components, heuristics audits. |
| `docs-librarian`      | `docs/graph/` health, fact ownership, wiki leaves, catalogs, close-out. |
| `research-scout`      | Internet research; ingest libraries/specs into the wiki.          |
| `devils-advocate`     | Hostile pass over a *finished* claim-bearing deliverable; refutes from primary sources. |
| `legal`               | Regulatory compliance: corpus-bound legal reasoning, four-part findings, citation ledger. |
| `multi-agent-architect` | Agent-topology design/review: delegation bounds, tool contracts, fail-closed gates, evals, cost budgets. |
| `growth-orchestrator` | Growth DNA: conducts grow/adopt/from-scratch end to end.          |
| `growth-scout`        | Read-only per-boundary evidence gathering for graph authors.      |
| `seed-installer`      | Additive seed/adapter install; verifies the host loads the kernel. |

## Route mechanically first

Before spawning, run `python3 docs/graph/agent-lint.py --route "<task>"`
and cite the ranked line + confidence band in the brief. It is a
keyword heuristic, not an oracle — reason over it, and record why if
you override a HIGH-band pick. On **LOW/NONE** no specialist fits:
check `agent-corpus/` for the role first — where present, harvested on
demand — before authoring from scratch, then spawn an Opus-class
agent-definition author to create the missing expert. (A *specialist* is a member of the shipped roster above; an *expert*
is one you commission here for this project — it joins the *project's* roster,
never the seed's. The words are otherwise interchangeable.) A definition
authored mid-session is not yet a spawnable type — see
`delegation.harness-registration` below before delegating to it. Author it from
`docs/graph/templates/agent.template.md`, grounded in the
project's version-pinned facts (the `stack.*` node, the library wiki) —
never in memory of a version the project may not use. The *new
expert's* `model:` frontmatter is sonnet if it only investigates, opus
if it authors; the definition author itself is always opus. The expert
library compounds.

## Route by model class

Read-only investigation and mechanical retrieval/normalization →
**sonnet-class** (draft artifacts are finalized by an opus librarian);
authoring, implementation, judgment-heavy design, review, or adversarial
validation → **opus-class**. This **model class** lives in each
agent's `model:` frontmatter. It is a distinct axis from the **task tier**
(T0–T3, kernel §0) and the graph **load-tier** (the node `tier:` field): three
independent axes that share the word loosely — only the risk axis is written
`T0–T3`; "model class" and "load-tier"/`tier:` name the other two.

## Delegation is bounded

Six coordinators (`orchestrator`, `multi-agent-architect`,
`growth-orchestrator`, `architect`, `reviewer`, `docs-librarian`) hold
a depth-capped `Task` and spawn only within their `delegates_to`
allowlist (deepest legal chain: depth 3). Every other agent is a
Task-less leaf — the one recursion cap the harness itself enforces
whenever the specialist was registered as a type (see the next section
for the case where it was not): at an out-of-domain boundary a leaf
STOPs and hands back, naming the next specialist, never doing the work
itself. `agent-lint --lint` enforces the frontmatter invariants.

## A specialist is spawnable only once the host registered it

`docs/graph/agents/` is the home; a *spawnable* specialist is the host's
**projection** of it (`.claude/agents/`, `.opencode/agents/`,
`.codex/agents/`, `.github/agents/`), and a host enumerates that
directory when a session **starts**. Spawning a specialist by name
therefore has two preconditions: the session's project root is the
plant, and the projection already existed at startup. (**Prime Agent is
the exception that proves the rule:** it has no session-start roster
enumeration — its projection `.prime/agent/agents/` is a set of *brief
sources* the orchestrator reads and passes into a runtime `rlm()` spawn,
so a brief written mid-session is spawnable immediately and the trap
below never arises there.) Anything that
*writes* a projection mid-session — the install, a graft's roster delta,
a newly commissioned expert (above) — produces a specialist that is on
disk and unspawnable. Check; never assume.

**Preflight once per protocol, before the first dispatch.** Attempt one
throwaway dispatch of the type with a trivial task, or read the host's
own agent-listing surface if it has one. What does **not** answer this:
`agent-lint --route`. It globs the on-disk projection, so it names — at
HIGH confidence — exactly the types an unregistered session cannot
spawn. A route band is evidence about *fit*, never about registration.

**Remedy, in order.** (1) Re-enter the protocol from a session rooted at
the *plant* — the directory that owns the projection (for an umbrella,
the umbrella root, not a sibling repo). That also loads the plant's
kernel and route hook, which the install was supposed to guarantee
anyway. A session rooted at the **seed** never registers a plant's
roster however often it restarts: the seed is a source to copy from, not
a root to work in. (2) If your host offers an explicit reload of its
agent directory, that is cheaper — but re-run the preflight afterward,
because an unverified reload is not a remedy.

**Fallback — role emulation.** When neither remedy is available, spawn
the host's generic worker and rebuild the specialist inside the brief:

- pin the model to the specialist's `model:` class (above);
- embed `docs/graph/agents/<name>.md` **verbatim** as the worker's role;
- restore in prose every bound the frontmatter no longer enforces — the
  `tools:` allowlist as an explicit prohibition; for a leaf
  (`can_delegate: false`) "you hold no `Task`: at an out-of-domain
  boundary STOP and hand back"; and for a **coordinator**, its
  `delegates_to` allowlist and `max_spawn_depth` as a named ceiling. An
  emulated coordinator with no restated ceiling is an uncapped spawner;
- **carry this section down.** An emulated coordinator will reach its own
  by-name dispatches inside a subagent that cannot restart the session,
  so its brief must hand it both the preflight and this fallback for its
  children;
- stamp `produced_by: <role>` — the role, never the generic type — plus
  `harness_override: role-emulated (<reason>)`, so `protocol.deliver`
  can tell a recorded emulation from a silent substitution. Stamping the
  role alone makes the two identical.

Role emulation is a **degradation, not an equivalence**: a generic
worker carries `Task` and write tools, so the leaf recursion cap and the
read-only bound drop from harness-enforced to brief-requested. Scope it
to the phase that needed it, and report it in the delivery as a recorded
deviation (`protocol.deliver`) — never as a silent substitution.

## What a "turn" is

A **turn** is one **spawn → return cycle of a single worker**: the caller
spawns it, it works for as many tool calls as it needs, and it returns control
once. That return ends the turn. A turn is *not* one tool call, not one
assistant message, and not one exchange with the user.

A worker therefore hands back **exactly once per spawn** — never per tool call.
It hands back on all three ways a turn can end: it finished (`complete`), it hit
work outside its domain (`blocked-out-of-domain`), or it failed (`failed`). The
payload is required in all three; a leaf that stops at a domain boundary still
returns it, naming the next specialist rather than doing the work.

Where a document means something else, it says so in words rather than reusing
this term — "per exchange with the user" for a conversational round, "each time
the caller re-reads the payload" for a caller-side read.

## Every brief carries the graph discipline

Hooks do not reach subagents, so the brief is the only enforcement that
crosses the boundary. Embed the canonical block from
`docs/graph/templates/prompts/graph-session-bootstrap.md` verbatim,
plus the routing evidence and the handback requirement
(`docs/graph/templates/prompts/handback-payload.md` — `produced_by` and
`route_evidence` feed the deliver-time attribution assertion,
`protocol.deliver`). Parameterized briefs live in
`docs/graph/templates/prompts/`; use them.

### One step per spawn

A funnel worker (`tester`, `implementer`, `reviewer`) brief names **one**
well-defined step and embeds its inputs — the contract text, the test
paths, the diff — so the worker spends its tokens on the work, not on
rediscovering context. An oversized step is re-sliced by the orchestrator
*before* spawning, per `docs/graph/plans/grill.md` §9 (increment
shape); it is never handed whole to the worker to absorb.

**At the boundary, stop.** A worker that discovers mid-spawn that the
step is bigger than briefed finishes the briefed step (or the coherent
part it can finish), then STOPS and hands back naming the remainder in
its handback — the caller re-slices and re-spawns. Absorbing the
overflow in-place is the unbounded-spawn anti-pattern; the step scope
only bounds anything if overrunning it has this one defined outcome.

## Every spawn is traced

Every delegation carries a **`spawn_id`** — a dot-chained correlation id
the CALLER mints by extending its own: the session's first spawns are
`orchestrator.1`, `orchestrator.2`, …; a coordinator spawned as
`orchestrator.3` mints `orchestrator.3.architect.1` for its own first
child, and so on. The brief states it; the handback echoes it verbatim
(`spawn_id:` field, `templates/prompts/handback-payload.md`); the
delivery record and grill.md §15 cite it wherever a spawn's work is
referenced. The chain IS the trace: any handback's id reconstructs the
full delegation path without any infrastructure, and an id deeper than
the caller's `max_spawn_depth` allows is a bound violation on its face.
Leaves never mint one — a leaf has no children to trace.

## Spec authoring is shared

`product` writes the user-facing layer, `architect` the functional
contracts, `tester` the executable encoding. A spec is finished when
all three signed off on the same document.

## Neighbours

- `method.tiers` — decides whether to delegate at all — cross when
  classifying, before choosing workers.
