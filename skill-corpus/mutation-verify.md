# Suggested skill: mutation-verify

> Optional procedure — establish that an assertion actually bites, by naming
> the smallest change that would leave the subject broken while the assertion
> still passes, making that change, and watching the gate. Not a core skill;
> instantiate into `docs/graph/skills/<name>.md` (its home, projected into the
> harness dirs the plant uses) from `templates/skill.template.md` if selected.
> The *doctrine* is already owned and is not restated here:
> `protocols/test-first.md` owns proving an inherited suite by mutation, and
> the two corollaries that decide whether a mutation result may be read at all;
> `protocols/verify.md` owns the planted-violation clause that makes a gate
> trusted. This page is the **operational procedure** neither carries — where
> to cut, what the assertion must watch, how to mutate an artifact the working
> tree must keep, and what a survivor means. It **composes both by reference**.
> Parameterized by `<GATE_COMMAND>`, `<SUBJECT>` (a code path or a
> configuration/data artifact), and `<SCRATCH_LOCATION>`.

## When to apply

- Before citing a green assertion as evidence that a property holds, when
  nobody in this session has watched that assertion fail.
- On an inherited or newly adopted suite, as the adoption-time move
  `protocols/test-first.md` prescribes — this page is the *how* of that move.
- On a checker, linter, or gate you just authored, as the planted violation
  `protocols/verify.md` requires before the gate is trusted.
- After any refactor around an assertion: a tautology that survives a rewrite
  is worse than a deleted check.

## The procedure

### 1. Name the mutation before you make it

Write down, before touching anything: the smallest change to `<SUBJECT>` that
would leave the feature genuinely broken while the assertion still passes, and
which rows of `<GATE_COMMAND>` you expect to go red. This is a prediction, and
it is the part that carries the information — a mutation invented after the
run is scored against whatever happened.

The change must be small and *plausible* — the edit a tired author or a
refactor would actually make: an inverted comparison, a dropped guard, a
loosened membership check, a swapped field, an omitted call. Deleting the whole
function is not a mutation test; it proves the file is loaded, which nobody
doubted.

### 2. Cut at the seam the caller experiences

Mutate the **wiring**, not the helper behind it. A helper that is correct in
isolation and never reached proves nothing about the system, and an assertion
aimed at the helper stays green through every mutation of the wiring that
routes around it. Follow the invocation chain from the caller's entry point to
the point where behavior is decided, and cut there: the registration, the
dispatch, the argument actually passed, the branch actually taken, the
configuration actually read.

If the mutation at the wiring seam survives while the same mutation inside the
helper is killed, you have learned the real result: the suite tests a component
and the system is unguarded.

### 3. Assert at the boundary the claim names

A killed mutant is only as meaningful as the place the assertion watches. Check
that the assertion sits at the boundary its claim actually names, not at a
proxy one step upstream of it: the rendered output rather than the structure the
renderer was handed, the persisted record rather than the object passed to the
writer, the response the client receives rather than the value the handler
returned. An assertion upstream of the boundary is true of a system that never
reaches the boundary at all.

When the mutation is killed by an upstream assertion only, tighten the
assertion to the boundary and re-run the same mutation before recording a kill.

### 4. Mutating an artifact the tree must keep: mutate by copy

When `<SUBJECT>` is a configuration or data artifact rather than code, do not
edit it in place and restore from memory. Build the mutant **outside the
working tree**:

1. Record a checksum of the original artifact.
2. Copy it to `<SCRATCH_LOCATION>` and mutate the copy.
3. Point `<GATE_COMMAND>` at the copy through the input it already accepts —
   a path argument, an environment override, a fixture directory. A gate that
   cannot be aimed at an alternate input is itself the finding: it can only
   ever be run against reality, so it can never be proven.
4. Read the result, then keep the mutant *as a diff* against the original — the
   diff is what the record cites, and it is reviewable without re-running
   anything.
5. Re-checksum the original and confirm it is unchanged.

The tree is never disturbed, so there is no window in which a mutated artifact
can be committed, and no restore step that can be forgotten.

### 5. Read the result honestly

A killed mutant proves the assertion **bites** — it is sensitive to that
specific change. It does not prove the assertion's **unit of comparison** is
the right one: an assertion may be sensitive to the mutation you chose and
blind to the property you care about. Before citing the kill, say what the
assertion compares and why that unit is the contract's unit.

## When the mutant survives: what it usually means

A survivor is a finding about the *instrument* first. Work this list before
concluding the suite has a gap:

- **The assertion compares a description of the thing, not the thing.** A
  name, a label, a declared type, a manifest line, a docstring, a count of
  entries — these all survive a mutation of the content they describe. This is
  the most common survivor and the most expensive, because the assertion reads
  as though it covers the subject.
- **The harness short-circuits, so the survivor was never reached.** A
  per-case harness that stops at the first failing assertion never ran the
  later ones: the mutation may have been killed by an assertion that never
  executed, and the reported count is a lower bound, not a total (the
  lower-bound rule is `protocols/verify.md`'s). Re-run with the earlier
  failure removed before believing the survivor.
- **The mutant never ran.** See the rebuild corollary in
  `protocols/test-first.md` — confirm the artifact under test is the mutated
  one before reading anything into its survival.
- **The cut was behind the seam** (step 2), or **the assertion is upstream of
  the boundary** (step 3). Both produce survivors that say nothing about
  coverage.
- **The gate's subject set was empty.** A glob that matched nothing passes
  every mutation ever made.

Only after all of these are excluded is a survivor a genuine coverage gap — and
then it is a RED waiting to be written, under `protocols/test-first.md`.

## Reporting

State **the mutation you actually made**, not that you mutated. "Inverted the
membership comparison in the request-routing wiring; three rows went red,
naming the contract; reverted, green" is a finding. "Verified by mutation" is
an assertion about your own diligence and carries no information a reader can
check. The record names: the mutation, where it was cut, which rows went red
with their failure text, and — for an artifact mutated by copy — the diff and
the restored checksum.

## Anti-patterns

- Reporting "proven by mutation" without naming the mutation.
- Inventing the mutation after seeing which rows failed.
- A mutation so large that any assertion would catch it — it proves the subject
  is loaded, not that the assertion discriminates.
- Mutating the helper when the caller's seam is the wiring.
- Recording a kill from an assertion that watches a proxy upstream of the
  boundary the claim names.
- Editing a configuration or data artifact in the working tree and restoring it
  by hand.
- Treating a kill as proof that the assertion's unit of comparison is correct.
- Treating a survivor as a coverage gap before excluding the instrument faults
  above.

## Reference files

- `protocols/test-first.md` (owns proving an inherited suite by mutation, and
  the corollaries on rebuild and on exact-membership mutants — this page is the
  operational form of that move and restates none of it)
- `protocols/verify.md` (owns the planted-violation clause that makes a gate
  trusted, the assertion-shape questions, and the lower-bound reporting rule)
- `skills/test-first/SKILL.md` (how to shape the replacement assertion once a
  survivor turns out to be a real gap)
- `core/method/vcs-posture.md` (the tree stays byte-identical to its pin — what
  mutating by copy buys)
- `skill-corpus/prove-red-after-green.md` (the sibling move: when the subject is
  a fix that already landed, park it rather than mutate it)
