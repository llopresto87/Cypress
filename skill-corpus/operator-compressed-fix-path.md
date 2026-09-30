# Suggested skill: operator-compressed-fix-path

> Optional procedure — the disciplined form of a **compressed-ceremony** fix:
> the owner, in words, opens a path that reduces *who is involved* and *how much
> process wraps the change*, for a defect whose root cause is already known and
> whose diff is small. Two neighbours already own most of the rules and are
> cited: `core/method/tiers.md` owns the contained lane's eligibility edges and
> the tier rule; `core/method/vcs-posture.md` owns the local commit as the
> resting state of work and publishing as a separate authorization. What this
> page owns is only three things: the **owner-opened authorization**, the
> **disclosed sibling sweep**, and the **temporary causality test whose removal
> is recorded as a debt**. Parameterized by `<BUILD_COMMAND>` and
> `<OWNER_INVOCATION>` — the words that opened the path.

## When to apply

Apply ONLY when the owner has opened the path, in words, in this conversation,
for this change: the compression is an **authorization**, granted per
invocation. Urgency, a small diff, an earlier grant, and "just fix it" or "go
ahead" are not those words. Without them, the change takes the ordinary path
for its tier.

Record `<OWNER_INVOCATION>` verbatim in the why-record. A compression nobody can
point at later is indistinguishable from process that was skipped quietly.

## What is compressed and what stays at full strength

The path reduces the number of people and spawns involved and the ceremony
around the change. It leaves four things at full strength:

- the risk classification — the tier is what the change's surface makes it, and
  it does not move because the ceremony did (`tiers.hard-edges`);
- the build — `<BUILD_COMMAND>` runs, and the gates the change's blast radius
  earns run with it (`protocols/verify.md` owns that depth, and it follows the
  radius);
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

The fix rests as a local commit (`core/method/vcs-posture.md` §1). Publishing
it, a push or a deploy included, is a separate authorization the compression
did not grant, so the delivery asks for it and reports the fix as unpublished
until it lands: a small fix kept local leaves the defect live everywhere else,
and the next person fixes it again, usually wider. "Fix it quickly" is not a
push.

## The four gates

All four must hold. Two are the contained lane's eligibility edges read
forward, and are `tiers.contained-lane`'s: read them there, in full, before
using this page; the other two are this path's own.

1. **Root cause established.** Not suspected, not narrowed to a file — known,
   and statable in one sentence that explains every observed symptom. A fix
   aimed at a symptom is a guess, and a guess is exactly what the compressed
   path has no capacity to catch. The root cause covers every shape the
   producer can emit: a guard written for the one malformed value in front of
   you is not a guard for the class, and an upstream that sends a null may also
   send an empty string, a blank one, and the literal word for null. Enumerate
   those shapes before deciding the diff is small; a shape you have not
   measured is a root cause you have not finished understanding.
2. **Diff small and local**, on one surface, reversible — `tiers.contained-lane`.
3. **No new dependency, contract, or persisted format** — `tiers.contained-lane`.
4. **Result self-verifiable.** The correctness of the change can be established
   by this session, now, with `<BUILD_COMMAND>` and the gates available to it.
   If confirming the fix requires another actor, another environment, or a
   judgment this session cannot make, the path is closed.

**Any doubt escalates back to the full path.** Unanimity is the rule: a gate you
are unsure of is a gate that does not hold. Escalating mid-change is the
expected outcome sometimes: say so and re-route; it costs a message.

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
they were not part of what the owner asked for. A sibling that is only similar
in shape is named as a finding and left for its own decision.

An undisclosed preemptive fix is **undisclosed scope**, even when it is good
engineering and even when every occurrence was genuinely the same shape. The
owner authorized a compression of ceremony over a change they had in mind; a
diff larger than that change, unannounced, spends the compression on something
they never saw. Disclosure costs one sentence and keeps the path usable next
time.

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
with its debt. The tier is stated as the change's surface makes it, whatever
ceremony ran: the compression is a fact about process, the tier a fact about
the change, and a record that aligns the second to the first makes the whole
path untrustworthy.

## Reference files

- `core/method/tiers.md` (owns the contained lane's eligibility edges — one
  surface, no new dependency, reversible, no spec owns the surface — and the
  tier rule)
- `core/method/vcs-posture.md` (owns the local commit as the resting state and
  publishing as a separate authorization the compression does not grant)
- `protocols/verify.md` (gate depth follows blast radius; the record states
  what ran and what did not)
- `protocols/canonize.md` (where the why-record and the recorded debt land)
- `skill-corpus/prove-red-after-green.md` (the sequence step 4 composes: park
  the production paths, watch the named failure, restore, re-run)
- `skills/holistic-editing/SKILL.md` (the shape step 2 requires of the edit)
