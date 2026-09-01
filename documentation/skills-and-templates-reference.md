# CYPRESS Seed — Skills and Templates Reference

This document describes the **skills** and **templates** shipped in the
CYPRESS seed. The seed is a project-agnostic multi-agent coding-assistant
system. It installs itself into a target project as a knowledge graph
under `docs/graph/`. The files documented here are the shippable source.

The reference has three parts:

- **Part A** — the 13 skills in `skills/*/SKILL.md`.
- **Part B** — the artifact templates in `templates/*.template.md` and the
  knowledge-graph contract in `templates/knowledge-graph/`.
- **Part C** — the prompt and brief templates in `templates/prompts/`.

All facts come from the source files. Where a source states a rule
literally, the quoted text is preserved. Each part cites its source paths.

A note on paths. Inside a skill or template, paths are written as they
appear **after installation** into a plant — for example
`docs/graph/skills/context-router.md` or
`docs/graph/templates/prompts/handback-payload.md`. In this seed repo the
same files live under `skills/`, `templates/`, and
`templates/prompts/`. The document uses the seed-repo path when it points
at a source file and the installed path when it quotes a cross-reference
inside a file.

---

# Part A — Skills

Source: `skills/<name>/SKILL.md` (13 files).

A **skill** is a *procedure*: how to do one thing well. It is not a role
(that is an agent) and not an artifact (that is a tool or template). Each
skill is a graph node of `kind: skill`, `tier: 2`, `origin: seed`. Every
skill frontmatter carries:

- `id` — the graph id, always `skill.<name>`.
- `owns` — the fact-keys this skill is the single home of.
- `requires` — nodes always loaded with it (its hard closure).
- `peers` — neighbour nodes, not loaded unless the task crosses into them.
- `load_when` — natural-language triggers the router matches a task against.
- `artifacts` — template files the skill fills or points at.
- `est_tokens` — the honest body-size estimate the router sums.

## Summary table — all 13 skills

| Skill | id | owns | requires | peers | est_tokens |
|---|---|---|---|---|---|
| adopt-existing | `skill.adopt-existing` | `adopt-existing.method`, `.refresh`, `.validation` | `protocol.grow` | `protocol.initialize`, `skill.knowledge-graph`, `skill.from-scratch-bootstrap` | 1600 |
| adr-writer | `skill.adr-writer` | `adr-writer.method`, `.reversibility`, `.numbering` | (none) | `skill.grill-planner`, `agent.architect` | 1400 |
| brainstorm-socratic | `skill.brainstorm-socratic` | `brainstorm-socratic.method` | (none) | `protocol.brainstorm`, `skill.spec-author` | 650 |
| context-router | `skill.context-router` | `rule.knowledge`, `context-router.method`, `.declaration` | `skill.knowledge-graph` | `skill.validate-knowledge` | 2100 |
| from-scratch-bootstrap | `skill.from-scratch-bootstrap` | `from-scratch-bootstrap.method` | `protocol.from-scratch` | `skill.brainstorm-socratic`, `skill.grill-planner` | 680 |
| grill-planner | `skill.grill-planner` | `grill-planner.method`, `.audit` | `protocol.grill` | `skill.spec-author` | 1300 |
| holistic-editing | `skill.holistic-editing` | `holistic-editing.method`, `.forbidden-moves` | (none) | `skill.context-router`, `protocol.test-first` | 1500 |
| knowledge-graph | `skill.knowledge-graph` | `knowledge-graph.method`, `.node-contract`, `.linter` | (none) | `skill.context-router`, `skill.library-wiki`, `skill.validate-knowledge` | 1700 |
| library-wiki | `skill.library-wiki` | `library-wiki.method`, `.version-pinning` | (none) | `skill.research-and-ingest`, `protocol.ingest-library` | 1200 |
| research-and-ingest | `skill.research-and-ingest` | `research-and-ingest.method`, `.source-ranking` | (none) | `skill.library-wiki`, `agent.research-scout` | 1200 |
| spec-author | `skill.spec-author` | `spec-author.method`, `.sign-off` | `protocol.specify` | `skill.test-first`, `skill.grill-planner` | 1250 |
| test-first | `skill.test-first` | `test-first.shaping`, `.level-selection` | `protocol.test-first` | `skill.spec-author` | 350 |
| validate-knowledge | `skill.validate-knowledge` | `validate-knowledge.method`, `.adversarial-questions` | (none) | `skill.knowledge-graph`, `skill.context-router` | 1050 |

Roles at a glance:

| Group | Skills |
|---|---|
| Knowledge graph | context-router, knowledge-graph, validate-knowledge |
| Dependency knowledge | library-wiki, research-and-ingest |
| Growing a project | adopt-existing, from-scratch-bootstrap |
| Planning and specs | brainstorm-socratic, grill-planner, spec-author |
| Writing and testing code | holistic-editing, test-first |
| Recording decisions | adr-writer |

---

## A.1 adopt-existing
Source: `skills/adopt-existing/SKILL.md`

**id:** `skill.adopt-existing` · **owns:** `adopt-existing.method`,
`adopt-existing.refresh`, `adopt-existing.validation` ·
**requires:** `protocol.grow` · **peers:** `protocol.initialize`,
`skill.knowledge-graph`, `skill.from-scratch-bootstrap`

**load_when:** adopt an existing codebase into the graph · initialize
cypress on a project that already has code · refresh the knowledge graph
after material code changes · onboard a multi-repo or monorepo project ·
build docs/graph for existing source.

**What it does.** Grows an existing single- or multi-repo codebase into
the unified `docs/graph/` knowledge plant, source-first. It supplies the
discovery and authoring discipline for `docs/graph/protocols/initialize.md`.

**Procedure.**

- **Invariants.** `docs/graph/` is the only maintained knowledge root.
  Executable source outranks prose. Make additive changes only — never
  delete or relocate competing AI configurations. Do not run builds or
  application test suites; extract their commands and label them
  `discovered, not executed`. Do not fetch, pull, switch, commit, or
  push. Observed behavior is not a spec; observed choices are not ADRs.
- **Scout pass.** Establish the governed boundary (one repo, monorepo, or
  umbrella of sibling repos). Record path, branch, HEAD, worktree state,
  role, manifests, stack. Inventory cheaply, skipping generated/vendor/
  cache/build output. Trace seven things: entry points; module boundaries;
  inbound/outbound edges; data and migrations; config, deployment,
  observability; tests, CI, prompts, evals; direct dependencies and their
  real usage. Return facts with exact paths and symbols. Record a
  non-English identifier/domain language as a graph fact.
- **Librarian pass.** Normalize evidence into single fact owners: set
  `ROOT_ID` and `KINDS` in `graph-lint.py`; author a root node and
  subsystem nodes; factor shared facts into their own nodes; give nodes
  concrete `load_when` and source paths; keep `requires` minimal and
  acyclic. Enrich leaf collections (`product/`, `architecture/`, `api/`,
  `data/`, `libraries/`, `sources/`, `prompts/`, `evaluations/`,
  `runbooks/`, `plans/`, `best-practices/`). Leave `specs/` and
  `decisions/` empty unless genuine intent records exist. When no test or
  gate infrastructure exists, emit explicit `absent (YYYY-MM-DD) — <reason>`
  rows in the verification runbook, never a blank. When a legacy doc source
  conflicts with the evidence graph, give the exclusion a real routable node
  (excluded as evidence; what supersedes it; a trust decision, not
  permission to delete).
- **Dependency wiki depth.** Index every direct dependency from manifests.
  Write a rich library page when a dependency is architecturally
  significant, security/ops critical, unusual, or cross-cutting.
- **Refreshing.** Treat graph prose as a read model: compare revisions,
  scout changed areas and blast radius, update the existing fact owner
  (never duplicate), preserve valid hand-authored context, supersede stale
  seed-owned claims only with cited contrary evidence. Never claim a full
  refresh when part of the source was unavailable.
- **Validation.** Run knowledge checks only (`graph-lint.py` and
  `--plan`). Verify links resolve, every Tier-3 leaf is reachable, no
  duplicate homes, routes are small, commands say if they ran. Use
  known-answer navigation questions plus an adversarial false-premise
  question. A wrong or bulk-read answer is a graph defect: **at most two
  fix-and-rerun rounds per defect**; a surviving defect is recorded as an
  honest unknown.
- **Handoff (stopping condition).** Adoption is DONE when validation passes
  within its rounds and open defects are recorded — not when every file has
  been read. End with the handback payload, reporting revisions, evidence,
  artifacts, validation, deliberately excluded docs (named by their
  exclusion node), unknowns, and one highest-leverage next action.

**When to use.** Onboarding CYPRESS onto a project that already has code,
or refreshing the graph after material code changes.

---

## A.2 adr-writer
Source: `skills/adr-writer/SKILL.md`

**id:** `skill.adr-writer` · **owns:** `adr-writer.method`,
`adr-writer.reversibility`, `adr-writer.numbering` · **requires:** (none) ·
**peers:** `skill.grill-planner`, `agent.architect`

**load_when:** write an ADR · record an architecture decision · why did we
choose this dependency or design · supersede an existing decision record ·
opening a one-way door decision.

**What it does.** Encodes the discipline of writing an Architecture
Decision Record (ADR). ADRs live in `docs/graph/decisions/` and record a
non-obvious technical choice — "why did we pick this?"

**Procedure.**

- **When to apply.** A new dependency, framework, language, or platform is
  chosen; a one-way door is opened; a service/module boundary is drawn; two
  specialists disagreed and the orchestrator picked; a post-mortem revealed
  an implicit decision; anyone asks "why did we do it this way?" and no ADR
  answers.
- **Numbering.** ADRs are `adr-NNNN-short-slug.md`, numbered monotonically.
  **Never reuse a number.** To replace a decision, write a new ADR and mark
  the old one `superseded by ADR-NNNN`. The index is
  `docs/graph/decisions/README.md`.
- **The four sections that matter.** Context (the constraint that makes
  "do nothing" not viable), Decision (one sentence), Consequences (concrete
  downstream changes and reversal cost), Alternatives considered (each
  rejected option with a concrete reason). The skill gives good/bad examples
  for each.
- **Reversibility tag.** Every ADR tags one of `reversible`, `expensive`,
  or `one-way`. `one-way` gets extra scrutiny.
- **Do not fabricate a decision.** An ADR records a choice that was made,
  not a reconstructed as-built fact. If a survey finds no genuine decisions,
  the index stays empty. Two decisions people forget: **"do nothing now" is
  a decision** (ratify the destination, defer timing behind a checkable
  trigger); and **the asymmetric cost of being wrong** is often the whole
  rationale.
- **Workflow.** Find the next number, read recent ADRs for tone, copy the
  template, fill Context first, then Decision, Consequences, Alternatives,
  Reversibility; cross-link spec/grill/wiki/sources; add a row to the index
  and to grill.md §6.
- **Anti-patterns.** ADR as design doc; a decision sentence that is three
  decisions; vague rejection reasons; no reversibility tag; no cross-links;
  rewriting an ADR after the fact (supersede, do not edit); an as-built
  observation dressed as a decision.

**When to use.** Any time a non-obvious technical choice needs its rationale
recorded on disk.

---

## A.3 brainstorm-socratic
Source: `skills/brainstorm-socratic/SKILL.md`

**id:** `skill.brainstorm-socratic` · **owns:**
`brainstorm-socratic.method` · **requires:** (none) · **peers:**
`protocol.brainstorm`, `skill.spec-author`

**load_when:** converge a vague or contested goal · socratic questioning
for requirements · brainstorm a new feature idea · the goal is too fuzzy to
specify.

**What it does.** The Socratic questioning technique that takes a vague goal
from "build me a thing" to precise, without designing UI, picking a
framework, or committing to architecture. Applied inside
`docs/graph/protocols/brainstorm.md`, which owns entry/exit and output map.

**Procedure.**

- **Ask the smallest set of questions that changes the design the most.**
  Limit: **one to three questions per turn, no more.**
- **Reflect every two answers** with a one-paragraph "I now believe X. Tell
  me where I'm wrong."
- **Hard cap at nine questions total.** If not converged, accept the gaps,
  mark each as an assumption in grill.md §12, write what you have, and move
  to `specify`.
- **Convergence checklist (8 points).** By the end you can write, without
  hand-waving: problem statement (one sentence), primary user (a specific
  role), first useful slice, success criteria (measurable, time horizon),
  non-goals (three to five), operating constraints, shaped options (two to
  four named approaches, each naming its tradeoff), risks and assumptions.
- **Anti-patterns.** Boiling the ocean; premature framework choice;
  designing the UI; skipping non-goals; pretending the user is "everyone";
  treating brainstorm as a milestone instead of a step.

**When to use.** When a goal is too fuzzy to specify and needs convergence.

---

## A.4 context-router
Source: `skills/context-router/SKILL.md`

**id:** `skill.context-router` · **owns:** `rule.knowledge`,
`context-router.method`, `context-router.declaration` · **requires:**
`skill.knowledge-graph` · **peers:** `skill.validate-knowledge`

**load_when:** what should I load for this task · resolve the minimal node
set before working · route a task through the knowledge graph · declare
loaded and skipped nodes · orient in a large codebase without bulk-reading ·
context budget for a change.

**What it does.** Resolves the minimum set of graph nodes a task needs
*before reading any source file*. This is the mechanism that keeps a large
or multi-repo codebase inside a context window. It owns the **knowledge
rule** and the traversal that makes it executable.

**The knowledge rule.** The project keeps one LLM-maintained knowledge
system at `docs/graph/`: Tier 1 routes, Tier 2 nodes own concise facts,
Tier 3 leaves hold source-backed depth. Load minimally and declare it. One
home per fact. Graph before code, ahead of memory. The graph compounds.
Never fabricate a fact, version, or URL — write "not recorded".

**The algorithm.**

1. **Classify the task in one sentence.** Four kinds route differently:
   Question → the node that owns the fact; Change → the owning subsystem
   node + required closure; Trace → every node on the path (the one kind
   that legitimately crosses `peers`); Plan → the plan-of-record + platform
   nodes.
2. **Resolve entry nodes** by matching `load_when` triggers; prefer the most
   specific. Watch for aliased names across layers — the Tier-1 router index
   must carry a **naming-divergence note** listing aliases.
3. **Take the required closure** — each entry node plus its transitive
   `requires`. It is small by construction.
4. **Do not take `peers`** unless the task crosses into them (a trace is the
   exception).
5. **Declare before you work** — print the resolved LOAD / NOT LOADED /
   Tier-3-on-demand set.
6. **Widen honestly, never silently.**

**Dry-run it.** The router is executable and must run inside every spawned
worker session. `python3 <graph-tools>/graph-lint.py --plan "<task>"`.
`--plan` is a keyword heuristic, not an oracle: trust your own reasoning
over it on traces, false-premise questions, policy questions, and
compound/multi-topic tasks.

**Stopping rules and cost discipline.** Stop when the closure is exhausted,
you can name the contract you must not break, or the next node is an
uncrossed peer. Retrieve progressively within scope. A change loads a
handful of nodes; a trace may load many on one path; never load two sibling
subsystem nodes "for comparison."

**When to use.** At the start of every non-trivial task, once a project has
a graph.

---

## A.5 from-scratch-bootstrap
Source: `skills/from-scratch-bootstrap/SKILL.md`

**id:** `skill.from-scratch-bootstrap` · **owns:**
`from-scratch-bootstrap.method` · **requires:** `protocol.from-scratch` ·
**peers:** `skill.brainstorm-socratic`, `skill.grill-planner`

**load_when:** start a brand-new project · bootstrap an empty repo · mkdir a
new project and cd into it · no grill.md exists yet · first day of a project.

**What it does.** Stands up a brand-new project from an empty repo through
the nine-phase `docs/graph/protocols/from-scratch.md` (brainstorm, skeleton,
grill, research, architecture, verification baseline, specify first slice,
test-first the first slice, deliver). The protocol owns the phase sequence;
this skill owns the honesty that keeps the first day from cutting corners.

**Procedure (the honesty rules).**

- Bootstrapping is inherently task-tier T3 — the full funnel is proportional,
  never discounted because the goal "sounds clear."
- The skeleton phase is done only when the host tool actually **loads** the
  machinery from its own directory (Claude Code → `.claude/` + `CLAUDE.md`;
  Prime Agent → `.prime/agent/` + `AGENTS.md`; opencode → `.opencode/` +
  `AGENTS.md`; Codex → `.codex/` + config; Copilot → `.github/` +
  `copilot-instructions.md`), not when files merely exist.
- The stack is chosen from verified research, never memory.
- The verification baseline passes on a clean checkout before any feature
  code.
- Specs before tests before code, always.

**Common failure modes.** Skipping the brainstorm; picking the stack from
memory; writing feature code before gates pass; skipping ADR-0001; skipping
SPEC-0001; writing code in Phase 7 instead of the spec; "we'll add tests
later" in Phase 6.

**When to use.** When a project does not exist yet and the repo is empty or
near-empty.

---

## A.6 grill-planner
Source: `skills/grill-planner/SKILL.md`

**id:** `skill.grill-planner` · **owns:** `grill-planner.method`,
`grill-planner.audit` · **requires:** `protocol.grill` · **peers:**
`skill.spec-author`

**load_when:** update the plan of record · author or revise grill.md · scope
the next increment · plan a new feature · grill.md drifted from the specs.

**What it does.** Authors, updates, and audits the project's plan-of-record
at `docs/graph/plans/grill.md` — the single living plan the next agent reads
first.

**Principles.**

- **Append, don't rewrite.** Sections 1–14 evolve; obsolete claims are
  struck through (or moved to history) with the new claim dated. §15 is the
  session-by-session changelog.
- **Section numbers are stable.** Do not renumber; tooling indexes by number.
- **Specs upstream, plan downstream.** Every §9 increment names at least one
  spec contract; every contract in the spec's §4 appears in an increment.
- **Increments are small and verifiable** — one RED-GREEN-REFACTOR cycle.
- **Structure earns its place at plan time** — an increment that adds a
  module/layer/interface names the single responsibility and the present
  variation that justifies any abstraction.
- **Cite, and mark what you haven't verified** with `[verify]` or
  "not recorded"; mark human-input values **do-not-guess** in §12.

**Workflow.** Creating grill.md fills §0–§4 then hands §5 to research-scout,
§6–§8 to architect, slices §9 with tester, §10–§11 to security/reliability,
open questions to §12, §13 done criteria from the spec's §9, §14 one next
step, and the §15 entry. Updating after an increment appends to §15, crosses
out completed §9 rows, records decision/risk/question changes, and updates
§14. Auditing checks every increment has a spec contract, every active spec
is referenced, every library has a wiki page, every ADR matches a §6 row,
every gate has a runbook entry, §14 names one action.

**Anti-patterns.** §14 with five bullets; §6 with no evidence column; §9
rows like "implement the feature"; vague risks in §11; silent rewrites.

**When to use.** Whenever a feature is planned, a plan is revised after
research or implementation, an increment is scoped, or grill.md needs a
consistency pass.

---

## A.7 holistic-editing
Source: `skills/holistic-editing/SKILL.md`

**id:** `skill.holistic-editing` · **owns:** `holistic-editing.method`,
`holistic-editing.forbidden-moves` · **requires:** (none) · **peers:**
`skill.context-router`, `protocol.test-first`

**load_when:** edit an existing file of any substance · refactor without
bolting on · review a diff for coherence · additive-only diff smells wrong ·
rename crossing a serialization or wire boundary.

**What it does.** The discipline for any change larger than a trivial
one-liner. The unit of work is the whole file or module, never the smallest
diff. **Prime directive:** a change is complete only when the file reads as
if the requirement had existed from the beginning; coherence outranks minimal
diffs. This does not license gold-plating — "minimum" still governs *new
behavior*.

**Mandatory process, in order.**

1. **Comprehend first** — state the file's responsibilities, structures, and
   conventions; load owning conventions via `context-router` if they live in
   a node.
2. **Locate the change architecturally.**
3. **Assess the ripple** — everything the change invalidates, duplicates, or
   makes obsolete.
4. **Integrate** — rewrite affected regions as a whole; deletion and
   consolidation are first-class outcomes.
5. **Output the whole revised unit**, never a fragment.

**Forbidden moves.** Appending functions at the bottom; `handleXNew`, `_v2`,
`Improved`, `Enhanced` wrappers or boolean flags that route around old logic;
special-casing when the general logic should change; leaving dead/duplicated
code "to be safe"; fixing the symptom at the call site when the defect is in
the abstraction; preserving a bad structure because the request didn't name
it.

**Scope rule.** Stay within the file/module and the direct consequences of
the request. Unrelated issues are filed as their own increment, not silently
fixed. If integration requires touching other files, say so and list them.

**Append-only exception.** Do NOT apply this skill to the plan-of-record
changelog, ADRs, or any changelog/audit log — those follow
supersede-don't-delete.

**Self-check and output format.** Run a self-check (read the whole file?
purely additive diff = red flag; anything now in two places?; dangling
imports?; do names/comments/docs still tell the truth?). Deliver: Read (2–4
sentences), Integration plan, Full revised code, Changelog (surfacing
anything removed or restructured beyond the literal request).

**When it does NOT apply.** Genuinely trivial changes (typo, comment, lint,
single config value). A **rename is the sharp exception** — the moment an
identifier crosses a serialization, wire, or process boundary it is an
unversioned contract change, never a trivial edit.

**When to use.** Before editing any file of substance; it governs how the
implementer, reviewer, and every specialist touch existing files.

---

## A.8 knowledge-graph
Source: `skills/knowledge-graph/SKILL.md`

**id:** `skill.knowledge-graph` · **owns:** `knowledge-graph.method`,
`knowledge-graph.node-contract`, `knowledge-graph.linter` · **requires:**
(none) · **peers:** `skill.context-router`, `skill.library-wiki`,
`skill.validate-knowledge`

**load_when:** author or edit a graph node · one home per fact violation ·
graph-lint fails · add or sharpen a load_when trigger · split an oversized
node · build the docs/graph structure.

**What it does.** Builds and maintains the tiered node graph the router
traverses. `context-router` reads the graph; this skill authors it.

**Tiers.** Tier 0 kernel (always loaded by host tool); Tier 1
`docs/graph/index.md` (router, every task first); Tier 2
`docs/graph/nodes/*.md` (one subject each, by traversal); Tier 3 leaf
collections (only when a Tier-2 node names the leaf and the task needs it).

**The node contract.** Every node begins with frontmatter; the full contract
lives in `docs/graph/templates/knowledge-graph/_schema.md`. The key that
carries the whole design is `owns` — each fact-key appears in exactly one
node's list, project-wide.

**The rules.**

1. **One home per fact.** Duplicated facts rot asymmetrically. When two nodes
   want a fact, extract it to a shared node and both `require` it.
2. **Version pins live in the library tier.**
3. **Cite; do not fabricate** — write "not recorded"/"not audited". Separate
   **observed** from **audited**; add an "observed absences / what this page
   is NOT" note where scope is partial.
4. **Bodies stay small** — under ~150 lines; `est_tokens` within 2× of the
   real body.
5. **Compound, don't restart** — add facts, sharp edges, and triggers as the
   project earns them. When a recorded fact is later found false, add a dated
   **Correction** note *alongside* the original, keeping the wrong reasoning.
6. **One graph, several depths** — leaf collections are not autonomous docs
   trees; a leaf without an owning-node edge is orphaned.
7. **Never inline secret material** — record a pointer (secret-manager path,
   env-var name, vault key), never a value or a masked copy.

**Node body shape.** what this is · what you must know · sharp edges · where
the code is · neighbours.

**The linter.** `graph-lint.py` enforces the dedup rule and more (frontmatter
parses; unique fact-keys; resolvable acyclic `requires`; reachability;
`libraries`/`artifacts` resolution; no version-pin leakage; `est_tokens`
within 2× and bodies under the line ceiling). Run before committing any graph
change. "A graph without a passing linter is a graph that has already started
to lie." A pass is DONE when the linter passes and each motivating fact has
one home — growth is demand-driven.

**When the graph is wrong.** The code wins on facts (fix the node in the same
change); the node wins on contracts (a code violation of a recorded contract
is a bug). Sharpen a missed `load_when` in the same commit.

**When to use.** Adopting a project, when a fact changes, when a node grows
too large, or when a task should have matched a node's triggers and didn't.

---

## A.9 library-wiki
Source: `skills/library-wiki/SKILL.md`

**id:** `skill.library-wiki` · **owns:** `library-wiki.method`,
`library-wiki.version-pinning` · **requires:** (none) · **peers:**
`skill.research-and-ingest`, `protocol.ingest-library`

**load_when:** add a new dependency · create or refresh a library wiki page ·
bump a pinned version · record a library pitfall or idiom · wiki page is
stale or missing.

**What it does.** Maintains a project-local, version-pinned wiki of every
direct dependency at `docs/graph/libraries/`. The wiki is the source of truth
consulted **before** writing code that touches a library, because agent
memory of library APIs is unreliable across versions.

**The discipline.**

1. **The wiki is local, not a mirror** — the narrow slice this project uses,
   plus project idioms, pitfalls, and history. The full upstream goes in
   `docs/graph/sources/`.
2. **Pin to a version** — "latest" is not a version; on upgrade, update the
   pin and add an §8 upgrade-path entry.
3. **Cite, don't paraphrase** — every claim cited in §10 with URL and date.
4. **Compound, don't restart** — add API names, idioms, and dated pitfalls
   only when they become real. A bare page is a valid start.
5. **Validate before publishing** — a page is not authoritative until a smoke
   test imports the pinned version, calls one or two §3 names, and passes in
   the project harness.

**Workflows.** Creating a page fills §0–§3, §10, adds an index row, writes and
runs the smoke test, then promotes. Refreshing diffs the upstream CHANGELOG,
updates the pin (§0), §3 API surface, §4 idioms, §6 deprecations, §7 security,
re-runs the smoke test, updates the index.

**Also create a `best-practices/` page** when a *concern* spans multiple
libraries.

**Anti-patterns.** Page as tutorial; page covers names we don't use; no
citations; theoretical pitfalls; page never updated after creation.

**When to use.** Adding, upgrading, or documenting an idiom/pitfall for a
dependency, or when a page is missing for code that already uses a library.

---

## A.10 research-and-ingest
Source: `skills/research-and-ingest/SKILL.md`

**id:** `skill.research-and-ingest` · **owns:** `research-and-ingest.method`,
`research-and-ingest.source-ranking` · **requires:** (none) · **peers:**
`skill.library-wiki`, `agent.research-scout`

**load_when:** research a library before adding it · fetch upstream
documentation · snapshot and normalize a source · refresh sources for a stale
wiki page · use context7 or deepwiki for docs.

**What it does.** Finds authoritative sources (web or documentation MCP
servers such as Context7/DeepWiki), snapshots them when allowed, normalizes
them into clean Markdown, and stages them for the library wiki. Output: raw
snapshots in `docs/graph/sources/raw/`, normalized summaries in
`docs/graph/sources/normalized/`, and a row in `docs/graph/sources/index.md`.

**Source ranking (preferred order).** 1) official upstream docs for the exact
version; 2) official upstream source code; 3) official blog/migration guides;
4) security advisories (CVE, CISA, OWASP); 5) well-maintained community
resources with current dates; 6) recent credible blog posts; 7) anything else,
marked `community`/`mirror`.

**Workflow per source.** Identify (authority, version coverage, date, license,
slug) → Fetch (host web-fetch or MCP server) → Snapshot when licensed (strip
nothing) → Normalize (clean Markdown with a metadata block) → Register (index
row) → Hand off to `docs-librarian`.

**Documentation MCP servers.** Prefer Context7, DeepWiki, or `llms.txt`
providers when configured; the local wiki stays authoritative.

**Disagreement handling.** Prefer the more recent official source; a security
advisory beats the docs; a persistent disagreement is recorded with versions
and an open question in grill.md §12.

**Source reconciliation (lightweight drift check).** Between full passes,
cheaply diff resolved versions against the wiki pins **without** re-fetching,
classifying each line: no mismatch / refresh before the next API-affecting
change / superseded — treat as historical. Distinct from a full research pass
and from `validate-knowledge`.

**Anti-patterns.** Ingesting paywalled content without OK; over-paraphrasing;
skipping the version pin; snapshotting forbidden content; ingesting from one
source per topic.

**When to use.** Adding/evaluating a library, refreshing stale sources, or
gathering current evidence for an ADR or spec.

---

## A.11 spec-author
Source: `skills/spec-author/SKILL.md`

**id:** `skill.spec-author` · **owns:** `spec-author.method`,
`spec-author.sign-off` · **requires:** `protocol.specify` · **peers:**
`skill.test-first`, `skill.grill-planner`

**load_when:** write a spec · define functional contracts · given when then
contract slugs · spec sign-off before code · code and spec disagree.

**What it does.** Writes an executable specification under
`docs/graph/specs/` that turns a clear goal into testable contracts. A spec is
**executable** when every functional contract maps to at least one test and
the test name names the contract.

**How to write each section.** §1 Summary (one paragraph, no marketing); §2
Scope (in/out, out-of-scope equally important); §3 user-facing behavior
(product, user's vocabulary); §4 functional contracts (architect — one
Given/When/Then per contract, `UPPER_SNAKE_CASE` slugs, one outcome each,
observable from outside); §5 non-functional (only binding constraints); §6
data shapes; §7 failure modes (architect + security adversarial cases); §8
examples (happy, edge, failure — real values); §9 acceptance criteria
(product, measurable, mapped to contracts); §10 test mapping (tester;
statuses `pending`/`red`/`green`/`skipped`); §11 open questions (a spec with
open questions stays `draft`).

**The sign-off rule.** A spec promotes from `draft` to `active` only with
product ✓, architect ✓, tester ✓ (testability review), and security ✓ (when
it touches auth, secrets, payments, uploads, external integrations, or AI
behaviors). Sign-off goes in §0. Once active, §4 slugs are enforced by
`python3 docs/graph/spec-lint.py` — the §3.1 gate; a new spec's contracts
report uncovered until `test-first` lands RED tests (that failing gate is the
spec working).

**Spec drift management.** When code and spec disagree, decide deliberately
(code right → edit spec + changelog + re-sign-off; spec right → file a bug +
regression test + fix code; both partial → back up to brainstorm/specify).

**Anti-patterns.** Spec as marketing; spec as implementation; no failure
modes; no examples; one giant contract; skipped sign-offs.

**When to use.** Whenever a feature, endpoint, job, function, or AI
interaction needs a contract the tester can encode and the implementer can
satisfy.

---

## A.12 test-first
Source: `skills/test-first/SKILL.md`

**id:** `skill.test-first` · **owns:** `test-first.shaping`,
`test-first.level-selection` · **requires:** `protocol.test-first` ·
**peers:** `skill.spec-author`

**load_when:** shape a new test · pick a test level · name a test after a spec
contract · unit vs integration vs e2e choice · one outcome per test.

**What it does.** The test-*shaping* technique. The RED → GREEN → REFACTOR →
COMMIT cycle and its gates live in `docs/graph/protocols/test-first.md`; this
skill owns the craft of shaping each test.

**Test level selection.** Pick the lowest level that exercises the behavior:

| Level | Use when |
|---|---|
| Unit | Pure logic, transformations, parsers, validators. |
| Integration | Crossing an adapter (DB, file, network, SDK, model). |
| Contract | API endpoints, structured outputs, message schemas. |
| End-to-end | Critical flows — one or two per flow, no more. |
| Golden / snapshot | Deterministic transforms, prompts, renderers. |
| Property-based | Algorithms where the property is clearer than examples. |
| Evaluation | LLM/VLM behavior, with rubrics and pass thresholds. |

**Test shape.** The name names the spec §4 contract slug (in the language's
convention); the body is Given/When/Then; one outcome per test.

**When to use.** When shaping any new test or choosing its level.

---

## A.13 validate-knowledge
Source: `skills/validate-knowledge/SKILL.md`

**id:** `skill.validate-knowledge` · **owns:** `validate-knowledge.method`,
`validate-knowledge.adversarial-questions` · **requires:** (none) · **peers:**
`skill.knowledge-graph`, `skill.context-router`

**load_when:** validate the knowledge graph after adoption · clean-context
test agent questions · false-premise adversarial question · prove the linter
catches a planted violation · is the graph trustworthy.

**What it does.** Proves a knowledge base actually works before it is trusted.
"Documentation you wrote is documentation you already believe" — so a context
that does not share your memory must be able to use it. Two methods.

**Method 1 — clean-context test agents.** Spawn agents with no prior context;
give them only the entry point (the kernel), not the answers. Ask questions
whose correct answer you know across the base (a fact lookup, a "how does X
work," a change-impact, a trace). Require them to declare what they loaded and
skipped (this tests routing, not just content). **Include adversarial
false-premise questions** ("Confirm the system uses <tech it does not use>") —
the highest-value test; a trustworthy base lets the agent reject the premise
with a citation. Grade and fix: every wrong answer, missed rejection, or
over-broad load is a defect in the base, not the agent.

**Method 2 — enforcement tests.** A rule is enforced only if you have seen it
fail. Plant a violation in a scratch copy (duplicate fact-key, broken edge,
misplaced version pin) and confirm the linter fails with the right message.
Prove drift detection with `--check` mode. Wire the passing linter into the
verification gates.

**Scope and cost.** Match effort to the base; prefer a few sharp adversarial
questions over many easy ones. Run read-only — the test agents' output is
evidence, not changes.

**What this catches that nothing else does.** A node correct but unreachable;
a base that reads well to its author but leaves a newcomer guessing; a
fabricated fact that survived authoring; a linter or drift-check that was
never exercised.

**When to use.** At the end of an adoption, after a large docs change, or
before relying on the graph to route work.

---

# Part B — Artifact and knowledge-graph templates

Sources: `templates/*.template.md` (10 files) and
`templates/knowledge-graph/` (5 files).

An **artifact template** is a blank form. An author copies it into a target
path under `docs/graph/` and fills every `<placeholder>`. Stable section
numbers must not be renumbered — agents and tooling index into them.
Templates are Tier-3 artifacts; a machinery node points at them via
`artifacts:`.

## Summary table — artifact templates

| Template | Produces (installed path) | Authored by | Used when |
|---|---|---|---|
| `adr.template.md` | `docs/graph/decisions/adr-NNNN-<slug>.md` | architect, orchestrator | every non-obvious technical decision (one ADR per decision) |
| `agent.template.md` | `agents/<name>.md` (host tool's agent dir) | orchestrator | roster has a gap; author a new specialist before delegating |
| `data-contract.template.md` | `docs/graph/data/data-contracts.md` (one section per dataset) | data-ml | adding/changing a dataset other code depends on |
| `grill.template.md` | `docs/graph/plans/grill.md` | orchestrator, grill-planner | once per project; updated continuously |
| `library-page.template.md` | `docs/graph/libraries/<name>.md` | docs-librarian, research-scout | every new dependency or version refresh |
| `prompt-contract.template.md` | `docs/graph/prompts/prompt-contracts/PROMPT-NNNN-<slug>.md` | data-ml, security | every active LLM/VLM prompt |
| `skill.template.md` | `docs/graph/skills/<name>.md` (projected to `.claude/skills/<name>/SKILL.md` and kin) | orchestrator (commission) or harvest | a repeatable project-specific procedure recurs |
| `spec.template.md` | `docs/graph/specs/SPEC-NNNN-<slug>.md` | product + architect + tester (joint) | every new behavior or behavior change |
| `threat-model.template.md` | `docs/graph/decisions/threat-model-<feature>.md` | security | a sensitive feature is being designed |
| `tool-page.template.md` | `docs/graph/tools/<tool-name>.md` | docs-librarian | a task produces a durable, reusable tool |

## Summary table — knowledge-graph contract files

| File | Installed path | Role |
|---|---|---|
| `_schema.md` | `docs/graph/_schema.md` | the node contract graph-lint.py enforces |
| `index.md` | `docs/graph/index.md` | Tier-1 router template |
| `node.template.md` | `docs/graph/nodes/<id>.md` | one blank node form |
| `graph-lint.py` | `docs/graph/graph-lint.py` | the graph linter and router dry-run |
| `spec-lint.py` | `docs/graph/spec-lint.py` | the spec-coverage gate |

---

## B.1 adr.template.md
Source: `templates/adr.template.md`

Produces `docs/graph/decisions/adr-NNNN-<slug>.md`. Structure:

- **Title** `# ADR-NNNN: <short slug>`.
- **Status** — `proposed` | `accepted` | `superseded by ADR-NNNN` |
  `deprecated`.
- **Date** — YYYY-MM-DD.
- **Context** — the situation that forces a decision, including the
  constraint that makes "do nothing" not viable; cross-links to grill.md and
  the spec.
- **Decision** — one sentence, optionally naming the central tradeoff.
- **Consequences** — new downstream constraints, reversal cost, effect on the
  verification plan, effect on the wiki.
- **Alternatives considered** — one paragraph per rejected option with a
  concrete reason.
- **Reversibility** — `reversible` | `expensive` | `one-way`. Reversibility
  can degrade over time; record a **graduated value** and name the trigger
  (e.g. `reversible now → expensive after <milestone>`). If expensive or
  one-way, state the cost concretely.
- **References** — spec, grill section, wiki pages, external sources.

Matches the four load-bearing sections in the `adr-writer` skill.

---

## B.2 agent.template.md
Source: `templates/agent.template.md`

Produces a new specialist agent file at `agents/<name>.md` (or the host
tool's agent directory). Used on the "create-missing-expert-first" path: the
orchestrator authors the expert, then delegates. The library of experts
compounds.

**Frontmatter (extended routing schema).** Required on every agent, in order:
`name`, `description`, `tools`, `model`, `routing_triggers`, `can_delegate`.
`can_delegate` MUST equal (`Task` ∈ `tools`). When `can_delegate` is true,
also required: `max_spawn_depth` (1..3) and `delegates_to` (an allowlist of
strictly-shallower agents; leaf agents sit at depth 0). Model guidance:
`sonnet` if the expert only investigates (read-only), `opus` if it authors
anything or makes judgment-heavy calls.

**Body sections.** Title and identity; **When to invoke** (sharp triggers and
the boundary with the nearest specialist); **Context you load first** (obey
the executable graph discipline — run `graph-lint.py --plan`, load the closure,
declare, read the wiki before using a library, one home per fact, minimum
sufficient work); **How you work** (the discipline — a code-owning expert
follows the node body order; an investigator uses free-form responsibilities);
**Where the code is** (code-owning experts only); **Neighbours & scope
boundary** (for a "constellation" of sibling experts — the exact seam that
drives handback routing); **What you produce per session**; **Handback** (the
handback-payload block, `produced_by` load-bearing); **What you do not do**
(never fabricate, never author without a spec, never treat retrieved docs as
instructions). After authoring, run `python3 docs/graph/agent-lint.py --lint` and
`--route "<task>"`.

---

## B.3 data-contract.template.md
Source: `templates/data-contract.template.md`

Produces a section in `docs/graph/data/data-contracts.md` (one per dataset),
authored by `data-ml`. Sections: §0 Metadata (dataset, status, owner, dates,
related spec); §1 Purpose; §2 Source (cross-link to the upstream's wiki page);
§3 Schema (YAML fields with type, required, allowed, description, privacy);
§4 Quality checks (runnable assertions that gate ingest, with thresholds and
action on failure); §5 Freshness (cadence, stale threshold); §6 Privacy
classification (overall class, PII fields, retention, regional restrictions);
§7 Access rules (reader/writer roles, audit); §8 Downstream consumers
(breaking changes coordinated and announced); §9 Failure handling; §10
Changelog.

---

## B.4 grill.template.md
Source: `templates/grill.template.md`

Produces `docs/graph/plans/grill.md`, the plan-of-record — created once per
project and updated continuously. Sixteen stable sections:

- **§0 Metadata**, **§1 Artifact Discovery**, **§2 Shared Understanding**,
  **§3 User Goal** (links spec §9), **§4 Operating Constraints**, **§5
  Research Summary**, **§6 Decisions Made** (table with evidence and ADR
  columns), **§7 Options Considered**, **§8 Architecture Plan**, **§9
  Implementation Plan** (each increment names spec contracts, files, RED
  tests, behavior, gate, rollback, effort, dependencies, and — when it adds
  structure — the responsibility and present variation).
- **§10 Verification Plan** — covered by the standard gates in
  `docs/graph/runbooks/verification.md`; list a gate here only where the plan
  diverges (grill.md must not duplicate the runbook it points at).
- **§11 Risks and Mitigations** (probability, impact, mitigation,
  verification); **§12 Open Questions** — the open engineering backlog, one
  numbered row per decision/finding with an owner and "Pinned by"; mark
  human-input rows **do-not-guess**; resolve in place (strike-through, dated),
  never by deleting.
- **§13 Done Criteria** (align with spec §9); **§14 Recommended Next Step**
  (one action); **§15 Changelog** (append-only).
- A trailing note: append, don't fork — a follow-up that grows past a
  changelog line becomes a new top-level section (§16, §17, …), never a
  separate document.

---

## B.5 library-page.template.md
Source: `templates/library-page.template.md`

Produces `docs/graph/libraries/<name>.md`. Fill §0–§3 on creation; §4–§12 are
demand-grown (add a section's body only when a real fact exists; a bare page
with an honest pin is a valid start; never write "none" rows to look
complete). Sections: §0 Pin (name, exact version, ecosystem, license,
maintenance signal, last-reviewed); §1 Role in this project; §2 Install (exact
command with pin); §3 Used API surface (only the names the codebase touches);
§4 Project idioms; §5 Pitfalls and sharp edges (dated); §6 Deprecations in
this version; §7 Security (advisory feed, known CVEs, watcher); §8 Upgrade
path; §9 Performance & cost notes; §10 References (cited, with retrieval
dates); §11 Alternatives considered (cross-link the ADR); §12 Changelog.

---

## B.6 prompt-contract.template.md
Source: `templates/prompt-contract.template.md`

Produces `docs/graph/prompts/prompt-contracts/PROMPT-NNNN-<slug>.md`, authored
by `data-ml` and `security`, for every active LLM/VLM prompt. Sections: §0
Metadata (ID, status, owner, date, version, related spec/eval); §1 Purpose;
§2 Model role; §3 Inputs (user, context sources, system); §4 Tool permissions
(tools + argument-validation rules that run before the tool fires); §5 Output
schema; §6 Validation rules (deterministic assertions on output); §7 Refusal
or escalation conditions (map to spec failure modes); §8 Privacy boundaries;
§9 Safety boundaries (adversarial inputs tested — prompt injection direct and
indirect, tool hijacking, exfiltration, jailbreaking, refusal evasion — and
controls); §10 Evaluation cases (reference `docs/graph/evaluations/`, minimum
coverage list); §11 Version history; §12 Prompt body (fenced, treated as
code — diffable, reviewable, testable).

---

## B.7 skill.template.md
Source: `templates/skill.template.md`

Produces a project-specific skill whose home is `docs/graph/skills/<name>.md`
(projected into `.claude/skills/<name>/SKILL.md` and kin), used
when a repeatable project-specific procedure recurs and no existing skill
covers it. The header comment states the taxonomy: if it is code that runs, it
is a tool; if it is who does the work, it is an agent; if it is the
disciplined sequence of steps, it is a skill. Frontmatter: `name`,
`description` (the procedure + exact triggers the router matches). Body: one
paragraph of purpose; "When to apply this skill" (concrete recurring
triggers); "The procedure" (disciplined steps, each naming its move and the
gate that proves it done — **compose existing protocols/skills by reference,
do not restate their rules**); "Anti-patterns"; "Reference files".

---

## B.8 spec.template.md
Source: `templates/spec.template.md`

Produces `docs/graph/specs/SPEC-NNNN-<slug>.md`, authored jointly by product +
architect + tester. Sections: §0 Metadata (identifier, status —
`draft`/`active`/`implemented`/`superseded`/`back-written` — owner, dates,
related grill/ADRs/wiki, supersedes/superseded-by, and the sign-off line
`product [ ] · architect [ ] · tester [ ] · security [ ]`); §1 Summary; §2
Scope (in/out); §3 User-facing behavior (product); §4 Functional contracts
(architect; one Given/When/Then per contract, stable `UPPER_SNAKE_SLUG`s the
tests reuse); §5 Non-functional requirements (only the binding ones); §6 Data
shapes (language-agnostic YAML, cross-link native schemas); §7 Failure modes
(architect + security adversarial); §8 Examples (happy, edge, failure — real
values); §9 Acceptance criteria (product, measurable, mapped to contracts);
§10 Test mapping (tester; contract → test name → file → level → status); §11
Open questions (a spec with open questions is still `draft`); §12 Changelog.
The contract slugs in §4 are exactly what `spec-lint.py` scans for in tests.

---

## B.9 threat-model.template.md
Source: `templates/threat-model.template.md`

Produces `docs/graph/decisions/threat-model-<feature>.md`, authored by
`security` when a sensitive feature is designed. Sections: §0 Metadata; §1
Assets (tangible and intangible); §2 Actors (legitimate and adversarial, each
with capabilities and goals); §3 Trust boundaries (where data crosses an
authority change — including retrieved document → model prompt); §4 Entry
points; §5 Data flows (cross-link spec §6); §6 Abuse cases (including
AI-specific: prompt injection, tool hijacking, exfiltration, hallucinated
authority, adversarial vision/audio inputs); §7 Security controls (each names
the spec contract or test that proves it); §8 Privacy controls; §9 Detection
and logging; §10 Residual risk; §11 Verification plan (tests, CI scans,
red-team eval cases, manual checkpoints); §12 Changelog.

---

## B.10 tool-page.template.md
Source: `templates/tool-page.template.md`

Produces `docs/graph/tools/<tool-name>.md`, authored by `docs-librarian`, used
by `toolcraft` (kernel §3.8) whenever a task produces a durable, reusable
tool worth cataloging. Reached from the owning node via an `artifacts:` edge
and registered in `docs/graph/tools/index.md`. Sections: §0 Identity (name,
path, language/runtime, owner, stability, last-reviewed); §1 What it does; §2
Interface & invocation (the stable public contract — inputs, outputs,
preconditions; changing it is a versioned change); §3 Where the code lives
(entry point, supporting files, dependencies); §4 When to use it (and when
not) plus idioms; §5 Pitfalls and sharp edges (dated); §6 Tests that cover it
("A tool with no test is not durable — add one before cataloging"); §7
References & neighbours (owning node, related tools, ADR, sources, seed
corpus); §8 Changelog.

---

## B.11 The knowledge-graph node contract — `_schema.md`
Source: `templates/knowledge-graph/_schema.md` (installs to `docs/graph/_schema.md`)

`_schema.md` defines the shape of every node under `docs/graph/nodes/`. It is
the contract `graph-lint.py` enforces; the human-readable rules live here, the
machine-checked ones in the linter.

**Why a graph and not a folder.** A large or multi-repo codebase does not fit
in a context window, and a flat `docs/` tree gives no way to decide what *not*
to read. The graph makes loading a **traversal with a stopping rule**: nodes
are the unit of loading (one node ≈ one subject); `requires:` edges are the
closure you must load transitively; `peers:` edges are subjects you must not
load unless the task crosses into them; tiers bound the depth.

**Three axes named "tier".** The document warns that "tier" is used on three
axes: the graph **load-tier** (the node `tier:` field — this document's
subject), the **task tier** (T0–T3 risk classification in kernel §0), and the
**model class** (sonnet/opus). Only the risk axis is written `T0–T3`.

**Load-tiers.** Tier 0 kernel (always, by host tool — a bootstrap only); Tier
1 `docs/graph/index.md` (every task first); Tier 2 project nodes
`docs/graph/nodes/*.md` and machinery nodes
`docs/graph/{protocols,skills,agents,method}/*.md` (by traversal); Tier 3 the
leaf collections under `docs/graph/` (only when a Tier-2 node names it and the
task needs it).

**Machinery nodes.** The seed's method surface — protocols, skills, agents,
method nodes — lives inside the graph as Tier-2 nodes of kind
`protocol`/`skill`/`agent`/`method`, each carrying `origin: seed` (graft's
ownership marker). They route through the same schema and load progressively.
Two project-fact checks do NOT apply to them (version-pin leakage; the
~150-line body ceiling); their filenames keep natural names, and the id's
`<name>` part must equal the filename stem with any `NN-` ordering prefix
stripped.

**Frontmatter.** A small YAML subset: `key: scalar`, or `key:` then
two-space-indented `  - item` lines — no nested maps, no inline `[a, b]`
lists. Keys: `id`, `tier`, `kind`, `title`, `repo` (optional), `owns`,
`requires`, `peers`, `libraries` (optional), `artifacts` (optional),
`load_when`, `est_tokens`.

**Node kinds.** Each project sets its own small set in `graph-lint.py`
(`KINDS`). A common starting set: `root`, `subsystem`, `stack`, `platform`,
`data`, `crosscut`, `domain`. Four kinds are reserved for machinery and always
present: `protocol`, `skill`, `agent`, `method`. An id's prefix must match its
kind (`subsystem.orders`), except the single root node whose id *is* the root
id.

**Key semantics.** `owns` is the dedup mechanism — each fact-key appears in
exactly one node's list project-wide. `requires` is a hard, minimal, acyclic
dependency. `peers` is soft adjacency (printed as "not loaded"). `artifacts`
are progressive-discovery edges to leaves (relative to `docs/graph/`, must
resolve); `libraries` is the specialized wiki edge. `load_when` is what the
router matches. `est_tokens` is an honest body estimate.

**Body order.** what this is (2–3 sentences) · what you must know · sharp
edges (dated) · where the code is (concrete paths) · neighbours. Under ~150
lines; a longer node is two nodes.

**The eleven linter rules (as stated in `_schema.md`).**

1. Frontmatter parses and has every required key.
2. `id` is unique and matches the filename (`<id>.md`).
3. `id` prefix matches `kind` (root node excepted).
4. Every fact-key in `owns` is unique across all nodes.
5. Every id in `requires`/`peers` resolves to a real node.
6. `requires` is acyclic.
7. Every node is reachable from the root by edges, or listed in `index.md`.
8. Every id in `libraries` has a page in `docs/graph/libraries/`.
9. Every path in `artifacts` resolves beneath `docs/graph/`.
10. Version pins do not appear in a node body unless it owns a `*.versions`
    fact-key.
11. `est_tokens` is within 2× of the measured body; body under the line
    ceiling.

**Anti-patterns.** A node that restates a version; a node that `requires`
everything; a subsystem node that explains the language/framework (that is a
`stack.*` node); a node with no `owns` (a link farm); growing a node instead
of splitting it; filling an unknown with a guess.

---

## B.12 The router template — `index.md`
Source: `templates/knowledge-graph/index.md` (installs to `docs/graph/index.md`)

Tier 1 — the router every task opens first, and the only index. Match the task
against the triggers, load the entry node plus its `requires:` closure, and do
not load `peers:` unless the task crosses into them. The traversal is
specified in `skills/context-router.md` and is executable via
`graph-lint.py --plan "<task>"`. Blocks:

- **Start here by task shape** — a table mapping common task phrasings to the
  entry node (root, roster, subsystem, data, auth, secrets, testing, deploy,
  config).
- **Method — how we work** — the pre-filled machinery routing table (task
  state → machinery entry node): `method.tiers`, `method.delegation`, the
  protocols (brainstorm → specify → grill → test-first → ingest-library →
  verify → recover → canonize → deliver → grow/initialize → from-scratch), the
  graph skills, the posture method nodes, and the user-sovereign
  `protocol.harvest` / `protocol.graft` (never automatic). It also lists the
  full specialist-agent roster and the situational skills.
- **The node table** — grouped by tier/kind (roots; stacks/platform/data/
  cross-cutting/domain; subsystems), with honest `~tokens` that sum to the
  budget.
- **Cost discipline** and **When the graph is wrong** — the same rules
  `context-router` and `knowledge-graph` own, restated at the router.

---

## B.13 The node form — `node.template.md`
Source: `templates/knowledge-graph/node.template.md` (installs to `docs/graph/nodes/<id>.md`)

A single blank node. Its comment tells the author to copy an existing node in
preference to this form when peers of the same kind exist. Frontmatter matches
`_schema.md`. Body sections in order: **What this is** (2–3 sentences),
**What you must know** (the owned facts, terse; link facts other nodes own),
**Sharp edges** (dated), **Where the code is** (concrete paths), **Neighbours**
(one line per peer: why it exists and when to cross).

---

## B.14 The graph linter — `graph-lint.py`
Source: `templates/knowledge-graph/graph-lint.py` (installs to `docs/graph/graph-lint.py`)

A dependency-free Python 3 script — "it must run on a bare python3." On
install/adoption it is copied next to `index.md` and the `nodes/` directory
and its PROJECT CONFIG block is set to the project's kinds and root id.

**Usage.**

```sh
python3 graph-lint.py                 # lint; exit 1 on error
python3 graph-lint.py --graph         # print the requires-DAG
python3 graph-lint.py --plan "TASK"   # dry-run the context router
```

**PROJECT CONFIG.** `ROOT_ID` (default `"root"`); `KINDS` (the set of node
kinds, default the common starting set plus the four machinery kinds);
`KIND_PREFIX` (optional map letting a verbose kind live in a terse id
namespace, default `{}`); `MACHINERY_DIRS` (maps `protocols`→`protocol`,
`skills`→`skill`, `agents`→`agent`, `method`→`method`).

**What it loads.** All `*.md` under `nodes/` plus the machinery directories,
skipping files starting with `_` and `index.md`. It parses the small YAML
frontmatter subset with a hand-written parser (no PyYAML dependency).

**The checks (functions).**

- `check_schema` — required keys present (`id`, `tier`, `kind`, `title`,
  `owns`, `requires`, `load_when`, `est_tokens`; an agent node with
  `routing_triggers` is exempt from needing `load_when`); list keys are lists;
  `tier` is 2; `kind` is in `KINDS`; the id prefix matches the kind (via
  `kind_prefix`); machinery kind matches its directory and its id name part
  equals the stem with any `NN-` prefix stripped; a project node's filename
  equals its id; every node `owns` at least one fact.
- `check_unique_ownership` — the dedup invariant: a fact-key owned by two
  nodes is an error ("extract to a shared node").
- `check_edges` — every `requires`/`peers` id resolves; no self-edge.
- `check_acyclic` — a DFS three-colour cycle check on `requires`.
- `check_reachability` — reachable from `ROOT_ID` by edges, or listed in
  `index.md`. A pre-growth grace lets a fresh install carry only machinery
  nodes; the root becomes mandatory the moment the first project node lands.
- `check_libraries` — every `libraries` id has a page under `libraries/`.
- `check_artifacts` — every `artifacts` path resolves beneath `docs/graph/`
  and cannot escape it.
- `check_version_leakage` — a version pin in a node body (outside inline/
  fenced code) is an error unless the node owns a `*.version(s)` key;
  machinery nodes are exempt.
- `check_budget` — `est_tokens` within 2× of the measured body (words ×
  1.35); a project node body over 170 newline lines is over the ~150-line
  ceiling; machinery nodes are exempt from the ceiling.

**The router dry-run (`resolve` / `--plan`).** Mirrors the `context-router`
traversal. It extracts task terms (keeping paths whole and split), scores each
node by IDF-weighted token overlap between the task and the node's
name/title/`repo` (weight ×2) and its `load_when`/`routing_triggers`, using
whole-token matching only (an exact hit outranks a morphological fold; never a
substring). It seeds from the top-ranked nodes above a floor, expands the
`requires` closure, and reports the loaded set (with summed `est_tokens`) plus
the skipped `peers`. Stopwords and a 6-char stem-fold reduce noise. The linter
prints `graph-lint: OK — N nodes, ~T tokens if fully loaded` and reminds that
"no task should ever load them all."

---

## B.15 The spec-coverage gate — `spec-lint.py`
Source: `templates/knowledge-graph/spec-lint.py` (installs to `docs/graph/spec-lint.py`)

A dependency-free Python 3 gate that makes "specs are executable" (kernel
§3.1) mechanical: every functional contract must map to at least one test, and
tests reuse the contract's stable `UPPER_SNAKE_SLUG`.

**Usage.**

```sh
python3 docs/graph/spec-lint.py           # gate: exit 1 on uncovered
python3 docs/graph/spec-lint.py --list    # dump contract -> tests map
python3 docs/graph/spec-lint.py --warn    # report but always exit 0
```

**Configuration.** `TEST_GLOBS` (the project's test file patterns) and
`LIVE_STATUSES` = `{"active", "implemented"}`.

**What it does.** It scans `docs/graph/specs/SPEC-*.md`, reads each spec's
`**Status:**`, and for live specs collects every `### Contract: SLUG` slug.
Then it scans the test files (skipping `.git`, `node_modules`, `.venv`, etc.,
and the specs dir itself) for each slug. Behaviors:

- Every active/implemented contract must appear in ≥1 test file, or the gate
  **FAILs**.
- A slug in tests but in no live spec is drift → a **WARN**.
- Live contracts + **zero** matching test files is a "green lie" — it FAILs
  loudly, never a vacuous pass ("A coverage check over an empty set is a green
  lie; fix TEST_GLOBS or write the tests.").
- No live contracts at all → PASS ("no live contracts to cover").

This is the §3.1 gate a new spec's contracts fail until `test-first` lands the
RED tests — the failing gate is the spec working, not a defect.

---

# Part C — Prompt and brief templates

Source: `templates/prompts/*.md` (9 files).

These are the **delegation briefs** — the runtime prompts an orchestrator or a
growth run hands to a spawned worker. Because hooks do not reach a subagent's
clean context, the brief is the only enforcement that crosses the delegation
boundary. Several briefs embed the same canonical **graph-session bootstrap**
block verbatim; every static seed file references it instead of paraphrasing.

## Summary table — prompt/brief templates

| Brief | Role in delegation | Model class | Producer / consumer |
|---|---|---|---|
| `graph-session-bootstrap.md` | canonical GRAPH DISCIPLINE block every brief embeds verbatim | — | the one home of the discipline |
| `handback-payload.md` | the block a worker returns at every hand-back | — | every spawned worker |
| `growth-scout-brief.md` | dispatch one read-only scout at one boundary | sonnet | producer of the evidence ledger |
| `growth-author-brief.md` | dispatch an author to turn a ledger into a deliverable | opus | consumer of the evidence ledger |
| `growth-evidence-ledger.md` | canonical schema passed scout → author | — | scout writes, author reads |
| `growth-completeness-ledger.md` | canonical schema proving growth reached full depth | — | the orchestration chat fills it |
| `node-authoring-brief.md` | delegate authoring of graph nodes with linter rules as hard constraints | opus | node author |
| `investigation-brief.md` | delegate a read-only fact-gathering investigation | sonnet | investigator (leaf) |
| `clean-context-validation-brief.md` | spawn a fresh agent to validate a knowledge base | opus | validator (read-only leaf) |

---

## C.1 graph-session-bootstrap.md
Source: `templates/prompts/graph-session-bootstrap.md`

**The canonical home of the graph-session discipline.** Every delegation brief
embeds the block below verbatim; every other seed file references this file.
The embedded block (`GRAPH DISCIPLINE — execute before reading any source`)
has six numbered steps:

1. Run `python3 docs/graph/graph-lint.py --plan "{{exact delegated task}}"`
   and include the command and output as **graph-route evidence** (context
   routing — not the `route_evidence` field).
2. Load only the reported nodes plus their `requires:` closure.
3. Declare what you loaded, what you skipped, and any later widening (with the
   reason).
4. One home per fact — link, never duplicate; the graph outranks memory; write
   "not recorded" instead of fabricating.
5. Minimum sufficient work — smallest sufficient evidence, cheapest reliable
   method; return findings, not raw dumps.
6. If the graph has no nodes yet (bootstrap pass), report the failed probe and
   stay inside the brief's exact paths.

**Companion requirements** every brief also carries: **routing evidence**
(paste the `agent-lint --route` ranked line and confidence band; the worker
echoes it back as `route_evidence`) and **handback** (the worker ends with the
handback-payload block).

**Why embedding, not referencing, at the boundary.** Subagents start with a
clean context and no hooks fire for them; a reference the worker may never
resolve is not enforcement. This is the one deliberate exception to
one-home-per-rule: the runtime brief embeds; every static seed file references.

---

## C.2 handback-payload.md
Source: `templates/prompts/handback-payload.md`

Used once per spawn, at the moment a worker returns control — delegating or
leaf, and on all three endings (complete, blocked-out-of-domain, failed). Not
per tool call. This block is the only reliable carrier across the subagent
boundary. The payload fields:

- `produced_by` — this agent's name. **Load-bearing:** a unit of work with no
  `produced_by` is a deliver-time BLOCK, not a pass (fail-closed).
- `status` — `complete` | `blocked-out-of-domain` | `failed`.
- `failure_class` — only when failed: `transient` | `deterministic` |
  `capability` | `ambiguity` | `systemic` | `unregistered` (feeds `recover`).
- `in_domain_work_done` — what this agent legitimately did, with paths.
- `out_of_domain_needed` — work this agent must not do itself, or "none".
- `route_evidence` — the `agent-lint --route` line that selected THIS agent
  (echoed from the brief) — about YOU, not the next hop, and not graph-lint
  `--plan` output.
- `harness_override` — only for a role-emulated specialist.
- `recommended_next` — an addressable agent + protocol/step, or "none —
  session ends here". Never only a protocol name.
- `next_route_evidence` — the routing line supporting `recommended_next`.
- `gates` — commands run + results, or "none".
- `tools_built` — durable reusable tools (name + path + invocation), feeding
  the §3.8 close-out; leaving one out is a silent capability leak.
- `skills_built` — repeatable multi-step procedures a future session will walk
  again, feeding the same close-out; the procedure sibling of `tools_built`.

Rules make explicit: a **leaf worker recommends, it does not spawn** (no `Task`
tool); a **delegator that stops still fills this in**; `failure_class` feeds
`recover` and what survived is preserved in `in_domain_work_done` so the next
attempt starts from the frontier.

---

## C.3 growth-scout-brief.md
Source: `templates/prompts/growth-scout-brief.md`

**Model class: sonnet.** Dispatches one read-only `growth-scout` at one real
subsystem or repository boundary. The scout is the producer end of a contract:
authors build every growth deliverable from its ledger, so what the scout fails
to collect, the authors cannot write. Its collection target is the **growth
evidence ledger** schema — feedstock for graph nodes/wiki, spec candidates, ADR
candidates, project-specific specialist agents, and runbooks.

**Rules (stated verbatim to the sub-agent).** Execute the graph first (the
embedded GRAPH DISCIPLINE block). Executable source is the truth — READMEs and
prior docs are clues; every claim carries `path:line` + a symbol; where source
and prose disagree, believe the source. Fill the ledger schema, do not
improvise a format; write it to the plant's gitignored seed-organ scratch
`.cypress/growth/<boundary-slug>.ledger.md`, never to `docs/graph/`. Stay
inside your boundary (cross-boundary facts go in the ledger's notes for the
orchestrator). Do NOT bulk-read. Say `not recorded` rather than guessing;
`none found` for an empty section is a fact. Read-only (`Bash` only for
`ls`/`git log`/`wc`; no fetch/pull/commit/push). Cite the router. Return the
ledger path, a one-line coverage note per section, and the handback payload
(`produced_by: growth-scout`); as a read-only leaf, name the next specialist
and STOP.

---

## C.4 growth-author-brief.md
Source: `templates/prompts/growth-author-brief.md`

**Model class: opus.** Dispatches an author that turns a completed growth
evidence ledger into a specific deliverable. Its **evidence is already
gathered** — it builds from the ledger, not from a fresh reading of source.

**Feedstock.** Read the ledger(s) at `.cypress/growth/{{boundary-slug}}.ledger.md`
plus `docs/graph/_schema.md` and an exemplar. Rules: build only on cited
claims (a fact the ledger marks `not recorded` stays so); route ledger section
→ deliverable (graph node → §1–§6, §11; `specs/` → §7; ADR → §8; specialist
agent → §9; runbooks → §10 labeled "discovered, not executed"; `libraries/` →
§5); one home per fact; smallest sufficient artifact (growth validation audits
over-growth exactly as it audits gaps).

**Rules (verbatim).** Execute the graph first (the embedded GRAPH DISCIPLINE
block). Obey the per-deliverable contract — for a graph node, embed the HARD
RULES from `node-authoring-brief.md`; for a spec/ADR/library/agent, follow the
matching template. Write only your exclusive scope (exact file paths; knowledge
writes under `docs/graph/`; no touching application code, manifests, CI, or
Git). Never invent. Cite the router. **Return** the file paths written, the
ledger claims each rests on, any ledger fact deliberately omitted, linter
confirmation, and the handback payload; spawn only from the `delegates_to`
allowlist within the depth cap, else STOP.

---

## C.5 growth-evidence-ledger.md
Source: `templates/prompts/growth-evidence-ledger.md`

**The canonical schema of the growth evidence ledger** — the one structured
artifact that passes between a growth-scout (producer) and a growth author
(consumer). One boundary, one ledger. Every claim is a fact **from executable
source**, anchored to `path:line` and a symbol; prose is clues until
corroborated; a fact that cannot be established is written `not recorded`.

**A seed organ, not a plant organ.** It is growth-time feedstock, transient to
a grow/adopt run, written to the plant's gitignored
`.cypress/growth/<boundary-slug>.ledger.md`, never to `docs/graph/`. After
delivery the plant keeps `docs/graph` and may discard `.cypress/growth/`.

**Sections (each names the downstream deliverable it feeds).** §0 Boundary &
provenance → root/subsystem node, changelog; §1 Structure & entry points →
architecture nodes; §2 Capabilities, actors & flows → product nodes; §3
Contracts (api/messages/jobs) → api nodes; §4 Data & entities → data nodes +
data-contracts (put version-pinned facts here with their lockfile source); §5
Dependencies → libraries index + rich pages (read pins from the tree, never
memory); §6 Prompts & evaluations → prompts + evaluations nodes; §7 Spec-worthy
behaviors → specs feedstock (the §3.1 gate; a candidate list, not an authored
spec); §8 ADR-worthy decisions → decisions feedstock (only decisions visible in
source; unknown rationale `not recorded`); §9 Specialist-agent signals →
project-specific expert agents; §10 Operational evidence → runbooks +
verification (**discovered, not executed**); §11 Sharp edges → wherever the
owning fact lives; §12 Uncertainties & cross-boundary notes. The scout ends
with the handback payload naming the ledger file.

---

## C.6 growth-completeness-ledger.md
Source: `templates/prompts/growth-completeness-ledger.md`

**The canonical schema of the growth completeness ledger** — the artifact that
makes `protocols/grow.md`'s completeness contract mechanical instead of a
matter of judgment. **Who fills it:** the orchestration chat, not a spawned
worker. It is the proof, produced before growth is declared done and carried
in the delivery block, that growth reached full depth. **Where it lives:** a
seed organ at `.cypress/growth/completeness-ledger.md`, never `docs/graph/`.

**One row per knowledge collection**, with status exactly one of:

- **COVERED** — authored to the full depth the evidence supports; give the
  node/leaf count and the strongest source paths.
- **ABSENT** — the source genuinely has no such evidence; give the reason and
  the paths searched (a real absence is a fact).
- **UNKNOWN** — a named blocker prevents coverage; the only legitimate way a
  collection stays uncovered, and it ships reported, never silent.

"ran out of context", "seemed enough", "templates are present", and "common
cases done" are NOT statuses — they are the failure the contract forbids. Rows
cover: the root node, subsystem/capability nodes, stack/cross-cutting nodes,
the Tier-1 router, `product/`, `architecture/`, `api/`, `data/`, `libraries/`,
`sources/`, `legal/` (if in scope), `prompts/`, `evaluations/`,
`runbooks/verification.md`, `plans/grill.md`, `specs/`, `decisions/`,
`best-practices/`, `changelog.md`, and project-specific agent(s). Growth is
done only when every row is COVERED or ABSENT (or a named UNKNOWN), Phase 6
independent validation passes against the graph, and the maturity test at the
foot of `protocols/grow.md` is met — against the graph, never the file tree.

---

## C.7 node-authoring-brief.md
Source: `templates/prompts/node-authoring-brief.md`

**Model class: opus.** Delegates authoring of one or more knowledge-graph nodes
(or wiki pages) with the linter's rules stated as hard constraints so the
output passes on the first try. The author reads `docs/graph/_schema.md` first
and an existing node as a style exemplar, executes the embedded GRAPH
DISCIPLINE block, cites the router, and writes exactly the listed file paths
(filename MUST equal the id + `.md`).

**HARD RULES (a linter enforces these).**

1. Frontmatter is the tiny YAML subset only (no nested maps, no inline lists).
2. Required keys in order: `id`, `tier`, `kind`, `title`, `repo` (optional),
   `owns`, `requires`, `peers`, `libraries` (may be empty), `artifacts` (may be
   empty), `load_when`, `est_tokens`; `tier: 2`.
3. No version numbers in the body (outside inline/fenced code) — versions live
   in `docs/graph/libraries/`; link instead.
4. `owns:` fact-keys are prefixed with the node's short name and unique across
   the whole graph.
5. `requires:` only ids from the allowed set — minimal (2–4); `peers:` only
   from the allowed set.
6. Body ≤ 150 lines, sections in order (What this is; What you must know;
   Sharp edges; Where the code is; Neighbours).
7. `est_tokens` ≈ 1.35 × body word count — honest; the linter fails if off by
   >2×.
8. Every `artifacts:` path is relative to `docs/graph/`, resolves there, and
   points to source-backed depth owned by this node.

A **FACTS** block supplies verbatim investigation facts; a fact not supplied
means the node says "not recorded" — the sub-agent does not fill gaps from
memory. **Return** the file paths written, any fact omitted for length, and
linter confirmation.

---

## C.8 investigation-brief.md
Source: `templates/prompts/investigation-brief.md`

**Model class: sonnet.** Delegates a read-only investigation of a subsystem to
gather facts for a spec, a graph node, or a plan — facts only, no authoring, no
judgment-heavy design. The sub-agent executes the embedded GRAPH DISCIPLINE
block, cites the router (and says so if routed at LOW/NONE confidence), and
ends with the handback payload — as a read-only leaf it names the next
specialist and STOPs.

**Rules.** Do NOT read every file — sample intelligently (prioritized
manifests, entry points, config); confirm a path with `ls`/`grep` before
reading. Report facts with evidence — every claim carries a concrete file path
(and line where it matters) and an exact value, not a paraphrase. Say
"not found" rather than guessing. Read-only. Be terse (bullets and tables — it
feeds a system prompt or a node).

**Report these concretely.** 1) structure (layout, abstractions,
conventions); 2) versions/pins/config other work depends on; 3) external edges
(what it calls, what calls it, over what protocol); 4) data it owns (entities,
constraints, enums); 5) tests, gates, CI (what exists and what is absent); 6)
anything surprising or non-standard. **Return** a structured terse report,
citing paths, flagging every "not found", and anything omitted for length.

---

## C.9 clean-context-validation-brief.md
Source: `templates/prompts/clean-context-validation-brief.md`

**Model class: opus.** Spawns a **fresh** agent (not a fork of yourself — a
fork inherits your assumptions and passes a base a stranger would fail) to
validate a knowledge base by answering known-answer and adversarial questions
using only the docs. The caller grades the answers against ground truth it
already knows. This is the runtime form of the `validate-knowledge` skill's
Method 1.

**Strict rules.** Read-only (do not create, edit, or delete anything). Before
answering each question, run the `--plan` router command with that exact
question and compare the route output with the nodes actually loaded. Answer by
loading the **minimum** context — do NOT bulk-read the source tree. For each
question, first declare the exact nodes/pages loaded and skipped, then answer.
If the base can't answer without opening source, say so — that is a finding.
Cite the router; end with the handback payload naming the specialist who should
fix the defects (a read-only leaf names them and STOPs).

**Questions.** A mix — a fact lookup, a change-impact ("what must I check
before changing X?"), a trace across subsystems, and at least one
**adversarial false-premise** question whose correct answer is to reject the
premise with a citation. **Then a system assessment:** did the kernel orient
you and point to the router/graph? how many nodes did you load? did you ever
open a source file or bulk-read? for each adversarial question, could the base
let you reject the false premise? did any node contradict another or point
somewhere that didn't deliver? did `--plan` agree with your hand-picked sets?
could a newcomer reproduce your answers from the base alone? "Be blunt. A
negative finding is worth more than praise."

---

*End of reference. Sources: `skills/*/SKILL.md`, `templates/*.template.md`,
`templates/knowledge-graph/*`, and `templates/prompts/*.md` under
`/home/okik/cypress-6.6.0/cypress`.*
