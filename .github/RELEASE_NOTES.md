## 7.36.0 — a declarative edit is proved by a run, not a new test (2026-09-30)

An owner reported that a plant, asked to add a selector to a pipeline, set
out to write a RED test first. That test could only read back the line it was
testing: red while the line is missing, green once it is there. It proves
nothing the diff does not already show, and it breaks on the next rename.
The rules led the worker there because they said, with no qualifier, that
every production change starts from a failing test. This release adds the
missing qualifier and puts the question where increments are planned.

### What a plant gets

- **A change with nothing to get wrong earns no new test.** Before RED, the
  worker names what a test could catch that the edit being present does not
  already guarantee. For a declarative edit (a selector, a pipeline stage, a
  route, a flag, a config key, a mapping entry, a label) the answer is
  usually nothing. The proof is then the run that shows the edit working: an
  existing test or gate over that surface, or the cheapest real run (a
  dry-run, a validate command, one pipeline run), named with its result in
  the handback. A declaration that holds logic still earns a test: a pattern
  (regex, glob, wildcard), a condition, an order that changes the output, or
  a computed value. The rule lives in `test-first.proportionate-checks`.
- **The planner asks first.** `grill.increment-shape` asks of every
  increment whether it needs a test. A no reads
  `Tests to write (RED): none — <why>; proved by <run>`, and that increment
  gets no RED spawn: the implementer makes the change and runs the named
  proof, and review and commit stand. When the planner cannot tell, the row
  keeps its test and the tester decides at RED, handing back unwritten if
  the answer is no. The grill template shows the form.
- **Spec coverage counts the run.** `spec-lint.py` treats the live contracts
  that such a row names as covered by its run, and says so in its PASS line
  and in `--list`. A row that reads `none — consolidation` covers nothing.
- **The tier does not move.** A config or selector edit still changes
  behavior, so it is T2 or above and keeps its reviewer audit. On the
  contained lane the recorded run takes the place of the pinning test, and
  the why-record names "test or run".

### What changed and why

- The kernel's §3.4 anchor gains one line pointing at the exception, and
  `method.tiers`' contained lane, the test-first rule statement and the
  canonize why-record point at `test-first.proportionate-checks` instead of
  contradicting it.
- The test-first exceptions list replaces "Pure configuration changes" with
  "Declarative edits with nothing to get wrong". The old entry applied only
  where there was no unit-testable behavior, and almost any edit is
  unit-testable in the weak sense, so it never stopped the read-back test.
- The implementer's contained-lane handback and the tester's step 3 name the
  run as the proof for such an edit.

### Decisions and checks

- [ADR-0023](docs/decisions/adr-0023-a-declarative-edit-is-proved-by-a-run.md),
  `proposed`, amends ADR-0006 in part: the contained lane still trades the
  spec for proof plus a why-record, and the proof is now the one the change
  earns. Its named risk is a worker calling logic "declarative" to skip a
  test; the logic list above is the check, and the reviewer audits the
  claim.
- `tests/test-spec-lint.sh` case P1 holds the run-proved coverage and the
  consolidation case.

### How plants pick this up

- **A new plant** gets the rule from `install.sh`.
- **An existing plant** gets it by `graft`. Plans written before it keep
  their test rows and stay valid; the `none — <why>; proved by <run>` form is
  available to new increments. A plant that already recorded a declarative
  edit under the old "Pure configuration" exception needs no change.
