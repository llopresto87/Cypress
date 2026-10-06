---
name: graft
description: The distribution arm of the cross-project meta-loop, and the complement of harvest. Once harvest has folded a mature plant's generalizable lessons back into the seed, graft carries that enriched seed outward onto an existing, already-grown plant — re-propagating the evolved kernel, protocols, skills, agents, templates, and shared tooling, and refreshing the plant's own library/tool pages from the seed's now-richer corpus — so a plant that grew from an older seed inherits the fruits of every harvest since, without being regrown from scratch. It upgrades a plant's seed-owned machinery only; the plant's own life — its source code and the knowledge facts it authored — stays exactly as the plant left it. Trigger is user-decided — the user starts a graft, or the system at most proposes that a plant is due for one (typically right after a harvest lands). Every upgrade is additive and proposed for ratification before it is applied; every replaced file is backed up by one canonical writer, and the unwind procedure, with the cases that are not recoverable named one by one, is stated in the protocol rather than assumed. A local divergence the plant made to its own machinery is preserved, never overwritten, and surfaced back as a harvest candidate.
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
est_tokens: 22017
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
The two share the corpus withdraw contract from opposite ends (harvest fills
the corpus, graft withdraws from it into a grown plant), and each hands work to
the other: a KEEP-PLANT divergence graft finds is a harvest candidate.
`canonize` keeps the plant's **project-specific** knowledge in the plant's own
graph, and graft leaves it in place: when graft refreshes a library/tool
surface, it renews the orientation layer canonize and `ingest-library` maintain
and keeps every pinned fact those protocols recorded.

## Trigger: user-decided; the system proposes, the steward starts (`graft.user-sovereignty`)

Like harvest, graft is **user-sovereign**. It changes an established, possibly
production plant, so the decision belongs to a human: the **steward**, the user
acting as the plant's owner, the two words naming the same person. The steward
decides when a plant is upgraded and ratifies the result before it is applied.

- **The user starts it**: by invoking this protocol or pasting
  `GRAFT_PROMPT.md` with a plant (or a set of sibling plants) as the target.
- **The system may propose it**: most naturally as the tail of a `harvest`:
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
- The plant's working tree is **clean**, or the steward has named its dirty
  paths and accepted a file-by-file unwind from backups, which cover only the
  files `place_file` replaced (*Reversibility*, (b) and (d)).

## The rootstock line: the heart of this protocol

Harvest's heart is the agnosticism gate: *nothing project-specific enters the
seed*, mechanically floored by `tools/agnosticism-lint.py`, which the graft
also installs into the plant as `docs/graph/agnosticism-lint.py` so a plant can
check its own harvest candidates before offering them. Graft's heart is its
mirror, the **rootstock line**: *every fact the plant authored about itself
survives the upgrade.* Draw it once and hold it through every phase. The two
gates point opposite ways: run the agnosticism lint on what the plant sends
*up*, and only there, because a plant's own knowledge names the plant,
correctly.

Two territories: graft upgrades the first and preserves the second, writing
into it only under the two conditions below.

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
  graph engine scripts `docs/graph/{graph-lint.py,spec-lint.py,grill-lint.py}`
  (and the config-free `agent-lint.py` / `agnosticism-lint.py` /
  `prose-lint.py` / `status-register.py`, which fast-forward), preserving the
  config each engine carries. Graft carries the seed's newest version of these
  onto the plant. `_schema.md` and `index.md` stay the plant's: they are
  project-instantiated (the engine-vs-instance rule, Phase 3).
- **The plant's own life (graft preserves, always).** The rootstock: the
  plant's application source, and every knowledge fact the plant authored under
  `docs/graph/`, its `nodes/`, `specs/`, `decisions/`, `libraries/`, `plans/`,
  `runbooks/`, product, architecture, API, and data collections, any graph node
  **without** `origin: seed`, and the pinned, version-specific facts in its
  library and tool pages. Its `deviation.*` nodes are the plant's own: a
  standing departure the plant chose is its truth, and graft keeps it as
  written. So is every `status:` frontmatter the plant authored: a fast-forward
  leaves each lifecycle state as the plant set it, and the ratified status
  migration below moves the plant's own recorded value into the plant's own
  frontmatter unchanged. Graft reads this territory to understand the plant and
  to place refreshed surface knowledge accurately; it treats every fact in it
  as the plant's to keep.

> **The rootstock line:** every fact the plant authored about itself survives
> the graft. A fact may be **re-homed**, into the node that owns it, into
> frontmatter, into a refreshed page's pinned block; it always arrives intact,
> and it moves only with the steward's ratification. A plant fact the graft
> corrects is retracted as `skill.holistic-editing` retracts a recorded claim.

Graft does write inside `docs/graph/`: Phase 4 refreshes a page surface, Phase
5 moves routing prose into an expertise node, Phase 6 re-homes a drifted fact,
and each migration below touches plant-authored material somewhere. Every such
write meets two conditions, and an upgrade that cannot meet both stops and
becomes a proposal for the steward:

1. **Value-preserving.** The fact arrives at the other end intact. A plant's
   library and tool pages are the standing example: they live in `docs/graph/`
   and are plant-owned, yet Phase 4 renews their version-durable orientation
   layer from the enriched corpus and re-pins the version-specific facts fresh
   against the plant's real lockfile. Graft renews the orientation and keeps
   every pin.
2. **Ratified.** The steward saw the change named, file by file, and said yes.
   Deletion needs more: an explicit confirmation that names the resource
   (kernel §4). Graft lists what it would delete and deletes only what the
   steward confirms by name.

## The pure-graph mandate (`graft.pure-graph-mandate`): every graft leaves the plant more purely a graph

The rootstock line is graft's conservative heart: *preserve what the plant
authored.* The pure-graph mandate is its reconstructive heart: *every graft
leaves the plant closer to the seed's architecture than it found it.* The two
are complements: the mandate refactors **structure, placement, and
projection**, and the rootstock line keeps every **fact** intact through the
move.

The seed's architecture is a **pure graph**: everything that can activate
progressively is a routable `docs/graph/` node; nothing about how to work is
always-loaded except a small bootstrap kernel; every tool-dir surface is a
*generated projection* of a node, not a hand-maintained copy; each fact has one
home; and no obsolete era, duplicate home, or competing doctrine survives.
Anywhere a plant falls short of that (machinery still living outside the graph,
a fact with two homes, an always-loaded file that should be a node, a
hand-maintained projection drifting from its source, dead compatibility
residue), **it is a drift from the spec, and closing it is in graft's scope.**
Beyond fast-forwarding files, graft drives the plant, end to end, toward
maximal pure graph.

Graft executes that drive as the **holistic reconstruction** the seed's own
rebalancing doctrine prescribes: reconstruct from evidence rather than
preference, move each fact to its natural owner, integrate each change into its
file (`skill.holistic-editing`), slice so the plant stays routable throughout,
and fix each drift at its home. **Phase 6 is the one home of that procedure**:
its ledger, its drift classes, and its worker classes are stated there and
nowhere else.

The mandate is **standing**. The pre-6.0 layout migration below and its
knowledge fact-sweep (step (f)) are its maximal instance, because a plant that
predates the graph needs the whole reconstruction; a plant one version behind
still runs Phase 6, lighter.

## The three-way reconciliation (`graft.reconcile-flow`): how the machinery is upgraded

A plant is not a blank target. Since it grew, its steward may have locally
sharpened a protocol, adjusted a setting, or fixed a script: the very kind of
divergence a future `harvest` exists to pull back. Graft respects that work by
reconciling three versions of every seed-owned artifact, exactly as a
well-behaved merge does:

- **base**: the seed revision the plant grew from (the tag of the stamped
  version, else inferred by content lineage; Phase 1 prints it; see *Provenance
  & the seed stamp* below);
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
  them as a single **holistic re-integration** (`skill.holistic-editing`):
  produce one coherent file that carries the seed's new capability *and*
  preserves the plant's intent, and surface it to the steward as a reviewable
  proposal. A three-way conflict is a decision, and the decision is the
  steward's.

A plant that deliberately carries no seed machinery, because its own
instruction system is the rootstock, classes all of that machinery as
KEEP-PLANT. It still receives the seed's substance: Phase 5 re-weaves the delta
into its own surfaces.

## The installer is the hand that applies it

The reconciliation decides; `install.sh` writes. What it does to a plant is
therefore part of this procedure, not an implementation detail behind it: the
whole safety story of a graft rests on properties of that one script.

**One canonical writer.** Every byte that replaces a seed-owned destination
passes through `place_file`, so the safety properties belong to the installer
rather than to whichever call site remembered them: a destination that is
already correct is left alone (no churn, no backup); a divergent destination is
moved aside to `<path>.bak-YYYYMMDD-HHMMSS` **first**; the backup is taken with
`mv`, which moves the link object, so a destination symlinked outside the
target is replaced rather than written through.
`tests/test-install-placement.sh` holds the installer to that over a
**discovered** destination set, so a destination added tomorrow is covered
without anyone remembering to add it, under three invariants it keeps separate:

- **M7, recoverability.** Every destination the run *replaced* has a
  timestamped sibling beside it. Its sole declared exception is
  `is_installer_state()`: `.cypress/seed.json` and
  `.cypress/recreated-nodes.txt`. Read the scope as carefully as the exception.
  The sweep reaches M7's branch only where the plant's edit is *gone*; a
  destination that still carries its edit is diverted one branch earlier, into
  M1's question of whether the installer still maintains it. So every
  `is_plant_owned()` destination, `docs/graph/index.md` among them, is answered
  by M1 and never evaluated for M7. The property is "what `place_file` replaced
  is recoverable", and it is silent about a writer that reaches a plant-owned
  file by another route.
- **M9, link uniformity.** Under `--symlink` every placed file is a link, or
  else one of three recorded exceptions: `is_plant_owned()`, because a
  plant-owned file must not be a link into the seed; `is_generated()`, because
  content generated per target has no seed original to link to; and
  `is_installer_state()`. M9 is about link mode, not backups.
- **M10, containment.** No write escapes the target directory, by any writer,
  through any symlink. `place_file`'s own `mv` covers `place_file` and nothing
  else, so M10 also holds the three writers that reach the filesystem past it:
  the note write described below; the destination preflight, for a symlink **to
  a directory** (such a link satisfies both `-e` and `-d`); and
  `fill_plant_facts`, which rewrites `docs/graph/index.md` in place, the one
  destination the installer does not reach through `place_file`, with a call
  that follows a link. M10 asserts: a link at a destination is moved aside
  rather than followed; a destination directory whose link resolves outside the
  target is refused before the first byte; the plant facts are not written
  through an `index.md` link that leaves the target; and a link that stays
  **inside** the target keeps working, because the rule is about leaving the
  target, not about links. A plant that uses symlinks is the plant this matters
  to, and it is the plant a steward is most likely to be grafting.

Read M9's exception list as link-mode exceptions only; read as M7's, it inverts
the gate. `place_generated` (slash commands, the transformed Copilot views, the
Codex snippet) sets `LINK_MODE=copy` and then **calls `place_file`**, so it
backs up exactly like everything else; `graft-audit.py` resolves those backups
through `generator_for()` and gives them a classification of their own,
comparing the replaced body against the generator for plant signal, since there
is no seed twin to compare it with.

**The preflight refuses before writing anything** when a destination directory
is occupied by a file, by a symlink to one, or by a dangling symlink; when a
destination directory is a symlink that resolves **outside** the target (M10's
second half); when a destination directory exists and is not writable; and when
`docs/graph/plans` is blocked. The refusal names every offending path and
leaves nothing on disk. A destination symlink that stays inside the target is
allowed, so a plant that arranges its own directories with links is not refused
for doing so.

**What the writer does not cover.** Five paths reach the filesystem without
`place_file`, and **three of them replace bytes with no backup**, so
`find <plant> -name '*.bak-*'` does not account for every byte a run replaced:

- `place_state` writes `.cypress/seed.json` and `.cypress/recreated-nodes.txt`,
  replacing both with no backup. They are M7's one recorded exception, and the
  only *declared* one.
- `place_if_missing` places the scaffold leaves, `_schema.md`, `index.md`, and
  the graph engines (`graph-lint.py`, `spec-lint.py`, `grill-lint.py`). It only
  ever **adds**, so there is nothing to back up and nothing M7 asks of it.
  Their fast-forward is Phase 3's engine reconciliation.
- `fill_plant_facts` rewrites `docs/graph/index.md` in place, with no backup:
  **a write into a plant-owned file**, the same file the territory list above
  declares the plant's. It is *bounded in content*: it fills placeholder
  `plant:` values and adds a missing key in the template's own words, and every
  value the plant declared stays. It is *bounded in frequency*: it writes only
  when the rendered frontmatter differs from what is on disk, so a run that
  changes nothing touches nothing. Neither bound makes it recoverable.
  `graft.gate.rootstock` has no `.bak` to read, so
  `git -C <plant> diff docs/graph/index.md` is the only thing that sees the
  write. Read that diff before ratifying; *Reversibility* (b) 5 covers a plant
  with no committed version to diff against.
- `record_instruction_migration` creates and appends to
  `docs/graph/plans/adopted-instructions.md` with shell redirection. It guards
  the create on `! -e`, which is **false for a dangling symlink**, so it treats
  a symlink at that path the way `place_file` treats any destination link: the
  link object is moved aside as a `.bak-`, a warning names where it went, and
  the note is written as a real file inside `PROJECT_DIR`.
  `tests/test-install-placement.sh` pins it as M10 (1).
- `place_kernel`'s sibling branch `rm -f`s the second of `CLAUDE.md` /
  `AGENTS.md` unconditionally and replaces it with a project-local symlink. The
  backup before it is guarded on `! cmp -s` against the seed kernel, so a
  sibling that happened to match the seed goes with nothing left behind
  (*Reversibility*, (b) 4).

**The instruction ledger is work, not a note.** When the kernel replaces a
project's own root instruction file, the old body survives as a `.bak` and
stops being in force. So the installer files it: `record_instruction_migration`
appends one row per replaced instruction file, addressed to `docs-librarian`,
with a table of where each kind of instruction belongs. Nothing is migrated
automatically, on purpose. Two consequences for a graft: the note lands inside
`plans/`, the one subtree this protocol's own audit treats as untouchable, so
the graft reports it (`graft.gate.adopted-instructions`); and a run whose note
write failed after the kernel was already swapped is not filed by the next run
either (*Reversibility*, (b) 3). The preflight refuses a blocked
`docs/graph/plans`, and `sweep_orphaned_instruction_backups` catches the
general case by re-filing any repo-root kernel backup with no ledger entry.

**The installer's two prior-install safety nets.** The orphaned-backup sweep
and the re-created-node notice (below) are both gated on `PRIOR_INSTALL`. The
installer sets it before its first write, where `.cypress/seed.json` already
exists or `docs/graph/protocols/` already holds a node; in the second case it
also warns that the plant's record is missing and that the recorded owner
decisions cannot be recovered from disk. On a target with neither, such as a
pre-6.0 plant that has no stamp, both nets are silent: the sweep returns early
and files nothing, and the notice prints nothing.

**The flags, and what a steward must know about each.**

- `--force` suppresses the per-file `backed up existing …` warning; the backup
  is always made. Prefer a graft without it: those warnings are the cheapest
  divergence signal there is, and the customization audit is a slower second
  opinion, not a replacement.
- `--symlink` places links into the seed instead of copies, and it changes what
  a graft *means*. A symlinked plant's machinery moves whenever the seed moves,
  and an edit to a placed file writes back **into the seed**, so `ours` and
  `theirs` are the same file, the three-way reconciliation has nothing to
  reconcile, and what looks like a plant divergence may be a seed edit. Graft a
  copy-mode plant in copy mode, the default. If the plant is already symlinked,
  say so in the graft record and treat every apparent KEEP-PLANT as unverified
  until its provenance is established.
- `--copy` is the default and the way back. Switching an already-symlinked
  plant to copies is a real, graft-relevant operation: it restores the `ours` /
  `theirs` distinction the three-way reconciliation needs, and it is a
  **write**: every link is replaced by a file, each one through `place_file`,
  so it produces a full set of fresh backups and a `graft.gate.customization`
  run of its own. Do it as a ratified step of its own, before the
  reconciliation, because a flag flip in the upgrade run shares its `.bak` date
  with the version advance and the two become indistinguishable.
- The four plant facts (`--environment-class`, `--commit-attribution`,
  `--deliverable-language`, `--comment-language`), `--legal-corpus` and
  `--legal-jurisdiction` are the **owner's** recorded decisions. A run that
  passes no flag inherits what the stamp already holds; only `undecided` is
  overwritten by silence. A graft carries each decision from the stamp or asks
  the owner; it never infers one from the plant's contents.
- `--expertise <id>,...` is the owner's decision too, and an additive one: it
  places the listed corpus pages and adds them to the record, and a run with no
  flag re-applies the record. `--expertise propose` writes nothing and is safe
  on any plant at any time. Phase 4 owns both uses.

The stamp the run writes is the last additive step of a successful upgrade:
`write_seed_stamp` runs after every adapter, after the re-created notice and
after the orphaned-backup sweep. So a stamp at the new version is evidence the
run reached the end, and `graft.gate.stamp` reads it that way. How to read the
stamp's *contents* is one fact with one home, *Provenance & the seed stamp*
below.

**Check every re-created node.** The installer tracks seed-owned graph nodes
that were *absent* from a plant that already carried the seed, and prints a
"re-created" notice for them once, after the last adapter has run. That is
correct fast-forward behaviour, and it is also exactly how a plant's
**deliberate deletion** gets silently reverted (`graft.gate.recreated-nodes`).
Two properties bound what the notice is worth. It is gated on `PRIOR_INSTALL`
(above), so a target the installer did not recognise as a prior install gets
none, and the gate is N-A there rather than clean. And the console stops at ten
paths: the whole list is in `.cypress/recreated-nodes.txt`, which every run
that writes the stamp rewrites. A re-run lists none of them, because the nodes
now exist, so **read the file before any remedy re-runs the installer** and
cite it as the gate's evidence.

## Provenance & the seed stamp

A plant that knows which seed version it carries can be grafted cleanly forever
after, because every future graft has a real **base** for its three-way merge.
`install.sh` writes that stamp: `.cypress/seed.json`, recording the seed name,
the version just placed, the date, the adapters installed under `tools`, the
owner's corpus and jurisdiction decisions, `agent_projections`, the corpus
pages the owner chose to place (`expertise`: one entry per page, with its
corpus id, its placed path and the SHA-256 of the bytes the installer wrote),
and `installed_from` when it advanced over an older stamp. It is tracked, like the
coverage record beside it. A plant grown before 7.3.0 has no stamp, because
nothing wrote one then. On its first graft, reconstruct the base as best the
evidence allows; the install step of the graft then establishes the stamp, and
every graft after that starts from certainty.

**How to read it.** This is the one home, and every phase that touches the
stamp reads it here. The stamp is a *record*, not a log of the last command
typed. A run merges into it and never narrows it: installing one adapter into a
plant that runs five adds that adapter and does not retract the other four,
forget `installed_from`, or reset the owner's corpus decisions. Consequences:

- **`tools` is the adapter list, it is per-plant, and it is a string.**
  Adapters are chosen at install time, so a plant carries exactly what its
  installs placed and nothing more. A phase that says "each adapter" means each
  one this stamp names, never a fixed roster of five. Read it correctly:
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
- **`expertise` is a record of placed pages, and silence keeps it.** A run
  with no `--expertise` flag re-applies every entry; a run with a list adds
  its ids to the entries already there. No run removes an entry or deletes a
  placed page, so a dependency the plant has dropped keeps its entry until the
  owner removes it from the stamp by hand. A plant that never used the flag has
  no `expertise` key at all, and none appears. Phase 4 reads it.

## The flow

Orchestrated like `grow` and `harvest`: the session plans, briefs, reconciles,
and delivers; clean-context workers survey and author. Model classes follow
`delegation.model-classes`: **investigation-class** workers survey and classify
(read-only); **authoring-class** workers perform every reconciliation, holistic
merge, corpus refresh, and validation. Every spawned worker executes the
canonical GRAPH DISCIPLINE block of
`docs/graph/templates/prompts/graph-session-bootstrap.md` (the one home for the
worker discipline; briefs embed it, this file only points at it) and returns
the `--plan` command, the loaded closure, and its deliberate skips. Where the
host supports model-class selection and clean-context spawning, honour it.
Where it cannot, report that this host cannot execute the seed's operating
model; the workers' work does not collapse into the main chat.

### Phase 1: Locate the plant and establish the base (session + investigation class)

Identify the plant or the set of sibling plants in scope, and for each record
its path, host integration (`.claude/` / `.prime/agent/` / `.opencode/` /
`.codex/` / `.github/`), current branch, HEAD, and worktree cleanliness, as
read-only provenance (*Reversibility*, (d)). Read the plant's **seed stamp** to
learn the base version it carries;
`python3 <seed>/tools/graft-ledger.py <plant> <seed> --base` prints the base:
the stamped version's tag, or else the seed commit the plant's machinery
matches best, with the match count. With no stamp the base is that inference,
and this graft establishes the stamp. A corrupt stamp is reconstructed the same
way (*Provenance & the seed stamp*), and the record says that the plant's
recorded decisions were re-derived rather than inherited. A target with no
stamp and no `docs/graph/protocols/` node is also where the installer's two
prior-install safety nets are silent (`graft.gate.recreated-nodes` is N-A, and
no orphaned kernel backup is swept), so that graft owes the closest reading of
the install output. Confirm the seed's own version and what has changed between
base and now (its CHANGELOG and harvest log are the map of available fruit). A
clean working tree here makes the whole upgrade easy to review and to unwind.

### Phase 2: Survey the drift (investigation-class scouts, read-only)

The machinery half is a command, not a guess:
`python3 <seed>/tools/graft-ledger.py <plant> <seed>` prints one row per
seed-owned file with its three-way class (the tool's docstring defines each).
Dispatch read-only scouts to inventory the **fruit the plant can withdraw**:
the libraries, tools, and, where the plant is subject to externally-authored
rules, the legal instruments the plant actually reasons against (from its
`docs/graph/libraries/`, `docs/graph/tools/`, and `docs/graph/legal/`) for
which the seed's `library-corpus/`, `tool-corpus/`, or `legal-corpus/` now
holds a page the plant predates or lacks. The **graft ledger** is the tool's
table plus one row per withdrawable page, with provenance (plant path, seed
source, base state). Claims cite paths; centralized prose is an untrusted clue
until corroborated against the installed files.

### The migrations (`graft.migration`): between the survey and the reconcile

A plant can be behind the seed in ways no file-for-file fast-forward reaches.
Its machinery may sit in a layout the seed has replaced; its lifecycle state
may be recorded where nothing can query it; its own artifacts may carry a form
the seed has since redefined; what its sessions learned may sit in harness
memory instead of the plant. The four subsections below are one fact and one
slot in the flow, and they are independent of each other: a plant may owe all
four, one, or none. Each is proposed, ratified, and recorded separately. Before
the graft calls any migration optional, it reads the plant's operator node
(`crosscut.operator`, the seed's node kind from
`templates/docs/nodes/_operator.template.md`): an owner rule recorded there can
make that migration owed.

#### Layout migration: 5.x → 6.0.0

The survey may find a **pre-6.0 plant**: its machinery lives in the old
tool-dir layout (`.claude/protocols/`, `.claude/templates/`, `.claude/core/`,
and the `.opencode/` / `.codex/` / `.github/` equivalents) instead of the graph
subtrees `docs/graph/{protocols,skills,agents,method,templates}/`. Such a plant
is not fast-forwarded file-for-file; it is **migrated**, and the migration
threads through the phases that follow:

- **(a) Install the new machinery into `docs/graph/` as usual, and read what
  the install says it did.** The installer places the seed's current protocols,
  skills, agents, method nodes, and template artifacts as `origin: seed` graph
  nodes, and regenerates the agent/skill harness projections. Phase 3's
  reconciliation then runs against these new homes. The preflight may refuse
  the run before its first write (*The installer is the hand that applies it*);
  fix what it names and re-run. **Redirect the output to a file** and keep it.
  The `adopted-instructions` warning, the displaced-symlink warning, and the
  per-file backup warnings are how a reader learns what to look for before
  Phase 7 goes looking.
- **(b) Diff the old tool-dir copies against their seed base; the plant's
  customizations survive the move.** Each old copy under `.claude/protocols/`,
  `.claude/templates/`, `.claude/core/` (and kin) is three-way-compared against
  the seed revision the plant grew from. A pristine copy needs nothing; a
  **plant-local customization** is carried into the corresponding graph copy as
  a holistic MERGE (Phase 3's discipline), so the new layout arrives already
  carrying the plant's intent. And exactly as this protocol already holds for
  KEEP-PLANT: a local divergence is also a **harvest candidate**, so hand it
  back that way.
- **(c) Relocate the plant's own agents and skills into the graph, and
  reconcile them.** A 5.x plant's *plant-authored* machinery, the experts and
  project skills it grew (`origin: project`, not seed-owned), sits in the
  harness dirs (`.claude/agents/*.md`, `.claude/skills/<name>/SKILL.md`) with
  no `docs/graph/` home. The 6.0.0 layout is where **every** agent and skill
  node lives, seed-owned or plant-owned, so a plant left with its own
  agents/skills in the old spot is half-migrated: the router cannot route them,
  and graph-lint cannot see them. Relocating alone is not reconciling. Promote
  each into `docs/graph/{agents,skills}/`, adding the node frontmatter it lacks
  (`id`/`tier`/`kind`/`origin: project`/`title`/`owns`/`est_tokens`, reusing an
  agent's `routing_triggers` as its `load_when`, and, for an expert,
  `plant_knowledge:` naming the collections or expertise nodes it must be able
  to read, without which the relocated expert lands as a node the coverage gate
  cannot answer for). Then read its content against the rest of the graph,
  because a plant-authored expert that predates the graph was written with no
  graph to defer to and will almost certainly restate facts the graph's
  crosscut/platform/subsystem nodes already own (an auth mechanism, a secrets
  inventory, a platform topology). Trim every restated fact to a genuine
  cross-reference (name the owning node), keeping only the routing charter and
  the facts this node is the true, sole home of: exactly the treatment Phase 3
  gives a MERGE. **The projection then follows from the graph on its own.**
  `project_agents` and `project_skills` read the *plant's*
  `docs/graph/{agents,skills}/`, not the seed's, so re-running the installer
  for each adapter the plant carries projects the relocated node like any
  other, once the node sits where the projection reads
  (`delegation.harness-registration`). Copilot's views are transformed rather
  than copied, so they are not byte-identical by design, and
  `agent_projection_for` records which adapters are verbatim. That reconciliation is authoring-class work, and its
  result is additive: it lands in the ratifiable proposal like every other
  migration step.
  This step is not bound to the 5.x layout. A plant of any version can author
  an agent or skill straight into a harness directory, and it is then just as
  invisible to the router and to every other harness. On every graft,
  `install.sh <host> --check` and `tools/graft-audit.py` name each such entry
  `ORPHAN` (SPEC-0001 CHECK_FLAGS_ORPHAN_HARNESS_ENTRY), and the graft proposes
  its relocation into `docs/graph/{agents,skills}/` by this step. The flag
  writes nothing and deletes nothing; the harness copy stays until (d).
- **(d) List the now-redundant old machinery for the steward's deletion.** Once
  the graph homes and projections exist, the old tool-dir copies are redundant.
  Graft lists every such file by name and deletes only what the steward
  confirms **explicitly, by name** (rootstock condition 2). Until then they
  stay in place, inert. List Python bytecode found inside a machinery subtree
  (a `__pycache__` or `.pyc` file an older installer carried in) the same way:
  it has no seed source, so it is residue for the steward's deletion, never an
  artifact to reconcile.
  This step is not bound to the 5.x layout either. When the seed folds a node
  away (a skill merged into a protocol, an agent renamed), the plant keeps the
  old `origin: seed` node in `docs/graph/` and the installer goes on projecting
  it, so the harness loads machinery the seed retired. On every graft,
  `install.sh <host> --check` and `tools/graft-audit.py` name the node and each
  projection of it `RETIRED` (SPEC-0001 CHECK_FLAGS_RETIRED_HARNESS_ENTRY).
  List each one here for the steward's deletion by name, with the seed node
  that now owns its content where one does, and the harness copy of a relocated
  `ORPHAN` beside them. Neither the installer nor the audit deletes one: the
  deletion is the owner's act (the owner decided on 2026-10-04 that such
  entries are flagged, never deleted).
- **(e) Rewrite stale references in plant-authored docs only with consent.**
  Plant-authored pages may cite the old paths (`.protocols/x.md`,
  `.skills/<name>/SKILL.md`, `.templates/…`, `.core/operating-principles.md`).
  Rewriting them to the `docs/graph/…` homes touches the rootstock, so graft
  first lists **every file it would touch** with the exact rewrites, and
  proceeds only on the steward's consent.
- **(f) Sweep the plant's own pre-graph knowledge: a migration this old owes a
  fact-sweep, not just a machinery swap.** A plant old enough to predate the
  graph architecture entirely was never run through `adopt-existing` or
  `ingest-library`: its real, load-bearing knowledge (deploy-pipeline docs,
  per-repo READMEs, sharp edges recorded only in a comment, drift between what
  a config claims and what the code does) has had nowhere to land and was never
  captured. Finishing (a) to (e) leaves the graph *structurally* current (the
  router works, the machinery is in place) while leaving it *substantively*
  thin, a plant whose facts still mostly live outside the graph structure, in
  the repos the graph is supposed to orient a reader away from re-reading.
  Dispatch read-only scouts across the plant's actual source, not just its
  machinery, to inventory facts missing from the graph, cross-checked against
  what existing nodes already own so nothing already-covered is re-reported,
  then hand confirmed findings to authoring-class authors to weave into the
  owning node. This sweep is **part of the migration** for any plant old enough
  to have predated the graph, and the graft runs it without a separate request
  from the steward.

The migration's outcome feeds Phase 7 unchanged: the audit runs over the
backups, the redundant-copy list and any un-consented reference rewrites appear
in the proposal, and the stamp records the plant as a 6.0.0-layout plant.

#### Status migration: pre-7.0.0 → 7.0.0

A plant grown or last grafted before 7.0.0 carries lifecycle status as body
prose (an ADR's `## Status` line, a spec's `**Status:**` bullet) in a
vocabulary per kind, which nothing can query and which drifts from its index
rows. The graft runs
`python3 <seed>/tools/status-migrate.py --root <plant>/docs/graph` (dry run)
and reports its table in the graft record; on the steward's ratification it
re-runs with `--write`, moving each value into frontmatter in the schema's one
vocabulary (`docs/graph/_schema.md` §"Lifecycle status") and leaving the body
line as a pointer. What the tool cannot map it reports rather than invents: a
threat model's `active` means "in force", not lifecycle debt, and its new home
is the steward's call via `--map`; a companion the old record never stated is
written `not recorded: <why>`. This moves plant-authored frontmatter, so it
runs only on ratification, and it moves the plant's own value unchanged (the
territory list above). The installer has already placed
`docs/graph/status-register.py`; Phase 7 runs its lint after the write
(`graft.gate.status-register`).

#### Shape migration: plant-authored artifacts whose form the seed has changed

The migrations above move things the seed owns. This one does not, and that is
the whole difficulty: a plant's own records (its plan-of-record, its specs, its
nodes) are never fast-forwarded, because they hold decisions no upgrade may
touch. But the seed sometimes changes the *shape* such an artifact is meant to
take, and a plant left in the old shape is not wrong so much as stranded: it
still lints, it still reads, and it no longer gets the property the new shape
was introduced for.

So a shape migration is a **proposal about the plant's own content**: the graft
notices the old shape, says what the new one buys, shows the conversion, and
stops. The steward ratifies; the plant's own authors do the work.

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
2. Replace §9's body with an index, one row per increment, the last cell naming
   the file: `| # | Increment | Status | Detail |`.
3. Leave every other section where it is. Only §9 moves.
4. `python3 docs/graph/grill-lint.py` must pass afterwards. It resolves the
   index, enforces the same required fields inside each child, and refuses a
   row with no file, a file no row points at, and an increment defined twice.
   It checks the form. That nothing moved is checked by `verify-ledger.py`:
   `python3 <seed>/tools/verify-ledger.py --monolith <copy> --ledger docs/graph/plans/grill.md --leaves docs/graph/plans/grill/`,
   where `<copy>` is the plan as it stood before step 1, must rebuild it byte
   for byte.

Convert **one increment at a time**: both forms lint, so a half-migrated plan
is a valid plan. The plant's own authors convert it; `plans/` is deliberately
outside graft-audit's machinery subtrees, so a backup over a plan record
reports as buried plant knowledge rather than a routine upgrade. That is the
protection, and the migration respects it by being a proposal. It is also why
the installer's own write into that subtree, the adopted-instructions ledger,
has to be reported by hand.

The same three questions apply to any future shape change: **what form does the
plant carry, what does the new form buy it, and what is the conversion**, asked
about the plant's content, answered in the graft record, decided by the
steward.

#### Memory migration: from harness memory to a session record (7.31.0)

The kernel's §3.2 says harness memory is not a home: a session starts from the
newest record in `docs/graph/plans/sessions/` and writes what it learns there
for canonize (`stewardship-posture.session-record`). A plant grown from a seed
older than 7.31.0 may keep what its sessions learned in the host's memory,
which lives outside the plant, so no fast-forward reaches it. The graft moves
it once:

1. Read the harness memory this session can reach, **read-only**. Where each
   host keeps it is that host's fact, not this protocol's.
2. Write the plant's first session record in `docs/graph/plans/sessions/`, from
   the seed's form
   (`templates/docs/plans/sessions/_session-record.template.md`; the plant's
   own copy arrives only with the installer re-run), listing every entry in its
   "Harness memories to migrate" table. Like every migration here, it is
   proposed first and written once the steward ratifies it.
3. The graft's own canonize close-out files the record
   (`canonize.session-record`). What happens to each harness entry after that
   is `stewardship-posture.session-record`'s. The graft leaves harness memory
   as it found it; retiring an entry is the steward's decision, by name.

A plant whose host holds no memory for it owes this migration nothing. The rest
of the change needs no migration. The §3.2 sentence arrives with the kernel
fast-forward, so a kernel diff that adds it is expected, and
`graft.gate.kernel` checks the result. The form,
`docs/graph/plans/sessions/_session-record.template.md`, is added by the
installer's scaffold walk because it is missing, and `graft.gate.rootstock`
reads it as an expected new file.

### Phase 3: Reconcile the machinery (authoring-class authors)

For each ledger row, act on its class: nothing on CURRENT; adopt on
FAST-FORWARD and SEED-NEW, and on HARVESTED, whose plant lines a harvest
already carried into the seed, so it raises no candidate. A file where the
plant removed a line the seed still carries is MERGE, whatever the plant added.
Retain and raise a harvest candidate on KEEP-PLANT; author one holistic
re-integration on MERGE. Every merged file arrives whole, integrated as if it
had always read that way. Each reconciliation records its provenance: base
state, decision, and what the plant kept.

**The roster delta may not be spawnable in this session.** Reconciling the
agent nodes rewrites the harness projection mid-session, and when a host sees
such a write is host-dependent, so every specialist the seed *added or renamed*
since the plant's base is on disk and may be unspawnable for the phases that
follow. Preflight before dispatching by name, and take the remedy or the
recorded fallback in `docs/graph/method/delegation-bounds.md`
(`delegation.harness-registration`). Carry the delta forward as a named list;
Phase 7 reports it.

**The graph engines are machinery too, and the installer does not fast-forward
them.** The installer drops the knowledge-graph scaffold (`graph-lint.py`,
`spec-lint.py`, `grill-lint.py`, `_schema.md`, `index.md`) *only if absent*, so
a plant that already has them keeps its old engines across a graft's install
run and misses every linter improvement since it grew. A plain re-install
leaves a placed engine as it is: an existing plant receives a new engine by
graft only, and this step is where it does. (The config-free `agent-lint.py`
fast-forwards with the rest of the machinery; see the territory list.) **Bring
all three engines current.** Reconcile each explicitly, as a config-preserving
fast-forward: adopt the seed's current engine body and re-inject the PROJECT
CONFIG that engine carries (`ROOT_ID` / `KINDS` / `KIND_PREFIX` in
`graph-lint.py`; `TEST_GLOBS` in `spec-lint.py`; none in `grill-lint.py`, whose
reconciliation is a plain fast-forward with a backup).
`tools/graft-graph-engine.py` picks that set from the plant file's name when no
`--preserve` is given, and an explicit `--preserve` wins. The plant gains the
engine, keeps its configured identity, and a knob it predates adopts the seed
default. **Union a config knob the seed has extended since the base.** The
load-bearing case is `KINDS`: 6.0.0 added the machinery kinds
`protocol`/`skill`/`agent`/`method`, so keeping the plant's older `KINDS` set
verbatim would drop them and every newly-installed machinery node would fail
lint with `kind not in KINDS`. The union keeps the plant's own kinds *and* adds
the seed's new members; only a scalar identity (`ROOT_ID`) or a plant-list
(`TEST_GLOBS`) is kept wholesale. Where the plant's engine is a strict
*superset* of the seed's, that is a KEEP-PLANT (the plant is ahead) and a
harvest candidate. `tools/graft-graph-engine.py` performs exactly this merge
(set-valued knobs unioned, others kept wholesale) and the superset detection.
This is the **engine-vs-instance rule**: the engines are reconciled, while
`_schema.md` and `index.md` stay the plant's (they are project-instantiated,
and copying the seed template would regress placeholders and wipe the authored
router). The engine is what makes the `composes` rules enforceable on this
plant at all: that every composed id resolves and both ends are
`kind: expertise`, that `composes` is acyclic on its own, that a node which
`requires` an expertise parent is listed in that parent's `composes`, and that
an expertise node carries at least one depth edge to the pin or standard it
routes to. A plant on the old engine is not failing those rules. It is not
being asked them.

**`TEST_GLOBS` is kept wholesale, and kept is not confirmed: put it to the
steward as a fact.** Which directories hold the plant's tests is an owner fact
(`grow.plant-facts` owns the ask and why a scout can only propose it). A plant
grown before that ask existed, or one whose test layout has moved since it
grew, carries globs nobody confirmed, and the config-preserving fast-forward
carries them forward unexamined. The seed's default reads only the
conventional unit layouts, so a plant whose tests are black-box checks in a
directory of another name (end-to-end suites, shell checks, smoke or contract
runs against a live service) reports that the globs matched zero files the
moment it has a live spec, and a plant with none yet reports nothing at all.
So after the engine is reconciled, print the files the kept globs resolve to
(`python3 -c "import runpy; print(runpy.run_path('docs/graph/spec-lint.py')['test_files']())"`)
beside the test directories the Phase 2 survey found and the runners the
plant's build and CI invoke. Where the globs are still the seed's default, or
miss a directory the survey found, or match files that are not tests, put the
layout to the steward as a numbered decision (`deliver.numbered-decisions`):
the proposed globs, each directory left out and why. Write the confirmed globs
into the reconciled engine; never widen the seed's default to cover a layout
nobody confirmed. An unanswered layout stays an open item, steward named, in
the Phase 8 entry, and the kept globs stay as they were.

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
therefore kept by the post-FF audit (Phase 7, `tools/graft-audit.py`): any
seed-owned file whose backup differs from the seed *and* carries plant-signal
content is a divergence the graft re-integrates into the FF'd file or puts to
the steward to ratify. Know what the audit's map reaches, because a path it
cannot map is a path it cannot classify: every adapter tree including
`.prime/agent/`, the harness projections of agents and skills, the machinery
subtrees, and the legal corpus pages under `docs/graph/legal/corpus/` all
resolve to a seed source, so a replaced legal page is audited like any other
machinery file. A backup that resolves to nothing is reported unresolved and
fails, because unknown is not green.

### Phase 4: Refresh the plant's knowledge from the corpus (authoring-class authors)

For each withdrawable library/tool page from Phase 2, **seed the refresh from
the corpus as the orientation layer**, exactly as `ingest-library` and
`toolcraft` do for a new plant, then re-pin the plant's version-specific facts
fresh against the plant's real lockfile. The plant keeps every pinned fact it
discovered; it gains the enriched, version-durable surface the corpus now
holds. Where the plant has no page yet for a library it uses that the corpus
covers, propose growing one from the corpus orientation plus a fresh pinned
delta.

A withdrawable **legal** page refreshes the same way with one added step:
re-confirm each entry's `verified` date and `legal_status` against the
publisher before the plant relies on it, because the corpus carries the
citation and not its currency. The plant authors its own application of the
rule; the corpus holds no determination to copy (`harvest.corpus-contracts`). A
corpus entry whose currency cannot be re-confirmed is refreshed as orientation
only, and said to be such.

**Merge into the plant's existing page: one home per dependency.** When the
plant already has a page for the dependency, the refresh folds the corpus
orientation into that page: it adds whatever generic orientation the page lacks
and keeps every pin and sharp edge it already carries. The corpus's
sub-namespace (for example `library-corpus/container/docker.md`) is seed-side
organization: its content lands in the plant's flat `libraries/docker.md`, and
the corpus page's *location* stays in the corpus. A second page beside the
plant's is two homes for one dependency, a one-home-per-fact violation
`graft.gate.minimum-sufficient` blocks. This is the fruit reaching the plant:
harvest lifted the surface up into the seed, and graft lets this plant withdraw
it.

A corpus **tool** is adopted as-is only when the plant's stack matches;
otherwise treat the page as a blueprint and re-author against the plant's
stack, test-first. A tool page the plant carries for a tool it has not
built is marked as grow's withdraw step marks it, `blueprint only, not
built here`; one whose tool the plant has since built, still carrying the
corpus's `<…>` run and test slots, is re-pointed here to the real
implementation path and test command.

**Pages the installer placed: re-propose, re-apply, merge.** A plant grown or
grafted under 8.0.0 or later may carry corpus pages the installer placed on
the owner's list (`install.sh <host> --expertise <ids>`), recorded in the
stamp's `expertise` key with the hash of the bytes written. Those pages are
refreshed by the installer and merged here, in three steps, before the Phase 7
apply.

1. **Re-propose against the plant's current manifests.** The plant's
   dependencies have moved since the list was confirmed, and the seed's corpus
   has grown. Run, from the seed:

   ```sh
   <seed>/install.sh <host> --expertise propose --project-dir <plant>
   jq -r '.expertise[]? | "\(.id)  \(.path)"' <plant>/.cypress/seed.json
   ```

   The first writes nothing and prints one line per page the manifests match,
   with the manifest entry or the `stack:` match behind it (SPEC-0001 §6,
   "Selective placement", holds the matcher's rules). The second lists the
   record. Read the two against each other and against the plant's
   `docs/graph/libraries/`, `docs/graph/tools/` and `docs/graph/skills/`:

   - **proposed and recorded**: the installer re-applies it at Phase 7;
     nothing to decide.
   - **proposed, not recorded, destination absent**: a page the plant can
     withdraw. Filter it as grow's Phase 1 does (an upgrade page only while
     the declared line is older than its target), then put it to the steward
     as a numbered decision (`deliver.numbered-decisions`), each id with its
     evidence line. The confirmed ids go to the Phase 7 apply as
     `--expertise <id>,...`, which places and records them; an id the steward
     adds by hand is placed all the same.
   - **proposed, not recorded, destination present**: the plant's own page
     for that dependency, authored before the corpus had one or by hand.
     Listing the id would place nothing there (SPEC-0001
     PLANT_OWNED_PAGE_IS_NEVER_REPLACED); the merge below folds the corpus
     page into the plant's page instead, and the id stays unrecorded.
   - **recorded, no longer proposed**: the plant dropped the dependency, or
     a manifest the matcher read was renamed. The page stays and so does its
     entry, because no run removes either; name it to the steward, who decides
     whether the page goes and the entry with it.

2. **Read what the installer will do with each recorded page.**
   `<seed>/install.sh <host> --check --project-dir <plant>` writes nothing and
   names each recorded page that is missing, stale (untouched by the plant,
   and the running seed would place different bytes), edited by the plant, or
   withdrawn from the seed (SPEC-0001 EXPERTISE_CHECK_NAMES_MISSING_OR_STALE).
   Before the apply, a stale or missing line is expected: the Phase 7 install
   refreshes an untouched page to the new seed version with a backup, and
   places a deleted one again and names it in the log, because the record
   holds the owner's decision until the owner changes it. A page the plant
   deleted on purpose goes to the steward under `graft.gate.recreated-nodes`'
   rule: re-apply the deletion and remove the entry, or ratify the page. A
   **withdrawn** id (the seed renamed or dropped its page) is warned about and
   left, page and entry both; decide here whether the plant keeps the page as
   its own, and name the decision in the record.
   `tools/graft-audit.py` classifies the backup of a refreshed page
   `CORPUS-PLACED`, neither seed-owned nor plant-authored, so it never reads as
   a knowledge overwrite at `graft.gate.rootstock`.

3. **Merge each page the installer leaves and names.** A recorded page whose
   bytes differ from its recorded hash was edited by the plant: its pin, its
   project role, its sharp edges. The installer leaves it byte-identical, makes
   no backup, keeps its entry and hash, and prints one line naming its path and
   this phase (SPEC-0001 PLANT_EDITED_PAGE_IS_LEFT_AND_NAMED); a plant-owned
   page at the destination of a listed id gets the same line. Each such page is
   merged here by the rule above, one home per dependency: an author folds in
   whatever the corpus page at the new seed version holds that the plant's page
   lacks, keeps every pin and sharp edge the plant wrote, and re-pins nothing
   from the corpus, which carries no pin. A placed page keeps its provenance
   line as its first line, with the version updated to the seed whose layer was
   merged, so the line says which corpus layer the page carries. The page stays
   edited in the installer's eyes, so every later graft finds it here again,
   which is the point: from its first edit on, the page is the plant's,
   refreshed by merge and never replaced. The Phase 7 install log names the
   same pages; one it names that this step did not merge comes back here before
   the record is written.

Two ids the seed places at one destination (a `pypi` client and a `container`
image of one name) are refused before the install writes anything; the steward
keeps one, and the author folds what the other page knows into it by hand.

### Phase 5: Grow the new capabilities onto the living plant (authoring-class authors)

Fast-forwarding the machinery *carries* a capability to the plant; it does not
*grow* it there. A refreshed protocol, a new skill template, a new runbook
template, a corpus tool the plant's stack could use, each arrives as inert
machinery. **Grafted is not grown.** This phase closes that gap: for each new
or newly-enriched capability the graft delivered, grow it onto the plant
**where doing so is appropriate and necessary**, actualized into the plant's
living skills, tools, and knowledge, not left sitting as a template.

**Load `protocol.grow` here and run its loop.** Grow is a `peers:` edge of this
node, loaded only once this phase has a capability to actualize, so a graft
that finds nothing new to actualize never pays for it. Until then, cite what
this phase needs: `grow.completeness-contract` for what "grown" means,
`grow.stack-inventory` for how the plant's stack is read, `grow.legal-corpus`
for the whole-or-nothing corpus rule. Start by re-planning the coverage record
against the seed the plant now carries:

```sh
python3 <seed>/tools/growth-audit.py <plant> <seed> --plan
python3 <seed>/tools/growth-audit.py <plant> <seed>
```

`--plan` derives the required rows from the new seed, so every collection,
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

An expertise row is usually grown from facts the plant already holds. Where its
`stack.*` node already carries the routing prose (when this stack is in play,
what goes wrong without it, which sub-expertises apply under which
condition), the graft **moves** that prose into the expertise node and leaves a
`requires:` edge behind rather than copying it: the `stack.*` node keeps this
project's conventions, the expertise node owns applicability and composition,
and the routing fact has one home. Where a new row needs evidence the plant's
graph does not hold, the graft dispatches the same workers grow does: a
growth-scout at the boundary, and a `research-scout` for anything the plan
marks `grounding.required`, so a new `best-practices/` or `libraries/` page is
written from retrieved upstream documentation rather than model memory. The
loop is grow's: inventory, plan, author, lint, repeat while findings remain. A
row closes only by coverage or an honest record: `UNKNOWN` with its blocker, or
`ABSENT` with the reason and the paths searched, written where the audit reads
it. The collection's own `index.md` or `README.md` is the legitimate home of an
authored absence, and a reason that lives only in the graft's chat output fails
a row the procedure was otherwise followed for. It ships reported: named in the
Phase 8 entry, which is where `growth-audit.py` looks (`SILENT` otherwise), and
put to the steward as a numbered decision where the blocker is theirs to
resolve (`deliver.numbered-decisions`). A collection this seed added after the
plant's base, whose material the plant already authored under another home, is
Phase 6 drift (the "filled elsewhere" class), and it moves.

- **Grow what the plant evidently needs, grounded in its own facts.**
  Instantiate a suggested skill or expert the plant's real stack calls for (the
  `skill-corpus` / `agent-corpus` withdraw contract, into `docs/graph/skills/`
  / `docs/graph/agents/`, placed where the projection reads
  (`delegation.harness-registration`); the coverage gate reports a node one
  directory down as unspawnable), withdraw a corpus
  library/tool page the plant uses today, place the **whole** `legal-corpus`
  where the plant's stamp records `"legal_corpus": "yes"` and re-ask the owner
  where it records `undecided` (`grow.legal-corpus` owns the whole-or-nothing
  rule and its reason; a graft never decides it by inspection and never
  withdraws a subset), re-ask the national jurisdiction the same way and raise
  an ingest request where the corpus carries no national layer for it instead
  of reading across from a neighbouring country, or ground a runbook the plant
  can fill from its own deploy/release nodes. Every grown addition is anchored
  in evidence the plant's graph already holds: its references resolve inside
  the plant.
- **Grow only from evidence.** A capability whose content can only come from
  the plant's real, recurring use (a project skill for a procedure that has
  recurred here, an ADR for a decision this plant took, a runbook's real
  commands) waits for that use and sprouts through the close-out lifecycle
  (`canonize` → `docs-librarian`). The seed's anti-fabrication discipline (the
  `adr-writer` "don't invent a decision" and `grill-planner` "mark what you
  haven't verified" rules) applies to every surface: thin evidence is a reason
  to defer.
- **Surface what was grafted but not grown.** Report every capability now
  present as machinery yet still inert (no project skill sprouted, runbook
  templates still unfilled, a corpus page not yet withdrawn), so the steward
  sees the copy-but-not-actualized state plainly, and knows which items were
  grown now (grounded) versus deferred to real use (ungrounded). A silent inert
  capability reads as "delivered" when it is only "installed."
- **Own-kernel plants receive the substance as a weave.** A plant whose own
  instruction system is the rootstock (its machinery KEEP-PLANT, per the
  three-way reconciliation) also receives the upgrade: the seed's substantive
  delta since the plant's base is **re-woven** into the plant the same way the
  seed itself carries it. Map each seed surface the delta changed to the
  plant's equivalent surface (the seed's verify discipline → the plant's
  validation playbook; the reviewer's checks → the plant's change guide; the
  kernel posture → the plant's instruction file; a template rule → the plant's
  matching template or convention), and land each rule where it acts, in the
  plant's idiom, sized to its budget. One summary section in one file is a
  photocopy: the plant's operating surfaces would keep steering every session
  exactly as before. The weave lands as a ratifiable proposal like any other
  rootstock-adjacent change, and it exists, authored surface by surface, before
  the graft closes.

### Phase 6: Rebalance the plant toward pure graph (investigation-class audit, then authoring-class authors)

The reconstruction pass, and the one home of the mandate's procedure.

- **(1) Inventory the drift (investigation-class scouts, read-only → a
  rebalance ledger).** Audit the plant against the pure-graph spec and record
  each shortfall with its location, the invariant it breaks, its natural graph
  home, and confidence. Hunt the standing drift classes:
  - **machinery outside the graph**: any protocol/skill/agent/method content,
    or any always-loaded instruction the kernel need not carry, that lives
    somewhere other than a routable `docs/graph/` node;
  - **a fact with two homes**: the same rule, topology, or contract stated in
    two nodes, or in a node *and* a hand-maintained projection or summary;
  - **a hand-maintained projection**: a tool-dir command, prompt, or view that
    was hand-edited instead of generated from its node, and has drifted from
    it;
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
- **(2) Reconstruct in slices (authoring-class authors), bounded by the
  rootstock line.** Move each item to its natural node home as a holistic
  MERGE; collapse duplicate homes into one and trim restated facts to
  cross-references; regenerate a drifted projection from its node; and list
  obsolete residue for the steward's deletion (rootstock condition 2). Every
  relocation keeps its fact (the rootstock line), and each slice keeps the
  plant routable so the upgrade stays reversible.
- **(3) Leave the drift closed at its home.** Where the shortfall was a missing
  fitness function the seed now ships, install it; where it was a projection
  that drifted, the regeneration is the fix. Residue this pass could not close
  is surfaced with a remediation and a reason. The ledger closes when every row
  is fixed or carried with a reason, and closing it is what
  `graft.gate.pure-graph` asks the reviewer to assert.

Split across parallel authoring-class authors when the rebalance is large; that
parallelism is exactly what `graft.gate.cross-author` exists to reconcile.

### Phase 7: Apply, verify, and stamp (`graft.integrity-gates`; authoring-class authors, session gates)

Apply the ratified upgrade **additively**, to a clean tree or to one whose
dirty paths the steward has accepted (*Reversibility*, (d)).

`python3 <seed>/tools/graft-run.py <plant> <seed> --stage <dir>` rehearses the
mechanical half on a copy outside the plant: the ledger, the install with its
log, the engines, the audits and the lints. It prints this table's result
column, a judgment row as `not run` with its judge. It writes nothing in the
plant and ratifies nothing.

Then prove the plant is left more capable and no less itself. Every gate is one
row of the table below: that table is the single home for what a graft asserts,
and the record's integrity-gate block is its result column.

**Run them in this order, and name `--date` on every row that reads the `.bak`
set.** This is the one home of that caveat; the rows below pass `--date`
without re-explaining it. Left to itself the flag defaults to the newest `.bak`
stamp on disk, which is to say it follows whatever wrote last. The remedies
that re-run the installer write a fresh set of backups under a new date:
`graft.gate.projection-drift`'s regeneration, `graft.gate.kernel`'s kernel
fast-forward, and the fourth `STALE` condition under `graft.gate.coverage`,
whose remedy is an installer re-run for every adapter in the stamp's `tools`.
An audit taken after any of them, with the date left to default, audits the
remedy's own writes and prints `clean` over the graft it was supposed to
examine. So: audit first, remediate second, name the date every time, and after
any remediating re-run re-audit under **both** dates. A remedy's re-run also
overwrites the files Phase 3 merged or kept, with a backup and no question, and
the backup audit reads such a file as an ordinary version advance. The last row,
`graft.gate.kept-deltas`, therefore checks each of those files against the
record, after every remedy has run.

| Gate | Asserts | Command | On failure | Class |
|---|---|---|---|---|
| `graft.gate.backups` | every file `place_file` replaced is recoverable from a timestamped sibling. It does **not** assert that the backup set accounts for every byte the run destroyed: *The installer is the hand that applies it* names the writers that replace with no backup | `tools/graft-audit.py <plant> <seed> --date=<this run's stamp>` classifies every fresh `.bak` and refuses a vacuous audit (zero for the named date while others exist); the totality property (M7) is proven seed-side by `tests/test-install-placement.sh` over a *discovered* destination set, whose sole exception is `is_installer_state()` and whose scope is stated with it | BLOCK: ratify only an upgrade whose replaced files are all found; file a no-backup replacement by any writer outside those named there as an installer defect | soft |
| `graft.gate.rootstock` | the rootstock line held: every plant-authored fact survived, and each write into plant-authored material was value-preserving and ratified | the same audit's *knowledge overwrite* count over `docs/graph/`, plus `git -C <plant> status --porcelain` scoped to non-machinery paths (tracked files only, on purpose; stray files are what grow's `--ignored -uall` form finds), plus `git -C <plant> diff docs/graph/index.md` by name, for the reason *The installer is the hand that applies it* gives. New blank forms under `plans/` are expected and are no breach: `docs/graph/plans/sessions/_session-record.template.md` (the memory migration) and `docs/graph/plans/_harvest-candidates.template.md`, each placed by the scaffold walk | BLOCK: restore from the backup and re-reconcile | soft |
| `graft.gate.customization` | no plant divergence was buried by a blind fast-forward | `tools/graft-audit.py <plant> <seed> --date=<this run's stamp> --base=<the base Phase 1 printed, tagged or inferred> --tokens=<plant tokens> --engine=<plant>/docs/graph/graph-lint.py:<seed>/templates/knowledge-graph/graph-lint.py --engine=<plant>/docs/graph/spec-lint.py:<seed>/templates/knowledge-graph/spec-lint.py --engine=<plant>/docs/graph/grill-lint.py:<seed>/templates/knowledge-graph/grill-lint.py`, one pair per engine | BLOCK: re-integrate each hit into the FF'd file as a holistic MERGE, or ratify it explicitly | soft |
| `graft.gate.kernel` | every kernel destination this plant carries holds the seed's `core/AGENTS.md` body | the same audit's kernel-currency check gates the exit code, but it reads exactly two files, `<plant>/AGENTS.md` and `<plant>/CLAUDE.md`. A plant whose stamp lists `github-copilot` has a third, and the audit is silent on it: add `cmp <plant>/.github/copilot-instructions.md <seed>/core/AGENTS.md` | BLOCK: see *When a gate blocks* | soft |
| `graft.gate.schema` | the plant's `_schema.md` still describes the machinery this graft installed | the same audit's node-schema line | report: it does **not** gate the exit code, so read the line; the remedy is a ratified MERGE (Phase 3) | detective |
| `graft.gate.engine` | the plant runs the seed's current graph engines, each with its own config preserved | the same audit's engine-currency check, via the three `--engine=<plant>:<seed>` pairs `graft.gate.customization` passes, each reported on its own line naming its plant file. Each value is a **pair**; a single path is malformed and the audit refuses it rather than skipping the check | report: the audit prints `graph engine STALE` without gating the exit code, as `graft.gate.schema` does, so read the line: ratify only when every engine is current, or is a superset recorded as KEEP-PLANT. Reconcile a stale engine with `tools/graft-graph-engine.py`. The one thing here that gates is a malformed or unreadable `--engine` pair, and it gates because the check did not run | detective |
| `graft.gate.scaffolds` | no `docs/graph/` leaf is still byte-identical to its `templates/docs/**` template; an unfilled model map, `docs/graph/models.md`, is a `DISCLOSED` line and passes (every agent inherits its caller's model) | `tools/graft-audit.py <plant> <seed> --unfilled` | BLOCK: see *When a gate blocks* | soft |
| `graft.gate.coverage` | every capability this graft carried was grown, or is answered | `python3 <seed>/tools/growth-audit.py <plant> <seed>`; non-zero blocks | BLOCK: see *When a gate blocks* | soft |
| `graft.gate.routes` | the upgraded graph routes, the agent router is clean, and every context hook the plant wires runs and prints its context | `python3 docs/graph/graph-lint.py`, a representative `--plan`, `python3 docs/graph/agent-lint.py --lint` and `--eval` where installed; then `install.sh <host> --check --project-dir <plant>` once for each host in the stamp's `tools`. That check runs each wired `UserPromptSubmit` and `SessionStart` hook once, on an envelope with no session id, writes nothing in the plant, and fails naming any hook whose script is missing, exits non-zero or prints nothing (SPEC-0001 CHECK_EXECUTES_EACH_WIRED_HOOK). The hooks are fail-open in a session, so this is the step that finds a dead one before a session runs without its route. The same check names each agent or skill in a harness directory with no graph home: `RETIRED` for an `origin: seed` one the running seed does not ship, `ORPHAN` for one the plant authored there (SPEC-0001 CHECK_FLAGS_RETIRED_HARNESS_ENTRY, CHECK_FLAGS_ORPHAN_HARNESS_ENTRY). Those lines do not gate this row; they feed migration steps (c) and (d). `tools/graft-run.py`'s rehearsal runs this second half once per host on the stage copy and reports, in this row, the hooks that ran, the hooks that failed and the flagged entries | BLOCK: fix the node, not the linter. A failed hook is restored by re-running the installer for its host, which is an apply with its own backup date, as under `graft.gate.projection-drift` | soft |
| `graft.gate.status-register` | a migrated plant's lifecycle status is queryable and agrees with its index rows | `python3 docs/graph/status-register.py --root docs/graph` | BLOCK, or N-A where no status migration was ratified | soft |
| `graft.gate.prose` | the prose this graft authored into the plant meets the plant's own prose floor | `python3 docs/graph/prose-lint.py --file <node>` for each node Phases 4–6 wrote or re-wove (`--against <rev>` where the plant's Git state names one) | BLOCK the item: re-author; never lower the linter | soft |
| `graft.gate.adopted-instructions` | every instruction file the kernel replaced has a ledger row, and every ledger row has an owner | list this graft's kernel backups (`ls <plant>/CLAUDE.md.bak-<date>-* <plant>/AGENTS.md.bak-<date>-* <plant>/.github/copilot-instructions.md.bak-<date>-*`) and match each against `docs/graph/plans/adopted-instructions.md`. Three outcomes, and the command separates them: no backups and no ledger file is **nothing to report**; backups all matched by rows is the healthy replacement; a backup with no row is *Reversibility* (b) 3, the case that is permanent | report every unstruck row and hand it to `docs-librarian`: open librarian work, not a defect of this graft. BLOCK on an unmatched backup and file it by hand | detective |
| `graft.gate.recreated-nodes` | a node the installer re-created is re-applied or ratified, so no deliberate deletion is silently reverted | `.cypress/recreated-nodes.txt`, this run's whole list (the next run rewrites it, so read it before any remedy re-runs the installer) | report each path; a deliberate deletion the steward confirms is re-applied, else ratified in the plant's record | detective |
| `graft.gate.roster-delta` | the specialists this graft added or renamed are handed to the plant's next session | diff the plant's `docs/graph/agents/` against the base seed's roster; cite `delegation.harness-registration` | report: this session cannot verify them spawnable, and saying it did would be the claim the fact exists to prevent | detective |
| `graft.gate.stamp` | the plant records the seed it now carries, with dated provenance | read `version` from `<plant>/.cypress/seed.json` and compare with the seed's `manifest.json`; `growth-audit.py` reports `STALE` when stamp and coverage record disagree | BLOCK: a stamp that disagrees with the coverage record means the upgrade was audited against a seed the plant does not carry | soft |
| `graft.gate.minimum-sufficient` | everything this graft added beyond the machinery contract earns its place | none: the graft reviewer (authoring class) audits the additions against `docs/graph/method/minimum-sufficient-work.md`. Judge: the graft reviewer (authoring class) | BLOCK that item; the rest of the graft may proceed | judgment |
| `graft.gate.projection-drift` | every tool-dir projection still matches the node it is a projection of | read-only, and in two halves, because the projections are of two kinds. Where the stamp's `agent_projections` entry says `"verbatim": true`, the projection is a placed copy, so `diff <plant>/docs/graph/agents/<n>.md <plant>/<adapter path>` is the whole check. Where it says `false` (`github-copilot`, whose views are transformed), `install.sh github-copilot --check` regenerates to a temp dir and diffs, writing nothing to the plant | BLOCK: regenerate by re-running the installer for the affected adapter, never hand-patch the copy. That re-run is an apply: it writes, it creates a new backup date, and a tree regenerated that way matches by construction, so it is a remedy and never the detector | soft |
| `graft.gate.pure-graph` | the Phase 6 rebalance ledger closed | none: **the graft reviewer (authoring class), the same judge as `graft.gate.minimum-sufficient`**, reads the ledger row by row against the pure-graph spec: no seed-class machinery or superfluous always-loaded instruction outside a node, no fact with two homes, no unlisted obsolete residue. Judge: the graft reviewer (authoring class) | BLOCK: or surface the residual drift with a remediation and a reason | judgment |
| `graft.gate.cross-author` | a parallel absorption reconciled across author boundaries | none: **`docs-librarian` judges**, in one final spawn seeing the whole graph at once, followed by a structural audit, pass/fail per node. Judge: `docs-librarian`, in one final whole-graph spawn | BLOCK: see *When a gate blocks*; N-A where no phase used parallel authors | judgment |
| `graft.gate.kept-deltas` | every file the graft record lists as merged or kept still carries its plant delta at the end of the graft, after every remedy that re-ran the installer | `tools/graft-audit.py <plant> <seed> --record <plant>/docs/graph/changelog.md`, run last, once the record's entry is written: it reads the newest graft entry's `Merged` and `Kept as the plant's` bullets and prints `LOST` for a file byte-equal to its seed source and `MISSING` for one the plant no longer carries | BLOCK: re-apply the delta from the newest backup that holds it, then re-run the row; never edit the record to match the loss | soft |

Every row names its command, or the judgment and who owns it (`rule.verify`): a
row whose Command cell reads `none` names its judge.

The Class column uses `verify.gate-classes`. Nothing here is `hard`: no
harness prevents a steward applying an upgrade, and saying so is the point of
the column.

**What `--tokens` is, and what a clean result is worth.** The customization
audit's whole verdict is bounded by the vocabulary it is given. Explicit tokens
are the plant's own name and paths, and they are always signal; the generic
self-reference list ("this project's", "our stack") counts only where the seed
source does not also carry the phrase, so a charter the seed reworded is not
reported as a customization, and a steward is not taught to ratify without
looking. Derive the token list from the plant: its repository and product
names, the names in `.cypress/seed.json`, its top-level module and package
names, its domains, its service and environment names, and the identifiers its
`product/` and `nodes/` collections use for itself. Then say plainly in the
record which tokens were supplied: **a `clean` verdict is clean *for those
tokens*,** and an under-supplied list produces a reassuring pass over a real
divergence.

**When a gate blocks.** These remedies do not fit a table cell:

- `graft.gate.kernel` has three verdicts. **Current** (byte-equal) passes.
  **Stale**, a seed line missing (so an old or hand-edited body), blocks:
  fast-forward the kernel body by re-running the installer for every adapter
  the stamp's `tools` names (*Provenance & the seed stamp*). Then re-project
  the plant's own agents and skills into any adapter that lacks them, and
  re-audit under the new backup date as well as the graft's. **Extended**, the
  seed body plus plant-authored lines, blocks unless a standing `deviation.*`
  node with `departs_from: kernel.body` records the boundary, in which case the
  audit reports the deviation and its `ends_when` and passes. A kernel line the
  plant added is a departure from the pure-graph mandate: move it into a graph
  node the kernel routes to, or record that deviation. The installer's kernel
  pass rewrites the body, so re-apply the recorded lines after every graft and
  re-run the audit. The kernel loads on every session of every adapter, which
  is why this gate always runs.
- `graft.gate.scaffolds` blocks on a leaf that is a scaffold posing as
  knowledge, shadowing the authored leaf a cold agent needed
  (`grow.completeness-contract` owns the rule; `runbooks/verification.md` is
  exempt only while it carries an `executed` gate). List each one in the
  record. `--rename` is the default remedy: `<name>.unfilled.md`, a marker the
  installer honours so the blank is never re-created. `--prune` is a deletion
  (rootstock condition 2), so it runs only on the steward's own naming of the
  files. Prefer the rename regardless: a pruned leaf reappears at the next
  install or graft. The model map is the one template-identical leaf that
  passes: its unfilled rows mean "inherit the caller's model", so the audit
  names it on a `DISCLOSED` line, and the record lists it for the owner to fill.
- `graft.gate.coverage` speaks in `growth-audit.py`'s verdicts, quoted once in
  `protocol.grow` (*What the coverage gate reports*). Read `MISSING` or `BLANK`
  as a capability this graft carried and never grew, and `UNGROWN` / `HOLLOW` /
  `UNGROUNDED` as one grown without the material; substance, not path, is the
  test, so a leaf edited just enough to stop being byte-identical still fails.
  `CONTRADICTED` arrives in two shapes a graft meets often: a row claimed
  `COVERED` whose own paths hold only scaffolds, `.unfilled.md` markers, or no
  leaf that states a fact (the shape a `plant_knowledge:` directory takes when
  a migration moved its material and the record was not re-planned); and a row
  claimed `ABSENT` whose searched paths include a filled leaf, or which names
  an expert that is on disk. In both, the record is the half that is wrong.
  `SILENT` means a row this graft closed `UNKNOWN` (the owner's decision, by
  the record's own words) was never named in the Phase 8 entry: filed, not
  asked. **`STALE` is four findings under one word, and three of them share a
  remedy the fourth does not**; read which one the line says. A record naming
  no `seed_version`, a record planned against a different seed than the audit
  ran with, and a record whose `seed_version` disagrees with the plant's stamp
  are all fixed by re-running `--plan`, because auditing a stale record is how
  a graft reports coverage it never checked. The fourth is not about the record
  at all: a **stamp with no `agent_projections`** means nothing says where this
  plant's roster has to be spawnable from, so every expert passes the
  registration check by default. `--plan` does nothing for it. Re-run the
  installer for each adapter in the stamp's `tools`, then re-audit. Genuine
  absences pass as `ABSENT` with a reason and the paths searched, and named
  `UNKNOWN` blockers pass reported. A 5.x plant meets this gate differently:
  its own experts live in the harness directories with no graph home, so they
  are invisible until migration step (c) relocates them, and then they surface
  as `MISSING` rows the record does not yet answer, the same gap in a shape
  this phase can act on.
- `graft.gate.cross-author` exists because a large migration, rebalance, or
  fact-sweep is real parallel work: Phases 3, 4, 5, 6 and step (f) each split
  across multiple authoring-class authors with disjoint file ownership, because
  that is what makes the absorption tractable. Disjoint ownership means nobody
  owned cross-file consistency, and two failure modes follow that no linter
  reports: a shared summary file (an `index.md` node table, a `root.md`
  topology map) that no single author's file list covered goes stale the moment
  any author changes something it depended on, and the same fact ends up
  restated in two files each author touched independently. One final
  `docs-librarian` spawn, seeing the whole graph at once the way disjoint
  authors structurally cannot, catches both, plus register drift (a passage
  that reads as bolted-on rather than woven). Follow it with a structural
  audit, pass/fail per node, for what `graph-lint.py` cannot see: it validates
  that edges *resolve*, not that they make *sense*. Is every node's `kind` the
  right one, does the plant's topology map list every node the migration or
  sweep added, and does every `requires:`/`peers:` edge reflect what the node's
  body actually depends on. A green `graph-lint` proves the graph is
  well-formed; run the structural audit even when it is green.

### Phase 8: Deliver (propose, then ratify)

Graft **proposes**; the plant's steward **ratifies**. Emit the reconciled
upgrade as a reviewable patch/proposal with the graft summary below, and add a
provenance entry to the plant's own `docs/graph/changelog.md` naming the graft.
Hand the KEEP-PLANT divergences back as harvest candidates, closing the loop
the other way: each one that passes the admission test gets a row in the
plant's harvest-candidate record (`canonize.harvest-candidates`), so the
hand-back outlives this entry. End with the single highest-leverage next step.

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
trees, then the kernel **last**, and restore **both** kernel backups, the real
file and the sibling. `place_kernel` `rm -f`s the sibling and replaces it with
a project-local symlink, so a plant that carried two independent kernel files
now carries a symlink pair, and restoring only the real file leaves it paired
for ever. Confirm afterwards that each is the kind of object it was
(`ls -l <plant>/CLAUDE.md <plant>/AGENTS.md`).

Files placed by `place_if_missing` left no backup because they only ever added.
Removing them is a **deletion** (rootstock condition 2): the steward names the
files, explicitly.

**(b) What an unwind cannot reach.** A steward calibrating risk needs every one
of these. The list is complete for the installer's writers as they stand, and a
writer added later can extend it. It lists what an unwind cannot reach, which
is wider than what has no backup: items 2 and 3 have a `.bak` and are still out
of reach, and item 5 has none. Read the two questions separately, because the
backup scan answers only one of them:

1. **`.cypress/seed.json` and `.cypress/recreated-nodes.txt`.** Written by
   `place_state` with no backup, on purpose: each carries a fresh timestamp
   every run, so it is never byte-identical and a backup policy would leave one
   sibling per install for ever; and each is *derived* (the stamp from the last
   one plus the run's flags, the list from the run) rather than authored, so a
   backup would carry no recovery value anyway. Recover the stamp by
   re-deriving: re-run the base installer with the plant's recorded flags, or
   hand-write it from `installed_from` and the adapter list. An earlier run's
   list is not recoverable, which is why the gate reads it first.
2. **A project's own root instruction file.** The `.bak` exists, but a backup
   is recovery evidence, not operational preservation: the content is out of
   force the moment the kernel lands. Its restoration is a *migration*, tracked
   in `docs/graph/plans/adopted-instructions.md` and owned by `docs-librarian`,
   not a `mv`.
3. **An instruction file replaced where the ledger row was never written.** The
   next run sees a kernel matching the seed, therefore no deviation, and files
   nothing; the original body sits in a backup nobody is told about. Three
   guards cover the known paths to it (the preflight, the orphaned-backup
   sweep, and the symlink handling of the note write; *The installer is the
   hand that applies it*). It stays on this list because the cost of missing it
   is permanent.
4. **A sibling kernel file that happened to match the seed.** `place_kernel`
   takes the sibling's backup only `if ! cmp -s "$seed_kernel" "$other"`, then
   `rm -f`s it unconditionally. No plant *content* is lost when the two
   matched. What is lost has no backup and no record: that the plant carried
   two independent files rather than a symlink pair, and, where `other` was a
   symlink pointing outside the target that merely resolved to matching bytes,
   the link itself, its target unrecorded.
5. **The `plant:` block of `docs/graph/index.md` as it stood before the run.**
   `fill_plant_facts` rewrites that frontmatter in place and takes no backup,
   so there is no sibling for step (a) to `mv` back and nothing for the backup
   scan in (c) to report. On a plant whose `index.md` is committed and clean
   the loss is nominal, because `git diff` shows the change and `git checkout`
   would undo it. On a plant where `index.md` is uncommitted or already dirty
   there is no committed version to diff against, and by (d) the graft has not
   put one there: it records Git state and leaves it as it is. The pre-run
   block is then both **unrecoverable and invisible**, which is the worse half.
   The defence is procedural and belongs before the run: capture
   `git -C <plant> show HEAD:docs/graph/index.md` alongside the install log, or
   commit the file first.

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
    --engine=<plant>/docs/graph/graph-lint.py:<seed-at-base>/templates/knowledge-graph/graph-lint.py \
    --engine=<plant>/docs/graph/spec-lint.py:<seed-at-base>/templates/knowledge-graph/spec-lint.py \
    --engine=<plant>/docs/graph/grill-lint.py:<seed-at-base>/templates/knowledge-graph/grill-lint.py
```

`<seed-at-base>` is a checkout of the seed at the version in the *restored*
stamp (`git -C <seed> worktree add <dir> v<base>`). Read step 3's verdict for
what it is. The graft's backups are gone, consumed by the `mv`, so the backup
scan can only report `zero backup files — nothing was overwritten` (or refuse
as vacuous, if backups from another date remain, which is itself a finding: a
restore left one graft's writes in place). That line proves nothing about the
restore. What proves it is the rest of the same run, and the two halves of it
are not worth the same. **Kernel-currency gates the exit code**, and it now has
to read the *base* seed as current, so a non-zero exit here is a real finding
about the restore. **Engine-currency does not gate** (`graft.gate.engine`): it
prints a line per engine and returns success whatever it finds, so a green exit
code is not evidence the engines came back. Read each line with your own eyes,
and drop the pair for an engine the base seed did not ship. Then confirm the
stamp reads the base version, and record the unwind in the plant's
`docs/graph/changelog.md` the way the graft itself was recorded.

**(d) Git is provenance here, not a mechanism.** Graft records the plant's Git
state and leaves it as it is: it runs no fetch, switch, commit or push. An
unwind therefore has no `git checkout` to fall back on, only the backups, and
on a dirty tree the backups cannot tell the graft's writes from the steward's
own uncommitted work. So the rule the apply step obeys is: **a dirty tree is
applied to only when the steward has named the dirty paths and accepted that
the unwind will be file-by-file from backups.** The one moment that distinction
is needed is the moment it would be gone.

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
- <placed page> (<corpus id>) — refreshed by the installer | merged by hand (plant-edited or plant-owned) | newly placed on the steward's list | withdrawn from the seed, kept or removed by the steward's decision

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
- Re-created nodes: <path> — deliberate deletion re-applied / ratified (N-A where the installer did not treat the target as a prior install: it prints no notice)
- Roster delta (not assumed spawnable until the preflight confirms it): <specialists added or renamed>
- Flags used: <--force / --symlink / --copy / none>, and what that means for this record

## Shape migrations proposed (plant-authored artifacts in a superseded form; N/A if none)
- <artifact — form it carries → form the seed now defines, the version that changed it, what that buys, and the conversion; PROPOSED / RATIFIED / DECLINED; applied only once RATIFIED.>

## Status migrated (pre-7.0.0 plant; N/A otherwise)
- <status-migrate.py table: path — old value → `status` + companions; items reported-not-migrated, with the steward's `--map` decision>

## Harness memories moved to a session record (N/A if none)
- <the session record's path; each harness entry → the home canonize gave it, or why not; the entries put to the steward for retirement, by name>

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

- Reconciles every artifact three-way: fast-forwarding cleanly, preserving
  every plant divergence and flagging it upstream as a harvest candidate, and
  re-integrating true conflicts holistically into one coherent file for the
  steward, including a relocated plant expert/skill trimmed to genuine
  cross-references.
- Withdraws the corpus fruit the plant is due, re-pinning the plant's own
  version-specific facts fresh so nothing pinned is lost, and sweeps a
  pre-graph plant's own knowledge into the graph as part of the same migration.
- **Grows** the newly-delivered capabilities onto the plant where evidenced and
  necessary, and surfaces every capability it left inert.
- Delivers what is due and no more: it adds no artifact the plant will not
  consume, and re-integrates a conflict with the rewrite the conflict requires.
- Rebalances toward pure graph on every graft, not only a legacy migration, and
  surfaces the residual drift it could not close with a remediation and a
  reason.
- Delivers the seed's substantive delta even to a plant that carries no seed
  machinery, re-authored into the plant's own surfaces as a complete,
  ratifiable proposal.
- Says what its own verdicts are worth: which tokens the audit was given, which
  `--date` each audit read (the graft's, not a remedy's), which gates are
  judgment, and what the unwind cannot reach.
- Proposes for ratification; the steward decides before it lands.

## Reach

- Graft reads the seed and writes the plant; a divergence worth flowing back
  goes to `harvest`.
- Graft runs knowledge-and-machinery checks only: the plant's application
  source stays untouched, and its application builds and test suites stay the
  plant's to run. Its Git state is read-only provenance (*Reversibility*, (d)),
  which is why the unwind is by backup file.
- Conflicts, reconciliations, and every write into plant-authored material go
  to the steward for ratification (the three-way reconciliation, the rootstock
  line, Phase 8).
