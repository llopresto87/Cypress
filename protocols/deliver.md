---
name: deliver
description: End the session with a cold-pickup summary covering files changed, specs touched, docs updated, decisions recorded, gates run/passed/skipped, known limitations, and ONE recommended next step. Use at the end of EVERY work session, before handing off to another specialist, and before the user closes the chat. Tier 0/1 tasks (kernel §0) use the compact form; Tier 2/3 use the full form after the canonize close-out has run. A session without a delivery summary is paused, not finished — never skip this protocol.
id: protocol.deliver
tier: 2
kind: protocol
origin: seed
title: deliver — ending every session in a cold-pickup state with attributed, gated work
owns:
  - rule.deliver
  - deliver.forms
  - deliver.attribution-assertion
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
est_tokens: 1450
command: true
---

# Protocol: deliver

Every session ends with delivery. The deliverable is a concise summary
that lets another agent (or the same agent next time) pick the project
up cold.

This node owns **the deliver rule** — every session ends with a
delivery, compact for T0/T1, full for T2/T3: files changed, routing
attribution, docs updated, decisions, gates with outcomes,
limitations, and **one** recommended next step. The deliver-time
attribution assertion is fail-closed: a unit of work with no
`produced_by` is a BLOCK. If another senior engineer could pick up
cold, you are done; if not, you are not.

## When to invoke

- At the end of every work session.
- Before the user closes the chat or moves to another task.
- Before handing off to a different specialist for a different phase.

## Compact form (Tier 0/1 only — kernel §0)

A question answered (T0) or a trivial non-behavioral edit (T1) does not
earn the full ceremony. Deliver in the chat, in five lines or fewer:

```markdown
# Delivery (compact) — <what> — YYYY-MM-DD
- Changed: <paths, or "nothing — question answered with citations">
- Gates: <the one focused check run, or "n/a (read-only)">
- Canonize: nothing of interest / no tool, because <one line>   # or: escalated to close-out
- Next: <one step, or "none">
```

A T1 edit that turns out to touch behavior, a contract, or anything a
spec covers is not T1 — reclassify and take the full path. The compact
form appends to grill.md §15 only when it changed a file.

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

## Gates run
- Formatter, linter, type-check, unit, integration, ... — each as executed /
  discovered / absent (reason), the three states owned by
  docs/graph/protocols/verify.md. There is no FAIL state: a failing gate is
  fixed or handed back, never recorded and delivered.

## Known limitations
- <thing that doesn't work yet> — link to grill.md section 12 row
- <assumption not yet validated> — link to grill.md section 12 row

## Session metrics
- Tier: <T0-T3> (reclassified: <none, or T1→T2 + why>)
- Spawns: <N> (<agent×count, ...>)
- Route bands: <HIGH×n MEDIUM×n LOW×n> — overrides: <none, or count + why>
- Retries: <none, or class×count per docs/graph/protocols/recover.md>
- Gates: <run/failed-then-fixed counts>

## Recommended next step
<single highest-leverage action, named specifically>
```

The metrics block is five lines of telemetry, not prose. It is what
lets the system improve on evidence instead of anecdote: `harvest`
aggregates these across deliveries to find *systemic* seed problems —
recurring misroutes mean a specialist's `routing_triggers` need
sharpening, frequent tier reclassifications mean the tier edges need
tuning, repeated transient retries in one area is a reliability signal.

## Quality bar

A delivery summary that passes:
- Names every changed file.
- Names every documentation update with its location.
- Cites verification outcomes (no hand-waving).
- Lists every limitation explicitly (no "should mostly work").
- Recommends exactly one next step (not a list).
- Is the smallest summary that permits correct use and appropriate
  trust: material caveats and risks stay in; process narration,
  restated requests, and recaps of settled context stay out
  (proportionate communication —
  `docs/graph/method/engineering-posture.md`).

A delivery summary that fails:
- Says "implemented X" without naming the files.
- Says "tests pass" without naming the gates.
- Says "next, do whatever feels right" or lists five options.
- Hides limitations behind optimism.
- Pads the record with narration the next session must filter out —
  future context is a cost this summary imposes on every later turn.

## Routing-attribution assertion (fail-closed)

Before you sign off, attribute every unit of work to the specialist that
produced it, reading the `produced_by` and `route_evidence` fields from the
handback payloads (`docs/graph/templates/prompts/handback-payload.md`) the workers
returned. Then run these checks:

- **Missing `produced_by` on any unit of work → BLOCK.** A missing proof of
  who did the work is a block, never a pass — the same fail-closed rule the
  release gates use (a missing proof is a BLOCK, not a PASS).
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
  declaration is the only thing separating them — and every emulated unit
  carries weaker bounds than its frontmatter claims
  (`delegation.harness-registration`). Report the count in the delivery.

This assertion runs in the top session at `deliver` — the one place a hook
can reach, since subagent hooks do not fire. A top-session `Stop` hook that
greps the delivery / grill.md §15 for attributions stays **deliberately
unwired until this plant's real deliveries carry `produced_by`** — a gate
landed before the thing it checks either checks nothing or blocks
everything (kernel §3.5, the green-lie rule). Once deliveries carry the
field, wire it warn-first, then block.

## The cold-pickup test

The standard for "is this delivery complete?" is the cold-pickup test:
another senior engineer, with no context except the repository and
the delivery summary, should be able to:
1. Run the project locally.
2. Run the verification gates.
3. Find the current plan-of-record.
4. Know the next step.

If they can't, the delivery isn't done.

## What you do not do

- You do not deliver with red tests, undeclared.
- You do not use the compact form for work that changed behavior,
  contracts, or spec-covered code; that is Tier 2/3 and takes the full
  form after the close-out.
- You do not deliver with libraries used but not wikified.
- You do not deliver a unit of work with no `produced_by`; a missing
  attribution is a BLOCK, not a pass.
- You do not deliver without updating grill.md.
- You do not deliver a half-finished increment as if it's done; mark
  it WIP and recommend resuming it as the next step.
