---
name: harvest
description: The inverse of grow. Once a plant (a project grown from the seed) is mature, harvest its GENERALIZABLE lessons back into the seed — tooling fixes, new skill rules, protocol gaps, agent-definition and template improvements — while keeping the seed STRICTLY project-agnostic, so the next plant grows more magnificent. TRIGGER IS MANUAL ONLY — the user starts a harvest, or the system at most PROPOSES that one is worth running; it NEVER runs automatically. Nothing reaches the seed until the user is satisfied with the growth. There must be NO reference to any specific project anywhere in the seed — not a name, a stack fingerprint (a language/framework combo that identifies the plant), an identifying count, an internal-component or file/config name, a path, or an illustrative example framed as "this project's X" — and this applies to EVERYTHING committed, including the CHANGELOG entry, the harvest-log, and provenance notes; plant-identifying provenance lives only in the ratification proposal shown to the steward, never in the seed's committed files. Never copies project-specific facts, names, domains, stack pins, data, or self-healing incident narratives into the seed; it proposes generalized fold-backs for human ratification, never silently mutates the seed.
id: protocol.harvest
tier: 2
kind: protocol
origin: seed
title: harvest — folding a mature plant's project-agnostic lessons back into the seed, user-triggered only
owns:
  - harvest.fold-back-flow
  - harvest.agnosticism-gate
requires:
peers:
  - protocol.graft
  - protocol.grow
load_when:
  - "harvest lessons back into the seed"
  - "fold generalizable improvements upstream"
  - "the plant is mature, propose a harvest"
  - "seed improvement from project experience"
est_tokens: 7000
---

# Protocol: harvest

`grow` runs the seed → into a project → and grows it. `harvest` runs the
other direction: a mature project → back into the seed → so the next
project starts ahead of where this one did. A seed that only ever seeds,
and never harvests, cannot improve; a seed that harvests carelessly rots
into a pile of one project's specifics. This protocol is the disciplined
gate that lets the seed compound **without** losing its agnosticism.

The metaphor is load-bearing: the seed grows a plant; the plant lives its
own life and learns things; harvest takes only the seed-worthy essence of
what it learned — never the plant's flesh — and folds it back so the next
seed is richer. What goes back in must be true for *any* future plant, not
this one.

## Trigger — manual only, never automatic

Harvest is **user-sovereign**. Unlike `canonize`, which runs at the end of
every task, harvest is **never** triggered automatically, on a schedule, by a
hook, or as a "while I'm here" step at the end of another protocol. The seed is
the inheritance of every future plant; changing it is the user's call, not the
system's.

- **The user starts it** — by invoking this protocol or pasting `HARVEST_PROMPT.md`.
- **The system may, at most, PROPOSE it** — when a mature plant clearly holds
  generalizable lessons, an agent may *suggest* "this looks worth harvesting into
  the seed" and stop. It does not begin. The suggestion is a doorbell, not an
  entry.
- **Nothing reaches the seed until the user is satisfied with the growth.** Every
  fold-back is a proposal the user ratifies; an unratified harvest is a draft, not
  a change. If the user is not satisfied, the proposal is revised or dropped — the
  seed stays as it was.

## When to invoke

- The **user** has asked to harvest, or ratified a proposal to. (Maturity below
  is a precondition for *proposing*, never an automatic trigger.)
- A plant is **fully grown**: delivered, its verification gates green, its
  plan-of-record closed or steady. Harvest a living, still-churning project
  and you will backport half-baked lessons.
- The plant's life produced **generalizable** artifacts worth compounding:
  a shared-tooling bug fixed, a new hard rule a skill should have carried, a
  protocol gap discovered, a new reusable expert authored, a template that
  grew a better section, a class of failure whose *prevention* is universal.
- You are the seed's **steward** (the user acting as the seed's owner — the two
  words name the same person), working with the seed as the target scope. The
  plant is a read-only donor; the seed is the only thing this protocol writes.

## The agnosticism gate — the heart of this protocol

Every candidate improvement passes one hard test before it may touch the
seed:

> **Would this help an arbitrary next project, in a different language,
> framework, and domain, that has never heard of this plant?**

- **YES, verbatim** → harvest as-is (rare; usually only tool-neutral rules).
- **YES, once generalized** → rewrite it stripping every plant-specific
  name, domain term, stack pin, path, and example, until only the universal
  kernel remains — *then* harvest the generalized form. State the
  before→after generalization explicitly.
- **NO** → reject. It is the plant's life, not the seed's. Record why, leave
  it in the plant.

Fail-closed corollary: **if you cannot state the lesson without naming the
plant, it is not ready to harvest.** Generalize it or drop it. A single
leaked project name, domain noun, credential, dataset shape, or
version-pinned specific in the seed is a failed harvest — worse than a
missed lesson, because it silently narrows the seed for everyone downstream.

### What counts as a project reference (all forbidden in the seed)

"Project-agnostic" is stricter than "unnamed" — a reference need not name the
plant to identify it. **Every one of these is a project reference and must not
survive into the seed anywhere — including the CHANGELOG entry, the harvest-log
row, provenance notes, and any illustrative example:**

- a **name** — the plant, its product, company, service, or an internal tool or
  library of its own;
- a **stack fingerprint** — the specific language/framework/datastore combination
  that identifies the plant (e.g. "a `<language>/<framework>` microservices
  plant"). Name a library only where the seed genuinely documents that library
  for *any* project (the library corpus), never as "the stack this plant ran";
- an **identifying count or metric** — "authored N library pages", "an N-observer
  registry" — a figure that describes this plant's scale rather than a universal
  rule;
- a **description of the plant's internals** — its file names, config keys, plugin
  names, module wiring, or a security finding on its own code;
- a **path, host, port, credential, or absolute install location** (`/root/…`);
- an **illustrative example framed as the plant's own** — "this project's fleet
  does X". Recast every example in the generic ("a fleet may do X"); an example
  is admissible only once it no longer belongs to any specific project.

Plant-identifying provenance — which plant it was, its stack, the exact
before-text that was stripped — belongs in the **ratification proposal you show
the steward**, never in the seed's committed files. The seed records *that* a
harvest happened and *what* generalized lesson landed; it never records *whose*
plant it came from.

### The second gate — durability (surface, not pin)

Agnosticism asks *"true for another project?"* Durability asks a second,
independent question of every fact:

> **Will this still be true a version from now — is it about the library,
> or about one pinned release of it?**

The seed's inheritance is **surface-level, version-durable** knowledge: what
a library is for, its stable API shape, its enduring idioms and conceptual
pitfalls. That is what compounds. Anything keyed to an exact release is the
*plant's* concern, discovered fresh by `ingest-library` against the plant's
own lockfile — it rots the moment the pin moves.

- **KEEP (surface, durable):** the capability the library provides; its core
  API shape and canonical usage; idioms and best practices that hold across
  minor/major lines; conceptual gotchas inherent to the tool; the upstream
  doc/repo home.
- **REJECT (pinned, ephemeral):** CVEs and advisories tied to an exact
  version; "version X.Y.Z is a breaking-change marker"; deprecations
  introduced in a specific release; upgrade/migration diffs between two
  pins; a resolved-version number itself. These belong in the plant's
  `docs/graph/libraries/<name>.md`, never in the seed.

When in doubt, a fact is pinned — drop it. A corpus page that reads like a
security bulletin for one release has failed this gate; one that reads like
the opening orientation of the library's own docs has passed.

### The third gate — non-redundancy (does the seed already own this?)

Agnosticism asks *"true for another project?"*; durability asks *"true a
version from now?"*. The third gate asks the question this protocol most
often forgets:

> **Does the seed ALREADY say this — in a kernel rule, an agent, a skill, a
> protocol, or a template?**

A plant grew *from* the seed, so its ADRs, plan-of-record, best-practices,
and runbooks are saturated with the seed's own doctrine filled in with local
facts. A survey that reads only the plant will keep "discovering" rules the
seed already ships — reversibility-with-trigger, a risk paired with its
verifying check, fail-closed defaults, released-bits-are-tested-bits,
resolve-in-place, two-axis severity — and proposing them back is not a
harvest, it is an echo. Before any candidate is proposed, **open its would-be
seed home and read it**: if the rule already lives there, the candidate is
**rejected as redundant**, and only the genuinely net-new residue survives.
Corroboration across several plants raises confidence that a *net-new* rule is
universal; it never converts a seed duplicate into a fold-back. A candidate
that bolts a second home onto a fact the seed already owns fails the seed's
one-home-per-fact rule (`seed-lint`) — worse than a missed lesson, because it
splits a fact across two homes that will drift.

## The flow

Orchestrated like `grow`: the session plans, briefs, and ratifies; clean-context
workers survey, triage, and author. Model policy is strict — Sonnet-class for
read-only survey, Opus-class for every generalization and authoring call.

### Phase 1 — Survey the mature plant (Sonnet scouts, read-only)

Inventory how the plant diverged from the seed it grew from, and what it
accumulated. A prior `graft`'s customization-audit ledger and its KEEP-PLANT list
(`tools/graft-audit.py` output, the graft record's "kept as the plant's" section)
is a ready-made divergence inventory — a machinery file the plant customized that
the graft preserved is already a flagged harvest candidate; start from it rather
than rediscovering the divergence. Candidate donor surfaces:
- shared scripts/tooling the plant fixed or added;
- skills whose rules the plant sharpened, or gaps it hit that a core skill
  should close — and any **project skill** the plant authored (a repeatable
  procedure) whose steps generalize, mined for the agnostic procedure only;
- protocols the plant found insufficient or missing a step;
- agent/expert definitions authored to fill a roster gap;
- templates that gained a better section or default;
- the plant's accumulated sharp-edges / case library / ADRs — mined for the
  *generalizable prevention rule* only, never the incident narrative;
- the plant's **plan-of-record** (`grill.md` §6 Decisions, §7 Options, §11
  Risks, §12 Open Questions) and its **ADRs** — mined for *decision and
  planning discipline* a plan should always carry (a decision's evidence and
  reversibility-with-trigger, a risk paired with the check that verifies it,
  an open question's pinned-by and do-not-guess marker, "do nothing" recorded
  as a decision), never this plant's actual decisions or their content;
- the plant's **best-practices pages** (`docs/graph/best-practices/`) — mined
  for a durable engineering/security/testing *principle*, never a
  stack-specific rule, a framework API, or a pinned advisory;
- the plant's **runbooks** (`release`, `rollback`, `incident-response`,
  `verification`) — mined for operational *discipline* (a release-readiness
  gate, a reversal that is non-autonomous and reversible-before-destructive,
  an incident loop that closes by adding a gate), never its hosts, commands,
  or ports;
- the library & language wiki pages the plant built during `ingest-library`
  — mined for their **version-durable surface** only (see the corpus section
  below): what the library is and how it is idiomatically used, never the
  plant's pinned CVEs, per-release deprecations, or migration diffs.
- the plant's reusable-tool catalog (`docs/graph/tools/`) built during
  `toolcraft` — mined for **project-agnostic, durable tools** (see the tool
  corpus section below): the capability and interface, and the portable
  implementation when it is stack-neutral, never the plant's paths,
  credentials, or stack-pinned wiring;
- the plant's **legal / regulatory leaves**, where the plant reasoned against
  externally-authored rules — mined for the **citation only** (instrument,
  provision, `text_form` and text, publisher URL, verification grade, status),
  never the plant's application of the rule, its own determination, or any
  finding drawn from it. A citation is portable; a determination never is;
- the plant's **session metrics**, aggregated from delivery summaries
  (grill.md §15 / `docs/graph/changelog.md`, the block defined in
  `docs/graph/protocols/deliver.md`) — the seed's only *quantitative* donor
  surface: recurring routing overrides or LOW-band spawns of the same
  kind → a specialist's `routing_triggers` need sharpening; frequent
  tier reclassifications in one direction → the kernel §0 tier edges
  need tuning; repeated retries of one failure class
  (`docs/graph/protocols/recover.md`) → a protocol is missing a step, a gate, or
  a sharp-edge rule. Mine the *pattern*, propose the seed change; the
  plant's raw numbers stay in the plant.
- a **capability the seed ships that stays inert** — a surface (a suggested
  skill, a runbook template, a corpus withdrawal) present as machinery on many
  plants yet grown on none. Inertness across plants is a design signal, not a
  plant fact: the withdraw contract may be missing, the capability may be
  mis-placed, or `graft`/`grow` may lack a step that actualizes it. Harvest the
  *fix to the seed's own machinery* (a clearer withdraw contract, a grow step),
  never any plant's would-be content.

Output: a **candidate ledger** — each row a candidate with provenance (where
in the plant, what triggered it) and a first guess at its class. Claims cite
plant paths/symbols; centralized prose is an untrusted clue until corroborated.

### Phase 2 — Triage against all three gates (Opus authors)

For each candidate, apply **all three** gates — agnosticism (§ above),
durability (§ the second gate), and non-redundancy (§ the third gate) — and
decide KEEP-AS-IS / GENERALIZE / REJECT. For anything kept, write its
**generalized restatement** — the tool-neutral, version-durable form that will
land in the seed, with the before→after shown (what plant-specifics *and* what
pinned specifics were stripped). Reject rows carry a one-line reason (including
"redundant — the seed already owns this at `<home>`"). This phase is where the
seed's purity is defended; be conservative — when in doubt, reject or
generalize harder.

### Phase 3 — Backport authoring (Opus authors)

Apply each surviving generalized improvement to the SEED artifact it belongs
in (`skills/`, `protocols/`, `agents/`, shared scripts, `templates/`,
`library-corpus/`, `legal-corpus/`, `tool-corpus/`, `agent-corpus/`,
`skill-corpus/`, kernel), each as a **holistic edit** — integrated into the
artifact as if it had always been there, never bolted on. Every fold-back
records provenance: which plant lineage it came from, the generalization
applied, and the seed files touched. The seed evolves spec/test-first too: a
harvested tooling fix arrives with its regression test generalized alongside it.

### Phase 4 — Seed integrity gate (fail-closed)

The seed must leave harvest **more capable and no less agnostic**:
- **Agnosticism scan** — grep the *entire* diff, including the CHANGELOG entry,
  the harvest-log row, and any provenance note (they are seed artifacts too), for
  any plant name, domain noun, stack fingerprint (a language/framework combo that
  identifies the plant), identifying count, internal-component/file/config name,
  path, credential, dataset shape, or version pin. Any hit BLOCKS.
- **Self-consistency** — run the seed's own lints/tests; the kernel,
  manifest, protocol table, and any registries stay in sync.
- **Clean install** — a dry-run install into a scratch target still succeeds
  and is additive.
- **Minimum-sufficient fold-back** — a candidate that passed all three gates
  still pays rent review (the seed's `core/method/engineering-posture.md` —
  minimum sufficient work, rent-earning structure): generalize an
  existing rule rather than appending a sibling; land the lesson in the
  cheapest surface that reaches its audience (a reference file before a
  protocol, a protocol before the kernel — kernel bytes cost every session of
  every plant); prefer the smallest edit that carries it. A fold-back that
  could have been a one-line sharpening of an existing home is returned in
  that form, not as a new rule, file, or section.
- **Version + provenance** — bump the seed version, add a CHANGELOG entry and
  a harvest-log row. A gate that runs but asserts nothing is a green lie;
  each check names its command and result.

### Phase 5 — Deliver (propose, do not impose)

Harvest **proposes**; the human steward **ratifies**. Emit the fold-back as a
reviewable patch/proposal against the seed with the harvest summary below —
never a silent mutation of the seed. The seed is deliberate; its evolution is
too.

## The library & language documentation corpus

Ingesting a dependency is expensive: a scout downloads upstream docs, an author
normalizes and wikifies them into a version-pinned page. Most of that cost is
paid rediscovering the same **surface** every time — what the library is, its
core API, how it is idiomatically used. That surface barely moves between
versions; only the pins, CVEs, and per-release quirks do. Harvest folds the
durable surface into a shared corpus in the seed so the next plant starts from
an orientation instead of a blank page — then ingests the version-specific
delta fresh.

- **Where it lives.** A seed-side corpus keyed by ecosystem + library,
  **not by version**: `library-corpus/<ecosystem>/<library>.md`. One page per
  library, describing the library in general, carrying its upstream doc/repo
  home as provenance. It is a cache of *library-surface* knowledge, never a
  second home for a plant's facts and never a version-pinned bulletin.
- **What is portable (surface, durable).** Only the version-durable surface:
  the capability the library provides, its core API shape and canonical usage,
  idioms and best practices that hold across releases, and conceptual pitfalls
  inherent to the tool. Strip every plant-specific usage example, path, and
  domain reference (agnosticism gate) **and** every version-pinned specific
  (durability gate) before it lands. The page must read like the opening
  orientation of the library's own docs — usable by any project on any recent
  version.
- **What stays out (pinned, ephemeral).** Exact-version CVEs and advisories,
  "version X.Y.Z is a breaking marker" notes, deprecations introduced in a
  specific release, upgrade/migration diffs between two pins, and resolved
  version numbers. These live in the *plant's* `docs/graph/libraries/<name>.md`
  and are rediscovered per project — they are wrong the moment the pin moves.
- **The withdraw contract (consumed by `grow` / `ingest-library`).** When a new
  plant needs a library, `ingest-library` checks the corpus FIRST: if a surface
  page exists, **seed the plant's `docs/graph/libraries/<name>.md` from it as
  the orientation layer**, then ingest from upstream only the version-specific
  facts the plant actually needs — the exact pin, its advisories, its
  deprecations — against the plant's real lockfile. If no surface page exists,
  ingest from upstream as usual, and the durable surface of that work becomes a
  harvest candidate for the next cycle. Never re-derive the surface the corpus
  already holds; never trust the corpus for a pinned fact.
- **Currency.** A surface page ages slowly but not never — an API redesign
  across a major line can outdate it. Treat it as orientation to confirm, not
  gospel to copy. Pinned facts are never read from here at all, so a stale pin
  cannot leak: the corpus simply has none to be stale.

## The legal & regulatory documentation corpus

Verifying a legal citation is expensive: a scout must find the official
publisher, get past whatever blocks a non-browser client, read the provision,
and correctly date the edition it actually read. Most of that cost is paid
rediscovering the same **primary text** every time — and that text is durable
far longer than any one plant's application of it: a statute outlives several
codebases. Harvest folds the durable **citation** into a shared corpus in the
seed so the next plant that must comply with or reason about the same body of
law starts from a sourced orientation instead of a blank page — then confirms
currency and derives its own application fresh. This is the statute mirror of
the library corpus above; both gates apply.

- **Where it lives.** A seed-side corpus keyed by jurisdiction scope +
  instrument, **not by the plant reading it**:
  `legal-corpus/<scope>/<instrument-slug>.md`, where `<scope>` is `eu`,
  `national` (country-code-prefixed filename), `international` (global standards
  bodies), or `case-law` (judicial and regulator decisions, which span
  jurisdictions and so get their own scope). One page per instrument, its entry
  shape fixed by `legal-corpus/_schema.md` and routed by `legal-corpus/index.md`.
  It is a cache of *citation* knowledge, never a second home for a plant's
  compliance findings.
- **What is portable (citation, durable).** The citable entry itself: the
  instrument in full official form, the provision, its text graded by
  `text_form`, the official publisher URL, the `verification_grade` and
  verification date, and the `legal_status` on that date — plus the blockage that
  stopped a primary fetch, and any *verified absence* (a searched-for decision
  found not to exist). Inside its own scope a citation is as reusable as a
  library's API surface: the law says the same thing to every project subject to
  it. Strip every plant-specific application (agnosticism gate) **and** every
  unstated-edition citation (durability gate) before it lands.
- **What stays out (application, plant-bound).** Any application of the law to a
  system — how a plant's architecture does or does not trigger a provision — and
  every finding, risk posture, gap, remediation status, source-file or component
  reference used to ground one, and every in-scope/compliant/exposed
  determination. These live in the *plant's* own `docs/graph/legal/` (or
  equivalent), generated fresh per project **against** the corpus as its
  orientation layer. The corpus states what the law says; the plant states what
  that means for one system. Legal analysis feels portable and is not: this is
  the sharpest agnosticism boundary of the five corpora.
- **The withdraw contract (consumed by `grow`).** When a new plant must reason
  about a body of law, it checks the corpus FIRST: if an instrument page exists,
  **seed the plant's legal leaf from it as the orientation layer**, re-confirm
  each entry's `verified` + `legal_status` before relying on it, then author the
  plant's own application against it. If no page exists, ingest from the official
  publisher as usual, and the durable, graded citation from that work becomes a
  harvest candidate for the next cycle. Never re-derive a citation the corpus
  already holds; never read a plant's determination out of it, because there are
  none in it to read.
- **Currency.** A citation ages more slowly than a library API but law amends,
  transposes, is annulled, and comes under appeal. Treat an entry as orientation
  to confirm, not gospel to copy. Two disciplines are non-negotiable and are why
  a stale entry cannot quietly pass as current: an entry must state whether its
  text is the **original** or the **consolidated/as-amended** edition — the
  *amendment trap*, where an unamended reading of an amended instrument reads
  exactly like a correct one — and a `verification_grade` is **never upgraded
  without a new fetch**. Downgrading on new evidence is expected; upgrading
  without re-reading the source is falsification.

## The reusable-tool corpus

A plant builds durable tools during its life (`toolcraft`, kernel §3.8) and
catalogs them in `docs/graph/tools/`. Most of a tool's value is not the one
project's wiring but the **capability and approach** — what it does, its
interface, the algorithm behind it. When that is genuinely stack-neutral,
harvest folds it into a shared corpus in the seed so the next plant starts from
a working tool or a clear blueprint instead of reinventing the wheel. This is
the tool mirror of the library corpus above; both gates apply.

- **Where it lives.** A seed-side corpus keyed by category + tool, **not by
  project**: `tool-corpus/<category>/<name>.md`. One page per tool, describing
  the tool in general. It is a cache of *reusable-tool* knowledge, never a second
  home for a plant's operations.
- **What is portable (durable).** The capability and the recurring operation it
  serves; the interface shape (invocation, inputs, outputs) in the general; the
  approach/algorithm and enduring idioms; the portable implementation **when the
  tool is genuinely stack-neutral** (a self-contained script with no third-party
  or project dependencies — like the seed's own `graph-lint.py` / `agent-lint.py`).
  Strip every plant path, credential, domain reference (agnosticism gate) **and**
  every stack-pinned specific (durability gate) before it lands.
- **What stays out (project-bound, ephemeral).** Project names, paths,
  credentials, dataset shapes, a call-site tied to one repo's layout, a
  version-locked dependency, an environment only this project has. These live in
  the *plant's* `docs/graph/tools/<name>.md` and never in the seed.
- **The withdraw contract (consumed by `grow` / `toolcraft`).** When a new plant
  needs a capability, it checks the corpus FIRST: if a matching tool exists,
  **seed the plant's `docs/graph/tools/<name>.md` from it as the orientation
  layer** — adopt the portable implementation when the stack matches, or
  re-author against the plant's own stack (test-first) when it does not. If no
  tool exists, build it fresh, and the durable, agnostic surface of that work
  becomes a harvest candidate for the next cycle.
- **Currency.** A tool page ages slowly but not never — an approach can be
  superseded. Treat it as orientation to confirm and adapt, not gospel to copy.

## The suggested-expert corpus

The roster mirror of the library and tool corpora. A plant sometimes needs a
specialist the base roster lacks and commissions one (the orchestrator's
LOW/NONE commission step). Most of that role's value is not its stack wiring
but its **mandate** — what it owns, when to select it, how it bounds against
the base roster. When that mandate is genuinely stack-neutral, harvest folds it
into a seed-side catalog so the next plant selects a ready role instead of
reinventing it. Both gates apply, plus the roster's own economy: the base team
is paid on every session of every plant, so a harvested role lands in the
**catalog** by default, never straight into the always-loaded roster.

**Promotion to the base roster is a separate, steward-only decision**, and the
bar is higher than "useful": the role's mandate must be **universal** — every
project produces the thing it addresses, not merely many of them — and no
base-roster agent may already cover it. A role that serves a domain some
projects simply do not have (a regulatory analyst, a stack specialist) stays in
the catalog however good it is, because the catalog costs nothing until
selected. Harvest may *propose* a promotion; it never performs one.

- **Where it lives.** `agent-corpus/<name>.md` — one page per suggested role,
  keyed by role, not project. A catalog of *candidate* experts, never the
  active roster.
- **What is portable (durable).** The role's mandate, its when-to-select, its
  boundary against the base roster, and its `routing_triggers` exemplars — all
  statable with zero framework names.
- **What stays out.** A stack-specific expert (a framework/language/library
  specialist), and any role that duplicates a base-roster mandate — the first
  is the plant's own, commissioned fresh; the second breaks one-home-per-fact.
- **The withdraw contract (consumed by `grow` / `graft` / commission).** When a
  project needs a role the base roster lacks, check the corpus FIRST: if a match
  exists, instantiate it into the project's `docs/graph/agents/` (the harness
  projections — `.claude/agents/` and kin — are regenerated from it) from
  `docs/graph/templates/agent.template.md`, grounded in the project's version-pinned facts
  and the role's mandate + triggers; else commission fresh, and its durable,
  agnostic mandate becomes a harvest candidate. A selected role joins the
  *project's* roster (and its kernel table), never the seed's.

## The suggested-skill corpus

The procedure mirror of the corpora above. A plant sometimes authors a
project **skill** — a repeatable procedure (a migration recipe, a release
choreography) — that is not stack-bound and would serve any project. Harvest
folds its agnostic form into a seed-side catalog so the next plant instantiates
a ready procedure instead of rediscovering the sequence.

- **Where it lives.** `skill-corpus/<name>.md` — one page per suggested
  procedure, keyed by procedure, not project. The core `skills/` stay the fixed
  shared methodology; this corpus holds *optional* procedures a project selects.
- **What is portable (durable).** The procedure's steps and the gate each one
  clears, stated by **composing** existing protocols/skills by reference —
  never a stack-bound recipe and never a restatement of a discipline the seed
  already owns (one home per procedure).
- **What stays out.** A procedure bound to one stack or repo layout (the
  plant's own), and anything duplicating a core skill.
- **The withdraw contract (consumed by `grow` / `toolcraft` / commission).**
  Check the corpus first; if a match exists, instantiate it into the project's
  `docs/graph/skills/<name>.md` (projected into `.claude/skills/<name>/SKILL.md`
  and kin by the harness) from `docs/graph/templates/skill.template.md`, grounding
  its steps in the project's real gates and tools; else author it fresh, and its
  durable form becomes a harvest candidate.

## Output format

Harvest produces **two distinct records, and they do not carry the same
content**:

1. **The ratification proposal** — stated in chat / the PR for the steward to
   review. It *may* name the plant and show every before→after generalization,
   because it is the evidence the steward weighs. It is **never committed to the
   seed.**
2. **The seed-committed record** — the CHANGELOG entry and harvest-log row that
   land *inside* the seed. Bound by the agnosticism gate exactly like any other
   seed artifact: no plant name, stack fingerprint, identifying count,
   internal-component name, path, or "from <this stack> plant" line. It records
   *that* a harvest happened and *what* generalized lesson landed — never *whose*
   plant it came from.

**Proposal — to the steward, may reference the plant, NOT committed:**

```markdown
# Harvest proposal — from <plant lineage id> — YYYY-MM-DD

## Harvested (generalized fold-backs)
- <seed file touched> — lesson: <universal statement> — generalized-from:
  <plant surface> — before→after: <what was stripped to make it agnostic>
- ...

## Rejected (stayed in the plant)
- <candidate> — reason it is not project-agnostic

## Provenance ledger
- <one row per fold-back: plant lineage, source surface, seed target, test added>

## Recommended next step
<single highest-leverage action — usually "ratify and merge" or "one more
candidate to generalize">
```

**Seed-committed harvest-log — agnostic, no plant identity — this is what
enters the CHANGELOG (and `HARVEST_LOG.md` if the seed keeps one):**

```markdown
# Harvest — from a grown plant — YYYY-MM-DD

Harvested:   <count + kind of generalized fold-backs, e.g. "3 corpus pages;
             6 doctrine/template rules"> — no plant identity.
Generalized: every plant name/domain/path/credential/host/port, every stack
             fingerprint and identifying count, and every version pin stripped.
Rejected:    <generic categories only, e.g. "internal/proprietary pages;
             kernel/agent duplicates">.

## Seed integrity gate
- Agnosticism scan: PASS (no plant name/domain/stack/fingerprint/path/count in
  the diff OR this log) / BLOCK (<hit>)
- Seed lint/tests: PASS / FAIL
- Clean dry-run install: PASS / FAIL
- Version bump: <old> → <new>; CHANGELOG + harvest-log updated
```

## Quality bar

A harvest that passes:
- Lands only lessons true for an arbitrary next project.
- Shows the before→after generalization for every fold-back.
- Carries provenance and a proof (test/lint) for every seed change.
- Leaves the agnosticism scan clean and the seed installing cleanly.
- Proposes for ratification; never silently rewrites the seed.

A harvest that fails:
- Copies a plant's name, domain, stack fingerprint, identifying count,
  internal-component name, path, data, or incident narrative into the seed —
  including into the CHANGELOG, the harvest-log, or a provenance note.
- Backports a lesson "because it was useful here" without generalizing it.
- Bolts a special-case onto a seed artifact instead of integrating it.
- Bumps the version with no CHANGELOG/harvest-log provenance.
- Mutates the seed without a human ratifying the proposal.

## What you do not do

- You do not start a harvest on your own. It is user-triggered; the most an
  agent does unprompted is *propose* one and stop. Never automatic, never a
  hook, never a tail-end step of another protocol.
- You do not merge a fold-back the user has not ratified; an unratified harvest
  is a draft. The user must be satisfied with the seed's growth first.
- You do not harvest a plant that is still churning; wait for maturity.
- You do not copy project-specific facts, names, domain terms, stack pins or
  fingerprints, identifying counts, internal-component/file/config names, paths,
  secrets, or datasets into the seed — the agnosticism gate is absolute, and it
  applies to every committed byte, the CHANGELOG and harvest-log included. Plant
  identity lives only in the ratification proposal, never in the seed.
- You do not harvest a self-healing / diagnostic case **narrative**; you
  harvest only its generalized prevention rule, recast tool-neutrally.
- You do not harvest the plant's `docs/graph/` content — that is the plant's
  life, not the seed's.
- You do not break the seed's clean install or agnosticism to land a lesson;
  if it cannot be generalized cleanly, leave it in the plant and record why.
- You do not silently mutate the seed; harvest proposes, the steward ratifies.
- You do not fold a change in without provenance and a proof.
