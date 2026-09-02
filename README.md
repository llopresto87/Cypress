# CYPRESS

**CYPRESS** — the **C**ontextual **Y**ield **P**rotocol for **R**outed
**E**xpert **S**eed **S**ystems — is a multi-agent seed for general
programming projects. Drop it into any codebase and an AI coding agent
(Claude Code, Prime Agent, opencode, OpenAI Codex, or GitHub Copilot) gains
a senior
team, a set of named protocols, a progressive-discovery knowledge graph
that keeps the codebase inside a context window, and a spec-driven,
test-driven discipline by default.

The name is a backronym: the CYPRESS seed still grows and *routes*
*expert* teams over a project's knowledge graph, *yielding*
project-specific knowledge as it goes — the branding changed, the
behavior did not.

CYPRESS is **language-agnostic, vendor-agnostic, and project-agnostic**.
It does not assume your stack, your domain, your deployment target, or
even your repository count — the same method governs a single repo or a
program of several. It assumes only that you want serious engineering
practice on the production path.

## What you get

> This section is a human overview, not a source of truth. The authoritative
> catalog is `manifest.json` (roster, protocols, skills, templates) and each
> node's own frontmatter (`title`, `owns`, `routing_triggers`); counts here are
> lint-checked against the tree, but for the canonical list read those homes or
> the router at `docs/graph/index.md`.

- **A bootstrap kernel** (`core/AGENTS.md`) — read by every supported
  AI coding tool on every session. ~7 KB and deliberately nothing more:
  identity, the first move (open the router), the tier table, the eight
  rules as one-line anchors, and the boundaries. Everything else — every
  protocol, skill, agent charter, posture principle, and template — is
  a routable node inside the plant's `docs/graph/` and activates only
  when the router resolves it for the task at hand. A hard size budget
  is enforced by `tests/seed-lint.py`, so kernel growth is a lint
  failure, not a drift.
- **An 19-agent team** under `agents/`:
  - `orchestrator` (first contact, routing)
  - `architect`, `implementer`, `reviewer`, `tester`
  - `security`, `pentest`, `reliability`, `data-ml`, `product`
  - `docs-librarian`, `research-scout`
  - `ui-ux-designer` (interface and interaction design)
  - `devils-advocate` (hostile refutation of a finished deliverable's claims)
  - `legal` (regulatory compliance: corpus-bound reasoning, citation ledger)
  - `multi-agent-architect` (agent-topology design and review)
  - `growth-orchestrator`, `growth-scout`, `seed-installer` (growth DNA)
- **Named protocols** under `protocols/`:
  - `grow` (canonical tool-neutral source-to-graph full-growth workflow)
  - `initialize` (optional coding-tool adapter to `grow`)
  - `from-scratch` (9-phase bootstrap)
  - `brainstorm` (Socratic convergence)
  - `specify` (executable spec authoring)
  - `grill` (plan-of-record discipline)
  - `test-first` (RED-GREEN-REFACTOR-COMMIT)
  - `ingest-library` (build the wiki)
  - `verify` (risk-proportional gate discipline)
  - `recover` (classified, bounded failure recovery — never an identical
    retry of a deterministic failure, three attempts, then escalate)
  - `canonize` (the single close-out spawn: persist knowledge AND
    catalog tools in one librarian brief)
  - `toolcraft` (durable-tool doctrine; executes inside the canonize spawn)
  - `deliver` (cold-pickup summary — compact for T0/T1, full for T2/T3)
  - `harvest` (user-triggered-only cross-project meta-loop: plant → seed)
  - `graft` (user-decided-only cross-project meta-loop: seed → existing plant)
- **Thirteen composable skills** under `skills/`:
  - `knowledge-graph`, `context-router`, `validate-knowledge`
  - `holistic-editing`
  - `library-wiki`, `research-and-ingest`
  - `spec-author`, `test-first`, `adr-writer`
  - `grill-planner`, `brainstorm-socratic`
  - `from-scratch-bootstrap`, `adopt-existing`
- **Ten templates** under `templates/`:
  - `spec.template.md` — executable spec
  - `grill.template.md` — plan-of-record
  - `library-page.template.md` — wiki page
  - `adr.template.md` — decision record
  - `prompt-contract.template.md` — LLM/VLM prompt
  - `data-contract.template.md` — dataset contract
  - `threat-model.template.md` — security threat model
  - `agent.template.md` — commissioned specialist agent
  - `skill.template.md` — project-specific procedure
  - `tool-page.template.md` — durable-tool catalog card
- **A mechanical agent-router** (`docs/graph/agent-lint.py`, projected
  to `.claude/agent-lint.py` on Claude Code) — the
  specialist-selection analog of the knowledge router. `--route "<task>"`
  ranks specialists by their `routing_triggers` frontmatter and prints a
  confidence band to cite in the delegation brief; `--lint` validates the
  routing/delegation frontmatter; `--eval` runs a golden routing set.
  Delegation is **bounded**: only six coordinator agents carry a depth-capped
  `Task`, every leaf worker is Task-less (the hard recursion cap), and each
  turn ends with a handback payload that attributes the work.
- **A populated unified `docs/graph/` skeleton** the installer adds to
  projects without overwriting existing knowledge.
- **Per-tool integration layers** under `integrations/` for Claude
  Code, Prime Agent, opencode, Codex, and GitHub Copilot — each with the
  right config files and tool-specific overlays. Claude Code and Prime
  Agent are first-class citizens at full parity (progressive-discovery
  enforcement hook/extension plus the same `agent-lint.py` CI gate).
- **`install.sh`** — drops the seed into a target project for any
  one tool or all five, copying by default; pass `--symlink` for live
  seed links so updates to the seed propagate.

## Core ideas

### Risk-proportional tiers

Process is proportional to risk, never to habit. Every task is
classified before acting — **T0** a question (read minimally, answer
with citations, no spawn), **T1** a trivial edit with no behavior,
contract, or spec surface (the one in-session authoring exception, one
focused gate, compact delivery), **T2** a change already authorized by
an active spec and plan (minimal worker set, focused gates, close-out),
**T3** anything spec-bearing (the full delegated funnel). The tier
edges are load-bearing: misclassifying *down* is the violation;
escalating up mid-task is normal and cheap. This keeps a typo fix from
paying a feature's coordination cost while keeping every consequential
change inside the full discipline (kernel §0).

### Spec-driven (SDD)

Every non-trivial behavior has a spec at `docs/graph/specs/SPEC-NNNN-*.md`
authored jointly by product, architect, and tester. Specs use stable
section numbers (§1–§12) so agents and tooling can index into them.
Code that exists without a spec is in remediation mode; specs that
exist without code are unimplemented features. The two stay in sync
because every increment in `docs/graph/plans/grill.md` §9 names the spec
contracts it implements.

### Test-driven (TDD)

No production code is written without a failing test that authorizes
it. The cycle is RED → GREEN → REFACTOR → COMMIT, run per increment.
Tests name spec contracts: the reviewer reading the test list
reconstructs the spec. Bug fixes start with a regression test that
stays in the suite forever. The few documented exceptions
(throwaway prototypes, type-only changes, pure config) are explicit
in `protocols/test-first.md`.

### One knowledge system: progressive discovery + graph + LLM wiki

A large or multi-repo codebase does not fit in a context window, and an
agent that has read everything has no signal about what matters. So
CYPRESS keeps **all maintained project knowledge** at `docs/graph/`:
Tier-1 routing, Tier-2 fact-owning nodes, and Tier-3 wiki leaves for
dependencies, sources, product, architecture, APIs, data, prompts,
evaluations, plans, runbooks, specs, and decisions. Before
touching code, an agent opens the router (`docs/graph/index.md`),
resolves the few nodes its task needs — entry nodes plus their required
closure — and **declares what it loaded and what it deliberately
skipped**. A task touching one subsystem loads a handful of nodes, not
the whole tree.

Two invariants, enforced by `graph-lint.py` (a dependency-free linter
scaffolded into `docs/graph/`): **one home per fact** — every fact lives
in exactly one node, everything else links, so it is updated in one
place instead of drifting — and **every detailed leaf resolves through
an owning node's edge**. The `context-router` skill walks the graph; the
`knowledge-graph` skill builds it; `validate-knowledge` proves it works
with clean-context test agents.

### LLM wiki depth

`docs/graph/libraries/` is a project-local, version-pinned, agent-maintained
wiki of every external dependency — one specialized Tier-3 collection
inside the same graph. Other collections provide the same source-backed
depth for project architecture and operations. Built using the
[llm-wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f),
it compounds — every time the project uses a library in a new way, the
page records the idiom. Agent memory of library APIs is unreliable
across versions; the wiki is not. Built via the `ingest-library`
protocol, optionally accelerated by an MCP server like
[Context7](https://github.com/upstash/context7).

### Integrate, don't patch

When an agent changes a file, the unit of work is the whole file, not
the smallest diff. A change is complete only when the file reads as if
the requirement had always existed — no appended functions, no `_v2`
wrappers, no dead code left behind. Deleting and consolidating are
first-class outcomes; an additive-only diff is a red flag. (Append-only
artifacts — the plan history, ADRs, changelogs — are the deliberate
exception.) See `skills/holistic-editing/`.

### Plan-of-record

`docs/graph/plans/grill.md` is the living plan. Sections 0–15 are stable.
Appended, not silently rewritten. Linked to specs, ADRs, and the graph.
The orchestrator opens it first thing every session.

### Mechanical routing + bounded delegation

The knowledge router mechanized the cheap decision (which docs to read); the
seed also mechanizes the expensive one (which expert does the work).
`agent-lint.py --route` gives specialist selection the same executable floor,
confidence signal, and citable evidence — a heuristic to reason over, never an
oracle. Only six opus coordinators (orchestrator, multi-agent-architect,
growth-orchestrator, architect, reviewer, docs-librarian) hold a depth-capped `Task`; the leaves are
Task-less, which is the one hard, harness-enforced recursion cap. A deliver-time
`produced_by` assertion (fail-closed) attributes every unit of work back to the
specialist that produced it. The decisions are recorded as
`docs/decisions/adr-0001..0003`.

### Reverse loop: canonize + harvest + graft

The seed compounds because knowledge flows back. `canonize` (kernel
§3.7 + §3.8) is the **single close-out spawn**: one docs-librarian
brief that makes a task **incomplete** until its knowledge of interest
— new or changed facts, sharp edges, corrected assumptions, provenance,
failed `load_when:` triggers — is persisted into `docs/graph/` AND any
durable tool it produced is cataloged in `docs/graph/tools/` (the
`toolcraft` doctrine), or each is explicitly recorded empty; it runs
before `deliver`. T0/T1 tasks satisfy it with a one-line self-record. `harvest` is the
inverse of `grow`: once a plant is mature, its **project-agnostic** lessons
and its version-durable library, legal-citation, tool, expert and skill
corpora are proposed back into the seed for
human ratification. Harvest is **user-triggered only — never automatic**;
the system may at most propose a harvest and stop, and nothing lands until
you are satisfied. Its standalone entry is `HARVEST_PROMPT.md`.

`graft` is harvest's outward complement — it distributes what harvest collects.
Where harvest folds one plant's lessons *up into* the seed, graft carries the
enriched seed *back out onto* an existing, already-grown plant: it
three-way-reconciles the plant's seed-owned machinery (adopting what advanced,
preserving the plant's own divergences, re-integrating true conflicts) and
refreshes the plant's library/legal/tool surfaces from the corpora — additively,
reversibly, and without touching the plant's own source or authored facts — so
one plant's harvested fruit reaches all the others. Graft is **user-decided —
never automatic**; the most the system does is propose one (typically right after
a harvest) and stop. Its standalone entry is `GRAFT_PROMPT.md`.

### Progressive disclosure

Every file in the seed follows Anthropic's progressive-disclosure
discipline — tight `name`/`description` frontmatter always in context,
`<500`-line bodies loaded on trigger, deeper references bundled and
loaded only when needed — so every supported tool's context budget
stays honest. The knowledge graph applies the same principle to the
*project's own* facts, not just the seed's files.

## Quick start

There is **one entry point**: paste [`INSTALL_PROMPT.md`](INSTALL_PROMPT.md) into
an agent-capable chat. It runs one flow in three named phases:

1. **PLACE** — invoke `install.sh` to drop every seed file into the target. This
   phase may run from a chat rooted at the seed (the seed is only a source to
   copy from).
2. **HAND OFF** — re-enter the prompt in a fresh session **rooted at the target**,
   because a harness registers agent types when a session *starts*, so growth
   cannot dispatch specialists by name until then
   (`core/method/delegation.md` → `delegation.harness-registration` owns that
   rule). The installer keeps a target-local mirror named
   `EXPERT_SEED_INSTALL_PROMPT.md` for this re-entry and later refreshes.
3. **GROW IN FULL** — execute the tool-neutral `grow` protocol end to end under
   its **completeness contract** (`grow.completeness-contract`): every
   evidence-backed knowledge collection is grown to full depth, proven by a
   growth completeness ledger — never a skeleton.

Throughout, the chat stays in orchestration/planning, spawning Sonnet-class
workers for read-only scouting and Opus-class workers for every authoring, code,
deep analysis, review, and validation task. Every worker executes
`docs/graph/graph-lint.py --plan` with its exact task inside its own session,
loads that route, and returns routing evidence.

If files are already installed and the coding tool exposes commands,
`/initialize` remains a convenience adapter to the same workflow. It is not
the canonical entry point.

For an existing project, after growth finishes:

```
# 3. The orchestrator can navigate a source-grounded graph and reports
#    evidence gaps plus one highest-leverage next step.
# 4. Drive the next change through the normal flow:
#    specify → grill → test-first → verify → deliver.
```

For a new project, growth enters `from-scratch`'s 9-phase
bootstrap and walks you through brainstorm → specify → test-first all
the way to your first useful slice.

## Per-tool details

- [Claude Code integration](integrations/claude-code/README.md)
- [Prime Agent integration](integrations/prime-agent/README.md)
- [opencode integration](integrations/opencode/README.md)
- [Codex integration](integrations/codex/README.md)
- [GitHub Copilot integration](integrations/github-copilot/README.md)

## Repository layout

```
core/                 Bootstrap kernel (AGENTS.md) + method/ posture nodes
agents/               19 specialist agents (graph nodes; projected to the harness)
protocols/            Protocol graph nodes (installed to docs/graph/protocols/)
skills/               13 skill graph nodes (installed flat to docs/graph/skills/)
templates/            Per-artifact templates (spec, grill, ADR, etc.; Tier-3 artifacts)
templates/knowledge-graph/  Node contract, graph-lint.py, router, node template
templates/prompts/    Parameterized delegation/investigation/validation briefs
templates/docs/       Leaf collections installed beneath docs/graph/
library-corpus/       Harvested library/language surface notes (by ecosystem)
legal-corpus/         Harvested law/standards citations (by jurisdiction)
tool-corpus/          Harvested reusable tools (by category)
agent-corpus/         Harvested optional expert roles (not the base roster)
skill-corpus/         Harvested optional procedures (not the core skills)
integrations/         Per-tool overlays + config + slash commands
install.sh            Drops the seed into a target project
manifest.json         Machine-readable catalog of all seed files
README.md             You are here
INSTALL.md            Detailed install/upgrade/uninstall instructions
CHANGELOG.md          Seed-system changes
```

## Updating the seed

The installer copies by default. Re-running `install.sh` in the target
project fast-forwards the machinery (kernel, protocols, agents, skills,
method, templates, the agent router): identical files are untouched,
changed ones are backed up first. It does NOT refresh the knowledge-graph
engines or your instantiated `_schema.md`/`index.md` — those are
add-if-missing, and upgrading a grown plant properly is the graft
protocol's job (engine reconciliation included). For installs made with
`--symlink`, edits to the seed propagate automatically.

For a principled, reconciled upgrade of an existing grown plant — one that
adopts what the seed advanced, preserves the plant's own local machinery
divergences (and flags them back as harvest candidates), re-integrates true
conflicts, and refreshes the plant's library/legal/tool surfaces from the
enriched corpora while leaving the plant's own source and authored facts
untouched — use
the [`graft`](protocols/graft.md) protocol via [`GRAFT_PROMPT.md`](GRAFT_PROMPT.md).
Graft is how the fruits of a `harvest` reach the plants that were grown before
the seed learned them.

## Heritage

CYPRESS extends the language-agnostic expert-prompts archive
with: SDD/TDD as foundational protocols, the LLM-wiki pattern for
library docs, the brainstorm/grill/from-scratch protocols from the
[Superpowers](https://claude.com/plugins/superpowers) framework
generalized to the five major coding agents, and progressive
disclosure throughout for context efficiency.

## License

CYPRESS is released under the **MIT License** — see [`LICENSE`](LICENSE).

Copyright (c) 2026 Luigi Lopresto.
</content>
</invoke>
