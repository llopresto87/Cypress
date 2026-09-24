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
| [0003](adr-0003-enforcement-layering-honesty.md) | Enforcement layering, honestly labelled (tool-grant hard; caps soft; deliver-time detective) | accepted (amended 2026-09-14) | 2026-07-13 | plan §3 ADR-C | P2 |
| [0004](adr-0004-pure-graph-architecture.md) | The seed is a pure graph (machinery as routable nodes; kernel is a bootstrap) | accepted | 2026-07-22 | pure-graph-refactor.md | 6.0.0 |
| [0005](adr-0005-composable-expertise-as-graph-nodes.md) | Composable expertise is a node kind and a lazy edge, not a deeper agent tree | accepted | 2026-09-09 | grill-7.5.0-composable-expertise.md | 7.5.0 |
| [0006](adr-0006-t2-contained-lane.md) | T2 gains a contained lane — a small change is authorized by a test and a why, not a spec | accepted | 2026-09-13 | grill-7.14.0-t2-contained-lane.md | 7.14.0 |
| [0007](adr-0007-lifecycle-protocol-ceiling.md) | The cross-project meta-loop answers to a larger body ceiling than the rest of the graph | accepted | 2026-09-14 | grill-7.15.0-remediation.md | 7.16.0 |
| [0008](adr-0008-roster-justification-lives-in-the-node.md) | A component's justification lives in the component (`prevents:`), derived not published; the name-occurrence count is retired | accepted | 2026-09-14 | grill-7.15.0-remediation.md | 7.16.0 |
| [0009](adr-0009-host-support-tiers.md) | Hosts sit in three support tiers (first-class, supported, frozen); `install.sh all` installs only the first two | proposed | 2026-09-23 | grill-7.27.0-host-support-tiers.md | 7.27.0 |
| [0010](adr-0010-context-residency.md) | Text enters a session once, at the lowest residency class that serves it; the per-prompt hooks hold to that per host, and the ledger's threat model | proposed | 2026-09-23 | grill-7.28.0-context-residency.md | 7.28.0 |
| [0011](adr-0011-donor-token-redaction.md) | Donor-identifying tokens in append-only seed records are replaced in place, under one scoped exception whose home is `CLAUDE.md` Conventions | proposed | 2026-09-24 | grill-7.29.0-front-door.md | 7.29.0 |

ADRs **0001–0003** were decided inline in the plan-of-record
[`../plans/agent-routing-and-delegation.md`](../plans/agent-routing-and-delegation.md)
§3 and promoted to standalone ADRs on 2026-07-13; the plan's §3 remains their
faithful source. They describe agent-routing mechanics decided under the **pre-6.0
layout** — their agent counts and file paths reflect that era; the underlying
decisions still hold (the mechanical router, bounded delegation, and honest
enforcement layering are all current), and ADR-0002 carries a dated amendment
where the roster later grew. **ADR-0004** records the current governing
architecture (the 6.0.0 pure graph), sourced from
[`../plans/pure-graph-refactor.md`](../plans/pure-graph-refactor.md).
**ADR-0005** extends that architecture with the `expertise` kind and the lazy
`composes:` edge, and is the standing answer to "how does project-specific
expertise compose" — through the router's own edges, never through a deeper
agent tree.
**ADR-0007** records why the three cross-project meta-loop protocols answer to a
larger body ceiling than the rest of the graph, and why that is a second ceiling
rather than an exemption.
**ADR-0008** puts each component's justification in the component — the failure
its absence produces, as a required `prevents:` key — and retires the
name-occurrence count that had been standing in for evidence of use, which
measured how much other prose discusses a component rather than whether anything
needs it. Verified
gate results for each implementation are recorded once, in the owning plan's
changelog. ADRs are append-only: supersede or amend, never rewrite.
