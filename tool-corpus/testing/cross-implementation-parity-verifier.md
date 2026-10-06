# Tool: cross-implementation-parity-verifier

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). This page is a **BLUEPRINT**: the
> corpus-against-executed- reference technique, the fallback-is-a-loud-downgrade
> rule, and the skips-never-count-as-passes discipline are portable; invoking
> each language- or path-specific implementation is written per project.

## 0. Identity

- **Category:** testing
- **Name:** cross-implementation-parity-verifier
- **Language / runtime:** any — it drives each candidate implementation
  through whatever process boundary that implementation runs in
- **Stability:** **blueprint** — no portable implementation, because
  invoking N separately-implemented languages or paths is inherently
  project-specific. The comparison technique is the value of the page.

## 1. What it does

When one rule is implemented more than once — in several languages, several
code paths, or several deployment targets that no single test harness can
see across at once — this feeds a **shared input corpus** to every
implementation and diffs each one's answer against the **executed**
reference implementation, never against a hand-written table of expected
answers.

It generalizes, to any number of candidate implementations, the principle
`tool-corpus/testing/auth-parity-oracle.md` already owns for one domain
(authentication): a hand-written expectation and the implementation under
test were written by the same author, from the same reading of the same
rule, often on the same afternoon, so **two hand-written answers that agree
prove only that one author held one belief twice**. Executing the reference
and reading its real answer is the only comparison that carries information.

## 2. Interface & invocation

```sh
parity-verifier \
  --corpus <shared input corpus> \
  --reference '<command that executes the reference implementation>' \
  --candidate '<command that executes implementation N>' [--candidate ...] \
  [--allow-frozen-fallback]
```

- **Inputs:** a shared input corpus built around **classes** of value the
  rule must agree on (well-formed, malformed, edge, empty or absent,
  structurally-valid-but-semantically-rejected) — not a handful of
  happy-path values; a command that executes the reference implementation on
  one input; one or more commands that execute each candidate
  implementation on the same input.
- **Outputs:** per input, per candidate: the reference's answer, the
  candidate's answer, and a pass/fail; a summary that reports the **skip
  count as its own number**, separate from pass and fail, and marks any
  **load-bearing** corpus case that could not be run as **UNMEASURED** —
  never folded into "passed."
- **Exit codes:** non-zero on any disagreement; non-zero, or a distinct and
  loudly reported code, when the reference could not be executed and the run
  fell back to frozen expectations.
- **Preconditions:** the reference implementation is executable in this
  environment (nothing it needs is down); a candidate's own optional
  dependency is probed before use, never assumed present.

## 3. Approach / algorithm

### Never gate on a hand-written expectation table

The durable core, restated from `auth-parity-oracle.md` for the general
N-way case: a hand-written table of "what the rule should answer for input
X" is the same author's belief written down twice — once as the
implementation, once as the table. Every misreading of the rule is
faithfully reproduced in both, and a test built this way goes green on
exactly the inputs where the belief is wrong.

### Diff against the executed reference, not a description of it

Run the reference implementation for real, on the real corpus, and read its
actual answer. Compare every candidate against that executed answer. When
the reference genuinely cannot be executed in the current environment,
falling back to frozen expectations is allowed only as an **explicit, loud
downgrade** — stated in the run's own output — never as a silent
substitution that reads the same as a live-reference run.

### The corpus is built around classes, not a handful of values

Enumerate the classes of input the rule must handle — not a few strings that
once caused a bug. A parity check is only as strong as the corpus it runs
over; a corpus of happy-path values proves agreement on the cases where
disagreement was least likely.

### Skips never count as passes

Report the skip count as its own number in the summary, and separate it
plainly from the pass count. A corpus case marked **load-bearing** that
could not be run — because a candidate's runtime was unavailable, because a
network dependency was down, whatever the reason — is reported as
**UNMEASURED**, not as passed and not silently dropped from the total. A
summary line that reads "all green" while a load-bearing case never ran is
the exact shape of false assurance this discipline exists to prevent.

## 4. Portable vs blueprint

- **Blueprint (the whole page):** invoking each implementation — its
  calling convention, its process boundary, the exact command that drives
  it on one input — is written per project.
- **Durable across every implementation:** never gate on a hand-written
  expectation table; diff every candidate against the executed reference;
  a frozen-expectation fallback is an explicit, loud downgrade, never silent;
  skips never count as passes, and an unmeasured load-bearing case is
  reported as such; build the corpus around classes of input, not a handful
  of values.

## 5. Pitfalls and sharp edges

- **A "passed" summary that hides a nonzero skip count is a false-green
  risk.** Read the skip line, not the exit code alone — a run can be green
  while most of the cross-implementation evidence was never gathered.
- **Two candidates tested only against each other, with no executed
  reference, can agree while both are wrong.** That is agreement, not
  parity, and reporting it as parity overstates what was measured.
- **A frozen-expectation fallback that produces the same summary shape as a
  live-reference run hides which check ran.** Give the fallback its
  own, visibly different summary line.
- **A reference invoked through a stubbed or mocked entry point is not the
  reference.** Strip it to whatever offline configuration lets it run
  without a live dependency, exactly as `auth-parity-oracle.md` strips an
  authenticator to its offline form — but never touch the decision logic
  itself, or the "reference" becomes another hand-written expectation
  wearing a costume.
- **Matching on outcome alone, when the rule has a richer answer shape,
  under-reports disagreement.** Compare the full answer each implementation
  returns, not a coarsened pass/fail projection of it, unless the rule
  itself is genuinely binary.

## 6. Tests that cover it

Cover: a candidate that disagrees with the executed reference on one corpus
class fails and names the class and both answers; a candidate that agrees on
every corpus item passes; making the reference deliberately unreachable
triggers the frozen-expectation fallback and the run's own output states
that the fallback was used; a corpus case marked load-bearing that could not
be executed is reported as UNMEASURED, never as passed, and the exit code
reflects it; the skip count printed in the summary matches the actual number
of skipped cases; a reference stubbed to a fixed answer is detected as a
false oracle by a known-disagreement fixture case built for that purpose.

- **How to run the tests:** `<the plant's test command for its implementation>`

## 7. References & neighbours

- **Related tools:** `tool-corpus/testing/auth-parity-oracle.md` (owns the
  one-directional parity principle for one domain — authentication — between
  a guard and its downstream oracle; this page generalizes the
  corpus-against-executed-reference half of that principle to full agreement
  across any number of candidate implementations, and adds the skip-
  accounting discipline that a single-oracle check does not need).
- **Sources:** distilled from practice; no external URL.

## 8. Changelog

- 2026-09-26 — created by
  docs-librarian.
