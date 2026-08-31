# Graft the enriched seed onto an existing plant

Use this prompt as the tool-neutral entry point for the **graft** protocol —
the distribution arm of the cross-project loop and the outward complement of
harvest. Paste it into an agent-capable chat with an existing, already-grown
project (a "plant") as the working scope. It carries the seed's evolved
machinery and the fruits of every harvest since the plant grew onto that plant,
so a plant grown from an older seed inherits the improvements — without being
regrown from scratch.

Run it when the plant is **grown and steady** (its graph routes, its
plan-of-record is closed or calm) and the seed has **moved on since the plant
grew from it** — a harvest folded in new fruit, a protocol sharpened, the corpus
gained pages for libraries this plant already uses. A clean working tree makes
the additive upgrade and its automatic backups easy to review and to unwind.

Graft is **user-decided**. The most the system does unprompted is *propose* a
graft — most naturally right after a harvest lands ("the seed now carries fruit
these sibling plants predate") — and stop. You start it by pasting this prompt,
and the reconciled result reaches the plant only once you ratify it. Because
every replaced file is backed up first, a ratified graft is also reversible.

---

Graft the current seed at `{{seed path; locate the seed repository if not in
scope}}` onto the existing plant at `{{plant path or umbrella; default: current
working directory}}`. Upgrade only the plant's seed-owned machinery and refresh
its library/tool knowledge surfaces from the seed's corpus. Do not modify the
seed. Do not rewrite anything the plant authored about itself. Propose the
reconciled upgrade for my ratification; never silently mutate the plant.

This chat is the orchestration and planning plane. Do not perform survey,
reconciliation, or authoring in the main chat. Maintain the plan here, talk to me
here, and spawn clean-context workers with bounded briefs: the exact paths they
may inspect, the graph bootstrap, evidence rules, and deliverables. Model policy
is strict — **Sonnet-class** workers only survey and classify (read-only);
**Opus-class** workers do every reconciliation, holistic merge, corpus refresh,
and validation.

Every spawned worker runs the plant's graph router before reading plant source:
`python3 docs/graph/graph-lint.py --plan "<its exact task>"`, and returns the
command/output, the loaded closure, and deliberate skips.

A graft installs a **roster delta** — specialists the seed added or renamed since
the plant's base — and those types are not spawnable in this session, because the
host enumerated its agent directory before the graft wrote them. A plant grafted
across a roster rename hits that every time. Preflight before the phases that
dispatch by name, and take the remedy or the recorded fallback in
`docs/graph/method/delegation.md` (`delegation.harness-registration`). Run this
chat rooted at the **plant**, never at the seed.

Hold the **rootstock line** throughout: graft upgrades seed-owned machinery
only, and never overwrites anything the plant authored about itself — its
application source and every knowledge fact it authored under `docs/graph/`
(any node without `origin: seed`, and the pinned version-specific facts in its
library/tool pages). If an upgrade cannot land without rewriting something the
plant authored, stop at the line and surface it to me. `protocols/graft.md`
defines the two territories in full — hold the line exactly as the node draws
it.

Beyond upgrading machinery, graft **rebalances the plant toward pure graph,
end to end** (its Phase 6, the pure-graph mandate): every graft leaves the plant
at least as purely a graph as the seed's own architecture — no machinery or fact
living outside a `docs/graph/` node, no fact with two homes, no hand-maintained
projection drifted from its node, no dead-era residue. It re-homes each such
drift into its owning node as a holistic merge (the fact itself preserved — the
rootstock line holds), regenerates drifted projections from their nodes, lists
obsolete residue for your deletion, and surfaces any drift it could not close.

Now **execute the graft protocol — `protocols/graft.md` — in full**: read it,
then drive every phase and every gate it defines, in order, including its
three-way reconciliation, the **pure-graph rebalance (Phase 6)**, and its
**5.x → 6.0.0 layout-migration** section where the survey finds a pre-6.0 plant. That node is the single authority on the
flow; do not work from a summary and do not skip, reorder, or collapse its
phases. In particular the protocol closes only after it has **grown** the newly
delivered capabilities onto the living plant (not merely fast-forwarded them
as inert machinery) and passed every fail-closed gate — the customization
audit (`tools/graft-audit.py`, the reconcile-before-overwrite gate), the
minimum-sufficient-upgrade audit, and the cross-author rebalance where parallel
authors were used. Deliver the reconciled upgrade as a reviewable proposal with
the node's graft summary; hand every KEEP-PLANT divergence back as a harvest
candidate.

Keep the plant's own life inviolate throughout: graft gives the plant the seed's
new growth and leaves the plant's roots, trunk, and fruit exactly as they were.
