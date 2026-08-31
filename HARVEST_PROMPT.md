# Harvest a grown plant back into the seed

Use this prompt as the tool-neutral entry point for the **harvest** protocol —
the inverse of install/grow. Paste it into an agent-capable chat while a mature
project (a "plant" grown from CYPRESS) is the working scope. It
folds that plant's *project-agnostic* lessons back into the seed so the next
plant grows more magnificent — without re-deriving what this one already learned.

Run it when the plant is **fully grown**: delivered, verification gates green,
plan-of-record closed or steady. Harvesting a still-churning project backports
half-baked lessons.

Harvest is **user-triggered only** — nothing in the system starts it on its own
(no schedule, no hook, no tail-end step of another protocol). You start it by
pasting this prompt; the most an agent does unprompted is *suggest* that a
harvest looks worthwhile and stop. And nothing reaches the seed until you are
satisfied with the growth — every fold-back is a proposal you ratify.

---

Harvest generalizable improvements from the mature plant at `{{plant path or
umbrella; default: current working directory}}` back into CYPRESS
at `{{seed path; locate the seed repository if not in scope}}`. Do not modify the
plant. Propose changes to the seed for my ratification; never silently mutate it.

This chat is the orchestration and planning plane. Do not perform investigation,
generalization, or authoring in the main chat. Maintain the plan here, talk to me
here, and spawn clean-context workers with bounded briefs: the exact paths they
may inspect, the graph bootstrap, evidence rules, and deliverables. Model policy
is strict — **Sonnet-class** workers only survey/inventory/extract (read-only);
**Opus-class** workers do every generalization, authoring, and adversarial check.

Every spawned worker runs the plant's graph router before reading source:
`python3 docs/graph/graph-lint.py --plan "<its exact task>"`, and returns the
command/output, the loaded closure, and deliberate skips.

Now **execute the harvest protocol — `protocols/harvest.md` — in full**: read
it, then drive every phase it defines, in order. That node is the single
authority on the flow; do not work from a summary and do not skip, reorder, or
collapse its phases. Its heart is the triage that every candidate must survive
before it may touch the seed — the **three hard gates**: **agnosticism** (would
this help an arbitrary next project that never heard of this plant?),
**durability** (will this still be true a version from now, or is it pinned to
one release?), and **non-redundancy** (does the seed *already* own this rule —
open its would-be home and read it before proposing an echo?). A single leaked
project-specific or version-pinned detail — anywhere, the CHANGELOG and
harvest-log included — or a second home bolted onto a fact the seed already
owns is a failed harvest. Deliver the fold-back as a reviewable proposal with
the node's harvest summary; I ratify before anything merges into the seed.

Keep the seed strictly project-agnostic throughout: it is the inheritance of
every future plant, and what goes back in must be true for all of them.
