# ADR-0004: The seed is a pure graph (machinery as routable nodes; kernel is a bootstrap)

## Status

`accepted` — shipped as **6.0.0** (2026-07-22). This ADR is the standalone
decision record for the architecture the plan-of-record
[`../plans/pure-graph-refactor.md`](../plans/pure-graph-refactor.md) executed;
that plan (marked EXECUTED) and CHANGELOG 6.0.0 remain the faithful source, and
this file restates the decision and links back. It is the current governing
architecture — ADRs 0001–0003 describe agent-routing mechanics decided under the
pre-6.0 layout and predate it.

## Date

2026-07-22

## Context

Through 5.x the kernel (`core/AGENTS.md`, loaded on **every** session of **every**
plant) had grown to ~21 KB, and the method surface — protocols, skills, agent
charters, and the operating-principles posture — lived partly in always-loaded
files and partly as tool-directory copies (`.claude/protocols/`, `.claude/core/`,
…). Two costs followed. First, **always-loaded rent**: every byte of method a
session might never need was still paid on every session. Second, **projection
drift**: the same method content lived in the kernel/authored files *and* in
per-tool copies, with nothing forcing them to agree. The seed already enforced
one-home-per-fact on its *knowledge* graph but not on its own *machinery*.

## Decision

Make the seed a **pure graph**: everything that can activate progressively is a
routable node, and only a small bootstrap is always-loaded.

- Every protocol, skill, agent charter, and method/posture principle installs
  INTO the plant's `docs/graph/` as a first-class routable node
  (kinds `protocol`/`skill`/`agent`/`method`, marked `origin: seed`), routed by
  the one router, costed by `est_tokens`, linted by the one `graph-lint.py`.
- The kernel shrinks to a **~7 KB bootstrap** (budget 8 000 bytes): identity,
  the first move (open the router), the tier table, the eight rules as one-line
  anchors each naming its owning node, the §4 boundaries, and pointers. Every
  full rule statement moved to its owning node.
- `operating-principles.md` split at its thematic joints into three posture
  nodes — `method.engineering-posture`, `method.design-posture`,
  `method.stewardship-posture`; the old file became a tombstone.
- Tool directories keep only **generated projections** of nodes (the surfaces a
  host loads from fixed locations), never a hand-authored second home.

This supersedes the 5.6/5.7 layout, which shipped the doctrine as an
always-loaded `operating-principles.md` plus tool-dir machinery copies.

## Consequences

- A fresh install lints clean at 49 machinery nodes (~77 K tokens if fully
  loaded — which is the point: no task loads more than its resolved closure,
  typically ~3 nodes).
- `seed-lint.py` gained the machinery-node contract (frontmatter on every
  node, global `owns`-uniqueness, the eight `rule.*` homes) and a 8 000-byte
  kernel budget; `graph-lint.py` gained the machinery kinds/dirs and the
  `origin:` key.
- **Breaking for 5.x plants.** `graft` carries a layout-migration path
  (5.x → 6.0.0) that relocates machinery into `docs/graph/`, reconciles
  plant customizations, and sweeps pre-graph knowledge into the graph.
- The pure-graph principle is **standing**, not a one-time move: any surface
  that reverts to a hand-maintained copy of node content, or an always-loaded
  file that could be a node, is a drift from this ADR and is closed at its home.
  Later work extended the principle to slash commands (generated as projections
  of the command-protocol nodes) and made graft's pure-graph rebalance of
  existing plants a per-graft gate (`graft.pure-graph-mandate`).

## Alternatives considered

- **Keep the always-loaded kernel + tool-dir machinery, just trim it.** —
  rejected: it leaves the always-loaded rent and the two-home drift in place; it
  treats a symptom (kernel size) not the cause (method that should route).
- **Move method into the graph but keep authored per-tool copies.** — rejected:
  the copies are the drift. Projections must be generated from the one node.

## Reversibility

`reversible in principle, breaking in practice` — the split is mechanical to
undo, but plants grown on 6.0.0 assume the graph layout; a rollback would
require re-inlining every node into the kernel and regrowing tool-dir copies.
Forward migration (`graft`) is the supported path, not rollback.

## References

- Plan (source of the decision): `../plans/pure-graph-refactor.md` (EXECUTED).
- CHANGELOG: the `6.0.0 — the seed becomes a pure graph` entry.
- Superseded layout: `../plans/integrate-design-doctrine.md` (5.7, superseded).
- Sibling ADRs (pre-6.0 agent-routing mechanics): `adr-0001-mechanical-agent-router.md`,
  `adr-0002-bounded-delegation-hybrid.md`, `adr-0003-enforcement-layering-honesty.md`.
- Catalog: `index.md`.
