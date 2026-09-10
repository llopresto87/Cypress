---
name: grow
description: Canonical tool-neutral full-growth workflow for turning an installed project-agnostic seed into a complete source-grounded docs/graph knowledge system. Invoked by INSTALL_PROMPT.md (installed as EXPERT_SEED_INSTALL_PROMPT.md); coding-tool commands such as /initialize are convenience adapters only. Orchestrates Sonnet-class read-only scouts and Opus-class authors/reviewers, unifies progressive discovery, graph routing, and LLM-wiki depth, and validates the result without changing/building the application or publishing Git state.
id: protocol.grow
tier: 2
kind: protocol
origin: seed
title: grow — the canonical full-growth workflow that turns an installed seed into a source-grounded graph
owns:
  - grow.worker-topology
  - grow.growth-flow
  - grow.completeness-contract
  - grow.stack-inventory
  - grow.plant-facts
  - grow.legal-corpus
requires:
peers:
  - protocol.harvest
  - protocol.graft
  - protocol.initialize
  - protocol.ingest-library
  - protocol.canonize
load_when:
  - "grow the knowledge graph, first growth"
  - "install prompt, EXPERT_SEED_INSTALL_PROMPT"
  - "docs/graph is missing or badly drifted"
  - "regrow or refresh the graph after major drift"
  - "declare the plant block: environment class, commit attribution, languages"
  - "is this plant fully grown, coverage record, growth audit"
est_tokens: 7726
---

# Protocol: grow

This is the canonical workflow. `docs/graph/protocols/initialize.md` is only a
thin coding-tool adapter back to this file.

The caller is an orchestration chat. It owns user communication, planning,
worker selection, briefing, sequencing, and acceptance. It does not perform
the delegated investigation or authoring itself.

## Mandatory worker topology

1. Spawn clean-context **Sonnet-class** scouts for read-only source discovery.
   Partition by real subsystem, repository, or evidence domain. Use the
   growth-dedicated `docs/graph/templates/prompts/growth-scout-brief.md`, whose
   collection target IS the evidence-ledger schema
   (`docs/graph/templates/prompts/growth-evidence-ledger.md`) — demand paths/symbols for
   every claim. Each scout persists ONE ledger per boundary to the plant's
   gitignored seed-organ scratch, `.cypress/growth/<slug>.ledger.md` (never
   under `docs/graph/` — the ledger is growth-time feedstock, not plant
   knowledge).
2. Reconcile the per-boundary ledgers into a coherent evidence set in the
   orchestration plane, cross-referencing the persisted ledgers rather than
   re-holding every claim in context. Resolve contradictions with another
   bounded scout; do not guess.
3. Spawn clean-context **Sonnet-class** `research-scout`s for the **external
   evidence** the graph must be grounded in — the mandatory flip side of
   step 1, not an optional extra. Growth-scouts read this project's code;
   research-scout reads the upstream world that code operates in. Mine the
   reconciled ledgers' §5 for every architecturally significant,
   cross-cutting, security- or operations-critical dependency, and the
   evidence set as a whole for external standards the project is held to
   (protocols, community conventions, regulatory or ecosystem norms); for
   each, dispatch a research-scout per
   `docs/graph/protocols/ingest-library.md` to retrieve version-pinned
   upstream documentation, snapshot/normalize it under `docs/graph/sources/`,
   and hand drafts to the authors. "Executable source is the truth" scopes
   to claims *about this project*; it is not a license to skip the web. A
   growth that spawns only growth-scouts has gathered half its evidence.
4. Spawn **Opus-class** authors for every written artifact or deep synthesis.
   Use purpose-made agents/skills and the growth-dedicated
   `docs/graph/templates/prompts/growth-author-brief.md`, which CONSUMES the
   ledger and maps each section to its deliverable — authors build on the
   collected, cited evidence, never a fresh reading of source or structure
   invented from scratch. (It embeds
   `docs/graph/templates/prompts/node-authoring-brief.md`'s HARD
   RULES for the node-authoring case.)
5. Spawn separate **Opus-class** reviewers/validators for graph integrity,
   source fidelity, navigation, and false-premise rejection.
6. Route each finding back to a bounded Opus author, then revalidate.

Every brief states purpose, exact scope, allowed reads/writes, required graph
context, evidence supplied, constraints, output contract, and verification.
Hooks do not substitute for a self-contained worker brief.

Every spawned session executes the graph-session discipline exactly as
`docs/graph/templates/prompts/graph-session-bootstrap.md` states it — that
canonical block, embedded verbatim in every brief, owns the `--plan` before
source reads, the loaded/skipped report, the widening log, and the
bootstrap fallback. Do not paraphrase it here or in a brief; the block
forbids paraphrase.

Route each spawn the way you route knowledge. Run
`python3 docs/graph/agent-lint.py --route "<exact delegated task>"` and cite the
ranked specialist and confidence band in the brief. Delegating workers spawn
only from their `delegates_to` allowlist and under their `max_spawn_depth` cap
— the deepest legal chain is orchestrator → multi-agent-architect → architect
→ leaf (depth 3). Leaf workers carry no `Task` tool and cannot recurse: at an
out-of-domain boundary they STOP and return the handback payload
(`docs/graph/templates/prompts/handback-payload.md`) naming the next specialist. Every
worker, delegating or leaf, ends its turn with that payload carrying
`produced_by` and `route_evidence`.

Two host conditions look alike here and only one is fatal. If the host cannot
spawn clean-context workers with selectable model classes, stop and report that
this host cannot execute the seed's required operating model — do not silently
collapse delegated work into the main chat. If it can spawn them but a named
specialist is **not registered as a spawnable type** — the ordinary state of the
session that just installed the roster — that is *not* the fatal condition:
preflight it before the first dispatch and apply the remedy, or the recorded
role-emulation fallback, from `docs/graph/method/delegation.md`
(`delegation.harness-registration`). Emulating a specialist without recording it
is the failure; discovering the gap mid-phase is the avoidable cost.

## Boundaries

- Executable source is primary evidence: manifests, entry points, routes,
  models, migrations, configuration, deployment descriptors, tests, CI,
  prompts, and evaluations. Existing prose and centralized documentation are
  clues only; corroborate imported facts against source.
- That rule scopes to claims **about this project**. For what a dependency
  or external standard *is*, authoritative upstream documentation — fetched
  by `research-scout` during this growth — is the primary evidence, and
  internal source is the evidence of how this project *uses* it. Reading
  only the project's own files is not evidence discipline; it produces a
  graph with no grounding in the ecosystem the project operates in. Web
  retrieval of upstream docs is in scope for growth; Git publishing is not.
- Preserve target-owned files. Knowledge writes stay under `docs/graph/`.
- Do not change application code, manifests, CI, infrastructure, or tests.
- Growth does not run application builds or application test suites. It may
  run knowledge-only lint, link, route, and generated-view drift checks.
- Do not fetch, pull, switch, commit, push, or publish Git state. Record current
  branch and commit only as provenance.
- Never invent behavior, requirements, rationale, ADRs, commands, URLs,
  project skills, or passing status. A surface with no real recurring use behind
  it (a project skill, an ADR, a runbook's commands) is left to sprout from that
  use at close-out (`canonize` → `docs-librarian`), never fabricated to look
  populated. Mark uncertain claims `unknown` and name needed evidence.
- Observed implementation is descriptive architecture, not a normative spec.

## Unified knowledge shape

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

Growth is **complete or it is not done**. A first growth that stops at a
skeleton — a root node, a router, and a handful of leaves — is a failed
growth reported as a success, and it is the single most common way this
protocol is mis-run. The contract below is binding on whatever model
orchestrates growth; it does not soften with model size, context pressure,
or operator impatience. Full depth is the default, not an upgrade.

**The rule of evidence-bounded totality.** For every knowledge collection in
the unified shape above, growth produces one of exactly two outcomes, and
never a third silent one:

- *Covered* — the collection is authored to the full depth its evidence
  supports: every real subsystem has a node; every direct dependency is
  indexed and each architecturally-significant one has a project-specific
  page grounded in retrieved upstream documentation (topology step 3);
  every observed route/message/job/entity/migration/config/AI-contract
  is homed; every leaf is connected to its owning node by an `artifacts:`
  edge; the router resolves representative tasks to small closures.
- *Absent with a named reason* — the collection is empty because the
  **source has no such evidence** (no HTTP surface, no migrations, no AI
  prompts), and that absence is stated explicitly in the coverage record
  with the paths that were searched.

Any collection that is neither fully covered nor explicitly absent-with-reason
is an incomplete growth. "Ran out of context", "seemed enough", "the templates
are present", and "the common cases are done" are not the second outcome — they
are the failure the contract exists to forbid. Template files existing at their
paths is never coverage; only authored, source-cited content is.

**The coverage record and the loop it serves.** Coverage is recorded, not
narrated. Before declaring growth done the orchestration chat fills
`.cypress/coverage.json` in the schema of
`docs/graph/templates/prompts/growth-coverage-record.md`, and
`tools/growth-audit.py` reads it back:

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
declares `plant_knowledge:` — the collections that agent must be able to read
before it can work on this project at all — and one per project-specific expert
the plant's own graph carries. The second set is what makes "all agents" a
checkable claim rather than an intention, and it is why a graft to a newer seed
surfaces the specialists it added as rows the plant does not yet answer. The
third holds this protocol to the other half of its promise: growth is supposed
to leave behind experts this project needs and the shipped roster does not
have, and an expert is only real once it is a node, cites what earned it, and
is projected where the host can spawn it.

The record is **tracked**, beside the plant's `.cypress/seed.json` stamp — not
under `.cypress/growth/`, which stays the run's gitignored scratch, and not
under `docs/graph/`, which is the plant's own knowledge. It outlives the run
that wrote it because its whole purpose is to let a later session, and the next
graft, tell a collection nobody looked at from one the project genuinely has no
evidence for. A row may not be left blank, and template files existing at their
paths is never coverage.

**No unfilled scaffold survives growth.** The installer places every leaf of
the seed's `templates/docs/**` under `docs/graph/` so each collection has
somewhere to land; a leaf still byte-identical to its template when growth
ends is a scaffold posing as knowledge, and it **shadows** the authored leaf a
cold agent needed — the router resolves to placeholders and reads them as
facts. Phase 6 runs `python3 <seed>/tools/graft-audit.py <plant> <seed>
--unfilled` and it must report zero. Where a scaffold is honestly unfilled
(its collection is absent-with-reason), the session re-runs with `--rename`
— the leaf becomes `<name>.unfilled.md`, a marker the installer honours so
the blank never comes back — and lists every renamed leaf in the completion
report. `runbooks/verification.md` earns exemption only by carrying at least
one gate marked `executed`. Growth never `--prune`s: a pruned leaf reappears
at the next install or graft, and removal is the steward's call, not the
growth's.

**No early stop.** Growth does not end at the orchestrator's discretion when
"enough" has been produced. It ends when the ledger shows every collection is
covered-to-evidence or absent-with-reason, Phase 6's independent validation
passes, and the maturity test at the foot of this protocol is met against the
graph — not against the file tree. If a fatal host limit, a two-round
non-converging finding (`recover`), or an evidence gap the scouts cannot close
blocks a specific collection, that collection is delivered as an honest
`unknown` with the blocker named — the one legitimate way a collection stays
uncovered, and it is reported, never silent.

## Phase 1 — Detect and plan

Determine whether the target is empty/new, one repository, a workspace or
monorepo, or an umbrella containing sibling repositories. Stay inside the
user-placed scope. Record each repository's path, current branch, HEAD,
worktree state, role, manifests, and stack without mutating Git.

Ensure the plant gitignores `.cypress/growth/` before scouting — that is where
the growth evidence ledgers land, and they are a seed organ transient to this
run, not plant knowledge the plant commits. Two files beside it are the
exception and stay TRACKED: the `.cypress/seed.json` stamp and
`.cypress/coverage.json`, the coverage record — it is the durable answer to
what this growth covered, and a gitignored answer is one the next session and
the next graft cannot read. Ignore `.cypress/growth/`, not `.cypress/`.

**Ask the owner for the plant facts — once (`grow.plant-facts`).**
`docs/graph/index.md` carries a `plant:` block (`docs/graph/_schema.md`
§"The `plant:` block") holding the facts only the owner can assert and
agents otherwise re-ask or guess: `environment_class`, `commit_attribution`,
`deliverable_language`, `comment_language`. Propose each value from evidence
— deployment descriptors and CI targets for the environment class, trailers
in the recent commit log for attribution, the language of existing comments,
docs, and UI strings for the two languages — and record the evidence used
beside each proposal (the scout that gathered it cites paths like any other
claim). Put the four to the owner as one numbered ask
(`deliver.numbered-decisions`) and write the confirmed values into the
frontmatter block. A value the owner does not answer is not guessed: it
stays a `status: open` item, owner named, in the coverage record
and in the delivery — and `graph-lint.py` fails a grown plant until the block
is declared. Never ask twice; later sessions read the block.

**Ask the owner about the legal corpus — once, before authoring
(`grow.legal-corpus`).** `agent.legal` runs without web access: the corpus the
installer places plus this plant's own legal leaf is the only law it can reach,
and its charter turns a gap into a refusal rather than a reconstructed
citation. A plant with no corpus therefore has an analyst that can only refuse,
and one whose corpus was filtered has an analyst that cannot tell a page nobody
copied from an instrument that does not exist — which is the refusal rule
inverted into a silent false negative. So the question is binary and it is the
owner's: `--legal-corpus yes` places every page under
`docs/graph/legal/corpus/`, `no` records that this plant carries none.

**And ask which national law, in the same breath (`--legal-jurisdiction <cc>`).**
The corpus's EU and international layers are jurisdiction-neutral and travel
with it whole. Its **national** layer is only as wide as what has been
ingested — today that is Italy, and the installer derives the list from
`legal-corpus/national/` rather than claiming it here. A plant established
somewhere else is not a smaller case of the Italian one: naming a code the
corpus does not carry records an **ingest request**, closed by a
`research-scout` pass under the corpus's own entry contract, and until it lands
`agent.legal` refuses on that jurisdiction — correctly. What must never happen
is a neighbouring country's statute standing in for the missing one, or an
EU directive being cited for a national obligation it only binds Member States
to transpose (`legal-corpus/_schema.md` §"Four instrument kinds").

Put both as numbered decisions (`deliver.numbered-decisions`) alongside the four
plant facts, before Phase 4 authors anything. Unanswered, it stays a `status: open`
item with the owner named, exactly as an unset plant fact does, and
`.cypress/seed.json` records `"legal_corpus"` / `"legal_jurisdiction"` as
`"undecided"`. What may **not**
happen is a run deciding it by inspection: relevance is expressed afterwards,
in `legal/index.md`, and revised as the project evolves.

**An existing graph that predates 7.0.0** (a refresh, or an adopted plant)
carries lifecycle status as body prose in a vocabulary per kind. Run
`python3 <seed>/tools/status-migrate.py --root docs/graph` (dry run) and
show the owner its table; on the owner's go, re-run with `--write`. The tool
moves each status into frontmatter in the schema's one vocabulary and turns
the body line into a pointer; what it cannot map (a threat model's `active`,
a superseded record with no named successor) it reports for the owner to
decide — never invents.

Settle spawnability here too, not in Phase 2. A session that just installed the
seed holds an agent registry from before the install, and a session rooted at
the seed rather than the plant never holds the plant's roster at all — so
preflight one roster type now and take the remedy or the recorded fallback
(`docs/graph/method/delegation.md`, `delegation.harness-registration`). Scouting
is the wrong place to learn that no scout can be spawned.

Inventory cheaply before opening large files. Ignore generated, vendor,
cache, and build directories. Identify real subsystem boundaries and divide
read-only scouting across them. Also assign focused scouts for cross-cutting
evidence: APIs/messages, data/migrations, platform/config,
tests/CI/operations, dependencies, prompts/evaluations, **the interface and
design surface**, **the project's regulatory exposure**, and **the external
standards its stack and domain are held to**.

This list is the intake, and a domain missing from it is a collection no plant
ever grows. It is derived from the roster, not from habit: every agent that
declares `plant_knowledge:` needs some collection filled before it can work on
this project at all, and a scout must be assigned to gather the evidence that
fills it. When the seed adds a specialist, this list gains its evidence domain
in the same change — the three domains named in bold above are the ones added
late to the roster and left out of this list for several versions, which is why
plants grown in that window carry a `ui-ux-designer` with no design material
and a `legal` analyst with no corpus.

If there is no executable project evidence, route through `from-scratch` for
intent discovery, while retaining this worker/model policy and graph root.

## Phase 2 — Scout and establish evidence

Spawn the planned Sonnet-class scouts on
`docs/graph/templates/prompts/growth-scout-brief.md`. Each writes ONE ledger to
`.cypress/growth/<slug>.ledger.md` in the schema of
`docs/graph/templates/prompts/growth-evidence-ledger.md` — every section keyed
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
- discrepancies between executable source and existing prose.

The persisted per-boundary ledgers ARE the evidence set: claim area, strong
source, corroborating source, confidence, and gaps, each keyed to the
deliverable it feeds. Reconcile across them, resolve contradictions by scoped
follow-up scouting, and record which ledger owns each contested fact. Do not
let a centralized docs repository become authoritative by repetition.

**Then reconcile the ledgers into the stack inventory (`grow.stack-inventory`).**
Every item the project is made of gets one row: each language and its version,
each runtime and framework, each direct dependency with its significance, the
infrastructure it runs on, its data stores, the external and AI services it
calls, each design surface, and each regulatory exposure — every row anchored
to the source path that proves it. Write it into the `inventory` array of
`.cypress/coverage.json` and run
`python3 <seed>/tools/growth-audit.py <plant> <seed> --plan`, which turns each
row into the artifacts growth now owes it and marks which rows require
grounding in retrieved upstream documentation. The inventory is what growth is
held to; a project item that never reaches it is an item no gate can miss the
absence of.

**Then establish the external evidence (topology step 3) before authoring
begins.** Every inventory row the plan marks `grounding.required` needs
upstream documentation retrieved from the open web during THIS run — languages,
runtimes and frameworks (their current guidance and the practices they name as
wrong, not only their API surface), significant dependencies, infrastructure
components, data stores, external and AI services, the design standards the
interface is held to, and the instruments behind each regulatory exposure. A
page written from model memory is the failure this step exists to prevent:
memory is unversioned, undated, and uncitable. Dispatch one bounded `research-scout`
per item (batched sensibly) following `docs/graph/protocols/ingest-library.md`:
retrieve authoritative upstream documentation pinned to the versions the tree
actually locks, snapshot raw sources to `docs/graph/sources/raw/`, normalize
to `docs/graph/sources/normalized/`, and register each in
`docs/graph/sources/index.md`. A normalized snapshot names its raw file, or
the reason none was kept, in the `raw:` line of its metadata block — the
coverage gate holds `sources/` to it (`UNJUSTIFIED`), because "when the
license permits" recorded nowhere is an out every scout takes. These
sonnet-class writes are mechanical
normalization, not authoring (`agent.research-scout` owns that distinction).
Record the dispatch list in the orchestration plan: Phase 4's `libraries/`
rich pages, normative `best-practices/`, and `sources/` provenance are
authored FROM this material, and the coverage record audits against this
list. If the host truly has no web retrieval, that is a named blocker — the
affected collections ship as honest `unknown`, never as a silent thin index.

## Phase 3 — Model and author through Opus workers

Configure `ROOT_ID` and `KINDS` in `graph-lint.py`. Brief Opus-class authors on
`docs/graph/templates/prompts/growth-author-brief.md`: point each at the ledgers it reads
(`.cypress/growth/*.ledger.md`), the exact output paths, schema, relevant
existing nodes, and exclusive write scopes. Authors build from the ledger's
cited claims — a fact the ledger marks `not recorded` stays unrecorded, a
section marked `none found` is omitted, never invented. Author:

- one root node for the governed project/program;
- one node per real subsystem or bounded capability;
- shared stack, platform, data, domain, and cross-cutting nodes where they
  remove duplication or materially improve routing;
- a compact Tier-1 task-to-entry router using realistic developer phrases.

Each node has unique `owns`, minimal acyclic `requires`, explicit boundary
`peers`, concrete `load_when` phrases/paths, honest token cost, source paths,
and leaf edges. Never ask multiple authors to own overlapping facts or files.

## Phase 4 — Grow source-backed leaves

Through bounded Opus authors, populate every collection supported by evidence:

- `product/`: actors, capabilities, flows, constraints, observed behavior;
- `architecture/`: context, components, boundaries, runtime flows,
  integrations, and dated sharp edges;
- `api/`: observed HTTP/RPC/event/job contracts and source locations;
- `data/`: entities, ownership, persistence, migrations, lineage, privacy;
- `libraries/` — with `best-practices/` below and `nodes/expertise.*`, three
  artifacts authored from ONE body of evidence (the ledgers' §5, §9 and §14
  and the upstream sources the research-scouts retrieved in Phase 2), each
  owning a different question and restating neither of the others.
  `libraries/` is the **fact and pin home**: every direct dependency
  indexed, and a rich project-specific page for every architecturally
  significant, cross-cutting, security, or operational dependency, grounded
  in that retrieved documentation per
  `docs/graph/protocols/ingest-library.md` — a thin index table where the
  ledgers' §5 flags significant dependencies is NOT coverage. The exact
  major(s) this plant runs are recorded there and nowhere else. Growth runs
  no application code, so `ingest-library`'s smoke-test validation is
  recorded on each page and in `plans/grill.md` as a pending backfill,
  never claimed passed. `nodes/expertise.<slug>.md` is the **routing node** —
  one per core or significant language, runtime, framework, dependency,
  infrastructure component, and datastore the stack inventory carries, which
  the coverage plan derives; an item the scouts marked incidental owes none.
  It owns exactly when that element is in play for a task, what must not be
  done without it, and which sub-expertises apply under which condition; it
  carries no version and no API surface, pointing at the pin with
  `libraries:` and at the standard with `artifacts:` instead of repeating
  either. Composition is wired downward with `composes:` on the parent and
  upward with `requires:` on the child, so the router descends only into the
  children a task names specifically. Where the inventory carries one slug
  at two majors, the unversioned node composes one version-qualified child
  per major (`expertise.dotnet-8`) whose triggers are that major's target
  tokens — the only place a version enters a slug;
- `legal/`: the corpus itself is placed by the installer, **whole or not at
  all**, on the owner's `grow.legal-corpus` answer — never assembled here and
  never subsetted (`legal-corpus/_schema.md` §"Whole corpus, or none").
  What this phase authors is `legal/index.md`: the **scope instruction** —
  which instruments bear on this project today, which do not and why, and what
  the corpus does not carry at all. That is a determination, it is revised as
  the project evolves, and it is the only legitimate way to narrow what
  `agent.legal` considers; deleting a page is not. Each in-scope instrument's
  `verified` and `legal_status` are **re-confirmed against the publisher**
  before anything is relied on — a citation that shipped once is not thereby
  current. The corpus supplies the citation; the project's own application of a
  rule is authored in the node that makes the claim, cites the entry id, and is
  never folded back (see `docs/graph/protocols/harvest.md`);
- `sources/`: provenance rows for every upstream source the research-scouts
  retrieved during THIS growth (raw snapshot, normalized copy, index row).
  Growth creates its own external consumption via topology step 3 — marking
  `sources/` absent with "no external information was consumed" when no
  research-scout was ever dispatched is circular: the absence is the
  orchestrator's omission, not a property of the project, and it is a
  completeness defect. `sources/` may be absent only when the reconciled
  ledgers genuinely flag no significant dependency and no external standard
  — a rare project, and the ledger rows proving it must be cited;
- `design/`: one leaf per interface surface the source shows — screens and
  flows, interaction states, the component system and its design tokens,
  visual hierarchy, and how the accessibility floor is met — authored by
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
- `plans/grill.md`: inspected evidence, gaps, drift/backfill work, and the
  smallest useful next increment;
- `best-practices/`: the **standard home** of the trio above, and
  **normative, not descriptive** — the community and upstream standards the
  project's stack and domain are held to (cited from the same retrieved
  sources), and where the project observably stands against each (conforms /
  deviates / unknown, with source paths). "Here is what the project happens
  to do" alone is a description that belongs in `architecture/`; the leaf
  earns its home by stating the standard and the project's stance, which is
  what the matching expertise node routes a worker here for rather than
  restating;
- `changelog.md`: artifacts/revisions covered by the growth pass.

Prepare indexes for `specs/` and `decisions/`, but do not manufacture records.
Formalize a spec only from a ledger §7 spec-worthy behavior with a real
observable, and an ADR only from a ledger §8 decision the source actually
shows — never invent rationale to fill a record. If genuine intent records
exist, preserve them with provenance. Put observed implementation choices in
architecture leaves or nodes.

**Staff the project, and record the decision either way.** A plant is not only
knowledge; it is also the expertise that knowledge is for. Every core or
significant stack element owes an `expertise.*` node (the coverage plan derives
it), and that node is the default answer to "who knows this here": the router
composes it into any worker whose task names it. An **agent** is warranted only
for what a node cannot serve — work that needs different `tools`, a different
`model` class, an adversarial `stance`, or context `isolation` — and every
inventory item of kind `domain` or marked `significance: core` closes its
`expert` decision in the coverage record with `warranted`, a `why`, and, when
true, the `needs` it names. A decision nobody recorded reads exactly like a §9
nobody opened. Where an agent is warranted, check the seed's `agent-corpus/`
first, author from `docs/graph/templates/agent.template.md` and the cited
evidence, mark it `origin: project`, declare its `plant_knowledge:`
(collections or the expertise nodes it draws on), cite what motivated it, and
project it to every path this plant's `.cypress/seed.json` records —
unprojected it is on disk and unspawnable
(`delegation.harness-registration`), and on most harnesses spawnable only in
the next session; say so in the delivery.

Apply the same withdraw-on-evidence discipline to the reusable-tool and
suggested-skill corpora, so harvested tooling and procedures reach a new plant
at growth time and not only via a later graft. Anything the plant authors that
is *meant to travel* — a tool or skill it may later offer back, a component it
declares project-agnostic — runs `docs/graph/agnosticism-lint.py` over it
before it is called done, with the plant's own name and paths passed as
`--forbid`; that is the same floor harvest will apply, applied early enough to
be cheap. Everything else the growth authors SHOULD name the project: this is
the plant's own knowledge, and the lint has no business there. Where the plant's real stack
matches a portable tool the corpus carries (`tool-corpus/<category>/<name>.md`)
— a self-contained capability the source genuinely needs — seed
`docs/graph/tools/<name>.md` from it as the orientation layer (adopt the
portable implementation when the stack matches; re-author test-first when it
does not). Where a repeatable procedure the source actually performs matches a
`skill-corpus/<name>.md` entry, seed `docs/graph/skills/<name>.md` from it
(projected into the harness by the plant itself). Both are candidates, not
mandates, and neither is fabricated: a tool or skill whose need has not actually
arisen in the source is left for `toolcraft`/`canonize` to sprout from real
recurring use, and the absence is recorded ("no corpus tool/skill warranted")
rather than padded.

For an existing graph, refresh current fact owners rather than duplicating
them, preserve valid hand-authored knowledge, cite contrary evidence for
stale claims, and record unresolved conflicts. Never claim coverage for source
that scouts could not access.

## Phase 5 — Connect and fertilize (the librarian rebalance pass)

This phase is a **mandatory, named dispatch** — one Opus-class
`docs-librarian` pass over the whole authored graph, run after Phase 4 and
before validation, never skipped because the authors "already linked things".
Authors work in exclusive scopes; only a whole-graph pass can see the seams
between them. The librarian:

- ensures every leaf has an owning-node `artifacts:` edge and every node is
  reachable from the router;
- **rebalances**: merges near-duplicate homes (one home per fact), splits
  nodes that accreted unrelated facts, moves depth behind edges out of the
  always-loaded router and oversized nodes, deletes pass-through nodes that
  only forward, and sharpens the expertise families the same way —
  `graph-lint.py` warns where a composed child's trigger is shared with a
  sibling (family vocabulary that belongs on the parent, where it cannot
  descend anyone) or is carried by too much of the graph to say this child
  is what a task is about, and each warning names the move: lift the term
  one level, or replace it with the child's own words;
- verifies searchable paths/symbols/commands sit in the right home and
  unknowns are answerable questions with likely evidence locations;
- keeps the router compact and re-runs `graph-lint.py` after rebalancing.

Report the pass in the delivery (what was merged, split, moved, deleted, and
which triggers were sharpened).
"No rebalance needed" is a legitimate result only when the librarian pass
actually ran and says so.

## Phase 6 — Independent validation

Dispatch separate Opus reviewers and clean-context validators. They run only
knowledge checks:

```sh
python3 docs/graph/graph-lint.py
python3 docs/graph/graph-lint.py --plan "change a representative subsystem"
python3 docs/graph/agent-lint.py --lint
python3 docs/graph/status-register.py --root docs/graph
python3 <seed>/tools/graft-audit.py <plant> <seed> --unfilled
python3 <seed>/tools/growth-audit.py <plant> <seed>
```

They also verify:

1. internal links and every `artifacts:`/`libraries:` edge resolve;
2. no maintained knowledge collection exists outside `docs/graph/`;
3. no template placeholders or fabricated dates/statuses remain — and no
   unfilled scaffold: `--unfilled` reports zero, or every leaf renamed
   `<name>.unfilled.md` is listed in the completion report
   (`grow.completeness-contract`);
4. every expert this growth authored is a spawnable agent, not just a file:
   `agent-lint.py --lint` passes on it (an expert with no `routing_triggers`
   is a node the router cannot reach), and the coverage audit's expert rows
   report no missing projection;
5. representative tasks load small, relevant node closures, and descent is
   as narrow as the graph claims it is: a task specific to one library loads
   the parent expertise node and that library's node and none of its
   siblings, and `--plan` accounts for every child it left out by printing
   the reason no task term was specific to it;
6. known-answer questions are answered from routed graph context with source
   citations, including adversarial false-premise rejection;
7. observed implementation has not been mislabeled as specs or ADR rationale;
8. commands distinguish executed from merely discovered;
9. generated tool views pass their read-only drift check where available;
10. the growth is **minimum-sufficient and well-composed**
   (`docs/graph/method/engineering-posture.md` and
   `docs/graph/method/design-posture.md`): every authored node,
   leaf, and specialist serves a real routing or fact-owning need; no
   artifact lacks a consumer; no fact gained a second home; the router
   stays compact; and each node holds one coherent responsibility — a
   node owning unrelated facts is weak cohesion to split, a node that
   only forwards to others is a pass-through to delete. Over-growth and
   mis-composition are findings routed back to an author exactly as gaps
   are.
11. the growth is **complete** against `grow.completeness-contract`:
   `growth-audit.py` exits 0. Its verdicts are the findings — a planned
   artifact that never appeared (`UNGROWN`), one that appeared as a scaffold
   (`HOLLOW`), an item that needed retrieved documentation and cites none
   (`UNGROUNDED`), a row claimed covered that the plant's own files
   contradict, or an agent's absence that found a filled leaf of the graph
   where it searched (`CONTRADICTED`), an absence asserted without a reason
   or the paths searched, or a retrieved source with neither its raw
   snapshot nor the reason there is none (`UNJUSTIFIED`), a surface that
   never answered whether it warrants an expert of its own, claimed one
   without naming what a node could not have served, or named one the plant
   does not carry (`UNSTAFFED`), an `UNKNOWN` whose blocker the record names
   and the delivery entry never does (`SILENT`), a collection, agent, or
   expert the record never answers for (`MISSING`, `BLANK`). Each routes
   back to a bounded author
   exactly as any other gap does, and the audit re-runs. Validators also
   spot-audit a sample of the cited paths by hand: the linter proves the file
   exists and says something, not that what it says is true. Under-growth is
   a defect on equal footing with over-growth.
12. the growth is **externally grounded**: every ledger-§5 dependency flagged
   architecturally significant / cross-cutting / security- or
   operations-critical has a rich `libraries/` page citing retrieved
   upstream sources; every `docs/graph/sources/index.md` row resolves to a
   real normalized file; `best-practices/` leaves state the external
   standard AND the project's stance; and any `sources/` ABSENT row is
   audited against the ledgers' §5 — an absence that exists because no
   research-scout was dispatched is a completeness finding (the circular
   absence), not a fact about the project;
13. the **librarian rebalance pass (Phase 5) actually ran** and its
   merge/split/move/delete report is present in the delivery — authored
   collections without a whole-graph librarian pass are a finding.

Route findings to bounded Opus authors and repeat independent validation —
**bounded by the recover discipline** (`docs/graph/protocols/recover.md`): a finding
that survives two author-fix → revalidate rounds is not converging; stop,
record it as an honest unknown or a defect in the delivery, and hand the
decision to the user. Do not weaken the linter to make a defective graph
pass, and do not loop a fourth time.

When validation passes, set `grown: true` in the frontmatter of
`docs/graph/index.md` — the marker `graph-lint.py` reads to hold this plant
to the grown standard (a missing `plant:` block fails, not warns, from here
on). Set it only then; a plant stamped grown while half-grown lies to every
later lint.

Also configure the spec-coverage gate while the stack evidence is fresh:
set `TEST_GLOBS` in `docs/graph/spec-lint.py` to the project's real test
layout (the scouts reported it) and run `python3 docs/graph/spec-lint.py
--warn` — with no specs yet it reports clean, but the first spec this
plant authors will land with a working §3.1 gate instead of a dormant one.

## Delivery and maturity

Before reporting, close the growth session itself through
`docs/graph/protocols/canonize.md` (§3.7): its single librarian close-out
spawn records what the growth learned — sharp edges met, contradictions
resolved, tools discovered — so the plant's first working session inherits
it. Growth that ends without canonize leaks its own lessons.

The orchestration chat reports target boundary/revisions, worker assignments,
evidence inspected, artifacts created/refreshed, the Phase 5 librarian
rebalance report, validation results,
untrusted/excluded docs, honest unknowns, and one next action — **with its
tier** (kernel §0), so the next session starts classified instead of cold.
Every `UNKNOWN` row is named there **and** in the plant's `changelog.md`
entry for the pass — the row, what it waits on, and who — and a blocker
that is the owner's to resolve is put to the owner as a numbered decision
(`deliver.numbered-decisions`), the same ask the plant facts use, not left
for them to find. The record is not where the owner reads:
`growth-audit.py` reports an `UNKNOWN` the changelog never names as
`SILENT`, and the gate fails on it. A blocker filed as "the owner's
determination" that the owner never saw was not put to anyone.
Include the **coverage record** (`grow.completeness-contract`) —
every collection marked covered-to-evidence or absent-with-reason, the
scaffolds renamed `.unfilled.md`, and any `plant:` value the owner left open
— so the delivery proves totality instead of asserting it. Include growth metrics (the
delivery block from `docs/graph/protocols/deliver.md`): scouts and authors
spawned, contradictions resolved by follow-up scouting, validation findings
raised and fixed, evidence gaps left open. These are the plant's birth
telemetry; `harvest` mines them like any other session metrics.

The plant is mature when a clean-context agent can orient from `index.md`
without bulk-reading source; major capabilities, integrations, data, and
cross-cutting concerns have single fact owners and concrete source paths;
useful leaf depth is connected; critical dependencies have project-specific
context; operational status is explicit; representative routing is narrow;
and adversarial navigation rejects false premises. Template presence alone is
never evidence of maturity.
