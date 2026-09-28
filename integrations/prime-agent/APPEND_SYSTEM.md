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

  Opus-class work runs on **Opus 5.5**; use **Opus 4.6** only for extremely
  light authoring that Sonnet should not be trusted with. The Sonnet floor is
  Sonnet 4.6 or newer. `grow`, `harvest` and `graft` name each phase's model
  class in their own nodes, the single home, and this rule maps it to a version.

  Resolve the selector at spawn with `await rlm.find_models("<family/version>")`
  and pass the returned `.selector` to `rlm(..., model=...)`. If a named version
  is absent from the catalog, fall back to the nearest-HIGHER available in the
  same family, never lower; omit `model` (inherit) only as a last resort. Never
  a weaker default for seed work, and never over-provision.
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

## Surfaced nodes

Keep a Python set of graph node ids, `_cypress_surfaced`, in the IPython
kernel, and add each id whose node body you open. Before opening a body the
router suggests, check the set. An id in it means surfaced earlier this
session: re-open it if its content is not in view. IPython state outlives
compaction; your context does not.

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
- **A cross-session OPERATING lesson** (an owner rule, a corrected assumption,
  where paused work stands) → the plant's **session record** in
  `docs/graph/plans/sessions/` (`method.stewardship-posture`), written when you
  learn it; canonize files it into the graph. The continual harness
  (`refine.run(...)`) is private to you and keeps at most a one-line pointer
  to that directory, never the lesson itself.

Do not let a reusable win evaporate with the session — but put it where its
owner can find it.

## Long-running work

For multi-phase or slow work, drive a nonblocking control loop: start children
or gates, record their handles/output locations, end the turn, and read results
when replies arrive. Use `goal` to hold the objective across turns and
`rlm_heartbeat` when the user asks for scheduled progress. Give the user concise
progress updates at milestones.
A `goal` or heartbeat exits when every open step is the user's: list those steps
once, numbered, then stop (`docs/graph/protocols/deliver.md`, "When every open
step is the owner's").

## What stays identical to Claude Code

Tier table, the eight rules, spec-driven contracts, progressive discovery, and
the roster/skills/command set — all shared from the same `docs/graph/` nodes.
The difference is only in *how you execute*: RLM-native, in this kernel.
