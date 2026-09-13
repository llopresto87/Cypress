# Suggested skill: prove-red-after-green

> Optional procedure — recover the missing RED for a fix that landed before its
> test was ever seen failing, by parking the fix on purpose and requiring the
> named rows to fail without it. Not a core skill; instantiate into
> `docs/graph/skills/<name>.md` (its home, projected into the harness dirs the
> plant uses) from `templates/skill.template.md` if selected.
> `protocols/verify.md` states the obligation — a gate whose test never went
> red has authorized nothing, and the runbook entry records the red before the
> green — and delegates the *how* to `protocols/test-first.md`, which carries
> only the **adoption-time** analog: an inherited suite, proven by reintroducing
> a historical defect. This page is the **same-session sibling** of that move,
> for a fix written in this session whose RED nobody watched. It composes both
> by reference and restates neither. Parameterized by `<CONTRACT_FILTER>` (the
> exact selector for the rows that encode the contract), `<PRODUCTION_PATHS>`
> (the non-test paths the fix touched), and `<VCS_PARK_MECHANISM>`.

## When to apply

The RED goes missing in exactly three ways, and each is ordinary rather than
shameful — what is not ordinary is calling the result verified:

- **The implementer overtook the tester.** The fix and its test were written in
  one pass, and the test first ran against code that already worked.
- **The suite was green on arrival.** The rows that encode the contract already
  existed and already passed, so nothing was ever observed to fail.
- **The bug was fixed while writing the reproduction.** Reproducing the defect
  required reading the code closely enough to correct it, and the reproduction
  first ran against the corrected code.

In all three the green run proves the **state of the tree**, not the strength
of the test. Until the procedure below has actually been observed, the
increment's status is **unproven green** — say those words in the handback and
in the runbook entry; do not write PASS.

When the subject is not a parkable fix — an inherited suite, a checker, a
configuration artifact — use `skill-corpus/mutation-verify.md` instead: mutate
what you cannot park.

## The procedure

### 1. Name the rows and the paths, in writing, before running anything

Record two lists first:

- `<CONTRACT_FILTER>` — the selector for the rows that claim the contract, and
  for each row, **the failure it must produce** with the fix removed, in the
  words you expect to see.
- `<PRODUCTION_PATHS>` — the non-test paths the fix touched.

A prediction written after the run is scored against whatever happened.

### 2. Park the production paths only

Put the fix aside with `<VCS_PARK_MECHANISM>`, restricted to
`<PRODUCTION_PATHS>`. Every test file stays in place, untouched.

**Parking a test file proves nothing.** A row that disappears with its file
cannot fail, and a suite that no longer collects the row reports a green that
means only that nobody asked the question. The whole point of the exercise is
to run *this* test against *unfixed* code; removing the test removes the
experiment.

The parking mechanics themselves — record the pin commit, keep the patch
outside the tree, verify the tree afterwards, say where the work went — are
`core/method/vcs-posture.md`'s discipline. Follow it there. What this page adds
is only the selection rule: production paths, never test paths.

### 3. Run the contract filter and read rows, not totals

Run `<CONTRACT_FILTER>` against the parked tree. Read the result **row by
row**, against the predictions from step 1.

A suite in which many rows fail for environment reasons unrelated to the change
— an absent service, a missing runtime, a fixture that needs credentials — is
common and is not a blocker here. The suite total is unreadable in that state
and must not be quoted. The filter's rows are what is read: the question is
whether *these named rows* fail for *this named reason*, and the surrounding
noise is irrelevant to it. Record the environment failures separately as
`discovered` or `absent`, per `protocols/verify.md`.

### 4. An unexpected pass is a finding, and it blocks

Any row that **passes with the fix removed** does not assert what its name
claims. It is green against the defect it is named for, which means it would
have been green against the defect in production. Stop: that row is the defect
now.

Fix the row before restoring — write the assertion that fails against the
parked tree, watch it fail, and only then continue. A row repaired in this
state has had its RED observed by construction, which is the whole objective.
Do not restore first and repair afterwards; the parked tree is the only place
the repair can be proven.

Where the row is green because it watches a proxy rather than the boundary, the
diagnosis and the cut are `skill-corpus/mutation-verify.md`'s.

### 5. Restore, confirm the tree is clean, re-run

Restore the parked patch. **Confirm the tree is clean and byte-identical to the
pin** before reading anything into the next run — an unrestored hunk, a
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

Never report a bare "tests pass". A single green number is exactly what an
assertion-free suite produces, and it is the shape of report this procedure
exists to replace. Until the pair is in the record, the increment is unproven
green and the delivery says so.

## Anti-patterns

- Reporting "tests pass" for a fix whose RED nobody watched.
- Parking a test file — or the whole change — instead of the production paths.
- Predicting the failures after seeing them.
- Quoting the suite total on a suite with unrelated environment failures,
  instead of reading the contract filter's rows.
- Restoring first and repairing a vacuous row afterwards, where its RED can no
  longer be observed.
- Re-running a narrower or wider filter after restoring than the one that
  produced the red.
- Skipping the clean-tree confirmation and reading the restored green as proof.
- Treating a row that passed with the fix removed as good news.

## Reference files

- `protocols/verify.md` (owns the obligation: a gate whose test never went red
  has authorized nothing, and the runbook records the red with its failure text
  before the green; also the three gate states this page's environment failures
  are recorded under)
- `protocols/test-first.md` (owns the cycle this page retrofits, and the
  adoption-time analog — an inherited suite proven by reintroducing a historical
  defect — of which this is the same-session sibling)
- `core/method/vcs-posture.md` (owns the parking discipline: the pin commit, the
  patch outside the tree, the byte-identical check afterwards)
- `skill-corpus/mutation-verify.md` (the move for a subject that cannot be
  parked, and the diagnosis for a row that passes without the fix)
