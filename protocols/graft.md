---
name: graft
description: The distribution arm of the cross-project meta-loop, and the complement of harvest. Once harvest has folded a mature plant's generalizable lessons back into the seed, graft carries that enriched seed OUTWARD onto an existing, already-grown plant — re-propagating the evolved kernel, protocols, skills, agents, templates, and shared tooling, and refreshing the plant's own library/tool pages from the seed's now-richer corpus — so a plant that grew from an older seed inherits the fruits of every harvest since, without being regrown from scratch. It upgrades a plant's SEED-OWNED machinery only; the plant's own life — its source code and the knowledge facts it authored — stays exactly as the plant left it. TRIGGER IS USER-DECIDED — the user starts a graft, or the system at most PROPOSES that a plant is due for one (typically right after a harvest lands). Every upgrade is additive, backed up, and reversible; graft proposes the reconciled result and the steward ratifies before it is applied. A local divergence the plant made to its own machinery is preserved, never overwritten, and surfaced back as a harvest candidate.
id: protocol.graft
tier: 2
kind: protocol
origin: seed
title: graft — carrying the enriched seed onto an existing grown plant, additively and reversibly
owns:
  - graft.reconcile-flow
  - graft.user-sovereignty
  - graft.pure-graph-mandate
requires:
peers:
  - protocol.harvest
  - protocol.grow
load_when:
  - "upgrade this plant to the newer seed"
  - "graft the seed, re-propagate machinery"
  - "plant grew from an older seed version"
  - "reconcile local machinery divergence"
est_tokens: 10000
---

# Protocol: graft

`grow` runs the seed into a **new** project. `harvest` runs the other way — a
mature plant back into the seed — so the next plant starts ahead of where this
one did. `graft` closes the third side of the triangle: it carries the enriched
seed **outward onto an existing plant**, so a plant that was grown from an older
seed inherits everything the seed has learned since — without being torn up and
regrown.

The metaphor is load-bearing. In the garden you do not uproot an established,
fruiting plant to give it a better cultivar's traits — you **graft** the new
scion onto the living rootstock, and the plant keeps its roots, its trunk, and
its own fruit while gaining the new growth. Here the rootstock is the plant's
own life — its source code and the knowledge it authored about itself — and it
is inviolate. The scion is the seed's evolved machinery: the kernel, protocols,
skills, agents, templates, shared tooling, and the library/tool corpus. Graft
fuses the new machinery onto the living plant and leaves the plant's own life
exactly where the plant left it.

Harvest and graft are one circulatory system. Harvest is the **collection** arm
— it draws one plant's generalizable lessons up into the seed. Graft is the
**distribution** arm — it pushes the enriched seed back out to every sibling
plant. A seed that only harvests hoards its improvements in one place; a seed
that also grafts lets one plant's lesson reach all the others. That reach is the
whole point: **enrich the other plants with the fruits of the harvest.**

## Trigger — user-decided; the system proposes, the steward starts

Like harvest, graft is **user-sovereign**. It changes an established, possibly
production plant, so a human — the **steward** (the user acting as the plant's
owner; the two words name the same person) — decides when a plant is upgraded
and ratifies the result before it is applied.

- **The user starts it** — by invoking this protocol or pasting `GRAFT_PROMPT.md`
  with a plant (or a set of sibling plants) as the target.
- **The system may PROPOSE it** — most naturally as the tail of a `harvest`:
  when a harvest has just enriched the seed, an agent may observe "the seed now
  carries fruit that plants X, Y, Z predate — each is due for a graft" and stop.
  The proposal is a doorbell, not an entry.
- **Every upgrade is ratified before it lands.** Graft reconciles, then proposes
  the result; the plant's steward reviews the reconciled diff and ratifies. An
  unratified graft is a draft. Because every replacement is backed up first, a
  ratified graft is also reversible.

## When to invoke

- The **user** has asked to graft a plant, or ratified a proposal to.
- The plant is **grown and steady** — its graph routes, its own plan-of-record
  is closed or calm. Grafting mid-churn mixes a machinery upgrade into unrelated
  in-flight work and muddies both; let the plant reach a quiet point first.
- The seed has **moved on since the plant grew from it** — a harvest folded in
  new fruit, a protocol sharpened, a skill gained a rule, the corpus grew pages
  for libraries this plant already uses. The wider the gap, the more the plant
  has to gain.
- The plant's working tree is **clean** (or the steward accepts a backup-only
  safety net), so the additive upgrade and its automatic backups are easy to
  review and to unwind.

## The rootstock line — the heart of this protocol

Harvest's heart is the agnosticism gate: *nothing project-specific enters the
seed.* Graft's heart is its mirror, the **rootstock line**: *nothing the plant
authored about itself is overwritten by the upgrade.* Draw it once and hold it
through every phase.

Two territories, and graft writes to exactly one of them:

- **Seed-owned machinery (graft's to upgrade).** The artifacts the seed installs
  and continues to own: the kernel (`CLAUDE.md` / `AGENTS.md` /
  `.github/copilot-instructions.md` ← the seed's `core/AGENTS.md`); the
  seed-owned graph subtrees
  `docs/graph/{protocols,skills,agents,method,templates}/` — every node in them
  marked `origin: seed` (the protocols, the skills, the agent roster, the
  method/posture nodes, and the Tier-3 template artifacts: the delegation
  briefs, the graph-session-bootstrap block, the handback payload, the artifact
  templates); the harness projections of agents and skills (`.claude/agents/`,
  `.claude/skills/`, the `.prime/agent/`, `.opencode/` and `.codex/`
  equivalents, and `.github/`'s transformed views); the tool-specific commands,
  settings, and
  hooks; the shared router script `docs/graph/agent-lint.py` (also projected
  to `.claude/agent-lint.py` on Claude Code installs); and the graph engine
  scripts `docs/graph/{graph-lint.py,spec-lint.py}` — preserving the
  plant's configured `TEST_GLOBS`. Graft carries the seed's newest version
  of these onto the plant. `_schema.md` and `index.md` are NOT in this
  list — they are project-instantiated and stay the plant's (see the
  engine-vs-instance rule below).
- **The plant's own life (graft preserves, always).** The rootstock: the plant's
  application source, and every knowledge fact the plant authored under
  `docs/graph/` — its `nodes/`, `specs/`, `decisions/`, `libraries/`, `plans/`,
  `runbooks/`, product, architecture, API, and data collections, any graph node
  **without** `origin: seed`, and the pinned, version-specific facts in its
  library and tool pages.
  Graft reads this territory to understand the plant and to place refreshed
  surface knowledge accurately; it treats every fact in it as the plant's to
  keep.

> **The rootstock line:** the plant's source and its authored `docs/graph/`
> facts stay as the plant left them. If an upgrade cannot land without rewriting
> something the plant authored about itself, it stops at the line and becomes a
> proposal for the steward — never a silent overwrite.

The one nuance worth stating plainly: a plant's library and tool **pages** live
in `docs/graph/` and are plant-owned, yet graft may refresh their *surface* from
the enriched corpus (Phase 4). That refresh honours the line by construction —
it renews only the version-durable orientation layer and re-pins the plant's
version-specific facts fresh against the plant's real lockfile, so no pinned
fact the plant discovered is ever lost. Renewing the orientation is a graft;
overwriting a pin is not.

## The pure-graph mandate — every graft leaves the plant more purely a graph

The rootstock line is graft's conservative heart: *preserve what the plant
authored.* The pure-graph mandate is its reconstructive heart: *every graft
leaves the plant closer to the seed's architecture than it found it.* The two
are complements, not tensions — the mandate refactors **structure, placement,
and projection**; the rootstock line guarantees the **facts themselves** are
never lost in the move.

The seed's architecture (6.0.0) is a **pure graph**: everything that can
activate progressively is a routable `docs/graph/` node; nothing about how to
work is always-loaded except a small bootstrap kernel; every tool-dir surface
is a *generated projection* of a node, not a hand-maintained copy; each fact has
one home; and no obsolete era, duplicate home, or competing doctrine survives.
Anywhere a plant falls short of that — machinery still living outside the graph,
a fact with two homes, an always-loaded file that should be a node, a
hand-maintained projection drifting from its source, dead compatibility residue —
**it is a drift from the spec, and closing it is in graft's scope.** Graft does
not merely fast-forward files onto a plant frozen in an older shape; it drives
the plant, end to end, toward maximal pure-graph.

Graft executes that drive as the **holistic reconstruction** the seed's own
rebalancing doctrine prescribes, bounded by the rootstock line:

- **Reconstruct from evidence, not preference.** Inventory the plant's drift
  from the pure-graph spec as a ledger — each item with its location, the
  invariant it breaks, its natural graph home, and its confidence — before
  moving anything.
- **One home, natural owner.** Move each responsibility and fact to the node
  that should own it; collapse duplicate and competing homes into one;
  trim every restated fact to a cross-reference.
- **Integrate, don't bolt on.** Every relocation is a holistic MERGE (Phase 3's
  discipline), not a copy — a block that reads as "bolted beside" the nodes it
  sits among has not been reconstructed.
- **Minimum-sufficient, sliced, reversible.** Rebalance in coherent slices that
  keep the plant routable throughout; each slice earns its change, preserves
  observable behavior, and lands in the ratifiable proposal with a backup.
- **Verify and fix the drift at its home.** Prove each slice with the graph's
  own fitness functions (`graph-lint.py`, one-home checks, router compactness),
  and where a projection drifted, regenerate it from its node rather than
  hand-patching the copy.

The pre-6.0 **layout migration** below and its knowledge fact-sweep (step (f))
are the *maximal instance* of this mandate — a plant that predates the graph
needs the whole reconstruction. But the mandate is **standing**: even a plant
one version behind gets audited for drift and rebalanced toward purity as
**Phase 6**, every graft. A graft that only swaps machinery versions and leaves
a structurally-drifted plant structurally drifted has upgraded the scion and
neglected the tree.

## The three-way reconciliation — how the machinery is upgraded

A plant is not a blank target. Since it grew, its steward may have locally
sharpened a protocol, adjusted a setting, or fixed a script — the very kind of
divergence a future `harvest` exists to pull back. Graft respects that work by
reconciling three versions of every seed-owned artifact, exactly as a
well-behaved merge does:

- **base** — the seed revision the plant grew from (read from the plant's seed
  stamp; reconstructed from install backups or content lineage on a first graft;
  see *Provenance & the seed stamp* below);
- **theirs** — the artifact in the seed today;
- **ours** — the artifact as it currently stands in the plant.

Each artifact then takes one of three clean paths:

- **FAST-FORWARD** — the seed advanced and the plant left the artifact
  pristine. Adopt the seed's new version outright. This is the common case and
  the bulk of a graft's value.
- **KEEP-PLANT (and flag upstream)** — the plant diverged and the seed did not.
  Keep the plant's version untouched, and record the divergence as a **harvest
  candidate**: the plant improved its machinery, and that improvement may deserve
  to flow back into the seed for everyone. Graft's outbound pass thus feeds the
  inbound loop.
- **MERGE** — both the seed and the plant advanced the same artifact. Reconcile
  them as a single **holistic re-integration** (the seed's own "integrate, don't
  patch" principle): produce one coherent file that carries the seed's new
  capability *and* preserves the plant's intent, and surface it to the steward as
  a reviewable proposal. A three-way conflict is a decision, and the decision is
  the steward's.

## The flow

Orchestrated like `grow` and `harvest`: the session plans, briefs, reconciles,
and delivers; clean-context workers survey and author. Model policy is strict —
**Sonnet-class** workers survey and classify (read-only); **Opus-class** workers
perform every reconciliation, holistic merge, corpus refresh, and validation.

Every spawned worker executes the canonical GRAPH DISCIPLINE block of
`docs/graph/templates/prompts/graph-session-bootstrap.md` (the one home for
the worker discipline — briefs embed it; this file only points at it) and
returns the `--plan` command, the loaded closure, and its deliberate skips. Where the host supports
model-class selection and clean-context spawning, honour it; if it cannot, report
that this host cannot execute the seed's operating model rather than collapsing
the work into the main chat.

### Phase 1 — Locate the plant and establish the base (session + Sonnet)

Identify the plant or the set of sibling plants in scope, and for each record
its path, host integration (`.claude/` / `.prime/agent/` / `.opencode/` /
`.codex/` / `.github/`),
current branch, HEAD, and worktree cleanliness — as provenance, without mutating
Git. Read the plant's **seed stamp** to learn the base version it carries; on a
first graft where no stamp exists, reconstruct the base from install backups
(`*.bak-*`) or from content lineage against tagged seed revisions, and note that
the stamp will be established by this graft. Confirm the seed's own version and
what has changed between base and now (its CHANGELOG and harvest log are the map
of available fruit). A clean working tree here makes the whole upgrade easy to
review and to unwind.

### Phase 2 — Survey the drift (Sonnet scouts, read-only)

Dispatch read-only scouts to inventory every seed-owned artifact installed in
the plant and classify its three-way state (base vs. theirs vs. ours) as a first
guess at FAST-FORWARD / KEEP-PLANT / MERGE. In parallel, inventory the **fruit
the plant can withdraw**: the libraries, tools, and — where the plant is subject
to externally-authored rules — the legal instruments the plant actually reasons
against (from its `docs/graph/libraries/`, `docs/graph/tools/`, and
`docs/graph/legal/`) for which the seed's `library-corpus/`, `tool-corpus/`, or
`legal-corpus/` now holds a page the plant predates or lacks.
Return a **graft ledger** — one row per artifact or withdrawable page, with
provenance (plant path, seed source, base state) and a candidate class. Claims
cite paths; centralized prose is an untrusted clue until corroborated against the
installed files.

### Layout migration: 5.x → 6.0.0 (between survey and reconcile)

The survey may find a **pre-6.0 plant**: its machinery lives in the old
tool-dir layout — `.claude/protocols/`, `.claude/templates/`, `.claude/core/`
(and the `.opencode/` / `.codex/` / `.github/` equivalents) — instead of the
graph subtrees `docs/graph/{protocols,skills,agents,method,templates}/`. Such a
plant is not fast-forwarded file-for-file; it is **migrated**, and the
migration threads through the phases that follow:

- **(a) Install the new machinery into `docs/graph/` as usual.** The installer
  places the seed's current protocols, skills, agents, method nodes, and
  template artifacts as `origin: seed` graph nodes, and regenerates the
  agent/skill harness projections. Phase 3's reconciliation then runs against
  these new homes.
- **(b) Diff the old tool-dir copies against their seed base — the plant's
  customizations must survive the move.** Each old copy under
  `.claude/protocols/`, `.claude/templates/`, `.claude/core/` (and kin) is
  three-way-compared against the seed revision the plant grew from. A pristine
  copy needs nothing; a **plant-local customization** is carried into the
  corresponding graph copy as a holistic MERGE (Phase 3's discipline), so the
  new layout arrives already carrying the plant's intent. And exactly as this
  protocol already holds for KEEP-PLANT: a local divergence is also a
  **harvest candidate** — hand it back that way.
- **(c) Relocate the plant's OWN agents and skills into the graph too,
  holistically reconciled — not just tagged and moved.** A 5.x plant's
  *plant-authored* machinery — the experts and project skills it grew
  (`origin: project`, not seed-owned) — sits in the harness dirs
  (`.claude/agents/*.md`, `.claude/skills/<name>/SKILL.md`) with no
  `docs/graph/` home. The 6.0.0 layout is where **every** agent and skill node
  lives, seed-owned or plant-owned, so a plant left with its own agents/skills
  in the old spot is half-migrated: the router cannot route them, and
  graph-lint cannot see them. But relocating is not reconciling. Promote each
  into `docs/graph/{agents,skills}/`, adding the node frontmatter it lacks
  (`id`/`tier`/`kind`/`origin`/`title`/`owns`/`est_tokens`, reusing an agent's
  `routing_triggers` as its `load_when`) — then read its content against the
  rest of the graph, because a plant-authored expert that predates the graph
  was written with no graph to defer to and will almost certainly restate
  facts the graph's crosscut/platform/subsystem nodes already own (an auth
  mechanism, a secrets inventory, a platform topology). Trim every restated
  fact to a genuine cross-reference — name the owning node, don't re-explain
  it — keeping only the routing charter and the facts this node is the true,
  sole home of: exactly the treatment Phase 3 gives a MERGE. Regenerate the
  `.claude/` projection from the reconciled home so the two stay
  byte-identical. A relocated-but-unreconciled expert is rootstock in name
  only: it reads as a "seed block bolted beside a plant block" the moment it
  sits next to nodes it duplicates, actively working against
  one-home-per-fact rather than joining it — which is why this step is
  Opus-class work, not a mechanical copy. The result is additive and lands in
  the ratifiable proposal like every other migration step.
- **(d) List the now-redundant old machinery; the STEWARD confirms deletion.**
  Once the graph homes and projections exist, the old tool-dir copies are
  redundant. Graft lists every such file and asks the steward to confirm their
  deletion **explicitly, by name** — it never deletes them itself (deletion
  requires an explicit confirmation naming the resource, per the kernel's
  boundaries). Until confirmed, they stay in place, inert.
- **(e) Rewrite stale references in plant-authored docs only with consent.**
  Plant-authored pages may cite the old paths (`.protocols/x.md`,
  `.skills/<name>/SKILL.md`, `.templates/…`, `.core/operating-principles.md`).
  Rewriting them to the `docs/graph/…` homes touches the rootstock, so graft
  first lists **every file it would touch** with the exact rewrites, and
  proceeds only on the steward's consent — never as a silent sweep.
- **(f) Sweep the plant's own pre-graph knowledge — a migration this old owes
  a fact-sweep, not just a machinery swap.** A plant old enough to predate the
  graph architecture entirely was never run through `adopt-existing` or
  `ingest-library`: its real, load-bearing knowledge — deploy-pipeline docs,
  per-repo READMEs, sharp edges recorded only in a comment, drift between what
  a config claims and what the code does — has had nowhere to land and was
  never captured. Finishing (a)–(e) leaves the graph *structurally* current
  (the router works, the machinery is in place) while leaving it
  *substantively* thin — a plant whose facts still mostly live outside the
  graph structure, in the repos the graph is supposed to orient a reader away
  from re-reading. Dispatch read-only scouts across the plant's actual source
  — not just its machinery — to inventory facts missing from the graph,
  cross-checked against what existing nodes already own so nothing
  already-covered is re-reported, then hand confirmed findings to Opus
  authors to weave (never append) into the owning node. This sweep is **part
  of the migration** for any plant old enough to have predated the graph, not
  an optional follow-on task the steward has to separately request — a
  migration that upgrades the machinery and stops there has moved the
  furniture without unpacking the house.

The migration's outcome feeds Phase 7 unchanged: the audit runs over the
backups, the redundant-copy list and any un-consented reference rewrites appear
in the proposal, and the stamp records the plant as a 6.0.0-layout plant.

### Phase 3 — Reconcile the machinery (Opus authors)

For each seed-owned artifact, apply the three-way reconciliation above and
produce the upgraded result: adopt on FAST-FORWARD; retain and raise a harvest
candidate on KEEP-PLANT; author one holistic re-integration on MERGE. Every
merged file arrives whole, integrated as if it had always read that way — never a
seed block bolted beside a plant block. Each reconciliation records its
provenance: base state, decision, and what the plant kept.

**The roster delta is not spawnable in this session.** Reconciling the agent
nodes rewrites the harness projection, but the host enumerated that directory
before this graft ran — so every specialist the seed *added or renamed* since the
plant's base is on disk and unspawnable for the phases that follow. Preflight
before dispatching by name, and take the remedy or the recorded fallback in
`docs/graph/method/delegation.md` (`delegation.harness-registration`). Carry the
delta forward as a named list; Phase 7 reports it.

**The graph engine is machinery too — and the installer will not fast-forward
it.** The installer drops the knowledge-graph scaffold (`graph-lint.py`,
`spec-lint.py`, `_schema.md`, `index.md`) *only if absent*, so a plant that
already has them keeps its OLD engine across a graft and silently misses every
linter improvement since it grew. (The agent router `docs/graph/agent-lint.py`
is the exception: it carries no project config, so the installer fast-forwards
it like any machinery file — identical untouched, changed backed up for the
audit — and it needs no engine-style reconciliation.) **A graft that leaves a plant on a stale graph
engine is not a true upgrade.** Reconcile the engine explicitly, as a
config-preserving fast-forward: adopt the seed's current engine body and
re-inject the plant's own PROJECT CONFIG (`ROOT_ID` / `KINDS` / `KIND_PREFIX` in
`graph-lint.py`; `TEST_GLOBS` in `spec-lint.py`) — the plant gains the engine, keeps
its configured identity, and a knob it predates adopts the seed default. **A
config knob the seed has *extended* since the base is UNIONED, not re-injected
wholesale.** The load-bearing case is `KINDS`: 6.0.0 added the machinery kinds
`protocol`/`skill`/`agent`/`method`, so keeping the plant's older `KINDS` set
verbatim would drop them and every newly-installed machinery node would fail
lint with `kind not in KINDS`. The union keeps the plant's own kinds *and* adds
the seed's new members; only a scalar identity (`ROOT_ID`) or a plant-list
(`TEST_GLOBS`) is kept wholesale. Where the
plant's engine is a strict *superset* of the seed's, that is a KEEP-PLANT (the
plant is ahead) and a harvest candidate. `tools/graft-graph-engine.py` performs
exactly this merge (set-valued knobs unioned, others kept wholesale) and the
superset detection; `_schema.md` and `index.md` stay
the plant's (they are project-instantiated — copying the seed template would
regress placeholders and wipe the authored router).

**The installer fast-forwards blindly, so reconciliation is only real if it is
audited.** The installer overwrites every seed-owned machinery file with a
per-file backup but does **not** check whether the file it replaces carried a
plant customization first — so a FF can bury a local divergence (recoverable from
the `.bak`, but invisible). The reconcile-before-overwrite promise is therefore
kept by a **mandatory post-FF audit** (Phase 7, `tools/graft-audit.py`): any
seed-owned file whose backup differs from the seed *and* carries plant-signal
content is a divergence that must be re-integrated into the FF'd file or ratified
— never left buried.

### Phase 4 — Refresh the plant's knowledge from the corpus (Opus authors)

For each withdrawable library/tool page from Phase 2, **seed the refresh from the
corpus as the orientation layer**, exactly as `ingest-library` and `toolcraft`
do for a new plant — then re-pin the plant's version-specific facts fresh against
the plant's real lockfile. The plant keeps every pinned fact it discovered; it
gains the enriched, version-durable surface the corpus now holds. Where the plant
has no page yet for a library it uses that the corpus covers, propose growing one
from the corpus orientation plus a fresh pinned delta.

A withdrawable **legal** page refreshes the same way with one added, non-negotiable
step: the corpus carries the citation, never its currency. Re-confirm each entry's
`verified` date and `legal_status` against the publisher before the plant relies on
it, and never copy a determination — the plant authors its own application of the
rule. A corpus entry whose currency cannot be re-confirmed is refreshed as
orientation only, and said to be such.

**One home per dependency — merge into the plant's existing page, never add a
parallel one.** When the plant already has a page for the dependency, the refresh
**merges the corpus orientation into that existing page** (fold in whatever
generic orientation the plant's page lacks; keep every pin and sharp edge it
already carries) — it does **not** create a second page. In particular, **do not
mirror the corpus's own internal grouping into the plant.** The corpus may file a
page under a sub-namespace (e.g. `library-corpus/container/docker.md`); that
grouping is a seed-side organizational detail, not a path to replicate. Dropping
it in beside the plant's flat `libraries/docker.md` produces two homes for the
same dependency — a one-home-per-fact violation the graft itself created — and
the minimum-sufficiency gate (Phase 7) BLOCKS on exactly that duplicate. The
corpus page's *content* lands in the plant's existing page; the corpus page's
*location* stays in the corpus. This is the fruit reaching
the plant: harvest lifted the surface up into the seed, and graft lets this plant
withdraw it. Adopt a portable corpus tool only when the plant's stack matches;
otherwise treat the page as a blueprint and re-author against the plant's stack,
test-first.

### Phase 5 — Grow the new capabilities onto the living plant (Opus authors)

Fast-forwarding the machinery *carries* a capability to the plant; it does not
*grow* it there. A refreshed protocol, a new skill template, a new runbook
template, a corpus tool the plant's stack could use — each arrives as inert
machinery. **Grafted is not grown.** This phase closes that gap: for each new or
newly-enriched capability the graft delivered, grow it onto the plant **where
doing so is appropriate and necessary** — actualized into the plant's living
skills, tools, and knowledge, not left sitting as a template.

- **Grow what the plant evidently needs, grounded in its own facts.** Instantiate
  a suggested skill or expert the plant's real stack calls for (the
  `skill-corpus` / `agent-corpus` withdraw contract, into `docs/graph/skills/` /
  `docs/graph/agents/`, with the harness projections regenerated from them),
  withdraw a corpus library/tool page the plant actually uses, withdraw a
  `legal-corpus` instrument the plant is genuinely subject to (currency
  re-confirmed, per Phase 4),
  or ground a runbook the plant can now fill from its own deploy/release nodes.
  Every grown addition is anchored in evidence already in the plant's graph — its
  references resolve inside the plant, never at a seed-corpus path.
- **Never fabricate to fill a surface.** A capability whose content can only come
  from the plant's real, recurring use — a project skill for a procedure that has
  actually recurred, an ADR for a decision actually taken, a runbook's real
  commands — is **not** manufactured here. The seed's own anti-fabrication
  discipline (the `adr-writer` "don't invent a decision" and `grill-planner`
  "mark what you haven't verified" rules) applies to every surface: thin evidence
  is a reason to defer, not to invent. These sprout during real use, owned by the
  close-out lifecycle (`canonize` → `docs-librarian`), not by the graft.
- **Surface what was grafted but not grown.** Report every capability now present
  as machinery yet still inert — no project skill sprouted, runbook templates
  still unfilled, a corpus page not yet withdrawn — so the steward sees the
  copy-but-not-actualized state plainly, and knows which items were grown now
  (grounded) versus deferred to real use (ungrounded). A silent inert capability
  reads as "delivered" when it is only "installed."
- **Own-kernel plants still receive the substance — as a weave, not a
  summary.** A plant that deliberately carries no seed machinery — its own
  instruction system is the rootstock — is not exempt from the upgrade. Its
  machinery classes as KEEP-PLANT, but the seed's substantive delta since the
  plant's base is **re-woven** into the plant the same way the seed itself
  carries it: map each seed surface the delta changed to the plant's
  equivalent surface (the seed's verify discipline → the plant's validation
  playbook; the reviewer's checks → the plant's change guide; the kernel
  posture → the plant's instruction file; a template rule → the plant's
  matching template or convention), and land each rule where it acts, in the
  plant's idiom, sized to its budget. Collapsing the delta into one summary
  section of one file is a photocopy, not a graft — the plant's operating
  surfaces would keep steering every session exactly as before. The weave
  lands as a ratifiable proposal like any other rootstock-adjacent change,
  but it must exist, authored surface-by-surface, before the graft may
  close: a stamp advance with the substance undelivered is bookkeeping
  wearing an upgrade's name.

### Phase 6 — Rebalance the plant toward pure graph (Sonnet audit → Opus authors)

The reconstruction pass. Carrying the pure-graph mandate above, drive the plant
end to end toward the seed's architecture — on **every** graft, not only a
legacy-layout migration. The 5.x→6.0 layout migration and its fact-sweep (step
(f)) are this phase's maximal instance; a plant already on the 6.x layout still
runs it, lighter.

- **(1) Inventory the drift (Sonnet scouts, read-only → a rebalance ledger).**
  Audit the plant against the pure-graph spec and record each shortfall with its
  location, the invariant it breaks, its natural graph home, and confidence.
  Hunt the standing drift classes:
  - **machinery outside the graph** — any protocol/skill/agent/method content, or
    any always-loaded instruction the kernel need not carry, that lives somewhere
    other than a routable `docs/graph/` node;
  - **a fact with two homes** — the same rule, topology, or contract stated in
    two nodes, or in a node *and* a hand-maintained projection/summary;
  - **a hand-maintained projection** — a tool-dir command, prompt, or view that
    was hand-edited instead of generated from its node, and has drifted from it;
  - **obsolete residue** — a superseded era's file, a dead compatibility shim, a
    tombstone with no pointer, a stale index/topology entry;
  - **substantive thinness** — real, load-bearing plant knowledge (deploy docs,
    per-repo READMEs, comment-only sharp edges) still living outside the graph
    structure (the (f) sweep, now standing).
- **(2) Reconstruct in slices (Opus authors), bounded by the rootstock line.**
  Move each item to its natural node home as a holistic MERGE — never a copy;
  collapse duplicate homes into one and trim restated facts to cross-references;
  regenerate a drifted projection from its node rather than hand-patching it;
  and list obsolete residue for the steward's explicit deletion confirmation
  (graft never deletes unprompted). Every relocation preserves the fact itself —
  the rootstock line holds; a fact the plant authored is re-homed, never lost —
  and each slice keeps the plant routable so the upgrade stays reversible.
- **(3) Leave the drift closed at its home.** Where the shortfall was a missing
  fitness function the seed now ships, install it; where it was a projection that
  drifted, the regeneration is the fix. The plant should end the graft at least
  as purely a graph as the seed's spec requires, with any residue that could not
  be closed this pass surfaced with a remediation, not silently carried.

Split across parallel Opus authors when the rebalance is large; that parallelism
is exactly what the Phase 7 cross-author rebalance gate exists to reconcile.

### Phase 7 — Apply, verify, and stamp (Opus authors; session gates)

Apply the ratified upgrade **additively**, backing up every replaced file first
(the installer's backup behaviour is the safety net; rely on it and confirm the
backups exist). Then prove the plant is left more capable and no less itself:

- **Rootstock intact** — confirm the plant's source and its authored
  `docs/graph/` facts are byte-for-byte unchanged outside the machinery and the
  deliberately refreshed library/legal/tool surfaces. Any unexpected change to the
  plant's own life BLOCKS.
- **Customization audit (the reconcile-before-overwrite gate)** — run
  `tools/graft-audit.py <plant> <seed> --tokens=<plant tokens>
  --engine=<plant>/docs/graph/graph-lint.py` over the fresh
  backups. Every seed-owned file whose backup differs from the seed *and* carries
  plant-signal content is a divergence the blind FF overwrote; each must be
  re-integrated into the FF'd file (holistic MERGE) or explicitly ratified. An
  un-reintegrated, un-ratified customization BLOCKS — a buried divergence is the
  one failure the installer cannot catch on its own.
- **Kernel current (the always-loaded bootstrap)** — the plant's kernel body
  (`AGENTS.md` / `CLAUDE.md`, resolving the shared symlink) must be byte-equal to
  the seed's `core/AGENTS.md`. The kernel loads on every session of every
  adapter, yet `place_kernel` shares the two files by symlink and once left a
  STALE body behind (with no `.bak`, so the customization audit was blind to it):
  the audit's kernel-currency check (`tools/graft-audit.py`) now asserts it
  directly, and a stale kernel BLOCKS — fast-forward the kernel body (re-run the
  installer for each adapter the plant uses; a plant that runs Prime Agent, all
  its `.claude`/`.codex`/`.opencode`/`.github`/`.prime` adapters must each be
  grafted, none silently skipped) and re-project the plant's own agents/skills
  into any adapter that lacks them.
- **Machinery healthy** — the plant's graph still routes
  (`python3 docs/graph/graph-lint.py` and a representative `--plan`) **on the
  upgraded engine** (the audit's engine-currency check reports no seed engine
  line missing from the plant — else reconcile with `tools/graft-graph-engine.py`),
  the agent router lints and evals clean (`python3 docs/graph/agent-lint.py --lint` /
  `--eval` where installed), and internal links and edges resolve. Report the
  **roster delta** Phase 3 carried forward — the specialists added or renamed by
  this graft — as work the plant's next session registers, not as something this
  session verified spawnable (`delegation.harness-registration`).
- **Minimum-sufficient upgrade (the graft reviewer)** — audit what this graft
  *added* against the seed's minimum-sufficient-work posture
  (`docs/graph/method/engineering-posture.md`). Fast-forwarding seed-owned machinery
  is the contract; everything beyond it must earn its place: every capability
  grown in Phase 5 cites the plant evidence that demanded it, every MERGE is
  the smallest re-integration that preserves both intents (never a larger
  rewrite than the conflict required), every refreshed page serves a library
  or tool the plant actually uses, and no artifact lands that nothing in the
  plant consumes. Over-delivery is a finding, not a bonus: an unconsumed
  artifact, a capability grown on thin evidence, or a duplicate home for a
  fact the plant's graph already owns BLOCKS that item (the rest of the graft
  may proceed).
- **Pure-graph integrity (the rebalance gate)** — the plant must end the graft
  at least as purely a graph as the seed's spec requires. Assert the Phase 6
  rebalance actually closed its ledger: no seed-class machinery or superfluous
  always-loaded instruction remains outside a `docs/graph/` node; no fact has
  two homes (a node-and-projection or node-and-node duplicate); every tool-dir
  command/prompt/view matches what regenerating it from its node would produce
  (drifted, hand-edited projections BLOCK — regenerate, don't patch); and no
  obsolete-era residue lingers unlisted. Any residual drift that could not be
  closed this pass is surfaced in the proposal with a remediation and a reason —
  never silently carried. A graft that swapped versions but left the plant
  structurally drifted has not met this gate.
- **Cross-author rebalance (only if reconciliation/growth/rebalance/(f) used parallel
  authors)** — a large migration, rebalance, or fact-sweep is real parallel
  work: Phase 3, 4, 5, 6, and (f) each split across multiple Opus authors with disjoint file
  ownership, because that's what makes the absorption tractable. But disjoint
  ownership means nobody owned cross-file consistency. Two failure modes are
  near-guaranteed and neither shows up as a lint error: a shared summary file
  (an `index.md` node table, a `root.md` topology map) that no single author's
  file list covered drifts stale the moment any author changes something it
  depended on; and the same fact ends up restated in two files each author
  touched independently, since neither saw the other's edit. Run **one** final
  docs-librarian spawn — seeing the whole graph at once, the way disjoint
  authors structurally cannot — to catch both: one-home-per-fact violations
  introduced across author boundaries, register drift (a passage that reads
  as bolted-on rather than woven), and any shared index/summary file gone
  stale. Follow it with a structural audit, pass/fail per node, for what
  `graph-lint.py` cannot see (it validates that edges *resolve*, not that they
  make *sense*): is every node's `kind` the right one, does the plant's
  topology map list every node the migration or sweep added, and does every
  `requires:`/`peers:` edge reflect what the node's own body actually depends
  on. A green `graph-lint` proves the graph is well-formed; it does not prove
  a parallel absorption reconciled correctly, and skipping this step because
  the linter passed is exactly the gap it exists to close.
- **Stamp + provenance** — record the seed version the plant now carries in its
  seed stamp, and add a provenance entry to the plant's own `docs/graph/changelog.md`
  naming the graft. A gate that runs but asserts nothing is a green lie; each
  check names its command and result.

### Phase 8 — Deliver (propose, then ratify)

Graft **proposes**; the plant's steward **ratifies**. Emit the reconciled
upgrade as a reviewable patch/proposal with the graft summary below. Hand the
KEEP-PLANT divergences back as harvest candidates, closing the loop the other
way. End with the single highest-leverage next step.

## Provenance & the seed stamp

A plant that knows which seed version it carries can be grafted cleanly forever
after, because every future graft has a real **base** for its three-way merge.
Graft therefore both reads and maintains a lightweight, **plant-owned** stamp —
a `.cypress/seed.json` marker or an equivalent line the plant's steward keeps —
recording the seed name, the version last grown-or-grafted in, and the date. On
the first graft of a plant grown before stamps existed, reconstruct the base as
best the evidence allows, then establish the stamp so the next graft starts from
certainty. The stamp is provenance the plant owns, not machinery the seed
overwrites; graft updates it as the last additive step of a successful upgrade.

## The relationship to grow, harvest, and canonize

- `grow` installs and grows a **new** plant from the current seed; graft upgrades
  an **existing** plant to the current seed. Grow starts from a blank target;
  graft starts from a living one and reconciles.
- `harvest` is inbound (plant → seed) and `graft` is outbound (seed → plant).
  They share the corpus withdraw contract from opposite ends: harvest fills the
  corpus, graft withdraws from it into an already-grown plant. A KEEP-PLANT
  divergence graft finds is precisely a harvest candidate — the two protocols
  hand work to each other.
- `canonize` keeps the plant's **project-specific** knowledge in the plant's own
  graph; graft never disturbs it. When graft refreshes a library/tool surface, it
  is renewing the orientation layer canonize and ingest-library maintain, and it
  leaves every pinned fact those protocols recorded in place.

## Output format

State the summary in the chat, and record a provenance entry in the plant's own
`docs/graph/changelog.md` (the seed is not modified by a graft).

```markdown
# Graft — <plant lineage id> — seed <base> → <new> — YYYY-MM-DD

## Fast-forwarded (adopted from the seed)
- <artifact> — base <state> → seed's current version

## Merged (holistic re-integration; steward-ratified)
- <artifact> — kept: <plant intent preserved> — gained: <seed capability added>

## Kept as the plant's (divergence preserved) → harvest candidates
- <artifact> — the plant's version stands; raised upstream because: <why it may be seed-worthy>

## Knowledge refreshed from the corpus
- <library/tool page> — surface renewed from corpus; version-specific facts re-pinned fresh

## Grown onto the plant (new capabilities actualized, grounded in plant facts)
- <skill/expert/runbook/page> — grown because <the plant's evidenced need>

## Grafted but not yet grown (inert machinery; deferred to real use)
- <capability> — present as machinery, ungrounded now; sprouts via <use / close-out>

## Pure-graph rebalance (Phase 6 — drift closed toward the spec)
- <drift item> — <class: machinery-outside-graph / duplicate-home / drifted-projection / obsolete-residue / thin-knowledge> → re-homed into <owning node> (fact preserved) / regenerated / listed for deletion
- Residual drift carried (with remediation): <item — why it could not close this pass>

## Pre-graph knowledge swept (migration (f); N/A if not a pre-graph plant)
- <fact> — found in <plant source path>, woven into <owning node>

## Integrity gate
- Rootstock intact (source + authored facts unchanged): PASS / BLOCK (<hit>)
- Kernel current (AGENTS.md/CLAUDE.md == seed core/AGENTS.md; every adapter grafted, none skipped): PASS / BLOCK (<stale kernel / skipped adapter>)
- Graph engine upgraded to seed's (or superset kept): PASS / FAIL (<lines / KEEP-PLANT>)
- Customization audit — no divergence buried by the FF: PASS / BLOCK (<file + signal>)
- Plant graph routes on upgraded engine / agent-router lint+eval: PASS / FAIL (<command + result>)
- Minimum-sufficient upgrade — every addition evidenced and consumed, merges minimal: PASS / BLOCK (<item + why>)
- Pure-graph integrity — plant ≥ the seed's pure-graph spec; no machinery outside the graph, no duplicate home, no drifted projection, no unlisted residue: PASS / BLOCK (<drift + home>)
- Cross-author rebalance + structural topology audit (if parallel authors used): PASS / FAIL / N-A (<librarian + audit result>)
- Host loads upgraded kernel: PASS / FAIL
- Backups present for every replaced file: PASS / FAIL
- New capabilities grown where appropriate; inert-but-grafted surfaced: PASS / FAIL
- Seed stamp updated: <base> → <new>; plant changelog provenance added

## Recommended next step
<single highest-leverage action — usually "ratify and apply", "graft the next
sibling plant", or "harvest the flagged divergence back into the seed">
```

## Quality bar

A graft that passes:
- Upgrades only seed-owned machinery and the deliberately refreshed library/tool
  surface, and leaves the plant's source and authored facts exactly as they were.
- Reconciles every artifact three-way — fast-forwarding cleanly, preserving every
  plant divergence, and re-integrating true conflicts holistically for the
  steward, including a relocated plant expert/skill trimmed to genuine
  cross-references rather than left restating facts the graph already owns.
- Upgrades the graph engine to the seed's current (plant config preserved) unless
  the plant's is a superset, and **audits** the fast-forward so no plant
  customization is silently buried.
- Withdraws the corpus fruit the plant is due, re-pinning the plant's own
  version-specific facts fresh so nothing pinned is lost, and sweeps a
  pre-graph plant's own knowledge into the graph as part of the same migration.
- **Grows** the newly-delivered capabilities onto the plant where evidenced and
  necessary, fabricates none, and surfaces every capability grafted-but-not-grown.
- **Rebalances the plant toward pure graph** (Phase 6) on every graft, not only a
  legacy migration: re-homes any machinery or fact living outside its node,
  collapses duplicate homes, regenerates drifted projections from their nodes,
  and lists obsolete residue — every move preserving the fact itself (the
  rootstock line), leaving the plant at least as purely a graph as the seed's
  spec, and surfacing any residual drift with a remediation.
- Delivers the seed's substantive delta even to a plant that carries no seed
  machinery — re-authored into the plant's own surfaces as a complete,
  ratifiable proposal, never a raw copy and never a bare stamp advance.
- Audits its own additions for minimum sufficiency: nothing grown without
  evidenced need, no artifact without a consumer, and the smallest
  reconciliation that preserves both intents
  (`docs/graph/method/engineering-posture.md`) — and, where the work was split
  across parallel authors, runs the single-spawn cross-author rebalance and
  structural topology audit that disjoint file ownership cannot self-check.
- Applies additively with a backup behind every replaced file, verifies the plant
  still routes and loads, and updates the seed stamp with dated provenance.
- Proposes for ratification and is reversible; the steward decides before it lands.

A graft that fails:
- Overwrites a fact the plant authored about itself, or a pinned library/tool
  version the plant discovered.
- Leaves the plant on a stale graph engine, keeps an extended set knob (e.g.
  `KINDS`) wholesale so newly-installed nodes fail lint, or lets the blind
  fast-forward bury a plant customization without auditing for it.
- Half-migrates a 5.x plant — leaves the plant's own agents/skills in the old
  harness-only layout instead of relocating them into `docs/graph/{agents,skills}/`;
  relocates them with frontmatter tagged on but content never reconciled
  against the rest of the graph (a "seed block bolted beside a plant block"
  restating facts the graph already owns instead of joining them); or drops a
  corpus page in as a *second* home beside the plant's existing page for that
  dependency instead of merging into it.
- Upgrades a pre-graph plant's machinery and calls it done without sweeping the
  plant's own real knowledge into the graph — leaving the router current while
  most of the plant's actual facts still live outside the graph structure.
- Swaps machinery versions but leaves a structurally-drifted plant drifted —
  machinery outside the graph, a fact with two homes, a hand-edited projection
  diverged from its node, or dead-era residue — instead of rebalancing it toward
  the pure-graph spec (Phase 6) and surfacing what could not close.
- Clobbers a plant's local machinery divergence instead of preserving it and
  flagging it upstream.
- Bolts the seed's new version beside the plant's instead of re-integrating a
  true conflict into one coherent file.
- Leaves a new capability as inert machinery without growing it where needed or
  surfacing it, or fabricates a skill/ADR/runbook to fill an empty surface.
- Closes on an own-kernel plant as a stamp advance with the seed's substance
  undelivered — "proposed" in name with nothing authored for the steward to
  ratify.
- Over-delivers: grows capabilities on thin evidence, pads the plant with
  unconsumed artifacts, or re-integrates a conflict with a larger rewrite than
  it required.
- Splits absorption across parallel authors for tractability, then never runs
  the single-spawn rebalance or structural topology audit afterward — shipping
  a stale shared summary file or a fact restated across two author-touched
  files, unnoticed because `graph-lint` only checks that edges resolve, not
  that they make sense.
- Applies without backups, or reports green without naming the command that ran.
- Mutates the plant before the steward has ratified the reconciled result.

## What stays out of scope

- Graft does not start on its own. It is user-decided; the most an agent does
  unprompted is *propose* a graft — typically as the tail of a harvest — and stop.
- Graft does not touch the plant's application source, run its application builds
  or test suites, or fetch/switch/commit/push its Git state. It records Git state
  as provenance and runs knowledge-and-machinery checks only.
- Graft does not rewrite the plant's authored `docs/graph/` facts, and it does not
  overwrite a pinned library/tool version the plant discovered; it renews only the
  version-durable surface and re-pins fresh.
- Graft does not modify the seed. A divergence worth flowing back is handed to
  `harvest`; graft only reads the seed and writes the plant.
- Graft does not collapse a three-way conflict by picking a side silently, and it
  does not apply an unratified reconciliation. The steward ratifies; the backups
  make it reversible.
