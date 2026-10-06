# Seed self-docs — Decisions (ADRs)

Durable architecture decisions about the **CYPRESS framework itself**
(not any application built with it). These live under the seed's self-docs tree
(`docs/`, alongside `docs/plans/`) — deliberately **not** under `docs/graph/`,
which is the installed *application* knowledge graph. ADR bodies use
`templates/adr.template.md`.

| ADR | Title | Status | Decided | Source | Plan phase |
|---|---|---|---|---|---|
| [0001](adr-0001-mechanical-agent-router.md) | Mechanical agent-router (`agent-lint.py --route`) fed by `routing_triggers` | accepted | 2026-07-13 | plan §3 ADR-A | P0 |
| [0002](adr-0002-bounded-delegation-hybrid.md) | Bounded-delegation hybrid (originally 5 delegators, now 6 — see amendment; leaf-only allowlists, depth ≤ 3) | accepted (amended 2026-07-23, 2026-08-06, 2026-09-28) | 2026-07-13 | plan §3 ADR-B | P1 |
| [0003](adr-0003-enforcement-layering-honesty.md) | Enforcement layering, honestly labelled (tool-grant hard; caps soft; deliver-time detective) | accepted (amended 2026-09-14, twice 2026-09-24) | 2026-07-13 | plan §3 ADR-C | P2 |
| [0004](adr-0004-pure-graph-architecture.md) | The seed is a pure graph (machinery as routable nodes; kernel is a bootstrap) | accepted | 2026-07-22 | pure-graph-refactor.md | 6.0.0 |
| [0005](adr-0005-composable-expertise-as-graph-nodes.md) | Composable expertise is a node kind and a lazy edge, not a deeper agent tree | accepted | 2026-09-09 | grill-7.5.0-composable-expertise.md | 7.5.0 |
| [0006](adr-0006-t2-contained-lane.md) | T2 gains a contained lane — a small change is authorized by a test and a why, not a spec | accepted (amended in part by ADR-0023, 2026-09-30) | 2026-09-13 | grill-7.14.0-t2-contained-lane.md | 7.14.0 |
| [0007](adr-0007-lifecycle-protocol-ceiling.md) | The cross-project meta-loop answers to a larger body ceiling than the rest of the graph | accepted | 2026-09-14 | grill-7.15.0-remediation.md | 7.16.0 |
| [0008](adr-0008-roster-justification-lives-in-the-node.md) | A component's justification lives in the component (`prevents:`), derived not published; the name-occurrence count is retired | accepted | 2026-09-14 | grill-7.15.0-remediation.md | 7.16.0 |
| [0009](adr-0009-host-support-tiers.md) | Hosts sit in three support tiers (first-class, supported, frozen); `install.sh all` installs only the first two | proposed | 2026-09-23 | grill-7.27.0-host-support-tiers.md | 7.27.0 |
| [0010](adr-0010-context-residency.md) | Text enters a session once, at the lowest residency class that serves it; the per-prompt hooks hold to that per host, and the ledger's threat model | proposed (superseded in part by ADR-0024, 2026-10-01) | 2026-09-23 | grill-7.28.0-context-residency.md | 7.28.0 |
| [0011](adr-0011-donor-token-redaction.md) | Donor-identifying tokens in append-only seed records are replaced in place, under one scoped exception whose home is `CLAUDE.md` Conventions | proposed | 2026-09-24 | grill-7.29.0-front-door.md | 7.29.0 |
| [0012](adr-0012-red-waves-ahead-of-green.md) | Work runs in cycles of a RED wave and a clean GREEN wave; holds are per increment; one ruling pass per cycle rules on what was flagged; `grill-lint.py --waves` reports the schedule | accepted | 2026-09-28 | grill-7.31.0-wave-scheduling.md | 7.31.0 |
| [0013](adr-0013-harness-memory-is-not-a-home.md) | Harness memory is not a home: a session writes what it learns to a session record in the plant (`docs/graph/plans/sessions/`), which canonize files; the kernel's §3.2 points there | accepted | 2026-09-28 | grill-7.31.0-wave-scheduling.md | 7.31.0 |
| [0014](adr-0014-graft-reconciles-every-graph-engine.md) | Graft reconciles every graph engine with the config each one carries (the tool picks it per engine; the audit checks every pair); the installer keeps engines plant-owned | accepted | 2026-09-28 | grill-7.31.0-wave-scheduling.md | 7.31.0 |
| [0015](adr-0015-cross-repository-decision-references.md) | A plan may cite another repository's decision as `<name>:ADR-NNNN`; `grill-lint.py` reports it as external and does not resolve it | proposed | 2026-09-28 | grill-7.32.0-harvest.md | 7.32.0 |
| [0016](adr-0016-stamp-carries-keys-it-does-not-own.md) | The seed stamp is an open record: the installer carries forward every key it does not own | proposed | 2026-09-28 | grill-7.32.0-harvest.md | 7.32.0 |
| [0017](adr-0017-pre-growth-pointers-leave-the-kernel.md) | The pre-growth pointers leave the kernel and live in the placeholder index that grow rewrites | proposed (a consequence amended in part by ADR-0027, 2026-10-01) | 2026-09-28 | grill-7.32.0-harvest.md | 7.32.0 |
| [0018](adr-0018-code-fact-freshness-anchor.md) | Facts the graph states are settled; code facts are checked once per session against an anchor canonize records | proposed | 2026-09-28 | grill-7.32.0-harvest.md | 7.32.0 |
| [0019](adr-0019-no-opus-version-table-in-the-seed.md) | The seed names no Opus version table; a protocol names the model class, and one rule maps the class to a version | proposed (superseded in part by ADR-0022, 2026-09-30) | 2026-09-28 | grill-7.32.0-harvest.md | 7.32.0 |
| [0020](adr-0020-a-plans-ledger-lives-beside-it.md) | A plan's increments live beside it in a directory named for its stem; the seed's round plans are ledgers | proposed | 2026-09-28 | grill-7.32.0-harvest.md | 7.32.0 |
| [0021](adr-0021-seed-only-procedures-stay-home.md) | A seed-only procedure lives under `docs/skills/`, and `check_seed_only_stays_home` proves it never reaches a plant | proposed | 2026-09-30 | owner rulings D1, D2 (kept outside the seed) | 7.35.0 |
| [0022](adr-0022-the-plant-model-map.md) | A plant names its models once, in `docs/graph/models.md`; nodes name the class, and each host reads the map in its own way (supersedes ADR-0019 in part) | proposed | 2026-09-30 | owner ruling D9 (kept outside the seed) | 7.35.0 |
| [0023](adr-0023-a-declarative-edit-is-proved-by-a-run.md) | A declarative edit with nothing to get wrong is proved by a run, not a RED test (amends ADR-0006 in part) | proposed | 2026-09-30 | owner report, a pipeline selector (kept outside the seed) | unreleased |
| [0024](adr-0024-one-hook-core-per-session-residency.md) | One Python hook core gives every hooked host per-session residency; children and non-human turns are not routed (supersedes ADR-0010 in part) | accepted | 2026-10-01 | owner ruling D1 (kept outside the seed) | 7.37.0 |
| [0025](adr-0025-compact-route-lines-json-between-programs.md) | The router talks to models in compact lines that keep every resolved path; JSON is only for programs; nodes are read through `--show` | accepted | 2026-10-01 | owner rulings on JSON, D3, O1 (kept outside the seed) | 7.37.0 |
| [0026](adr-0026-node-router-ladder-and-gated-corpus.md) | The node router ranks named ids and paths above words, abstains with a cheap notice instead of forcing root, and is gated per class on a node-route corpus (a quality change; no token claim) | accepted | 2026-10-01 | the round's routing investigation (kept outside the seed) | 7.37.0 |
| [0027](adr-0027-first-move-runs-the-router.md) | The kernel's FIRST MOVE runs the router and `index.md` becomes the fallback map, landed on a measurement that favoured it (amends a consequence of ADR-0017 in part) | accepted | 2026-10-01 | owner ruling D2 (kept outside the seed) | 7.37.0 |
| [0028](adr-0028-harvest-takes-knowledge-whole.md) | Harvest generalizes instead of rejecting, admits the version facts a library documents (security facts, calendar dates and a plant's own version stay out), and classes every fact by provenance | proposed | 2026-10-05 | owner decisions of 2026-10-04 and 2026-10-05 | 8.0.0 |

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
changelog. ADRs are append-only: supersede or amend, never rewrite. One scoped
exception to append-only, for other records: [`CLAUDE.md` Conventions](../../CLAUDE.md).
