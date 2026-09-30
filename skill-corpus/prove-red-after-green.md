# Suggested skill: prove-red-after-green

> Optional procedure: recover the missing RED for a fix that landed before its
> test was ever seen failing, by parking the fix on purpose and requiring the
> named rows to fail without it. `protocols/verify.md` states the obligation
> (a gate whose test never went red has authorized nothing, and the runbook
> entry records the red before the green) and delegates the *how* to
> `protocols/test-first.md`, which carries only the **adoption-time** analog:
> an inherited suite, proven by reintroducing a historical defect. This page is
> the **same-session sibling** of that move, for a fix written in this session
> whose RED nobody watched. It composes both by reference. Parameterized by
> `<CONTRACT_FILTER>` (the exact selector for the rows that encode the
> contract), `<PRODUCTION_PATHS>` (the non-test paths the fix touched), and
> `<VCS_PARK_MECHANISM>`.

## When to apply

The RED goes missing in exactly three ways, and each is ordinary rather than
shameful. What is not ordinary is calling the result verified:

- **The implementer overtook the tester.** The RED and the GREEN that
  implements it ran side by side, or the fix and its test were written in one
  pass, and the test first ran against code that already worked.
- **The suite was green on arrival.** The rows that encode the contract already
  existed and already passed, so nothing was ever observed to fail.
- **The bug was fixed while writing the reproduction.** Reproducing the defect
  required reading the code closely enough to correct it, and the reproduction
  first ran against the corrected code.

In all three the green run proves the **state of the tree**, not the strength
of the test. Until the procedure below has actually been observed, the
increment's status is **unproven green**: write those words in the handback and
in the runbook entry, in place of PASS.

The moments to catch it are the ones where a green is about to be spent: a
handback reports GREEN and names no observed RED; the tests for a
characterization passed on their first run; a spec §10 row is about to move
from `red` to `green` on the strength of one run.

The first cause is the preventable one: `protocols/test-first.md`'s cycle table
has each phase wait for the handback it needs. This page is for when that order
was broken anyway.

When the subject is not a parkable fix (an inherited suite, a checker, a
configuration artifact), use `skill-corpus/mutation-verify.md` instead: mutate
what you cannot park.

## The procedure

### 1. Name the rows and the paths, in writing, before running anything

Record two lists first:

- `<CONTRACT_FILTER>`: the selector for the rows that claim the contract, and
  for each row, **the failure it must produce** with the fix removed, in the
  words you expect to see.
- `<PRODUCTION_PATHS>`: the non-test paths the fix touched.

A prediction written after the run is scored against whatever happened, and a
failure reasoned about rather than observed ("it would obviously have thrown")
is still only a prediction; this procedure turns it into a result.

### 2. Park the production paths only

Put the fix aside with `<VCS_PARK_MECHANISM>`, restricted to
`<PRODUCTION_PATHS>`. Every test file stays in place, untouched. Before
running, confirm the test files are still present and still hold their new
content; a park that caught one by accident is found here or not at all.

**Parking a test file proves nothing.** A row that disappears with its file
cannot fail, and a suite that no longer collects the row reports a green that
means only that nobody asked the question. The whole point of the exercise is
to run *this* test against *unfixed* code; removing the test removes the
experiment.

The parking mechanics themselves (record the pin commit, keep the patch
outside the tree, verify the tree afterwards, say where the work went) are
`core/method/vcs-posture.md`'s discipline. Follow it there.

**When the fix is already committed**, the working tree holds nothing to park.
The state the RED should have run against is the last commit before the fix
with the new tests copied in: pre-fix production code, post-fix tests. Build
that state inside the one working tree (`core/method/vcs-posture.md` §3): a
second tree can skip, cache or resolve differently, so a RED observed there and
a GREEN observed here are two questions asked of two environments, not a pair.
Start from a clean tree at the pin (the current commit, recorded), then undo
only the fix's own changes to `<PRODUCTION_PATHS>`, which means reversing the
fix's diff restricted to those paths. Reverting the whole fix commit takes the
tests with it and is harder to restore exactly; rolling the paths back
wholesale to an older revision also undoes any later commit that touched them,
and the measurement then covers changes it was never meant to. The test files
stay exactly as the pin has them.

### 3. Run the contract filter and read rows, not totals

Run `<CONTRACT_FILTER>` against the parked tree. Read the result **row by
row**, against the predictions from step 1.

A suite in which many rows fail for environment reasons unrelated to the change
(an absent service, a missing runtime, a fixture that needs credentials) is
common and does not block this procedure; the suite total is unreadable in that
state, so the record quotes only the filter's rows: the question is
whether *these named rows* fail for *this named reason*, and the surrounding
noise is irrelevant to it. Record the environment failures separately as
`discovered` or `absent`, per `protocols/verify.md`.

### 4. An unexpected pass is a finding, and it blocks

Any row that **passes with the fix removed** does not assert what its name
claims. It is green against the defect it is named for, which means it would
have been green against the defect in production. Stop: that row is the defect
now.

Fix the row before restoring, because the parked tree is the only place the
repair can be proven: write the assertion that fails against the parked tree,
watch it fail, and only then continue. A row repaired in this state has had its
RED observed by construction, which is the whole objective.

Where the row is green because it watches a proxy rather than the boundary, the
diagnosis and the cut are `skill-corpus/mutation-verify.md`'s.

### 5. Restore, confirm the tree is clean, re-run

Restore the parked patch; for a committed fix, return `<PRODUCTION_PATHS>` to
the pin. **Confirm the tree is clean and byte-identical to the
pin** before reading anything into the next run. An unrestored hunk, a
conflict resolved by hand, or a stray edit makes the green that follows a
statement about a tree nobody has seen. Then re-run the **same**
`<CONTRACT_FILTER>`, unchanged: every named row green.

Re-running a *different* filter than the one that produced the red breaks the
pair; the two runs must be the same question asked of two trees.

### 6. Report the pair

The record is two numbers and the tree each belongs to:

```
- Contract rows, fix parked:   <N> failed (<filter>) — <the expected failure text>
- Contract rows, fix restored: <N> passed (<filter>) — tree clean at <pin>
```

The pair replaces a bare "tests pass", because a single green number is exactly
what an assertion-free suite produces. Until the pair is in the record, the
increment is unproven green and the delivery says so.

The pair proves the test. It does not turn the increment into one that followed
the cycle. The record says the RED was recovered after the GREEN, and why it
went missing, so the departure from `protocols/test-first.md` stays visible.

## Reference files

- `protocols/verify.md` (owns the obligation: a gate whose test never went red
  has authorized nothing, and the runbook records the red with its failure text
  before the green; also the three gate states this page's environment failures
  are recorded under)
- `protocols/test-first.md` (owns the cycle this page retrofits, including the
  spawn order that keeps a RED from running beside its GREEN, and the
  adoption-time analog, an inherited suite proven by reintroducing a historical
  defect, of which this is the same-session sibling)
- `core/method/vcs-posture.md` (owns the parking discipline: the pin commit, the
  patch outside the tree, the byte-identical check afterwards; and the one
  working tree, which is why a committed fix is un-applied in place rather than
  re-checked-out elsewhere)
- `skill-corpus/mutation-verify.md` (the move for a subject that cannot be
  parked, and the diagnosis for a row that passes without the fix)
