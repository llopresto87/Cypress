---
name: verify
description: 'Run the verification gates that apply to the current change and record their exact commands and outcomes in docs/graph/runbooks/verification.md. Use at the end of every increment and before any merge or deploy. Gates: formatter, linter, type check, unit, integration, contract, end-to-end, build, security scan, smoke test, evaluation suite, manual review. Every gate is reported as exactly one of three states — executed (run this pass), discovered (exists but not run this pass), or absent (with a dated reason and a planned-add owner) — so silence never implies a pass. A gate that executed and found nothing reports its positive control alongside the zero; a gate whose test was never seen red has authorized nothing; an assertion is judged by its shape (composition, literal expectations, independent witness), a disagreement between a check and its subject indicts the instrument first, and a lifecycle status of closed is itself a gate — it requires evidence a reader can open.'
id: protocol.verify
tier: 2
kind: protocol
origin: seed
title: verify — risk-proportional gates that pass, and mean something, before merge
owns:
  - rule.verify
  - verify.gate-states
  - verify.risk-depth
  - verify.null-result
  - verify.composition
  - verify.silent-substitutes
  - verify.test-first
  - verify.status-evidence
  - verify.tool-faults
  - verify.characterize
  - verify.measure-integrity
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
  - "gate found nothing, zero results, is that a real finding"
  - "refactor or migration must preserve behavior"
  - "record a missing or skipped gate"
  - "mark it closed, what counts as status evidence"
  - "assert the count or the composition, expected value derived from the subject"
  - "silent no-op, empty output that looks like success"
  - "gate never went red, does the green mean anything"
  - "golden master, stored oracle before a migration"
  - "gate script left half-applied state, environment failure or repository failure"
  - "the checker disagrees with the file, fix the tool or the declaration"
est_tokens: 5350
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
worse than a missing gate, because it is trusted. A binding rule or
done-criterion is a control only once it is a mechanically checkable
predicate wired into a gate and asserting the property itself, not a
positional proxy for it — a comment, a README warning, or a review habit
is never a control. After building or adopting the graph, validate the
*knowledge* too (`docs/graph/skills/validate-knowledge.md`). `tester`
and `reliability` own this rule.

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
| Status register      | A lifecycle status whose required companion is missing — a `closed` with no evidence, a `hotfix` with no owner (`python3 docs/graph/status-register.py`). |
| Spec-coverage lint   | Live spec contracts with no test naming them (`python3 docs/graph/spec-lint.py`) — the §3.1 "specs are executable" claim, checked mechanically. |
| Plan-of-record lint  | grill.md out of shape — a §9 row depending on a later row, a §5 silent about a page §9 depends on, a contract the plan invents or never implements (`python3 docs/graph/grill-lint.py`) — the §3.3 "it is a plan" claim, checked mechanically. |
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

## A gate that found nothing has not yet said anything

`executed` splits further when the result is empty. A scan with no
findings, a grep with no hits, a discovery run that collected no tests,
and a port check that saw nothing open all return exactly what a
*broken probe* returns. The two are indistinguishable from the result
alone, so a zero is not yet evidence — it is a claim awaiting its
control.

**Report a zero only with a positive control the probe did detect on
the same run.** Point the scanner at a known-vulnerable fixture, grep
for a string you know is present, assert the discovery run collected
the tests you know exist. The control proves the instrument was live
and aimed where you think it was aimed; only then does the empty result
carry information.

A checker you own goes further: it counts what it examined and **fails
when that count is zero inside its perimeter** — a glob that matched
nothing, a suite that collected no tests. An empty subject set genuinely
outside the repository is an honest skip; inside it, an environment
failure. The empty-input pass is the false green that hides every other
one.

State the coverage the control establishes, not more. "No secrets
found by <tool> across <paths>, control fixture detected" is a
finding. "No secrets" is a hope with a command-line history.

Order protects the reading the same way the control does. The criterion
that decides a change is written before the measurement runs; a result
that fails it is a recorded negative and the change is reverted, never
rationalized into a partial success.

This is `verify.gate-states` one level down: the three states say
whether a gate *ran*, and a run that reports nothing still owes proof
that it *could have* reported something. Control depth follows the same
blast-radius rule as gate depth above — a throwaway grep needs a
one-line sanity check, a security scan gating a deploy needs a fixture
that is known to trip it.

## Silent no-ops and plausible substitutes are defects

The indistinguishability that makes a bare zero worthless in a gate is
a defect when the *system* produces it. A missing required input, an
unrendered template, a skipped step, an unmatched route, a computation
that cannot produce a valid answer, an oversized payload clamped to fit
— each must fail visibly and distinctly, never emit an empty, clamped,
or plausible-looking result a caller cannot tell from success. The
failure must be representable in the type or status the caller receives,
never as a value the success path could also produce. A catch-all that
answers a missing route with a success-shaped response, a status column
no code writes, a presence-guard that skips silently when its
configuration is absent, and an encoding where "not yet decided" and
"deliberately empty" look alike are the same defect in different
clothes.

The gate over such a path asserts the *distinct* failure — the status,
the omitted fields, the raised error — and asserts the degraded case as
its own named passing outcome. Two empty results that agree have proved
nothing; a gate that lets an empty result pass by default has installed
the substitute it was meant to catch.

## An assertion is only as strong as its shape

A gate that executes and asserts can still be tautological. Three
questions decide whether an assertion is a witness or an echo:

- **Composition, or a count?** An aggregate total passes again the
  moment offsetting errors cancel; a count returns to its expected value
  while the underlying set is wrong. Assert what the result is made of.
  Where completeness matters and no gate can check it, do the full set
  difference — a spot-check of the newest items is not an audit. Report
  new coverage as the delta, never the run total, and establish "no
  regression" on a red baseline by comparing the *names* of failing
  tests before and after, not their number.
- **Is the expected side independent of the subject?** An expectation
  derived from the value under test, or a gate seeded from the artifacts
  it checks, agrees with every mutation and asserts nothing. Spell
  expected values as literals; verify a derived value by a join across
  independently maintained sources, never by re-reading its own input.
  The test for any duplicate is the same: if one coordinated edit could
  change both copies with nothing failing, the copy is not an
  independent witness — and a copy that *is* one is kept on purpose.
- **Does a failure say what drifted?** Assert each dimension under its
  own name so a red identifies the property that moved, and choose a
  witness sensitive to the change you guard against — a projection only
  witnesses what it is sensitive to. The invocation-*count* assertion on
  a mock is the canonical failure: it passes vacuously the moment the
  code stops calling the collaborator for an unrelated, wrong reason.
  Assert on the destination, content, or argument passed, which cannot
  go vacuous the way a bare count can.

Whether a *test* discriminates the change it covers is `test-first`'s
rule; this section is about what a recorded assertion can have proved.

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
2. **Run them in order**, cheapest and most syntactic first (formatter,
   linter, type check) and only proceed to slower gates if the cheap
   ones pass. All checks live behind **one entry point** whose default
   tier runs on a clean checkout with no external runtime; heavier
   tiers are explicit opt-in strict supersets, and a tier whose tooling
   is missing fails rather than degrading to the tier below. CI is a
   caller of that entry point, never a second home for the checks.
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
   - Not verified: <property> — deliberately excluded, owner <who>, tracked in grill.md §12
   ```

   The entry closes with what was **not** verified and deliberately
   excluded, blocked distinguished from skipped, so a partial pass is
   never read as completion.

4. **Report every gate as exactly one of three states — silence must
   never imply a pass.** Each gate you considered lands in exactly one
   of these, and is recorded as such:

   - **executed** — actually run this pass, with its command and result
     (the entries in the block above). A zero exit code is `executed`
     only if the check's prerequisites held and its assertions ran: a
     step that skipped itself, a suite whose precondition never holds
     here, a run whose test count came back short, a configured-but-inert
     tool — these are **discovered**, whatever the runner printed, and a
     test named for more than it asserts is recorded under what it
     asserts. If it fails, either fix the increment or hand it back; do
     not record a fake PASS.
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
   in a later increment — never both in the same one. A gate is trusted
   only once a **planted violation** has turned it red, naming the
   offender, and the plant's removal has turned it green again; that
   demonstration is part of the gate's record, and is repeated after any
   refactor around the assertion — a surviving tautology is worse than a
   deleted check.

   A gate that *does* execute and *does* assert can still lie by not
   discriminating what it claims. A recorded verdict uses only the words
   the check actually proved, never the words of the goal the check
   served, and names what the gate **structurally cannot see** — a
   structural linter is evidence about shape, never content; a result at
   one layer is never evidence about another; a zero-finding scan is a
   claim about scope before it is a claim about content.

   **The gate-side of test-first.** A gate authorizes a change only if
   its test was seen to fail *before* the change, for the reason named
   in advance — a gate whose test never went red has authorized nothing,
   because it may be green for exactly the reason it would be green
   against an empty implementation. The runbook entry for a new gate
   records the red, with its actual failure text, before the green.
   Getting RED for the right reason, proving an inherited suite by
   mutation, and the pure-refactor variant (the same gates green
   immediately before and after the edit) are
   `docs/graph/protocols/test-first.md`'s workflow; verify's stake is
   only that the record shows the red.

6. **For the knowledge layer**, run the graph lint
   (`python3 docs/graph/graph-lint.py`) and the status register
   (`python3 docs/graph/status-register.py`), and, after a large docs
   change or an adoption, validate that the graph can orient a fresh
   agent and resist false premises
   (`docs/graph/skills/validate-knowledge.md`). A knowledge base with no
   passing lint has already begun to rot.

7. **For LLM/VLM features**, also record latency and (when relevant)
   token cost as metrics, even if they're not pass/fail.

8. **Update grill.md** section 15 (Changelog) with the date and
   verification outcome.
9. **Hand off.** When the gates for the whole piece of work are green,
   hand to `canonize` (close-out) to persist what the work taught, then
   to `deliver` for the handoff package.

## `closed` means evidenced

A lifecycle status is a gate on a record the way a test is a gate on
code, and it lies the same way. `closed` means *resolved with evidence*:
`status_evidence` names a path#anchor, a commit, or a gate-run id that a
reader can open — the same thing an `executed` runbook entry records.
When that evidence does not exist yet, the honest states are `hotfix`
(resolved improperly, a proper fix owed) and `deferred` (parked, with
the condition that reopens it), each with an owner, so nothing rests as
"done" on a promise. A `closed` without evidence is the green lie one
level up: a gate without an assertion says the check ran and proved
nothing; a `closed` without evidence says the work finished and proves
nothing, and is trusted just as readily.

Promotion is the same gate at the other end of a record's life. A
specification is not promoted to a live status until executable
assertions covering its contracts exist and pass, and the promotion
lands in the same change that adds them; a live status over an empty
assertion set is a false green.

The vocabulary and each status's required companions live in
`docs/graph/_schema.md` §"Lifecycle status" — read them there, never
restate them. The enforcement is the delivered
`docs/graph/status-register.py` in its lint role: a `closed` with no
companion fails the run with ``status 'closed' requires
`status_evidence` ``, exactly as a missing gate fails this protocol.
Reviewing what is still `open` or `hotfix` at close-out is `canonize`'s.

## Adding a new gate

If verification reveals a kind of bug that no existing gate would have
caught, add a gate. New gates:
- Pick the lowest level that catches the bug.
- Get a test case that reproduces the bug (RED).
- Get added to the verification runbook in the same increment.
- Get added to CI in the next reliability-owned increment.

A gate is a tool, and a tool that can fail halfway is a second thing to
verify. Any gate or verification script you author is **all-or-nothing**:
it validates everything it will touch before it writes anything, so a
failure never leaves a half-applied state; it runs under strict error
and unset-variable handling and resolves its own root from its location,
never from the working directory; and it keeps **environment failures
distinct from repository failures** in both remedy text and exit status
— a missing interpreter, an absent fixture, or a tool that could not
start never degrades into a skip or an empty success, or a broken
environment reads as a clean tree. Fixtures raise on an environment
fault and reserve the empty result for a genuine empty success. Fail
closed by default; a soft mode for local troubleshooting is an explicit,
documented switch. Whether a check deserves to become a cataloged tool
at all is `toolcraft`'s doctrine.

## Behavior-preserving changes (refactors, migrations, dependency bumps)

When a change must preserve observable behavior — a refactor, a framework
or dependency migration, a re-platforming — "it builds and the tests pass"
is not the gate; **unchanged behavior** is. Two disciplines make that
mechanically checkable:

- **Characterize first, then change — and land the oracle as its own
  slice.** Before touching the code, capture a stored oracle of the
  current observable behavior (endpoint responses, persisted shapes,
  message payloads, computed outputs), one golden master per consumer,
  normalized to mask only volatile leaves (timestamps, ids, tokens).
  Capture it read-only: once a migration has overwritten the system,
  that evidence is unrecoverable. The oracle must exist and pass on the
  *pre-change* code and land **before any code change**, or the
  preservation claim is unfalsifiable; a new guard is seeded green from
  today's state and tightened only in the increment that can prove the
  tightening safe. On a codebase with no tests this baseline is often
  the only executable gate — say so, and treat effort estimates as
  floors carrying that risk. The test-shaped form of the same move — the
  characterization test that becomes your RED — is
  `docs/graph/protocols/test-first.md`'s characterize-first rule.
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

## When the check and its subject disagree

What a gate measures is the **effective state** — the resolved, merged,
deployed reality, read back through the same path a real client takes —
never a declaration, a source file, a tool's own change report, or an
exit code that says the state *should* have converged; a slice that
mocks a layer has not proven the architecture, and a check that reaches
the service by a shortcut cannot see faults in the path it skipped. The
same holds for a control: verify its flag value and its wiring on every
code path that can produce the outcome, not the presence of the
implementing code, the documentation, or the fact that the system works
— and state the strength it actually enforces, never the strength its
name implies; present-but-unwired permission machinery is protection
that does not exist.

When the check and its subject disagree, **the instrument is the first
suspect.** Put the prior on the checker: read the raw source at the
cited location and verify a tool's finding against the underlying data
before recording it. Two of your own contradictory measurements indict
your method, not the other reader. Match the instrument's shape to the
subject's — a line-oriented scan over multi-line constructs produces a
number that looks like evidence and is not. A tool that produced a false
positive is fixed or deleted in the same change that retracts its
output; a discredited tool left in place will be quoted again.

Never satisfy a check by changing what it measures: not by removing the
thing it observes (retiring an observed value is a separate, argued
decision from making it correct), not by falsifying the declaration the
tool reads (fix the tool, so the declaration keeps meaning intent), not
by reverting the change that tripped it. When an assertion fails because
the product *deliberately* changed, update the assertion — but never
revert a deliberate change, least of all a security revocation, to make
a suite green. When it fails because it found a real defect, pin the
broken behavior as a characterization and route it to a decision owner
rather than adjusting the test until it passes; and when the test you
discount was a contract's only verifier, record the coverage loss with
the discount.

A second measurement confirms the first only if it **re-derives the
result from the artifact by a different method** — a recount that reuses
the upstream number or premise is the same measurement written twice,
and three counts sharing one premise are one count.

## Anti-patterns

- "All gates green, but I disabled the flaky one." Either fix the
  flake or document it explicitly; do not silently disable.
- "Tests pass locally, didn't run them in CI." If the gate isn't in
  CI, it isn't a gate; it's a hope.
- "We don't have time for the eval suite this increment." That is the
  signal to merge a smaller increment, not to skip the gate.
- "The scan came back clean." Clean against what? A probe with a
  broken pattern, a wrong path, or an unbuilt image reports zero
  exactly as a healthy system does. No control, no finding.
- "The check was wrong, so I fixed the file it reads." Now the
  declaration records a bug instead of an intent, and the tool misfires
  on the next reader. Fix the instrument.
- "The step exited zero." Did it run? A skipped precondition, an empty
  collection, and a tool that could not start all exit zero when nobody
  made them fail. An exit code says a process ended, not that a property
  held.
