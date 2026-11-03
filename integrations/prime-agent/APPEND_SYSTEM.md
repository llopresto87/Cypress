# CYPRESS on Prime Agent

The kernel (`AGENTS.md`) and `docs/graph/` govern; this overlay only maps them
onto RLM children, the IPython kernel and agent messaging.

## Delegation — recursive subagents, not a Task tool

For every T2/T3 unit of *doing* (investigating a subsystem, writing a spec, a
test, code, or a doc), spawn a clean-context child instead of doing it inline:

- **Compose the brief, then spawn.** There is no session-start roster; the
  composer carries the role's charter, both bootstrap blocks and the handback
  block, so you read none of them:
  `brief = (await bash('python3 docs/graph/brief.py --role architect --charter --spawn-id <id> --task "<task line>" --route "<routing evidence>" --part task.md')).output`;
  `await rlm.spawn(brief, name="<spawn-id>", model=..., thinking=...)`; the
  name pairs each reply with its spawn in the spawn log.
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
  later turns. New work goes to a fresh child, even when an old one knows the
  area: message a finished child only for a small follow-up that needs its
  context; resume only a child a limit, network or provider error cut off
  mid-turn (`delegation.continuation`). Use `agent_observe` to inspect a child's rollout and
  `rlm.list_subagents()` to recover handles. Keep finished children: their
  sessions are the trajectory record the work is audited from.

## Gates — run them in this kernel

The verify discipline assumes you can run the gate. Run it directly in the
IPython kernel (`bash tests/run.sh`, the linters, the test suite) and keep the
evidence in variables. That is your native tool.

## Close-out

Project knowledge goes to `docs/graph/` through canonize. A project skill's home
is `docs/graph/skills/<name>.md`, projected to `.prime/agent/skills/<name>/SKILL.md`
and committed (`skill.toolcraft`); redirect skill-creator's global default there.
A cross-session lesson goes to the session record (`method.stewardship-posture`);
`rlm.harness` keeps at most a pointer to it.

## Long-running work

Start children or gates, record their handles, end the turn, read the replies.
When every open step is the owner's, list them once, numbered, and stop
(`protocol.deliver`).
