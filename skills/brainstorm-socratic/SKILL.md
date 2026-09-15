---
name: brainstorm-socratic
description: The Socratic questioning technique that converges a vague goal — question selection, one-to-three-per-turn pacing, the reflect-every-two-answers cadence, the nine-question hard cap, and the eight-point convergence checklist that defines "converged". This is the USER-FACING of the brainstorm protocol's two modes — use it when the decision is the owner's to make; when it is the session's own, the mode is skill.brainstorm-internal and there is nobody to question. The protocol owns entry/exit conditions, mode selection and where output lands; this skill owns how to converge with a person.
id: skill.brainstorm-socratic
tier: 2
kind: skill
origin: seed
title: brainstorm-socratic — the user-facing brainstorm mode: questioning that converges a goal, capped at nine questions
owns:
  - brainstorm-socratic.method
requires:
peers:
  - protocol.brainstorm
  - skill.brainstorm-internal
  - skill.humanizer
  - skill.spec-author
load_when:
  - "converge a vague or contested goal"
  - "socratic questioning for requirements"
  - "brainstorm a new feature idea"
  - "the goal is too fuzzy to specify"
  - "ask the owner what they actually want"
artifacts:
  - templates/grill.template.md
prevents: A convergence pass that never converges — open-ended questioning with no cap and no checklist, which from the outside is indistinguishable from stalling.
est_tokens: 955
---

# brainstorm-socratic

**This is the mode with a person in it.** It applies when the answer is the
owner's to give — what to build, for whom, what counts as done, which tradeoff
they have to live with. When the decision is the session's own, there is nobody
to question and the technique below does not apply: use
`docs/graph/skills/brainstorm-internal.md`. `brainstorm.mode-selection` in
`docs/graph/protocols/brainstorm.md` owns the test.

A goal that arrives as "build me a thing" is not yet ready to specify
or plan. This skill is the questioning technique that takes it from
vague to precise — without designing the UI, picking a framework, or
pre-committing to architecture. It is applied inside
`docs/graph/protocols/brainstorm.md`, which owns entry conditions, the grill.md
output map, and the explicit-confirmation exit; this file owns the
method.

## How to brainstorm

### Ask the smallest set of questions that change the design the most

Bad: "What colour?", "What should the homepage look like?", "What
framework?"

Good: "Who is this for and what do they do today instead?", "What
counts as success one month in?", "What is explicitly out of scope?"

Limit: **one to three questions per turn, no more**. Pace matters
— each set of answers reshapes the next question. Twenty questions
at once gets answered with platitudes.

### Reflect every two answers

After every two answers, write a one-paragraph reflection:
"I now believe X. Tell me where I'm wrong."

This forces the brainstorm to converge and lets the user
disagree precisely.

### Hard cap at nine questions total

If you haven't converged in nine questions, accept the gaps. Mark
each one as an assumption in grill.md §12, write what you have,
and proceed to `specify`.

A brainstorm that drags past nine questions is usually trying to
specify and plan at the same time. Stop; move to `specify`.

## The convergence checklist

By the end of brainstorm, you can write the following without
hand-waving:

1. **Problem statement.** One sentence. "X user does Y today; we
   want them to be able to Z instead."
2. **Primary user.** A specific role and context, not "developers"
   or "users".
3. **First useful slice.** The smallest end-to-end thing that
   delivers the outcome for one well-defined case.
4. **Success criteria.** Measurable, with a time horizon.
   Quantitative where possible; qualitative with explicit rubrics
   where not.
5. **Non-goals.** Three to five things this is explicitly not.
6. **Operating constraints.** Runtime, security, privacy, data,
   cost, latency, compliance, maintenance — at least the ones
   that bind.
7. **Shaped options.** Two to four named technical approaches with
   one-line summaries, not full designs. Each option names the
   tradeoff it makes.
8. **Risks and assumptions.** The top three risks; every
   assumption that, if false, changes the plan.

## Anti-patterns

- **Boiling the ocean.** Asking twenty questions about edge cases
  before the main flow is clear.
- **Premature framework choice.** "Should we use X or Y?" Wait for
  `architect` after research.
- **Designing the UI.** UI emerges from the user flow, which
  emerges from the outcome.
- **Skipping non-goals.** Without non-goals, scope grows
  uncontrollably.
- **Pretending the user is "everyone".** Pick one.
- **Treating brainstorm as a milestone instead of a step.**
  Brainstorm converges enough to start specifying; the spec then
  refines further.

## Reference files

- `docs/graph/protocols/brainstorm.md` — the workflow: entry, output map, exit.
- `docs/graph/protocols/specify.md` — the protocol that consumes brainstorm
  output.
- `docs/graph/templates/grill.template.md` — where brainstorm output is
  recorded.

## What the owner actually reads

Converging is half the job. The other half is that the person can tell what they
are agreeing to.

Everything this mode puts in front of the owner — the reflections, the options,
the problem statement they are asked to confirm — goes through
`docs/graph/skills/humanizer.md` before it is sent. Not restyled afterwards:
drafted as prose a person reads, carrying every fact intact.

An options table is a working artifact. A person confirming "yes, that one" off
a table has agreed to a row, not to a decision — and the difference surfaces
later as "that isn't what I thought I picked". State what is being decided, why
it is on the table now, what each option commits them to, and what it would cost
to change later. The confirmation this mode waits for is only worth waiting for
if it was informed.
