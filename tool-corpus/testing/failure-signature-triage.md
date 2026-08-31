# Tool: failure-signature-triage

> Project-agnostic, durable capability notes, folded into the seed by the
> harvest protocol. Orientation for a reusable tool — the signature model and
> both operations over it are portable; only the structured-result parser is
> bound to the test framework in use.

## 0. Identity

- **Category:** testing
- **Name:** failure-signature-triage
- **Language / runtime:** any (illustrated in bash with `sort`/`comm`); needs
  only a reader for the runner's structured result file
- **Stability:** **portable** — the signature model, the cross-run
  set-difference, and the single-run bucketing are language- and
  framework-neutral; the parser that turns a result file into failure records is
  the one framework-specific part

## 1. What it does

Tells a **genuine regression** apart from a suite's **standing flake
population**, by comparing runs on a **failure signature** instead of a test
name.

In a suite with a large known-nondeterministic failing set, "test X failed" is
almost information-free: X is on the flaky list, it fails sometimes, and the
name alone cannot say whether *this* failure is the usual one or something new
wearing the same name. The signature carries that information: two failures of
the same test that differ in exception type, in message class, or in where they
died are **different failures**, and one of them may be new.

The tool exists so that "did anything new break in this run?" is answered
**mechanically** — by a set operation over signatures — rather than by a human
re-reading a wall of red.

## 2. Interface & invocation

One test-results file in, signatures or a bucketed report out:

```sh
signatures.sh <results-file>     # op 1: one TSV signature line per failure, sorted
triage.sh     <results-file>     # op 2: known-flake bucket + verbatim residual
```

- **Inputs:** a single **structured** test-result artifact — whatever
  machine-readable report the runner emits (an XML or JSON result file), which
  is the parser target. No flags are needed for the basic reducer: a results
  file is the whole interface.
- **Outputs:**
  - op 1 — **TSV signature lines** on stdout, one per failed test, deduplicated
    and sorted under a pinned collation, so the output of two runs can be fed
    straight into a set-difference.
  - op 2 — a **bucketed text report**: a compact list of failures matched as
    known flakes, and every unmatched failure printed **verbatim**.
- **Preconditions:** the run emitted its structured result file (see the
  authoritative-artifact pitfall in §5); a parser for that format.

## 3. Approach / algorithm

### The signature (the shared core)

For each **failed** test, reduce the failure to a tuple:

```
exception type  ×  failure "kind"  ×  first non-framework stack frame (with line)
```

- **Exception type** — the thrown/asserted type as the runner reports it.
- **Failure "kind"** — a **windowed literal-pattern classification** of the
  failure message: match a fixed, ordered list of literal substrings against a
  bounded prefix of the message and emit the first hit's label, `other`
  otherwise. The window matters — the tail of a failure message carries ids,
  timings, paths, and diffs that vary run to run, and letting them into the
  classification makes every occurrence look unique.
- **First non-framework stack frame, with line number** — walk the stack from
  the top and take the first frame that is not the test framework, the assertion
  library, or the runner. The line number is part of the signature: the same
  frame failing at a different line is a different failure.

That tuple is the whole model. Both operations are just different reductions
over it.

### Operation 1 — cross-run set-difference

Reduce a run to a **minimal, sortable signature set**: one line per failure,
tab-separated, deduplicated, sorted under a **pinned collation**. "Is anything
in this run new relative to N baseline runs?" then becomes a set difference:

```sh
signatures.sh new-run.xml            | LC_ALL=C sort -u > new.tsv
for f in baseline/*.xml; do signatures.sh "$f"; done \
                                     | LC_ALL=C sort -u > baseline.tsv
LC_ALL=C comm -23 new.tsv baseline.tsv    # signatures ONLY in the new run
```

An empty difference is a mechanical statement — *this run produced no failure
shape the baseline runs have not already produced* — not a judgment call. A
non-empty difference is a short, exact list to look at.

The baseline is a **union over N runs**, not one run: a flake population is only
characterized by repeated sampling, and a single baseline run makes every
unsampled flake look new.

### Operation 2 — single-run asymmetric triage

Bucket **one** run's failures into two piles:

- **Known flake** — matched by a **calibrated, conjunctive predicate**: every
  condition must hold (exception type **and** kind **and** frame, plus whatever
  else the calibration required). Conjunctive is the point. A predicate loosened
  to "any of these matches" swallows genuine failures that merely resemble a
  flake.
- **Everything else** — the **residual**, printed **verbatim**, one failure at a
  time, with its message and stack, and **never summarized into a count**.

The asymmetry is deliberate. The known bucket can be compressed to a tally
because it is, by construction, the part already understood. The residual is
exactly the bucket that can hide a real regression, so it gets the expensive
treatment: full text, individually, every time. A residual reduced to "3 other
failures" is a triage tool that has quietly stopped triaging.

```sh
# shape of the predicate — every clause must hold (never `||`)
is_known_flake() {                       # exc, kind, frame from the signature
  [ "$exc"   = "<calibrated type>"  ] &&
  [ "$kind"  = "<calibrated kind>"  ] &&
  [ "$frame" = "<calibrated frame>" ]
}
```

## 4. Portable vs blueprint

- **Portable (use as-is):** the signature tuple; the windowed literal
  classification; the "first non-framework frame, with line" rule; the
  reduce-to-sorted-unique-TSV shape; the `comm` set-difference over a
  union-of-N baseline; the conjunctive predicate; the verbatim residual.
- **Framework-specific (fill in):** the **parser** — how failed tests, their
  exception type, message, and stack are read out of the runner's structured
  report; and the frame-prefix list that says which frames are "framework".
- **Per-suite (calibrate):** the literal-pattern list behind `kind`, and the
  clauses of the known-flake predicate (see §5, calibration).

Portable skeleton (the parser is the one stub):

```bash
#!/usr/bin/env bash
set -uo pipefail
WINDOW=120                                  # bytes of message used to classify

classify() {                                # windowed literal-pattern match
  local msg="${1:0:$WINDOW}"
  case "$msg" in
    *"<literal A>"*) echo "kind-a" ;;
    *"<literal B>"*) echo "kind-b" ;;
    *)               echo "other"  ;;
  esac
}

first_app_frame() {                         # first frame that is not framework
  while IFS= read -r frame; do
    case "$frame" in
      *"<framework prefix>"*|*"<assert lib prefix>"*|*"<runner prefix>"*) continue ;;
      *) printf '%s\n' "$frame"; return ;;
    esac
  done <<< "$1"
  echo "<no-app-frame>"
}

# parse_failures: FRAMEWORK-SPECIFIC. Emit one TSV record per FAILED test:
#   test <TAB> exception-type <TAB> message <TAB> stack(newline-separated)
parse_failures "${1:?results file}" |
while IFS=$'\t' read -r test exc msg stack; do
  printf '%s\t%s\t%s\n' "$exc" "$(classify "$msg")" \
                        "$(first_app_frame "$(printf '%b' "$stack")")"
done | LC_ALL=C sort -u                     # sorted output is part of the contract
```

## 5. Pitfalls and sharp edges

- **Set-difference on unsorted input fails silently wrong.** `comm` (and every
  equivalent) assumes both sides are sorted under the **same** collation; given
  unsorted input it does not error, it reports a confidently wrong difference —
  missing new signatures and inventing others. Always sort **both** sides with a
  **pinned collation** (`LC_ALL=C sort`) immediately before diffing, and make
  sorted output part of the reducer's contract so a caller cannot forget. Locale
  differences between two machines are the same bug wearing a different hat.
- **A 100%-consistent failure is permanently invisible.** Signature matching
  answers "is this new?", and a test that fails **identically in every run** is
  maximally matched — it is in the baseline of every comparison and in the known
  bucket of every triage, forever. This is a **structural** blind spot, not a
  tuning problem. Pair this technique with a **companion check**: look for tests
  that fail identically across N runs and have **never once reached their own
  assertions** (dead before the test body's first assertion — a broken fixture,
  a missing dependency, a setup throw). That is a different, complementary
  check; signature matching does not and cannot solve it.
- **An uncalibrated classifier must not gate anything.** Before the bucketing
  predicate is allowed to decide whether a run is clean, run it against runs
  whose bucket counts are **already known by hand** and confirm it reproduces
  those known-correct counts **exactly**. A predicate that is close but not
  exact is worse than none: it produces a green result with a specific,
  invisible false-negative rate.
- **Read the authoritative structured artifact, never the convenience log.**
  When a run emits both a machine-readable result file and a free-text console
  log, the structured file is the **complete and authoritative** record; the
  log's completeness varies — sometimes by orders of magnitude — between
  otherwise-identical runs, because of truncation, buffering, verbosity
  settings, and interleaving. A signature built from a truncated log silently
  degrades: missing stacks collapse to the same frame, and distinct failures
  merge into one signature.
- **Summarizing the residual defeats the tool.** The moment the unmatched bucket
  is rendered as a count instead of full text, the one bucket that can contain a
  regression becomes the one bucket nobody reads.

## 6. Tests that cover it

Cover: two runs with the same failing **test names** but different exception
type / kind / frame produce **different** signatures (and therefore a non-empty
difference); identical failures produce an empty difference; the reducer's
output is sorted and deduplicated under the pinned collation even when the
parser emits records out of order; the known-flake predicate reproduces
**hand-counted** bucket counts on calibration fixtures exactly; a failure
matching some-but-not-all predicate clauses lands in the **residual**; residual
output contains each unmatched failure's full text.

- **How to run the tests:** `<the plant's test command for its implementation>`

## 7. References & neighbours

- **Related tools:** `tool-corpus/testing/ci-runner-local-simulator.md`
  (reproduces the runs this consumes locally, so N baseline runs are cheap);
  `tool-corpus/testing/http-smoke-suite.md` (the same "assert the mechanical
  fact, don't eyeball the output" posture at the protocol level).
- **Sources:** distilled from harvested plant experience; no external URL.

## 8. Changelog

- 2026-08-05 — created from harvested, generalized capability (three donor
  scripts sharing one signature core, consolidated into one page), by
  docs-librarian.
