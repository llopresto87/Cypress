---
name: deliver
description: End the session with a cold-pickup summary covering files changed, specs touched, docs updated, decisions recorded, gates run/passed/skipped, known limitations, and one recommended next step. Use at the end of every work session, before handing off to another specialist, and before the user closes the chat. Tier 0/1 tasks (kernel §0) use the compact form; Tier 2/3 use the full form after the canonize close-out has run. A session without a delivery summary is paused, not finished — never skip this protocol.
id: protocol.deliver
tier: 2
kind: protocol
origin: seed
title: deliver — ending every session in a cold-pickup state with attributed, gated work
owns:
  - rule.deliver
  - deliver.forms
  - deliver.attribution-assertion
  - deliver.numbered-decisions
requires:
peers:
  - protocol.canonize
  - protocol.recover
artifacts:
  - templates/prompts/handback-payload.md
load_when:
  - "session is ending, wrap up, hand off"
  - "delivery summary, cold pickup"
  - "what did we change, session report"
  - "attribution, produced_by, routing evidence"
  - "decisions for the owner, options to approve, answer by number"
  - "every remaining step is the owner's, goal loop or stop hook keeps firing"
  - "session metrics after each increment, cost and quality so far"
prevents: A session that ends without a cold-pickup state, leaving the next one to re-derive what changed, what was gated and what is still open from a diff.
est_tokens: 2471
command: true
---

# Protocol: deliver

Every session ends with delivery. The deliverable is a concise summary
that lets another agent (or the same agent next time) pick the project
up cold.

This node owns **the deliver rule**: every session ends with a
delivery, compact for T0/T1, full for T2/T3: files changed, routing
attribution, docs updated, decisions, gates with outcomes,
limitations, and **one** recommended next step. The deliver-time
attribution assertion is **detective** (ADR-0003): a unit of work with
no `produced_by` is a BLOCK (§Routing-attribution assertion). The
standard for done is §The cold-pickup test.

## When to invoke

- At the end of every work session.
- Before the user closes the chat or moves to another task.
- Before handing off to a different specialist for a different phase.

## Compact form (Tier 0/1 only — kernel §0)

A T0 answer or a T1 trivial non-behavioral edit takes the compact form:
in the chat, in five lines or fewer:

```markdown
# Delivery (compact) — <what> — YYYY-MM-DD
- Changed: <paths, or "nothing — question answered with citations">
- Gates: <the one focused check run, or "n/a (read-only)">
- Canonize: nothing of interest / no tool, because <one line>   # or: escalated to close-out
- Next: <one step, or "none">
```

A T1 edit that turns out to touch behavior, a contract, or anything a
spec covers is reclassified (`method.tiers` owns the edges; a small
behavior change is T2's contained lane) and takes the full form after the
close-out. The compact form appends to grill.md §15 only when it changed a
file.

## Full form (Tier 2/3)

Runs after the `canonize` close-out spawn has confirmed (or
record-emptied) knowledge and tools. State the summary in the chat AND
append the same content to `docs/graph/changelog.md` and to grill.md
section 15.

```markdown
# Delivery — <feature or session title> — YYYY-MM-DD

## Files changed
- path:purpose
- ...

## Routing attribution
- <unit of work> — produced_by: <specialist> — route: <agent-lint --route band + line, or override rationale>
- ...

## Documentation created or updated
- docs/graph/plans/grill.md — sections updated: N, N, N
- docs/graph/libraries/<name>.md — created / refreshed
- docs/graph/decisions/adr-NNNN-*.md — added
- docs/graph/runbooks/verification.md — increment recorded
- ...

## Key decisions
- <one-line decision> — link to ADR or grill.md section 6 row
- Awaiting the owner: 1. <item> 2. <item> … — answer by number

## Gates run
- Formatter, linter, type-check, unit, integration, ... — each as executed /
  discovered / absent (reason), the three states owned by
  docs/graph/protocols/verify.md. A failing gate is fixed, or its increment
  goes out marked WIP under Known limitations with the failure record
  docs/graph/protocols/recover.md requires.

## Known limitations
- <thing that doesn't work yet> — link to grill.md section 12 row
- <assumption not yet validated> — link to grill.md section 12 row

## Session metrics
- Tier: <T0-T3; for T2 name the lane: covered | contained> (reclassified: <none, or T1→T2 + why>)
- Spawns: <N> (<agent×count with model class/reasoning effort, ...>)
- Route bands: <HIGH×n MEDIUM×n LOW×n> — overrides: <none, or count + why>
- Retries: <none, or class×count per docs/graph/protocols/recover.md>
- Gates: <run/failed-then-fixed counts>
- Full-suite runs: <N> (<how many were red>)
- Serial waits: <spawns issued only after another's handback returned, read from spawn_id issue order>
- Overflow notes: <none, or count + paths of handback overflow notes>
- Quality: <review Critical/Major per increment; red full-suite runs and bisects; mutants killed/total, or "no mutation pass">

## Recommended next step
<single highest-leverage action, named specifically>
```

**A question put to the owner is as understandable as possible, and
its decisions are numbered** (`deliver.numbered-decisions`). The
standard is the owner's words: "when asking question the seed/plant
should strive to be as understandable as possible". Before a choice is
asked, it is explained in prose: what the earlier decision says, quoted;
what changes, with one concrete example; what it costs; and what stays
the same. If the owner says the explanation fell short, explain again
and confirm the answer before building on it. Wherever this summary, or
any message in the session, puts a choice in the owner's hands (an
option set, an open question, a conflict between specialists, a
ratification), it arrives as a numbered list of individually approvable
items, so the owner answers "1 and 3, not 2" instead of re-describing
each. That holds for the Key decisions still open, for a limitation
that needs a call, and for the next step when it needs a go/no-go.
Every item names each branch, environment, or resource by its exact
identifier (a branch by its branch name, never by the environment it
deploys to), because an approval given against an ambiguous name can land
on the wrong target. Default on; the owner may waive it.

The metrics block is telemetry, and the orchestrator fills every line
from its own trace (spawn ids, handbacks, gate runs), with no transcript
access. It is what lets the system improve on evidence instead of
anecdote: `harvest` aggregates these across deliveries to find
*systemic* seed problems. Recurring misroutes mean a specialist's
`routing_triggers` need sharpening, frequent tier reclassifications mean
the tier edges need tuning, and repeated transient retries in one area
are a reliability signal. The Quality line sits beside the cost lines on
purpose. A cost figure read alone would endorse any change that made a
session cheaper by making it worse, so a cheaper session counts as
progress only when its quality line held.

In a long session, take the block after each landed increment as well
as at the end, and append it to the grill.md §15 entry that increment's
revision pass writes. The cost curve is then visible while it can still
change, and a retrospective after the money is spent is too late to act
on it. Where the host exposes tokens and wall time per spawn, add them to
the Spawns line; the block does not depend on them.

## Quality bar

A delivery summary that passes:
- Names every changed file.
- Names every documentation update with its location, grill.md among them.
- Cites verification outcomes by gate (no hand-waving).
- Lists every limitation explicitly (no "should mostly work"), and marks
  a half-finished increment WIP, with resuming it as the next step.
- Recommends exactly one next step (not a list).
- Numbers every decision left to the owner, so the answer can be by
  number.
- Covers every library the work used with its wiki page
  (`protocol.ingest-library`).
- Reads as the writer, not as a model: the full-form summary and any
  pull-request description or commit message pass the `humanizer` skill
  in embedded mode (`docs/graph/skills/humanizer.md`), and
  `docs/graph/prose-lint.py` reports no strong tell on the text.
- Is the smallest summary that permits correct use and appropriate
  trust: material caveats and risks stay in; process narration,
  restated requests, and recaps of settled context stay out, because
  future context is a cost this summary imposes on every later turn
  (proportionate communication, `docs/graph/method/decision-economy.md`).

## Routing-attribution assertion (detective)

Before you sign off, attribute every unit of work to the specialist that
produced it, reading the `produced_by` and `route_evidence` fields from the
handback payloads (`docs/graph/templates/prompts/handback-payload.md`) the workers
returned. Then run these checks:

- **Missing `produced_by` on any unit of work → BLOCK**, the same
  missing-proof-is-a-BLOCK rule the release gates use. You call that block
  yourself.
- **Out-of-domain authoring → FLAG.** A `produced_by` specialist whose
  `routing_triggers` do not cover the work it authored is flagged for the
  operator to confirm or re-route.
- **Unexplained generic-role override → FLAG.** When `agent-lint --route`
  returned a HIGH band for specialist X but the work was produced by a
  generic role (`general-purpose` / `claude`) or a different specialist with
  no recorded rationale in `route_evidence`, flag it.
- **Role emulation → FLAG unless declared.** A worker that ran as a generic
  type wearing a specialist's role must carry `harness_override:
  role-emulated (<reason>)` in its handback. Without it, a recorded emulation
  and a silent substitution stamp the identical `produced_by`, so the
  declaration is the only thing separating them, and every emulated unit
  carries weaker bounds than its frontmatter claims
  (`delegation.harness-registration`). Report the count in the delivery.

This assertion runs in the top session at `deliver`, where the whole
delivery is in view; no hook the seed installs reads a worker's result
(`delegation.briefs`), and no harness refuses a delivery that skips the
check. A top-session `Stop` hook that greps the delivery / grill.md §15
for attributions stays deliberately unwired until this plant's real
deliveries carry `produced_by`, because a gate landed before the thing it
checks either checks nothing or blocks everything (kernel §3.5, the
green-lie rule). Once deliveries carry the field, wire it warn-first, then
block.

## When every open step is the owner's

When every open step is the owner's (a merge, an approval, a check or
credential only they can create), the session has reached its end, not
a wait. State those steps once, as a numbered list with the exact
command to run or control to click for each, each target named by its
exact identifier, then deliver and stop. An autonomous continuation (a
goal condition, a stop hook, a heartbeat, a scheduled loop) treats that
state as its exit: it ends, or is reshaped so that its exit message names
the owner-only steps. A loop that keeps firing there makes no progress and
spends a main-loop turn on every firing.

## The cold-pickup test

The standard for "is this delivery complete?" is the cold-pickup test:
another senior engineer, with no context except the repository and
the delivery summary, should be able to:
1. Run the project locally.
2. Run the verification gates.
3. Find the current plan-of-record.
4. Know the next step.

If they can't, the delivery isn't done.
