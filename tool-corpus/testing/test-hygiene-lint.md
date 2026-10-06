# Tool: test-hygiene-lint

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). This page is a **BLUEPRINT**: no reference
> implementation exists, so the whole page is a blueprint by the corpus README's
> own definition. The four smell definitions and the report-only,
> planted-violation discipline are what a project builds from.

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
flags four smells. The first three inflate a suite past what its actual
coverage warrants; the fourth hides a gate that did not run:

1. **Byte-identical test bodies**, after normalization: a test whose whole
   body, setup included, matches another's proves nothing the other doesn't.
2. **Several tests calling the same expensive helper with the same
   arguments** — the true action is identical across them, and only the
   asserted outcome differs; the fix is one action with several named
   subcases, not one test per outcome.
3. **Expensive per-test setup** — a repository copy, a version-control
   initialization, a full gate or subprocess run — performed inside one
   test's own setup instead of paid once in a shared or module-level
   fixture.
4. **An environment guard that skips instead of failing**: a test that
   checks a precondition the gate host must provide (a container runtime, a
   non-root user, a service it connects to) through an assumption or a skip
   call. When the precondition is missing, the test is reported as skipped,
   and a build with a skipped gate still reads as green.

It is **report-only**. It never deletes, merges, or rewrites a test; it
produces the survey a reviewer or a planned consolidation pass needs before
making that judgment call.

## 2. Interface & invocation

```sh
test-hygiene-lint --suite <path to the test tree or a file glob> \
  [--helper-pattern <name> ...] [--setup-pattern <name> ...] \
  [--guard-pattern <call> ...] [--precondition-pattern <expr> ...]
```

- **Inputs:** the test tree or glob to scan; a **caller-supplied** list of
  helper names or patterns considered "expensive" for smell 2; a
  caller-supplied list of setup operations considered "expensive" for smell
  3 (a repository copy, a version-control init, a full gate run — whatever
  the project itself judges costly). Neither list ships as a baked-in
  default: what counts as expensive is a project fact, not a seed fact. For
  smell 4, a caller-supplied list of the framework's assumption and skip
  calls (`--guard-pattern`) and of the gate-host preconditions they must
  not guard (`--precondition-pattern`: the container-runtime check, the
  user-id check, the connection probe).
- **Outputs:** one finding per smell instance, naming the file, the test
  name(s) involved, and the smell class; a summary count per class.
- **Exit codes:** non-zero when any finding exists, so the lint can gate a
  review step without itself deciding anything; zero on a clean suite. It
  never mutates the suite under any exit path.
- **Preconditions:** the target suite's source is readable. No test in the
  target suite needs to *run* for these four smells to be detected (this
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
default (owned by `skills/test-first/SKILL.md` "Proportionate checks",
linked and not restated here): where that default is a review guideline,
this lint checks it mechanically, over every test in the suite, every run.

### An environment guard that skips instead of failing

An assumption or a skip call is how a test framework says "this test does not
apply here". JUnit's `assumeTrue` aborts the test, and an aborted test is not
a failure; pytest's `skip` and `importorskip` produce a skip outcome; other
frameworks have the same construct. Used on a developer laptop without a
container runtime, that is convenient. Used in a gate, it is a false green:
when the runtime is unreachable for any reason (a stopped daemon, a missing
socket mount, or a client the engine rejects, the case
`library-corpus/maven/testcontainers.md` owns), every guarded test is
skipped, the summary says `Skipped: n`, and the build still succeeds.

Flag each call to a declared guard pattern whose predicate matches a
declared precondition pattern. The fix the finding points at is a guard that
**fails and names the missing precondition** on a gate host, while a
developer run may still skip when the plant decides so (an explicit
environment flag that only gate hosts set, never the reverse).

The user the gate runs as is a precondition too. A test that cannot hold
under root (a file-permission check, which root bypasses) is often guarded
with an assumption on the user id, so a gate that runs as root skips it
silently, and container gates often run as root by default. Run gates as a
non-root user, and make the guard fail under root on a gate host.

Two companions make the smell checkable at run time, outside this source
lint: the gate asserts that its report shows zero skipped tests for the
packages that hold the gates, and a mutation proof removes the precondition
(unset the runtime's address, run as root) and expects the build to go red.

One case is legitimate: an assumption on a precondition the test creates
itself (a fixture file it writes, a directory it makes) guards the test's own
setup, not the gate host. Keep it, and record in the file why it stays, so
the next sweep does not "fix" it.

### Report only, always

This tool never rewrites, merges, or deletes a test on its own authority.
The decision to consolidate belongs to a planned review step
(`protocols/grill.md`'s consolidation-increment discipline, linked and not
restated), and this lint is the mechanical survey that review step runs
against, not a replacement for the judgment about which test should survive.

### The planted-violation self-test

Because no reference implementation exists, the adopting project's own
test-first authoring of this tool must ship with a fixture test suite
carrying a **deliberately planted instance of each of the four smells**.
Without that fixture, "the lint found nothing" and "the lint checked
nothing" are indistinguishable. This is the same self-check-group idiom
`tool-corpus/testing/static-config-contract-gate.md` uses for its own
reader.

## 4. Portable vs blueprint

- **Blueprint (the whole page):** there is no implementation to adopt. The
  parser for a given test framework's syntax — what counts as a test body, a
  named-subcase construct, and a fixture/setup boundary — is written per
  language and per framework, test-first.
- **Durable across every implementation:** the four smell definitions
  exactly as stated above; report-only posture with no mutation on any exit
  path; caller-supplied (never baked-in) lists of expensive helpers and
  expensive setup patterns, and of the guard and precondition patterns smell 4
  matches; the requirement that a fixture suite with a
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
- **A green build with skipped gates.** A Surefire summary of
  `Tests run: n, Failures: 0, Errors: 0, Skipped: k` with `k > 0` in a gate package is a gate that did
  not run. Smell 4 finds the guards in the source; the report check finds
  the skips the source lint cannot see (a guard added by an annotation or a
  build profile).
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
fixture is not; an assumption on a declared gate-host precondition is
flagged, and an assumption on a file the test itself writes is not; a clean
fixture suite containing none of the four smells
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
  "Proportionate checks" owns the review-level default this lint checks
  mechanically; `protocols/grill.md`'s consolidation-increment step owns the
  planned pass this lint's findings feed into. `protocols/verify.md` owns the
  run-time half of smell 4: a step that skipped itself is reported
  `discovered`, never `executed`. `library-corpus/maven/testcontainers.md`
  owns the container-runtime case: fail, not assume, on a host where the
  runtime must exist, and the engine API floor that skips every guarded test
  while the runtime is up.
- **Sources:** distilled from practice; no reference
  implementation exists. Smell 4's framework semantics: the JUnit user guide,
  "Assumptions" (https://docs.junit.org/current/writing-tests/assumptions.html:
  an invalid assumption aborts the test instead of failing it), and the pytest
  guide "How to use skip and xfail to deal with tests that cannot succeed"
  (https://docs.pytest.org/en/stable/how-to/skipping.html).

## 8. Changelog

- 2026-09-26 — created as a blueprint, by docs-librarian. No reference
  implementation exists.
- 2026-09-26 — smell 1 compares the whole normalized body, setup included;
  identifiers are not normalized. The vacuous-pass pitfall names the page
  that owns the empty-census guard.
- 2026-10-05 — added smell 4, the environment guard that skips instead of
  failing (container runtime, non-root user), with its run-time companions and
  the one legitimate case, from practice; by tool-smith.
