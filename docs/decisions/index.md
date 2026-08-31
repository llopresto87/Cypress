# Seed self-docs — Decisions (ADRs)

Durable architecture decisions about the **CYPRESS framework itself**
(not any application built with it). These live under the seed's self-docs tree
(`docs/`, alongside `docs/plans/`) — deliberately **not** under `docs/graph/`,
which is the installed *application* knowledge graph. ADR bodies use
`templates/adr.template.md`.

| ADR | Title | Status | Decided | Source | Plan phase |
|---|---|---|---|---|---|
| [0001](adr-0001-mechanical-agent-router.md) | Mechanical agent-router (`agent-lint.py --route`) fed by `routing_triggers` | accepted | 2026-07-13 | plan §3 ADR-A | P0 |
| [0002](adr-0002-bounded-delegation-hybrid.md) | Bounded-delegation hybrid (originally 5 delegators, now 6 — see amendment; leaf-only allowlists, depth ≤ 3) | accepted (amended 2026-07-23) | 2026-07-13 | plan §3 ADR-B | P1 |
| [0003](adr-0003-enforcement-layering-honesty.md) | Enforcement layering, honestly labelled (tool-grant hard; caps soft; deliver-time detective) | accepted | 2026-07-13 | plan §3 ADR-C | P2 |
| [0004](adr-0004-pure-graph-architecture.md) | The seed is a pure graph (machinery as routable nodes; kernel is a bootstrap) | accepted | 2026-07-22 | pure-graph-refactor.md | 6.0.0 |

ADRs **0001–0003** were decided inline in the plan-of-record
[`../plans/agent-routing-and-delegation.md`](../plans/agent-routing-and-delegation.md)
§3 and promoted to standalone ADRs on 2026-07-13; the plan's §3 remains their
faithful source. They describe agent-routing mechanics decided under the **pre-6.0
layout** — their agent counts and file paths reflect that era; the underlying
decisions still hold (the mechanical router, bounded delegation, and honest
enforcement layering are all current), and ADR-0002 carries a dated amendment
where the roster later grew. **ADR-0004** records the current governing
architecture (the 6.0.0 pure graph), sourced from
[`../plans/pure-graph-refactor.md`](../plans/pure-graph-refactor.md). Verified
gate results for each implementation are recorded once, in the owning plan's
changelog. ADRs are append-only: supersede or amend, never rewrite.
