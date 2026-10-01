---
status: accepted
status_date: 2026-10-01
owner: seed steward
---

# ADR-0024: one Python hook core gives every hooked host per-session residency; children and non-human turns are not routed

## Status

See frontmatter, which is the single home. Filed 2026-10-01 for 7.37.0 from
the owner's ruling D1 of that round, kept with the round's working records
outside the seed. The increments it names landed in the same round, the live
host probes held, and the record was flipped to `accepted` at the release pass
of 2026-10-01. It supersedes [ADR-0010](adr-0010-context-residency.md) in part: the
prime-agent row of its per-host table, and its two rejected alternatives for a
Prime Agent ledger, which were rejected "by owner choice". ADR-0010's
Residency Rule, its Claude Code design, its threat model and its evidence
stand.

## Date

2026-10-01

## Context

ADR-0010 gave Claude Code a session ledger: the first routed prompt gets the
full router text, later prompts get a reminder that names known nodes by id,
and `status-hook.py` resets the ledger at every session start. Prime Agent got
none of it. Its `route-extension.ts` keeps no state and injects the full text
on every prompt, and a model-kept set, `_cypress_surfaced`, was meant to stop
re-reads. The owner chose that design on 2026-09-23.

The round's investigation and its refutation pass, kept with the round's
working records outside the seed, measured real Prime Agent transcripts. The
largest measured session had ten routed prompts and six spawned children, and
processed 30.5M tokens:

- Injected route and status text was 4.5% of all processed tokens. Children
  held 86% of the session's tokens, and each child's injected route and status
  was 3.0% to 4.3% of its own.
- Every `rlm()` child is routed on its whole brief (about 8.5 KB, 25 to 29
  LOAD nodes, a wide-descent notice). The brief already tells the child to run
  `--plan` on its task line (GRAPH DISCIPLINE step 1), so the injected route
  is a second route on the wrong input. Children opened 0 to 10 of those
  suggested nodes.
- In the parent, 79% of the characters of the nine follow-up routes were entry
  lines for ids an earlier route had already printed. A replay of 22 real
  short sessions (two to five prompts) through the router found 66%.
- `status-extension.ts` injects once per process (`let shown`), so every child
  gets the status register and the code anchor too, and a compacted parent
  never sees them again.
- An `agent_message` delivered to an idle child fires `before_agent_start` and
  is routed; four deliveries to the parent produced no route. On Claude Code,
  28 of 81 routed turns in one transcript were not typed by a person: peer
  messages, task notifications and auto-continuations.
- `ctx.sessionManager.getSessionId()` exists on the extension context, so the
  reason ADR-0010 gave for a stateless extension, "no session id on this
  event", no longer holds.

The full text on every Prime Agent prompt is not a regression. The seed's
`route-extension.ts` has injected in full in every version since it was
written. The steward plant ran no route extension on Prime Agent until its
graft of 2026-10-01, and has run the Claude Code ledger since its graft of
2026-09-29. The difference the owner saw is the gap between the two hosts.

The owner's ruling D1 on Prime Agent residency: "aboslutely". His goal for the
round: "it's not about being fast but about being cheaper by token count wasted
by the model, and redundant information if it can be gleaned mechanically.
plus the issue with prime agent restating everything in full every time."

## Decision

`integrations/claude-code/route-hook.py` and `status-hook.py` become the one
residency core for every host that has a session id: `install.sh prime-agent`
places byte-identical copies at `.prime/agent/hooks/`, the two Prime Agent
extensions call them through an argv envelope (`--session-id`, `--depth`,
`--origin`, `--source`, `--prompt`) and compose no text of their own, and the
core injects nothing into a child session (`--depth` above 0) or into a turn a
person did not type.

## Consequences

- Prime Agent moves from full text on every prompt to the Claude Code ledger
  semantics: one ledger format (version 1, unchanged), one `decide`, one
  reminder grammar, one reset path. `status-extension.ts` runs `status-hook.py`
  on `session_start`, `session_compact`, `session_tree` and
  `refine_complete`, and injects what it returns on the next prompt of that
  session, once.
- Measured effect, before the compact grammar of ADR-0025: follow-up route
  characters fall 73% on the real session and 59% on the short-session
  replay; injected route and status fall from 4.5% to 0.67% of the measured
  session's processed tokens. This decision carries about 85% of the round's
  measured token saving. It needs no other change of the round to pay. The
  built core, replayed over the same short sessions after the increment
  landed, gave -59.1% on follow-up route characters (164,134 to 67,081, 47
  follow-ups), confirming the figure before the compact grammar began.
- The extensions shrink to envelopes. The seed's gate has no TypeScript
  runtime, so the behaviour now lives where the gate can run it: the argv
  envelope reruns the stdin cases (`HOOK_ARGV_ENVELOPE_EQUALS_STDIN_ENVELOPE`).
  The extensions keep structural checks only.
- The TypeScript `findLint` and `findTool` walks go away with the text they
  served. The Python walks stop at the plant root (`_is_plant_root`), which
  fixes the walk that could leave a nested checkout.
- The `## Surfaced nodes` overlay section is deleted. The reminder line names
  known ids and says to open what is not in view, on both hosts. The
  prime-agent eager surface falls by the section's bytes.
- The status register and the code anchor reach a session once per session
  start, and never a child. This fixes the once-per-process flag.
- A turn whose origin is not a person is not routed and does not count toward
  `REFRESH_EVERY`. The core recognizes it by a leading marker
  (`NON_HUMAN_MARKERS` in `route-hook.py`, SPEC-0003 §6): on Prime Agent the
  agent-message delivery header (`[agent-message from `), the background-job
  completion turn (`[bash-done `), which a second live probe showed does fire
  `before_agent_start`, and the harness digest (`[harness-digest]`); a child
  is not routed at all. Prime Agent's `before_agent_start` payload carries no
  origin, so its extension passes `--origin` only if a later host version
  adds one. On Claude Code the hook reads leading markers until a probe shows
  the envelope carries an origin (SPEC-0003 §11).
- Unknown is resolved toward inclusion (I-1). If the session id cannot be
  read, the core gets none and injects the full text, as today. If the depth
  cannot be read, the prompt is routed. A missed reset is bounded by
  `REFRESH_EVERY` - 1 reminders, and every LOAD id is still named.
- Three host facts were probed on a live Prime Agent session (0.9.8) before
  the GREEN of the adapter, and all three held: `getSessionId()` answers in
  `before_agent_start` and `session_start` and equals the header `id`; the
  header carries `rlmDepth` (0 in a parent, 1 in a child) and `parentSession`;
  under jiti `__dirname` names the extension's own directory (`import.meta.url`
  is a `data:` URL). The probe also showed why every child got the status
  text: parent and children share one process, and the extension module is
  evaluated once per session. Had the first probe failed, Prime Agent would
  have stayed in full mode and the session-file ledger alternative below would
  have reopened. SPEC-0003 §6 records the host facts.
- A live session of the built step confirmed the GREEN on the host: the first
  prompt got the full route and the status line once, through
  `.prime/agent/hooks/`; a `[bash-done ...]` turn, a delivered agent message
  and the spawned child got nothing; the second prompt got the reminder.
- Threat model, beside ADR-0010's: the argv values are checked by the same
  patterns as the stdin ones (a session id that fails the pattern is no id);
  the prompt stays one argv element with no shell; the ledger I/O and its
  descriptor discipline are unchanged; the extensions write no file.
- Contracts: SPEC-0003 `HOOK_ARGV_ENVELOPE_EQUALS_STDIN_ENVELOPE`,
  `PRIME_SESSION_ID_PASSED`, `PRIME_RESET_ON_EVENTS`,
  `CHILD_SESSION_GETS_NO_INJECTION`, `NON_HUMAN_TURN_NOT_ROUTED`,
  `STATUS_ONCE_PER_SESSION`, `SESSION_INJECTION_WITHIN_BUDGET`; SPEC-0001
  `PRIME_HOOK_SCRIPTS_ARE_PLACED`. Seven Prime Agent contracts and two
  failures of SPEC-0003 retire with the model-kept set and the text the
  extensions no longer compose.
- The core reads `graph-lint.py --plan-json` from the first increment on
  (ADR-0025), so it never parses router text. It rendered the 7.32.0 text
  grammar from the document until the compact grammar landed in the next
  increment, which changed the rendering and nothing else. A plant whose
  engine lacks `--plan-json` gets the pointer line and one notice naming the
  graft (SPEC-0003 `ENGINE_OLDER_THAN_HOOK_IS_NAMED`), never a text
  fallback.

## Alternatives considered

- **A host-neutral core at `docs/graph/route-inject.py`.** Rejected: it puts a
  runtime file into opencode and codex plants that never call it, and adds a
  graph engine for graft to reconcile (ADR-0014). The per-host copy has the
  same single source with no new engine, as the Copilot hooks already do.
- **A ledger in TypeScript.** Rejected: it duplicates about 170 lines of
  descriptor-safe I/O in a language the gate cannot run, and two copies of
  `decide` drift.
- **The session file as the ledger (`details` and `getBranch()`).** Deferred:
  exact by construction, but its branch walk would be ungated TypeScript and
  it reopens ADR-0010's rejection of `appendEntry`. It can sit behind the same
  Python `decide` later. It reopens if a missed reset is observed on Prime
  Agent.
- **Route a child on its task line, found by a marker in the brief.**
  Rejected: a parser over free text (`<TASK>`, `TASK LINE:`) is brittle, and
  it repeats what the brief already tells the child to do.
- **Keep the injection in children and drop brief step 1.** Rejected: it
  changes the byte-identical canonical block (`BRIEF_TEMPLATES_BYTE_IDENTICAL`)
  and keeps the noisier input.
- **Port the ledger first and keep parsing the router's text.** Rejected: it
  would bank the same saving, but keep the echo-prefix rule and the text
  parser's indent defect, and the parser would be rewritten one increment
  later. `--plan-json` holding only what the hooks consume is small, and lands
  in the same increment.
- **Keep the model-kept set.** Rejected by D1: it is soft, unmeasured, and
  costs every Prime Agent session its overlay bytes.

## Reversibility

`reversible`. Ledger version 1 is unchanged, so no plant data migrates. The
copies at `.prime/agent/hooks/` are placed files with backups, and the
extensions are two placed files.

## References

- Spec: SPEC-0003 (the core, the envelopes, the Prime Agent contracts),
  SPEC-0001 (`PRIME_HOOK_SCRIPTS_ARE_PLACED`)
- Plan: `docs/plans/grill-7.37.0-routing-context.md`, increment 1
- [ADR-0010](adr-0010-context-residency.md) (superseded in part),
  [ADR-0009](adr-0009-host-support-tiers.md) (host tiers),
  [ADR-0014](adr-0014-graft-reconciles-every-graph-engine.md) (engines)
- Owner ruling D1 of 7.37.0, the owner's note that "the problem is not much
  about first prompt but subsequent prompts", and the round's investigation
  and refutation reports, kept with the round's working records outside the
  seed
