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
requires:
peers:
  - protocol.harvest
  - protocol.graft
  - protocol.initialize
load_when:
  - "grow the knowledge graph, first growth"
  - "install prompt, EXPERT_SEED_INSTALL_PROMPT"
  - "docs/graph is missing or badly drifted"
  - "regrow or refresh the graph after major drift"
est_tokens: 3600
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
3. Spawn **Opus-class** authors for every written artifact or deep synthesis.
   Use purpose-made agents/skills and the growth-dedicated
   `docs/graph/templates/prompts/growth-author-brief.md`, which CONSUMES the
   ledger and maps each section to its deliverable — authors build on the
   collected, cited evidence, never a fresh reading of source or structure
   invented from scratch. (It embeds
   `docs/graph/templates/prompts/node-authoring-brief.md`'s HARD
   RULES for the node-authoring case.)
4. Spawn separate **Opus-class** reviewers/validators for graph integrity,
   source fidelity, navigation, and false-premise rejection.
5. Route each finding back to a bounded Opus author, then revalidate.

Every brief states purpose, exact scope, allowed reads/writes, required graph
context, evidence supplied, constraints, output contract, and verification.
Hooks do not substitute for a self-contained worker brief.

Every spawned session executes
`python3 docs/graph/graph-lint.py --plan "<exact delegated task>"` before
source reads or writes, loads the resulting nodes plus `requires` closure, and
returns its route output, loaded/skipped set, and widening log. Before the
first nodes exist, bootstrap workers still execute and report the failed probe,
then stay inside their explicitly enumerated paths. Re-run the tool normally
for all workers spawned after the graph becomes routable.

Route each spawn the way you route knowledge. Run
`python3 .claude/agent-lint.py --route "<exact delegated task>"` and cite the
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
├── nodes/
├── libraries/, sources/
├── legal/            (only when externally-authored rules are in scope)
├── product/, architecture/, api/, data/
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
  page; every observed route/message/job/entity/migration/config/AI-contract
  is homed; every leaf is connected to its owning node by an `artifacts:`
  edge; the router resolves representative tasks to small closures.
- *Absent with a named reason* — the collection is empty because the
  **source has no such evidence** (no HTTP surface, no migrations, no AI
  prompts), and that absence is stated explicitly in the completeness ledger
  with the paths that were searched.

Any collection that is neither fully covered nor explicitly absent-with-reason
is an incomplete growth. "Ran out of context", "seemed enough", "the templates
are present", and "the common cases are done" are not the second outcome — they
are the failure the contract exists to forbid. Template files existing at their
paths is never coverage; only authored, source-cited content is.

**The growth completeness ledger.** Before declaring growth done, the
orchestration chat fills one ledger in the schema of
`docs/graph/templates/prompts/growth-completeness-ledger.md` — a table over every
collection in the unified shape (product, architecture, api, data, libraries,
sources, legal, prompts, evaluations, runbooks, plans, specs, decisions,
best-practices, changelog, and every subsystem/stack/cross-cutting node) —
marking each `covered` (with the count of nodes/leaves authored and the
strongest source paths), `absent` (with the reason and searched paths), or a
named `unknown` blocker. It is a seed-organ transient, written to the plant's
gitignored `.cypress/growth/completeness-ledger.md`, never under `docs/graph/`.
A collection may not be left blank. This ledger is part of the delivery block
and is what Phase 6 validation audits against — coverage is asserted, not
asserted-to.

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
run, not plant knowledge the plant commits (the `.cypress/seed.json` stamp
stays tracked; the growth scratch does not).

Settle spawnability here too, not in Phase 2. A session that just installed the
seed holds an agent registry from before the install, and a session rooted at
the seed rather than the plant never holds the plant's roster at all — so
preflight one roster type now and take the remedy or the recorded fallback
(`docs/graph/method/delegation.md`, `delegation.harness-registration`). Scouting
is the wrong place to learn that no scout can be spawned.

Inventory cheaply before opening large files. Ignore generated, vendor,
cache, and build directories. Identify real subsystem boundaries and divide
read-only scouting across them. Also assign focused scouts for cross-cutting
evidence where needed: APIs/messages, data/migrations, platform/config,
tests/CI/operations, dependencies, and prompts/evaluations.

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
- discrepancies between executable source and existing prose.

The persisted per-boundary ledgers ARE the evidence set: claim area, strong
source, corroborating source, confidence, and gaps, each keyed to the
deliverable it feeds. Reconcile across them, resolve contradictions by scoped
follow-up scouting, and record which ledger owns each contested fact. Do not
let a centralized docs repository become authoritative by repetition.

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
- `libraries/`: every direct dependency indexed; rich project-specific pages
  for architecturally significant, cross-cutting, security, or operational
  dependencies;
- `legal/`: **only when the project is subject to externally-authored rules**
  (statute, regulation, a standards catalog, a contractual regime). Check the
  seed's `legal-corpus/<scope>/<instrument>.md` **first** and seed each page
  from it as the orientation layer, then **re-confirm `verified` and
  `legal_status` against the publisher** before anything here is relied on — a
  citation that shipped once is not thereby current. The corpus supplies the
  citation; the project's own application of it is authored here and never
  folded back (see `docs/graph/protocols/harvest.md`);
- `sources/`: provenance for external information actually used;
- `prompts/` and `evaluations/`: AI contracts, call sites, datasets, rubrics,
  gates, and failure modes;
- `runbooks/verification.md`: exact commands and prerequisites, explicitly
  labeled `discovered, not executed` during growth;
- `plans/grill.md`: inspected evidence, gaps, drift/backfill work, and the
  smallest useful next increment;
- `best-practices/`: conventions demonstrated by this project;
- `changelog.md`: artifacts/revisions covered by the growth pass.

Prepare indexes for `specs/` and `decisions/`, but do not manufacture records.
Formalize a spec only from a ledger §7 spec-worthy behavior with a real
observable, and an ADR only from a ledger §8 decision the source actually
shows — never invent rationale to fill a record. If genuine intent records
exist, preserve them with provenance. Put observed implementation choices in
architecture leaves or nodes.

Where a ledger's §9 specialist-agent signal genuinely warrants it — a
high-risk surface or dominant domain the base roster does not cover — author a
project-specific expert agent (`docs/graph/templates/agent.template.md`) from that cited
evidence. A signal is a candidate, not a mandate: absent a real need, record
"no custom agent warranted" rather than padding the plant's roster.

For an existing graph, refresh current fact owners rather than duplicating
them, preserve valid hand-authored knowledge, cite contrary evidence for
stale claims, and record unresolved conflicts. Never claim coverage for source
that scouts could not access.

## Phase 5 — Connect and fertilize

Dispatch an Opus librarian to ensure every leaf has an owning-node edge, every
node is reachable, searchable paths/symbols/commands appear in the right home,
unknowns are answerable questions with likely evidence locations, and the
router stays compact. Depth belongs behind edges, not in the always-loaded
router or oversized nodes.

## Phase 6 — Independent validation

Dispatch separate Opus reviewers and clean-context validators. They run only
knowledge checks:

```sh
python3 docs/graph/graph-lint.py
python3 docs/graph/graph-lint.py --plan "change a representative subsystem"
```

They also verify:

1. internal links and every `artifacts:`/`libraries:` edge resolve;
2. no maintained knowledge collection exists outside `docs/graph/`;
3. no template placeholders or fabricated dates/statuses remain;
4. representative tasks load small, relevant node closures;
5. known-answer questions are answered from routed graph context with source
   citations, including adversarial false-premise rejection;
6. observed implementation has not been mislabeled as specs or ADR rationale;
7. commands distinguish executed from merely discovered;
8. generated tool views pass their read-only drift check where available;
9. the growth is **minimum-sufficient and well-composed**
   (`docs/graph/method/engineering-posture.md` and
   `docs/graph/method/design-posture.md`): every authored node,
   leaf, and specialist serves a real routing or fact-owning need; no
   artifact lacks a consumer; no fact gained a second home; the router
   stays compact; and each node holds one coherent responsibility — a
   node owning unrelated facts is weak cohesion to split, a node that
   only forwards to others is a pass-through to delete. Over-growth and
   mis-composition are findings routed back to an author exactly as gaps
   are.
10. the growth is **complete** against `grow.completeness-contract`: the
   growth completeness ledger has a row for every collection in the unified
   shape, each `covered` (audit a sample of its cited source paths) or
   `absent` (confirm the source truly has no such evidence). A collection
   silently missing from the ledger, or marked covered where the evidence is
   thin or template-only, is a completeness finding routed back exactly as a
   gap is. Under-growth is a defect on equal footing with over-growth.

Route findings to bounded Opus authors and repeat independent validation —
**bounded by the recover discipline** (`docs/graph/protocols/recover.md`): a finding
that survives two author-fix → revalidate rounds is not converging; stop,
record it as an honest unknown or a defect in the delivery, and hand the
decision to the user. Do not weaken the linter to make a defective graph
pass, and do not loop a fourth time.

Also configure the spec-coverage gate while the stack evidence is fresh:
set `TEST_GLOBS` in `docs/graph/spec-lint.py` to the project's real test
layout (the scouts reported it) and run `python3 docs/graph/spec-lint.py
--warn` — with no specs yet it reports clean, but the first spec this
plant authors will land with a working §3.1 gate instead of a dormant one.

## Delivery and maturity

The orchestration chat reports target boundary/revisions, worker assignments,
evidence inspected, artifacts created/refreshed, validation results,
untrusted/excluded docs, honest unknowns, and one next action — **with its
tier** (kernel §0), so the next session starts classified instead of cold.
Include the **growth completeness ledger** (`grow.completeness-contract`) —
every collection marked covered-to-evidence or absent-with-reason — so the
delivery proves totality instead of asserting it. Include growth metrics (the
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
