<!-- CYPRESS seed — Prime Agent native-execution overlay.
     Installed to .prime/agent/APPEND_SYSTEM.md by `install.sh prime-agent`.
     Prime Agent APPENDS this to the system prompt on every session; Claude Code
     never reads it. It does NOT replace the kernel (AGENTS.md) — it teaches you
     to run the kernel's discipline with Prime Agent's NATIVE primitives, which
     Claude Code lacks. Nothing here overrides the kernel, a spec, or a gate. -->

# Running CYPRESS natively on Prime Agent

You are executing the CYPRESS seed on Prime Agent. Obey the kernel
(`AGENTS.md`): route first through `docs/graph/index.md`, classify the tier,
then follow the protocol. Do the *doing* with your native RLM primitives — do
not emulate a file-based harness.

## Delegation — recursive subagents, not a Task tool

For every T2/T3 unit of *doing* (investigating a subsystem, writing a spec, a
test, code, or a doc), spawn a clean-context child instead of doing it inline:

- **Read the roster brief, then spawn.** The specialists live as brief sources
  in `.prime/agent/agents/<role>.md` (there is no session-start roster to
  enumerate — a brief on disk is usable by the very next call). Load the brief
  and pass it into the child:
  `brief = Path(".prime/agent/agents/01-architect.md").read_text()`;
  `await rlm(brief + "\n\n<TASK>...</TASK>", name="architect", model=...)`.
- **Fan out narrow, in parallel.** Decompose the work into MULTIPLE
  single-scoped children and spawn them in one turn (several `rlm()` calls),
  each owning one facet and writing its own report file. Never hand one broad
  child the whole job. Then end the turn; do not poll with sleep.
- **Model + effort policy — Prime Agent picks model VERSIONS per spawn (Claude
  Code cannot), so match the spawn to the task kind and set thinking/effort to
  the tier.** The roster brief's `model:` field is the class floor; this refines
  it by task kind:

  | Task kind | Model | Effort |
  |---|---|---|
  | Watching logs, polling, trivial checks | Haiku 4.5 | low |
  | Read-only inventory, measurement, counting | Sonnet 5 | low–medium |
  | Research & scouting with sources | Opus 4.6 | medium–high |
  | Routine implementation behind a gate | Opus 4.6 | medium |
  | Planning, ADR drafting, design | Opus 4.8 | high |
  | Crypto, token issuer, one-way doors | Opus 5 | high |

  Resolve the selector at spawn with `await rlm.find_models("<family/version>")`
  and pass the returned `.selector` to `rlm(..., model=...)`. If a named version
  is absent from the catalog, fall back to the nearest-HIGHER available in the
  same family, never lower; omit `model` (inherit) only as a last resort. Never
  a weaker default for seed work, and never over-provision — a docs edit behind
  a linter gate is routine-behind-a-gate, not design.
- **The meta-loop protocols pick the version per phase.** The table above is for
  arbitrary tasks. `grow`, `harvest`, and `graft` tag every phase with a model
  *class* in their own nodes — that class is the single home, and the seed's
  tool-neutral core never names a vendor version. On Prime Agent each class
  resolves to a version inside its OWN family, never across families; this table
  refines the one above for those three protocols and wins where they overlap:

  | Protocol · phase | Class | Model | Effort |
  |---|---|---|---|
  | grow · scout source discovery | sonnet | Sonnet 4.6 | low–medium |
  | grow · research-scout, external sources | sonnet | Sonnet 5 | medium–high |
  | grow · node authoring (behind graph-lint) | opus | Opus 4.6 | medium |
  | grow · reconcile contradictory ledgers | opus | Opus 4.8 | high |
  | grow · librarian final pass | opus | Opus 4.8 | high |
  | harvest · Phase 1 survey | sonnet | Sonnet 4.6 | low–medium |
  | harvest · Phase 2 triage (three gates, generalize) | opus | Opus 4.8 | high |
  | harvest · Phase 3 backport authoring | opus | Opus 4.8 · Opus 5 if it lands in the kernel | high |
  | harvest · Phase 4 G3 independent review | opus | Opus 4.8 | high |
  | graft · Phase 1 locate plant / base | sonnet | Sonnet 4.6 | low |
  | graft · Phase 2 survey drift | sonnet | Sonnet 4.6 | low–medium |
  | graft · Phase 3 reconcile machinery | opus | Opus 4.8 | high |
  | graft · Phase 4 refresh from corpus | opus | Opus 4.6 | medium |
  | graft · Phase 5 grow new capabilities | opus | Opus 4.6 | medium |
  | graft · Phase 6 rebalance: inventory | sonnet | Sonnet 4.6 | low–medium |
  | graft · Phase 6 rebalance: reconstruct | opus | Opus 4.6 | medium |
  | graft · Phase 7 apply / verify / stamp | opus | Opus 4.8 · Opus 5 (writes into a living plant) | high |

  Default opus work to **Opus 4.6** — routine authoring behind a gate, about a
  third fewer tokens than 4.8. Spend **Opus 4.8** on judgment: triage,
  reconciliation, a 3-way merge, adversarial review. Spend **Opus 5** only on
  the highest blast radius — an edit that lands in the kernel, or a write into a
  living plant. Read-only survey stays **Sonnet 4.6**; source-grounded scouting
  rises to **Sonnet 5**, the only sonnet rung above 4.6. Resolve and fall back
  by the same rule as the generic table above.
- **Collect handbacks by message.** A child returns results with
  `await agent_message.send(payload, receiver_role="parent")`; you fan-in on
  later turns. Use `agent_observe` to inspect a child's rollout and
  `rlm.list_subagents()` to recover handles. Delete finished children with
  `rlm.delete_subagent(...)`.

## Gates — run them in this kernel

The verify discipline assumes you can run the gate. Run it directly in the
IPython kernel (`bash tests/run.sh`, the linters, the test suite) and keep the
evidence in variables. That is your native tool; use it instead of asking a
harness to shell out.

## Close-out — three destinations, routed by what the artifact IS

A reusable win has exactly one correct home; the three do not overlap.

- **Project knowledge** (structure, decisions, specs) → `docs/graph/`, via
  canonize. Unchanged from Claude Code.
- **A durable TOOL or a project SKILL** — the §3.8 toolcraft artifact,
  including any Agent-Skills `SKILL.md` you author for this plant → it belongs
  **in the plant**. Per `skill.toolcraft`, a project skill's home is the
  graph node `docs/graph/skills/<name>.md`, and you project it into the harness
  dir this plant actually uses: `.prime/agent/skills/<name>/SKILL.md` (the dir
  this plant's `settings.json` already discovers), committed to the plant's git
  so the team and CI share it. NEVER accept skill-creator's default drop into
  the GLOBAL `~/.prime/agent/skills/` (private to you, uncommitted, invisible
  to the team) and NEVER stash a project skill in the continual harness.
- **A cross-session OPERATING lesson** (a durable fact, a reusable delegation
  role, an agent-operating procedure or preference that is NOT a plant
  deliverable) → the **continual harness** via `await refine.run(...)`
  (memories, subagent specs, prompt notes). This is Prime Agent's own memory,
  private to you across sessions — a complement to the graph, never a
  substitute for a plant tool or skill.

Do not let a reusable win evaporate with the session — but put it where its
owner can find it.

## Long-running work

For multi-phase or slow work, drive a nonblocking control loop: start children
or gates, record their handles/output locations, end the turn, and read results
when replies arrive. Use `goal` to hold the objective across turns and
`rlm_heartbeat` when the user asks for scheduled progress. Give the user concise
progress updates at milestones.

## What stays identical to Claude Code

Tier table, the eight rules, spec-driven contracts, progressive discovery, and
the roster/skills/command set — all shared from the same `docs/graph/` nodes.
The difference is only in *how you execute*: RLM-native, in this kernel.
