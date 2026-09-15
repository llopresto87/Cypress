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
  - tiers.contained-lane
requires:
peers:
  - method.delegation
load_when:
  - "which tier is this task, classify the task"
  - "is this T1 or T2, does this need the full funnel"
  - "how much process does this change need"
  - "can I just edit this directly, trivial edit"
  - "small fix but no spec covers it, does it really need the full funnel"
  - "two-line bug fix in code no spec covers"
prevents: Every task handled at the same depth, so a typo fix is routed through the full pass and a migration is treated as a one-liner.
est_tokens: 850
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
| **T2** | a **contained change** — bounded, local, reversible — reached by either lane: the *covered lane*, already authorized by an active spec contract and plan line; or the *contained lane*, small enough that a regression test plus a why-record are the proportional authorization (`tiers.contained-lane`) | Spawn the minimal worker set. One **implementer** spawn, briefed with the contract text (covered lane) or the defect and its reproduction (contained lane), may own RED→GREEN in a single context **when the increment covers a single contract and the RED is mechanical**; split tester/implementer when it spans contracts or the RED is judgment-heavy. The reviewer audit stays independent either way. Close-out spawn (`protocol.canonize`) + full delivery. No brainstorm, no specify pass, no grill refutation. |
| **T3** | anything that creates or changes behavior at a scale the contained lane cannot hold, or changes architecture, contracts, dependencies, or is ambiguous — **and anything no other row clearly covers** | Full funnel: brainstorm* → specify → grill → test-first → verify → close-out → deliver. All doing delegated to clean-context specialists. |

## T2's contained lane — a small change no spec covers

Most maintenance is a defect fix or a small behavioral correction in
code that has no spec yet. Routing all of it to T3 buys a specify pass
and a grill pass to authorize three lines, and the cost is paid so
often that the funnel stops being believed. The contained lane is the
proportional answer: the authorization for a small change is **the
failing test that pins the new behavior** plus **a recorded why**, not
a spec document.

A change enters the contained lane only when **every** one of these
holds:

- **One surface.** A single module, package, or endpoint — not a
  contract, a public interface, a persisted format, or a schema.
- **No new dependency.** Adding one routes to `protocol.ingest-library`,
  which is T3.
- **Reversible.** Undoing it is a revert, not a migration. No one-way
  door, no data migration, no change to auth, authorization, secrets,
  concurrency, or a security boundary.
- **No spec owns the surface.** If an active spec covers it, this is the
  covered lane instead — amend the contract there and stay honest to
  §3.1.
- **The intent fits in a decision note.** If explaining the change
  honestly requires a spec, it *is* spec-bearing work: T3.

What the lane produces, and what it does not:

| Produced                                                             | Not produced                          |
|----------------------------------------------------------------------|---------------------------------------|
| A regression test written **before** the fix, naming the behavior — the executable record of the contract, and the §3.4 obligation in full | A spec document, its §0 sign-offs, or a `specify` pass |
| A **why-record** at close-out: what was wrong, why this fix, which test pins it — an ADR when a real choice was made among options, otherwise the plant `changelog.md` entry (`protocol.canonize`) | A grill refutation spawn, an architect pass, a devil's-advocate pass |
| A `grill.md` line added on entry — bookkeeping, so the plan-of-record stays a record of what happened | A full `grill` pass |
| The independent reviewer audit and the gates the change's blast radius earns (`protocol.verify`) | Any discount on verification — depth follows blast radius, never the lane |

The lane trades the *spec* for the *test plus the why*. It never trades
away the test, the review, the gates, or the record.

## The hard edges

Three edges keep the tiers honest:

- **T1 is defined by what it cannot touch.** If the edit could alter
  behavior, an interface, a persisted format, security posture, or
  anything a spec covers, it is not T1 — reclassify. A config value
  change alters behavior; it is never T1.
- **The covered lane requires existing spec authorization.** No active
  spec contract covering the change means the covered lane is closed —
  take the contained lane if it qualifies, else T3. A missing grill.md
  line for a spec-covered change is bookkeeping, not missing
  authorization — add the line on entry and stay T2.
- **The contained lane is unanimous, and it escalates on the first
  doubt.** Every condition above must hold; one that does not, or one
  you are unsure of, is T3. The moment the work turns out to need an
  interface change, a dependency, a migration, or a spec to explain
  itself, stop, say so, and reclassify upward — mid-task escalation is
  the expected outcome sometimes, not a failure.

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
- `protocol.canonize` — where the contained lane's why-record lands —
  cross at close-out.
