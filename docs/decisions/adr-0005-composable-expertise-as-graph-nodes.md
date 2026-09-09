---
status: accepted
status_date: 2026-09-09
owner: seed steward
---

# ADR-0005: Composable expertise is a node kind and a lazy edge, not a deeper agent tree

## Status

See frontmatter — the single home. Shipped as **7.5.0**; the plan-of-record
[`../plans/grill-7.5.0-composable-expertise.md`](../plans/grill-7.5.0-composable-expertise.md)
is the faithful source for the mechanism and its verification, and this file
records the decision and links back.

## Date

2026-09-09

## Context

A plant needs project-specific expertise — what a runtime, framework, or
library means *for this project*, what must not be done without it, and which
of its parts a given task actually needs. Through 7.4.0 the seed had exactly
one way to supply that: author an expert agent. The staffing arm shipped in
7.4.0 made the decision recorded and the resulting agent spawnable, but it did
not change what the answer had to be.

That single answer is expensive in three ways. Every expert is a registered
agent file, so N libraries means N roster entries, N sets of routing triggers
competing for distinctiveness, and a registration each. Every spawn is a fresh
context, so a caller cannot see the callee's in-progress work and a chain of
three costs three graph loads and two handbacks to answer what is usually a
factual question. And the delegation graph is deliberately bounded to depth 3
(ADR-0002), so an implementer reaching library knowledge through agents would
consume the orchestrator's entire budget with no headroom.

The operator asked for something narrower and cheaper: expertise that composes
as **nodes and leaves**, not as agents spawning agents. The obstacle was that
the graph had no edge for it. `requires:` is defined as a hard dependency
always loaded with its node, and `_schema.md` names "a node that requires
everything" as an anti-pattern; composing a stack's libraries through it would
drag every library page into every task that touched the stack. `peers:` is
the opposite and equally wrong: never loaded unless the task deliberately
crosses.

## Decision

Expertise is a **node kind**, composed through a **new lazy edge**, resolved by
the context router. Agents stay flat and few.

- **`kind: expertise`**, at `docs/graph/nodes/expertise.<slug>.md`, owning
  exactly two facts: `<slug>.applicability` (when this is in play, and what
  must not be done without it) and `<slug>.composition` (which sub-expertises
  apply under which condition). It routes to depth through `libraries:` and
  `artifacts:` and restates nothing those leaves own. A node with no depth edge
  routes to nothing and fails lint.
- **`composes:`** — lazy, downward, expertise-to-expertise only. Where
  `requires:` is a closure the router always takes, `composes:` is a menu it
  reads. The union of the two is deliberately not cycle-checked: `parent
  composes child` together with `child requires parent` is the intended shape,
  the eager edge pointing up and the lazy one down.
- **Delta-exact descent.** The router descends into a composed child when the
  task names, exactly, a term in the child's own vocabulary — its `load_when`
  plus its whole slug — that the parent does not carry. Family words therefore
  sit on the parent by construction and can descend nobody. It is IDF-free, so
  routing does not drift as a plant grows, and exact-only, so a prefix fold
  cannot pull in a sibling. `--plan` prints why each un-composed child stayed
  out.
- **Unversioned slugs**, with one exception. The pin lives in
  `libraries/<slug>.md`, and the node points at it. When a plant runs two
  majors of one stack at once, the unversioned node composes one
  version-qualified child per major — the only place a version enters an id,
  derived from the inventory rather than decided.
- **The seam with `stack.*`.** A stack node owns this project's own
  conventions and requires its expertise node; an expertise node owns
  applicability over external depth. Neither restates the other.
- **Expertise is called, not carried.** No agent declares it in
  `plant_knowledge:`. Every delegation brief already runs the router on the
  exact delegated task, so writing that task line in the domain's words is
  what composes the right expertise in, and the node's own Depth section tells
  a reader of any identity which leaf to open.
- **Staffing narrows to four triggers.** Every core or significant stack
  element owes a node, derived mechanically. An agent is warranted only for
  what a node cannot be — different tools, a different model class, an
  adversarial stance, or context isolation — and the coverage record names
  which.

## Consequences

- A task about one library loads the parent expertise and that library's node
  and not its siblings. Per-library granularity becomes affordable, which is
  what makes the operator's example expressible at all.
- The coverage gate derives an expertise obligation per inventory item, so a
  plant cannot arrive without one by nobody having decided — and a plant whose
  stack owes none stays green with no row to answer.
- `graph-lint.py` gains five rules (15–19) and two authoring warnings; its
  `--plan` output gains provenance and reasons, and `--graph` prints `~>` for
  the lazy edge. Existing graphs carrying no `composes:` route exactly as
  before.
- Every plant gains the kind on its next graft: the engine's `KINDS` is a
  set-literal that `graft-graph-engine.py` unions.
- ADR-0001 is reinforced rather than amended — the router still routes
  knowledge nodes and never agents. ADR-0002's delegation bounds are untouched,
  because nothing here widens the delegation graph.

## Alternatives considered

- **Expert agents that spawn expert agents** (`implementer → dotnet →
  library-X`) — rejected by the operator explicitly, and independently
  unsound: `implementer` is a leaf, making the chain legal would consume the
  whole depth budget and supersede ADR-0002, each level costs a fresh context
  and a handback, and it partially reverses ADR-0001.
- **Compose through `requires:`** — rejected: closure explosion by
  construction, and the anti-pattern the schema already names.
- **An upward `specializes:` edge on the child** — rejected: it needs a
  reverse index at plan time and the parent stops reading as a menu. The
  reciprocity lint gives its one real advantage, a child that cannot forget
  its parent, without either cost.
- **A scored threshold for descent** — rejected: the score is IDF-weighted, so
  the same child descends on a small plant and not on a large one, and a score
  cannot tell "the task names EF Core" from "the task names dotnet loudly".
- **Versioned slugs everywhere** (`expertise.dotnet-9`) — rejected: it puts a
  pin in every referrer's edge list, and a major upgrade becomes a new node
  plus a retirement convention the repo does not have.
- **Replacing `stack.*` with `expertise.*`** — rejected: it breaks grown
  plants and conflates this project's conventions with external applicability.
- **A `docs/graph/expertise/` directory** — rejected: it reads as a second
  graph, and its one advantage (an automatic coverage row) is unnecessary once
  coverage is derived per inventory item.

## Reversibility

`reversible` — the kind and the edge are additive. Removing them leaves nodes
that lint as an unknown kind, so the supported path is a graft that folds each
expertise node's applicability back into its `stack.*` node and drops the
edge; no plant data is lost, because every fact the node points at already
lives in `libraries/` and `best-practices/`.

## References

- Plan (source of the decision and its verification):
  [`../plans/grill-7.5.0-composable-expertise.md`](../plans/grill-7.5.0-composable-expertise.md).
- CHANGELOG: the `7.5.0` entry.
- Contract: `templates/knowledge-graph/_schema.md` — the `expertise` kind, the
  `composes` key semantics, rules 15–19.
- Sibling ADRs: [`adr-0001-mechanical-agent-router.md`](adr-0001-mechanical-agent-router.md)
  (the router routes nodes, never agents),
  [`adr-0002-bounded-delegation-hybrid.md`](adr-0002-bounded-delegation-hybrid.md)
  (the delegation bounds this decision avoids widening),
  [`adr-0004-pure-graph-architecture.md`](adr-0004-pure-graph-architecture.md)
  (the governing architecture this extends).
- Catalog: [`index.md`](index.md).
