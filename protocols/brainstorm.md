---
name: brainstorm
description: 'The workflow that converges a vague goal into a precise problem statement, primary user, first useful slice, constraints, shaped options, and risks — entry conditions, where the output lands in grill.md, and explicit user confirmation before exit. Use whenever the goal is vague, contested, or under-specified, whenever the user says "build me a thing", and whenever stakeholders disagree about scope. The questioning technique itself (pacing, reflection cadence, nine-question cap, convergence checklist) is the brainstorm-socratic skill. Output feeds the `specify` protocol.'
id: protocol.brainstorm
tier: 2
kind: protocol
origin: seed
title: brainstorm — converging a vague or contested goal into a precise problem statement
owns:
  - brainstorm.entry-and-exit
  - brainstorm.output-landing
requires:
  - skill.brainstorm-socratic
peers:
  - protocol.specify
  - protocol.grill
  - protocol.from-scratch
load_when:
  - "goal is vague, build me a thing"
  - "stakeholders disagree about scope"
  - "what should we actually build, converge the idea"
  - "problem statement, first useful slice"
est_tokens: 400
command: true
---

# Protocol: brainstorm

Use this when the goal is vague, contested, or under-specified. The
deliverable is a precise problem statement, a primary user, a first
useful slice, the constraints, and a shaped set of options.

You do not write code in brainstorm. You do not pick a stack. You
converge.

## Entry conditions

One or more of:
- The user said "build me a thing", "we should look into X", "what if
  we did Y", or otherwise expressed a goal without a defined outcome.
- The goal mentions a verb but not the user.
- The goal mentions the user but not the outcome.
- The team has competing visions for the goal.

## The technique

How to converge — question selection, the one-to-three-per-turn
pacing, the reflect-every-two-answers cadence, the nine-question hard
cap, the eight-point convergence checklist, and the questioning
anti-patterns — lives in `docs/graph/skills/brainstorm-socratic.md`, the
one home for the Socratic method. This protocol owns when you enter,
where the output lands, and when you are done.

## Output format

Write the brainstorm output directly into the relevant sections of
`docs/graph/plans/grill.md`:

- Section 2 → problem statement.
- Section 3 → primary user, primary outcome, acceptance criteria
  (drafted from success criteria), non-goals.
- Section 4 → operating constraints.
- Section 7 → shaped options.
- Section 11 → risks.
- Section 12 → assumptions and open questions.

If the project does not yet have a grill.md, create one from the
template (`docs/graph/templates/grill.template.md` or `docs/graph/protocols/grill.md`).

## Exit conditions

The brainstorm protocol is done when:
- The skill's convergence checklist is satisfied (or each gap is a
  flagged assumption in grill.md §12).
- The user has confirmed the problem statement, the primary user,
  and the first useful slice. Confirmation is explicit ("yes",
  "looks right"), not assumed from silence.
- The next protocol (`grill` or `from-scratch` Phase 4) has an
  unambiguous entry point.
