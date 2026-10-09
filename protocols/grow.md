---
name: grow
description: Canonical tool-neutral full-growth workflow for turning an installed project-agnostic seed into a complete source-grounded docs/graph knowledge system. Invoked by INSTALL_PROMPT.md (installed as EXPERT_SEED_INSTALL_PROMPT.md); coding-tool commands such as /initialize are convenience adapters only. Orchestrates investigation-class read-only scouts and authoring-class authors/reviewers, unifies progressive discovery, graph routing, and LLM-wiki depth, and validates the result without changing/building the application or publishing Git state.
id: protocol.grow
tier: 2
kind: protocol
origin: seed
title: grow — the canonical full-growth workflow that turns an installed seed into a source-grounded graph
owns:
  - grow.worker-topology
  - grow.write-boundaries
  - grow.knowledge-shape
  - grow.growth-flow
  - grow.completeness-contract
  - grow.gate-table
  - grow.stack-inventory
  - grow.node-authoring
  - grow.librarian-pass
  - grow.plant-facts
  - grow.legal-corpus
requires:
  - method.delegation
peers:
  - protocol.harvest
  - protocol.graft
  - protocol.initialize
  - protocol.ingest-library
  - protocol.canonize
  - protocol.deliver
  - protocol.recover
  - protocol.from-scratch
  - method.engineering-posture
  - method.design-posture
  - skill.source-index
load_when:
  - "grow the knowledge graph, first growth"
  - "install prompt, EXPERT_SEED_INSTALL_PROMPT"
  - "docs/graph is missing or badly drifted"
  - "regrow or refresh the graph after major drift"
  - "declare the plant block: environment class, commit attribution, languages"
  - "is this plant fully grown, coverage record, growth audit"
  - "does this plant carry the legal corpus, which jurisdiction, compliance scope"
  - "author the project nodes and expertise nodes, configure graph-lint kinds"
  - "which gates must pass before a growth can be called done"
  - "the growth audit reported UNGROWN, HOLLOW, UNSTAFFED, STALE — what now"
prevents: An installed seed that never becomes a graph — the method is present, the project knowledge it routes to is not, and every session reads source from scratch.
est_tokens: 13096
---

# Protocol: grow

This is the canonical workflow for a target that has source to scout.
`docs/graph/protocols/initialize.md` is the entry fork: a thin coding-tool
adapter that decides between this file and `from-scratch`, and delegates to
whichever fits. With no executable project evidence there is nothing for the
scouts to read, so the work goes to `from-scratch` (`protocol.initialize`
owns the fork and its test), which authors the project and its graph and runs
to its own `deliver`.

The caller is an orchestration chat. It owns user communication, planning,
worker selection, briefing, sequencing, and acceptance, and it ONLY
orchestrates: scouts investigate and authors write.

## Mandatory worker topology (`grow.worker-topology`)

1. Spawn clean-context **investigation-class** scouts for read-only source
   discovery. Partition by real subsystem, repository, or evidence domain. Use
   the growth-dedicated `docs/graph/templates/prompts/growth-scout-brief.md`,
   whose collection target is the evidence-ledger schema
   (`docs/graph/templates/prompts/growth-evidence-ledger.md`); demand
   paths/symbols for every claim. Each scout writes one ledger per boundary
   to the plant's gitignored seed-organ scratch,
   `.cypress/growth/<slug>.ledger.md`, outside `docs/graph/`, because a ledger
   is growth-time feedstock rather than plant knowledge.
2. Reconcile the per-boundary ledgers into a coherent evidence set in the
   orchestration plane, cross-referencing the persisted ledgers rather than
   re-holding every claim in context. Resolve each contradiction with another
   bounded scout, so every reconciled claim cites a path; do not guess.
3. Spawn clean-context **investigation-class** `research-scout`s for the
   **external evidence** the graph must be grounded in, the required
   counterpart of step 1: growth-scouts read this project's code,
   research-scouts read the upstream world it runs in, and growth needs both
   (evidence scope: Boundaries). Mine the
   reconciled ledgers' §5 for every architecturally significant,
   cross-cutting, security- or operations-critical dependency, and the
   evidence set as a whole for external standards the project is held to
   (protocols, community conventions, regulatory or ecosystem norms), and
   dispatch one research-scout each on the retrieval Phase 2 specifies.
4. Spawn **authoring-class** authors for every written artifact or deep
   synthesis. Use purpose-made agents/skills and the growth-dedicated
   `docs/graph/templates/prompts/growth-author-brief.md`, which consumes the
   ledger and maps each section to its deliverable; authors build ONLY on the
   collected, cited evidence. (It embeds
   `docs/graph/templates/prompts/node-authoring-brief.md`'s HARD
   RULES for the node-authoring case.)
5. Spawn separate **authoring-class** reviewers/validators for graph
   integrity, source fidelity, navigation, and false-premise rejection.
6. Route each finding back to a bounded authoring-class author, then
   revalidate.

Every brief states purpose, exact scope, allowed reads/writes, required graph
context, evidence supplied, constraints, output contract, and verification.
Hooks do not substitute for a self-contained worker brief.

Every spawned session executes the graph-session discipline exactly as
`docs/graph/templates/prompts/graph-session-bootstrap.md` states it. That
canonical block, embedded verbatim in every brief, owns the `--plan` before
source reads, the loaded/skipped report, the widening log, and the
bootstrap fallback. Embed it verbatim; the block owns its wording.

Route each spawn the way you route knowledge. Run
`python3 docs/graph/agent-lint.py --route "<exact delegated task>"` and cite the
ranked specialist and confidence band in the brief. Delegating workers spawn
only from their `delegates_to` allowlist and under their `max_spawn_depth` cap;
the deepest legal chain is orchestrator → multi-agent-architect → architect
→ leaf (depth 3). Leaf workers carry no `Task` tool and cannot recurse: at an
out-of-domain boundary they stop and return the handback payload
(`docs/graph/templates/prompts/handback-payload.md`) naming the next specialist. Every
worker, delegating or leaf, ends its turn with that payload carrying
`produced_by` and `route_evidence`.

Two host conditions look alike here and only one is fatal. If the host cannot
spawn clean-context workers with selectable model classes, stop and report that
this host cannot execute the seed's required operating model; do not silently
collapse delegated work into the main chat. If it can spawn them but a named
specialist is **not registered as a spawnable type** (the ordinary state of the
session that just installed the roster), that is *not* the fatal condition:
Phase 1 preflights it and applies the remedy, or the recorded role-emulation
fallback, from `docs/graph/method/delegation-bounds.md`
(`delegation.harness-registration`).

## Boundaries (`grow.write-boundaries`)

- Executable source is primary evidence: manifests, entry points, routes,
  models, migrations, configuration, deployment descriptors, tests, CI,
  prompts, and evaluations. Existing prose and centralized documentation are
  clues only; corroborate imported facts against source.
- That rule scopes to claims **about this project**. For what a dependency
  or external standard *is*, authoritative upstream documentation, fetched
  by `research-scout` during this growth, is the primary evidence, and
  internal source is the evidence of how this project *uses* it. A graph
  built from the project's own files alone has no grounding in the ecosystem
  the project runs in, so web retrieval of upstream docs is in scope for
  growth.
- Plant **knowledge** writes stay under `docs/graph/`. Outside it, growth
  writes ONLY three seed-organ places, all owned by Phase 1: the gitignored
  run scratch `.cypress/growth/` (the Phase 1 boundary plan and the evidence
  ledgers), the tracked coverage record `.cypress/coverage.json`, and the
  installer's `.cypress/seed.json` stamp. The Phase 1 placement run is an
  installer run, and it adds one more: the harness projection of each corpus
  skill page it places (`.claude/skills/<name>/SKILL.md` and its sibling in
  every other harness the stamp records), which its log names. Application
  code, manifests, CI, infrastructure and tests are target-owned and stay as
  growth found them.
  Anything else growth leaves outside `docs/graph/` is a stray, and
  `grow.gate.write-scope` looks for one by re-reading the working tree Phase
  1 recorded as the baseline.
- Growth runs ONLY knowledge checks: lint, link, route, and generated-view
  drift. Application builds and application test suites stay with the
  target.
- Record the current branch and commit as provenance ONLY. Never fetch,
  pull, switch, commit, push, or publish Git state: it is the owner's, and a
  publish cannot be undone.
- Every claim growth writes has evidence behind it; never invent behavior,
  requirements, rationale, ADRs, commands, URLs, project skills, or passing
  status. Mark an uncertain claim `unknown` and name the evidence it needs. A
  surface with no real recurring use behind it yet (a project skill, an ADR,
  a runbook's commands) sprouts later from that use, at close-out
  (`canonize` → `docs-librarian`).
- Observed implementation is descriptive architecture, not a normative spec.

## Unified knowledge shape (`grow.knowledge-shape`)

All maintained project knowledge lives under one root:

```text
docs/graph/
├── README.md, index.md, _schema.md, graph-lint.py
├── nodes/            (project facts · expertise.* · deviation.*)
├── libraries/, sources/, tools/
├── legal/            (only when externally-authored rules are in scope)
├── product/, architecture/, api/, data/, design/
├── prompts/, evaluations/
├── plans/, runbooks/
├── specs/, decisions/, best-practices/
└── changelog.md
```

Tier 1 routes; Tier 2 owns concise facts; Tier 3 provides source-backed
depth. Every useful leaf is connected from its owning node using `artifacts:`;
dependency pages use `libraries:`. A fact has one owner and links elsewhere.

## The completeness contract (`grow.completeness-contract`)

Growth is **complete or it is not done**. It establishes the plant's facts
so that no later session has to: a fact the graph states is settled
(`rule.knowledge`), and a fact growth left out is re-derived in every
session after it. A first growth that stops at a skeleton (a root node, a
router, and a handful of leaves) is a failed growth reported as a success,
and it is the single most common way this protocol is mis-run. The contract
below is binding on whatever model orchestrates growth; it does not soften
with model size, context pressure, or operator impatience. Full depth is the
default, not an upgrade.

**The rule of evidence-bounded totality.** For every knowledge collection in
the unified shape above, growth produces one of exactly two outcomes, and a
collection that is neither is an incomplete growth. "Ran out of context",
"seemed enough", "the templates are present" and "the common cases are done"
are the silent third outcome this rule exists to forbid.

- *Covered*: the collection is authored to the full depth its evidence
  supports: every real subsystem has a node; every direct dependency is
  indexed and each architecturally-significant one has a project-specific
  page grounded in retrieved upstream documentation (topology step 3);
  every observed route/message/job/entity/migration/config/AI-contract
  is homed; every leaf is connected to its owning node by an `artifacts:`
  edge; the router resolves representative tasks to small closures.
- *Absent with a named reason*: the collection is empty because the
  **source has no such evidence** (no HTTP surface, no migrations, no AI
  prompts). That absence is written in two places and both are required: the
  coverage-record row carries the reason and the paths that were searched,
  and the collection's own `index.md`/`README.md` states it in prose. The
  record is where the gate reads it; the descriptor is where a cold agent
  routed into that collection reads it. `growth-audit.py` accepts an authored
  descriptor as the home of an absence and accepts nothing else in its place.
  Any *other* authored leaf contradicts the claim, and a leaf still
  byte-identical to its template contradicts it too, so rename those under
  `grow.gate.no-scaffold` instead of leaving them sitting there. A run that
  states the absence only in the record has done the work and still fails.

**Coverage is measured as authored body.** Only authored, source-cited
content counts: what this plant wrote on top of whatever the seed's template at
that path already said, above the floor `tools/growth-audit.py` holds a leaf
to before the leaf reads as stating a fact (the tool owns the number). A
template file at its path, or a template with an edit, is not coverage,
because a byte-difference test would count one character appended to the
seed's own `design/README.md` or `legal/index.md` as covering those
collections, and every agent that has to read them with them. A leaf that
inherits its whole body from the template has been touched, not filled.

**The coverage record and the loop it serves.** Coverage is recorded, not
narrated. Before declaring growth done the orchestration chat fills
`.cypress/coverage.json` in the schema of
`docs/graph/templates/prompts/growth-coverage-record.md`, and
`tools/growth-audit.py` reads it back. The only other ledger growth keeps is
the per-boundary *evidence ledger* of Phases 1–2, which is growth-time
feedstock and never an answer about coverage. The loop the record serves:

```text
inventory  ->  plan  ->  growth  ->  lint --+
    ^                                       |
    +--------- repeat while findings --------+
```

The inventory is what the scouts found the project to be made of (Phase 2).
The plan turns each item into the artifacts growth owes it and marks which
need retrieved upstream documentation. Growth authors them. The lint checks
each planned artifact appeared and is not a scaffold. A finding names a row
still owed, so the cycle turns again: an item the scouts missed extends the
inventory, an artifact nobody owed extends the plan, an artifact that was owed
and never written sends an author back to write it.

Three of the record's four row sets are derived from somewhere other than the
run's own account of itself, so a row cannot go missing by being left out: one
per knowledge collection the installer creates, one per roster agent that
declares `plant_knowledge:` (the collections that agent must be able to read
before it can work on this project at all), and one per project-specific expert
the plant's own graph carries. The second set is what makes "all agents" a
checkable claim rather than an intention, and it is why a graft to a newer seed
surfaces the specialists it added as rows the plant does not yet answer. The
third holds this protocol to the other half of its promise: growth is supposed
to leave behind experts this project needs and the shipped roster does not
have, and an expert is only real once it is a node, cites what earned it, and
is projected where the host can spawn it.

The record is **tracked**, beside the plant's `.cypress/seed.json` stamp, not
under `.cypress/growth/`, which stays the run's gitignored scratch, and not
under `docs/graph/`, which is the plant's own knowledge. It outlives the run
that wrote it because its whole purpose is to let a later session, and the next
graft, tell a collection nobody looked at from one the project genuinely has no
evidence for. A row may not be left blank.

**No unfilled scaffold survives growth.** The installer places every leaf of
the seed's `templates/docs/**` under `docs/graph/` so each collection has
somewhere to land; a leaf still byte-identical to its template when growth
ends is a scaffold posing as knowledge, and it **shadows** the authored leaf a
cold agent needed: the router resolves to placeholders and reads them as facts.
`grow.gate.no-scaffold` is where that is proved. Where a scaffold is honestly
unfilled (its collection is absent-with-reason), the session re-runs the same
tool with `--rename`, which turns the leaf into `<name>.unfilled.md`, a marker
the installer honours so the blank never comes back, and lists every renamed
leaf in the completion report. `runbooks/verification.md` earns exemption only
by carrying at least one gate marked `executed`. Growth never `--prune`s: a
pruned leaf reappears at the next install or graft, and removal is the
steward's call, not the growth's.

**Growth ends on its exit test**, whatever the orchestrator's sense of
"enough": it ends when `.cypress/coverage.json` shows every
collection covered-to-evidence or absent-with-reason, every row of the gate
table below is green or declared by its named judge, and the maturity test at
the foot of this protocol is met against the graph, not against the file tree.
If a fatal host limit, a two-round non-converging finding (`recover`), or an
evidence gap the scouts cannot close blocks a specific collection, that
collection is delivered as an honest `unknown` with the blocker named, the one
legitimate way a collection stays uncovered, and it is reported, never silent.

## The gate table (`grow.gate-table`)

**This is the single home for every gate growth must pass.** A phase says what
it does; this says what must hold before growth closes. A gate is added here
and nowhere else: a gate written twice is maintained once and believed twice,
which is the defect this protocol tells a plant to fix in its own graph.

The honesty rule: **every row names its command, or names the judgment and
who owns it.** A gate that runs and asserts
nothing is a green lie, and a blank cell is not a third state. The judge of a
`judgment` row is named in its Command cell, because that cell is where a reader
looks for what to run. Usually it stands beside the word `none`; where the row
does have a runnable command that produces evidence without settling the
question, the judge is named after it.

`Class` uses `verify.gate-classes`. Every row here is `soft`, `detective` or
`judgment`: no harness stops a chat from declaring a growth done, so a linter
growth may decline to run, or run and override, is contract-enforced like every
other promise in this file. `<plant>` is the
plant root and `<seed>` the seed checkout; every `docs/graph/…` command runs
from the plant root.

| id | What it asserts | Command | On failure | Class |
|---|---|---|---|---|
| `grow.gate.write-scope` | growth wrote only under `docs/graph/`, `.cypress/coverage.json` and the gitignored `.cypress/growth/`, plus the installer's stamp and the harness projection of each corpus skill page the Phase 1 placement run placed, which that run's log names; no application code, manifest, CI, infrastructure or test file changed; branch and HEAD are still what Phase 1 recorded as provenance | `git -C <plant> status --porcelain --ignored -uall` and `git -C <plant> rev-parse --abbrev-ref HEAD HEAD`, each diffed against the listing Phase 1 recorded. Both flags are load-bearing and `-uall` is the one that makes this a file-level diff. Plain `--porcelain` is silent about every ignored path, the half of the tree a stray write is most likely to land in; `--ignored` on its own then names the shallowest ignored parent and nothing inside it (`!! .cypress/`), which is not an operand a stray file can be found in. With `-uall` the same command prints `!! .cypress/growth/boundaries.md`, and it un-collapses new untracked directories too, which the default reports as a bare `src/` | revert the stray write; knowledge found outside the graph is re-homed into it, never deleted and never left | detective |
| `grow.gate.graph-integrity` | every node carries its required keys, `owns` is unique, `requires` resolves and stays acyclic, every `artifacts:`/`libraries:` edge resolves, `est_tokens` is honest, and a grown plant declares its `plant:` block | `python3 docs/graph/graph-lint.py` | route to the node's owning author; never weaken the linter to make a defective graph pass | soft |
| `grow.gate.routing` | a representative task loads a small, relevant closure, and descent is as narrow as the graph claims: a task specific to one library loads the parent expertise node and that library's child and none of its siblings, and the run accounts for every child left out | `python3 docs/graph/graph-lint.py --plan "<representative task>"` prints the closure and the reason each node was left out, then a Phase 6 validator reads the two lists. `--plan` runs no check and exits 0 whatever it printed, so the command supplies the evidence and never the verdict. Judge: a Phase 6 validator, reading the closure the command prints | sharpen the child's own triggers, or lift the family word to the parent; Phase 5 owns the move | judgment |
| `grow.gate.roster-routable` | every agent this growth authored is reachable and consistent: `routing_triggers` present, delegation matching its actual tool grant | `python3 docs/graph/agent-lint.py --lint` | give the expert its own triggers, or delete it; an unroutable agent is a file, not a specialist | soft |
| `grow.gate.staffing` | every collection a roster agent declares in `plant_knowledge:` holds at least one filled leaf — all of them, not one of them — and every project-specific expert is a real node, marked the plant's own, citing what motivated it, and projected into every harness the stamp records | `python3 <seed>/tools/growth-audit.py <plant> <seed> --agents` | fill the collection that agent reads, or project the expert and re-run the installer for that adapter | soft |
| `grow.gate.status` | every status-bearing artifact carries its lifecycle status in frontmatter, in the schema's one vocabulary, rather than as body prose | `python3 docs/graph/status-register.py --root docs/graph --strict-unknown`. What the flag adds is one extra finding, not a wider scan: `missing-status`, raised when a file of kind `adr`, `spec`, `deviation` or `risk` carries frontmatter with no `status:` key. It does not make the body-restatement check read that file — a status-less file is skipped before that check with the flag exactly as without it | move the status into frontmatter and leave a pointer in the body; `<seed>/tools/status-migrate.py` does it in bulk (Phase 1) | soft |
| `grow.gate.no-scaffold` | no leaf under `docs/graph/` is still byte-identical to the seed template it was placed from | `python3 <seed>/tools/graft-audit.py <plant> <seed> --unfilled` | author the leaf, or record the honest blank — the remedy, the `runbooks/verification.md` exemption and the standing ban on `--prune` are in *No unfilled scaffold survives growth* above | soft |
| `grow.gate.coverage` | every required row of `.cypress/coverage.json` is answered and every planned artifact exists and is substantive | `python3 <seed>/tools/growth-audit.py <plant> <seed>` — exit 0 | every verdict names a row still owed: route it to a bounded author, then re-run the gate. There is no budget at which a red gate becomes acceptable | soft |
| `grow.gate.grounding` | every inventory item the plan marked `grounding.required` cites a retrieved source that resolves under `docs/graph/sources/`, and every normalized snapshot names its raw file or the recorded reason there is none | the same command; verdicts `UNGROUNDED`, `DANGLING`, `UNJUSTIFIED` | dispatch the `research-scout` that was never dispatched; a page written from model memory is what this gate exists to catch | soft |
| `grow.gate.circular-absence` | an absent `sources/` or thin `libraries/` is a fact about the project and not about the orchestrator | none — the Phase 6 validator reads the reconciled ledgers' §5 under `.cypress/growth/` and decides whether the absence is the project's or the run's. No tool reads that scratch, which is why this cannot be mechanical. Judge: a Phase 6 validator | an absence that exists because nobody was dispatched is a completeness finding, routed back exactly as a gap is | judgment |
| `grow.gate.disclosure` | every `UNKNOWN` row is named where the owner actually reads — the delivery and the plant's `changelog.md` — and a blocker that is the owner's to resolve was put to them as a numbered decision | `python3 <seed>/tools/growth-audit.py <plant> <seed>` — verdict `SILENT` | write the row, its blocker and its owner into the changelog entry and the delivery; see *Delivery and maturity* | soft |
| `grow.gate.prose` | the prose this growth authored clears the mechanical floor under the prose skills: the detectable tells, and on a refresh, that a rewrite kept its facts | `python3 docs/graph/prose-lint.py --file <artifact>` per artifact this growth authored, or `--root` over one authored collection, plus `--against <rev>` on a refresh. Scope it that way and not with `--root docs/graph`, which recurses with no exclusions into the protocols, skills, agents, method files, templates and legal corpus the installer places there — thousands of tells in machinery growth may not edit, on a plant that has grown nothing yet | fix the tell or justify it; weak tells are printed and forgiven until others share the paragraph, so the reviewer adjudicates those | soft |
| `grow.gate.agnosticism` | everything this growth authored that is *meant to travel* names no plant identifier, host address or pinned advisory | `python3 docs/graph/agnosticism-lint.py --file <artifact> --forbid <plant name> --forbid <plant path>`, over those artifacts and no others | re-author the artifact, or drop the claim that it is portable. The plant's own knowledge is out of scope and should name the project | soft |
| `grow.gate.spec-wired` | the plant's spec-coverage gate is configured against its real test layout, so the first spec this plant authors lands with a working §3.1 gate instead of a dormant one | none — the Phase 6 validator reads the edited `TEST_GLOBS` against the test layout the owner confirmed (`grow.plant-facts`) and the test paths the scouts reported, because no run of `spec-lint.py` can assert this on the plant this row describes. A plant that has authored no spec skips, or reports no live contracts to cover, and exits 0 whatever `TEST_GLOBS` holds, with or without `--warn`; the one check that would notice an empty glob is reached only once a *live* spec exists. For the validator's evidence, `python3 -c "import runpy; print(runpy.run_path('docs/graph/spec-lint.py')['test_files']())"` prints the files the globs currently resolve to — an empty list, or one missing a test directory the owner confirmed or the scouts named, is the finding, and the list is evidence and never the verdict. Judge: a Phase 6 validator | set `TEST_GLOBS` to the confirmed layout; leaving the seed's default is the dormant-gate failure this row exists for, and an unconfirmed layout stays an open owner item, never a guess | judgment |
| `grow.gate.scouts-ran` | one evidence ledger exists for every boundary Phase 1 planned to scout | `ls <plant>/.cypress/growth/*.ledger.md`, read against `<plant>/.cypress/growth/boundaries.md`, the plan Phase 1 wrote there so this comparison has a second operand a clean-context validator can open | a boundary with no ledger was never scouted: spawn it before any author builds on the gap | detective |
| `grow.gate.librarian` | the Phase 5 whole-graph librarian pass actually ran, and its merge/split/move/delete report is present in the delivery | none — the orchestration chat spawned the pass or it did not, and no tool can read a pass that did not happen. Judge: a Phase 6 validator, reading the delivery for the pass's own merge/split/move/delete report | authored collections with no whole-graph pass are a finding; run it | judgment |
| `grow.gate.composition` | the growth is minimum-sufficient and well-composed: every node, leaf and specialist serves a real routing or fact-owning need, no artifact lacks a consumer, no fact gained a second home, and each node holds one coherent responsibility | none — an authoring-class reviewer weighs the graph against `docs/graph/method/engineering-posture.md` and `docs/graph/method/design-posture.md`; `graph-lint.py` warns only on shared triggers. Judge: an authoring-class reviewer | over-growth and mis-composition route back to an author exactly as gaps do, and Phase 5 owns the moves that fix them | judgment |
| `grow.gate.links-resolve` | every relative link between graph files resolves, and every `sources/index.md` row names a normalized file that is really there | none — no linter in the plant walks links, so a Phase 6 validator follows them in the nodes and index rows it spot-audits. Judge: a Phase 6 validator | fix the link or author the missing target; a dead link in a router is where a cold agent's descent ends | judgment |
| `grow.gate.false-premise` | known-answer questions are answered from routed graph context with source citations, and an adversarial false premise is rejected rather than elaborated | none — a clean-context validator asks both kinds of question and reads what comes back. Judge: a clean-context validator | route the failing question to the node that should have owned the answer | judgment |
| `grow.gate.not-rationale` | observed implementation has not been mislabeled as a spec or as ADR rationale | none — an authoring-class reviewer reads each record against the evidence it cites. Judge: an authoring-class reviewer | move it to an architecture leaf or node; a record is formalized from evidence, never from a gap | judgment |
| `grow.gate.normative-practices` | every `best-practices/` leaf states the external standard AND where this project stands against it | none — an authoring-class reviewer reads each leaf against the source it cites. Judge: an authoring-class reviewer | author the stance, or move the description to `architecture/` where a description belongs | judgment |
| `grow.gate.executed` | every command the graph records says whether it was executed or only discovered | none — a Phase 6 validator reads the commands the graph now carries. Judge: a Phase 6 validator | label it; growth executes no application command, so `discovered, not executed` is the honest default | judgment |
| `grow.gate.harness-homes` | every agent and skill a harness directory carries has a home in the graph: no `RETIRED` entry (an `origin: seed` node, or a projection of one, the running seed does not ship) and no `ORPHAN` entry (one the plant authored straight into a harness directory, which the router and every other harness cannot see) | `<seed>/install.sh <host> --check --project-dir <plant>` once for each host in the stamp's `tools`, which writes nothing and prints one `RETIRED` or `ORPHAN` line per entry (SPEC-0001 CHECK_FLAGS_RETIRED_HARNESS_ENTRY, CHECK_FLAGS_ORPHAN_HARNESS_ENTRY), or says every harness entry has a graph home | name each entry in the delivery and the plant's `changelog.md`. An `ORPHAN` is relocated into `docs/graph/{agents,skills}/` as a node the plant owns, inside growth's write scope, and its harness copy is left for the owner; a `RETIRED` entry is put to the owner as a numbered decision. Growth deletes neither: the deletion is the owner's act | detective |
| `grow.gate.view-drift` | generated tool views still match what generates them | the read-only regenerate-and-diff command the plant's own `docs/graph/tools/` page records for that view | regenerate, or record the drift as a finding. Where the plant generates no view the row reads `none available`, never blank | soft |

### What the coverage gate reports

The verdict vocabulary has one home, `tools/growth-audit.py`, and this is
where growth quotes it. `grow.gate.coverage` fails on all of them but the last:

`MISSING`, a required row absent from the record entirely · `BLANK`, a row with
no status, so growth never reached it · `UNGROWN`, a planned artifact that does
not exist, or, for an incidental dependency whose artifact is an index line,
an index no row of which names it · `HOLLOW`, an artifact that exists and is
not one: byte-identical to the form it was authored from, still carrying a
template placeholder, under the authored-body floor, or missing the frontmatter
that makes it a node (a `${{ … }}` CI expression in a runbook authored from
real evidence is not a placeholder and is not counted as one) · `UNGROUNDED`, an
item that needed retrieved documentation and cites none that resolves ·
`DANGLING`, a covered row citing evidence paths that do not exist; cite files,
because a directory names where evidence would live rather than any evidence ·
`UNJUSTIFIED`, an absence with no reason or no searched paths, an `UNKNOWN`
with no named blocker, or a normalized source with neither a raw snapshot nor
the reason there is none · `CONTRADICTED`, a row the plant's own files disagree
with: a collection claimed covered that holds only scaffolds, or an absence
whose searched paths include a filled leaf of this graph, something to read,
found, then called absent · `UNSTAFFED`, a surface that never answered whether
it warrants an expert, claimed one without naming what a node could not have
served, or named one the plant does not carry · `SILENT`, an `UNKNOWN` the
record names and the changelog never does · `STALE`, a record answering for a
different seed than the one being audited: it names no `seed_version`, was
planned against another, or disagrees with the plant's stamp; a stamp that
records no agent projections reports here too, because without it every expert
passes the projection check by default · `UNKNOWN`, an honest named blocker,
always reported and never a failure.

Two further forms of the same command, both cheap and both worth knowing:
`--agents` answers "can every roster specialist work here?" without the full
lint (`grow.gate.staffing`), and `--json` prints the same findings
machine-readably for a validator that routes them.

### What these gates cannot see

A verdict is worth exactly what its input set is worth. These are the false
greens still open, recorded here so a green is not read for more than it
proves, and so the reviewer knows where to spend judgment.

- **The `inventory` row set is the run's own account of itself**, alone among
  the four (*The coverage record and the loop it serves*). It drives every
  planned artifact, so a project item that never reaches it is an item no gate
  can miss the absence of.
- **Nothing proves a scout read anything.** The evidence ledgers are the
  evidentiary basis of Phases 3–4, they are gitignored by mandate, and no tool
  reads them. `grow.gate.scouts-ran` proves a file was written, not that a
  bounded worker wrote it from source; a run that authored everything from
  model memory earns the same green.
- **`UNGROUNDED` proves a file exists** under `sources/`, not that anything was
  retrieved, and a stated reason is accepted in place of a raw snapshot.
- **`UNKNOWN` is uncapped.** A growth that marks `design/`, `legal/`, `api/`,
  `data/` and every dependency `UNKNOWN` exits 0 and prints coverage complete.
  `grow.gate.disclosure` forces the row to be named; it does not force work, and
  a reviewer who sees a wall of honest unknowns is looking at an ungrown plant.
- **`grown: true` is set by the same party that decided validation passed**,
  and `graph-lint.py` reads that marker to decide how strictly to judge the
  plant from then on.
- **`grow.gate.spec-wired` has no tool behind it**, which is why it is a
  `judgment` row. The resolved file list proves the globs match something, not
  that they match this project's tests, and nothing re-checks the config when
  the test layout later moves.
- **`grow.gate.status` cannot see the worst shape of the defect it names.** A
  file that states a status in body prose and carries no frontmatter block at
  all never becomes an item to lint, and the `missing-status` finding is scoped
  to four kinds, so a runbook, a plan or a project node that states a status in
  prose is outside the check either way.
- **`grow.gate.prose` and `grow.gate.agnosticism` read the files they are
  handed.** Neither discovers its own scope: a leaf outside `--root`, or a
  portable artifact nobody passed to `--file`, is not examined and reports
  nothing.
- **An ignored file that already existed can be rewritten invisibly.** `git
  status` records for an ignored path only that it is there, never what it
  says, so a growth that overwrites a file already listed `!!` leaves a listing
  byte-identical to Phase 1's. Under `-uall` a *new* file in an
  already-ignored directory appears as its own row, and no form of the command
  reads content. Only a reviewer who knows where the run was working does.

## The growth flow (`grow.growth-flow`)

Six phases follow, and their order is the contract: a phase opens on the
evidence the one before it produced, which is why authoring before scouting
and validating before the librarian pass both produce work that has to be
redone. `delegation.sequencing` is the general rule; this is its instance for
growth, and each phase heading below is the sole home of what that phase
spawns. `initialize`, and a regrow after drift, enter at Phase 1 like any
other growth.

## Phase 1 — Detect and plan

Determine whether the target is empty/new, one repository, a workspace or
monorepo, or an umbrella containing sibling repositories. Stay inside the
user-placed scope. Record each repository's path, current branch, HEAD, role,
manifests, and stack without mutating Git, and record the worktree state as
kept `git status --porcelain --ignored -uall` output: that listing is the
baseline `grow.gate.write-scope` diffs against at close, it is taken with the
flags that row states and no others, and a gate with one operand proves
nothing.

Ensure the plant gitignores `.cypress/growth/` before scouting. Ignore that
directory, not `.cypress/`: the two files beside it stay tracked, the
`.cypress/seed.json` stamp and the coverage record `.cypress/coverage.json`,
for the reason *The coverage record and the loop it serves* gives above.

**Ask the owner for the plant facts, once (`grow.plant-facts`).**
`docs/graph/index.md` carries a `plant:` block (`docs/graph/_schema.md`
§"The `plant:` block") holding the facts only the owner can assert and
agents otherwise re-ask or guess: `environment_class`, `commit_attribution`,
`deliverable_language`, `comment_language`. Propose each value from evidence
(deployment descriptors and CI targets for the environment class, trailers
in the recent commit log for attribution, and the wording of existing
comments, docs and UI strings for the two language fields), and record the
evidence used beside each proposal (the scout that gathered it cites paths
like any other claim). Put the four to the owner as one numbered ask
(`deliver.numbered-decisions`) and write the confirmed values into the
frontmatter block. An unanswered value stays a `status: open` item, owner
named, in the coverage record and in the delivery, and `graph-lint.py` fails
a grown plant until the block is declared. Ask once; later sessions read the
block. In the same ask, request the plant's model map in
`docs/graph/models.md` (`delegation.model-map`, ADR-0022): the providers, and a model for each class
and effort on each host the plant runs.

**The plant's test layout is an owner fact too, asked in the same ask.**
`TEST_GLOBS` in `docs/graph/spec-lint.py` decides which files the spec-coverage
gate counts as tests, and the seed's default reads only the conventional unit
layouts: `tests/`, `test/`, `spec/`, and the `*_test`, `*.test` and `test_*`
file names. A plant whose tests are black-box checks in a directory of another
name (end-to-end suites, shell checks, smoke or contract runs against a live
service) matches none of them, and the first live spec it authors reports
that the globs matched zero files, or, once a stray file matches, credits
coverage to the wrong set. Which directories hold this plant's tests, and which
of them hold tests and which hold fixtures or tooling, is a fact the owner asserts
and a scout can only propose. Propose the layout from evidence: the test
directories, the runners the build and CI invoke, and the paths those runners
read, each cited. Put it to the owner as one more numbered item beside the
four plant facts, with the globs that would read it, and name every directory
the proposal leaves out and why. When the Phase 2 scouts report a test path the
proposal missed, put the difference to the owner before Phase 6 writes the
globs. Never widen the seed's default to cover a layout nobody confirmed: a
default that counts non-tests is false coverage on every other plant. An
unanswered layout stays a `status: open` item, owner named, in the coverage
record and the delivery, and Phase 6 leaves the default in place and says so,
so `grow.gate.spec-wired` reports it open, not wired.

**Ask the owner about the legal corpus, once, before authoring
(`grow.legal-corpus`).** `agent.legal` runs without web access: the corpus the
installer places plus this plant's own legal leaf is the only law it can reach,
and its charter turns a gap into a refusal rather than a reconstructed
citation. A plant with no corpus therefore has an analyst that can only refuse,
and one whose corpus was filtered has an analyst that cannot tell a page nobody
copied from an instrument that does not exist, which is the refusal rule
inverted into a silent false negative. So the question is binary and it is the
owner's: `--legal-corpus yes` places every page under
`docs/graph/legal/corpus/`, `no` records that this plant carries none.

**And ask which national law, in the same breath (`--legal-jurisdiction <cc>`).**
The corpus's EU and international layers are jurisdiction-neutral and travel
with it whole. Its **national** layer is only as wide as what has been
ingested, and the installer derives that list from `legal-corpus/national/`.
Naming a code the corpus does not carry records an **ingest request**, closed
by a `research-scout` pass under the corpus's own entry contract, and until it
lands `agent.legal` refuses on that jurisdiction, correctly. Cite ONLY the
named jurisdiction's own ingested instruments: a neighbouring country's
statute must never stand in for the missing one, and an EU directive is never
cited for a national obligation it only binds Member States to transpose
(`legal-corpus/_schema.md` §"Four instrument kinds").

Put both as numbered decisions (`deliver.numbered-decisions`) alongside the four
plant facts, before Phase 4 authors anything. Unanswered, it stays a `status: open`
item with the owner named, exactly as an unset plant fact does, and
`.cypress/seed.json` records `"legal_corpus"` / `"legal_jurisdiction"` as
`"undecided"`. The owner decides it; a run never decides it by inspection.
Relevance is expressed afterwards, in `legal/index.md`, and revised as the
project evolves.

**Propose the corpus pages this plant can withdraw, put the list to the owner,
and place what the owner confirms before anyone authors.** The seed carries
version-durable pages for libraries (`library-corpus/`), stack-keyed
procedures (`skill-corpus/`) and portable tools (`tool-corpus/`), and the
installer places the ones the owner lists. A page placed here is one
`research-scout` this growth does not spawn for that library's surface
(`ingest-library.corpus-first`), so the proposal is made now, from the
manifests, and not after Phase 2 has already paid for the retrieval. Run, from
the plant root:

```sh
<seed>/install.sh <host> --expertise propose --project-dir <plant>
```

It writes nothing (SPEC-0001 EXPERTISE_PROPOSAL_WRITES_NOTHING). It reads the
project's own manifests through `<seed>/tools/corpus-match.py`, the matcher
that stays in the seed: the Maven POM's dependencies and plugins,
`package.json`, Python requirements and `pyproject.toml`, `.csproj` package
references, `pubspec.yaml`, every `image:` of a compose file and every stage's
`FROM` in a `Dockerfile` or `Containerfile`, `dotnet-tools.json`,
`azure-pipelines*.yml` and Ansible's `requirements.yml`. It skips dependency
stores, build output, virtual environments, version control, `docs/graph/`,
scratch and backup copies, the agent hosts' own directories, a nested plant
and a symlinked directory, so no evidence line names a copy. It prints one
line per page, sorted by id: the corpus id, then the manifest path and the
entry that matched, or, for a skill or tool page, `stack:` and the library page
its `stack:` field matched through. One entry can propose several pages: a
Maven starter proposes its module's own page and its family's umbrella page
together. A project that matches nothing gets one line saying so; a manifest
that does not parse is named on a line of its own and the proposal is made
from the rest. SPEC-0001 §6, "Selective placement", holds the exact
normalization per ecosystem.

The matcher reads names, not judgment, so the session filters its list before
the owner sees it, and says why beside each id it advises leaving out:

- an upgrade page (one that carries its subject across a major line,
  `library-corpus/README.md`, "A major line is not a pin") is advised only
  while the version the manifest declares is older than the line the page
  upgrades to, the same rule Phase 4 gives for withdrawing it;
- an entry the manifest declares only for a test or build step stays on the
  list, marked as such, because the owner decides whether the plant needs its
  page;
- a page no manifest can name (a command-line client a script calls, a cloud
  CLI, a host-hardening page) is never proposed; when the session sees the
  plant use one, it adds that id to the list with the path that shows the use.

Put the list to the owner as one more numbered decision in the same ask as the
plant facts and the legal corpus (`deliver.numbered-decisions`): each id with
its evidence line, the ids advised out with their reason, and the instruction
that the owner may strike any id or add one the matcher missed. On the owner's
answer, place the confirmed list, naming every host the stamp records so that
each harness projects a placed skill page:

```sh
<seed>/install.sh $(jq -r '.tools' <plant>/.cypress/seed.json) \
  --expertise <id>,<id>,... --project-dir <plant>
```

The installer places a library page at `docs/graph/libraries/<name>.md` and a
tool page at `docs/graph/tools/<name>.md`, each under its provenance line
(`<!-- origin: corpus@<seed version> id: <corpus id> -->`), and a skill page as
the top-level node `docs/graph/skills/<name>.md` with `origin: corpus@<seed
version>` in its frontmatter, projected by the harness's existing skill
projection. It records each page in `.cypress/seed.json` under `expertise`
with the SHA-256 of the bytes it wrote, so every later install refreshes the
pages nobody edited and graft merges the ones the plant did (SPEC-0001
EXPERTISE_PLACES_ONLY_THE_CONFIRMED_LIST, EXPERTISE_IS_RECORDED_IN_THE_STAMP).
Read the run's log for three things before going on:

- **A refusal writes nothing.** The preflight refuses, by id and before the
  first write, an id that names no page, two ids that place at one destination
  (a `pypi` client and a `container` image of one name, for example), and an id
  whose destination is a seed skill node or a scaffold leaf. Put the conflict
  back to the owner, who keeps one id; Phase 4 folds what the other page knows
  into it by hand.
- **A destination the plant already has is left and named.** A page an
  earlier attempt or a person wrote at that path is the plant's own: the
  installer neither replaces it nor records the id (SPEC-0001
  PLANT_OWNED_PAGE_IS_NEVER_REPLACED). Phase 4's author folds the corpus page
  into it, one home per dependency, and the delivery names it.
- **Each placed page is named with its path.** Copy that list into the
  orchestration plan: Phase 2's dispatch reads it.

An unanswered list stays a `status: open` item with the owner named, exactly
as an unset plant fact does. Nothing is placed, and Phase 2 dispatches its
research-scouts as it would for a plant with no corpus. A list answered after
Phase 2 began is placed then, and a scout already spawned for a library the
answer placed is left to finish: its sources are registered, and Phase 4's
author merges what it retrieved into the placed page instead of writing a
second page. Growth never runs the placement without the owner's answer and
never widens the list by inspection.

**An existing graph that carries lifecycle status as body prose** (a
refresh, or an adopted plant), in a vocabulary per kind: run
`python3 <seed>/tools/status-migrate.py --root docs/graph` (dry run) and
show the owner its table; on the owner's go, re-run with `--write`. The tool
moves each status into frontmatter in the schema's one vocabulary and turns
the body line into a pointer; what it cannot map (a threat model's `active`,
a superseded record with no named successor) it reports for the owner to
decide, never invents.

Settle spawnability here, before Phase 2. A session that just installed the
seed holds an agent registry from before the install, and a session rooted at
the seed rather than the plant never holds the plant's roster at all, so
preflight one roster type now and take the remedy or the recorded fallback
(`docs/graph/method/delegation-bounds.md`, `delegation.harness-registration`). Scouting
is the wrong place to learn that no scout can be spawned.

Inventory cheaply before opening large files. Before the scouts are
briefed, the session runs `python3 docs/graph/source-index.py build --json`
once; the `inventory` it prints (each file's path, language, and test class,
across the governed repositories) is the scouts' mechanical file list, so no
scout walks the tree to find its files. Nothing runs it per prompt or per
file access (ADR-0018). Ignore generated, vendor, cache, and build
directories. Identify real subsystem boundaries and divide
read-only scouting across them. Also assign focused scouts for cross-cutting
evidence: APIs/messages, data/migrations, platform/config,
tests/CI/operations, dependencies, prompts/evaluations, the interface and
design surface, the project's regulatory exposure, the external
standards its stack and domain are held to, and any agent-operations
system the project already runs (agent charters, harness hooks,
instruction files, lesson or memory logs). That last boundary is evidence,
not stale prose to wave off as a bulk read: Phase 4 says what each of its
parts yields.

Write that division down, one line per boundary carrying the `<slug>` its
ledger will use, in `.cypress/growth/boundaries.md`. The plan has to outlive
the orchestration context: Phase 6 dispatches clean-context validators, and
`grow.gate.scouts-ran` asks them to compare the ledgers on disk against the
boundaries planned, which nobody can do from a list that was only ever held in
a chat. A boundary added mid-run is appended there when it is added. The
orchestration chat writes the file; a scout's charter grants it one write, its
ledger. The installer places no `boundaries.md`, so a validator that finds none
has found a run that skipped this step.

This list is the intake, and a domain missing from it is a collection no plant
ever grows. It is derived from the roster, not from habit: every agent that
declares `plant_knowledge:` needs some collection filled before it can work on
this project at all, and a scout must be assigned to gather the evidence that
fills it. When the seed adds a specialist, this list gains its evidence domain
in the same change, because a plant grown without it carries that specialist
with nothing to read: a `ui-ux-designer` with no design material, a `legal`
analyst with no corpus.

## Phase 2 — Scout and establish evidence

Spawn the planned investigation-class scouts on
`docs/graph/templates/prompts/growth-scout-brief.md`. Each writes one ledger to
`.cypress/growth/<slug>.ledger.md` in the schema of
`docs/graph/templates/prompts/growth-evidence-ledger.md`, every section keyed
to a downstream growth deliverable, so nothing an author later needs is left
ungathered. Each reports terse factual claims with exact paths and symbols for:

- bootstrap, entry points, packages/services, imports, and responsibilities;
- inbound routes/messages/jobs and outbound integrations;
- entities, schemas, migrations, persistence, and data movement;
- configuration, secrets interfaces, deployment, and observability;
- tests, CI gates, scripts, operational commands, prompts, and evaluations;
- direct dependencies, lock constraints, and evidence of actual use;
- the interface surface: screens, components, design tokens, interaction
  states, and the accessibility affordances the source shows;
- regulatory exposure: personal or regulated data, the jurisdictions and
  sectors the deployment descriptors imply, and any compliance artifact
  already in the tree;
- an agent-operations system already in the tree: each charter, each hook
  with the event it fires on and what it blocks, each instruction file,
  and each lesson or memory log entry with its date and the paths it names;
- discrepancies between executable source and existing prose.

The persisted per-boundary ledgers are the evidence set: claim area, strong
source, corroborating source, confidence, and gaps, each keyed to the
deliverable it feeds. Reconcile across them, resolve contradictions by scoped
follow-up scouting, and record which ledger owns each contested fact. A
claim's weight comes from its strongest source; repetition across a
centralized docs repository adds none.

**Then reconcile the ledgers into the stack inventory (`grow.stack-inventory`).**
Every item the project is made of gets one row: each language and its version,
each runtime and framework, each direct dependency with its significance, the
infrastructure it runs on, its data stores, the external and AI services it
calls, each design surface, and each regulatory exposure, every row anchored
to the source path that proves it. Write it into the `inventory` array of
`.cypress/coverage.json` and run
`python3 <seed>/tools/growth-audit.py <plant> <seed> --plan`, which turns each
row into the artifacts growth now owes it and marks which rows require
grounding in retrieved upstream documentation. Re-run `--plan` whenever the
seed at `<seed>` moves: a record planned against one seed and audited against
another is `STALE`, and the collections and agents the newer seed added never
become rows anyone has to answer. The inventory is what growth is held to, and
it is the one row set the run writes about itself; see *What these gates
cannot see*.

**Then establish the external evidence (topology step 3) before authoring
begins.** Every inventory row the plan marks `grounding.required` needs
upstream documentation retrieved from the open web during this run: languages,
runtimes and frameworks (their current guidance and the practices they name as
wrong, not only their API surface), significant dependencies, infrastructure
components, data stores, external and AI services, the design standards the
interface is held to, and the instruments behind each regulatory exposure. A
page written from model memory is the failure this step exists to prevent:
memory is unversioned, undated, and uncitable. A library whose page Phase 1
placed from the corpus gets no surface scout: its version-specific delta is
pinned against the lockfile, and the deltas of every placed page go to one
bounded `research-scout` brief scoped to pins, deprecations and advisories
(`ingest-library.corpus-first`), whose sources are registered like any other.
For every other item, dispatch one bounded `research-scout`
per item (batched sensibly) following `docs/graph/protocols/ingest-library.md`:
retrieve authoritative upstream documentation pinned to the versions the tree
actually locks, snapshot raw sources to `docs/graph/sources/raw/`, normalize
to `docs/graph/sources/normalized/`, and register each in
`docs/graph/sources/index.md`. A normalized snapshot names its raw file, or
the reason none was kept, in the `raw:` line of its metadata block; the
coverage gate holds `sources/` to it (`UNJUSTIFIED`), because "when the
license permits" recorded nowhere is an out every scout takes. These
investigation-class writes are mechanical
normalization, not authoring (`agent.research-scout` owns that distinction).
Record the dispatch list in the orchestration plan: Phase 4's `libraries/`
rich pages, normative `best-practices/`, and `sources/` provenance are
authored from this material, and the coverage record audits against this
list. If the host truly has no web retrieval, that is a named blocker, and the
affected collections ship as honest `unknown`, never as a silent thin index.

## Phase 3 — Model and author through authoring-class workers

**Configure the linter to this project before anyone authors against it**
(`grow.node-authoring`). `docs/graph/graph-lint.py` opens with a project-config
block, and every later gate reads the graph through it: `ROOT_ID`, the id of
the single root node; `KINDS`, the node kinds this project actually uses; and
`KIND_PREFIX`, the optional map from a kind to a shorter id prefix, for a
verbose kind that should live in a terse id namespace. A kind absent from that
map keeps the identity rule (its ids must start with `<kind>.`), so an empty
map is the correct default and lints exactly as no map at all.

`KINDS` is extended freely and narrowed only within its floor. `root`,
`expertise` and `deviation` are the graph's own fixtures: the root node the
reachability check demands, the routing nodes this phase authors, and the
standing-departure nodes `canonize` records. `protocol`, `skill`, `agent` and
`method` are reserved by `docs/graph/_schema.md` for the machinery the
installer already placed under `docs/graph/`. Keep all seven in `KINDS`: every
node of a dropped kind fails with `kind not in KINDS`, and the graph cannot be
read at all. Six of the seven fail at once, since a node of that kind is on
disk the moment growth ends. `deviation` is the exception and is still a
floor: a fresh plant carries no standing departure, so dropping that kind
lints clean the day it is dropped and fails the first time `canonize` records
one, the worse of the two failures, because by then nobody connects it to
this edit. What a project
genuinely drops is the project-fact vocabulary it has no use for
(`subsystem`, `stack`, `platform`, `data`, `crosscut`, `domain`), and what it
adds is a kind its own facts need.

Brief authoring-class authors on
`docs/graph/templates/prompts/growth-author-brief.md`: point each at the
evidence ledgers it reads (`.cypress/growth/*.ledger.md`), the exact output
paths, schema, relevant existing nodes, and exclusive write scopes. Authors
build from the ledger's cited claims: a fact the ledger marks `not recorded`
stays unrecorded, a section marked `none found` is omitted, never invented.
Author:

- one root node for the governed project/program;
- one node per real subsystem or bounded capability;
- shared stack, platform, data, domain, and cross-cutting nodes where they
  remove duplication or materially improve routing;
- one `nodes/expertise.<slug>.md` per core or significant language, runtime,
  framework, dependency, infrastructure component, and datastore the stack
  inventory carries; the coverage plan derives exactly which, and an item the
  scouts marked incidental owes none;
- a compact Tier-1 task-to-entry router using realistic developer phrases.

Each node has unique `owns`, minimal acyclic `requires`, explicit boundary
`peers`, concrete `load_when` phrases/paths, honest token cost, source paths,
and leaf edges, against the contract `docs/graph/_schema.md` states in full.

**An expertise node ONLY routes.** It owns exactly
`<slug>.applicability` and `<slug>.composition`: when that element is in play
for a task, what goes wrong without it, and which sub-expertises apply
under which condition. Versions and API surface live in Phase 4's
`libraries/` and `best-practices/`, and the node reaches them with
`libraries:` and `artifacts:` edges instead of repeating either. A node with neither
edge routes to nothing and fails `grow.gate.graph-integrity`.

Composition is wired downward with `composes:` on the parent and upward with
`requires:` on the child, so the router descends only into the children a task
names specifically: a composed child loads when the task uses a term from the
child's **own** vocabulary, which is why a family word carried on a child
descends nobody and belongs on the parent. Where the inventory carries one slug
at two majors, the unversioned node composes one version-qualified child per
major (`expertise.dotnet-8`) whose triggers are that major's target tokens
(the only place a version enters a slug), and a child the plant has stopped
running is marked `superseded` rather than deleted. `grow.gate.routing` is
where a misplaced family word surfaces, and Phase 5 is where it is moved.

## Phase 4 — Grow source-backed leaves

Through bounded authoring-class authors, populate every collection supported by evidence:

- `product/`: actors, capabilities, flows, constraints, observed behavior;
- `architecture/`: context, components, boundaries, runtime flows,
  integrations, and dated sharp edges;
- `api/`: observed HTTP/RPC/event/job contracts and source locations;
- `data/`: entities, ownership, persistence, migrations, lineage, privacy;
- `libraries/`, with `best-practices/` below and the `nodes/expertise.*`
  nodes Phase 3 authored, is one of three artifacts built from one body of
  evidence (the ledgers' §5, §9 and §14 and the upstream sources the
  research-scouts retrieved in Phase 2), each owning a different question and
  restating neither of the others. `libraries/` is the **fact and pin home**:
  every direct dependency indexed, and a rich project-specific page for every
  architecturally significant, cross-cutting, security, or operational
  dependency, grounded in that retrieved documentation per
  `docs/graph/protocols/ingest-library.md`. A thin index table where the
  ledgers' §5 flags significant dependencies is not coverage. A page Phase 1
  placed from the corpus is that dependency's page: the author adds this
  project's role, used surface and sharp edges to it, under its provenance
  line, and never writes a second page beside it. The edit makes the page the
  plant's in the installer's eyes, so later installs leave it and graft
  merges the corpus's newer layer into it. The exact
  major(s) this plant runs are recorded there ONLY. Growth runs no
  application code, so `ingest-library`'s smoke-test validation is recorded
  on each page and in `plans/grill.md` as a pending backfill;
- `legal/`: the corpus itself is placed by the installer, **whole or not at
  all**, on the owner's `grow.legal-corpus` answer, never assembled here and
  never subsetted (`legal-corpus/_schema.md` §"Whole corpus, or none").
  What this phase authors is `legal/index.md`, the **scope instruction**:
  which instruments bear on this project today, which do not and why, and what
  the corpus does not carry at all. That is a determination, it is revised as
  the project evolves, and it is the only legitimate way to narrow what
  `agent.legal` considers; deleting a page is not. Each in-scope instrument's
  `verified` and `legal_status` are **re-confirmed against the publisher**
  before anything is relied on; a citation that shipped once is not thereby
  current. The corpus supplies the citation; the project's own application of a
  rule is authored in the node that makes the claim, cites the entry id, and is
  never folded back (see `docs/graph/protocols/harvest.md`);
- `sources/`: provenance rows for every upstream source the research-scouts
  retrieved during this growth (raw snapshot, normalized copy, index row).
  Growth creates its own external consumption via topology step 3, so this
  collection may be absent only where the reconciled ledgers genuinely flag no
  significant dependency and no external standard: a rare project, and the
  ledger rows proving it must be cited. `grow.gate.circular-absence` is where
  the other kind of absence is caught;
- `design/`: one leaf per interface surface the source shows (screens and
  flows, interaction states, the component system and its design tokens,
  visual hierarchy, and how the accessibility floor is met), authored by
  `ui-ux-designer` from the ledger's interface-surface evidence and grounded
  in the retrieved design standards (`tokens.md` carries the token and
  component reference). A plant with a user interface and an empty `design/`
  is an ungrown collection, not a project without design;
- `tools/`: a page per durable tool the plant actually runs, seeded from
  `tool-corpus/` where the stack matches and otherwise authored from the
  operational evidence (`toolcraft` owns the doctrine; this is its catalog);
- `prompts/` and `evaluations/`: AI contracts, call sites, datasets, rubrics,
  gates, and failure modes;
- `runbooks/verification.md`: exact commands and prerequisites, explicitly
  labeled `discovered, not executed` during growth;
- `runbooks/release.md` and `runbooks/rollback.md`: filled from the deploy
  or release procedure the source already carries (a deploy script, a
  pipeline's release stage, a project skill), each command cited and
  labeled `discovered, not executed`. A procedure the plant already runs is
  evidence, so these do not wait for use the way an unrun runbook does;
  with no such procedure in the source, they are renamed under
  `grow.gate.no-scaffold` like any other unfilled leaf;
- `plans/grill.md`: inspected evidence, gaps, drift/backfill work, and the
  smallest useful next increment;
- `best-practices/`: the **standard home** of the trio above, and
  **normative, not descriptive**. The community and upstream standards the
  project's stack and domain are held to are cited from the same retrieved
  sources, and the project's observed stance against each (conforms /
  deviates / unknown) carries source paths. The stance is what the matching
  expertise node routes a worker here for, and it is what
  `grow.gate.normative-practices` reads the leaf for;
- `changelog.md`: artifacts/revisions covered by the growth pass.

Prepare indexes for `specs/` and `decisions/`. Formalize a spec ONLY from a
ledger §7 spec-worthy behavior with a real observable, and an ADR ONLY from a
ledger §8 decision the source actually shows (no invented rationale:
Boundaries). If genuine intent records
exist, preserve them with provenance. Put observed implementation choices in
architecture leaves or nodes.

**Staff the project, and record the decision either way.** A plant also
carries the expertise its knowledge serves. The expertise nodes
Phase 3 authored are the default answer to "who knows this here": the router
composes one into any worker whose task names it and costs a worker whose task
does not name it nothing. An **agent** is warranted only for what a node cannot
serve (work that needs different `tools`, a different `model` class, an
adversarial `stance`, or context `isolation`), and every
inventory item of kind `domain` or marked `significance: core` closes its
`expert` decision in the coverage record with `warranted`, a `why`, and, when
true, the `needs` it names. A decision nobody recorded reads exactly like a §9
nobody opened. Where an agent is warranted, check the seed's
`agent-corpus/<name>.md` first, author from `docs/graph/templates/agent.template.md` and the cited
evidence, mark it `origin: project`, declare its `plant_knowledge:`
(collections or the expertise nodes it draws on), cite what motivated it, and
project it to every path this plant's `.cypress/seed.json` records;
unprojected it is on disk and unspawnable
(`delegation.harness-registration`), and on most harnesses spawnable only in
the next session; say so in the delivery.

Apply the same withdraw-on-evidence discipline to the reusable-tool and
suggested-skill corpora, so harvested tooling and procedures reach a new plant
at growth time and not only via a later graft. Anything the plant authors that
is *meant to travel* (a tool or skill it may later offer back, a component it
declares project-agnostic) runs `docs/graph/agnosticism-lint.py` over it
before it is called done, under `grow.gate.agnosticism`. That is the same
floor harvest will apply, applied early enough to be cheap. Everything else the
growth authors is the plant's own knowledge and names the project (the gate
row). `grow.gate.prose` runs the other way round,
over every leaf a person reads whether it travels or not, which is why the
installer places `prose-lint.py` in every plant. Run it per collection as each
author finishes rather than as one sweep at Phase 6 over a graph nobody has
re-read.

Where the plant's real stack matches a portable tool the corpus carries
(`tool-corpus/<category>/<name>.md`), a self-contained capability the source
genuinely needs, seed `docs/graph/tools/<name>.md` from it as the orientation
layer (adopt the
portable implementation when the stack matches; re-author test-first when it
does not). A page placed before the plant has built the tool says
`blueprint only, not built here` where its run and test commands would
stand, never the corpus's unfilled `<…>` slot, which reads to a later agent
as a command nobody wrote down. The close-out that later catalogs the plant's build
re-points the page (`protocol.canonize`). Where a repeatable procedure the
source actually performs matches a
generic `skill-corpus/<name>.md` entry or a stack-keyed
`skill-corpus/<key>/<name>.md` entry (`skill-corpus/README.md`, "Stack-keyed
pages"), seed `docs/graph/skills/<name>.md` from it (projected into the harness
by the plant itself). The key directory is the corpus's filing and never part
of the placed name. A stack-keyed page is withdrawn only on a stack match: the
plant's build files, or the stack inventory reconciled in Phase 2
(`grow.stack-inventory`), declare a library the page's `stack:` field names.
A key directory alone is not a match, and neither is a library the source
mentions without declaring it. An upgrade page, one that carries its subject
across a major line (`library-corpus/README.md`, "A major line is not a pin"),
is withdrawn only while the plant's declared line is older than the line the
page upgrades to: a plant already on the target line, or past it, has no
upgrade to run, and placing the page would hand its sessions a procedure that
does not apply. Record beside the withdrawn page which inventory row matched
and the path that proves it, as for any other claim. A tool or skill page the
owner confirmed in Phase 1 is already on disk, placed by the installer: this
rule is the one its proposal was filtered by, and the matching row and its
path are recorded for it all the same. A page withdrawn here that Phase 1 did
not place goes back to the owner as a numbered decision and is placed through
the installer, never copied by hand, so the record holds it and later
installs refresh it. Both are candidates: a tool
or skill whose need has not arisen in the source is left for `toolcraft`/`canonize` to sprout from real recurring
use, and the absence is recorded ("no corpus tool/skill warranted") instead of
padded.

**An agent-operations system the project already runs** is not a legacy
documentation source to exclude wholesale, because its parts are three
kinds of evidence. A **lesson or memory log** is dated incident evidence:
each entry is mined for a sharp edge (into the node that owns its topic)
or a spec candidate (into `plans/grill.md`), and an owner rule found there
is placed as `canonize.session-record` places one. A placed edge cites its
dated entry and is marked unverified until source corroborates it, because
a log is prose like any other and may describe a host or version the
project has since left. A **hook** is
enforcement the project already relies on: the graph records what it fires
on and what it blocks, and it stays wired; re-homing or retiring it is the
owner's call, and dropping it silently removes a guard nobody will notice
is gone. A **table of facts copied into a charter** is drift by
construction: each fact is homed in its owning node, and the plan names the
copy stale, pointing at that node. The charters and logs themselves stay as
growth found them.

For an existing graph, refresh current fact owners rather than duplicating
them, preserve valid hand-authored knowledge, cite contrary evidence for
stale claims, and record unresolved conflicts. Source the scouts could not
access is recorded `unknown` with its blocker.

## Phase 5 — Connect and fertilize (the librarian rebalance pass)

This phase always runs, as a named dispatch (`grow.librarian-pass`): one
authoring-class `docs-librarian` pass over the whole authored graph, after
Phase 4 and before validation, however well the authors linked things,
because authors work in exclusive scopes and only a whole-graph pass can see
the seams between them. The librarian:

- ensures every leaf has an owning-node `artifacts:` edge and every node is
  reachable from the router;
- **rebalances**: merges near-duplicate homes (one home per fact), splits
  nodes that accreted unrelated facts, moves depth behind edges out of the
  always-loaded router and oversized nodes, deletes pass-through nodes that
  only forward, and works `graph-lint.py`'s shared-trigger warnings, each of
  which names its own move: lift a family term to the parent, or replace a
  term too widely carried to identify this child with the child's own words;
- verifies searchable paths/symbols/commands sit in the right home and
  unknowns are answerable questions with likely evidence locations;
- keeps the router compact and re-runs `graph-lint.py` after rebalancing.

"No rebalance needed" is a legitimate result, and only when the pass actually
ran and says so; `grow.gate.librarian` is where the report it owes the delivery
is checked for.

## Phase 6 — Independent validation

Dispatch separate authoring-class reviewers and clean-context validators. Their work is
the gate table: every row, in order, reported with its command and its result,
including the `judgment` rows, where the result is the named judge's finding
and the evidence they read. A row reported without a command and a result is a
row that did not run. They run knowledge checks only, within the Boundaries
above.

Two things the table cannot do for them. **Spot-audit a sample of the cited
paths by hand**, because a linter proves a file exists and says something, never
that what it says is true, and **read *What these gates cannot see* before
believing a green**, because the rows that pass most easily are the ones whose
input set the run itself supplied.

Route findings to bounded authoring-class authors and repeat independent
validation, **bounded by the recover discipline**
(`docs/graph/protocols/recover.md`): the authoring pass and two author-fix →
revalidate rounds are the three attempts `protocol.recover` allows. Stop there,
record a finding that survives them as an honest unknown or a defect in the
delivery, and hand the decision to the user. The linter stays as written
(`grow.gate.graph-integrity`).

When validation passes, set `grown: true` in the frontmatter of
`docs/graph/index.md`: the marker `graph-lint.py` reads to hold this plant
to the grown standard (a missing `plant:` block fails, not warns, from here
on). Set it only then; a plant stamped grown while half-grown lies to every
later lint. In the same edit, remove the pre-growth block: the lines from
`<!-- pre-growth: grow removes this block -->` through `<!-- /pre-growth -->`.
A grown plant has no reader for it.

Configure the spec-coverage gate while the stack evidence is fresh: set
`TEST_GLOBS` in `docs/graph/spec-lint.py` to the project's real test layout,
as the owner confirmed it in the plant-facts ask (`grow.plant-facts`), never
as a scout or the seed's default guessed it. `grow.gate.spec-wired` is where a
validator reads that edit.

## Delivery and maturity

Before reporting, close the growth session itself through
`docs/graph/protocols/canonize.md` (§3.7): its single librarian close-out
spawn records what the growth learned (sharp edges met, contradictions
resolved, tools discovered), so the plant's first working session inherits
it. Growth that ends without canonize leaks its own lessons. The growth session
keeps its own session record in `docs/graph/plans/sessions/` from Phase 1,
listing any memories the host already holds for this project so that close-out
can file them (`stewardship-posture.session-record`).

The orchestration chat reports target boundary/revisions, worker assignments,
evidence inspected, artifacts created/refreshed, the Phase 5 librarian
rebalance report, the gate table with each row's command and result,
untrusted/excluded docs, honest unknowns, and one next action **with its
tier** (kernel §0), so the next session starts classified instead of cold.

The owner reads the delivery and the changelog, not the coverage record, and a
blocker filed only in the record as "the owner's determination" is put to
nobody (`grow.gate.disclosure`). So the `changelog.md` entry for the
pass carries each `UNKNOWN` row, what it waits on, and who, and the blockers
that are the owner's to resolve go to them as numbered decisions
(`deliver.numbered-decisions`), the same ask the plant facts use.

Include the **coverage record** (`grow.completeness-contract`): every
collection marked covered-to-evidence or absent-with-reason, the scaffolds
renamed `.unfilled.md`, and any `plant:` value the owner left open, so the
delivery proves totality instead of asserting it. Include the **source-index
build report** of the last `growth-audit.py` run, printed after its verdicts
as advice and never a verdict, with what was done about each line: a `repo:`
value the growth wrote corrected to a path that exists, or a fix or hint
(`TEST_GLOBS`, the plant config, a repository no `repo:` names) put to the
owner as a numbered decision. Grow runs nothing extra for it. Include
growth metrics (the delivery block from `docs/graph/protocols/deliver.md`):
scouts and authors spawned, contradictions resolved by follow-up scouting,
validation findings raised and fixed, evidence gaps left open. These are the plant's birth
telemetry; `harvest` mines them like any other session metrics.

The plant is mature when a clean-context agent can orient from `index.md`
without bulk-reading source; major capabilities, integrations, data, and
cross-cutting concerns have single fact owners and concrete source paths;
useful leaf depth is connected; critical dependencies have project-specific
context; operational status is explicit; representative routing is narrow;
and adversarial navigation rejects false premises.
