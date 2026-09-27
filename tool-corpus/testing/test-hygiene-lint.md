# Tool: test-hygiene-lint

> Project-agnostic, durable capability notes, folded into the seed by the
> harvest protocol. This page is a **BLUEPRINT**: no reference
> implementation exists, so the whole page is a blueprint by the corpus
> README's own definition. The three
> smell definitions and the report-only, planted-violation discipline are
> what a project builds from.

## 0. Identity

- **Category:** testing
- **Name:** test-hygiene-lint
- **Language / runtime:** any (a parser for the target test framework's own
  syntax — recognizing a test body, a named-subcase construct, and a
  fixture/setup boundary)
- **Stability:** **blueprint**: there is no implementation anywhere to
  adopt. The smell definitions, the report-only posture, and the
  planted-violation self-test are the value of the page; everything else is
  written fresh, per language and per test framework, test-first.

## 1. What it does

A lint over a test suite's **source**, never its runtime behavior, that
flags three smells known to inflate a suite past what its actual coverage
warrants:

1. **Byte-identical test bodies**, after normalization — a test whose whole
   body, setup included, matches another's proves nothing the other doesn't.
2. **Several tests calling the same expensive helper with the same
   arguments** — the true action is identical across them, and only the
   asserted outcome differs; the fix is one action with several named
   subcases, not one test per outcome.
3. **Expensive per-test setup** — a repository copy, a version-control
   initialization, a full gate or subprocess run — performed inside one
   test's own setup instead of paid once in a shared or module-level
   fixture.

It is **report-only**. It never deletes, merges, or rewrites a test; it
produces the survey a reviewer or a planned consolidation pass needs before
making that judgment call.

## 2. Interface & invocation

```sh
test-hygiene-lint --suite <path to the test tree or a file glob> \
  [--helper-pattern <name> ...] [--setup-pattern <name> ...]
```

- **Inputs:** the test tree or glob to scan; a **caller-supplied** list of
  helper names or patterns considered "expensive" for smell 2; a
  caller-supplied list of setup operations considered "expensive" for smell
  3 (a repository copy, a version-control init, a full gate run — whatever
  the project itself judges costly). Neither list ships as a baked-in
  default: what counts as expensive is a project fact, not a seed fact.
- **Outputs:** one finding per smell instance, naming the file, the test
  name(s) involved, and the smell class; a summary count per class.
- **Exit codes:** non-zero when any finding exists, so the lint can gate a
  review step without itself deciding anything; zero on a clean suite. It
  never mutates the suite under any exit path.
- **Preconditions:** the target suite's source is readable. No test in the
  target suite needs to *run* for these three smells to be detected (this
  is a source-level lint), except the lint's own self-test, which does run.

## 3. Approach / algorithm

### Byte-identical bodies, after normalization

Normalize each test's **whole** body, together with the setup it runs (its
own per-test or per-class setup hook), and compare the normalized forms across
the suite. Flag any pair that matches. Two tests that share an assertion but
build different preconditions are different tests, so the setup is part of
what is compared. The same comparison applies one level up: a test class
whose normalized setup and methods match another class's is a duplicate
class.

Normalization strips comments and blank lines and collapses whitespace to one
canonical form. It does **not** rename identifiers. A body that differs only
by a renamed local variable is a near-duplicate, not a byte-identical one, and
this smell does not report it. A project that wants near-duplicates too must
define identifier normalization explicitly (which names are canonicalized,
and in what order) and test it as a separate mode.

### Same expensive helper, same arguments

Parse each test's calls to the caller-declared "expensive helper" names.
Flag any group of tests that call the same helper with the **same argument
values**. Same helper, *different* arguments is not this smell; the tests
are doing different work and matching on helper name alone over-reports.
Where the smell is real, the fix is one action performed once, with the
several outcomes asserted under their own named subcases: the setup is
shared, and each outcome is still asserted and reported by name.

### Expensive per-test setup

Flag a test whose **own** setup — not a shared or module-level fixture —
performs a caller-declared expensive operation: a repository copy, a
version-control initialization, a full gate or subprocess run. This is the
setup-cost half of the "one action, many named subcases, shared fixture"
default (owned by `skills/test-first/SKILL.md` "Keeping the suite lean",
linked and not restated here): where that default is a review guideline,
this lint checks it mechanically, over every test in the suite, every run.

### Report only, always

This tool never rewrites, merges, or deletes a test on its own authority.
The decision to consolidate belongs to a planned review step
(`protocols/grill.md`'s consolidation-increment discipline, linked and not
restated), and this lint is the mechanical survey that review step runs
against, not a replacement for the judgment about which test should survive.

### The planted-violation self-test

Because no reference implementation exists, the adopting project's own
test-first authoring of this tool must ship with a fixture test suite
carrying a **deliberately planted instance of each of the three smells**.
Without that fixture, "the lint found nothing" and "the lint checked
nothing" are indistinguishable. This is the same self-check-group idiom
`tool-corpus/testing/static-config-contract-gate.md` uses for its own
reader.

## 4. Portable vs blueprint

- **Blueprint (the whole page):** there is no implementation to adopt. The
  parser for a given test framework's syntax — what counts as a test body, a
  named-subcase construct, and a fixture/setup boundary — is written per
  language and per framework, test-first.
- **Durable across every implementation:** the three smell definitions
  exactly as stated above; report-only posture with no mutation on any exit
  path; caller-supplied (never baked-in) lists of expensive helpers and
  expensive setup patterns; the requirement that a fixture suite with a
  deliberately planted instance of each smell ships alongside the lint.

## 5. Pitfalls and sharp edges

- **Comparing only the assertion over-reports.** Two tests with the same
  assertion but different setup are not the same test. Smell 1 compares the
  whole normalized body, setup included.
- **Normalizing identifiers silently widens smell 1.** Once renamed variables
  count as equal, the lint reports near-duplicates under a byte-identical
  label. Leave identifiers alone unless the project defines that
  normalization and names it as its own mode.
- **A baked-in "expensive" list ages badly.** A helper cheap today can
  become expensive after a refactor, and the reverse. Keep both lists
  caller-supplied and reviewed periodically, never shipped as a seed
  default; this is a project fact, not a portable one.
- **Same helper, different arguments is not smell 2.** Matching on helper
  name alone, without comparing arguments, flags tests that are legitimately
  doing different work.
- **Treating the lint's own exit code as sufficient authorization to
  auto-delete a test defeats the discipline it exists to support.** The
  consolidation decision is planned and reviewed, never automatic; this
  lint produces the survey, not the ruling.
- **A "clean" run with an empty or near-empty selector is a vacuous pass,
  not a clean one.** Confirm the suite glob matched a meaningful number of
  tests before trusting a zero-finding result. The same guard, a hard
  failure on an empty census, is `tool-corpus/ops/layered-config-merge-verifier.md`
  "False-green guard".

## 6. Tests that cover it

Cover: a fixture suite with two test bodies that are byte-identical after
comment and whitespace normalization, setup included, is flagged; a pair with
the same assertion but different setup is not; a body that differs only by a
renamed local variable is not flagged (identifiers are not normalized); a
body with a genuinely different assertion is not; two tests calling the same declared expensive helper with
the same arguments are reported as one group, and two tests calling it with
different arguments are not; a test performing its own repository-copy,
version-control-init, or full-gate-run setup outside any shared fixture is
flagged, and the same operation performed once in a shared or module-level
fixture is not; a clean fixture suite containing none of the three smells
produces zero findings, proving the lint discriminates instead of flagging
everything; the lint never writes to, merges, or deletes any file in the
suite it scans, on any exit path; the planted-violation fixture itself is
part of the test suite, so "found nothing" can never mean "checked nothing."

- **How to run the tests:** `<the plant's test command for its implementation>`

## 7. References & neighbours

- **Related tools:** `tool-corpus/testing/static-config-contract-gate.md`
  (the self-check-group idiom this page's planted-violation self-test
  instantiates: proving a reader saw something, not merely that it ran).
- **Procedure:** `skill-corpus/mutation-verify.md` (the general
  planted-violation discipline that makes any gate trusted; linked, not
  restated).
- **Doctrine home (linked, not restated):** `skills/test-first/SKILL.md`
  "Keeping the suite lean" owns the review-level default this lint checks
  mechanically; `protocols/grill.md`'s consolidation-increment step owns the
  planned pass this lint's findings feed into.
- **Sources:** distilled from harvested plant experience; no reference
  implementation exists, and no external URL.

## 8. Changelog

- 2026-09-26 — created as a blueprint, by docs-librarian. No reference
  implementation exists.
- 2026-09-26 — smell 1 compares the whole normalized body, setup included;
  identifiers are not normalized. The vacuous-pass pitfall names the page
  that owns the empty-census guard.
