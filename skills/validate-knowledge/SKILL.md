---
name: validate-knowledge
description: 'Prove that a knowledge base actually works before trusting it — after building or adopting docs, a knowledge graph, or a wiki, verify it can orient a fresh agent and resist false premises. Use at the end of an adoption, after a large docs change, or before relying on the graph to route work. Two methods: clean-context test agents answering known-answer and adversarial questions, and enforcement tests that plant a violation and confirm the linter catches it. A smoke test proves code runs; this proves the knowledge is correct, navigable, and honest.'
id: skill.validate-knowledge
tier: 2
kind: skill
origin: seed
title: validate-knowledge — prove the knowledge base orients a cold agent and its guard rails actually catch
owns:
  - validate-knowledge.method
  - validate-knowledge.adversarial-questions
requires:
peers:
  - skill.knowledge-graph
  - skill.context-router
load_when:
  - "validate the knowledge graph after adoption"
  - "clean-context test agent questions"
  - "false-premise adversarial question"
  - "prove the linter catches a planted violation"
  - "is the graph trustworthy"
artifacts:
  - templates/prompts/clean-context-validation-brief.md
est_tokens: 1050
---

# validate-knowledge

Documentation you wrote is documentation you already believe. That is
exactly why you cannot validate it yourself: you fill every gap from
memory the reader won't have. A knowledge base is only proven when a
context that does *not* share your memory can use it to reach correct
answers — and when its own guard rails demonstrably catch violations.

This complements the code smoke test. A smoke test proves a snippet
runs; this proves the surrounding knowledge is correct, navigable, and
honest.

For version drift specifically — whether the library wiki's pins still
match the resolved dependencies — the complementary check is the
lightweight source-reconciliation pass in `research-and-ingest`; this
skill tests prose, not pin freshness.

## Method 1 — clean-context test agents

Spawn agents with **no prior context** on the project and have them
answer questions using only the knowledge base. Grade the answers
against ground truth you already know.

1. **Give them the entry point, not the answers.** Tell them to read
   the kernel and follow it — the same cold start a real session has.
   Do not paste the facts you're testing for.
2. **Ask questions whose correct answer you know**, spanning the base:
   a fact lookup, a "how does X work," a change-impact ("what must I
   check before editing Y"), a trace across subsystems.
3. **Require them to declare what they loaded** — which nodes/pages,
   and what they deliberately skipped. This tests the *routing*, not
   just the content: the right answer reached by loading half the
   codebase is a routing failure.
4. **Include adversarial false-premise questions.** "Confirm the
   system uses <technology it does not use>." "Show me the table where
   X is stored" (when X isn't stored). A trustworthy base lets the
   agent *reject* the premise with a citation; a weak one lets the
   agent hallucinate agreement. This is the highest-value test — it
   catches the gaps that ordinary questions glide over.
5. **Grade and fix — independently.** Every wrong answer, every missed
   rejection, every over-broad load is a defect in the base, not the
   agent. Fix the node or the trigger; re-run. In a standalone run the
   grading is done by (or reviewed by) an agent that did not author the
   base; when that is impossible, record the deviation with the result.
   (`docs/graph/protocols/grow.md` Phase 6 already enforces this inside
   `grow`.)

A base passes when a cold agent answers correctly, loads minimally, and
refuses the false premises — citing sources, without opening the raw
source tree.

## Method 2 — enforcement tests

A rule the tooling claims to enforce is only enforced if you have seen
it fail. Prove each guard rail:

- **Plant a violation, confirm the catch.** Copy the graph to a scratch
  location, introduce a duplicate fact-key, a broken edge, a version
  pin in the wrong node — and confirm the linter fails with the right
  message. A linter you have only ever seen pass is a linter you have
  not tested.
- **Prove drift detection.** If generated views are produced from
  sources (see `install`/multi-tool integrations), edit a source and
  confirm the `--check` mode flags the stale view; then regenerate and
  confirm it clears.
- **Wire the passing linter into the verification gates** so the base
  cannot silently rot.

## Scope and cost

Match the effort to the base. A handful of clean-context questions and
one enforcement pass is enough for a small docs set; a large graph
warrants questions spanning every tier and every guard rail. Prefer a
few sharp adversarial questions over many easy ones — the easy ones
mostly re-confirm what you already trust.

Run this read-only. The test agents must not modify the project; their
output is evidence you act on, not changes they make.

## What this catches that nothing else does

- A node that is *correct but unreachable* — the router never surfaces
  it, so the fact might as well not exist.
- A base that reads well to its author but leaves a newcomer guessing.
- A fabricated fact or citation that survived authoring — an
  adversarial question is how it surfaces.
- A linter or drift-check that was never actually exercised and quietly
  does nothing.

## Anti-patterns

- **Validating with an agent that shares your context** (a fork of
  yourself). It inherits your assumptions and will pass a base a
  stranger would fail. Use a clean context.
- **Grading your own base.** Authoring the nodes and then scoring the
  answers re-imports the assumptions the clean context was meant to
  strip. Have a non-author grade or review the grading, or record the
  deviation.
- **Only asking questions the docs obviously answer.** You are testing
  the seams, not the center.
- **Treating a wrong answer as the test agent's failure.** If the base
  is right and reachable, a competent cold agent finds it. A wrong
  answer is a map defect.
- **Declaring the linter "tested" because it passes on the real tree.**
  It has to be shown *failing* on a planted violation to count.

## Reference files

- `docs/graph/skills/knowledge-graph.md` — what is being validated.
- `docs/graph/skills/context-router.md` — the routing these tests exercise.
- `docs/graph/protocols/verify.md` — where the passing linter becomes a gate.
- `docs/graph/templates/prompts/clean-context-validation-brief.md` — the
  parameterized brief for a test agent.
