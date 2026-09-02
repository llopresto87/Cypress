# CYPRESS specialist agents — complete reference

This document describes all **19 specialist agents** shipped by the CYPRESS seed. Each agent is a fully-formed system prompt with YAML frontmatter, stored in `agents/*.md`. At install time these files are projected into the host tool's agent directory (for example `.claude/agents/`, `.prime/agent/agents/`, `.opencode/agents/`, `.codex/agents/`).

Sources for this reference: `agents/*.md` (the 18 agent definitions), `agents/_routes.golden.tsv` (the golden routing corpus), and `core/method/delegation.md` (the delegation model).

## 1. The sessions-route, workers-do model

Source: `core/method/delegation.md`.

The host session **is** the `orchestrator`. It routes, plans, briefs, verifies, communicates, and accepts. Whether it also *does* the work is decided by the task's tier (`method.tiers`). The specialists live in `docs/graph/agents/` — each a full system prompt. You invoke one by **spawning a clean-context worker with a purpose-made brief**. Simulating a specialist persona in the chat is not delegation.

Because hooks do not reach a subagent, the **brief is the only enforcement that crosses the boundary**. Whatever discipline the brief omits, the worker does not have. Every brief embeds the canonical graph-session block verbatim, carries the routing evidence, and requires the handback payload.

## 2. Mechanical routing (`agent-lint.py --route`)

Source: `core/method/delegation.md`, `00-orchestrator.md`.

Before spawning, the router runs `python3 docs/graph/agent-lint.py --route "<task>"` and cites the ranked line and confidence band in the brief. The route is a **keyword heuristic, not an oracle**: the router reasons over it and records a rationale whenever it overrides a HIGH-band pick. The deliver-time attribution assertion flags unexplained overrides.

On a **LOW / NONE** band, no shipped specialist fits. The router then **commissions** a new expert: it spawns an Opus-class agent-definition author to write one from `docs/graph/templates/agent.template.md`, grounded in the project's version-pinned facts. A commissioned expert joins the *project's* roster, never the seed's.

The routing_triggers in each agent's frontmatter are the keyword phrases the router matches on. The acceptance contract for those triggers is the golden corpus `agents/_routes.golden.tsv`, which maps example tasks to their expected agent (or the sentinel `LOW`, meaning the router must return low/none confidence and take the commission path). That corpus is owned and extended by `tester` + `data-ml`, and `agent-lint.py --eval` checks the routing_triggers against it.

## 3. Model classes

Source: `core/method/delegation.md`.

Each agent's `model:` frontmatter field is its **model class**:

- **sonnet-class** → read-only investigation.
- **opus-class** → authoring, implementation, and judgment-heavy design.

Only two agents run on sonnet — `research-scout` and `growth-scout`, the two scout roles (growth-scout writes only its evidence ledger; research-scout's drafts are mechanical normalization finalized by the librarian). The other 16 run on opus. Model class is a distinct axis from the **task tier** (T0–T3, kernel §0) and the graph **load-tier** (the node `tier:` field). Only the risk axis is written `T0–T3`.

## 4. Bounded delegation

Source: `core/method/delegation.md`.

Delegation is bounded so a fleet cannot fan out without limit.

**Six coordinators** hold a depth-capped `Task` tool and may spawn only within their own `delegates_to` allowlist:

| Coordinator | `max_spawn_depth` |
|---|---|
| `orchestrator` | 3 |
| `architect` | 1 |
| `reviewer` | 1 |
| `docs-librarian` | 1 |
| `growth-orchestrator` | 2 |
| `multi-agent-architect` | 2 |

The deepest legal chain is **depth 3** (through the `orchestrator`).

**Every other agent is a Task-less leaf.** The leaf has no `Task` tool, so it cannot spawn. This is the one recursion cap the harness itself enforces whenever the specialist was registered as a type. At an out-of-domain boundary a leaf **STOPs and hands back**, naming the next specialist, and never does the work itself. `agent-lint --lint` enforces these frontmatter invariants.

**`produced_by` attribution.** Every worker ends with the handback payload (`docs/graph/templates/prompts/handback-payload.md`). `produced_by` and `route_evidence` feed the deliver-time attribution assertion (`protocol.deliver`); a missing `produced_by` is a BLOCK. A worker hands back **exactly once per spawn** — on `complete`, `blocked-out-of-domain`, or `failed` — never once per tool call.

**The harness-registration boundary.** A specialist is spawnable by name only once the host has **registered** it. `docs/graph/agents/` is the home; the spawnable form is the host's *projection* of it, enumerated when a session starts. So spawning by name needs two preconditions: the session's project root is the plant, and the projection already existed at startup. Anything that *writes* a projection mid-session — the install, a graft's roster delta, a freshly commissioned expert — is on disk but **unspawnable** until a new session starts. The router preflights once per protocol with a throwaway dispatch; `agent-lint --route` does **not** answer registration (it globs the on-disk projection and can name types an unregistered session cannot spawn). *Prime Agent is the exception:* it has no session-start roster enumeration, so a brief written mid-session is spawnable immediately.

**Role-emulation fallback.** When neither remedy (re-enter from the plant root, or reload the agent directory) is available, the router spawns the host's generic worker and rebuilds the specialist inside the brief: pin the specialist's `model:` class, embed `docs/graph/agents/<name>.md` verbatim as the role, and restate in prose every bound the frontmatter no longer enforces — the `tools:` allowlist as an explicit prohibition, the leaf stop-and-hand-back rule, and for a coordinator its `delegates_to` allowlist and `max_spawn_depth` ceiling. The worker is stamped `produced_by: <role>` plus `harness_override: role-emulated (<reason>)`. Role emulation is a **degradation, not an equivalence**: on a generic worker the leaf recursion cap and the read-only bound drop from harness-enforced to brief-requested, so it is scoped to the phase that needs it and reported as a recorded deviation.

## 5. Shared spec authoring

Source: `core/method/delegation.md`.

Spec authoring is split across three agents: `product` writes the user-facing layer, `architect` the functional contracts, and `tester` the executable encoding. A spec is finished when all three have signed off on the same document.

## 6. Summary table — all 18 agents

| # | Agent (`name`) | `id` | `model` | Delegation | Owns (facts) |
|---|---|---|---|---|---|
| 1 | `orchestrator` | `agent.orchestrator` | opus | coordinator, depth 3 | `orchestrator.charter`, `orchestrator.tier-paths`, `orchestrator.delegation-brief` |
| 2 | `architect` | `agent.architect` | opus | coordinator, depth 1 | `architect.charter`, `architect.spec-sections`, `architect.reversibility-tags` |
| 3 | `implementer` | `agent.implementer` | opus | leaf (no Task) | `implementer.charter`, `implementer.preconditions`, `implementer.integration-discipline` |
| 4 | `reviewer` | `agent.reviewer` | opus | coordinator, depth 1 | `reviewer.charter`, `reviewer.checklist`, `reviewer.severity-scale` |
| 5 | `tester` | `agent.tester` | opus | leaf (no Task) | `tester.charter`, `tester.test-levels`, `tester.bug-fix-loop` |
| 6 | `security` | `agent.security` | opus | leaf (no Task) | `security.charter`, `security.secure-defaults`, `security.gate-bar` |
| 7 | `reliability` | `agent.reliability` | opus | leaf (no Task) | `reliability.charter`, `reliability.runbook-set`, `reliability.delivery-pipeline` |
| 8 | `data-ml` | `agent.data-ml` | opus | leaf (no Task) | `data-ml.charter`, `data-ml.synthetic-data-rules`, `data-ml.evaluation-design` |
| 9 | `product` | `agent.product` | opus | leaf (no Task) | `product.charter`, `product.first-useful-slice`, `product.accessibility-floor` |
| 10 | `docs-librarian` | `agent.docs-librarian` | opus | coordinator, depth 1 | `docs-librarian.charter`, `docs-librarian.close-out-flow`, `docs-librarian.sources-discipline` |
| 11 | `research-scout` | `agent.research-scout` | sonnet | leaf (no Task) | `research-scout.charter`, `research-scout.source-discipline`, `research-scout.conflict-resolution` |
| 12 | `pentest` | `agent.pentest` | opus | leaf (no Task) | `pentest.charter`, `pentest.authorization-gate`, `pentest.remediation-loop` |
| 13 | `devils-advocate` | `agent.devils-advocate` | opus | leaf (no Task) | `devils-advocate.charter`, `devils-advocate.verdict-vocabulary`, `devils-advocate.primary-source-rule` |
| 14 | `growth-orchestrator` | `agent.growth-orchestrator` | opus | coordinator, depth 2 | `growth-orchestrator.charter`, `growth-orchestrator.growth-phases` |
| 15 | `growth-scout` | `agent.growth-scout` | sonnet | leaf (no Task) | `growth-scout.charter`, `growth-scout.evidence-discipline` |
| 16 | `multi-agent-architect` | `agent.multi-agent-architect` | opus | coordinator, depth 2 | `multi-agent-architect.charter`, `multi-agent-architect.topology-catalog`, `multi-agent-architect.pre-ship-checklist` |
| 17 | `seed-installer` | `agent.seed-installer` | opus | leaf (no Task) | `seed-installer.charter`, `seed-installer.install-discipline` |
| 18 | `ui-ux-designer` | `agent.ui-ux-designer` | opus | leaf (no Task) | `ui-ux-designer.charter`, `ui-ux-designer.design-spec`, `ui-ux-designer.heuristics` |

Coordinators as an edge list of `delegates_to` allowlists:

| Coordinator | `max_spawn_depth` | `delegates_to` |
|---|---|---|
| `orchestrator` | 3 | `architect`, `implementer`, `reviewer`, `tester`, `security`, `reliability`, `data-ml`, `product`, `docs-librarian`, `research-scout`, `pentest`, `multi-agent-architect`, `growth-orchestrator`, `growth-scout`, `seed-installer`, `ui-ux-designer` |
| `architect` | 1 | `tester`, `research-scout` |
| `reviewer` | 1 | `security`, `reliability` |
| `docs-librarian` | 1 | `research-scout` |
| `growth-orchestrator` | 2 | `growth-scout`, `seed-installer`, `docs-librarian`, `architect`, `research-scout`, `tester`, `ui-ux-designer` |
| `multi-agent-architect` | 2 | `architect`, `tester`, `implementer`, `reviewer`, `data-ml`, `security`, `reliability` |

## 7. Agent reference (per agent)

Each subsection below documents one agent. All frontmatter fields are taken verbatim from that agent's file in `agents/`; the charter summary paraphrases the file body.

### 7.1 `orchestrator`

*Source file: `agents/00-orchestrator.md`*

- **id:** `agent.orchestrator`
- **Role:** Default agent. First contact for any request. Classifies the task tier (kernel §0), picks the right protocol, delegates to the right specialists, owns the grill.md plan-of-record, enforces spec-first and test-first, and runs the close-out and delivery rules at the end.
- **model class:** `opus`
- **Delegation:** coordinator — `can_delegate: true`, `max_spawn_depth: 3`, `delegates_to:` `architect`, `implementer`, `reviewer`, `tester`, `security`, `reliability`, `data-ml`, `product`, `docs-librarian`, `research-scout`, `pentest`, `multi-agent-architect`, `growth-orchestrator`, `growth-scout`, `seed-installer`
- **tools:** `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`, `WebSearch`, `WebFetch`, `Task`
- **tier (graph load-tier):** 2
- **owns (facts):** `orchestrator.charter`, `orchestrator.tier-paths`, `orchestrator.delegation-brief`
- **requires:** `method.tiers`
- **peers:** `agent.architect`, `agent.tester`, `agent.implementer`, `agent.reviewer`, `agent.docs-librarian`
- **routing_triggers:**
  - "route this task to the right specialist"
  - "which protocol should we enter for this request"
  - "coordinate the delivery across specialists"
  - "classify the request and pick the next step"

**Charter.** The orchestrator answers the door and ends every session in a known state. On turn 0 it bounds context from the graph router, then classifies the task tier (T0–T3) and picks the matching protocol. For T2/T3 work it delegates all doing to clean-context specialists with a written, mandatory brief, routes mechanically first with `agent-lint --route`, and commissions a new expert when no specialist fits. It enforces the eight rules of `AGENTS.md` §3 in dependency order, requires one close-out spawn per T2/T3 task, and ends every session with a `deliver`.

### 7.2 `architect`

*Source file: `agents/01-architect.md`*

- **id:** `agent.architect`
- **Role:** Senior system architect. Owns boundaries, interfaces, data flow, dependency choices, and Architecture Decision Records (ADRs).
- **model class:** `opus`
- **Delegation:** coordinator — `can_delegate: true`, `max_spawn_depth: 1`, `delegates_to:` `tester`, `research-scout`
- **tools:** `Read`, `Write`, `Edit`, `Glob`, `Grep`, `WebSearch`, `WebFetch`, `Task`
- **tier (graph load-tier):** 2
- **owns (facts):** `architect.charter`, `architect.spec-sections`, `architect.reversibility-tags`
- **requires:** —
- **peers:** `agent.tester`, `agent.implementer`, `agent.product`, `agent.research-scout`
- **routing_triggers:**
  - "design the data model for the orders service"
  - "choose a framework and write the adr for the split"
  - "decide sync versus async at the service boundary"
  - "define the interface contract between modules"
- **Golden routing tasks** (`agents/_routes.golden.tsv`, expected → `architect`):
  - "design the data model for the orders service"
  - "choose a framework and write the adr for the split"
  - "decide sync versus async at the service boundary"

**Charter.** The architect names the system's boundaries, designs the interfaces between them, and turns product intent into testable functional contracts. It records every non-obvious decision as an ADR and favors reversible choices, tagging each decision with a reversibility class. It is the central author of the technical part of every spec (§4 contracts, §6 data shapes, §7 failure modes). It may spawn `tester` or `research-scout` at bounded depth 1 but writes no production code itself.

### 7.3 `implementer`

*Source file: `agents/02-implementer.md`*

- **id:** `agent.implementer`
- **Role:** Senior implementer. Writes the code that turns a failing test green — the minimum new behavior, integrated into the file's existing design rather than bolted on as the smallest diff — after a spec has been authored and tests have been written.
- **model class:** `opus`
- **Delegation:** Task-less leaf — `can_delegate: false`, no `Task` tool; stops and hands back at any out-of-domain boundary
- **tools:** `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`
- **tier (graph load-tier):** 2
- **owns (facts):** `implementer.charter`, `implementer.preconditions`, `implementer.integration-discipline`
- **requires:** `skill.holistic-editing`
- **peers:** `agent.tester`, `agent.reviewer`
- **routing_triggers:**
  - "make the failing test pass"
  - "turn the red test green in the code"
  - "implement the minimum behavior to satisfy the test"
  - "wire the green code into the existing module"
- **Golden routing tasks** (`agents/_routes.golden.tsv`, expected → `implementer`):
  - "make the failing test pass"
  - "write the code to turn the red test green"
  - "implement the minimum behavior to satisfy the test"

**Charter.** The implementer turns RED into GREEN: it writes the minimum new behavior the spec asked for once the spec, contracts, and failing tests already exist. "Minimum" governs behavior, not diff size — the code is woven into the file's existing design, never bolted on, and it adds no abstraction the spec's variation does not yet demand. It loads context through the graph context-router before editing. It is a Task-less leaf and stops at any out-of-domain boundary.

### 7.4 `reviewer`

*Source file: `agents/03-reviewer.md`*

- **id:** `agent.reviewer`
- **Role:** Senior code reviewer. Audits diffs against the plan, the architecture, the wiki idioms, the project's conventions, and integration coherence (a change must be integrated, not bolted on).
- **model class:** `opus`
- **Delegation:** coordinator — `can_delegate: true`, `max_spawn_depth: 1`, `delegates_to:` `security`, `reliability`
- **tools:** `Read`, `Glob`, `Grep`, `Bash`, `Task`
- **tier (graph load-tier):** 2
- **owns (facts):** `reviewer.charter`, `reviewer.checklist`, `reviewer.severity-scale`
- **requires:** `skill.holistic-editing`
- **peers:** `agent.implementer`, `agent.security`, `agent.reliability`, `agent.devils-advocate`
- **routing_triggers:**
  - "audit this diff against the spec"
  - "review the pull request before we merge"
  - "check the change is integrated and not bolted on"
  - "produce severity tagged review findings"
- **Golden routing tasks** (`agents/_routes.golden.tsv`, expected → `reviewer`):
  - "audit this diff against the spec"
  - "review the pull request before we merge"
  - "check the change is integrated and not bolted on"

**Charter.** The reviewer reads and writes no files at all; its structured review goes in the report body. It compares a diff against the plan, the architecture, the library wiki, and project conventions, and returns findings tagged by severity: critical blocks the increment, major gates the merge, minor and nit are suggestions. For a hard security or operations finding it may spawn `security` or `reliability` via bounded Task (depth 1) and fold their findings in. It still writes no source itself.

### 7.5 `tester`

*Source file: `agents/04-tester.md`*

- **id:** `agent.tester`
- **Role:** Senior test engineer. Translates spec contracts into failing tests, runs the RED-GREEN-REFACTOR cycle, owns the verification gates and the evaluation suites for AI behavior, and maintains the regression corpus.
- **model class:** `opus`
- **Delegation:** Task-less leaf — `can_delegate: false`, no `Task` tool; stops and hands back at any out-of-domain boundary
- **tools:** `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`
- **tier (graph load-tier):** 2
- **owns (facts):** `tester.charter`, `tester.test-levels`, `tester.bug-fix-loop`
- **requires:** `protocol.test-first`
- **peers:** `agent.implementer`, `agent.reviewer`
- **routing_triggers:**
  - "write the failing test that encodes the spec contract"
  - "add a regression test for this bug"
  - "run the verification gates before merge"
  - "drive the red green refactor cycle"
- **Golden routing tasks** (`agents/_routes.golden.tsv`, expected → `tester`):
  - "write the failing test that encodes the spec contract"
  - "add a regression test for this bug"
  - "run the verification gates before merge"

**Charter.** The tester translates spec contracts into executable tests and runs the RED-GREEN-REFACTOR cycle. Every increment begins with the tester writing a failing test that encodes a contract, with the test name as the contract slug so a reviewer can reconstruct the spec from the test list. It owns the verification gates, the AI-behavior evaluation suites, and the regression corpus. It is a Task-less leaf.

### 7.6 `security`

*Source file: `agents/05-security.md`*

- **id:** `agent.security`
- **Role:** Senior security, privacy, and abuse-resistance engineer. Owns threat models, auth and authorization design, secrets handling, supply-chain risk, file-upload safety, and AI-specific abuse (prompt injection, tool hijacking, data exfiltration).
- **model class:** `opus`
- **Delegation:** Task-less leaf — `can_delegate: false`, no `Task` tool; stops and hands back at any out-of-domain boundary
- **tools:** `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`, `WebSearch`, `WebFetch`
- **tier (graph load-tier):** 2
- **owns (facts):** `security.charter`, `security.secure-defaults`, `security.gate-bar`
- **requires:** —
- **peers:** `agent.pentest`, `agent.reviewer`, `agent.reliability`
- **routing_triggers:**
  - "add a threat model for the upload endpoint"
  - "assess the supply-chain and secrets handling risk"
  - "design the authorization model for the api"
  - "check for prompt injection and data exfiltration"
- **Golden routing tasks** (`agents/_routes.golden.tsv`, expected → `security`):
  - "add a threat model for the upload endpoint"
  - "assess the supply-chain and secrets handling risk"
  - "design the authorization model for the api"

**Charter.** The security agent turns security, privacy, and abuse-resistance requirements into architecture, tests, runtime controls, and documentation. It produces threat models, ADRs, and verification gates rather than lectures, and should be called whenever a feature touches user data, auth, payments, secrets, uploads, external services, LLM/VLM features, or public exposure. It sets secure defaults and a gate bar the change must clear. It is a Task-less leaf.

### 7.7 `reliability`

*Source file: `agents/06-reliability.md`*

- **id:** `agent.reliability`
- **Role:** Senior reliability, platform, and delivery engineer. Owns standing infrastructure up from scratch, deployment, observability, rollback, capacity, cost, and the operational runbooks.
- **model class:** `opus`
- **Delegation:** Task-less leaf — `can_delegate: false`, no `Task` tool; stops and hands back at any out-of-domain boundary
- **tools:** `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`, `WebSearch`, `WebFetch`
- **tier (graph load-tier):** 2
- **owns (facts):** `reliability.charter`, `reliability.runbook-set`, `reliability.delivery-pipeline`
- **requires:** —
- **peers:** `agent.security`, `agent.tester`
- **routing_triggers:**
  - "the deploy is flaking under load, add observability"
  - "configure rollback and capacity budgets for the cluster"
  - "stand up fresh infrastructure from scratch"
  - "add health checks timeouts and retries"
- **Golden routing tasks** (`agents/_routes.golden.tsv`, expected → `reliability`):
  - "the deploy is flaking under load, add observability"
  - "configure rollback and capacity budgets for the cluster"
  - "stand up fresh infrastructure and set the timers"

**Charter.** The reliability agent turns software into an operable system: one that can be stood up from nothing, deployed by command, observed by dashboard, recovered by runbook, and rolled back by procedure. A first-class part of the job is bringing the pipeline and environment up from scratch and capturing it as an executable `local-development.md` and, where codified, infrastructure-as-code. Its artifacts live under `docs/graph/runbooks/`. It is a Task-less leaf.

### 7.8 `data-ml`

*Source file: `agents/07-data-ml.md`*

- **id:** `agent.data-ml`
- **Role:** Senior data and ML engineer. Owns dataset contracts, pipelines, model selection, evaluation design, reproducibility, and the generation of synthetic/example/fixture data for tests, demos, and fresh environments — never sourced from production.
- **model class:** `opus`
- **Delegation:** Task-less leaf — `can_delegate: false`, no `Task` tool; stops and hands back at any out-of-domain boundary
- **tools:** `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`, `WebSearch`, `WebFetch`
- **tier (graph load-tier):** 2
- **owns (facts):** `data-ml.charter`, `data-ml.synthetic-data-rules`, `data-ml.evaluation-design`
- **requires:** —
- **peers:** `agent.tester`, `agent.research-scout`
- **routing_triggers:**
  - "generate synthetic fixture data for tests not sourced from production"
  - "design the dataset contract and the pipeline"
  - "select a model and design its evaluation"
  - "build the eval suite and golden set"
- **Golden routing tasks** (`agents/_routes.golden.tsv`, expected → `data-ml`):
  - "generate synthetic fixture data for tests not sourced from production"
  - "design the dataset contract and the pipeline"
  - "select a model and design its evaluation"

**Charter.** The data/ML/evaluation engineer treats data quality and evaluation design as engineering work done up front, not at the end. It produces reproducible pipelines, named data contracts, and evaluation suites with stable thresholds, and it generates synthetic, fixture, and demo data that is never sourced from production. It is invoked whenever the project has a dataset, ships a model, or ships an LLM/VLM feature where quality matters. It is a Task-less leaf.

### 7.9 `product`

*Source file: `agents/08-product.md`*

- **id:** `agent.product`
- **Role:** Senior product-minded technical lead. Authors §3 (User-facing behavior) and §9 (Acceptance criteria) of every spec.
- **model class:** `opus`
- **Delegation:** Task-less leaf — `can_delegate: false`, no `Task` tool; stops and hands back at any out-of-domain boundary
- **tools:** `Read`, `Write`, `Edit`, `Glob`, `Grep`, `WebSearch`, `WebFetch`
- **tier (graph load-tier):** 2
- **owns (facts):** `product.charter`, `product.first-useful-slice`, `product.accessibility-floor`
- **requires:** —
- **peers:** `agent.architect`, `agent.tester`
- **routing_triggers:**
  - "write the acceptance criteria and the user flow"
  - "define onboarding and the accessibility floor"
  - "map the user flow states and recovery paths"
- **Golden routing tasks** (`agents/_routes.golden.tsv`, expected → `product`):
  - "write the acceptance criteria and the user flow"
  - "define onboarding and the accessibility floor"

**Charter.** The product-minded technical lead clarifies what the user is trying to do and designs the smallest coherent solution. It never jumps from goal to UI; it goes goal → outcome → flow → states → acceptance. It authors the user-facing sections of every spec (§3 user-facing behavior and §9 acceptance criteria) and owns user flows, the first useful slice, and the accessibility floor. It is a Task-less leaf.

### 7.10 `docs-librarian`

*Source file: `agents/09-docs-librarian.md`*

- **id:** `agent.docs-librarian`
- **Role:** Senior knowledge-graph architect. Owns the unified system at docs/graph/ — progressive-discovery router, fact-owning nodes, source provenance, detailed project leaves, dependency wiki, the reusable-tool catalog, the project-skill catalog (.claude/skills/), specs, decisions, plans, and runbooks.
- **model class:** `opus`
- **Delegation:** coordinator — `can_delegate: true`, `max_spawn_depth: 1`, `delegates_to:` `research-scout`
- **tools:** `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`, `WebSearch`, `WebFetch`, `Task`
- **tier (graph load-tier):** 2
- **owns (facts):** `docs-librarian.charter`, `docs-librarian.close-out-flow`, `docs-librarian.sources-discipline`
- **requires:** `skill.knowledge-graph`
- **peers:** `agent.research-scout`
- **routing_triggers:**
  - "author a graph node for the subsystem"
  - "fix the wiki page that fails graph validation"
  - "dedupe the knowledge facts so each has one home"
  - "refresh the library wiki page"
  - "catalog a reusable tool the work produced"
  - "crystallize a recurring procedure into a project skill"
- **Golden routing tasks** (`agents/_routes.golden.tsv`, expected → `docs-librarian`):
  - "author a graph node for the auth subsystem"
  - "fix the wiki page that fails graph validation"
  - "dedupe the knowledge facts so each has one home"
  - "catalog the reusable tool this task produced"

**Charter.** The docs-librarian is the knowledge-graph architect for the project's single maintained system at `docs/graph/`. It keeps the graph useful, current, routed, source-grounded, and deduplicated, and it enforces the one-home-per-fact rule: every fact lives in exactly one node's `owns:` list and everything else links. It runs `graph-lint.py` before committing any graph change and owns the close-out flow that persists knowledge and catalogs reusable tools. It may spawn `research-scout` at bounded depth 1.

### 7.11 `research-scout`

*Source file: `agents/10-research-scout.md`*

- **id:** `agent.research-scout`
- **Role:** Senior research scout. Goes to the internet, finds authoritative sources, downloads them when allowed, normalizes them, and hands them to the docs-librarian for the wiki.
- **model class:** `sonnet`
- **Delegation:** Task-less leaf — `can_delegate: false`, no `Task` tool; stops and hands back at any out-of-domain boundary
- **tools:** `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`, `WebSearch`, `WebFetch`
- **tier (graph load-tier):** 2
- **owns (facts):** `research-scout.charter`, `research-scout.source-discipline`, `research-scout.conflict-resolution`
- **requires:** `protocol.ingest-library`
- **peers:** `agent.docs-librarian`
- **routing_triggers:**
  - "retrieve the authoritative upstream documentation for a new library"
  - "find and normalize the official spec for this dependency"
  - "ingest a new dependency into the wiki"
- **Golden routing tasks** (`agents/_routes.golden.tsv`, expected → `research-scout`):
  - "retrieve the authoritative upstream documentation for a new library"
  - "find and normalize the official spec for this dependency"

**Charter.** The research scout is the bridge between the project and the open web. It finds authoritative sources, retrieves them when allowed, normalizes them, and hands them to the docs-librarian; it never invents facts and never trusts training data on version-sensitive details. It prefers official upstream docs for the exact version in use, then upstream source, and records conflicts rather than guessing. It runs on the sonnet model class as a read-only leaf.

### 7.12 `pentest`

*Source file: `agents/11-pentest.md`*

- **id:** `agent.pentest`
- **Role:** Senior offensive-and-defensive security engineer. Drives authorized penetration testing of the project's own systems, triages what it finds, and drives the fixes to closure.
- **model class:** `opus`
- **Delegation:** Task-less leaf — `can_delegate: false`, no `Task` tool; stops and hands back at any out-of-domain boundary
- **tools:** `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`, `WebSearch`, `WebFetch`
- **tier (graph load-tier):** 2
- **owns (facts):** `pentest.charter`, `pentest.authorization-gate`, `pentest.remediation-loop`
- **requires:** —
- **peers:** `agent.security`, `agent.tester`, `agent.devils-advocate`
- **routing_triggers:**
  - "run an authorized penetration test of the login"
  - "write a proof-of-concept exploit for the upload endpoint"
  - "reproduce and remediate the vulnerability"
- **Golden routing tasks** (`agents/_routes.golden.tsv`, expected → `pentest`):
  - "run an authorized penetration test of the login"
  - "write a proof-of-concept exploit for the upload endpoint"

**Charter.** The pentest agent attacks the project's own systems so that someone worse cannot, then confirms the hole is actually closed — it is red team and fix owner in one loop. It operates only within an authorized scope and must clear an authorization gate (named targets, environment, and rules) before touching anything, defaulting to a local or disposable environment. A finding it cannot drive to a verified remediation is half a job. It is a Task-less leaf.

### 7.13 `devils-advocate`

*Source file: `agents/12-devils-advocate.md`*

- **id:** `agent.devils-advocate`
- **Role:** Hostile second pass over a FINISHED, claim-bearing deliverable — a report, spec, ADR, security finding, audit result, or migration plan — whose sole job is to try to REFUTE each load-bearing claim from primary sources only, never the working papers that produced it.
- **model class:** `opus`
- **Delegation:** Task-less leaf — `can_delegate: false`, no `Task` tool; stops and hands back at any out-of-domain boundary
- **tools:** `Read`, `Glob`, `Grep`, `WebSearch`, `WebFetch`
- **tier (graph load-tier):** 2
- **owns (facts):** `devils-advocate.charter`, `devils-advocate.verdict-vocabulary`, `devils-advocate.primary-source-rule`
- **requires:** —
- **peers:** `agent.reviewer`, `agent.pentest`
- **routing_triggers:**
  - "try to refute every load-bearing claim in this finished document"
  - "check this deliverable's citations against the sources they name"
  - "what single fact would break this conclusion"
  - "what should this document claim and does not"
- **Golden routing tasks** (`agents/_routes.golden.tsv`, expected → `devils-advocate`):
  - "try to refute every load-bearing claim in this finished document"
  - "check this deliverable's citations against the sources they name"
  - "what single fact would break this conclusion"
  - "what should this document claim and does not"

**Charter.** The devil's advocate does not assess a finished deliverable — it tries to break it. It is read-only and advisory: it gates nothing by fiat, writes no files, and returns verdicts in its report body, keeping attack and repair structurally separate. It works only from primary sources and never reads the drafts, notes, or reasoning chain that produced a claim, because reading those is inherited-error confirmation. It is a Task-less leaf.

### 7.14 `growth-orchestrator`

*Source file: `agents/growth-orchestrator.md`*

- **id:** `agent.growth-orchestrator`
- **Role:** Senior growth conductor. Owns running the grow / adopt-existing / from-scratch flow end to end — detect the project's shape, dispatch growth-scouts by real subsystem/repository boundary, sequence the authoring of the unified docs/graph from their evidence ledgers, and gate on knowledge validation before delivery.
- **model class:** `opus`
- **Delegation:** coordinator — `can_delegate: true`, `max_spawn_depth: 2`, `delegates_to:` `growth-scout`, `seed-installer`, `docs-librarian`, `architect`, `research-scout`, `tester`
- **tools:** `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`, `Task`
- **tier (graph load-tier):** 2
- **owns (facts):** `growth-orchestrator.charter`, `growth-orchestrator.growth-phases`
- **requires:** `protocol.grow`
- **peers:** `agent.growth-scout`, `agent.docs-librarian`, `agent.seed-installer`, `agent.architect`
- **routing_triggers:**
  - "grow the knowledge graph from this existing codebase"
  - "conduct the grow protocol across these repositories"
  - "adopt this project into the docs graph by subsystem boundary"
  - "run the from-scratch bootstrap for a brand new project"
- **Golden routing tasks** (`agents/_routes.golden.tsv`, expected → `growth-orchestrator`):
  - "grow the knowledge graph from this existing codebase"
  - "adopt this project into the docs graph by subsystem boundary"
  - "run the from-scratch bootstrap for a brand new project"

**Charter.** The growth orchestrator is the specialist the generic orchestrator hands a *growth* to: it conducts the grow / adopt-existing / from-scratch flow end to end. It detects the project's shape, dispatches growth-scouts by real subsystem or repository boundary, sequences the authoring of a unified `docs/graph/` from their evidence ledgers, and gates on knowledge validation before delivery. It enforces the model policy — Sonnet scouts, Opus authors — and never gathers evidence or authors a node with its own hands. It coordinates at bounded depth 2.

### 7.15 `growth-scout`

*Source file: `agents/growth-scout.md`*

- **id:** `agent.growth-scout`
- **Role:** Senior growth scout. The read-only evidence-gatherer of the grow/adopt flow: dispatched at ONE real subsystem or repository boundary, it inspects executable source directly and returns claims tied to paths and symbols — the ledger the graph authors build from.
- **model class:** `sonnet`
- **Delegation:** Task-less leaf — `can_delegate: false`, no `Task` tool; stops and hands back at any out-of-domain boundary
- **tools:** `Read`, `Write`, `Glob`, `Grep`, `Bash`
- **tier (graph load-tier):** 2
- **owns (facts):** `growth-scout.charter`, `growth-scout.evidence-discipline`
- **requires:** —
- **peers:** `agent.growth-orchestrator`, `agent.docs-librarian`, `agent.research-scout`
- **routing_triggers:**
  - "gather executable evidence from this subsystem's source"
  - "scout this repository boundary and return claims with paths and symbols"
  - "inventory what this module actually does from its code not its docs"
  - "produce the evidence ledger for adopting this codebase"
- **Golden routing tasks** (`agents/_routes.golden.tsv`, expected → `growth-scout`):
  - "gather executable evidence from this subsystem's source"
  - "scout this repository boundary and return claims with paths and symbols"
  - "produce the evidence ledger for adopting this codebase"

**Charter.** The growth scout is the read-only evidence-gatherer of the grow/adopt flow, the bridge between a project's executable source and the authors who build its graph. It is dispatched to exactly one subsystem or repository boundary, reads what is actually there, and returns claims anchored to a path and a symbol. It authors no graph nodes, specs, or ADRs and never trusts centralized prose over the code it describes. It runs on the sonnet model class as a read-only leaf.

### 7.16 `multi-agent-architect`

*Source file: `agents/multi-agent-architect.md`*

- **id:** `agent.multi-agent-architect`
- **Role:** Senior multi-agent systems architect. Owns the design and review of agentic and multi-agent systems — topology, delegation, orchestration substrate, context and memory strategy, tool contracts, guardrails and fail-closed gates, observability, evaluation, and cost/latency budgets.
- **model class:** `opus`
- **Delegation:** coordinator — `can_delegate: true`, `max_spawn_depth: 2`, `delegates_to:` `architect`, `tester`, `implementer`, `reviewer`, `data-ml`, `security`, `reliability`
- **tools:** `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`, `WebSearch`, `WebFetch`, `Task`
- **tier (graph load-tier):** 2
- **owns (facts):** `multi-agent-architect.charter`, `multi-agent-architect.topology-catalog`, `multi-agent-architect.pre-ship-checklist`
- **requires:** `method.delegation`
- **peers:** `agent.architect`, `agent.tester`, `agent.security`
- **routing_triggers:**
  - "design a multi-agent topology with bounded delegation"
  - "diagnose runaway fan-out in the agent fleet"
  - "define the agent role tool and termination contract"
  - "review the orchestration framework and delegation caps"
- **Golden routing tasks** (`agents/_routes.golden.tsv`, expected → `multi-agent-architect`):
  - "design a multi-agent topology with bounded delegation"
  - "diagnose runaway fan-out in the agent fleet"
  - "define the agent role tool and termination contract"

**Charter.** The multi-agent architect decides whether a problem needs more than one agent and, if so, how the agents are shaped, wired, bounded, observed, and paid for. It is accountable for one thing: that the system does useful work under a known termination budget, with failures that are visible and recoverable rather than silent. It does not reach for a multi-agent design when a single well-tooled agent or plain code would do with less to go wrong, and it reads the wiki before pinning any model version. It coordinates at bounded depth 2.

### 7.17 `seed-installer`

*Source file: `agents/seed-installer.md`*

- **id:** `agent.seed-installer`
- **Role:** Senior seed-install engineer. Owns placing CYPRESS into a target project — running install.sh's place_file/place_tree mechanics, selecting only the host adapters actually used, backing up rather than overwriting, and verifying the host tool truly loads the kernel, agents, protocols, and skills.
- **model class:** `opus`
- **Delegation:** Task-less leaf — `can_delegate: false`, no `Task` tool; stops and hands back at any out-of-domain boundary
- **tools:** `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`
- **tier (graph load-tier):** 2
- **owns (facts):** `seed-installer.charter`, `seed-installer.install-discipline`
- **requires:** —
- **peers:** `agent.growth-orchestrator`
- **routing_triggers:**
  - "install the expert seed system into this target project"
  - "place the kernel and adapters additively for this host tool"
  - "wire the claude code or prime agent or opencode or codex adapter into the project"
  - "set up the seed skeleton before growth"
- **Golden routing tasks** (`agents/_routes.golden.tsv`, expected → `seed-installer`):
  - "install the expert seed system into this target project"
  - "place the kernel and adapters additively for this host tool"

**Charter.** The seed installer places CYPRESS into a target so a fresh agent session there loads the kernel, roster, protocols, and skills — and it does so additively, leaving every target-owned file exactly as found or safely backed up. An install that overwrites the project it serves is a failure no matter how clean the result. It selects only the host adapters actually used, backs up rather than clobbers, and does not build or run the target app or push Git state. It is a Task-less leaf.


### 7.18 `ui-ux-designer`

*Source file: `agents/13-ui-ux-designer.md`*

- **id:** `agent.ui-ux-designer`
- **Role:** Senior interface & interaction designer. The definitive authority on information architecture, screen/flow design, interaction states, design tokens and the component system, visual hierarchy, and usability-heuristics audits — and on HOW the accessibility floor is met in the interface.
- **model class:** `opus`
- **Delegation:** Task-less leaf — `can_delegate: false`, no `Task` tool; stops and hands back at any out-of-domain boundary
- **tools:** `Read`, `Write`, `Edit`, `Glob`, `Grep`, `WebSearch`, `WebFetch`
- **tier (graph load-tier):** 2
- **owns (facts):** `ui-ux-designer.charter`, `ui-ux-designer.design-spec`, `ui-ux-designer.heuristics`
- **requires:** —
- **peers:** `agent.product`, `agent.architect`, `agent.implementer`
- **routing_triggers:**
  - "design the interface layout and interaction states"
  - "create the component library and design tokens"
  - "audit the ui against usability heuristics"
  - "design the screen flows and visual hierarchy"

**Charter.** Authors implementable design specs under `docs/graph/design/` that map to spec §3 and §9. Distinct from `product`, which owns the user outcome and the accessibility floor itself, and from `implementer`, which writes the code. Frontmatter fields above are taken verbatim from `agents/13-ui-ux-designer.md`; that file is the single source of truth for the charter.
