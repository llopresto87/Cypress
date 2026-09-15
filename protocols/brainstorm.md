---
name: brainstorm
description: 'The workflow that converges a goal or a choice into a precise problem statement, primary user, first useful slice, constraints, shaped options, and risks — entry conditions, which of the two modes applies, where the output lands in grill.md, and, in the user-facing mode, explicit user confirmation before exit. Use whenever the goal is vague, contested, or under-specified, whenever the user says "build me a thing", and whenever stakeholders disagree about scope. Two modes: user-facing (skill.brainstorm-socratic — questioning, pacing, nine-question cap, convergence checklist, humanized for the owner) and internal (skill.brainstorm-internal — divergence against evidence in hand, no user, no cap). Output feeds the `specify` protocol.'
id: protocol.brainstorm
tier: 2
kind: protocol
origin: seed
title: brainstorm — converging a vague or contested goal into a precise problem statement
owns:
  - brainstorm.mode-selection
  - brainstorm.entry-and-exit
  - brainstorm.output-landing
requires:
peers:
  - skill.brainstorm-socratic
  - skill.brainstorm-internal
  - skill.humanizer
  - protocol.specify
  - protocol.grill
  - protocol.from-scratch
load_when:
  - "goal is vague, build me a thing"
  - "stakeholders disagree about scope"
  - "what should we actually build, converge the idea"
  - "problem statement, first useful slice"
  - "generate options for a decision nobody needs to confirm"
  - "shaped alternatives, is this mine to decide or theirs"
prevents: Work that starts from a goal nobody has stated in one sentence, so scope is settled later by whoever writes the next file and the disagreement surfaces after the build — and, in the other direction, a session asking the owner to settle what was always its own to decide.
est_tokens: 901
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

## Which mode (`brainstorm.mode-selection`)

Brainstorm has two audiences and they do not share a technique. Pick before
you start, and say which you picked.

**The test: is the decision the owner's to make?** Not "would the owner be
interested" — everything is interesting. The question is whether their answer
changes what gets built.

| The decision | Mode | Skill |
|---|---|---|
| what to build, for whom, what counts as done, what is out of scope, which tradeoff the owner has to live with | **socratic** — user-facing | `docs/graph/skills/brainstorm-socratic.md` |
| which of two designs satisfies a contract better, how to sequence increments, what an ADR records as rejected, which of several correct implementations to take | **internal** — no user | `docs/graph/skills/brainstorm-internal.md` |

Both failures are real and they are opposite. Using the internal mode on the
owner's decision presents a settled choice as a finished one, and the owner
finds out when it ships. Using the socratic mode on your own decision spends
their turn to be told "you decide" — and a session that does this routinely
teaches the owner to stop reading.

**When genuinely unsure, ask** — one question, framed as the mode question
("this is mine to call unless you want it; say if you do"), not as the
decision. That costs one turn and settles it; guessing wrong costs the build.

The two techniques are not variants of each other. Questioning, pacing, the
reflect-every-two-answers cadence, the nine-question hard cap and the
convergence checklist belong to the socratic mode alone, and are meaningless
where there is nobody to ask. Preconditions, kill conditions and the strawman
discipline belong to the internal mode alone, and are what replaces the user as
the thing that pushes back.

This protocol owns when you enter, which mode applies, where the output lands,
and when you are done.

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

If the project does not yet have a grill.md, create one from
`docs/graph/templates/grill.template.md` — brainstorm fills phase 1 of
the grill pass (`grill.flow`), which is why §2–§4 land before §1.

## Exit conditions

**Socratic mode** is done when:
- The skill's convergence checklist is satisfied (or each gap is a
  flagged assumption in grill.md §12).
- The user has confirmed the problem statement, the primary user,
  and the first useful slice. Confirmation is explicit ("yes",
  "looks right"), not assumed from silence.
- What they confirmed was put to them through `skill.humanizer` — a person
  cannot agree to a decision they had to reverse-engineer from an options
  table.
- The next protocol (`grill` or `from-scratch` Phase 2) has an
  unambiguous entry point.

**Internal mode** is done when the options set is written where the next step
reads it, each option carrying its preconditions and the one fact that would
kill it, and the pick naming which kill condition retired each loser. **No user
confirmation is required or waited for.** If one turns out to be needed, the
mode was wrong — go back to the table above.
