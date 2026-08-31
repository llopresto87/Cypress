# Plan of Record — Mechanical Agent Routing & Bounded Delegation

- **Status:** ~~draft (design/plan only — no implementation in this pass)~~ →
  **P0 + P1 + P2 implemented and verified** (2026-07-13). Reviewer verdict
  SHIP-WITH-MINORS (1 Major + Minors, all fixed). Gate results and the phase-by-phase
  record are in §9. Decisions ADR-A/B/C promoted to standalone ADRs — see §3 note.
  (P3 remains optional, not done.)
- **Owner:** multi-agent-architect
- **Date:** 2026-07-13
- **Subject system:** the CYPRESS orchestration framework itself
  (the "grown seed") — its own machinery, **not** any host application it is
  installed into.
- **Scope of this document:** self-contained enough to implement from the plan
  alone after context compression. It restates the problem, records the
  decisions at ADR grade, lists every file to touch, and phases the work.

---

## 0. How to read this file cold

You are picking this up with no memory of the investigation that produced it.
Everything you need is below. The framework under change is a multi-agent
system with a kernel (`core/AGENTS.md`, installed as `CLAUDE.md`), 13 specialist
agent definitions (`.claude/agents/*.md`), protocols (`.claude/protocols/*.md`),
a **knowledge** router (`docs/graph/graph-lint.py --plan` + `.claude/route-hook.py`),
and a knowledge graph (`docs/graph/`). The knowledge router works well. The
**agent** router does not exist — that is the core of what this plan fixes.

Two source trees hold the same agents/protocols/templates and must be kept in
sync:
- **Installed / live:** the host project's `.claude/…` and `docs/graph/…`.
- **Seed source (the shippable template):** the seed's own `cypress/…`
  (e.g. `cypress/agents/`, `cypress/protocols/`,
  `cypress/templates/`, `cypress/core/`,
  `cypress/integrations/claude-code/`).

Every edit below must be applied to **both** trees. Where a path is given as
`.claude/agents/NN-name.md`, its seed mirror is `cypress/agents/NN-name.md`
(same basename).

---

## 1. Problem restatement (RC1–RC5, with cited evidence)

The operator observes that the grown seed **(A)** often routes work to the
wrong specialist, and **(B)** agents frequently do out-of-domain work
themselves instead of spawning the correct sub-agent. Root causes:

### RC1 — There is no mechanical agent-router; only a knowledge-router. (drives A)
The one deterministic routing mechanism routes knowledge **nodes**, never
agents:
- `docs/graph/graph-lint.py` `resolve()` (lines 336–394) scores nodes by
  IDF-weighted keyword overlap against each node's `id`/`title`/`load_when`
  (347–348, 362–371). `main()` exposes only `--graph` and `--plan`
  (399–400). No agent/roster awareness anywhere.
- `.claude/route-hook.py` (the only hook; wired at `.claude/settings.json`
  `hooks.UserPromptSubmit`) injects a **knowledge** mandate + the `--plan` node
  suggestion (route-hook.py:83–102). Nothing about which *agent* to pick.
- `.claude/skills/context-router/SKILL.md` is only the node-traversal algorithm.

Agent selection is therefore 100% orchestrator model-judgment reading prose
`description:` frontmatter, guided by worked examples in
`.claude/agents/00-orchestrator.md` "Specialist routing" (56–155). No executable
floor, no confidence, no citable evidence.

### RC2 — Flat-by-tool-grant: only 2 of 13 specialists can sub-delegate. (drives B)
Only two agents carry the `Task` tool:
- `.claude/agents/00-orchestrator.md:4` — `tools: [Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch, Task]`
- `.claude/agents/multi-agent-architect.md:4` — same, includes `Task`.

The other eleven (architect `01`, implementer `02`, reviewer `03` — also no
Write/Edit, tester `04`, security `05`, reliability `06`, data-ml `07`, product
`08`, docs-librarian `09`, research-scout `10`, pentest `11`) have no `Task`, so
they physically cannot spawn a sub-agent. Their only moves at an out-of-domain
boundary are "hand back" or "do it myself."

### RC3 — Specialist prose says "delegate to peer X" but no tool backs it. (drives B, contradiction)
- `.claude/agents/03-reviewer.md:84` "(delegate hard cases to `security`)" and
  `:91` "(delegate hard cases to `reliability`)" — reviewer has no `Task`.
- `.claude/agents/01-architect.md` (tail) "You hand off to `implementer` after
  `tester`" — architect has no `Task`.
- `.claude/agents/02-implementer.md` (precondition 4) "stop and hand off to
  `research-scout` for `ingest-library`" — implementer has no `Task`.
- `.claude/agents/04-tester.md:99` "hand back to `specify`" names a **protocol**,
  not an addressable agent — ambiguous return target.

A model reconciling "delegate to security" against "you have no Task tool"
under task pressure resolves it the cheap way: it does the work inline. The
prose teaches the over-reach it means to prevent.

### RC4 — Coarse roster; commission-expert path is heavyweight and advisory. (drives A; adjacent)
No fine-grained (language/framework) experts exist unless commissioned; the
commission path is multi-spawn and enforced only by prose
(`00-orchestrator.md:76–87, 208–210`; `core/AGENTS.md §1`). Under load, work
falls to a generic role. Addressed as an optional phase, not the core.

### RC5 — Enforcement is prose; the one hook cannot reach subagents. (why A & B persist)
The framework repeatedly states its enforcement does not reach where routing
happens: `00-orchestrator.md:93, 111, 211–212` ("the route-hook does not fire
for subagents … the brief is the only enforcement"); `grow.md:31`; and
`route-hook.py` fires only on the top-session `UserPromptSubmit`. So nothing
verifies the orchestrator picked the right specialist, and nothing verifies a
specialist handed back instead of over-reaching.

**One-line diagnosis:** the seed mechanized the *cheap* decision (which docs to
read) and left the *expensive* one (which expert does the work) to unassisted
judgment, then built a flat topology whose only safe move (clean handback) is
un-tooled, contradicted by "delegate" prose, and unenforced.

---

## 2. Chosen direction (fixed by the operator — do not re-open)

1. Build a mechanical **agent-router** (`agent-lint.py --route`) analogous to
   `graph-lint.py --plan`, backed by a new routing-trigger frontmatter field.
2. Give the **coordinating/authoring** specialists a **bounded, depth-capped**
   `Task` capability so they can spawn the correct sub-agent; keep leaf workers
   Task-less. Reconcile every RC3 prose line to match the tools.
3. Make it stick with a deliver-time / brief-level **routing-attribution
   assertion**; the brief and handback templates are the carrier because hooks
   don't reach subagents.
4. RC4 (roster / commission lightening) is an optional adjacent phase.

---

## 3. Decisions at ADR grade

> ~~When implementing, promote each of these to a real ADR under
> `docs/graph/decisions/adr-NNNN-*.md` using the `architect` conventions and the
> `templates/adr.template.md`, then link them here.~~
> **DONE (2026-07-13):** promoted to the seed's own self-docs decisions area, not
> the host application's graph — ADR-A → `../decisions/adr-0001-mechanical-agent-router.md`,
> ADR-B → `../decisions/adr-0002-bounded-delegation-hybrid.md`,
> ADR-C → `../decisions/adr-0003-enforcement-layering-honesty.md`, catalogued in
> `../decisions/index.md`. The `docs/graph/` home named above was the host
> *application's* graph and is off-limits to seed self-docs; the seed keeps its
> self-docs under `docs/` (this plan lives at `docs/plans/`, so decisions live at
> `docs/decisions/`). The ADR bodies below (§3) remain the faithful source; the
> standalone ADRs restate them and link back here.

### ADR-A — A mechanical agent-router (`agent-lint.py --route`) fed by `routing_triggers` frontmatter
- **Decision:** ship `agent-lint.py` mirroring `graph-lint.py`'s parser and
  IDF-weighted `resolve()`; add a `routing_triggers:` list to every agent's
  frontmatter as the high-signal index (the agent analog of a node's
  `load_when:`). `--route "<task>"` returns a ranked specialist list with scores
  and a confidence band, to be **cited in every delegation brief**.
- **Rationale:** the knowledge router is proven; give the expensive decision the
  same executable floor, confidence signal, and citable evidence. It is a
  *heuristic floor*, not an oracle — the orchestrator still reasons over it (same
  honesty as `context-router/SKILL.md` §"--plan is a keyword heuristic").
- **Rejected alternatives:**
  1. *Route on `description:` prose only (status quo, richer NLP).* No
     deterministic floor, not citable, doesn't improve consistency.
  2. *An LLM-judge router.* Adds a model call, cost, and non-determinism to
     every routing decision; the whole point is a cheap deterministic floor.
  3. *A hardcoded task→agent table inside orchestrator prose.* This is
     essentially today's worked-examples list; invisible to subagent briefs and
     doesn't scale as the roster grows.
- **Reversibility:** reversible — additive frontmatter + a new script; nothing
  breaks if the tool is removed.

### ADR-B — Bounded-delegation hybrid (5 delegators, leaf-only allowlists, depth ≤ 3), not strict-flat-handback
- **Decision:** grant depth-capped `Task` to a **small set of opus coordinators**
  whose definitions already name a legitimate sub-spawn, and keep **all leaf
  workers Task-less**. Delegation tiers:

  | Agent | `can_delegate` | `max_spawn_depth` | `delegates_to` (allowlist) |
  |---|---|---|---|
  | orchestrator | true | 3 | (all specialists) |
  | multi-agent-architect | true | 2 | architect, tester, implementer, reviewer, data-ml, security, reliability |
  | architect | true | 1 | tester, research-scout |
  | reviewer | true | 1 | security, reliability |
  | docs-librarian | true | 1 | research-scout |
  | implementer, tester, security, reliability, data-ml, product, research-scout, pentest | **false** | 0 | — (leaf; STOP + handback) |

  **Invariant:** an agent's `delegates_to` may name only agents whose
  `max_spawn_depth` is strictly less than its own. A depth-1 delegator can
  therefore reach only depth-0 leaves. The deepest legal chain is
  orchestrator(3) → multi-agent-architect(2) → architect(1) → leaf(0) = depth 3.
- **Rationale:** strict-flat keeps the orchestrator a bottleneck and turns every
  cross-domain need into a top-session round-trip; unbounded delegation risks
  runaway fan-out. The hybrid reconciles the RC3 prose (reviewer really can pull
  `security`; architect can pull a scout), while the leaf agents' *absence of
  `Task`* is the one **hard, harness-enforced** recursion cap (they literally
  cannot spawn). This reuses the multi-agent-architect definition's own pattern:
  clamp `max_spawn_depth` to `[1,3]` and give leaf agents no delegate tool so a
  leaf cannot recurse.
- **Rejected alternatives:**
  1. *Strict-flat + enforced handback for everyone.* Kills the RC3 ergonomics,
     multiplies orchestrator round-trips, and makes the orchestrator the single
     point of routing failure that RC1 already indicts.
  2. *Give every opus agent `Task`.* Blast radius for fan-out too large; loses
     the leaf guarantee that makes the depth cap real.
- **Reversibility:** reversible per agent (remove `Task` + the frontmatter caps).

### ADR-C — Enforcement layering, honestly labelled (tool-grant hard; caps soft; deliver-time detective)
- **Decision:** state the *effective* enforcement of each control, and never let
  a config field imply enforcement the harness does not provide:
  - **Hard (harness-enforced today):** which agents have `Task` in `tools`.
    Leaf agents lack it → they cannot spawn → recursion depth is bounded by the
    chain of Task-holders, which we keep short by granting Task to only 5 agents.
  - **Soft (contract-enforced):** `can_delegate`, `max_spawn_depth`,
    `delegates_to`. The current Claude Code `Task` tool does **not** read these
    fields or enforce a numeric depth / allowlist. They are enforced by
    `agent-lint.py --lint` (static), the agent prose, and the brief templates.
  - **Detective (post-hoc):** the deliver-time routing-attribution assertion
    (Phase 2) flags out-of-domain authoring and generic-role overrides; it runs
    in the **top session** at `deliver`, so it *can* be wired to a `Stop` hook —
    the one enforcement point that does not hit the subagent-hook limitation.
- **Rationale:** RC5 is precisely the "dormant-but-enabled" trap (a control that
  looks enforced but isn't). Shipping `max_spawn_depth: 1` as if the harness
  clamped it would repeat that trap. This ADR makes the real guarantees visible.
- **Rejected alternative:** claim the numeric caps are hard-enforced. Rejected —
  it would mislead operators exactly as the dormant telemetry plugins do.
- **Reversibility:** reversible.
- **Known limitation (carry into risks §6):** a Task-holding subagent could, in
  principle, spawn a subagent outside its `delegates_to` allowlist, because the
  harness won't block it. Mitigation: keep the delegating set tiny (5) and the
  allowlists leaf-only, and rely on the detective assertion to surface any
  violation. If/when a delegation wrapper or subagent-reaching PreToolUse hook
  exists, promote the soft caps to hard.

---

## 4. Design detail

### 4.1 Extended agent frontmatter schema
Today `templates/agent.template.md` mandates exactly four keys
(`name, description, tools, model`). Extend to:

```yaml
---
name: <kebab-id, == filename stem>
description: <prose, unchanged — still what a human/model reads>
tools: [<inline list>]                 # unchanged syntax
model: opus | sonnet
routing_triggers:                      # NEW — required, non-empty, block list
  - "make the test pass"               #   sharp task phrases; the router's index
  - "turn a failing test green"        #   (the agent analog of a node load_when)
can_delegate: true | false             # NEW — required; MUST equal (Task in tools)
max_spawn_depth: <int 1..3>            # NEW — required iff can_delegate: true
delegates_to:                          # NEW — required iff can_delegate: true
  - <agent-name>                       #   allowlist; each must have lower depth
---
```

Rules enforced by `agent-lint.py --lint`:
1. `routing_triggers` present and non-empty for every agent.
2. `can_delegate == (Task ∈ tools)` exactly. (No dormant-but-enabled drift.)
3. If `can_delegate`: `1 ≤ max_spawn_depth ≤ 3`; `delegates_to` present; every
   name in `delegates_to` exists and has `max_spawn_depth < this.max_spawn_depth`
   (leaves = 0). If `not can_delegate`: `max_spawn_depth`/`delegates_to` absent.
4. Warn when a trigger phrase is shared across "too many" agents (the IDF
   analog — a non-distinctive trigger carries no routing signal); this is the
   agent version of graph-lint's fact-distinctiveness discipline.

### 4.2 `agent-lint.py` — CLI and scoring (mirror `graph-lint.py`)
Location: install target `.claude/agent-lint.py`; seed source alongside
`route-hook.py`'s source in `cypress/integrations/claude-code/`.
Resolve the agents directory by walking up for `.claude/agents/` the way
`route-hook.py:find_lint()` walks up for `docs/graph/graph-lint.py`.

**Parser:** reuse `graph-lint.py`'s `parse_frontmatter`/`_scalar` approach, with
one addition — agent `tools:` is an **inline** list `[a, b, c]`, which the node
parser treats as a scalar string. Add inline-list parsing (`[ ... ]` →
`split(",")` → strip) so `tools` and any inline `routing_triggers` parse to
lists. Block-list `routing_triggers` (`- item`) already parses.

**Scoring** (mirror `resolve()` at graph-lint.py:336–394):
- `_terms(task)` — reuse verbatim (≥3-char terms, stopword-filtered, path-split).
- For each agent build two token sets: `name_toks` = tokens of `name`;
  `trigger_toks` = tokens of all `routing_triggers`; `desc_toks` = tokens of
  `description` (weak fallback).
- IDF `weight(t)`: term appearing in ≤1 agent → 3; ≤3 → 2; else 1 (identical to
  graph-lint's `weight`).
- `score(agent) = Σ_t weight(t) · max( 2·match(t, name_toks),
  2·match(t, trigger_toks), 1·match(t, desc_toks) )` where `match` is the
  2-exact / 1-prefix-fold / 0-none function from graph-lint (`_match`). Triggers
  and name are first-class (2×); description is the fallback (1×).
- Rank descending, tie-break on agent name.

**Confidence bands** (tunable; calibrate against the golden set in §4.3):
- `best == 0` → **NONE** ("no specialist matched — commission an expert; see
  RC4 / orchestrator commission path").
- `best < FLOOR` (FLOOR ≈ 6, i.e. two distinctive double-hits) → **LOW** (same
  commission recommendation).
- `best ≥ FLOOR` and `best ≥ 1.5 × second` → **HIGH**.
- otherwise → **MEDIUM** (pick top-1 but the orchestrator should confirm).

**CLI:**
- `agent-lint.py --route "<task>"` → prints the task, the ranked list, and the
  confidence band + hint. Output shape mirrors `graph-lint.py --plan`:

  ```
  task: make the failing auth test pass

  ROUTE (ranked, confidence: HIGH):
    implementer      opus   can_delegate=false   score=14
    tester           opus   can_delegate=false   score=6
  HINT: cite this in the delegation brief. HIGH → route to `implementer`.
        If you override to a different/generic agent, record why (deliver assertion checks this).
  ```
  For LOW/NONE, the hint reads: `no clear specialist — commission an expert
  from templates/agent.template.md, then delegate (RC4 path).`
- `agent-lint.py --lint` (default when no `--route`) → validate the frontmatter
  schema across all agents (§4.1 rules 1–4) and the delegation graph
  (ADR-B invariant); exit non-zero on any error. This is the P0/P1 gate.
- `agent-lint.py --eval` → run the golden routing set (§4.3), print top-1
  accuracy and any misroutes; exit non-zero below threshold. This is the eval
  gate wired *before* the router changes behavior.

**Honesty note (surface in the tool banner):** print
"Router suggestion is a keyword heuristic — reason over it" exactly as
route-hook.py:98 does, so no one mistakes it for an oracle.

### 4.3 Golden routing set (eval gate)
Ship `.claude/agents/_routes.golden.tsv` (underscore-prefixed so graph tooling
ignores it; seed mirror `cypress/agents/_routes.golden.tsv`). Two
columns: `task<TAB>expected_agent`. ~30–40 realistic developer phrases covering
each of the 13 agents (e.g. "write the ADR for splitting the service" →
architect; "the deploy is flaking under load" → reliability; "add a threat model
for the upload endpoint" → security; "generate synthetic fixtures for the eval"
→ data-ml). Include a few deliberately ambiguous/novel-stack phrases whose
expected result is **LOW/commission**. `--eval` asserts top-1 accuracy ≥ 90% and
that the novel-stack phrases return LOW. Owned/extended by `tester` + `data-ml`.

### 4.4 Standard handback payload (the RC5 carrier)
New template `templates/prompts/handback-payload.md` (seed mirror
`cypress/templates/prompts/handback-payload.md`). Every agent
(delegating or leaf) ends its turn with this block; it is the only reliable
carrier across the subagent boundary:

```
HANDBACK
- produced_by: <this agent name>
- status: complete | blocked-out-of-domain | needs-precondition
- in_domain_work_done: <what this agent legitimately did, with paths>
- out_of_domain_needed: <work this agent must NOT do itself>
- recommended_next: <agent name> + <protocol/step>   # e.g. security / threat-model
- route_evidence: <the agent-lint --route line that selected me, or the override rationale>
- gates: <commands run + results, or "none">
```

### 4.5 Deliver-time routing-attribution assertion (enforcement)
Add to `.protocols/deliver.md`: the delivery summary must attribute every unit
of work to a `produced_by` specialist (from the handback payloads). The
assertion, run by the orchestrator at `deliver` (top session):
- **Missing `produced_by` on any unit of work → BLOCK** (fail-closed; a missing
  proof is a block, never a pass).
- **Out-of-domain authoring** (a `produced_by` agent whose `routing_triggers`
  do not cover the work) → FLAG.
- **Generic-role override:** `agent-lint --route` returned HIGH for specialist X
  but the work was produced by a generic role (`general-purpose`/`claude`) or a
  different specialist with no recorded override rationale → FLAG.
Optionally wire a `Stop` hook in `.claude/settings.json` (top session only) that
greps the delivery summary / `grill.md` changelog for the attributions and
blocks on a missing one. Mark this hook **optional** and roll it out warn→block.

---

## 5. Exact per-file changes (every file to touch)

Apply each to **both** the live tree and the `cypress/` seed mirror.

### New files
1. `.claude/agent-lint.py` (+ seed source in
   `cypress/integrations/claude-code/`) — the router/linter/eval
   tool (§4.2).
2. `.claude/agents/_routes.golden.tsv` (+ seed mirror) — golden routing set
   (§4.3).
3. `templates/prompts/handback-payload.md` (+ seed mirror
   `cypress/templates/prompts/handback-payload.md`) — §4.4.

### Frontmatter edits — all 13 agent defs (`.claude/agents/*.md` + seed mirrors)
Add `routing_triggers` + `can_delegate` to **all 13**. Add `Task` to `tools` and
`max_spawn_depth` + `delegates_to` to the **5 delegators**:
- `00-orchestrator.md` — has Task; add `can_delegate: true`, `max_spawn_depth: 3`,
  `delegates_to: [all]`, `routing_triggers`.
- `multi-agent-architect.md` — has Task; add `can_delegate: true`,
  `max_spawn_depth: 2`, `delegates_to: […]`, `routing_triggers`.
- `01-architect.md` — **add `Task` to tools**; `can_delegate: true`,
  `max_spawn_depth: 1`, `delegates_to: [tester, research-scout]`, triggers.
- `03-reviewer.md` — **add `Task` to tools**; `can_delegate: true`,
  `max_spawn_depth: 1`, `delegates_to: [security, reliability]`, triggers.
- `09-docs-librarian.md` — **add `Task` to tools**; `can_delegate: true`,
  `max_spawn_depth: 1`, `delegates_to: [research-scout]`, triggers.
- `02-implementer.md`, `04-tester.md`, `05-security.md`, `06-reliability.md`,
  `07-data-ml.md`, `08-product.md`, `10-research-scout.md`, `11-pentest.md` —
  `can_delegate: false`, no `max_spawn_depth`/`delegates_to`, add `routing_triggers`.

### RC3 prose reconciliation
- `03-reviewer.md:84` — "(delegate hard cases to `security`)" → "(spawn
  `security` via bounded Task, depth 1, then fold its findings into your review)".
- `03-reviewer.md:91` — same for `reliability`.
- `01-architect.md` (tail, "What you do not do") — "You hand off to `implementer`
  after `tester`" → "You produce handoff briefs for `tester` and `implementer`
  and **STOP** with a handback payload; you do not spawn `implementer` (writing
  code is a separately authorized RED-gated increment). You *may* spawn `tester`
  or `research-scout` via bounded Task to confirm a contract is testable or a
  fact is current."
- `02-implementer.md` (precondition 4) — "stop and hand off to `research-scout`"
  → "**STOP** and return a handback payload naming `research-scout` /
  `ingest-library` as the required next step" (implementer is a leaf; no Task).
- `04-tester.md:99` — "hand back to `specify`" → "**STOP** and return a handback
  payload: the missing contract + recommend the orchestrator enter `specify` via
  `product`/`architect`" (name an addressable agent, not just the protocol).

### Template + protocol + kernel edits
- `templates/agent.template.md` — replace the "EXACTLY four keys" contract with
  the extended schema (§4.1); add the handback block to the template body; add
  the `agent-lint --route` + handback discipline to "Context you load first".
- `.claude/agents/00-orchestrator.md` "Specialist routing" (56–155) — add the
  mandatory step: run `python3 .claude/agent-lint.py --route "<task>"`, cite its
  output in the brief, and on LOW/NONE confidence take the commission path.
- `templates/prompts/investigation-brief.md`, `node-authoring-brief.md`,
  `clean-context-validation-brief.md` — add (a) `agent-lint --route` evidence
  requirement, (b) the handback-payload requirement, (c) for delegators, the
  bounded-Task rules (allowlist + depth).
- `.protocols/deliver.md` — add the routing-attribution assertion (§4.5).
- `.protocols/grow.md` (16–43 "Mandatory worker topology") — add: each spawn
  cites `agent-lint --route`; delegating workers obey allowlist + depth caps.
- `core/AGENTS.md` (== `CLAUDE.md`) §1 and §4 — document the router and the
  delegation tiers; make LOW router confidence the trigger for the commission
  rule. Mirror in `cypress/core/AGENTS.md`.
- `.claude/settings.json` (+ seed mirror
  `cypress/integrations/claude-code/settings.json`) — **optional
  (P2)**: add the top-session `Stop` hook for the deliver assertion.

---

## 6. Phased roadmap

Smallest/safest first. Each phase is independently shippable and reversible.

### P0 — Additive router (zero behavior change)
- **Problem:** no mechanical agent selection (RC1).
- **Change:** add `routing_triggers` + `can_delegate` (reflecting *current*
  tools: only orchestrator + multi-agent-architect true) to all 13 agents.
  Ship `agent-lint.py` with `--route`, `--lint`, `--eval`. Ship the golden set.
  Update orchestrator prose to run/cite `--route`. **No tool grants change.**
- **Acceptance criteria:**
  - `agent-lint.py --lint` passes (schema rules 1–4, ADR-B invariant trivially
    holds since only 2 delegators, both already had Task).
  - `agent-lint.py --eval` ≥ 90% top-1 on the golden set; novel-stack phrases
    return LOW.
  - `--route` for each of ~13 representative tasks returns the intended
    specialist at MEDIUM+; output is citable in a brief.
  - No agent gains or loses a tool.
- **Files:** new `agent-lint.py`, `_routes.golden.tsv`; frontmatter of all 13;
  `00-orchestrator.md`; `templates/agent.template.md`.
- **Risk:** low (new script + additive frontmatter). **Verify:** `--lint`,
  `--eval`, manual spot-check; confirm `route-hook.py`/`graph-lint.py` untouched
  and still green.

### P1 — Bounded Task + prose reconciliation
- **Problem:** 11/13 cannot delegate (RC2); "delegate" prose is unbacked (RC3).
- **Change:** add `Task` to architect/reviewer/docs-librarian; add
  `max_spawn_depth` + `delegates_to` to the 5 delegators; set leaves
  `can_delegate: false`; apply the RC3 prose edits.
- **Acceptance criteria:**
  - `agent-lint.py --lint` now enforces `can_delegate == (Task ∈ tools)`, depth
    ∈ [1,3], and the strictly-decreasing-depth allowlist invariant; passes.
  - No leaf agent holds `Task`; a hand proof from the `delegates_to` graph shows
    no chain exceeds depth 3.
  - Every former "delegate to peer X" line either maps to a `delegates_to` entry
    or is rewritten to STOP + handback; `grep -n "delegate" .claude/agents/*.md`
    shows no unbacked delegation prose.
- **Files:** frontmatter of `01`, `03`, `09` (+ Task) and the other delegators;
  RC3 prose in `01`, `02`, `03`, `04`.
- **Risk:** **MEDIUM — runaway fan-out (the big one).** **Mitigations:** tiny
  delegating set (5); leaf-only allowlists; strictly-decreasing depth; the hard
  cap that leaves lack `Task`; detective assertion lands in P2. **Verify:**
  `--lint` depth/allowlist checks; a smoke test spawning architect→tester and
  confirming tester (leaf) has no Task to recurse with; confirm the deepest
  legal chain manually.

### P2 — Handback payload + deliver-time routing assertion (make it stick)
- **Problem:** nothing verifies routing or handback (RC5).
- **Change:** ship `handback-payload.md`; wire it into every agent def and the
  three brief templates; add the produced_by assertion to `deliver.md`;
  optionally add the top-session `Stop` hook.
- **Acceptance criteria:**
  - Every brief template requires `--route` evidence + a handback payload.
  - `deliver` BLOCKS (fail-closed) when any unit of work lacks `produced_by`;
    PASSES when all are attributed.
  - A HIGH-confidence route overridden to a generic role with no recorded
    rationale is FLAGGED.
- **Files:** `templates/prompts/handback-payload.md`; all 13 agent defs (add the
  handback section); the 3 brief templates; `.protocols/deliver.md`;
  `.protocols/grow.md`; `core/AGENTS.md`; optionally `.claude/settings.json`.
- **Risk:** low–medium (false-positive blocks). **Mitigation:** warn→block
  rollout; assertion defaults missing→BLOCK per the fail-closed rule. **Verify:**
  a sample delivery with a missing attribution asserts BLOCK; with attributions
  asserts PASS.

### P3 — Optional: RC4 roster / commission lightening
- **Problem:** heavyweight, advisory commission path pushes work to generic roles.
- **Change:** make LOW/NONE `--route` confidence the mechanical trigger for the
  commission rule; combine "author the expert" + "delegate to it" into one step
  in the template/orchestrator flow.
- **Acceptance criteria:** a novel-stack task scored LOW produces a commission
  recommendation in the orchestrator flow; commission is a single spawn.
- **Files:** `templates/agent.template.md`; `00-orchestrator.md` commission
  section; `core/AGENTS.md §1`.
- **Risk:** low. **Verify:** a deliberately novel-stack task → `--route` LOW →
  commission path invoked.

---

## 7. Risks and mitigations (consolidated)

| Risk | Severity | Mitigation | Verified by |
|---|---|---|---|
| Runaway fan-out once specialists can spawn | HIGH | Tiny delegating set (5); leaf agents have no `Task` (hard cap); strictly-decreasing depth allowlists; depth ≤ 3 | `agent-lint --lint` invariant + hand chain-depth proof (P1) |
| Soft caps look enforced but aren't (dormant-but-enabled trap / RC5) | HIGH | ADR-C labels each control's real enforcement; `--lint` asserts `can_delegate == (Task ∈ tools)`; detective assertion at deliver | ADR-C; `--lint`; deliver assertion (P2) |
| Router misroutes (keyword heuristic ≠ oracle) | MEDIUM | Treat as a floor, not an oracle; confidence bands; golden-set eval gate; orchestrator reasons over it and may override with recorded rationale | `--eval` ≥ 90% (P0); deliver override-rationale flag (P2) |
| Subagent spawns outside its allowlist (harness won't block) | MEDIUM | Keep set tiny + allowlists leaf-only; detective assertion surfaces it; promote to hard cap when a delegation wrapper/PreToolUse-for-subagents exists | Deliver assertion (P2); noted as known limitation |
| Trigger phrases collide across agents (low routing signal) | LOW | `--lint` warns on non-distinctive triggers (IDF analog); sharpen in the same change | `--lint` warnings (P0) |
| Two source trees (live vs seed) drift | LOW | Every edit applied to both; a follow-up parity check `diff` between `.claude/agents` and `cypress/agents` | manual/CI diff |
| Green-lie: adding the deliver gate before attributions exist | LOW | Land the handback payload (the checked thing) before the gate that checks it (kernel §3.5) | P2 sequencing |

---

## 8. Verification summary (per phase)
- **P0:** `agent-lint.py --lint` (schema) + `--eval` (golden ≥ 90%) + manual
  route spot-check; knowledge router untouched.
- **P1:** `--lint` delegation-graph invariant + chain-depth proof + leaf-cannot-
  recurse smoke test + `grep` for unbacked "delegate" prose.
- **P2:** deliver-assertion pass/block tests (missing vs present attribution);
  override-flag test.
- **P3:** novel-stack task → LOW → commission-path test.

All gate commands and results are to be recorded in
`docs/graph/runbooks/verification.md` when implemented (kernel §3.5). Do not add
a gate in the same increment as the first thing it checks (land the check, then
the gate).

---

## 9. Changelog stub
- 2026-07-13 — Plan authored (multi-agent-architect). Design/plan only; no code
  changed. Direction fixed by operator: mechanical agent-router + bounded
  delegation + deliver-time attribution. RC4 optional. ~~Decisions ADR-A/B/C
  pending promotion to `docs/graph/decisions/`.~~ (Superseded 2026-07-13: promoted
  to `docs/decisions/adr-0001..0003` — the seed's self-docs, not the host
  application's graph. See §3 note.)

- 2026-07-13 — **P0 implemented + verified** (tester RED → implementer GREEN, per
  §3.4). Shipped the mechanical agent-router `agent-lint.py`
  (`--route`/`--lint`/`--eval`, IDF-weighted `resolve()` mirroring
  `graph-lint.py`, confidence bands, inline-`tools` list parser) at
  `.claude/agent-lint.py` with seed source
  `integrations/claude-code/agent-lint.py`. Added `routing_triggers` +
  `can_delegate` frontmatter to all 13 agents (reflecting *current* tools: only
  orchestrator + multi-agent-architect `can_delegate: true`). Shipped the golden
  routing set `_routes.golden.tsv` (byte-identical copies in `agents/` and
  `.claude/agents/`). **Correction to the plan's §4.2 estimate:** the confidence
  **FLOOR was calibrated to 13** (not the "≈6" guessed at §4.2) against the golden
  set — the plan's placeholder was a genuine mis-estimate, fixed here; §4.2 left
  as the historical estimate, this entry is the authority.

- 2026-07-13 — **P1 implemented + verified.** Granted bounded `Task` to the 5
  delegators (orchestrator depth 3; multi-agent-architect depth 2;
  architect/reviewer/docs-librarian depth 1) and kept the 8 leaf workers
  Task-less. Added `max_spawn_depth` + `delegates_to` allowlists enforcing the
  ADR-B strictly-decreasing-depth invariant. Applied the 5 RC3 prose
  reconciliations (reviewer×2, architect, implementer, tester). Shipped
  `templates/prompts/handback-payload.md` (the RC5 cross-boundary carrier, §4.4).

- 2026-07-13 — **P2 implemented + verified.** Added the handback section to all 13
  agents; made the orchestrator `--route` step mandatory; updated the 3 brief
  templates (investigation / node-authoring / clean-context-validation) to require
  `--route` evidence + a handback payload; added the fail-closed `produced_by`
  routing-attribution assertion to `deliver.md`; updated `grow.md`, `core/AGENTS.md`
  (== `CLAUDE.md`), and `templates/agent.template.md` body. Per ADR-C green-lie
  discipline the top-session `Stop` hook was **deliberately left UNWIRED** and
  documented as a deferred warn→block follow-up (land the check before the gate).

- 2026-07-13 — **Reviewer audit: verdict SHIP-WITH-MINORS.** 1 Major (the installer
  shipped the router dead — `install.sh` did not copy `agent-lint.py` /
  `_routes.golden.tsv` into a claude-code install) + Minors. **All fixed:**
  `install.sh` now copies both artifacts (scratch-install proven: `--route` and
  `--eval` exit 0 in both copy and symlink modes); `multi-agent-architect.md`
  `delegate_task` → `Task`; tester added 5 regression guards (4 ADR-B
  depth-invariant negatives + golden parity).

- 2026-07-13 — **Verified gates (recorded verbatim as run; one home for these
  results — link here, do not re-copy):**
  - `python3 .claude/agent-lint.py --lint` → `OK — 13 agents, frontmatter and
    delegation graph valid`.
  - `python3 .claude/agent-lint.py --eval` → 100% top-1 (33/33); novel-stack
    phrases return LOW/NONE as intended.
  - `pytest cypress/tests/test_agent_lint.py -q` → **44 passed**.
  - `python3 docs/graph/graph-lint.py` → `OK — 20 nodes` (knowledge router
    untouched by this increment; confirms no regression).
  - Scratch install of the claude-code adapter → `--route` and `--eval` **exit 0**
    (copy mode and symlink mode).

- P3 (RC4 roster / commission lightening) — **not done**; remains the optional
  adjacent phase per §2.4 and §6.

---

## 10. Next step (single, highest-leverage)
Have `tester` write RED tests for `agent-lint.py` P0 — `--lint` schema
validation and `--route` scoring/confidence against the golden set — **before**
`implementer` writes the tool. That is the smallest increment that turns this
plan executable while honoring test-first.
