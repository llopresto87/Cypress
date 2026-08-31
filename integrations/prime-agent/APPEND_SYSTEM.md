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
- **Model policy (from the roster's `model:` field).** Read-only
  scouting / inventory / extraction / evidence → Sonnet-class, floor
  `anthropic/claude-sonnet-4-6`. Authoring / synthesis / architecture / code →
  Opus-class (`anthropic/claude-opus-4-5`+). Never a weaker default for seed
  work. Resolve with `await rlm.find_models(...)`.
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

## Close-out — persist to the graph AND the continual harness

Canonize still writes durable knowledge into `docs/graph/`. Prime Agent adds a
second, cross-session memory Claude Code has no equivalent for: the **continual
harness**. After a task, when a lesson, procedure, durable fact, or reusable
delegation role emerged, persist it with `await refine.run(...)` (memories,
skills, subagent specs, prompt notes). Keep project-knowledge in the graph;
keep reusable *operating* lessons in the harness. Do not let a reusable win
evaporate with the session.

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
