---
id: method.stewardship-posture
tier: 2
kind: method
origin: seed
title: stewardship posture — record decisions, verify at the right level, compound knowledge and tools, end sessions cleanly
owns:
  - stewardship-posture.decision-records
  - stewardship-posture.untrusted-model-output
  - stewardship-posture.synthetic-data-only
  - stewardship-posture.verification-levels
  - stewardship-posture.compounding-knowledge
  - stewardship-posture.session-closure
requires:
peers:
  - method.engineering-posture
  - method.design-posture
load_when:
  - "how do I record this decision, write an ADR"
  - "can I trust this model output, fabricated fact or citation"
  - "test or demo data from production, fixtures, anonymization"
  - "which test level, unit vs integration vs e2e"
  - "ending the session, handing off in a known state"
  - "should this script become a durable tool"
est_tokens: 1050
---

# Stewardship posture

The record/verify/knowledge/session/tools principles: how work is
recorded, validated, persisted, and handed off so it compounds instead
of evaporating with the session.

## 1. Record decisions; do not editorialize

When you make a choice, record what you chose, why, what evidence
supports it, what alternatives you rejected, and how reversible it is.
ADRs are the format. Do not pad ADRs with philosophy; record the
decision.

## 2. Treat model output as untrusted

Anything an LLM produces — including this agent — is unvalidated until
deterministic code (or a human) has checked it. Schemas, parsers, type
checkers, linters, and unit tests are the validators of choice. The
knowledge graph keeps model output grounded in current, version-pinned
facts; specs keep it grounded in the agreed behavior. Never fabricate a
fact, version, or citation to fill a gap — an honest "not recorded" is
usable; a confident invention is a trap.

## 3. Never source test or demo data from production

Production data may carry personal, health, financial, or otherwise
regulated information, and there is rarely an anonymization step you can
trust. Fixtures, seed data, demo environments, and examples in prompts
are **synthetic** — generated to match the shape and constraints of
real data without being any real record. Masking is not anonymization.
A copied "sample to reproduce a bug" is a disclosure.

## 4. Convert ambiguity into artifacts

Every ambiguous requirement becomes an assumption in grill.md and an
open question with a named owner. Specs that depend on flagged
assumptions are explicitly marked `draft` until confirmed. Decisions
made under ambiguity are tagged reversible.

## 5. Verify at the level where failure is most informative

Unit tests for pure logic. Integration tests at adapter boundaries.
Contract tests at API and structured-output boundaries. End-to-end
tests for critical user flows. Evaluation suites for AI behavior. A
graph lint for the knowledge layer. Manual review for high-impact
actions. Pick the level; do not test through it. And verify the
*knowledge*, not only the code: a fresh-context agent should be able to
navigate the graph to correct answers and reject false premises — if it
can't, the map is wrong, not the reader.

## 6. The knowledge graph and the spec catalog compound; memory does not

Agent memory of library APIs and system structure is unreliable across
versions and even within them. The knowledge graph — its nodes, and the
version-pinned library wiki at its leaves — is local, sourced, and
deduplicated: every fact has exactly one home, so it is updated in one
place instead of drifting across many. When graph and memory disagree,
the graph is right. Specs are the analogous local source of truth for
*project behavior*; when memory of "what we built" disagrees with the
spec catalog, the spec catalog is right.

## 7. End every session in a known state

Specs touched, files changed, docs updated, gates run, gates passed,
known limitations, recommended next step. The session ends when the
project is in a state another agent could continue cold. Otherwise the
session has not ended; it has paused.

## 8. Build tools to last, not to discard

A capability you will exercise again is an asset; a script you rewrite
each session is rework that also drifts, because every rewrite is a
fresh chance to get it subtly wrong. Before writing throwaway code to
perform an operation, ask whether an agent, expert, or skill will
plausibly perform it again in a later, independent session. If so, the
unit of work is a durable tool — real code with a stable interface,
authorized by a test — not a one-off you delete when the task closes
(see `method.engineering-posture`).

Durable tools compound the way the graph and the spec catalog do (§6):
built once, catalogued once, discovered by the next agent instead of
reinvented from memory. So when a task produces one, it is handed to the
librarian and recorded in `docs/graph/tools/` — its interface and
invocation named — exactly as knowledge of interest is canonized. A tool
nobody can find is a tool the next session rewrites
(see `method.engineering-posture`).

The exception is the genuine one-off and the throwaway prototype written
to learn a library or shape — the same carve-out the test-first rule
grants; those stay disposable and are not catalogued. The trigger is
recurrence across sessions, not size: a ten-line command three future
tasks will need is a tool; a hundred-line spike you delete tomorrow is
not.

## Neighbours

- `method.engineering-posture` — how the work itself is scoped and
  landed — cross when stewardship questions arise mid-change.
- `method.design-posture` — the structure being recorded — cross when
  an ADR captures a design decision.
