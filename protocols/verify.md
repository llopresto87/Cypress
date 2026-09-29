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
requires:
peers:
  - protocol.test-first
  - protocol.recover
  - protocol.canonize
  - protocol.deliver
  - skill.validate-knowledge
  - protocol.verify-new-gates
  - protocol.verify-disagreement
load_when:
  - "increment done, ready to merge or deploy"
  - "which gates to run, verification runbook"
  - "tests pass but is it verified, green lie"
  - "gate found nothing, zero results, is that a real finding"
  - "record a missing or skipped gate"
  - "assert the count or the composition, expected value derived from the subject"
  - "silent no-op, empty output that looks like success"
  - "gate never went red, does the green mean anything"
  - "scanner configuration or suppression file passed, was the input applied"
  - "grep count inflated by comments and prose that quote the identifier"
  - "chronic red gate, always red for an unrelated cause"
  - "tests whose subject is outside the shipped perimeter, excluded or skipped"
prevents: Gates that run and assert nothing, so green means the command exited zero rather than that the behavior holds.
est_tokens: 5786
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
done-criterion whose breach has a high blast radius
(`test-first.proportionate-checks`) is a control only once it is a
mechanically checkable predicate wired into a gate and asserting the
property itself, not a positional proxy for it — a comment, a README
warning, or a review habit is never a control. After building or adopting the graph, validate the
*knowledge* too (`docs/graph/skills/validate-knowledge.md`). `tester`
and `reliability` own this rule.

**Actor:** `tester` runs the gates (`reliability` for operational and
deploy gates) in its own context and reports outcomes in its handback;
the runbook entry is part of that worker's write scope. The
grill.md §15 record (step 8) is the session's — the plan-of-record is a
session-owned operational artifact (§3.3).

When each gate runs is `delegation.tip-cadence` (per increment, then the
full suite at the batch tip) and `delegation.mutation-at-end` (one
mutation pass per spec), both in
`docs/graph/method/delegation-cycle-economy.md`.

## The gates

Select the gates that apply to the change, at the lowest level that
catches the bug. Whether a check exists at all is
`test-first.proportionate-checks`.

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

The **tier does not pick the row; the blast radius does.** A T2
contained-lane change is usually the "local logic change" row, but a
three-line fix on a shared path earns the row its radius names — the
lane bought a cheaper *authorization*, never a cheaper gate
(`tiers.contained-lane`).

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
carry information. Run the check with the same privilege as the
operation it checks: a probe with less access than the copy, the
migration, or the scan it verifies silently skips what it cannot read,
and the shortfall reads as a defect in the subject. And never read
absence from output that was cut short for reading: a search piped
through a line cap is a sample, and a sample that missed the item is
not a search that proved it missing.

The control settles the instrument, not the subject. A negative result
is evidence about the exact subject that was presented and about nothing
that merely resembles it: a rejection collected by submitting a fresh,
equivalent input proves the system rejects that input, never that the
one you claim is dead is dead. Where the claim is about a specific
artifact, identifier, or credential, the run that proves it presents
that one.

A checker you own goes further: it counts what it examined and **fails
when that count is zero inside its perimeter** — a glob that matched
nothing, a suite that collected no tests. An empty subject set genuinely
outside the repository is an honest skip; inside it, an environment
failure. The empty-input pass is the false green that hides every other
one. It also reports every violation in its perimeter in one pass: a
checker that halts at the first makes each fix cost another run, and
its count of one says nothing about how many remain.

State the coverage the control establishes, not more. "No secrets
found by <tool> across <paths>, control fixture detected" is a
finding. "No secrets" is a hope with a command-line history.

A non-zero count has the mirror problem: it can be inflated by text
that only mentions what it counts. In a commented tree, prose and
comments quote the very identifiers being counted, so a bare pattern
counts the explanation along with the thing. Anchor the pattern to the
declaration form, filter comments out, or parse the file; for history,
read a name-only listing rather than output that also prints commit
messages. When a worker's count differs from yours, recheck your own
pattern first.

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

A gate that executes and asserts can still be tautological. Four
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
  The worst dependent expectation **defends the defect**: a fixture
  literal copied from what the code produced makes the assertion true
  only because the production code is wrong, so fixing the defect turns
  the test red. Ask of each expected literal where it came from.
- **Does a failure say what drifted?** Assert each dimension under its
  own name so a red identifies the property that moved, and choose a
  witness sensitive to the change you guard against — a projection only
  witnesses what it is sensitive to. The invocation-*count* assertion on
  a mock is the canonical failure: it passes vacuously the moment the
  code stops calling the collaborator for an unrelated, wrong reason.
  Assert on the destination, content, or argument passed, which cannot
  go vacuous the way a bare count can.
- **Value, or spelling?** A configuration contract asserts the
  effective value, read from whatever form it is written in (a literal,
  an interpolation, an interpolation with a default), never a required
  syntactic form. A rule about form can forbid the correct value
  written the other way, and can pass a wrong value written the
  expected way. When a refactor moves a value somewhere else, ask of
  each assertion left behind whether it can still fail; one that cannot
  is moved to where the value now lives, in the same change, because a
  tautological survivor is a green lie that a deleted check is not.

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
   `docs/graph/method/decision-economy.md`) — not when every
   possible gate has run.
2. **Run them in order**, cheapest and most syntactic first (formatter,
   linter, type check) and only proceed to slower gates if the cheap
   ones pass. All checks live behind **one entry point** whose default
   tier runs on a clean checkout with no external runtime; heavier
   tiers are explicit opt-in strict supersets, and a tier whose tooling
   is missing fails rather than degrading to the tier below. Automated
   runs call that entry point; they are never a second home for checks.
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

   Two failure modes live in the seams between these states. A harness
   that stops at the first failing assertion in a case reports a count
   that is a **lower bound**, not a total: every later assertion in that
   case would also have failed and was never reached, so a fix-and-recount
   loop reads as convergence while the real defect count is unknown. Say
   "at least N" until every assertion in the case has run. And a check
   recorded `discovered` or `absent` inside a list whose other rows are
   `executed` does not inherit their standing by sitting among them: a
   contract may not rest on such a row without saying so in the contract's
   own text, because an unmeasured assumption surrounded by measured ones
   is the one place in a verification record where being wrong costs
   nothing. So every `discovered` or `absent` row also says what it would
   have caught, in the form "unmeasured: X; if X is false, Y ships
   broken". A bare "not run, no container here" hides the belief;
   writing the sentence out states it, and a stated belief invites the
   few minutes of measurement that would refute it.

   A skip count reads as work pending; an exclusion states the
   perimeter. So before claiming that a suite's totals describe the
   perimeter that ships, show that none of its skips is a test whose
   subject does not exist inside that perimeter. The evidence for such
   a test is its removal from collection, with a written justification
   for it and the check that established that its subject is absent; a
   standing skip in its place leaves the totals describing work that
   will never arrive.

   Adopting an existing codebase with no test or gate infrastructure is
   not an excuse to leave the runbook empty: record each gate its blast
   radius calls for as `absent (YYYY-MM-DD) — <reason>`. A blank verification
   runbook is indistinguishable from one nobody checked, so it is not an
   acceptable resting state (the verify rule above).

5. **The three states are honest only if an executed PASS means
   something — the green-lie clause of the rule.** A test command with no
   tests, a linter over an empty set, a type check with everything untyped:
   these "pass" and mean nothing. Do not cite a vacuous pass as
   evidence, and do not make it a gate. Land the real check first (a
   test that asserts, a rule that fires); the gate follows in a later
   increment, by owner decision (`test-first.proportionate-checks`). A
   gate is trusted only once a **planted violation** has turned it red,
   naming the offender, and its removal has turned it green again; that
   demonstration is part of the gate's record. Over high blast-radius
   code it is repeated, once per batch, after a refactor around the
   assertion — a surviving tautology is worse than a deleted check. A
   gate later found to have been incapable of failing did not stop
   working; it never worked, so its greens are retracted
   rather than superseded. Record beside the gate the window in which
   its verdict meant nothing, so the increments it appeared to authorize
   can be re-read. Repairing the wiring without recording the window
   leaves every past pass standing as evidence for a property nobody
   measured.

   The mirror of the vacuous green is the **chronic red**: a gate that
   is always red for a reason unrelated to the property it guards (a
   permission error in its cleanup step, a stale cache, a teardown that
   never succeeds). It is a defect, not noise, because it trains every
   reader to ignore that colour, and the next genuine failure then
   arrives unnoticed. A red that reproduces every time is not flakiness,
   so before calling a red flaky or noise, show that it fails to
   reproduce. And before reading the rest of a run's colours as
   meaningful beside a chronic red, show the runbook entry that names it
   chronically red since a date, for a named reason, with an owner; that
   entry is what keeps the colour's meaning for everything else in the
   run.

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

## Anti-patterns

- "All gates green, but I disabled the flaky one." Either fix the
  flake or document it explicitly; do not silently disable.
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
- "The configuration was passed." Passed is not applied. A suppression
  list, a policy file, or a rules file handed to a tool can be rejected
  on every run while the tool carries on without it, and the record
  says the suppressions took effect. Before recording that an input took
  effect, show that the tool accepted it: a cheap offline check against
  the tool at the version the project pins, one that fails if the tool
  ignores or rejects the input, is that evidence (the inert item
  announcing itself, `method.restrictive-policy` §8). Likewise, before filing
  a non-zero exit as findings from a tool whose exit code means both
  "fatal error" and "findings", show which of the two it was; a wrapper
  that makes the two exit differently answers that on every run, and
  without it a crash reads as a finding.
- "The report was on disk." Was it written *this* run? A step that emits
  per-target artifacts into a persistent or shared output root can read a
  prior run's artifact as the current one's — present, readable, and
  well-formed, yet entirely false. A presence check (exists and non-empty)
  is the tempting fix for a crashed-run zero and silently swaps one false
  green for another. The evidence is that the artifact was observed written
  this run; without that observation the check fails closed and records a
  stale artifact as distinct from a missing one.

## Neighbours

- `protocol.verify-new-gates`: load when marking work closed, or adding
  a new gate.
- `protocol.verify-disagreement`: load when a check and its subject
  disagree, a change must preserve behavior, or a known defect is
  tolerated.
