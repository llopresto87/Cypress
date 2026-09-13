# Suggested skill: operator-compressed-fix-path

> Optional procedure — the disciplined form of a **compressed-ceremony** fix:
> the owner, in words, opens a path that reduces *who is involved* and *how much
> process wraps the change*, for a defect whose root cause is already known and
> whose diff is small. Not a core skill; instantiate into
> `docs/graph/skills/<name>.md` (its home, projected into the harness dirs the
> plant uses) from `templates/skill.template.md` if selected. Two neighbours
> already own most of the rules and are **cited, never re-derived**:
> `core/method/tiers.md` owns the contained lane's eligibility edges and the
> rule that the tier never moves to match a shortcut; `core/method/vcs-posture.md`
> owns the local commit as the resting state of work and publishing as a
> separate authorization. What this page owns is only three things: the
> **owner-opened authorization**, the **disclosed sibling sweep**, and the
> **temporary causality test whose removal is recorded as a debt**.
> Parameterized by `<BUILD_COMMAND>` and `<OWNER_INVOCATION>` — the words that
> opened the path.

## When to apply

Only when the owner has opened the path. This is the first and least negotiable
condition: the compression is an **authorization**, granted per invocation, in
the conversation, in words. It is never inferred from urgency, never carried
over from the last time it was granted, never implied by the smallness of the
diff, and never read into "just fix it" or "go ahead". Absent the words, the
change takes the ordinary path for its tier.

Record `<OWNER_INVOCATION>` verbatim in the why-record. A compression nobody can
point at later is indistinguishable from process that was skipped quietly.

## What is compressed and what is not

The path reduces the number of people and spawns involved and the ceremony
around the change. It does **not** reduce:

- the risk classification — the tier is what the change's surface makes it, and
  it does not move because the ceremony did (`tiers.hard-edges`);
- the build — `<BUILD_COMMAND>` runs, and the gates the change's blast radius
  earns run with it (`protocols/verify.md` owns that depth, and it follows the
  radius, never the lane);
- the causal proof — see below;
- the honesty of the record — the why-record still lands
  (`protocols/canonize.md`).

**One fix, one branch, one commit** — stacked on the previous fix's branch when
the fixes are sequential, so each remains revertible on its own. That shape is
what keeps the compressed path reversible: the ceremony was reduced, the ability
to undo one change without undoing its neighbours was not.

The message is plain and factual in three beats: **what broke, the production
signature it broke with, and what changed.** The signature is the beat people
drop, and it is the one that lets the next reader match a recurrence to this fix
without re-deriving the diagnosis.

Where the work rests afterwards is unchanged: a local commit is the resting
state, and publishing it is a separate authorization the compression did not
grant (`core/method/vcs-posture.md`). "Fix it quickly" is not a push.

## The four gates

All four must hold. Two are the contained lane's eligibility edges read
forward, and are `tiers.contained-lane`'s — read them there, in full, before
using this page; the other two are this path's own.

1. **Root cause established.** Not suspected, not narrowed to a file — known,
   and statable in one sentence that explains every observed symptom. A fix
   aimed at a symptom is a guess, and a guess is exactly what the compressed
   path has no capacity to catch.
2. **Diff small and local**, on one surface, reversible — `tiers.contained-lane`.
3. **No new dependency, contract, or persisted format** — `tiers.contained-lane`.
4. **Result self-verifiable.** The correctness of the change can be established
   by this session, now, with `<BUILD_COMMAND>` and the gates available to it.
   If confirming the fix requires another actor, another environment, or a
   judgment this session cannot make, the path is closed.

**Any doubt escalates back to the full path.** Unanimity is the rule: a gate you
are unsure of is a gate that does not hold. Escalating mid-change is the
expected outcome sometimes — say so and re-route; it costs a message.

## The procedure

### 1. Read the whole surrounding unit before editing the line

Read the entire function, class, module, or configuration block the line lives
in — not the line and its two neighbours. The compressed path removes the
independent reader who would otherwise notice that the line is correct and its
caller is not; reading the whole unit is what replaces that reader. A fix made
through a keyhole is how a small diff becomes a new defect.

### 2. Make the smallest change, integrated into the file's existing shape

Minimum is about behavior, not diff size. The edit takes the form the file
already uses — its naming, its error handling, its layering — so the result
reads as though the defect had never been there. A special case bolted beside
the code that should itself have changed is not a small fix; it is a second
shape to maintain (`skills/holistic-editing/SKILL.md`).

### 3. Sweep identical-shape siblings — and say so

When the same defect shape appears elsewhere in the surface you are already in,
fix those occurrences in the same pass. Then **disclose every one of them**:
enumerate the siblings by location in the report and in the why-record, and say
they were not part of what the owner asked for.

An undisclosed preemptive fix is **undisclosed scope**, even when it is good
engineering and even when every occurrence was genuinely the same shape. The
owner authorized a compression of ceremony over a change they had in mind; a
diff larger than that change, unannounced, spends the compression on something
they never saw. Disclosure costs one sentence and keeps the path usable next
time.

**The smallest correct change is only correct against the shapes you actually
measured.** A guard written for the one malformed value in front of you is not a
guard for the class: an upstream that sends a null may also send an empty
string, a blank one, and the literal word for null. Enumerate the shapes the
producer can emit before deciding the diff is small — the compressed path is for
a fix whose root cause is *understood*, and a shape you have not measured is a
root cause you have not finished understanding.

A related failure has nothing to do with correctness. **A small fix kept local
is a small fix nobody can build on.** A compressed path that ends in an
unpublished commit leaves the defect live everywhere but one working tree, and
the next person fixes it again — usually wider, because they measured more
shapes than you did. Publishing is a separate authorization
(`core/method/vcs-posture.md`), so the obligation here is to *ask for it*, not
to assume it: a fix parked indefinitely is an outcome to report, not a
resting state.

A sibling that is *similar* rather than identical in shape is not swept: it is
named as a finding and left for its own decision.

### 4. Prove causality when it is not self-evident

Gate 1 says the root cause is established. When the link between the change and
the symptom is self-evident on reading the diff, that is the proof. When it is
not:

1. Write a temporary test that fails on the defect and passes with the fix.
2. **Watch it fail with the fix removed** — park the production paths, observe
   the named failure, restore, observe the green
   (`skill-corpus/prove-red-after-green.md` owns that sequence).
3. Only then is causality proven. A test that has only ever been green proves
   the state of the tree.

The test may be discarded **only on the owner's instruction**, and discarding it
is not free: the coverage gap it leaves is recorded as a **debt** in the
why-record and the plan-of-record — what the test asserted, why it was
discarded, and what would have to be true to close the gap
(`protocols/canonize.md`). A temporary test deleted silently converts a proven
fix into an unproven one at the moment the record is written.

### 5. Say what ceremony was skipped

The delivery names the compression explicitly: the owner's words, which steps
were not taken (which spawns, which reviews, which pass), what ran anyway
(`<BUILD_COMMAND>` and the gates), the swept siblings, and any discarded test
with its debt. The tier is stated as the change's surface makes it.

Never reclassify the risk tier downward to make the record consistent with the
shortcut. The compression is a fact about process; the tier is a fact about the
change; a record that quietly aligns the second to the first is the one artifact
that makes the whole path untrustworthy.

## Anti-patterns

- Taking the compressed path without the owner's words, or reusing an invocation
  from an earlier change.
- Reading urgency, a small diff, or "go ahead" as the invocation.
- Reclassifying the tier to match the reduced ceremony.
- Fixing a symptom because the root cause would take longer to establish than
  the compression saved.
- Sweeping siblings and not disclosing them.
- Sweeping merely-similar occurrences under cover of the identical-shape rule.
- Discarding the temporary causality test without recording the gap as a debt.
- Treating the compression as authorization to push or deploy.
- Continuing on the path after a gate turns doubtful, rather than escalating.

## Reference files

- `core/method/tiers.md` (owns the contained lane's eligibility edges — one
  surface, no new dependency, reversible, no spec owns the surface — and the
  rule that the tier never moves; this page cites them and re-derives none)
- `core/method/vcs-posture.md` (owns the local commit as the resting state and
  publishing as a separate authorization the compression does not grant)
- `protocols/verify.md` (gate depth follows blast radius, never the lane; the
  record states what ran and what did not)
- `protocols/canonize.md` (where the why-record and the recorded debt land)
- `skill-corpus/prove-red-after-green.md` (the sequence step 4 composes: park
  the production paths, watch the named failure, restore, re-run)
- `skills/holistic-editing/SKILL.md` (the shape step 2 requires of the edit)
