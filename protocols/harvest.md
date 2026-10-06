---
name: harvest
description: The inverse of grow — fold a mature plant's generalizable lessons back into the seed (tooling fixes, skill and protocol gaps, agent and template improvements, and the five corpus contracts) so the next plant starts ahead of where this one did. Manual trigger only, never automatic; harvest proposes and the steward ratifies. Holds the three admission gates — agnosticism, durability, non-redundancy — and the seed integrity gate table every fold-back clears before it may land.
id: protocol.harvest
tier: 2
kind: protocol
origin: seed
title: harvest — folding a mature plant's project-agnostic lessons back into the seed, user-triggered only
owns:
  - harvest.fold-back-flow
  - harvest.agnosticism-gate
  - harvest.availability-gate
  - harvest.corpus-contracts
requires:
  - method.delegation
peers:
  - method.minimum-sufficient-work
  - skill.humanizer
  - protocol.canonize
  - protocol.graft
  - protocol.grow
  - protocol.ingest-library
  - skill.toolcraft
load_when:
  - "harvest lessons back into the seed"
  - "fold generalizable improvements upstream"
  - "the plant is mature, propose a harvest"
  - "seed improvement from project experience"
  - "should this library, tool, skill, or expert page go into the seed's corpus"
  - "is this lesson project-agnostic enough to land in the seed"
  - "wire a harvested artifact so install, grow, or graft actually delivers it"
  - "propose promoting a plant-commissioned expert into the base roster"
  - "a harvested page is in the seed but no plant can reach it"
prevents: A lesson learned in one plant and re-learned in every other, because fixes stay project-local and the next plant starts exactly where the last one did.
est_tokens: 15890
---

# Protocol: harvest

`grow` runs the seed into a project and grows it. `harvest` runs the other
direction: a mature project back into the seed, so the next project starts
ahead of where this one did. A seed that only ever seeds, and never harvests,
cannot improve; a seed that harvests carelessly rots into a pile of one
project's specifics. This protocol is the disciplined gate that lets the seed
compound **without** losing its agnosticism.

The metaphor is load-bearing. The seed grows a plant; the plant lives its own
life and learns things; harvest takes only the seed-worthy essence of what it
learned, never the plant's flesh, and folds it back so the next seed is richer.
What goes back in must be true for *any* future plant, not this one.

## Trigger: user-started; the system proposes, the steward starts

Harvest is **user-sovereign**. Unlike `canonize`, which runs at the end of
every task, harvest starts only when the user starts it: never automatically,
on a schedule, by a hook, or as a "while I'm here" step at the end of another
protocol. The seed is the inheritance of every future plant; changing it is the
user's call, not the system's.

- **The user starts it**, by invoking this protocol or pasting
  `HARVEST_PROMPT.md`.
- **The system may, at most, propose it.** When a mature plant clearly holds
  generalizable lessons, an agent may *suggest* "this looks worth harvesting
  into the seed" and stop. The suggestion is a doorbell, not an entry.
- **A fold-back reaches the seed only once the user is satisfied with the
  growth.** Every fold-back is a proposal the user ratifies, and an unratified
  harvest is a draft rather than a change. If the user is not satisfied, the
  proposal is revised or dropped and the seed stays as it was.

## When to invoke

- The **user** has asked to harvest, or ratified a proposal to. Maturity below
  is a precondition for *proposing*.
- A plant is **fully grown**: delivered, its verification gates green, its
  plan-of-record closed or steady. Harvest once the plant is steady, because a
  still-churning project yields half-baked lessons.
- The plant's life produced **generalizable** artifacts worth compounding: a
  shared-tooling bug fixed, a new hard rule a skill should have carried, a
  protocol gap discovered, a new reusable expert authored, a template that grew
  a better section, a class of failure whose *prevention* is universal.
- You are the seed's **steward** (the user acting as the seed's owner; the two
  words name the same person), working with the seed as the target scope. The
  plant is a read-only donor, and the seed is the only thing this protocol
  writes.
- **One plant or several.** A harvest may take every plant on a host at once.
  Each plant is then surveyed on its own, and the ledgers are consolidated
  before triage (§Phase 1, "Several plants"). The round's working records
  (ledgers, baselines, drafts, the friction log) name plants, so they live in
  the seed's gitignored `.cypress/harvest/<date>-<scope>/` and are never
  committed or quoted into seed text.

## The agnosticism gate (`harvest.agnosticism-gate`): the heart of this protocol

Every candidate improvement passes one hard test before it may touch the seed:

> **Would this help an arbitrary next project, in a different language,
> framework, and domain, that has never heard of this plant?**

- **YES, verbatim.** Harvest as-is (rare; usually only tool-neutral rules).
- **YES, once generalized.** Rewrite it stripping every plant-specific name,
  domain term, the plant's own pin (the version it runs), path, and example,
  until only the universal kernel remains, *then* harvest the generalized form.
  A version fact about the library itself stays (§the second gate). State the
  before→after generalization explicitly.
- **NO.** Reject it. It is the plant's life, not the seed's. Record why, leave
  it in the plant.

Fail-closed corollary: **a lesson is ready to harvest only when you can state it
without naming the plant.** Generalize it or drop it. A single leaked project
name, domain noun, credential, dataset shape, or the version one plant runs,
stated or cited as evidence, in the seed is a failed harvest, and it is worse
than a missed lesson, because it silently narrows the seed for everyone
downstream.

### What counts as a project reference

"Project-agnostic" is stricter than "unnamed": a reference need not name the
plant to identify it. **Each of these six classes is a project reference. Strip
every one from everything the seed commits, including the CHANGELOG entry, the
harvest-log row, provenance notes, and any illustrative example:**

1. a **name**: the plant, its product, company, service, or an internal tool or
   library of its own;
2. a **stack fingerprint**, the specific language/framework/datastore
   combination that identifies the plant (e.g. "a `<language>/<framework>`
   microservices plant"). Name a library only where the seed genuinely
   documents that library for *any* project (the library corpus), never as "the
   stack this plant ran". Versions can complete a fingerprint: a framework line
   on a runtime line with a given datastore identifies a plant as surely as a
   name does;
3. an **identifying count or metric**: "authored N library pages", "an
   N-observer registry", a figure that describes this plant's scale rather than
   a universal rule;
4. a **description of the plant's internals**: its file names, config keys,
   plugin names, module wiring, the exact versions its lockfile resolves, or a
   security finding on its own code;
5. a **path, host, port, credential, or absolute install location**
   (`/root/…`);
6. an **illustrative example framed as the plant's own**, such as "this
   project's fleet does X". Recast every example in the generic ("a fleet may
   do X"); an example is admissible only once it no longer belongs to any
   specific project.

**A plant's version is a project reference wherever it appears**, stated as a
fact or cited as evidence ("seen on N"): the version this plant runs or
resolved (class 4), or a set of versions that identifies its stack (class 2).
A plant-observed fact enters the seed with no version of the plant attached.
The versions a seed page may name are those the library's own release notes
or documentation state, said about the library ("the setting exists from N",
"the default changed in N"): those are version facts, and the second gate
admits them. Security facts and calendar dates are kept out by that gate, not
by this list.

Plant-identifying provenance (which plant it was, its stack, the exact
before-text that was stripped) belongs in the **ratification proposal you show
the steward**, never in the seed's committed files. The seed records *that* a
harvest happened and *what* generalized lesson landed; it never records *whose*
plant it came from.

This list is the one home of the rule. Phase 2 applies it, **G1** and **G2**
enforce it, and both point here by number rather than re-listing the classes.

### The second gate: durability (surface, not pin)

Agnosticism asks *"true for another project?"* Durability asks a second,
independent question of every fact:

> **Will this still be true, as stated, a version from now?**

A fact passes when it names the scope it holds for. "From version N the
default is X", "removed in N", "a pitfall of the N line only" stay true when
the next release ships, because each states the version it is bound to. A fact
that silently assumes one release ("the default is X", written against one
pin) rots the moment the pin moves. So the seed's inheritance is durable
knowledge with its version facts stated: what a library is for, its stable API
shape, its enduring idioms and conceptual pitfalls, and the versions at which
any of that changes. That is what compounds. The version one plant runs is the
*plant's* concern, discovered fresh by `ingest-library` against the plant's
own lockfile.

- **KEEP (durable, versions stated):** the capability the library provides;
  its core API shape and canonical usage; idioms and best practices; conceptual
  gotchas inherent to the tool; the upstream doc/repo home; and every **version
  fact the library's own release notes or documentation state**, written with
  the subject it qualifies: a minimum version, the version where a behaviour, a
  default or a coordinate changed, a deprecation or removal version, a
  version-specific pitfall, a major-line boundary of the page's own subject and
  the upgrade or migration diff across it. A major line stays the unit that
  earns a section of its own (`library-corpus/README.md`, "A major line is not a
  pin"); a finer version fact sits in the section it qualifies.
- **REJECT:**
  - a **security fact**: a CVE or advisory identifier, and any fact whose
    purpose is to warn about an exposure ("releases before N let an attacker
    do Y"). Vulnerability scanners and advisory feeds own these, and the plant
    reads them against its own lockfile. A page still states a library's
    secure defaults and what a careless setting opens (the withdraw-ready bar);
    that is configuration, not an advisory;
  - a **calendar date**, with two standing exceptions: the retrieval date of a
    `platform` page that has no version of its own (`library-corpus/README.md`,
    the last rule) and the dates `legal-corpus/_schema.md` requires
    (verification, edition and consolidation dates);
  - a **plant's own version**: the version one project runs or resolved. It
    is never stated in the seed and never cited as evidence for a fact there;
    it belongs in the plant's `docs/graph/libraries/<name>.md` §0;
  - a **bare version number** with no subject or behaviour attached;
  - a page that reads like one release's security bulletin.

When in doubt about a version fact, cite the release note or documentation page
that states it, or drop the version. A plant-observed fact keeps its provenance
class (§Phase 1, "A plant fact may be wrong") and carries no version. A
version-bound fact never passes as unbounded. A corpus page that reads like a
security bulletin for one release has failed this gate; one that reads like the
opening of the library's own docs, "changed in" notes included, has passed.

Of the classes above, only the CVE identifier has a detector
(`tools/agnosticism-lint.py`'s `CVE_RE`). An advisory-shaped fact, a calendar
date, a plant's version and a version fact missing its subject or its source
have none, so durability is read by a person (G2).

### The third gate: non-redundancy (does the seed already own this?)

Agnosticism asks *"true for another project?"*; durability asks *"true a
version from now?"*. The third gate asks:

> **Does the seed already say this, in a kernel rule, an agent, a skill, a
> protocol, or a template?**

A plant grew *from* the seed, so its ADRs, plan-of-record, best-practices, and
runbooks are saturated with the seed's own doctrine filled in with local facts.
A survey that reads only the plant will keep "discovering" rules the seed
already ships (reversibility-with-trigger, a risk paired with its verifying
check, fail-closed defaults, released-bits-are-tested-bits, resolve-in-place,
two-axis severity) and proposing them back is not a harvest, it is an echo.
Before any candidate is proposed, **open its would-be seed home and read it**:
if the rule already lives there, the candidate is **rejected as redundant**, and
only the genuinely net-new residue survives. Corroboration across several plants
raises confidence that a *net-new* rule is universal; it never converts a seed
duplicate into a fold-back. Corroboration counts **lineages, not plants**:
plants that share a lineage (one grown from another's tree, one product family,
one shared copy of a page) are one witness, however many directories they fill.
A survey's "already covered" call is a claim like any other: it names the seed
home and the line that covers the candidate, and the triage author opens that
line before rejecting the row. A candidate that bolts a second home onto a fact
the seed already owns breaks the seed's one-home-per-fact rule
(`rule.knowledge`), and that is worse than a missed lesson, because it splits a
fact across two homes that will drift.

## The flow (`harvest.fold-back-flow`)

Orchestrated like `grow`: the session plans, briefs, and ratifies, while
clean-context workers survey, triage, and author. Model classes follow
`delegation.model-classes`: the investigation class for read-only survey, the
authoring class for every generalization and authoring call.

**Running a large harvest.** Four habits carried a multi-plant round and are
the default:
- one read-only worker per plant (and per library in the cross-plant wave),
  each writing one scratch ledger and handing back a short summary;
- authoring lanes with disjoint write sets and one written ownership list
  that names each lane's files and its subjects: a shared file (an index, a
  README listing, a documentation mirror, the CHANGELOG) has exactly one
  owner, a fact two lanes could both write has one owner too, and no lane
  reads another lane's unlanded writes;
- every authoring lane is reviewed by a non-author before it lands (G2, G3),
  and the review's fixes are applied before the next batch;
- one full gate per batch, run when no writer is active, with only the
  changed files' own lints in between. A prose or corpus fold-back gets no new
  test: the existing checkers prove it (`test-first.proportionate-checks`).
  New tests come only with code, RED first.

A ruling the owner gives mid-flight is broadcast to the running workers and
recorded with the round's records. Keep a friction log against this protocol
as the round runs: it is the input to the next amendment of this node.

### Phase 1: Survey the mature plant (investigation-class scouts, read-only)

Inventory how the plant diverged from the seed it grew from, and what it
accumulated. A prior `graft`'s customization-audit ledger and its KEEP-PLANT
list (`tools/graft-audit.py` output, the graft record's "kept as the plant's"
section) is a ready-made divergence inventory: a machinery file the plant
customized that the graft preserved is already a flagged harvest candidate, so
start from it rather than rediscovering the divergence. Read the plant's
**harvest-candidate record** first of all, beside that ledger:
`docs/graph/plans/harvest-candidates.md`, the append-only rows the close-out
librarian added each time a lesson was flagged (`canonize.harvest-candidates`,
form `templates/docs/plans/_harvest-candidates.template.md`). Each row points
at the lesson's home in the plant; open the home, because the row never
restates the rule. A struck row stays struck unless new evidence is dated on it.

Before reading anything else, take **G5's baseline**: each plant's
`git rev-parse HEAD` and its `git status --porcelain` output, or, for a plant
with no repository of its own, a SHA-256 manifest of the files the survey will
read (G5 says why). Plants are often dirty when a harvest starts, and the gate
compares against what was there, not against a clean tree.

Harvest takes only the generalized, project-agnostic lesson from the plant's
`docs/graph/` and from the surfaces below that sit outside it. The plant's facts
stay in the plant. **Every plant-authored skill, procedure, tool, agent and
gate is a candidate by default**: the triage generalizes it rather than
rejecting it, and a procedure bound to one stack becomes a stack-keyed page,
not a reject (§Phase 2). Candidate donor surfaces, each mined that way:
- shared scripts/tooling the plant fixed or added;
- skills whose rules the plant sharpened, or gaps it hit that a core skill
  should close, and any **project skill** the plant authored (a repeatable
  procedure) whose steps generalize, mined for the agnostic procedure only;
- protocols the plant found insufficient or missing a step;
- agent/expert definitions authored to fill a roster gap;
- an **agent-operations system older than the graft**: charters and
  instruction files under the agent hosts' own directories (`.github/` and
  kin), hooks, and lesson or memory logs. Lesson logs are dated incident
  evidence, mined as problem-to-fix records; hooks are enforcement the plant
  ran; a copied facts table is drift. `grow` inventories the same surface when
  it adopts a project (`protocols/grow.md`, "An agent-operations system the
  project already runs");
- **harness-only skills**: procedures that live only in a harness directory
  (`.claude/skills/` and kin) with no home in `docs/graph/`. No graph survey
  sees them, and they are often the plant's most-used procedures;
- templates that gained a better section or default;
- the plant's accumulated sharp-edges / case library / ADRs, mined for the
  *generalizable prevention rule*, recast tool-neutrally;
- the plant's **problem-to-fix records** (ADRs, changelogs, plans of record,
  session records, runbooks, `recover` retries, lesson logs, and the plant
  repository's commit messages), mined for the case: symptom, cause, fix, the
  proof it held, and the trap that hid it, so a later session neither re-hits
  the problem nor guesses how it was solved. A case seen in several plants
  collapses into one. Strip the plant's identity and its incident timeline; keep
  the case. Each case lands in the existing page that owns its subject (a
  library page's pitfalls or major-line section, a skill-corpus step, a tool
  page, an agent charter, a method or protocol node, a runbook template), by
  holistic edit (§Phase 3);
- the **owner's decisions** in those records, mined for the decision rule and
  its reason, so a later session does not re-ask how the owner wants a kind of
  problem solved. An owner's *preference* (a working habit of the person, not a
  rule of the project) is owner-specific, and the seed is published: where a
  preference lands, the public corpus or a private overlay, is the owner's
  decision, asked before anything is written. Until the owner decides, it is
  not written;
- the plant's **plan-of-record** (`grill.md` §6 Decisions, §7 Options, §11
  Risks, §12 Open Questions) and its **ADRs**, mined for *decision and planning
  discipline* a plan should always carry (a decision's evidence and
  reversibility-with-trigger, a risk paired with the check that verifies it, an
  open question's pinned-by and do-not-guess marker, "do nothing" recorded as a
  decision), never this plant's actual decisions or their content;
- the plant's **best-practices pages** (`docs/graph/best-practices/`), mined
  for a durable engineering/security/testing *principle*;
- the plant's **runbooks** (`release`, `rollback`, `incident-response`,
  `verification`), mined for operational *discipline* (a release-readiness
  gate, a reversal that is non-autonomous and reversible-before-destructive, an
  incident loop that closes by adding a gate);
- the library & language wiki pages the plant built during `ingest-library`,
  mined for their **version-durable surface** only (see the corpora below): what
  the library is and how it is idiomatically used, its battle-tested pitfalls,
  and the version facts its release notes or docs state, never the plant's own
  version. The aim is a page a new plant adopts instead of running a scout (the
  withdraw-ready bar, §the corpora), so the depth the plant earned is harvested,
  not only its surface;
- the plant's reusable-tool catalog (`docs/graph/tools/`) built during
  `toolcraft`, mined for **project-agnostic, durable tools**: the capability
  and interface, and the portable implementation when it is stack-neutral;
- the plant's **legal / regulatory leaves**, where the plant reasoned against
  externally-authored rules, mined for the **citation only** (instrument,
  provision, `text_form` and text, publisher URL, verification grade, status),
  never the plant's application of the rule, its own determination, or any
  finding drawn from it. A citation is portable; a determination never is;
- the plant's **session metrics**, aggregated from delivery summaries (grill.md
  §15 / `docs/graph/changelog.md`, the block defined in
  `docs/graph/protocols/deliver.md`). This is the seed's only *quantitative*
  donor surface: recurring routing overrides or LOW-band spawns of the same
  kind mean a specialist's `routing_triggers` need sharpening; frequent tier
  reclassifications in one direction mean the kernel §0 tier edges need tuning;
  repeated retries of one failure class (`docs/graph/protocols/recover.md`)
  mean a protocol is missing a step, a gate, or a sharp-edge rule. Mine the
  *pattern*, propose the seed change; the plant's raw numbers stay in the
  plant. Read the block with the reader, never by hand:
  `python3 docs/graph/session-metrics.py --all --json` from the plant root
  prints every entry, an `incomplete` one included. A plant grown before the
  reader existed has no copy and an older `deliver.md`: run the seed's
  `tools/session-metrics.py --all --json --root <plant>/docs/graph --deliver
  <seed>/protocols/deliver.md`, so the labels come from the seed's template;
- a **capability the seed ships that stays inert**: a surface (a suggested
  skill, a runbook template, a corpus withdrawal) present as machinery on many
  plants yet grown on none. Inertness across plants is a design signal, not a
  plant fact. The withdraw contract may be missing, the capability may be
  mis-placed, or `graft`/`grow` may lack a step that actualizes it. Harvest the
  *fix to the seed's own machinery* (a clearer withdraw contract, a grow step).

Output: a **candidate ledger**, each row a candidate with provenance (where in
the plant, what triggered it) and a first guess at its class. Claims cite plant
paths/symbols; centralized prose is an untrusted clue until corroborated.

**A plant fact may be wrong: verify, do not transcribe.** Plants carry wrong
facts (a misremembered precedence order, a licence, the release a feature
became the default), and so do seed corpus pages. Every fact row in the ledger
carries one **provenance class**:
- **plant-proven**: the plant shows it with evidence a reader can open (a
  test, a measured run, a dated incident, a read of the library's source);
- **upstream-fetched**: a source retrieved this round, with its raw snapshot
  and `raw:` line (`skill.research-and-ingest`);
- **model-supplied**: the worker's own knowledge, tagged as such. It lands
  only after a `research-scout` fetch confirms it; unconfirmed, it is dropped.

Upstream documentation is right far more often than not, but a plant's
battle-tested observation can beat it. A plant-proven fact that upstream
confirms lands as fact. One that upstream contradicts or does not mention stays
on the page, labelled as observed in practice, with the conditions it was
observed under (never the plant's version) and what the docs say; a reproduced
or measured observation outweighs a one-off note, and neither side is silently
preferred. A plant claim shown wrong is dropped, and the ledger records why so
it is not carried over by the next harvest. A seed page that a plant or upstream
contradicts is a **correction candidate** like any other row: harvest doubles as
an audit of the corpus, and a correction is re-fetched upstream before the edit
(a legal entry's grade moves up only after a new fetch,
`harvest.corpus-contracts`).

**Several plants.** When a harvest takes more than one plant, Phase 1 runs in
two waves and a consolidation:
1. **Per plant.** One read-only worker per plant writes that plant's ledger.
2. **Per library, across plants.** A plant's library inventory is too big for
   its plant worker, and the same library recurs across plants. A second wave
   assigns each library to exactly one worker, by a written ownership list, and
   that worker reads every plant's page and evidence for it, checks the facts
   upstream or in the library's source, and writes one delta per library page.
   This wave is where wrong plant facts surface, because two plants disagree.
3. **Consolidate.** Merge the ledgers into one, one row per candidate, with
   each row's supporting lineages (not plants; §the third gate) and its
   provenance class. The merged `--forbid` vocabulary for G1 is collected
   here, from every plant.

### Phase 2: Triage against all three gates (authoring-class authors)

For each candidate, apply **all three** gates (agnosticism, durability,
non-redundancy) and decide KEEP-AS-IS / GENERALIZE / REJECT. For anything kept,
write its **generalized restatement**: the tool-neutral, version-durable form
that will land in the seed, with the before→after shown (what plant-specifics
*and* what plant versions were stripped). Reject rows carry a one-line
reason, including "redundant — the seed already owns this at `<home>`". This
phase is where the seed's purity is defended, and the default move is to
**generalize, not reject**: when in doubt, generalize harder. A row is
rejected only when it cannot be stated without the plant, when the seed already
owns it, or when it cannot reach the withdraw-ready bar. What generalizing
admits:
- **a stack-bound procedure or tool** lands as a stack-keyed page
  (`skill-corpus/<key>/<name>.md`, or a tool page's `stack:` field), keyed by
  the library corpus's ecosystem key, its subject the stack and never a plant;
- **deep stack expertise** lands in `library-corpus/`, deep enough that no
  plant re-researches that surface: install and configuration semantics,
  idioms, battle-tested pitfalls, testing, security defaults, operational
  behaviour, interop, and version facts. A page that cannot reach that bar
  (`library-corpus/README.md`, "The admission bar") is completed by a full
  ingest first or dropped; **no thin slice lands**;
- **a correction to a seed page** lands once re-fetched upstream (§Phase 1).

Every fact kept keeps its provenance class into Phase 3; a model-supplied fact
still unconfirmed here is dropped.

### Phase 3: Backport authoring (authoring-class authors)

Apply each surviving generalized improvement to the seed artifact it belongs in
(`skills/`, `protocols/`, `agents/`, shared scripts, `templates/`,
`library-corpus/`, `legal-corpus/`, `tool-corpus/`, `agent-corpus/`,
`skill-corpus/`, kernel), each as a **holistic edit**
(`skill.holistic-editing`), integrated into the artifact as if it had always
been there; a fold-back that cannot be integrated that way is not landed. Every
fold-back records provenance: which plant lineage or lineages it came from, the
generalization applied, and the seed files touched. The seed evolves
spec/test-first too, so a harvested tooling fix arrives with its regression
test generalized alongside it. Checks stay proportionate: a declarative or
prose fold-back (a corpus page, a doctrine edit) is proved by running the
existing checkers, never by writing a new test for it
(`test-first.proportionate-checks`).

**Disseminate into the homes that exist.** A case, a decision rule or a
corpus delta lands in the page or node that already owns its subject, woven in
so that it reads as if it had always been there. A new corpus, a new page kind
or a new top-level surface is the last resort: the proposal states why no
existing home can carry the row, and the owner rules on it before it is
written. This is the surface ladder (G9) applied to the harvest's bulk.

Three things are part of *authoring*, not of verifying, because a reader who
leaves them to Phase 4 has already written the defect:

- **Wire it in the same edit that lands it.** The delivery path an artifact
  needs (a `place_*` call, a line in the consuming node, a roster row) is
  written with the artifact, because an artifact deposited now and wired later
  is exactly the defect **G4** exists to find, and it can sit undelivered for
  many releases before anyone applies the gate. A fold-back that adds or
  changes a delivery mechanism (an installer arm, the corpus matcher, a grow
  step) is not GREEN until a **read-only live probe over the real donor
  plants** has run it: a fixture suite proves the cases its author thought of,
  and the live probe finds the recall gaps it missed.
- **Bring imported prose into the seed's voice.** A harvested page, charter,
  or section arrived in the plant's voice. Where it lands in a graph node, it
  becomes the node's compact instruction language, written for models, with no
  humanizer pass (`humanizer.scope`). Where it lands in human-facing
  documentation, apply `skill.humanizer`. Either way, floor the result with
  prose-lint and prove the pass dropped nothing. **G8** holds the commands.
- **Fit the fold-back to the limits.** Every budget, ceiling and debt ledger in
  the seed is recorded in `tools/ratchet-lint.py` and moves only toward
  stricter. A fold-back that does not fit a kernel budget, a body ceiling, or
  an eager-surface exemption is the wrong size: land it in a cheaper surface
  (**G9**). Raising the number is an owner decision taken in the open, and
  `ratchet-lint.py --bless` is the owner's signature alone, never the
  harvester's (**G11**).

### Phase 4: Seed integrity gate

The seed leaves harvest **more capable and no less agnostic**. A candidate
lands only when it clears every gate below; one that cannot stays in the plant,
with the reason recorded. The gates are not the price of a fold-back, they are
its definition. The table below is the **single home** of every gate this
protocol runs: the record in §Output format is its result column, and the
quality bar points at it rather than restating it. Adding a gate is one edit
here.

Every row names its command, **or** names the judgment and who owns it, in the
same cell (`rule.verify`).

`Class` uses `verify.gate-classes`. **Nothing here is `hard`**, because no
harness prevents a steward committing a harvest, and saying so is the point of
the column. The cell holds exactly that one word; the judge's name lives in the
command cell.

| # | Gate | What it asserts | Command, or the judge | On failure | Class |
|---|---|---|---|---|---|
| G1 | `harvest.gate.agnosticism-floor` | No host-IP literal, CVE id, operator home path, or supplied plant token survives in any changed file, and every changed file was actually opened | `python3 tools/agnosticism-lint.py --forbid <plant token> …` with one `--file` per changed file, the set enumerated from `git diff --name-only --diff-filter=d <pre-harvest rev>` (the literal invocation, and why the list is driven from git and never from an extension list: §G1 in detail). Exits 0, with no `unreadable` finding | BLOCK | soft |
| G2 | `harvest.gate.agnosticism-judgment` | The classes no regex sees: every class in §What counts as a project reference that G1's `--forbid` list did not cover | No command exists. Read `git diff` whole against that section, class by class, the version rule (§the second gate) included. Judge: the Phase-2 generalizer, then an authoring-class reviewer who did **not** author the diff and reads all of it, then the steward at ratification | BLOCK | judgment |
| G3 | `harvest.gate.faithful-import` | Each imported artifact carries the whole of its donor's generalizable discipline, with only plant-specifics stripped and never substance | No command exists. Section-by-section donor→import comparison, one per artifact; for a corpus page, also the withdraw-ready bar's sections marked present, absent or gap-stated, and spot-checks that re-open the cited sources and the provenance class of each sampled fact. Judge: an authoring-class reviewer who did **not** author the import | BLOCK | judgment |
| G4 | `harvest.gate.availability` | Every import is reachable by the flow that delivers it, proven against `install.sh` and the consuming node | The five-step resolution below; record the resolved path per artifact. A changed delivery mechanism also reports its read-only live probe over the real donors (§Phase 3) | BLOCK as INERT | detective |
| G5 | `harvest.gate.plant-untouched` | Every donor plant is byte-unchanged against the baseline taken before the survey read it (§Phase 1), because harvest is inbound-only | For each plant, `git -C <plant> rev-parse HEAD` matches the baseline HEAD and `git -C <plant> status --porcelain` matches the baseline porcelain line for line: empty when the plant was clean, the same dirt when the owner had work in progress. A plant with no repository of its own (`git rev-parse --show-toplevel` from its root names another directory) is compared by re-hashing the baseline's SHA-256 manifest: every listed file present with the same hash. A plant that is no longer reachable from the machine running the gate (the round moved hosts) is recorded as not checked, with the baseline kept as evidence, never as a pass. The plain form reads the tracked tree only, on purpose; stray files are what grow's `--ignored -uall` form finds. Both exit 0 either way, so the output is evidence a person reads, not a refusal | BLOCK | detective |
| G6 | `harvest.gate.self-consistency` | The seed's own full gate is green and every registry is in sync | `bash tests/run.sh`, every lint and suite: the whole run | BLOCK | soft |
| G7 | `harvest.gate.clean-install` | A by-hand install of the working tree into a fresh directory succeeds, and its owner-facing output says what this harvest expects | `bash install.sh claude-code --project-dir "$(mktemp -d)"` (the harness is positional; there is no `--harness` flag and the parser dies on one). Read the warnings, the re-created-node notices and the NEXT STEP lines. The install suites are G6's and are not re-run here | BLOCK | soft |
| G8 | `harvest.gate.prose` | Imported prose reads as the seed's own writing and lost no fact in the rewrite | `python3 tools/prose-lint.py --file <changed .md>` and `--against <pre-harvest rev>`, the floor on every changed file; above it, `skill.humanizer` judges human-facing documentation only, and a graph node gets no humanizer pass | BLOCK, or record the genre exception in the proposal | soft |
| G9 | `harvest.gate.minimum-sufficient` | The fold-back is the smallest edit that reaches its audience, in the cheapest surface that reaches it | No command exists. Weighed against `method.minimum-sufficient-work` and the surface ladder below. Judge: the steward at ratification | RETURNED as a smaller edit, not blocked | judgment |
| G10 | `harvest.gate.provenance` | The version is bumped, the CHANGELOG entry and harvest-log row exist, and every seed change carries a test or lint proof | `git diff --stat` shows `manifest.json` and `CHANGELOG.md`, read by a person; `python3 tests/seed-lint.py` holds the manifest, the kernel roster line and README to the agent frontmatter | NOT RELEASABLE | detective |
| G11 | `harvest.gate.no-loosened-limit` | No budget, ceiling, or debt ledger was widened to make a fold-back fit | `python3 tools/ratchet-lint.py`, the bare invocation `tests/run.sh` runs and G6 therefore covers. It is the only form that can fail, and it names each widened limit (`was LOOSENED`, `GREW by`). `--show` prints `recorded=… current=…` for every ratchet, says of none of them that it moved, and always exits 0: a reading aid, never a check. A loosening is an owner decision stated in the proposal | BLOCK pending the owner | soft |

**The surface ladder G9 weighs against.** Land the lesson in the cheapest
surface that still reaches its audience: a reference or corpus page before a
skill, a skill before a protocol, a protocol before the kernel. A new rule,
file, or section is the last resort, and kernel bytes cost every session of
every plant. `method.minimum-sufficient-work` owns *minimum sufficient work*;
this ladder is harvest's own ordering of the seed's surfaces, and the seed has
no other home for it.

**G6 is a green run, not a compliance certificate.** `tests/run.sh` exits 0 and
a reader hears "the seed obeys everything it checks", which is a different
claim: a large share of its steps read only `tests/fixtures/`, so they prove a
linter works and say nothing about the tree the seed ships.
`python3 tools/gate-registry.py --summary` prints how many of each, and
`--table` prints the false green each step can still produce. Read it before
writing G6's result line, and cite the class when a fold-back's only proof is a
fixture suite. If this harvest adds a step to `tests/run.sh`, the registry's
`--lint` (itself a step in `run.sh`) refuses it until the step is classified:
adding a gate without saying what it can miss is a defect the seed treats as
one.

#### G1 in detail: what the mechanical floor actually covers

`tools/agnosticism-lint.py` is the floor under G1 and G2, and the floor is
narrower than the definition it floors. State its real reach, because a clean
run reads like a verdict and is not one.

- It detects **host-IP literals** (loopback, unspecified, broadcast and the RFC
  5737 documentation ranges excepted), **CVE identifiers**, **absolute operator
  home paths** (generic placeholders excepted), and any term passed as
  `--forbid`. That is all four of its rules. It has no rule for a version
  number or a calendar date, so the version rule of §the second gate is G2's
  alone.
- It detects **none** of the six classes in §What counts as a project reference
  unless the run supplies them as `--forbid`. Supplying them is the harvester's
  job: the seed cannot hardcode a plant's vocabulary without leaking it, which
  is why the tool takes it as an argument. Whatever is not supplied is G2, and
  G2 has no tool.
- **Its default glob is `*.md` alone, and a glob list is a coverage boundary.**
  A directory contributes only its glob matches, so a changed `.py`, `.sh`,
  `.json`, `.tsv`, `.yml`, `.toml` or extensionless script under a changed
  `--root` is never opened and produces no finding of any kind. There is no
  silent-skip signal to read: the tool models `unreadable` for a file it failed
  to read and has no concept of a file it never matched, so an unlisted
  extension is indistinguishable from a clean tree. This is why **G1 names its
  files instead of its extensions.** A `--file` is scanned whatever the globs
  say, and the changed set comes from git with no hand-kept list in it:

  ```bash
  args=()
  while IFS= read -r -d '' f; do args+=(--file="$f"); done \
      < <(git diff -z --name-only --diff-filter=d <pre-harvest rev>)
  if [ ${#args[@]} -eq 0 ]; then
      echo "no changed files: G1 has nothing to scan"   # a PASS here is a lie
  else
      python3 tools/agnosticism-lint.py "${args[@]}" \
          --forbid <plant token> --forbid <plant domain>
  fi
  ```

  The loop is not ceremony, and the obvious one-liner
  (`$(git diff --name-only … | sed 's|^|--file |')`) fails two ways. A changed
  path containing a **space** word-splits under the unquoted `$(...)`, and the
  tool exits 2 on `unrecognized arguments`: the gate does not skip that file,
  it dies. And with **no changed files** the substitution contributes no
  arguments at all, so `roots` falls back to its default of `.`: the run scans
  an unrelated superset of the tree and prints `PASS`, which reads as "the
  changed set is clean" and is not. `-z` with `read -d ''` also survives a
  newline in a path, and is bash 3.2 (no `mapfile`, which this repo avoids for
  macOS).

  `--diff-filter=d` drops deletions, which would otherwise exit 2 as
  `no such path`. Reach for `--root`/`--glob` only for a directory added whole,
  and then state in the proposal which extensions the run could see.
- A file the tool cannot decode, a changed binary among them, is reported as
  `unreadable`. **Treat an `unreadable` finding as a BLOCK** to judge: an
  unread input is UNKNOWN, and unknown is not green. The tool also exits 2 on a
  run that matched no file, so a mistyped `--root` cannot print the verdict a
  real scan earns.
- **The seed's own committed gate covers less than this run does.**
  `tests/seed-lint.py` runs the same detector over
  `core/ agents/ protocols/ skills/ templates/` and the five corpora, with **no
  `--forbid` set** and the default `*.md` glob, plus `manifest.json`,
  `README.md` and `CHANGELOG.md` passed as **named files**, which are scanned
  whatever the glob says. So `docs/`, `tools/`, `tests/`, `integrations/`,
  `documentation/`, `install.sh` and the root prompt files sit outside the
  roots entirely, and inside the roots a `*.py`, `*.sh` or `*.tsv` file is
  never opened. A harvest that writes into any of them gets a green seed-lint
  that scanned none of it, and scans them itself with
  `--root`/`--file`/`--glob`.

#### G3 in detail: who judges a faithful import, and why it is not the author

An author comparing their own summary against its source reads the summary and
recognises it. Thinned passages and inverted contracts pass the author's own
check and are caught by a reviewer who did not do the import.

So G3's judge is a second authoring-class reviewer with the donor open, working
section by section, whose output is a per-artifact comparison and not a verdict
word. Reducing a full expert charter to a short blueprint, or a procedure to
its step titles, loses exactly the hard-won discipline the harvest exists to
compound, and reads like a clean summary while doing it.

The independent layer earns its cost. In a multi-plant round, every authoring
lane's own checks were lints, and the lints passed; the non-author reviews
then returned most lanes with fixes, mostly of three kinds: a fact the seed
already owns restated on a second page, a fact no source supports (or that the
source contradicts), and donor substance lost in the generalization. An
author's self-report ("no preference added", "no other page needs a change")
is a claim the review checks, not evidence. Run G2 and G3 on every lane, and
land the review's fixes before the next batch starts.

#### G4 in detail (`harvest.availability-gate`): prove reach against `install.sh` and the consumer

A withdraw contract in this file is a **claim about the installer**, and only
the installer settles it. A contract read back from this protocol's own prose
proves nothing: a corpus the installer never placed leaves every plant grown
meanwhile with an empty collection, and an analyst whose only available act is
refusal.

So for every artifact a harvest adds, resolve its delivery path:

1. **Decide which arm it uses.** There are two, and which one applies is a fact
   about the consumer, not a style choice.
   - **Placed**: the installer copies it into the plant. Two corpora are
     placed today, by two arms. The legal corpus is placed whole or not at
     all, and also on a re-install with no flag (its withdraw contract,
     below); its consumer has no filesystem reach to the seed, so an unplaced
     page is unreachable law. Library, tool and stack-keyed skill pages are
     placed **selectively**: `install.sh <host> --expertise propose` lists the
     pages the plant's manifests match (`tools/corpus-match.py`), the owner
     confirms a list, and `--expertise <id>,…` places exactly those (library
     pages at `docs/graph/libraries/<name>.md`, tool pages at
     `docs/graph/tools/<name>.md`, a skill page as the node
     `docs/graph/skills/<name>.md`), records them in `.cypress/seed.json`
     (`expertise`), and refreshes on every later install the recorded pages
     nobody edited (SPEC-0001 §6). A harvested page reaches this arm only if
     the matcher can name it: its `<key>/<name>` is a package a manifest
     declares, its `## What it is` own-package list names one (or, on a maven
     page, its coordinates), a page with no package carries a trigger
     SPEC-0001 §6 names, or its `stack:` field names a library page that
     matches.
   - **Read seed-side**: the corpus stays in the seed and the consuming node
     names its path formula. `agent-corpus/` is only of this kind, and a
     library, tool or skill page the owner did not place is read this way too:
     `ingest-library.corpus-first` looks for the seed's page on disk when the
     session can read a seed checkout. Such a page reaches a plant only through
     a session that has the seed.
2. **Prove the placed arm against the installer, by discovery.** Run
   `bash tests/test-install-placement.sh`: it discovers the destination set
   from a real install rather than from a list, and reading what it discovers
   is the move. A hardcoded list misses every writer added after it was written
   (bare `cp`s, redirections, `sed >`, embedded-Python writes), which is why
   the test discovers. Every destination a withdraw contract names appears in
   the discovered set.

   A grep is the **weaker fallback**, for when no install can be run, and it is
   weaker in a way that matters: it sees only the writers someone thought to
   name. Walk every composite `place_*` placer into the single-file writers it
   calls, and include the writers not named `place_*` at all. Any list written
   here would be out of date the next time a writer is added, which is why it
   is the fallback and not the step.
3. **Prove the seed-side arm against the consumer, and require a path
   formula.** A node that mentions a corpus without saying where a page lives
   establishes no reach. Two consumers meet that bar today:
   - `library-corpus/<ecosystem>/<library>.md` → `ingest-library.corpus-first`,
     which states the formula and the order it looks (a placed page, then the
     seed's corpus on disk);
   - `tool-corpus/<category>/<name>.md`, `skill-corpus/<name>.md` and the
     stack-keyed `skill-corpus/<key>/<name>.md` → `protocols/grow.md`, which
     states the formulas where it authors, and the stack-match condition: a
     keyed page is withdrawn only when the plant declares a library its
     `stack:` names (an upgrade page, only while the plant's line is older
     than the page's target line).

   Every other mention is a pointer, not reach, and the gate records it as
   such; each corpus's withdraw contract below names the consumers that point
   without a formula. Where the consumer names the corpus but no formula, the
   only reach is a seed-side session's own filesystem. Say that in the proposal
   instead of claiming a contract, and treat the gap as exactly the
   inert-capability candidate Phase 1 tells you to harvest. A README that
   states the formula is documentation, not reach: a file nobody is instructed
   to open is not a path.

   **Which corpora keep an index.** A consumer that can enumerate the directory
   is reached by the path formula alone, so an enumerable corpus keeps no
   index: a second listing is a copy of the filesystem that drifts against it.
   A consumer that **cannot** enumerate needs a routed `index.md`, because for
   that reader a missing row and a missing instrument are the same thing.
   Exactly one corpus is of the second kind: the legal corpus, read by an
   analyst with no filesystem reach whose whole discipline is that a gap
   produces a refusal. So a harvested legal page is in `legal-corpus/index.md`
   (and a decision in `legal-corpus/case-law/index.md`) or it is not reachable
   law, while a library, tool, expert or skill page is reached by its formula
   and gets no index at all. Nothing checks index membership; this one is the
   harvester's own read.
4. **Trace a harness-visible artifact to the harness.** An `agent-corpus` or
   `skill-corpus` entry is withdrawn by instantiating it into the project's
   `docs/graph/agents/` or `docs/graph/skills/<name>.md`; `install.sh`'s
   `project_agents` / `project_skills` then project it into every harness
   roster on the next run (`delegation.harness-registration` names the depth
   they read). Trace the last hop, to the harness, every time: a withdraw path
   that stops at `docs/graph/` leaves the artifact unspawnable.
5. **A base-roster promotion is present in every ground-truth surface**, and
   only some of them are held together by a tool. The surfaces are the agent
   file's frontmatter, `manifest.json`, the kernel roster line, the
   `method.delegation` specialist table, and `agents/_routes.golden.tsv`.
   `python3 tests/seed-lint.py` holds **three** of the five: frontmatter
   against `manifest.json`, and frontmatter against the kernel's §1 roster
   line. It never compares `agents/` to the delegation table, and it reads the
   golden corpus only to match `documentation/agents-reference.md` against it,
   so an agent with no golden rows passes. **A promoted agent missing from the
   delegation table or from `_routes.golden.tsv` passes this step green.** Open
   both by hand, name them in the proposal as hand-checked, and read the green
   as covering only the three it covers. Nothing at all checks that you *meant*
   to promote, which is the other half that is yours.

Record the resolved path per artifact in the proposal. Name the path:
"reachable" without one is a claim. A harvested artifact no
`install`/`grow`/`graft` path can reach is an **INERT** import: it compounds
nothing, and it is the mirror of grow's *"grown, not just installed"* and
graft's *"grown, not just grafted"*. Material imported but not made available
has not been harvested, only stored.

### Phase 5: Deliver (propose, do not impose)

Harvest **proposes**; the human steward **ratifies**. Emit the fold-back as a
reviewable patch/proposal against the seed with the harvest summary below. The
seed is deliberate, and its evolution is too.

## The corpora (`harvest.corpus-contracts`): five withdraw contracts

Five corpora carry knowledge forward between plants: library, legal, tool,
suggested-expert, suggested-skill. They are what `grow`, `graft`,
`ingest-library`, `toolcraft` and `canonize` actually consume from the seed,
and each is defined by the same four questions: where it lives, what is
portable, what stays out, and the withdraw contract that delivers it. Every
corpus page is orientation for the plant to confirm, not gospel to copy, and
every page is **withdraw-ready** before it lands: a new plant could adopt it
instead of rediscovering its subject, a library page instead of running a
research-scout on that library, a skill or tool page because a plant can run
the procedure or build the tool from the page alone. The bar's one home is
`library-corpus/README.md`, "The admission bar"; `tool-corpus/README.md` states
its procedure and tool form. A page that falls short is completed or dropped,
never landed thin.

**All three gates apply to every page of every corpus**: agnosticism (§the
agnosticism gate), durability (§the second gate) and non-redundancy (§the third
gate). Two carry an additional economy, stated in their own section: the
suggested-expert corpus is a catalog rather than a roster, and the legal corpus
is placed whole or not at all.

Every page also clears **G4**: each withdraw contract below is a claim about
what `install.sh` and the consuming node do, and G4 is where that claim is
checked against them rather than believed.

### The library & language documentation corpus

Ingesting a dependency is expensive: a scout downloads upstream docs, an author
normalizes and wikifies them into a version-pinned page. Most of that cost is
paid rediscovering the same **surface** every time, meaning what the library
is, its core API, how it is idiomatically used. That surface barely moves
between versions, and where it does move, the version it moved at is itself a
durable fact. What changes per plant is the pin, its advisories, and the
release notes that matter to that one project. Harvest folds the durable
surface, its version facts and the pitfalls plants paid for into a shared
corpus in the seed so the next plant starts from a page it can work from
instead of a blank page, then ingests its own pin's delta fresh.

- **Where it lives.** A seed-side corpus keyed by ecosystem + library, **not by
  version**: `library-corpus/<ecosystem>/<library>.md`. One page per library,
  describing the library in general, carrying its upstream doc/repo home as
  provenance. It is a cache of *library* knowledge, version facts included;
  the plant's facts, its pin and every security bulletin stay in the plant.
- **What is portable (surface, durable).** The durability gate's KEEP list: the
  capability the library provides, its core API shape and canonical usage,
  idioms and best practices that hold across releases, conceptual pitfalls
  inherent to the tool and the battle-tested ones plants met, and every version
  fact stated with the subject it qualifies. Strip every plant-specific usage
  example, path, and domain reference **and** every plant version before it
  lands. Each version it names is one the library's release notes or docs
  state. The page must read like the library's own docs, "changed in" notes
  included, usable by any project on any version the page covers, and it says
  which versions those are wherever the surface differs.
- **What stays out.** The durability gate's REJECT list: security facts (CVE
  ids, advisories, exposure warnings), calendar dates (the platform retrieval
  date excepted), a plant's own version, a bare version number. The pin and
  its advisories live in the *plant's* `docs/graph/libraries/<name>.md` and are
  rediscovered per project, because they are wrong the moment the pin moves.
- **The withdraw contract (consumed by `ingest-library`, and by `grow` through
  it).** Placed selectively on the owner's list (`install.sh --expertise`, which
  `grow` proposes from the plant's manifests and graft refreshes), or read
  seed-side when the session has a seed checkout, both as
  `ingest-library.corpus-first` states (G4 step 1); `grow` reaches this corpus
  only by proposing the placement and by invoking `ingest-library`. If a surface
  page exists, **seed the plant's `docs/graph/libraries/<name>.md` from it as
  the orientation layer**, then ingest from upstream only the version-specific
  facts the plant actually needs (the exact pin, its advisories, its
  deprecations) against the plant's real lockfile. If no surface page exists,
  ingest from upstream as usual, and the durable surface of that work becomes a
  harvest candidate for the next cycle. Start from the surface the corpus holds,
  and take every pinned fact from upstream.
- **Currency.** A surface page ages slowly but not never, since an API redesign
  across a major line can outdate it. A version fact the page states stays true
  for the version it names; what ages is the page's coverage of newer lines,
  which a later harvest or a correction extends. A plant's pin is never read
  from here at all, so a stale pin cannot leak: the corpus carries none.

### The legal & regulatory documentation corpus

Verifying a legal citation is expensive: a scout must find the official
publisher, get past whatever blocks a non-browser client, read the provision,
and correctly date the edition it actually read. Most of that cost is paid
rediscovering the same **primary text** every time, and that text is durable
far longer than any one plant's application of it, since a statute outlives
several codebases. Harvest folds the durable **citation** into a shared corpus
in the seed so the next plant that must comply with or reason about the same
body of law starts from a sourced orientation instead of a blank page, then
confirms currency and derives its own application fresh.

- **Where it lives.** A seed-side corpus keyed by jurisdiction scope +
  instrument, **not by the plant reading it**:
  `legal-corpus/<scope>/<instrument-slug>.md`, where `<scope>` is `eu`,
  `national` (country-code-prefixed filename), `international` (global
  standards bodies), or `case-law` (judicial and regulator decisions, which
  span jurisdictions and so get their own scope). One page per instrument, its
  entry shape fixed by `legal-corpus/_schema.md` and routed by
  `legal-corpus/index.md`. It is a cache of *citation* knowledge; the plant's
  compliance findings stay in the plant.
- **What is portable (citation, durable).** The citable entry itself: the
  instrument in full official form, the provision, its text graded by
  `text_form`, the official publisher URL, the `verification_grade` and
  verification date, and the `legal_status` on that date, plus the blockage
  that stopped a primary fetch, and any *verified absence* (a searched-for
  decision found not to exist). Inside its own scope a citation is as reusable
  as a library's API surface, because the law says the same thing to every
  project subject to it. Strip every plant-specific application and every
  unstated-edition citation before it lands.
- **What stays out (application, plant-bound).** Any application of the law to
  a system, meaning how a plant's architecture does or does not trigger a
  provision, and every finding, risk posture, gap, remediation status,
  source-file or component reference used to ground one, and every
  in-scope/compliant/exposed determination. These live in the *plant's* own
  `docs/graph/legal/` (or equivalent), generated fresh per project **against**
  the corpus as its orientation layer. The corpus states what the law says; the
  plant states what that means for one system. Legal analysis feels portable
  and is not, which makes this the sharpest agnosticism boundary of the five
  corpora.
- **The withdraw contract (consumed by `grow` / `graft`).** This is the one
  corpus the installer **places whole** (the library, tool and skill corpora are
  placed page by page, on the owner's list, G4 step 1): `place_legal_corpus`
  copies `legal-corpus/` whole into the plant's `docs/graph/legal/corpus/`, and
  refuses a partial copy, because the consuming analyst turns a corpus gap into
  a refusal and a subset therefore reads as a smaller body of law instead of a
  missing one. It runs on the owner's explicit `--legal-corpus yes`, and also
  with no flag at all on a re-install: when the flag is absent and the plant
  already exists, the installer re-derives the decision from `legal_corpus` in
  `.cypress/seed.json` and restores the corpus to match the record, so placement
  can happen on a run where nobody typed anything. The installer also reports
  which national jurisdictions the corpus carries against
  `--legal-jurisdiction`, so a country the corpus does not hold is recorded as
  absent instead of inferred. With the corpus in hand, a plant seeds its legal
  leaf from the matching entries as the orientation layer, re-confirms each
  entry's `verified` + `legal_status` before relying on it, then authors its own
  application against it. If no page exists, ingest from the official publisher
  as usual, and the durable, graded citation from that work becomes a harvest
  candidate for the next cycle. Start from the citation the corpus holds; the
  plant's determination is always its own, since the corpus carries none.
- **Currency.** A citation ages more slowly than a library API, but law amends,
  transposes, is annulled, and comes under appeal. Two disciplines keep a stale
  entry from passing as current. An entry states whether its text is the
  **original** or the **consolidated/as-amended** edition, the *amendment
  trap*, where an unamended reading of an amended instrument reads exactly like
  a correct one. And a `verification_grade` is **upgraded only after a new
  fetch**: downgrading on new evidence is expected, while upgrading without
  re-reading the source is falsification.

### The reusable-tool corpus

A plant builds durable tools during its life (`toolcraft`, kernel §3.8) and
catalogs them in `docs/graph/tools/`. Most of a tool's value is not the one
project's wiring but the **capability and approach**: what it does, its
interface, the algorithm behind it. When that is genuinely stack-neutral,
harvest folds it into a shared corpus in the seed so the next plant starts from
a working tool or a clear blueprint instead of reinventing the wheel.

- **Where it lives.** A seed-side corpus keyed by category + tool, **not by
  project**: `tool-corpus/<category>/<name>.md`. One page per tool, describing
  the tool in general. It is a cache of *reusable-tool* knowledge; the plant's
  operations stay in the plant.
- **What is portable (durable).** The capability and the recurring operation it
  serves; the interface shape (invocation, inputs, outputs) in the general; the
  approach/algorithm and enduring idioms; the portable implementation **when the
  tool is genuinely stack-neutral** (a self-contained script with no third-party
  or project dependencies, like the seed's own `graph-lint.py` /
  `agent-lint.py`). A tool that serves one stack is admissible too, with a
  `stack:` field naming the library-corpus pages it serves
  (`tool-corpus/README.md`, "The stack field"); its version facts (the minimum
  version of a tool it drives, a flag that changed) are those the driven tool's
  release notes or docs state. Strip every plant path, credential and domain
  reference **and** every plant's own pin before it lands.
- **What stays out (project-bound, ephemeral).** Project names, paths,
  credentials, dataset shapes, a call-site tied to one repo's layout, a
  dependency locked to one project's pin, an environment only this project has.
  These live in the *plant's* `docs/graph/tools/<name>.md`.
- **The withdraw contract (consumed by `grow`; pointed at by `toolcraft` /
  `canonize`).** Placed on the owner's list when its `stack:` matches the
  plant's manifests (G4 step 1), else read seed-side. The node that states the
  path formula is `protocols/grow.md`, where growth seeds
  `docs/graph/tools/<name>.md` from `tool-corpus/<category>/<name>.md` when the
  plant's real stack matches a portable tool the corpus carries. `toolcraft`
  names this corpus in the harvest direction (folding in, not withdrawing) and
  `canonize` tells the librarian to check it first; neither states where a page
  lives, so neither is reach on its own (G4 step 3). When a new plant needs a
  capability, it checks the corpus first: if a matching tool exists, **seed
  `docs/graph/tools/<name>.md` from it as the orientation layer**, adopting the
  portable implementation when the stack matches, or re-authoring against the
  plant's own stack (test-first) when it does not. If no tool exists, build it
  fresh, and the durable, agnostic surface of that work becomes a harvest
  candidate for the next cycle.
- **Currency.** A tool page ages slowly but not never, since an approach can be
  superseded; confirm it and adapt it to the plant.

### The suggested-expert corpus

The roster mirror of the library and tool corpora. A plant sometimes needs a
specialist the base roster lacks and commissions one, not because a stack was
unfamiliar (a plant closes a *knowledge* gap with an expertise node of its own,
which the router composes into the roster it already has) but because some work
needs its own tools, model class, stance, or isolation. Most of that role's
value sits in its **mandate**: what it owns, when to select it, how it bounds
against the base roster. Its stack wiring is the part that does not travel.
When that mandate is genuinely stack-neutral, harvest folds it into a seed-side
catalog so the next plant selects a ready role instead of reinventing it.

The roster's own economy applies on top of the three gates: the base team is
paid on every session of every plant, so a harvested role lands in the
**catalog** by default, and promotion is a separate decision.

**Promotion to the base roster is a separate, steward-only decision**, and the
bar is higher than "useful". The role's mandate must be **universal**, meaning
every project produces the thing it addresses rather than merely many of them,
and no base-roster agent may already cover it. A role that serves a domain some
projects simply do not have (a regulatory analyst, a stack specialist) stays in
the catalog however good it is, because the catalog costs nothing until
selected. Harvest may *propose* a promotion; it never performs one, and a
promotion that is ratified clears G4 step 5 before it is real.

- **Where it lives.** `agent-corpus/<name>.md`, one page per suggested role,
  keyed by role, not project. A catalog of *candidate* experts, never the
  active roster.
- **What is portable (durable).** The role's mandate, its when-to-select, its
  boundary against the base roster, and its `routing_triggers` exemplars, all
  statable with zero framework names.
- **What stays out.** A stack-specific expert (a framework/language/library
  specialist), and any role that duplicates a base-roster mandate. The first is
  the plant's own knowledge, which belongs in its expertise nodes against its
  own pins rather than in any roster; the second breaks one-home-per-fact. A
  role that owns a **discipline on a stack-shaped surface** (destroy-safety on
  declarative infrastructure, build-and-delivery from a commit to a running
  platform) is not a stack expert: it is admitted, catalog only, naming the
  base agent it narrows (`agent-corpus/README.md`, "What belongs here"). A role
  a plant lost and can only rebuild from its recorded outputs is marked as
  reconstructed, and nothing it did is invented.
- **The withdraw contract (consumed by `grow` / `graft` / commission).** Read
  seed-side. `core/method/delegation.md` and the orchestrator's charter both
  send a commissioning session here, and neither states the path formula, so
  the reach is a seed-side session's filesystem and G4 step 3 records it that
  way. When a project needs a role the base roster lacks, check the corpus
  first: if a match exists, instantiate it into the project's
  `docs/graph/agents/` from `docs/graph/templates/agent.template.md`, grounded
  in the project's version-pinned facts and the role's mandate + triggers; the
  harness projections (`.claude/agents/` and kin) are regenerated **from that
  graph home** by the next `install.sh` run, which is the hop that makes the
  role spawnable. Else commission fresh, and its durable, agnostic mandate
  becomes a harvest candidate. A selected role joins the *project's* roster
  (and its kernel table), never the seed's.

### The suggested-skill corpus

The procedure mirror of the corpora above. A plant sometimes authors a project
**skill**, a repeatable procedure such as a migration recipe or a release
choreography, that would serve any project, or any project on the same stack.
Harvest folds its agnostic form into a seed-side catalog so the next plant
instantiates a ready procedure instead of rediscovering the sequence. A
procedure bound to a stack (an upgrade across a framework's major lines, say)
is harvested as a stack-keyed page; it is generalized, not rejected.

- **Where it lives.** `skill-corpus/<name>.md`, one page per suggested
  procedure, keyed by procedure, not project; a stack-bound procedure at
  `skill-corpus/<key>/<name>.md`, where `<key>` is a library-corpus ecosystem
  key and the page's `stack:` field names the library-corpus pages whose
  presence in a plant makes it a candidate (`skill-corpus/README.md`,
  "Stack-keyed pages"). `<name>` is unique across the corpus, keys included. The
  core `skills/` stay the fixed shared methodology; this corpus holds *optional*
  procedures a project selects.
- **What is portable (durable).** The procedure's steps and the gate each one
  clears, stated by **composing** existing protocols/skills by reference (one
  home per procedure).
- **What stays out.** A procedure bound to one repo layout or one plant (the
  plant's own), anything duplicating a core skill, and a keyed page that
  restates the generic page it specializes instead of naming it. The stack is a
  keyed page's subject, and its version facts (a major-line boundary it
  upgrades across, a minimum version a step needs), as the library documents
  them, are admissible; a plant's version is not.
- **The withdraw contract (consumed by `grow`; pointed at by `toolcraft` /
  `canonize` / commission).** A stack-keyed page is also placed on the
  owner's list (G4 step 1); otherwise read seed-side. `protocols/grow.md` is
  the node that states the formula, seeding `docs/graph/skills/<name>.md` from
  `skill-corpus/<name>.md` or `skill-corpus/<key>/<name>.md` where a
  repeatable procedure the source actually performs matches an entry, a keyed
  page only on a stack match; `toolcraft` names the corpus in the harvest
  direction and `canonize` tells the librarian to check it first, neither
  saying where it lives (G4 step 3). Check the corpus first; if a match exists,
  instantiate it into the project's `docs/graph/skills/<name>.md` from
  `docs/graph/templates/skill.template.md`, grounding its steps in the
  project's real gates and tools. `install.sh` then projects that graph home
  into `.claude/skills/<name>/SKILL.md` and kin on the next run, the same as
  any seed skill. Else author it fresh, and its durable form becomes a harvest
  candidate. G4 step 4 re-verifies this contract's last hop on every harvest.

## Output format

Harvest produces **two distinct records, and they do not carry the same
content**:

1. **The ratification proposal**, stated in chat or the PR for the steward to
   review. It *may* name the plant and show every before→after generalization,
   because it is the evidence the steward weighs, and it is **never committed
   to
   the seed.**
2. **The seed-committed record**, the CHANGELOG entry and harvest-log row that
   land *inside* the seed, bound by the agnosticism gate (§What counts as a
   project reference) exactly like any other seed artifact. It records *that* a
   harvest happened and *what* generalized lesson landed, never *whose* plant
   it
   came from.

**Proposal: to the steward, may name the plant, never committed:**

```markdown
# Harvest proposal — from <plant lineage id, or each lineage of a multi-plant round> — YYYY-MM-DD

## Harvested (generalized fold-backs)
- <seed file touched> — lesson: <universal statement> — generalized-from:
  <plant surface> — before→after: <what was stripped to make it agnostic>
- ...

## Rejected (stayed in the plant)
- <candidate> — reason it is not project-agnostic

## Provenance ledger
- <one row per fold-back: plant lineage(s), source surface, provenance class
  of its facts (plant-proven / upstream-fetched; model-supplied only once
  fetched), seed target, the check that proves it (a test only for code)>

## Seed integrity gate (the result column; the plant may be named here)
- <one line per row of the Phase 4 gate table, in its order, no row omitted.
  A row that names a command reports `<id>: PASS — <command> → <result>` or
  `BLOCK (<what>)`. A `judgment` row reports `<id>: PASS — judged by <who>,
  evidence: <where it can be read>`. A row with no result is a blank cell, and
  a blank cell is the green lie the table exists to prevent.
  G4's line expands to one row per artifact: arm (placed / seed-side),
  resolved path (the `place_*` call the discovery found, or the consuming node
  and its path formula), last hop (harness projection, roster surface, or n/a).>

## Recommended next step
<single highest-leverage action — usually "ratify and merge" or "one more
candidate to generalize">
```

**Seed-committed harvest-log: agnostic, no plant identity; this is what
enters the CHANGELOG (and `HARVEST_LOG.md` if the seed keeps one):**

```markdown
# Harvest — from a grown plant — YYYY-MM-DD

Harvested:   <count + kind of generalized fold-backs, e.g. "3 corpus pages;
             6 doctrine/template rules"> — no plant identity.
Generalized: every plant name/domain/path/credential/host/port, every stack
             fingerprint and identifying count, every plant version and every
             security fact stripped; documented version facts about a library
             kept with their subject.
Rejected:    <generic categories only, e.g. "internal/proprietary pages;
             kernel/agent duplicates">.

## Seed integrity gate (verdicts only; no command, no output, no path)
- <id>: PASS
- <id>: BLOCK (<seed-side reason, e.g. "a rule the seed already owned">)
- <one such line per row of the Phase 4 gate table, in its order, no row
  omitted. The id and the verdict, nothing else: the evidence that produced
  the verdict is the proposal's.>
- Version bump: <old> → <new>
```

**Why the committed record carries no evidence.** It is bound by the
agnosticism gate, and a gate's own result string is made of plant identity:
G1's command is the plant's forbidden-token list spelled out, G5's result is
`git -C <plant> status` output, G4's is resolved paths. Printing
`<command> → <result>` into the seed would route every class in §What counts as
a project reference through this protocol's own output template, so the
contamination the gate stops would arrive by the door built to stop it. The
evidence lives in the proposal, where naming the plant is the point; the seed
keeps the
roll-call.

## Quality bar

Everything the Phase 4 table asserts is asserted *there*, and the discipline of
each phase is stated in that phase. What is left is the judgment neither one
carries: what a *good* harvest looks like once every row of that table is
green.

- **It leaves the seed more capable, and that is not the same as landing
  something.** A harvest that lands nothing because nothing generalized is a
  correct and complete outcome, and says so in the proposal. A harvest that
  lands a rule the seed already owned is a failure with every row green.
- **The steward weighs evidence, not a verdict.** Every fold-back reaches
  ratification with its before→after (Phase 2) and its resolved delivery path
  (G4) legible, because a proposal the steward cannot check is a request for
  trust, and trust is how contamination reaches the seed.
- **What the plants knew is not lost to a thin slice.** Depth a plant paid for
  (a pitfall, a version boundary, a problem and its fix) lands whole in the
  page that owns it, or the row is dropped with its reason. A corpus page that
  leaves the next plant to run the scout anyway was stored, not harvested.
- **The seed reads as one author afterwards.** An import that is agnostic,
  faithful and reachable but audibly written by somebody else has been stored
  rather than integrated (Phase 3, G8).
