---
id: method.tiers
tier: 2
kind: method
origin: seed
title: tiers — task classification T0–T3 and each tier's execution path
owns:
  - tiers.definitions
  - tiers.hard-edges
  - tiers.execution-paths
requires:
peers:
  - method.delegation
load_when:
  - "which tier is this task, classify the task"
  - "is this T1 or T2, does this need the full funnel"
  - "how much process does this change need"
  - "can I just edit this directly, trivial edit"
est_tokens: 550
---

# Task tiers — classification and execution paths

Process is proportional to risk, and the tier is the unit of
proportionality. Classify every task before acting, say the tier out
loud, and reclassify upward the moment the work crosses a tier
boundary. Misclassifying down is a violation; escalating up mid-task is
normal and cheap.

## The tiers

| Tier | The task is…                                                     | Execution path                                                                                  |
|------|------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|
| **T0** | a question — nothing changes                                   | Resolve minimal nodes, read, answer with citations. No spawn. Compact delivery (`protocol.deliver`). |
| **T1** | a trivial edit with **no behavior, contract, or spec surface** — typo, comment, doc wording, formatting | The session edits directly — the one in-session authoring exception. One focused gate. Compact delivery with a one-line canonize self-record. |
| **T2** | a bounded change **already authorized** by an active spec and plan — a bug fix with a regression test, a covered increment | Spawn the minimal worker set. One **implementer** spawn, briefed with the contract text, may own RED→GREEN in a single context **when the increment covers a single contract and the RED is mechanical**; split tester/implementer when it spans contracts or the RED is judgment-heavy. The reviewer audit stays independent either way. Close-out spawn (`protocol.canonize`) + full delivery. |
| **T3** | anything that creates or changes behavior, architecture, contracts, dependencies, or is ambiguous — **and anything no other row clearly covers** | Full funnel: brainstorm* → specify → grill → test-first → verify → close-out → deliver. All doing delegated to clean-context specialists. |

## The hard edges

Two edges keep the tiers honest:

- **T1 is defined by what it cannot touch.** If the edit could alter
  behavior, an interface, a persisted format, security posture, or
  anything a spec covers, it is not T1 — reclassify. A config value
  change alters behavior; it is never T1.
- **T2 requires existing spec authorization.** No active spec contract
  covering the change means it is T3, however small it looks. A missing
  grill.md line for a spec-covered change is bookkeeping, not missing
  authorization — add the line on entry and stay T2.

## What every session produces

One of three things: a clarifying question (only when genuinely
ambiguous), a stated protocol invocation, or a verified, attributed
unit of work ending in a delivery.

For T2/T3, every piece of *doing* — investigating a subsystem, writing
a spec, a test, code, or a doc — is delegated to a clean-context
specialist that obeys the graph discipline; the session's own work is
routing, planning, briefing, communication, and acceptance
(`method.delegation`).

## Neighbours

- `method.delegation` — who executes each tier's path — cross when the
  tier is decided and workers must be chosen and briefed.
