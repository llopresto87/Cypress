<!-- CYPRESS seed — Prime Agent native-execution overlay.
     Installed to .prime/agent/APPEND_SYSTEM.md by `install.sh prime-agent`.
     Prime Agent appends this file to every system prompt. -->

# Running CYPRESS natively on Prime Agent

You are executing the CYPRESS seed on Prime Agent. Obey the kernel
(`AGENTS.md`): route first through `docs/graph/index.md`, classify the tier,
then follow the protocol. The tier table, the eight rules, the specs and the
roster, skills and commands all come from the shared `docs/graph/` nodes; this
overlay overrides no kernel rule, spec or gate. It only maps the kernel's
discipline onto your native RLM primitives: spawned children, the IPython
kernel and agent messaging.

## Delegation — recursive subagents, not a Task tool

For every T2/T3 unit of *doing* (investigating a subsystem, writing a spec, a
test, code, or a doc), spawn a clean-context child instead of doing it inline:

- **Read the roster brief, then spawn.** The specialists live as brief sources
  in `.prime/agent/agents/<role>.md` (there is no session-start roster to
  enumerate — a brief on disk is usable by the very next call). Load the brief
  and pass it into the child:
  `brief = Path(".prime/agent/agents/01-architect.md").read_text()`;
  `await rlm.spawn(brief + "\n\n<TASK>...</TASK>", name="architect", model=..., thinking=...)`.
- **Fan out narrow, in parallel.** Give each child one facet and its own
  report file, and spawn them in one turn (several `rlm.spawn()` calls): a
  narrow brief keeps each context clean and each report checkable. Then end
  the turn; replies arrive as messages.
- **Model and effort come from the plant's model map.** The roster brief's
  `model:` field names the class (`opus` is the authoring class, `sonnet` the
  investigation class, `haiku` the investigation-low row) and the brief's
  routing evidence names the effort. Find that row in `docs/graph/models.md`,
  Prime Agent column, resolve the selector with
  `await rlm.find_models("<selector>")`, and spawn with
  `rlm.spawn(..., model=<its .selector>, thinking=<effort>)`. Run only a
  selector the map lists. When it does not resolve, stop and report it. When
  the row is unfilled, or the field says `inherit`, omit `model=` so the child
  inherits your model, and write `model: inherited (map row unfilled)` or
  `model: inherited (inherit)` in the routing evidence.
- **Collect handbacks by message.** A child returns results with
  `await agent_message.send(payload, receiver_role="parent")`; you fan-in on
  later turns. Use `agent_observe` to inspect a child's rollout and
  `rlm.list_subagents()` to recover handles. Delete finished children with
  `rlm.delete_subagent(...)`.

## Gates — run them in this kernel

The verify discipline assumes you can run the gate. Run it directly in the
IPython kernel (`bash tests/run.sh`, the linters, the test suite) and keep the
evidence in variables. That is your native tool.

## Surfaced nodes

Keep a Python set of graph node ids, `_cypress_surfaced`, in the IPython
kernel, and add each id whose node body you open. Before opening a body the
router suggests, check the set. An id in it means surfaced earlier this
session: re-open it if its content is not in view. IPython state outlives
compaction; your context does not.

## Close-out — three destinations, routed by what the artifact is

Persist every reusable win before the session ends, in the one home below that
fits it; the three do not overlap.

- **Project knowledge** (structure, decisions, specs) → `docs/graph/`, via
  canonize.
- **A durable tool or a project skill** — the §3.8 toolcraft artifact,
  including any Agent-Skills `SKILL.md` you author for this plant → it belongs
  **in the plant**. Per `skill.toolcraft`, a project skill's home is the
  graph node `docs/graph/skills/<name>.md`, and you project it into the harness
  dir this plant actually uses: `.prime/agent/skills/<name>/SKILL.md` (the dir
  this plant's `settings.json` already discovers), committed to the plant's git
  so the team and CI share it. When skill-creator offers its global default
  `~/.prime/agent/skills/`, redirect it to this path: the global directory and
  the continual harness are private to you, uncommitted and invisible to the
  team.
- **A cross-session operating lesson** (an owner rule, a corrected assumption,
  where paused work stands) → the plant's **session record** in
  `docs/graph/plans/sessions/` (`method.stewardship-posture`), written when you
  learn it; canonize files it into the graph. The continual harness
  (`rlm.harness`) is private to you and keeps at most a one-line pointer to
  that directory; the lesson lives in the record.

## Long-running work

For multi-phase or slow work, drive a nonblocking control loop: start children
or gates, record their handles/output locations, end the turn, and read results
when replies arrive. Use `goal` to hold the objective across turns and
`rlm_heartbeat` when the user asks for scheduled progress; a `goal` or
heartbeat exits when every open step is the user's: list those steps once,
numbered, then stop (`docs/graph/protocols/deliver.md`, "When every open step
is the owner's"). Give the user concise progress updates at milestones.
