---
name: verify
description: 'Run the verification gates that apply to the current change and record their exact commands and outcomes in docs/graph/runbooks/verification.md. Use at the end of every increment and before any merge or deploy. Gates: formatter, linter, type check, unit, integration, contract, end-to-end, build, security scan, smoke test, evaluation suite, manual review. Every gate is reported as exactly one of three states — executed (run this pass), discovered (exists but not run this pass), or absent (with a dated reason and a planned-add owner) — so silence never implies a pass.'
id: protocol.verify
tier: 2
kind: protocol
origin: seed
title: verify — risk-proportional gates that pass, and mean something, before merge
owns:
  - rule.verify
  - verify.gate-states
  - verify.risk-depth
requires:
peers:
  - protocol.test-first
  - protocol.recover
  - protocol.canonize
  - protocol.deliver
  - skill.validate-knowledge
load_when:
  - "increment done, ready to merge or deploy"
  - "which gates to run, verification runbook"
  - "tests pass but is it verified, green lie"
  - "refactor or migration must preserve behavior"
  - "record a missing or skipped gate"
est_tokens: 2100
command: true
---

# Protocol: verify

Use this at the end of every increment and before any merge or deploy.
The deliverable is a list of gates run, their commands, and their
outcomes, recorded in `docs/graph/runbooks/verification.md`.

This node owns **the verify rule** — gates pass, and mean something,
before merge. No work is "done" until the gates proportional to its
blast radius have run, with commands and results recorded in
`docs/graph/runbooks/verification.md`. A gate not yet available is
recorded **absent** with a date — never silently dropped, never faked
green. A gate that runs but asserts nothing is a **green lie** —
worse than a missing gate, because it is trusted. After building or
adopting the graph, validate the *knowledge* too
(`docs/graph/skills/validate-knowledge.md`). `tester` and
`reliability` own this rule.

**Actor:** `tester` runs the gates (`reliability` for operational and
deploy gates) in its own context and reports outcomes in its handback;
the runbook entry is part of that worker's write scope. The
grill.md §15 record (step 8) is the session's — the plan-of-record is a
session-owned operational artifact (§3.3).

## The gates

Select the gates that apply to the change. Use the lowest level that
catches the kind of bug you care about; don't run every gate on every
change.

| Gate                 | Catches                                                       |
|----------------------|---------------------------------------------------------------|
| Formatter            | Style drift.                                                  |
| Linter               | Common bugs, anti-patterns, undocumented behaviors.           |
| Type checker         | Contract violations across module boundaries.                 |
| Unit tests           | Pure-logic regressions.                                       |
| Integration tests    | Adapter and boundary regressions.                             |
| Contract tests       | API and structured-output regressions.                        |
| End-to-end tests     | Critical-flow regressions.                                    |
| Behavior-preservation | A refactor/migration changed observable behavior beyond an enumerated intended-delta list. |
| Build                | Distributable artifact health.                                |
| Security scan        | Known vulnerable dependencies, secret leaks, static rules.    |
| Smoke test           | Deployed system is at least minimally alive.                  |
| Evaluation suite     | LLM/VLM behavior regressions.                                 |
| Performance test     | Latency, throughput, memory budget regressions.               |
| Graph lint           | Knowledge-graph contract: duplicate facts, broken edges, leaked version pins. |
| Spec-coverage lint   | Live spec contracts with no test naming them (`python3 docs/graph/spec-lint.py`) — the §3.1 "specs are executable" claim, checked mechanically. |
| Manual review        | High-impact, non-automatable judgment.                        |

## Risk-proportional gate depth

Verification depth follows the change's blast radius, not habit. Start
from the change class, not the gate list:

| Change class                                                        | Minimum gate depth                                                    |
|---------------------------------------------------------------------|------------------------------------------------------------------------|
| T1 trivial edit (no behavior/contract surface)                      | The one focused check that actually covers it (formatter/linter/build). |
| Local logic change, contracts unchanged, affected path known        | Cheap static gates + the focused unit/integration tests on that path.  |
| Shared contract, public interface, or persisted format changed      | Full battery on the affected boundary: contract tests, integration, neighboring regression suites. |
| Central abstraction, dependency direction, concurrency, auth/security, data migration | Broad system gates: full test suite, security scan, e2e on critical flows, manual review. |
| Affected scope genuinely uncertain                                  | Treat as the row above; uncertainty buys breadth, never a discount.    |

Escalate one row the moment a "local" change turns out to touch a
shared surface. Never run the broad battery on a provably local change
out of ritual — wall-clock and attention are budget too.

## Workflow

1. **Pick the applicable gates** from the risk table above and the gate
   table. The reviewer's checklist usually tells you which. Order by
   risk: identify the assumption most capable of invalidating the
   increment and gate that first. Prefer one high-information gate
   that covers several failure modes over overlapping gates that
   re-test the same property; verification stops when the mandatory
   gates pass and the remaining uncertainty cannot materially change
   the result (proportionate verification —
   `docs/graph/method/engineering-posture.md`) — not when every
   possible gate has run.
2. **Run them in order**, cheapest first (formatter, linter, type
   check) and only proceed to slower gates if the cheap ones pass.
3. **Record outcomes** in `docs/graph/runbooks/verification.md` under the
   increment heading:

   ```
   ## Increment <title> (YYYY-MM-DD)
   - Formatter: `<command>` — PASS
   - Linter: `<command>` — PASS (warnings: 2, all in docs/)
   - Type check: `<command>` — PASS
   - Unit tests: `<command>` — PASS (47 cases)
   - Integration tests: `<command>` — PASS (12 cases)
   - Eval suite: `<command>` — PASS (rubric score: 0.92, gate 0.85)
   ```

4. **Report every gate as exactly one of three states — silence must
   never imply a pass.** Each gate you considered lands in exactly one
   of these, and is recorded as such:

   - **executed** — actually run this pass, with its command and result
     (the entries in the block above). If it fails, either fix the
     increment or hand it back; do not record a fake PASS.
   - **discovered** — known to exist (you read it in the source or
     config) but *not* run this pass. This is the middle rung: record it
     as discovered-not-run so it can never be mistaken for an executed
     pass:

     ```
     - End-to-end tests: DISCOVERED, not run (2025-06-01) — suite exists (e2e/), out of scope for this increment
     ```

   - **absent** — does not exist yet. Record it with a date, a reason,
     and the owner who will add it:

     ```
     - Smoke test: absent (2025-06-01) — no deploy target yet; reliability adds it with the first deploy (see grill.md §12)
     ```

   Adopting an existing codebase with no test or gate infrastructure is
   not an excuse to leave the runbook empty: record each standard gate
   explicitly as `absent (YYYY-MM-DD) — <reason>`. A blank verification
   runbook is indistinguishable from one nobody checked, so it is not an
   acceptable resting state (the verify rule above).

5. **The three states are honest only if an executed PASS means
   something — the green-lie clause of the rule.** A test command with no
   tests, a linter over an empty set, a type check with everything untyped:
   these "pass" and mean nothing. Do not cite a vacuous pass as
   evidence, and do not wire such a gate into CI. Land the real check
   first (a test that asserts, a rule that fires); *then* add the gate,
   in a later increment — never both in the same one.

   A gate that *does* execute and *does* assert can still lie by not
   discriminating what it claims. A recorded verdict uses only the words
   the check actually proved, never the words of the goal the check
   served. And an invocation-*count* assertion on a mock or collaborator
   passes vacuously the moment the code under test stops calling that
   collaborator for an unrelated, wrong reason — assert on the actual
   destination, content, or argument passed, which cannot go vacuous the
   way a bare count can. (Whether a *test* discriminates the change it
   covers is `test-first`'s rule, not this one.)

6. **For the knowledge layer**, run the graph lint
   (`python3 docs/graph/graph-lint.py`) and, after a large docs change
   or an adoption, validate that the graph can orient a fresh agent and
   resist false premises (`docs/graph/skills/validate-knowledge.md`). A
   knowledge base with no passing lint has already begun to rot.

7. **For LLM/VLM features**, also record latency and (when relevant)
   token cost as metrics, even if they're not pass/fail.

8. **Update grill.md** section 15 (Changelog) with the date and
   verification outcome.
9. **Hand off.** When the gates for the whole piece of work are green,
   hand to `canonize` (close-out) to persist what the work taught, then
   to `deliver` for the handoff package.

## Adding a new gate

If verification reveals a kind of bug that no existing gate would have
caught, add a gate. New gates:
- Pick the lowest level that catches the bug.
- Get a test case that reproduces the bug (RED).
- Get added to the verification runbook in the same increment.
- Get added to CI in the next reliability-owned increment.

## Behavior-preserving changes (refactors, migrations, dependency bumps)

When a change must preserve observable behavior — a refactor, a framework
or dependency migration, a re-platforming — "it builds and the tests pass"
is not the gate; **unchanged behavior** is. Two disciplines make that
mechanically checkable:

- **Characterize first, then change.** Before touching the code, capture a
  baseline oracle of the current observable behavior (endpoint responses,
  persisted shapes, message payloads, computed outputs), normalized to mask
  only volatile leaves (timestamps, ids, tokens). This is the RED spine: it
  must exist and pass on the *pre-change* code, or the preservation claim is
  unfalsifiable. On a codebase with no tests this baseline is often the only
  executable gate — say so, and treat effort estimates as floors carrying
  that risk.
- **Diff against the baseline; allow only an enumerated intended-delta
  list.** After the change, re-capture and diff. The gate passes only if
  everything matches the baseline *except* an explicit list of intended
  deltas — each row naming the change and why the flip is a deliberate
  strengthening, not a convenience relaxation. Byte-identical output is the
  wrong contract; observable-behavior preservation is. An unexplained diff,
  or an additive-only edit to the pinning tests, is a red flag to justify
  before the gate is green — never a silent re-baseline.

## Tolerating a known defect (the self-expiring exception)

When a suite must pass while a confirmed bug still lives, do not weaken or
skip the gate. Assert *today's broken behavior on purpose* under a named
marker (a `KNOWN_BUG_<id>` assertion) and record the trigger that should
tighten it — e.g. "accept a 500 on this path until the auth bug is fixed →
then require 401". The assertion passes while the bug lives and flips to
FAIL the moment the bug is fixed without the assertion being tightened, so
the debt is mechanically visible and self-retiring. A silently-relaxed gate
hides a known hole; a `KNOWN_BUG_*` assertion advertises it and dates its
own removal.

## Anti-patterns

- "All gates green, but I disabled the flaky one." Either fix the
  flake or document it explicitly; do not silently disable.
- "Tests pass locally, didn't run them in CI." If the gate isn't in
  CI, it isn't a gate; it's a hope.
- "We don't have time for the eval suite this increment." That is the
  signal to merge a smaller increment, not to skip the gate.
