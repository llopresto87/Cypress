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

Graft is **user-decided**: it starts only when you paste this prompt, and
unprompted the system may only *propose* a graft — most naturally right after
a harvest lands ("the seed now carries fruit these sibling plants predate") —
and stop there. The reconciled result reaches the plant only once you ratify
it. Because every replaced file is backed up first, a ratified graft is also
reversible.

---

Graft the current seed at `{{seed path; locate the seed repository if not in
scope}}` onto the existing plant at `{{plant path or umbrella; default: current
working directory}}`. Root this chat at the **plant**: the graft writes there
and dispatches its roster. Upgrade only the plant's seed-owned machinery and
refresh its library/tool knowledge surfaces from the seed's corpus. Leave the
seed as it is; the upgrade reaches the plant as a proposal I ratify, never as
a silent change.

Hold the **rootstock line** throughout: graft upgrades seed-owned machinery
only, and everything the plant authored about itself stays exactly as written
— its application source and every knowledge fact it authored under
`docs/graph/` (any node without `origin: seed`, and the pinned
version-specific facts in its library/tool pages). An upgrade that would need
to rewrite plant-authored text stops at the line and comes to me.
`protocols/graft.md` defines the two territories in full — hold the line
exactly as the node draws it. Graft gives the plant the seed's new growth and
leaves the plant's roots, trunk, and fruit exactly as they were.

This chat is the orchestration and planning plane: it routes, plans and talks
with me, and every survey, reconciliation and authoring task goes to a
clean-context worker with a bounded brief (the exact paths it may inspect, the
graph bootstrap, evidence rules, and deliverables). Investigation-class
workers ONLY survey and classify, read-only; authoring-class workers do every
reconciliation, holistic merge, corpus refresh, and validation
(`delegation.model-classes`). Every worker brief embeds the graph-session
bootstrap blocks (`docs/graph/templates/prompts/graph-session-bootstrap.md`)
verbatim.

A graft installs a **roster delta** — specialists the seed added or renamed since
the plant's base — and whether this session can spawn those types is
host-dependent, because the graft writes them mid-session. A graft across a
roster rename always produces such a delta. Preflight before the phases that
dispatch by name, and take the remedy or the recorded fallback in
`docs/graph/method/delegation-bounds.md` (`delegation.harness-registration`).

Beyond upgrading machinery, graft **rebalances the plant toward pure graph,
end to end** (its Phase 6, the pure-graph mandate): every graft leaves the plant
at least as purely a graph as the seed's own architecture, where every
machinery file and fact lives in exactly one `docs/graph/` node, every
projection matches its node, and leftover residue is listed for deletion. It
re-homes each drift from that state into its owning node as a holistic merge (the fact itself preserved — the
rootstock line holds), regenerates drifted projections from their nodes, lists
obsolete residue for your deletion, and surfaces any drift it could not close.

## The plant facts come from the owner, before the graft runs

Read the plant's `docs/graph/index.md` `plant:` block first. If any of `environment_class`,
`commit_attribution`, `deliverable_language`, `comment_language` is still a placeholder, put
the four to the owner as one numbered ask, proposing each value from evidence with the paths
you used, and write the confirmed values before running the installer (or pass them as its
flags). Take each value from this plant's evidence and the owner's answer, never from a
guess or another plant: the environment class alone decides what the release posture
tolerates on this plant.

## Run the graft

Now **execute the graft protocol — `protocols/graft.md` — in full**: read it,
then drive every phase and every gate it defines, in order, including its
three-way reconciliation, the **pure-graph rebalance (Phase 6)**, and its
**5.x → 6.0.0 layout-migration** section where the survey finds a pre-6.0
plant. That node is the single authority on the flow, so work from the node
itself, not a summary. In particular the protocol closes only after it has
**grown** the newly delivered capabilities onto the living plant (not merely
fast-forwarded them as inert machinery) and passed every fail-closed gate — the customization
audit (`tools/graft-audit.py`, the reconcile-before-overwrite gate), the
minimum-sufficient-upgrade audit, and the cross-author rebalance where parallel
authors were used. Deliver the reconciled upgrade as a reviewable proposal with
the node's graft summary; hand every KEEP-PLANT divergence back as a harvest
candidate.
