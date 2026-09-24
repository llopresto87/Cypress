---
name: graft
description: The distribution arm of the cross-project meta-loop, and the complement of harvest. Once harvest has folded a mature plant's generalizable lessons back into the seed, graft carries that enriched seed OUTWARD onto an existing, already-grown plant — re-propagating the evolved kernel, protocols, skills, agents, templates, and shared tooling, and refreshing the plant's own library/tool pages from the seed's now-richer corpus — so a plant that grew from an older seed inherits the fruits of every harvest since, without being regrown from scratch. It upgrades a plant's SEED-OWNED machinery only; the plant's own life — its source code and the knowledge facts it authored — stays exactly as the plant left it. TRIGGER IS USER-DECIDED — the user starts a graft, or the system at most PROPOSES that a plant is due for one (typically right after a harvest lands). Every upgrade is additive and proposed for ratification before it is applied; every replaced file is backed up by one canonical writer, and the unwind procedure, with the cases that are NOT recoverable named one by one, is stated in the protocol rather than assumed. A local divergence the plant made to its own machinery is preserved, never overwritten, and surfaced back as a harvest candidate.
id: protocol.graft
tier: 2
kind: protocol
origin: seed
title: graft — carrying the enriched seed onto an existing grown plant, additively and reversibly
owns:
  - graft.reconcile-flow
  - graft.user-sovereignty
  - graft.pure-graph-mandate
  - graft.migration
  - graft.integrity-gates
  - graft.reversibility
requires:
  - method.delegation
peers:
  - protocol.grow
  - protocol.harvest
  - protocol.deliver
  - method.engineering-posture
load_when:
  - "upgrade this plant to the newer seed"
  - "graft the seed, re-propagate machinery"
  - "plant grew from an older seed version"
  - "reconcile local machinery divergence"
  - "migrate a pre-6.0 plant out of the tool-dir layout into docs/graph"
  - "move a pre-7.0.0 plant's lifecycle status into frontmatter"
  - "this plant's plan-of-record is in a shape the seed has since changed"
  - "the graft audit reported a buried customization, a stale kernel, or an unmapped backup"
  - "undo a graft, restore a plant from the installer's backups"
  - "which installer flags are safe to use on a grown plant"
  - "does this upgraded plant carry the legal corpus, under which national jurisdiction"
  - "switch a symlinked plant back to copies before upgrading it"
prevents: An enriched seed that reaches no existing plant — improvements pile up in the seed while every grown project stays at the version it was installed at — and, when carried by hand instead, a plant's own customizations overwritten with no backup and no record.
est_tokens: 20079
---

# Protocol: graft

`grow` runs the seed into a **new** project. `harvest` runs the other way, a
mature plant back into the seed, so the next plant starts ahead of where this
one did. `graft` closes the third side of the triangle: it carries the enriched
seed **outward onto an existing plant**, so a plant that was grown from an
older seed inherits everything the seed has learned since, without being torn
up and regrown.

The metaphor is load-bearing. In the garden you do not uproot an established,
fruiting plant to give it a better cultivar's traits. You **graft** the new
scion onto the living rootstock, and the plant keeps its roots, its trunk, and
its own fruit while gaining the new growth. Here the rootstock is the plant's
own life, meaning its source code and the knowledge it authored about itself,
and it is inviolate. The scion is the seed's evolved machinery: the kernel,
protocols, skills, agents, templates, shared tooling, and the library/tool
corpus. Graft fuses the new machinery onto the living plant and leaves the
plant's own life exactly where the plant left it.

Harvest and graft are one circulatory system. Harvest is the **collection**
arm: it draws one plant's generalizable lessons up into the seed. Graft is the
**distribution** arm, pushing the enriched seed back out to every sibling
plant. A seed that only harvests hoards its improvements in one place; a seed
that also grafts lets one plant's lesson reach all the others. That reach is
the whole point: **enrich the other plants with the fruits of the harvest.**

## Trigger: user-decided; the system proposes, the steward starts (`graft.user-sovereignty`)

Like harvest, graft is **user-sovereign**. It changes an established, possibly
production plant, so the decision belongs to a human: the **steward**, the user
acting as the plant's owner, the two words naming the same person. The steward
decides when a plant is upgraded and ratifies the result before it is applied.

- **The user starts it**: by invoking this protocol or pasting
  `GRAFT_PROMPT.md` with a plant (or a set of sibling plants) as the target.
- **The system may PROPOSE it**: most naturally as the tail of a `harvest`:
  when a harvest has just enriched the seed, an agent may observe "the seed now
  carries fruit that plants X, Y, Z predate, each is due for a graft" and stop.
  The proposal is a doorbell, not an entry.
- **Every upgrade is ratified before it lands.** Graft reconciles, then
  proposes the result; the plant's steward reviews the reconciled diff and
  ratifies. An unratified graft is a draft. A ratified graft is unwound by the
  procedure in *Reversibility* below, which also names every case an unwind
  cannot reach, because a steward who believes an upgrade is reversible takes
  risks calibrated to that belief.

## When to invoke

- The **user** has asked to graft a plant, or ratified a proposal to.
- The plant is **grown and steady**, its graph routes, its own plan-of-record
  is closed or calm. Grafting mid-churn mixes a machinery upgrade into
  unrelated in-flight work and muddies both; let the plant reach a quiet point
  first.
- The seed has **moved on since the plant grew from it**: a harvest folded in
  new fruit, a protocol sharpened, a skill gained a rule, the corpus grew pages
  for libraries this plant already uses. The wider the gap, the more the plant
  has to gain.
- The plant's working tree is **clean**. This used to read "or the steward
  accepts a backup-only safety net", which assumed the backups were total; they
  were not, and the assumption is what the defining defect of 7.16.0 falsified.
  The installer now writes every byte through one canonical writer, so a
  backup-only unwind is a real option again, but only for files that writer
  replaced, and only on a tree where the backups can still tell the graft's
  writes from the steward's own (*Reversibility*, (b) and (d)).

## The rootstock line: the heart of this protocol

Harvest's heart is the agnosticism gate: *nothing project-specific enters the
seed*, mechanically floored by `tools/agnosticism-lint.py`, which the graft
also installs into the plant as `docs/graph/agnosticism-lint.py` so a plant can
check its own harvest candidates before offering them. Graft's heart is its
mirror, the **rootstock line**: *nothing the plant authored about itself is
overwritten by the upgrade.* Draw it once and hold it through every phase. The
two gates point opposite ways, and confusing them is the classic error: the
agnosticism lint belongs on what the plant sends *up*, never on what the plant
keeps. A plant's own knowledge names the plant, correctly.

Two territories, and graft writes to exactly one of them:

- **Seed-owned machinery (graft's to upgrade).** The artifacts the seed
  installs and continues to own: the kernel (`CLAUDE.md` / `AGENTS.md` /
  `.github/copilot-instructions.md` ← the seed's `core/AGENTS.md`); the
  seed-owned graph subtrees
  `docs/graph/{protocols,skills,agents,method,templates}/`, every node in them
  marked `origin: seed` (the protocols, the skills, the agent roster, the
  method/posture nodes, and the Tier-3 template artifacts: the delegation
  briefs, the graph-session-bootstrap block, the handback payload, the artifact
  templates); the harness projections of agents and skills (`.claude/agents/`,
  `.claude/skills/`, the `.prime/agent/`, `.opencode/` and `.codex/`
  equivalents, and `.github/`'s transformed views); the tool-specific commands,
  settings, and hooks; the shared router script `docs/graph/agent-lint.py`
  (also projected to `.claude/agent-lint.py` on Claude Code installs); and the
  graph engine scripts `docs/graph/{graph-lint.py,spec-lint.py}` (and the
  config-free `agent-lint.py` / `agnosticism-lint.py` / `prose-lint.py` /
  `status-register.py`, which fast-forward), preserving the plant's configured
  `TEST_GLOBS`. Graft carries the seed's newest version of these onto the
  plant. `_schema.md` and `index.md` are NOT in this list: they are
  project-instantiated and stay the plant's (see the engine-vs-instance rule
  below).
- **The plant's own life (graft preserves, always).** The rootstock: the
  plant's application source, and every knowledge fact the plant authored under
  `docs/graph/`, its `nodes/`, `specs/`, `decisions/`, `libraries/`, `plans/`,
  `runbooks/`, product, architecture, API, and data collections, any graph node
  **without** `origin: seed`, and the pinned, version-specific facts in its
  library and tool pages. Its `deviation.*` nodes are the plant's own: a
  standing departure the plant chose is its truth, never reconciled away by an
  upgrade. So is every `status:` frontmatter the plant authored: a fast-forward
  never advances, closes, or re-opens a plant's lifecycle state, with exactly
  one sanctioned exception: the ratified status migration below, which moves a
  plant's own recorded value into the plant's own frontmatter without changing
  it. Graft reads this territory to understand the plant and to place refreshed
  surface knowledge accurately; it treats every fact in it as the plant's to
  keep.

> **The rootstock line:** every fact the plant authored about itself survives
> the graft. A fact may be **re-homed**, into the node that owns it, into
> frontmatter, into a refreshed page's pinned block, but it is never lost and it
> never moves on the graft's own authority.

So the line is not "graft writes nothing inside `docs/graph/`". Phase 4
refreshes a page surface, Phase 5 moves routing prose into an expertise node,
Phase 6 re-homes a drifted fact, and each migration below touches
plant-authored material somewhere. The line is two conditions on **every** such
write, and an upgrade that cannot meet both stops and becomes a proposal for
the steward:

1. **Value-preserving.** The fact arrives at the other end intact. A plant's
   library and tool pages are the standing example: they live in `docs/graph/`
   and are plant-owned, yet Phase 4 renews their version-durable orientation
   layer from the enriched corpus and re-pins the version-specific facts fresh
   against the plant's real lockfile. Renewing the orientation is a graft;
   overwriting a pin is not.
2. **Ratified.** The steward saw the change named, file by file, and said yes.
   Deletion needs more than ratification: an explicit confirmation naming the
   resource, per the kernel's boundaries. Graft never deletes unprompted.

## The pure-graph mandate (`graft.pure-graph-mandate`): every graft leaves the plant more purely a graph

The rootstock line is graft's conservative heart: *preserve what the plant
authored.* The pure-graph mandate is its reconstructive heart: *every graft
leaves the plant closer to the seed's architecture than it found it.* The two
are complements, not tensions. The mandate refactors **structure, placement,
and projection**; the rootstock line guarantees the **facts themselves** are
never lost in the move.

The seed's architecture (6.0.0) is a **pure graph**: everything that can
activate progressively is a routable `docs/graph/` node; nothing about how to
work is always-loaded except a small bootstrap kernel; every tool-dir surface
is a *generated projection* of a node, not a hand-maintained copy; each fact
has one home; and no obsolete era, duplicate home, or competing doctrine
survives. Anywhere a plant falls short of that (machinery still living outside
the graph, a fact with two homes, an always-loaded file that should be a node,
a hand-maintained projection drifting from its source, dead compatibility
residue), **it is a drift from the spec, and closing it is in graft's scope.**
Graft does not merely fast-forward files onto a plant frozen in an older shape;
it drives the plant, end to end, toward maximal pure-graph.

Graft executes that drive as the **holistic reconstruction** the seed's own
rebalancing doctrine prescribes: reconstruct from evidence rather than
preference, move each fact to its natural owner, integrate rather than bolt on,
slice so the plant stays routable throughout, and fix each drift at its home.
**Phase 6 is the one home of that procedure**: its ledger, its drift classes,
and its worker classes are stated there and nowhere else.

The mandate is **standing**. The pre-6.0 layout migration below and its
knowledge fact-sweep (step (f)) are its maximal instance, because a plant that
predates the graph needs the whole reconstruction; a plant one version behind
still runs Phase 6, lighter. A graft that only swaps machinery versions and
leaves a structurally-drifted plant structurally drifted has upgraded the scion
and neglected the tree.

## The three-way reconciliation (`graft.reconcile-flow`): how the machinery is upgraded

A plant is not a blank target. Since it grew, its steward may have locally
sharpened a protocol, adjusted a setting, or fixed a script: the very kind of
divergence a future `harvest` exists to pull back. Graft respects that work by
reconciling three versions of every seed-owned artifact, exactly as a
well-behaved merge does:

- **base**: the seed revision the plant grew from (read from the plant's seed
  stamp; reconstructed from install backups or content lineage on a first
  graft; see *Provenance & the seed stamp* below);
- **theirs**: the artifact in the seed today;
- **ours**: the artifact as it currently stands in the plant.

Each artifact then takes one of three clean paths:

- **FAST-FORWARD**: the seed advanced and the plant left the artifact pristine.
  Adopt the seed's new version outright. This is the common case and the bulk
  of a graft's value.
- **KEEP-PLANT (and flag upstream)**: the plant diverged and the seed did not.
  Keep the plant's version untouched, and record the divergence as a **harvest
  candidate**: the plant improved its machinery, and that improvement may
  deserve to flow back into the seed for everyone. Graft's outbound pass thus
  feeds the inbound loop.
- **MERGE**: both the seed and the plant advanced the same artifact. Reconcile
  them as a single **holistic re-integration** (the seed's own "integrate,
  don't patch" principle): produce one coherent file that carries the seed's
  new capability *and* preserves the plant's intent, and surface it to the
  steward as a reviewable proposal. A three-way conflict is a decision, and the
  decision is the steward's.

## The installer is the hand that applies it

The reconciliation decides; `install.sh` writes. What it does to a plant is
therefore part of this procedure, not an implementation detail behind it: the
whole safety story of a graft rests on properties of that one script.

**One canonical writer.** Every byte that **replaces a seed-owned destination**
passes through `place_file`, so the safety properties belong to the installer
rather than to whichever call site remembered them: a destination that is
already correct is left alone (no churn, no backup); a divergent destination is
moved aside to `<path>.bak-YYYYMMDD-HHMMSS` **first**; the backup is taken with
`mv`, which moves the link object, so a destination symlinked outside the
target is replaced rather than written through. Until 7.16.0 seventeen
destinations reached the filesystem directly, 86 files in an `install.sh all`,
each one destroying plant edits with no backup for the audit to classify. That
is what makes "the backups are the safety net" a statement about the installer
today instead of a hope; `tests/test-install-placement.sh` holds it to that
over a **discovered** destination set, so a destination added tomorrow is
covered without anyone remembering to add it, under three invariants it keeps
separate:

- **M7, recoverability.** Every destination the run *replaced* has a
  timestamped sibling beside it. Its sole declared exception is
  `is_installer_state()`: `.cypress/seed.json`. Read the scope as carefully as
  the exception. The sweep reaches M7's branch only where the plant's edit is
  *gone*; a destination that still carries its edit is diverted one branch
  earlier, into M1's question of whether the installer still maintains it. So
  every `is_plant_owned()` destination, `docs/graph/index.md` among them, is
  answered by M1 and never evaluated for M7. The property is "what
  `place_file` replaced is recoverable", and it is silent about a writer that
  reaches a plant-owned file by another route.
- **M9, link uniformity.** Under `--symlink` every placed file is a link, or
  else one of three recorded exceptions: `is_plant_owned()`, because a
  plant-owned file must not be a link into the seed; `is_generated()`, because
  content generated per target has no seed original to link to; and
  `is_installer_state()`. M9 is about link mode, not backups.
- **M10, containment.** No write escapes the target directory, by any writer,
  through any symlink. `place_file`'s own `mv` argument covers `place_file` and
  nothing else, and review found three writers that reached the filesystem past
  it: the note write described below; the destination preflight, which waved
  through a symlink **to a directory** because such a link satisfies both `-e`
  and `-d`; and `fill_plant_facts`, which rewrites `docs/graph/index.md` in
  place because it is the one destination the installer does not reach through
  `place_file`, using a call that follows a link. That third one wrote a plant
  fact into a file outside the target and exited 0, with no warning and no
  backup anywhere to find it by. Each was reproduced before it was closed. What
  M10 asserts now is those behaviours and their limit: a link at a destination
  is moved aside rather than followed, a destination directory whose link
  resolves outside the target is refused before the first byte, the plant facts
  are not written through an `index.md` link that leaves the target, and a link
  that stays
  **inside** the target keeps working, because the rule is about leaving the
  target and not about links. A plant that uses symlinks is the plant this
  matters to, and it is the plant a steward is most likely to be grafting.

Reading M9's exception list as if it were M7's is the available mistake, and it
inverts the gate. `place_generated` (slash commands, the transformed Copilot
views, the Codex snippet) sets `LINK_MODE=copy` and then **calls
`place_file`**, so it backs up exactly like everything else; `graft-audit.py`
resolves those backups through `generator_for()` and gives them a
classification of their own, comparing the replaced body against the generator
for plant signal rather than against a seed twin it has none of. The audit is
not blind to them.

**What the writer does not cover.** Five paths reach the filesystem without
`place_file`, and **three of them replace bytes with no backup**. That is the
sentence a steward has to carry out of this section, because the obvious
reading of "one canonical writer" is that `find <plant> -name '*.bak-*'`
accounts for every byte the run destroyed, and it does not:

- `place_state` writes `.cypress/seed.json`, replacing it with no backup. The
  one recorded M7 exception, and the only *declared* one.
- `place_if_missing` places the scaffold leaves, `_schema.md`, `index.md`, and
  the graph engines (`graph-lint.py`, `spec-lint.py`, `grill-lint.py`). It only
  ever **adds**, so there is nothing to back up and nothing M7 asks of it;
  these also stay real files under `--symlink`, because a plant-owned file must
  not be a link into the seed. Their fast-forward is Phase 3's engine
  reconciliation.
- `fill_plant_facts` rewrites `docs/graph/index.md` in place, with no backup.
  **That is a write into a plant-owned file**, the same file the territory list
  above declares the plant's. Two bounds keep it honest and neither makes it
  recoverable. It is *bounded in content*: it fills placeholder `plant:` values
  and adds a missing key in the template's own words, and never replaces a
  value the plant declared. And it is *bounded in frequency*: the rendered
  frontmatter is compared against what was on disk and written only when the
  two differ, so an already-filled block is not rewritten and a run that
  changes nothing touches nothing. What it is not is backed up. So
  `graft.gate.rootstock` has no `.bak` to read and `git -C <plant> diff
  docs/graph/index.md` is the only thing that can see it. Read that diff before
  ratifying, and read *Reversibility* (b) 5 for what happens when there is no
  committed version to diff against.
- `record_instruction_migration` creates and appends to
  `docs/graph/plans/adopted-instructions.md` with shell redirection. It guards
  the create on `! -e`, which is **false for a dangling symlink**, so until
  7.16.0 `cat >` followed such a link and wrote the note outside the plant
  entirely. It now treats a symlink at that path the way `place_file` treats
  any destination link: the link object is moved aside as a `.bak-`, a warning
  names where it went, and the note is written as a real file inside
  `PROJECT_DIR`. `tests/test-install-placement.sh` pins it as M10 (1).
- `place_kernel`'s sibling branch `rm -f`s the second of `CLAUDE.md` /
  `AGENTS.md` and replaces it with a project-local symlink. The `rm -f` is
  unconditional; the backup before it is guarded on `! cmp -s` against the seed
  kernel, so a sibling that happened to match the seed is destroyed with
  nothing left behind (*Reversibility*, (b) 4).

**The instruction ledger is work, not a note.** When the kernel replaces a
project's own root instruction file, the old body survives as a `.bak` and
stops being in force. So the installer files it: `record_instruction_migration`
appends one row per replaced instruction file, addressed to `docs-librarian`,
with a table of where each kind of instruction belongs. Nothing is migrated
automatically, on purpose. Two consequences for a graft: the note lands inside
`plans/`, the one subtree this protocol's own audit is told to treat as
untouchable, so **the graft must report it or nobody will**
(`graft.gate.adopted-instructions`); and a run whose note write failed after
the kernel was already swapped is not filed by the next run either
(*Reversibility*, (b) 3). The preflight now refuses when `docs/graph/plans` is
blocked, and `sweep_orphaned_instruction_backups` catches the general case by
re-filing any repo-root kernel backup with no ledger entry. Both safety nets
are gated on `PRIOR_INSTALL`, which is set only where `.cypress/seed.json`
already exists when the run starts, so on a stampless plant (Phase 1's
pre-7.3.0 case) the sweep returns early and files nothing.

**The flags, and what a steward must know about each.**

- `--force` suppresses the per-file `backed up existing …` warning and nothing
  else. The backup is always made. It once did skip the backup in
  `place_kernel`'s sibling branch, because the help text said "without
  prompting" for a prompt that never existed and "`--force` means no backup"
  became folklore and then got implemented; that is fixed. Even so, prefer a
  graft **without** it: those warnings are the cheapest divergence signal there
  is, and the customization audit is a slower second opinion, not a
  replacement.
- `--symlink` places links into the seed instead of copies, and it changes what
  a graft *means*. A symlinked plant's machinery moves whenever the seed moves,
  and an edit to a placed file writes back **into the seed**, so `ours` and
  `theirs` are the same file, the three-way reconciliation has nothing to
  reconcile, and what looks like a plant divergence may be a seed edit. Never
  introduce `--symlink` on a graft of a copy-mode plant. If the plant is
  already symlinked, say so in the graft record and treat every apparent
  KEEP-PLANT as unverified until its provenance is established.
  (`place_if_missing` and `place_generated` destinations stay real files in
  both modes: M9's recorded exception list, not an oversight.)
- `--copy` is the default and the way back. Switching an already-symlinked
  plant to copies is a real, graft-relevant operation: it restores the `ours` /
  `theirs` distinction the three-way reconciliation needs, and it is a
  **write**: every link is replaced by a file, each one through `place_file`,
  so it produces a full set of fresh backups and a `graft.gate.customization`
  run of its own. Do it as a ratified step of its own, before the
  reconciliation, never folded into the upgrade run: the flag flip and the
  version advance produce the same `.bak` date and become indistinguishable
  afterwards.
- The four plant facts (`--environment-class`, `--commit-attribution`,
  `--deliverable-language`, `--comment-language`), `--legal-corpus` and
  `--legal-jurisdiction` are the **owner's** recorded decisions. A run that
  passes no flag inherits what the stamp already holds; only `undecided` is
  overwritten by silence. A graft never decides one by inspection.

The stamp the run writes is the last additive step of a successful upgrade:
`write_seed_stamp` runs after every adapter, after the re-created notice and
after the orphaned-backup sweep. So a stamp at the new version is evidence the
run reached the end, and `graft.gate.stamp` reads it that way. How to read the
stamp's *contents* is one fact with one home, *Provenance & the seed stamp*
below.

**A re-created node is not always a good thing.** The installer tracks
seed-owned graph nodes that were *absent* from a plant that already carried the
seed, and prints a "re-created" notice for them once, after the last adapter
has run. That is correct fast-forward behaviour, and it is also exactly how a
plant's **deliberate deletion** gets silently reverted
(`graft.gate.recreated-nodes`). Two properties bound what the notice is worth.
It is gated on `PRIOR_INSTALL`, so a stampless plant gets none and the gate is
N-A there rather than clean. And it is printed, not stored: nothing on disk
records it afterwards, and re-running the installer will not reproduce it,
because the nodes now exist. **Capture the install output to a file** and cite
that file as the gate's evidence; scrollback is not evidence.

## The flow

Orchestrated like `grow` and `harvest`: the session plans, briefs, reconciles,
and delivers; clean-context workers survey and author. Model policy is strict:
**Sonnet-class** workers survey and classify (read-only); **Opus-class**
workers perform every reconciliation, holistic merge, corpus refresh, and
validation. Every spawned worker executes the canonical GRAPH DISCIPLINE block
of `docs/graph/templates/prompts/graph-session-bootstrap.md` (the one home for
the worker discipline; briefs embed it, this file only points at it) and
returns the `--plan` command, the loaded closure, and its deliberate skips.
Where the host supports model-class selection and clean-context spawning,
honour it; if it cannot, report that this host cannot execute the seed's
operating model rather than collapsing the work into the main chat.

### Phase 1: Locate the plant and establish the base (session + Sonnet)

Identify the plant or the set of sibling plants in scope, and for each record
its path, host integration (`.claude/` / `.prime/agent/` / `.opencode/` /
`.codex/` / `.github/`), current branch, HEAD, and worktree cleanliness, as
provenance, without mutating Git. Read the plant's **seed stamp** to learn the
base version it carries; on a first graft where no stamp exists, reconstruct
the base from install backups (`*.bak-*`) or from content lineage against
tagged seed revisions, and note that the stamp will be established by this
graft. A corrupt stamp is reconstructed the same way (*Provenance & the seed
stamp*), and the record says that the plant's recorded decisions were
re-derived rather than inherited. A stampless plant is also the one where the
installer's own two safety nets are silent (`graft.gate.recreated-nodes` is
N-A, and no orphaned kernel backup is swept), so this is the graft that owes
the closest reading of the install output. Confirm the seed's own version and
what has changed between base and now (its CHANGELOG and harvest log are the
map of available fruit). A clean working tree here makes the whole upgrade easy
to review and to unwind.

### Phase 2: Survey the drift (Sonnet scouts, read-only)

Dispatch read-only scouts to inventory every seed-owned artifact installed in
the plant and classify its three-way state (base vs. theirs vs. ours) as a
first guess at FAST-FORWARD / KEEP-PLANT / MERGE. In parallel, inventory the
**fruit the plant can withdraw**: the libraries, tools, and, where the plant
is subject to externally-authored rules, the legal instruments the plant
actually reasons against (from its `docs/graph/libraries/`,
`docs/graph/tools/`, and `docs/graph/legal/`) for which the seed's
`library-corpus/`, `tool-corpus/`, or `legal-corpus/` now holds a page the
plant predates or lacks. Return a **graft ledger**, one row per artifact or
withdrawable page, with provenance (plant path, seed source, base state) and a
candidate class. Claims cite paths; centralized prose is an untrusted clue
until corroborated against the installed files.

### The migrations (`graft.migration`): between the survey and the reconcile

A plant can be behind the seed in ways no file-for-file fast-forward reaches.
Its machinery may sit in a layout the seed has replaced; its lifecycle state
may be recorded where nothing can query it; its own artifacts may carry a form
the seed has since redefined. The three subsections below are one fact and one
slot in the flow, and they are independent of each other: a plant may owe all
three, one, or none. Each is proposed, ratified, and recorded separately.

#### Layout migration: 5.x → 6.0.0

The survey may find a **pre-6.0 plant**: its machinery lives in the old
tool-dir layout (`.claude/protocols/`, `.claude/templates/`, `.claude/core/`,
and the `.opencode/` / `.codex/` / `.github/` equivalents) instead of the
graph subtrees `docs/graph/{protocols,skills,agents,method,templates}/`. Such a
plant is not fast-forwarded file-for-file; it is **migrated**, and the
migration threads through the phases that follow:

- **(a) Install the new machinery into `docs/graph/` as usual, and read what
  the install says it did.** The installer places the seed's current protocols,
  skills, agents, method nodes, and template artifacts as `origin: seed` graph
  nodes, and regenerates the agent/skill harness projections. Phase 3's
  reconciliation then runs against these new homes. The run is not fire-and-
  forget: it **refuses before writing anything** when a destination directory
  is occupied by a file, by a symlink to one, or by a dangling symlink; when a
  destination directory is a symlink that resolves **outside** the target,
  which is M10's second half and the shape that used to put `seed.json` outside
  the plant; or when a destination directory exists and is not writable. The
  refusal names every offending path and leaves nothing on disk, in place of
  the half-installed target that used to result. A destination symlink that
  stays inside the target is deliberately still allowed, so a plant that
  arranges its own directories with links is not refused for doing so.
  **Redirect the output to a file** and keep it. The "re-created" notice exists
  nowhere else once the run ends, and the `adopted-instructions` warning, the
  displaced-symlink warning, and the per-file backup warnings are how a reader
  learns what to look for before Phase 7 goes looking. Python bytecode is never
  seed content and is excluded from the machinery subtrees; a `__pycache__` or
  `.pyc` file found inside one on an older plant has no seed source, so it is
  residue to list for the steward's deletion, not an artifact to reconcile.
- **(b) Diff the old tool-dir copies against their seed base; the plant's
  customizations must survive the move.** Each old copy under
  `.claude/protocols/`, `.claude/templates/`, `.claude/core/` (and kin) is
  three-way-compared against the seed revision the plant grew from. A pristine
  copy needs nothing; a **plant-local customization** is carried into the
  corresponding graph copy as a holistic MERGE (Phase 3's discipline), so the
  new layout arrives already carrying the plant's intent. And exactly as this
  protocol already holds for KEEP-PLANT: a local divergence is also a **harvest
  candidate**, so hand it back that way.
- **(c) Relocate the plant's OWN agents and skills into the graph too,
  holistically reconciled, not just tagged and moved.** A 5.x plant's
  *plant-authored* machinery, the experts and project skills it grew (`origin:
  project`, not seed-owned), sits in the harness dirs (`.claude/agents/*.md`,
  `.claude/skills/<name>/SKILL.md`) with no `docs/graph/` home. The 6.0.0
  layout is where **every** agent and skill node lives, seed-owned or
  plant-owned, so a plant left with its own agents/skills in the old spot is
  half-migrated: the router cannot route them, and graph-lint cannot see them.
  But relocating is not reconciling. Promote each into
  `docs/graph/{agents,skills}/`, adding the node frontmatter it lacks
  (`id`/`tier`/`kind`/`origin: project`/`title`/`owns`/`est_tokens`, reusing an
  agent's `routing_triggers` as its `load_when`, and, for an expert,
  `plant_knowledge:` naming the collections or expertise nodes it must be able
  to read, without which the relocated expert lands as a node the coverage gate
  cannot answer for). Then read its content against the rest of the graph,
  because a plant-authored expert that predates the graph was written with no
  graph to defer to and will almost certainly restate facts the graph's
  crosscut/platform/subsystem nodes already own (an auth mechanism, a secrets
  inventory, a platform topology). Trim every restated fact to a genuine
  cross-reference (name the owning node, don't re-explain it), keeping only
  the routing charter and the facts this node is the true, sole home of:
  exactly the treatment Phase 3 gives a MERGE. **The projection then follows
  from the graph on its own.** Since 7.15.0 `project_agents` and
  `project_skills` read the *plant's* `docs/graph/{agents,skills}/`, not the
  seed's, so re-running the installer for each adapter the plant carries
  projects the relocated node like any other. Three things that discovery does
  not cover, and which a relocation must respect: only the **top level** of
  each home is projected (a node parked in a subdirectory is never spawnable);
  `_`-prefixed files, `index.md` and `README.md` are skipped; and a skill's
  home is the flattened `docs/graph/skills/<name>.md`, projected to
  `<adapter>/skills/<name>/SKILL.md`. Copilot's views are transformed rather
  than copied, so they are not byte-identical by design, and
  `agent_projection_for` records which adapters are verbatim. That
  reconciliation is Opus-class work rather than a mechanical copy, and its
  result is additive: it lands in the ratifiable proposal like every other
  migration step.
- **(d) List the now-redundant old machinery; the STEWARD confirms deletion.**
  Once the graph homes and projections exist, the old tool-dir copies are
  redundant. Graft lists every such file and asks the steward to confirm their
  deletion **explicitly, by name**. It never deletes them itself (deletion
  requires an explicit confirmation naming the resource, per the kernel's
  boundaries). Until confirmed, they stay in place, inert.
- **(e) Rewrite stale references in plant-authored docs only with consent.**
  Plant-authored pages may cite the old paths (`.protocols/x.md`,
  `.skills/<name>/SKILL.md`, `.templates/…`, `.core/operating-principles.md`).
  Rewriting them to the `docs/graph/…` homes touches the rootstock, so graft
  first lists **every file it would touch** with the exact rewrites, and
  proceeds only on the steward's consent, never as a silent sweep.
- **(f) Sweep the plant's own pre-graph knowledge: a migration this old owes a
  fact-sweep, not just a machinery swap.** A plant old enough to predate the
  graph architecture entirely was never run through `adopt-existing` or
  `ingest-library`: its real, load-bearing knowledge (deploy-pipeline docs,
  per-repo READMEs, sharp edges recorded only in a comment, drift between what
  a config claims and what the code does) has had nowhere to land and was
  never captured. Finishing (a) to (e) leaves the graph *structurally* current
  (the router works, the machinery is in place) while leaving it
  *substantively* thin, a plant whose facts still mostly live outside the
  graph structure, in the repos the graph is supposed to orient a reader away
  from re-reading. Dispatch read-only scouts across the plant's actual source,
  not just its machinery, to inventory facts missing from the graph,
  cross-checked against what existing nodes already own so nothing
  already-covered is re-reported, then hand confirmed findings to Opus authors
  to weave (never append) into the owning node. This sweep is **part of the
  migration** for any plant old enough to have predated the graph, not an
  optional follow-on task the steward has to separately request. A migration
  that upgrades the machinery and stops there has moved the furniture without
  unpacking the house.

The migration's outcome feeds Phase 7 unchanged: the audit runs over the
backups, the redundant-copy list and any un-consented reference rewrites appear
in the proposal, and the stamp records the plant as a 6.0.0-layout plant.

#### Status migration: pre-7.0.0 → 7.0.0

A plant grown or last grafted before 7.0.0 carries lifecycle status as body
prose (an ADR's `## Status` line, a spec's `**Status:**` bullet) in a
vocabulary per kind, which nothing can query and which drifts from its index
rows. The graft runs `python3 <seed>/tools/status-migrate.py --root
<plant>/docs/graph` (dry run) and reports its table in the graft record; on the
steward's ratification it re-runs with `--write`, moving each value into
frontmatter in the schema's one vocabulary (`docs/graph/_schema.md` §"Lifecycle
status") and leaving the body line as a pointer. What the tool cannot map it
reports rather than invents: a threat model's `active` means "in force", not
lifecycle debt, and its new home is the steward's call via `--map`; a companion
the old record never stated is written `not recorded: <why>`. This touches
plant-authored frontmatter, so it is the one sanctioned exception to the
rootstock rule on `status:`, and it is a narrow one: the plant's own value
moved into the plant's own frontmatter, ratified, never a change of state. The
installer has already placed `docs/graph/status-register.py`; Phase 7 runs its
lint after the write (`graft.gate.status-register`).

#### Shape migration: plant-authored artifacts whose FORM the seed has changed

The migrations above move things the seed owns. This one does not, and that is
the whole difficulty: a plant's own records (its plan-of-record, its specs,
its nodes) are never fast-forwarded, because they hold decisions no upgrade
may touch. But the seed sometimes changes the SHAPE such an artifact is meant
to take, and a plant left in the old shape is not wrong so much as stranded: it
still lints, it still reads, and it no longer gets the property the new shape
was introduced for.

So a shape migration is a **proposal about the plant's own content**, never an
edit the graft performs on its own authority. The graft's job is to notice the
old shape, say what the new one buys, show the conversion, and stop. The
steward ratifies; the plant's own authors do the work.

**Reading the versions.** Before proposing anything, the graft reads the seed's
`CHANGELOG.md` from the version in `.cypress/seed.json` forward to the new one,
and the affected protocol and template nodes. A shape change is announced there
in prose, with the reason; a graft that fast-forwards machinery without reading
why it changed will re-apply the old shape's assumptions to the new files and
call it done. The entries between the two versions are the migration's
specification.

**The worked example, monolithic plan-of-record to ledger + child files
(7.16.0).** A plan's §9 holds every increment ever planned: contracts, RED
tests, rollback path, dependencies. A plan is read whole, so past a certain
size the document describing the work becomes the largest single thing a
session loads, and progressive discovery is defeated by the plan itself. 7.16.0
makes §9 able to be an **index**: one row per increment, pointing at a file
under `docs/graph/plans/grill/`.

Propose the conversion when a plant's `docs/graph/plans/grill.md` is large
enough that §9 dominates it. The conversion:

1. For each `### Increment N — title` block in §9, create
   `docs/graph/plans/grill/increment-NN-<slug>.md` holding that block verbatim,
   heading included. Verbatim matters: an increment is a record of what was
   decided, and a migration that rewrites it while moving it has destroyed the
   thing it was preserving.
2. Replace §9's body with an index, one row per increment, the last cell
   naming the file: `| # | Increment | Status | Detail |`.
3. Leave every other section where it is. Only §9 moves.
4. `python3 docs/graph/grill-lint.py` must pass afterwards. It resolves the
   index, enforces the same required fields inside each child, and refuses a
   row with no file, a file no row points at, and an increment defined twice.

Both forms lint, so this is done **one increment at a time** and never as a
flag day, because a half-migrated plan is a valid plan. Nothing in the seed
converts it, and nothing in the seed may: `plans/` is deliberately absent from
graft-audit's machinery subtrees, so a backup over a plan record reports as
buried plant knowledge rather than a routine upgrade. That is the protection;
the migration respects it by being a proposal. It is also why the installer's
own write into that subtree, the adopted-instructions ledger, has to be
reported by hand.

The same three questions apply to any future shape change: **what form does the
plant carry, what does the new form buy it, and what is the conversion**,
asked about the plant's content, answered in the graft record, decided by the
steward.

### Phase 3: Reconcile the machinery (Opus authors)

For each seed-owned artifact, apply the three-way reconciliation above and
produce the upgraded result: adopt on FAST-FORWARD; retain and raise a harvest
candidate on KEEP-PLANT; author one holistic re-integration on MERGE. Every
merged file arrives whole, integrated as if it had always read that way, never
a seed block bolted beside a plant block. Each reconciliation records its
provenance: base state, decision, and what the plant kept.

**The roster delta may not be spawnable in this session.** Reconciling the agent
nodes rewrites the harness projection mid-session, and when a host sees such a
write is host-dependent, so every specialist the seed *added or renamed* since
the plant's base is on disk and may be unspawnable for the phases that follow.
Preflight before dispatching by name, and take the remedy or the recorded
fallback in `docs/graph/method/delegation.md`
(`delegation.harness-registration`). Carry the delta forward as a named list;
Phase 7 reports it.

**The graph engine is machinery too, and the installer will not fast-forward
it.** The installer drops the knowledge-graph scaffold (`graph-lint.py`,
`spec-lint.py`, `_schema.md`, `index.md`) *only if absent*, so a plant that
already has them keeps its OLD engine across a graft and silently misses every
linter improvement since it grew. (The agent router `docs/graph/agent-lint.py`
is the exception: it carries no project config, so the installer fast-forwards
it like any machinery file (identical untouched, changed backed up for the
audit) and it needs no engine-style reconciliation.) **A graft that leaves a
plant on a stale graph engine is not a true upgrade.** Reconcile the engine
explicitly, as a config-preserving fast-forward: adopt the seed's current
engine body and re-inject the plant's own PROJECT CONFIG (`ROOT_ID` / `KINDS` /
`KIND_PREFIX` in `graph-lint.py`; `TEST_GLOBS` in `spec-lint.py`). The plant
gains the engine, keeps its configured identity, and a knob it predates adopts
the seed default. **A config knob the seed has *extended* since the base is
UNIONED, not re-injected wholesale.** The load-bearing case is `KINDS`: 6.0.0
added the machinery kinds `protocol`/`skill`/`agent`/`method`, so keeping the
plant's older `KINDS` set verbatim would drop them and every newly-installed
machinery node would fail lint with `kind not in KINDS`. The union keeps the
plant's own kinds *and* adds the seed's new members; only a scalar identity
(`ROOT_ID`) or a plant-list (`TEST_GLOBS`) is kept wholesale. Where the plant's
engine is a strict *superset* of the seed's, that is a KEEP-PLANT (the plant is
ahead) and a harvest candidate. `tools/graft-graph-engine.py` performs exactly
this merge (set-valued knobs unioned, others kept wholesale) and the superset
detection; `_schema.md` and `index.md` stay the plant's (they are
project-instantiated, and copying the seed template would regress placeholders
and wipe the authored router). The engine is what makes the `composes` rules
enforceable on this plant at all: that every composed id resolves and both ends
are `kind: expertise`, that `composes` is acyclic on its own, that a node which
`requires` an expertise parent is listed in that parent's `composes`, and that
an expertise node carries at least one depth edge to the pin or standard it
routes to. A plant on the old engine is not failing those rules. It is not
being asked them.

**`_schema.md` is the plant's, and it can still be too old to read the
machinery.** The engine-vs-instance rule keeps the node contract the plant's
file; it does not keep it *current*. A plant carrying a schema several minors
old is linted against a vocabulary that predates the kinds, edges and lifecycle
values the nodes this graft just installed are written in: the contract an
author reads and the linter that holds them to it drift apart. The audit
reports this as a node-schema staleness line rather than gating on it
(`graft.gate.schema`), and the remedy is a MERGE the steward ratifies: the
plant's own additions kept, the seed's new contract lines folded in.

**The installer fast-forwards blindly, so reconciliation is only real if it is
audited.** The installer overwrites every seed-owned machinery file with a
per-file backup but does **not** check whether the file it replaces carried a
plant customization first, so a FF can bury a local divergence (recoverable
from the `.bak`, but invisible). The reconcile-before-overwrite promise is
therefore kept by a **mandatory post-FF audit** (Phase 7,
`tools/graft-audit.py`): any seed-owned file whose backup differs from the seed
*and* carries plant-signal content is a divergence that must be re-integrated
into the FF'd file or ratified, never left buried. Know what the audit's map
reaches, because a path it cannot map is a path it cannot classify: every
adapter tree including `.prime/agent/`, the harness projections of agents and
skills, the machinery subtrees, and the legal corpus pages under
`docs/graph/legal/corpus/` all resolve to a seed source, so a replaced legal
page is audited like any other machinery file. A backup that resolves to
nothing is reported unresolved rather than passed.

### Phase 4: Refresh the plant's knowledge from the corpus (Opus authors)

For each withdrawable library/tool page from Phase 2, **seed the refresh from
the corpus as the orientation layer**, exactly as `ingest-library` and
`toolcraft` do for a new plant, then re-pin the plant's version-specific facts
fresh against the plant's real lockfile. The plant keeps every pinned fact it
discovered; it gains the enriched, version-durable surface the corpus now
holds. Where the plant has no page yet for a library it uses that the corpus
covers, propose growing one from the corpus orientation plus a fresh pinned
delta.

A withdrawable **legal** page refreshes the same way with one added,
non-negotiable step: the corpus carries the citation, never its currency.
Re-confirm each entry's `verified` date and `legal_status` against the
publisher before the plant relies on it, and never copy a determination: the
plant authors its own application of the rule. A corpus entry whose currency
cannot be re-confirmed is refreshed as orientation only, and said to be such.

**One home per dependency — merge into the plant's existing page, never add a
parallel one.** When the plant already has a page for the dependency, the
refresh **merges the corpus orientation into that existing page** (fold in
whatever generic orientation the plant's page lacks; keep every pin and sharp
edge it already carries) and does **not** create a second page. In particular,
**do not mirror the corpus's own internal grouping into the plant.** The corpus
may file a page under a sub-namespace (for example
`library-corpus/container/docker.md`); that grouping is a seed-side
organizational detail, not a path to replicate. Dropping it in beside the
plant's flat `libraries/docker.md` produces two homes for the same dependency,
a one-home-per-fact violation the graft itself created, and
`graft.gate.minimum-sufficient` blocks that item. The corpus
page's *content* lands in the plant's existing page; the corpus page's
*location* stays in the corpus. This is the fruit reaching the plant: harvest
lifted the surface up into the seed, and graft lets this plant withdraw it.
Adopt a portable corpus tool only when the plant's stack matches; otherwise
treat the page as a blueprint and re-author against the plant's stack,
test-first.

### Phase 5: Grow the new capabilities onto the living plant (Opus authors)

Fast-forwarding the machinery *carries* a capability to the plant; it does not
*grow* it there. A refreshed protocol, a new skill template, a new runbook
template, a corpus tool the plant's stack could use, each arrives as inert
machinery. **Grafted is not grown.** This phase closes that gap: for each new
or newly-enriched capability the graft delivered, grow it onto the plant
**where doing so is appropriate and necessary**, actualized into the plant's
living skills, tools, and knowledge, not left sitting as a template.

**Run grow's loop, do not re-invent it — and this is the phase that loads it.**
`protocol.grow` is a **peer** of this node, not part of its closure, and the
distinction is deliberate: a graft that fast-forwards machinery, reconciles it,
and finds nothing new to actualize never opens grow at all, and making every
graft session pay for grow's whole body up front would be the eager loading the
graph exists to avoid. What this phase needs by citation it names by citation
(`grow.completeness-contract` for what "grown" means, `grow.stack-inventory`
for how the plant's stack is read, `grow.legal-corpus` for the whole-or-nothing
corpus rule). The moment this phase has a capability to actualize, the task has
explicitly crossed into grow's subject, which is what a `peers:` edge is for:
**load `protocol.grow` here, deliberately**, and use grow's loop instead of a
graft-shaped imitation of it. Start by re-planning the coverage record against
the seed the plant now carries:

```sh
python3 <seed>/tools/growth-audit.py <plant> <seed> --plan
python3 <seed>/tools/growth-audit.py <plant> <seed>
```

`--plan` derives the required rows from the NEW seed, so every collection,
every `plant_knowledge:`-declaring agent, and every `expertise.*` node this
seed's inventory kinds now owe arrives as a row the plant does not yet answer.
That is the "grafted is not grown" gap made visible, per capability, before any
authoring starts. The lint then names what is still owed; `--agents` narrows it
to the agent and expert rows when the question is only "can every roster
specialist work here?", and `--json` returns the same findings machine-readable
for the record. A plant grown under an older seed also gains rows for the
domains that seed never gathered evidence for: a `ui-ux-designer` with no
`design/` material and a `legal` analyst with no corpus are the standing
examples, and they are the reason an upgraded plant is re-audited rather than
assumed complete because it was grown once.

An expertise row is usually grown from facts the plant already holds. Where
its `stack.*` node already carries the routing prose (when this stack is
in play, what must not be done without it, which sub-expertises apply under
which condition), the graft **moves** that prose into the expertise node and
leaves a `requires:` edge behind rather than copying it: the `stack.*` node
keeps this project's conventions, the expertise node owns applicability and
composition, and the same routing fact may not stand in two homes. Where a new
row needs evidence the plant's graph does not hold, the graft dispatches the
same workers grow does: a growth-scout at the boundary, and a `research-scout`
for anything the plan marks `grounding.required`, so a new `best-practices/` or
`libraries/` page is written from retrieved upstream documentation rather than
model memory. The loop is grow's: inventory, plan, author, lint, repeat while
findings remain. What a graft may NOT do is close a row by lowering it. A row
that cannot be covered on this pass is recorded `UNKNOWN` with its blocker, or
`ABSENT` with the reason and the paths searched, written where the audit reads
it: the collection's own `index.md` or `README.md` is the legitimate home of an
authored absence, and a reason that lives only in the graft's chat output fails
a row the procedure was otherwise followed for. It ships reported: named in
the Phase 8 entry, which is where `growth-audit.py` looks (`SILENT` otherwise),
and put to the steward as a numbered decision where the blocker is theirs to
resolve (`deliver.numbered-decisions`). And a collection this seed added after
the plant's base, whose material the plant already authored under another home,
is not `ABSENT` at all: it is Phase 6 drift, the "filled elsewhere" class, and
it moves.

- **Grow what the plant evidently needs, grounded in its own facts.**
  Instantiate a suggested skill or expert the plant's real stack calls for (the
  `skill-corpus` / `agent-corpus` withdraw contract, into `docs/graph/skills/`
  / `docs/graph/agents/`, at the **top level** of each, since that is the only
  depth the installer's projection reads: a node one directory down is on disk
  and unspawnable, and the coverage gate reports it as such), withdraw a corpus
  library/tool page the plant uses today, place the **whole** `legal-corpus`
  where the plant's stamp records `"legal_corpus": "yes"` and re-ask the owner
  where it records `undecided` (`grow.legal-corpus`; a graft never decides it
  by inspection, and never withdraws a subset, because an analyst cannot
  distinguish a page nobody copied from an instrument that does not exist),
  re-ask the national jurisdiction the same way and raise an ingest request
  where the corpus carries no national layer for it instead of reading across
  from a neighbouring country, or ground a runbook the plant can fill from its
  own deploy/release nodes. Every grown addition is anchored in evidence the
  plant's graph already holds: its references resolve inside the plant, never
  at a seed-corpus path.
- **Never fabricate to fill a surface.** A capability whose content can only
  come from the plant's real, recurring use (a project skill for a procedure
  that has recurred here, an ADR for a decision this plant took, a runbook's
  real commands) is **not** manufactured here. The seed's own anti-fabrication
  discipline (the `adr-writer` "don't invent a decision" and `grill-planner`
  "mark what you haven't verified" rules) applies to every surface: thin
  evidence is a reason to defer, not to invent. These sprout during real use,
  owned by the close-out lifecycle (`canonize` → `docs-librarian`), not by the
  graft.
- **Surface what was grafted but not grown.** Report every capability now
  present as machinery yet still inert — no project skill sprouted, runbook
  templates still unfilled, a corpus page not yet withdrawn — so the steward
  sees the copy-but-not-actualized state plainly, and knows which items were
  grown now (grounded) versus deferred to real use (ungrounded). A silent inert
  capability reads as "delivered" when it is only "installed."
- **Own-kernel plants still receive the substance — as a weave, not a
  summary.** A plant that deliberately carries no seed machinery — its own
  instruction system is the rootstock — is not exempt from the upgrade. Its
  machinery classes as KEEP-PLANT, but the seed's substantive delta since the
  plant's base is **re-woven** into the plant the same way the seed itself
  carries it: map each seed surface the delta changed to the plant's equivalent
  surface (the seed's verify discipline → the plant's validation playbook; the
  reviewer's checks → the plant's change guide; the kernel posture → the
  plant's instruction file; a template rule → the plant's matching template or
  convention), and land each rule where it acts, in the plant's idiom, sized to
  its budget. Collapsing the delta into one summary section of one file is a
  photocopy, not a graft — the plant's operating surfaces would keep steering
  every session exactly as before. The weave lands as a ratifiable proposal
  like any other rootstock-adjacent change, but it must exist, authored
  surface-by-surface, before the graft may close: a stamp advance with the
  substance undelivered is bookkeeping wearing an upgrade's name.

### Phase 6: Rebalance the plant toward pure graph (Sonnet audit → Opus authors)

The reconstruction pass, and the one home of the mandate's procedure.

- **(1) Inventory the drift (Sonnet scouts, read-only → a rebalance ledger).**
  Audit the plant against the pure-graph spec and record each shortfall with
  its location, the invariant it breaks, its natural graph home, and
  confidence. Hunt the standing drift classes:
  - **machinery outside the graph**: any protocol/skill/agent/method content,
    or any always-loaded instruction the kernel need not carry, that lives
    somewhere other than a routable `docs/graph/` node;
  - **a fact with two homes**: the same rule, topology, or contract stated in
    two nodes, or in a node *and* a hand-maintained projection or summary;
  - **a hand-maintained projection**: a tool-dir command, prompt, or view that
    was hand-edited instead of generated from its node, and has drifted from it;
  - **obsolete residue**: a superseded era's file, a dead compatibility shim, a
    tombstone with no pointer, a stale index or topology entry, interpreter
    bytecode carried into a machinery subtree by an older installer;
  - **substantive thinness**: real, load-bearing plant knowledge (deploy docs,
    per-repo READMEs, comment-only sharp edges) still living outside the graph
    structure (the (f) sweep, now standing);
  - **a collection the seed added after the base, filled elsewhere**: material
    a newer seed gives a collection of its own, authored under another home
    when no such collection existed (design material under `product/` from
    before `design/` shipped). A move, never a copy, and never an `ABSENT` row:
    copying makes a second home, and `ABSENT` makes a phantom gap the roster's
    `plant_knowledge:` then points into, so a cold session spawns the agent at
    the empty directory while the material sits unread. The audit carries a
    verdict for exactly that mistake, read under `graft.gate.coverage`.
- **(2) Reconstruct in slices (Opus authors), bounded by the rootstock line.**
  Move each item to its natural node home as a holistic MERGE, never a copy;
  collapse duplicate homes into one and trim restated facts to
  cross-references; regenerate a drifted projection from its node rather than
  hand-patching it; and list obsolete residue for the steward's explicit
  deletion confirmation (graft never deletes unprompted). Every relocation
  preserves the fact itself — the rootstock line holds; a fact the plant
  authored is re-homed, never lost — and each slice keeps the plant routable so
  the upgrade stays reversible.
- **(3) Leave the drift closed at its home.** Where the shortfall was a missing
  fitness function the seed now ships, install it; where it was a projection
  that drifted, the regeneration is the fix. Residue that could not be closed
  this pass is surfaced with a remediation, never silently carried. The ledger
  closes when every row is fixed or carried with a reason, and closing it is
  what `graft.gate.pure-graph` asks the reviewer to assert.

Split across parallel Opus authors when the rebalance is large; that
parallelism is exactly what `graft.gate.cross-author` exists to reconcile.

### Phase 7: Apply, verify, and stamp (`graft.integrity-gates`; Opus authors, session gates)

Apply the ratified upgrade **additively**, to a clean tree or to one whose
dirty paths the steward has accepted (*Reversibility*, (d)).

Then prove the plant is left more capable and no less itself. Every gate is one
row of the table below — that table is the single home for what a graft
asserts, and the record's integrity-gate block is its result column, never a
second list.

**Run them in this order, and name `--date` on every row that reads the `.bak`
set.** This is the one home of that caveat; the rows below pass `--date`
without re-explaining it. Left to itself the flag defaults to the newest `.bak`
stamp on disk, which is to say it follows whatever wrote last. **Three** of
this table's remedies re-run the installer and so write a fresh set of backups
under a new date: `graft.gate.projection-drift`'s regeneration,
`graft.gate.kernel`'s kernel fast-forward, and the fourth `STALE` condition
under `graft.gate.coverage`, whose remedy is an installer re-run for every
adapter in the stamp's `tools`. An audit taken after any of the three, with the
date left to default, audits the remedy's own writes and prints `clean` over
the graft it was supposed to examine. So: audit first, remediate second, name
the date every time, and after any remediating re-run re-audit under **both**
dates.

| Gate | Asserts | Command | On failure | Class |
|---|---|---|---|---|
| `graft.gate.backups` | every file `place_file` replaced is recoverable from a timestamped sibling. It does **not** assert that the backup set accounts for every byte the run destroyed: three writers replace with no backup, and *The installer is the hand that applies it* names all three | `tools/graft-audit.py <plant> <seed> --date=<this run's stamp>` classifies every fresh `.bak` and refuses a vacuous audit (zero for the named date while others exist); the totality property (M7) is proven seed-side by `tests/test-install-placement.sh` over a *discovered* destination set, whose sole exception is `is_installer_state()` and whose scope is stated with it | BLOCK: do not ratify an upgrade whose replaced files cannot be found. A no-backup replacement outside those three is a defect of the installer, not a class to accept | soft |
| `graft.gate.rootstock` | the rootstock line held: every plant-authored fact survived, and each write into plant-authored material was value-preserving and ratified | the same audit's *knowledge overwrite* count over `docs/graph/`, plus `git -C <plant> status --porcelain` scoped to non-machinery paths, plus `git -C <plant> diff docs/graph/index.md` by name, for the reason *The installer is the hand that applies it* gives | BLOCK: restore from the backup and re-reconcile | soft |
| `graft.gate.customization` | no plant divergence was buried by a blind fast-forward | `tools/graft-audit.py <plant> <seed> --date=<this run's stamp> --tokens=<plant tokens> --engine=<plant>/docs/graph/graph-lint.py:<seed>/templates/knowledge-graph/graph-lint.py` — `--date` is not optional here, for the ordering reason above | BLOCK: re-integrate each hit into the FF'd file as a holistic MERGE, or ratify it explicitly | soft |
| `graft.gate.kernel` | every kernel destination this plant carries holds the seed's `core/AGENTS.md` body | the same audit's kernel-currency check gates the exit code, but it reads exactly two files, `<plant>/AGENTS.md` and `<plant>/CLAUDE.md`. A plant whose stamp lists `github-copilot` has a third, and the audit is silent on it: add `cmp <plant>/.github/copilot-instructions.md <seed>/core/AGENTS.md` | BLOCK: see *When a gate blocks* | soft |
| `graft.gate.schema` | the plant's `_schema.md` still describes the machinery this graft installed | the same audit's node-schema line | report: it does **not** gate the exit code, so read the line; the remedy is a ratified MERGE (Phase 3) | detective |
| `graft.gate.engine` | the plant runs the seed's current graph engine, its own config preserved | the same audit's engine-currency check, via `--engine=<plant>:<seed>` — the **pair**; a single path is malformed and the audit refuses it rather than skipping the check | report: a `graph engine STALE` line does **not** gate the exit code, exactly as `graft.gate.schema` does not, so read the line. The one thing here that gates is a malformed or unreadable `--engine` pair, and it gates because the check did not run. Reconcile with `tools/graft-graph-engine.py`, or record a superset as KEEP-PLANT; this protocol's own contract is that a stale engine is not ratified | detective |
| `graft.gate.scaffolds` | no `docs/graph/` leaf is still byte-identical to its `templates/docs/**` template | `tools/graft-audit.py <plant> <seed> --unfilled` | BLOCK: see *When a gate blocks* | soft |
| `graft.gate.coverage` | every capability this graft carried was grown, or is answered | `python3 <seed>/tools/growth-audit.py <plant> <seed>` — non-zero blocks | BLOCK: see *When a gate blocks* | soft |
| `graft.gate.routes` | the upgraded graph routes and the agent router is clean | `python3 docs/graph/graph-lint.py`, a representative `--plan`, `python3 docs/graph/agent-lint.py --lint` and `--eval` where installed | BLOCK: fix the node, not the linter | soft |
| `graft.gate.status-register` | a migrated plant's lifecycle status is queryable and agrees with its index rows | `python3 docs/graph/status-register.py --root docs/graph` | BLOCK, or N-A where no status migration was ratified | soft |
| `graft.gate.prose` | the prose this graft authored into the plant meets the plant's own prose floor | `python3 docs/graph/prose-lint.py --file <node>` for each node Phases 4–6 wrote or re-wove (`--against <rev>` where the plant's Git state names one) | BLOCK the item: re-author; never lower the linter | soft |
| `graft.gate.adopted-instructions` | every instruction file the kernel replaced has a ledger row, and every ledger row has an owner | list this graft's kernel backups — `ls <plant>/CLAUDE.md.bak-<date>-* <plant>/AGENTS.md.bak-<date>-* <plant>/.github/copilot-instructions.md.bak-<date>-*` — and match each against `docs/graph/plans/adopted-instructions.md`. Three outcomes, and the command separates them: no backups and no ledger file is **nothing to report**; backups all matched by rows is the healthy replacement; a backup with no row is *Reversibility* (b) 3, the case that is permanent | report every unstruck row and hand it to `docs-librarian` — open librarian work, not a defect of this graft. BLOCK on an unmatched backup and file it by hand | detective |
| `graft.gate.recreated-nodes` | a node the installer re-created is re-applied or ratified, never silently reverted | the "re-created" notice in the **captured install log** (the run prints it once and stores nothing; re-running the installer cannot reproduce it, because the nodes now exist) | report each path; a deliberate deletion the steward confirms is re-applied, else ratified in the plant's record | detective |
| `graft.gate.roster-delta` | the specialists this graft added or renamed are handed to the plant's next session | diff the plant's `docs/graph/agents/` against the base seed's roster; cite `delegation.harness-registration` | report: this session cannot verify them spawnable, and saying it did would be the claim the fact exists to prevent | detective |
| `graft.gate.stamp` | the plant records the seed it now carries, with dated provenance | read `version` from `<plant>/.cypress/seed.json` and compare with the seed's `manifest.json`; `growth-audit.py` reports `STALE` when stamp and coverage record disagree | BLOCK: a stamp that disagrees with the coverage record means the upgrade was audited against a seed the plant does not carry | soft |
| `graft.gate.minimum-sufficient` | everything this graft added beyond the machinery contract earns its place | none — the graft reviewer (Opus) audits the additions against `docs/graph/method/engineering-posture.md`. Judge: the graft reviewer (Opus) | BLOCK that item; the rest of the graft may proceed | judgment |
| `graft.gate.projection-drift` | every tool-dir projection still matches the node it is a projection of | read-only, and in two halves, because the projections are of two kinds. Where the stamp's `agent_projections` entry says `"verbatim": true`, the projection is a placed copy, so `diff <plant>/docs/graph/agents/<n>.md <plant>/<adapter path>` is the whole check. Where it says `false` — `github-copilot`, whose views are transformed — `install.sh github-copilot --check` regenerates to a temp dir and diffs, writing nothing to the plant | BLOCK: regenerate by re-running the installer for the affected adapter, never hand-patch the copy. That re-run is an apply: it writes, it creates a new backup date, and a tree regenerated that way matches by construction, so it is a remedy and never the detector | soft |
| `graft.gate.pure-graph` | the Phase 6 rebalance ledger closed | none — **the graft reviewer (Opus), the same judge as `graft.gate.minimum-sufficient`**, reads the ledger row by row against the pure-graph spec: no seed-class machinery or superfluous always-loaded instruction outside a node, no fact with two homes, no unlisted obsolete residue. Judge: the graft reviewer (Opus) | BLOCK: or surface the residual drift with a remediation and a reason; never carry it silently | judgment |
| `graft.gate.cross-author` | a parallel absorption reconciled across author boundaries | none — **`docs-librarian` judges**, in one final spawn seeing the whole graph at once, followed by a structural audit, pass/fail per node. Judge: `docs-librarian`, in one final whole-graph spawn | BLOCK: see *When a gate blocks*; N-A where no phase used parallel authors | judgment |

**Every check names its command, or names the judgment and who owns it.** A
gate that runs but asserts nothing is a green lie, and so is a gate whose
evidence is a person's impression with no name attached. Every row whose
Command cell reads `none` names the judge instead; a blank cell is neither, and
the table has none.

The classes are ADR-0003's, as amended 2026-09-14: `hard`
(the **harness** refuses), `soft` (a contract **or a tool** refuses),
`detective` (post-hoc; it reports and a human acts), `judgment` (a named human
or agent decides and no tool can). Nothing here is `hard`. No harness prevents
a steward applying an upgrade, and a linter someone may decline to run is a
contract, not a harness — saying so is the point of the column.

**What `--tokens` is, and what a clean result is worth.** The customization
audit's whole verdict is bounded by the vocabulary it is given. Explicit tokens
are the plant's own name and paths, and they are always signal; the generic
self-reference list ("this project's", "our stack") counts only where the *seed
source* does not also carry the phrase, because a pristine charter reworded by
the seed matched one and was reported as a buried customization, and a gate
that cries wolf teaches a steward to ratify without looking. Derive the token
list from the plant, not from memory: its repository and product names, the
names in `.cypress/seed.json`, its top-level module and package names, its
domains, its service and environment names, and the identifiers its `product/`
and `nodes/` collections use for itself. Then say plainly in the record which
tokens were supplied — **a `clean` verdict is clean *for those tokens*,** and
an under-supplied list produces a reassuring pass over a real divergence. This
is the one home of that caveat; the record's integrity-gate block carries the
token list as data, not the explanation.

One companion caveat, about the other half of what the audit reads. An
*unmapped* backup, meaning a file the audit cannot tie to any seed source, is
reported as unresolved and fails, because unknown is not green.

**When a gate blocks.** These remedies do not fit a table cell:

- `graft.gate.kernel` has three verdicts. **Current** (byte-equal) passes.
  **Stale**, a seed line missing (so an old or hand-edited body), blocks:
  fast-forward the kernel body by re-running the installer for **each adapter
  this plant actually carries**, read from `tools` in `.cypress/seed.json`.
  Adapters are chosen per install, so there is no fixed set a plant "must"
  have; what must not happen is an adapter in that list being silently skipped.
  Then re-project the plant's own agents and skills into any adapter that lacks
  them, and re-audit under the new backup date as well as the graft's.
  **Extended**, the seed body plus plant-authored lines, blocks unless a
  standing `deviation.*` node with `departs_from: kernel.body` records the
  boundary, in which case the audit reports the deviation and its `ends_when`
  and passes. A kernel line the plant added is a departure from the pure-graph
  mandate: move it into a graph node the kernel routes to, or record that
  deviation. It is never silently fast-forwarded away — the installer's kernel
  pass rewrites the body, so re-apply the recorded lines after every graft and
  re-run the audit. The kernel is why this gate is not optional: it loads on
  every session of every adapter, yet `place_kernel` shares the two files by
  symlink and once left a stale body behind with no `.bak` at all, which made
  the customization audit blind to it.
- `graft.gate.scaffolds` blocks on a leaf that is a scaffold posing as
  knowledge, shadowing the authored leaf a cold agent needed
  (`grow.completeness-contract` owns the rule; `runbooks/verification.md` is
  exempt only while it carries an `executed` gate). List each one in the
  record. `--rename` is the default remedy — `<name>.unfilled.md`, a marker the
  installer honours so the blank is never re-created. `--prune` is a deletion,
  and deletions follow the rootstock line's second condition, so it runs only
  on the steward's own naming of the files. Prefer the rename regardless: a
  pruned leaf reappears at the next install or graft.
- `graft.gate.coverage` speaks in verdicts. `MISSING` or `BLANK` means this
  graft carried a capability it never grew; `UNGROWN` / `HOLLOW` / `UNGROUNDED`
  mean it grew one without the material — including a leaf edited just enough
  to stop being byte-identical, which is why substance and not path is the
  test; `CONTRADICTED` is the record disagreeing with the disk, and it arrives
  in two shapes a graft meets often. A row claimed `COVERED` whose own paths
  hold only scaffolds, `.unfilled.md` markers, or no leaf that states a fact —
  the shape a `plant_knowledge:` directory takes when a migration moved its
  material and the record was not re-planned. And a row claimed `ABSENT` whose
  searched paths include a filled leaf, or which names an expert that is on
  disk: something was there to read, it was found, and it was called absent.
  In both, the record is the half that is wrong; `UNSTAFFED` means a dominant
  domain or a core part of the stack never answered whether it warrants an
  expert of its own; `DANGLING` means a covered row cites evidence paths that
  are not there, and `UNJUSTIFIED` an absence with no reason or no paths
  searched; `SILENT` means a row this graft closed `UNKNOWN` (the owner's
  decision, by the record's own words) was never named in the Phase 8 entry:
  filed, not asked. **`STALE` is four findings wearing
  one word, and three of the four share a remedy the fourth does not.** Read
  which one the line says. A record naming no `seed_version`, a record planned
  against a different seed than the audit ran with, and a record whose
  `seed_version` disagrees with the plant's stamp are all fixed by re-running
  `--plan`, because auditing a stale record is how a graft reports coverage it
  never checked. The fourth is not about the record at all: a **stamp with no
  `agent_projections`** means nothing says where this plant's roster has to be
  spawnable from, so every expert passes the registration check by default.
  `--plan` does nothing for it. Re-run the installer for each adapter in the
  stamp's `tools`, then re-audit. Genuine absences pass as `ABSENT` with a
  reason and the paths searched, and named `UNKNOWN` blockers pass reported. A
  5.x plant meets this gate differently: its own experts live in the harness
  directories with no graph home, so they are invisible until migration step
  (c) relocates them, and then they surface as `MISSING` rows the record does
  not yet answer, which is the same gap wearing a shape this phase can act on.
- `graft.gate.cross-author` exists because a large migration, rebalance, or
  fact-sweep is real parallel work: Phases 3, 4, 5, 6 and step (f) each split
  across multiple Opus authors with disjoint file ownership, because that is
  what makes the absorption tractable. Disjoint ownership means nobody owned
  cross-file consistency, and two failure modes follow that no linter reports:
  a shared summary file (an `index.md` node table, a `root.md` topology map)
  that no single author's file list covered goes stale the moment any author
  changes something it depended on, and the same fact ends up restated in two
  files each author touched independently. One final `docs-librarian` spawn,
  seeing the whole graph at once the way disjoint authors structurally cannot,
  catches both, plus register drift (a passage that reads as bolted-on rather
  than woven). Follow it with a structural audit, pass/fail per node, for what
  `graph-lint.py` cannot see: it validates that edges *resolve*, not that they
  make *sense*. Is every node's `kind` the right one, does the plant's topology
  map list every node the migration or sweep added, and does every
  `requires:`/`peers:` edge reflect what the node's body actually depends on. A
  green `graph-lint` proves the graph is well-formed; skipping this step
  because the linter passed is exactly the gap it exists to close.

### Phase 8: Deliver (propose, then ratify)

Graft **proposes**; the plant's steward **ratifies**. Emit the reconciled
upgrade as a reviewable patch/proposal with the graft summary below, and add a
provenance entry to the plant's own `docs/graph/changelog.md` naming the graft.
Hand the KEEP-PLANT divergences back as harvest candidates, closing the loop
the other way. End with the single highest-leverage next step.

## Reversibility (`graft.reversibility`): what an unwind actually restores

A ratified graft is unwound from the backups the canonical writer left. This is
the procedure behind the claim; without it "reversible" is a promise nobody
priced.

**(a) Restore.** Every replaced file has a sibling named
`<path>.bak-YYYYMMDD-HHMMSS`, stamped at the moment it was written, so one
graft's backups share a date and span the run's duration rather than one exact
second. Group by date, never by second:

```sh
# what this graft replaced
find <plant> -name '*.bak-<date>-??????' | sort
# restore one file (the backup is the LINK OBJECT where the destination was a link)
mv <path>.bak-<date>-<time> <path>
```

Order matters on a multi-adapter plant. Restore `docs/graph/` first (it is the
one home, and the tool-dir trees are projections of it), then the adapter
trees, then the kernel **last**. The kernel is last for a reason the ordering
must state correctly, because the obvious reason is wrong: `mv <path>.bak-…
<path>` leaves `<path>` present, so the sibling symlink still resolves and
**nothing dangles**. The real hazard runs the other way. `place_kernel` `rm
-f`s the sibling and replaces it with a project-local symlink, so a plant that
carried two independent kernel files now carries a symlink pair, and restoring
only the real file leaves it paired for ever. **Restore both kernel backups**,
the real file and the sibling, and confirm afterwards that each is the kind of
object it was (`ls -l <plant>/CLAUDE.md <plant>/AGENTS.md`).

Files placed by `place_if_missing` left no backup because they only ever added.
Removing them is a **deletion**, with everything that implies here: the steward
names the files, explicitly (`graft.user-sovereignty`).

**(b) What an unwind cannot reach.** A steward calibrating risk needs every one
of these, and the list is closed only until the installer grows another writer.
Its criterion is the heading's, not "replaced with no backup": items 2 and 3
have a `.bak` and are still out of reach, and item 5 has none. Read the two
questions separately, because the backup scan answers only one of them:

1. **`.cypress/seed.json`.** Written by `place_state` with no backup, on
   purpose: it carries a fresh `installed_at` every run, so it is never
   byte-identical and a backup policy would leave one sibling per install for
   ever; and the next stamp is *derived* from this one plus the run's flags
   rather than authored, so a backup would carry no recovery value anyway.
   Recover it by re-deriving: re-run the base installer with the plant's
   recorded flags, or hand-write it from `installed_from` and the adapter list.
2. **A project's own root instruction file.** The `.bak` exists, but a backup
   is recovery evidence, not operational preservation — the content is out of
   force the moment the kernel lands. Its restoration is a *migration*, tracked
   in `docs/graph/plans/adopted-instructions.md` and owned by `docs-librarian`,
   not a `mv`.
3. **An instruction file replaced where the ledger row was never written.** The
   next run sees a kernel matching the seed, therefore no deviation, and files
   nothing; the original body sits in a backup nobody is told about. Three
   known paths reached it and all three are closed: the preflight refuses when
   `docs/graph/plans` is blocked, the orphaned-backup sweep re-files any
   repo-root kernel backup with no row, and a symlink at the note's own path is
   now moved aside instead of written through, which used to file the row
   outside the plant and leave the plant's ledger empty (M10 (1)). It stays on
   this list because the cost of missing it is permanent.
4. **A sibling kernel file that happened to match the seed.** `place_kernel`
   takes the sibling's backup only `if ! cmp -s "$seed_kernel" "$other"`, then
   `rm -f`s it unconditionally. No plant *content* is lost when the two
   matched. What is lost has no backup and no record: that the plant carried
   two independent files rather than a symlink pair, and — where `other` was a
   symlink pointing outside the target that merely resolved to matching bytes —
   the link itself, its target unrecorded.
5. **The `plant:` block of `docs/graph/index.md` as it stood before the run.**
   `fill_plant_facts` rewrites that frontmatter in place and takes no backup,
   so there is no sibling for step (a) to `mv` back and nothing for the backup
   scan in (c) to report. On a plant whose `index.md` is committed and clean
   the loss is nominal, because `git diff` shows the change and `git checkout`
   would undo it. On a plant where `index.md` is uncommitted or already dirty
   there is no committed version to diff against, and by (d) the graft has not
   put one there: it records Git state and never mutates it. The pre-run block
   is then both **unrecoverable and invisible**, which is the worse half. The
   defence is procedural and belongs before the run, not after it: capture
   `git -C <plant> show HEAD:docs/graph/index.md` alongside the install log,
   or commit the file first.

**(c) Verify the restore.** The same standard every other gate meets: a restore
is done when the graph routes and the audit agrees, not when `mv` exits 0.
Three things, in this order:

```sh
# 1. the backups this graft made are gone, because the restore consumed them
find <plant> -name '*.bak-<date>-??????'          # must print nothing
# 2. the plant routes on its restored engine
python3 <plant>/docs/graph/graph-lint.py
# 3. the restored tree matches the seed the plant came from
tools/graft-audit.py <plant> <seed-at-base> --date=<date> \
    --engine=<plant>/docs/graph/graph-lint.py:<seed-at-base>/templates/knowledge-graph/graph-lint.py
```

`<seed-at-base>` is a checkout of the seed at the version in the *restored*
stamp (`git -C <seed> worktree add <dir> v<base>`), never the seed you grafted
from. Read step 3's verdict for what it is. The graft's backups are gone,
consumed by the `mv`, so the backup scan can only report `zero backup files —
nothing was overwritten` (or refuse as vacuous, if backups from another date
remain, which is itself a finding: a restore left one graft's writes in place).
That line proves nothing about the restore. What proves it is the rest of the
same run, and the two halves of it are not worth the same. **Kernel-currency
gates the exit code**, and it now has to read the *base* seed as current, so a
non-zero exit here is a real finding about the restore. **Engine-currency does
not gate** (`graft.gate.engine`): it prints a line and returns success whatever
it finds, so a green exit code is not evidence the engine came back. Read its
line with your own eyes. Then confirm the stamp reads the base version, and
record the unwind in the plant's `docs/graph/changelog.md` the way the graft
itself was recorded.

**(d) Git is provenance here, not a mechanism.** Graft records the plant's Git
state and never mutates it, which means an unwind has no `git checkout` to fall
back on — only the backups, and on a dirty tree the backups cannot tell the
graft's writes from the steward's own uncommitted work. So the rule the apply
step obeys is: **a dirty tree is applied to only when the steward has named the
dirty paths and accepted that the unwind will be file-by-file from backups.**
The one moment that distinction is needed is the moment it would be gone.

## Provenance & the seed stamp

A plant that knows which seed version it carries can be grafted cleanly forever
after, because every future graft has a real **base** for its three-way merge.
`install.sh` writes that stamp: `.cypress/seed.json`, recording the seed name,
the version just placed, the date, the adapters installed under `tools`, the
owner's corpus and jurisdiction decisions, `agent_projections`, and
`installed_from` when it advanced over an older stamp. It is tracked, like the
coverage record beside it. Before 7.3.0 nothing wrote it and the marker was
whatever a steward happened to keep by hand, so a plant's base was frequently
unknown at exactly the moment a graft needed it. On the first graft of a plant
grown before the installer wrote stamps, reconstruct the base as best the
evidence allows; the install step of the graft then establishes it, and every
graft after that starts from certainty.

**How to read it.** This is the one home, and every phase that touches the
stamp reads it here. The stamp is a *record*, not a log of the last command
typed. A run merges into it and never narrows it: installing one adapter into a
plant that runs five adds that adapter and does not retract the other four,
forget `installed_from`, or reset the owner's corpus decisions. Consequences:

- **`tools` is the adapter list, it is per-plant, and it is a string.**
  Adapters are chosen at install time, so a plant carries exactly what its
  installs placed and nothing more. A phase that demands "each adapter" means
  each one this stamp names, never a fixed roster of five. Read it correctly:
  `write_seed_stamp` emits the adapter names **space-joined into one JSON
  string**, not as a JSON array, so every phase here that says "for each
  adapter in `tools`" means split that string on whitespace. `jq -r '.tools'`
  gives the whole line; `jq -r '.tools' | tr ' ' '\n'` gives the adapters.
  `agent_projections` beside it *is* an array of objects, so the two fields in
  the same file are read two different ways.
- **A stamp that exists but does not parse is corrupt, not absent.** The
  recorded decisions cannot be inherited, the installer says so out loud, and a
  graft re-derives them rather than treating silence as `undecided`.
- **The record is checked against the disk, not trusted over it.** A recorded
  `legal_corpus: yes` over a corpus that is missing pages restores the whole
  corpus and announces the restoration.

## The relationship to grow, harvest, and canonize

- `grow` installs and grows a **new** plant from the current seed; graft
  upgrades an **existing** plant to the current seed. Grow starts from a blank
  target; graft starts from a living one and reconciles.
- `harvest` is inbound (plant → seed) and `graft` is outbound (seed → plant).
  They share the corpus withdraw contract from opposite ends: harvest fills the
  corpus, graft withdraws from it into an already-grown plant. A KEEP-PLANT
  divergence graft finds is precisely a harvest candidate — the two protocols
  hand work to each other.
- `canonize` keeps the plant's **project-specific** knowledge in the plant's
  own graph; graft never disturbs it. When graft refreshes a library/tool
  surface, it is renewing the orientation layer canonize and ingest-library
  maintain, and it leaves every pinned fact those protocols recorded in place.

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

## Coverage after the graft (growth-audit; rows this graft answered)
- UNKNOWN carried: <row> — waits on <decision>, owner <who>   (each by name; the audit reads this entry)

## Grafted but not yet grown (inert machinery; deferred to real use)
- <capability> — present as machinery, ungrounded now; sprouts via <use / close-out>

## Pure-graph rebalance (Phase 6: drift closed toward the spec)
- <drift item> — <class: machinery-outside-graph / duplicate-home / drifted-projection / obsolete-residue / thin-knowledge> → re-homed into <owning node> (fact preserved) / regenerated / listed for deletion
- Residual drift carried (with remediation): <item — why it could not close this pass>

## Pre-graph knowledge swept (migration (f); N/A if not a pre-graph plant)
- <fact> — found in <plant source path>, woven into <owning node>

## Unfilled scaffolds (listed; renamed by default, pruned only on say-so)
- <docs/graph/<rel>> — renamed `<name>.unfilled.md` / pruned (steward: <who, when>) / filled by <author>

## Installer side-effects this graft produced (each needs an owner, not just a mention)
- Adopted instructions: <n> unstruck row(s) in docs/graph/plans/adopted-instructions.md → docs-librarian; kernel backups with no row: <paths, or none>
- Unbacked write to docs/graph/index.md: <git diff of the `plant:` block, or "unchanged">; pre-run copy captured: <yes / no — and if no, say so plainly>
- Destination symlinks the installer moved aside: <path → .bak-, or none>
- Re-created nodes: <path> — deliberate deletion re-applied / ratified (N-A on a stampless plant: the installer prints no notice)
- Roster delta (not assumed spawnable until the preflight confirms it): <specialists added or renamed>
- Flags used: <--force / --symlink / --copy / none>, and what that means for this record

## Shape migrations proposed (plant-authored artifacts in a superseded form; N/A if none)
- <artifact — form it carries → form the seed now defines, the version that changed it, what that buys, and the conversion; PROPOSED / RATIFIED / DECLINED. Never applied without the steward.>

## Status migrated (pre-7.0.0 plant; N/A otherwise)
- <status-migrate.py table: path — old value → `status` + companions; items reported-not-migrated, with the steward's `--map` decision>

## Integrity gate
<One line per row of the gate table, in its order, by its gate id — no row
omitted, none invented: `<gate id>: PASS / BLOCK / N-A — <the command's own
output that proves it>`. A `judgment` row carries its judge's name in place of
output. For `graft.gate.customization`, list the `--tokens` supplied and the
`--date` audited.>

## Recommended next step
<single highest-leverage action — usually "ratify and apply", "graft the next
sibling plant", or "harvest the flagged divergence back into the seed">
```

## Quality bar

The gate table above is what a graft is *held* to. This is what it is *judged*
on, the calls no gate makes.

A graft that passes:

- Reconciles every artifact three-way — fast-forwarding cleanly, preserving
  every plant divergence, and re-integrating true conflicts holistically for
  the steward, including a relocated plant expert/skill trimmed to genuine
  cross-references rather than left restating facts the graph already owns.
- Withdraws the corpus fruit the plant is due, re-pinning the plant's own
  version-specific facts fresh so nothing pinned is lost, and sweeps a
  pre-graph plant's own knowledge into the graph as part of the same migration.
- **Grows** the newly-delivered capabilities onto the plant where evidenced and
  necessary, and fabricates none — thin evidence defers, it does not invent.
- Rebalances toward pure graph on every graft, not only a legacy migration, and
  surfaces the residual drift it could not close with a remediation and a
  reason.
- Delivers the seed's substantive delta even to a plant that carries no seed
  machinery — re-authored into the plant's own surfaces as a complete,
  ratifiable proposal, never a raw copy and never a bare stamp advance.
- Says what its own verdicts are worth: which tokens the audit was given, which
  gates are judgment, and what the unwind cannot reach.
- Proposes for ratification; the steward decides before it lands.

A graft that fails:

- Half-migrates a 5.x plant — leaves the plant's own agents/skills in the old
  harness-only layout instead of relocating them into
  `docs/graph/{agents,skills}/`, or relocates them with frontmatter tagged on
  and content never reconciled against the rest of the graph (a "seed block
  bolted beside a plant block" restating facts the graph already owns instead
  of joining them).
- Upgrades a pre-graph plant's machinery and calls it done without sweeping the
  plant's own real knowledge into the graph — leaving the router current while
  most of the plant's actual facts still live outside the graph structure.
- Preserves a plant's local machinery divergence and never flags it upstream,
  so the improvement the plant made reaches no sibling.
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
- Splits absorption across parallel authors for tractability and then skips the
  single-spawn rebalance and structural audit, shipping a stale shared summary
  file or a fact restated across two author-touched files.
- Reports a gate green without the command's output beside it, or a `judgment`
  row green with no judge named.
- Reads an audit run *after* a remediating re-run as the graft's own verdict:
  the fresh backup date is the remedy's, and the graft went unexamined.
- Mutates the plant before the steward has ratified the reconciled result.

## What stays out of scope

- Graft does not start on its own. It is user-decided; the most an agent does
  unprompted is *propose* a graft, typically as the tail of a harvest, and
  stop.
- Graft does not touch the plant's application source, run its application
  builds or test suites, or fetch/switch/commit/push its Git state. It records
  Git state as provenance and runs knowledge-and-machinery checks only, which
  is precisely why the unwind is by backup file (see *Reversibility*).
- Graft does not rewrite a plant-authored fact on its own authority, and it
  never overwrites a pinned library/tool version the plant discovered: it
  renews only the version-durable surface and re-pins fresh. Where it does
  touch plant-authored material, both of the rootstock line's conditions hold.
- Graft does not modify the seed. A divergence worth flowing back is handed to
  `harvest`; graft only reads the seed and writes the plant.
- Graft does not collapse a three-way conflict by picking a side silently, and
  it does not apply an unratified reconciliation. The steward ratifies.
