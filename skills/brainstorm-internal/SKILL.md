---
name: brainstorm-internal
description: The divergence technique CYPRESS applies to itself, with no user in the loop — generating genuinely distinct options against evidence already in hand, stating what would have to be true for each, and naming the one fact that would kill each. Use when a choice is the session's to make and the user has nothing to add to it - filling grill.md §7, assembling an ADR's rejected alternatives, choosing between two implementations that satisfy the same contract, or deciding how to sequence work. The user-facing mode is brainstorm-socratic; the protocol owns which mode you are in.
id: skill.brainstorm-internal
tier: 2
kind: skill
origin: seed
title: brainstorm-internal — divergence against your own evidence, with nobody to ask
owns:
  - brainstorm-internal.method
requires:
peers:
  - protocol.brainstorm
  - skill.brainstorm-socratic
  - skill.adr-writer
  - skill.grill-planner
load_when:
  - "generate options for a decision that is mine to make"
  - "what are the alternatives, nobody to ask"
  - "fill the rejected alternatives of an adr"
  - "two designs satisfy the same contract, which one"
  - "shaped options for the plan, no user input needed"
prevents: A decision recorded with one real option and two invented to flank it, so the rejected alternatives read as due diligence and the choice was never actually contested.
est_tokens: 900
---

# brainstorm-internal

Some choices are not the user's. Which of two implementations satisfies a
contract better, how to sequence four increments, what an ADR should record as
rejected — the user has nothing to add, and asking costs a turn and gets "you
decide". This is the divergence technique for those.

**There is no user here.** No questions, no pacing, no cap, no confirmation to
wait for. The nine-question machinery in
`docs/graph/skills/brainstorm-socratic.md` is not a stricter version of this
skill — it is the other mode, and it does not apply when there is nobody to ask.
The exit is a written options set, not an agreement.

## The failure this exists to prevent

**A session brainstorming against itself generates one real option and two
strawmen.** It has already, quietly, decided; what it produces is the decision
plus two alternatives shaped to lose. The output looks exactly like genuine
divergence — three options, a comparison, a pick — and an ADR built on it
records rejected alternatives nobody ever considered.

Every rule below exists because of that one failure.

## The method

1. **Write the decision as a question with at least two answers you could
   defend.** If you cannot defend the second answer, you have not found an
   option yet; you have found an objection to one. Go back.

2. **Generate against evidence already in hand** — the ledgers, the wiki pages,
   the specs, the source. This mode does not go to the internet
   (`agent.research-scout` does) and does not ask the user
   (`skill.brainstorm-socratic` does). If a genuine option needs evidence you do
   not have, that is the finding: name it and say which of the two it would
   settle.

3. **For each option, state what would have to be true for it to be right.**
   Not its advantages — its *preconditions*. This is the step that kills
   strawmen, because an option whose preconditions you cannot write down is one
   you invented to lose.

4. **For each option, name the single fact that would kill it.** If an option
   has no kill condition it is not a real option; if two options share a kill
   condition they are one option described twice.

5. **Say which preconditions are already known true, known false, or
   unchecked.** Unchecked is the useful category and the one that gets
   collapsed: an option rejected on an unchecked precondition is rejected on a
   guess, and must be recorded as such.

6. **Pick, and record why the others lost** — against their kill conditions, not
   against their vibes. The losers go into `grill.md` §7 or the ADR's rejected
   alternatives verbatim; that is what makes this mode's output worth producing
   rather than reasoning silently.

## Honesty checks before you exit

- Could a competent reader of the losing options tell they were seriously
  considered? If the answer depends on your say-so, they were not.
- Did any option change shape while you worked? Real divergence moves; a set
  that arrives finished was a decision wearing three hats.
- Is any option rejected on a precondition you never checked? Say so in the
  record, or check it.
- Did you produce exactly three options because three is the habit? Two
  defensible options beat three where one is filler.

## Exit conditions

- Each option carries its preconditions and its one kill condition.
- Every precondition is marked known-true, known-false, or unchecked.
- The pick names which kill condition retired each loser.
- The options set is written where the next step reads it — `grill.md` §7, an
  ADR's rejected alternatives, or the plan record — not left in the session.

**No user confirmation is required to exit.** If it turns out one is — the
decision was the user's after all — you were in the wrong mode:
`brainstorm.mode-selection` in `docs/graph/protocols/brainstorm.md` is the test,
and switching is cheap while the options set is fresh.
