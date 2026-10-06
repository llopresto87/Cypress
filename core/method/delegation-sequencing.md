---
id: method.delegation-sequencing
tier: 2
kind: method
origin: seed
title: delegation sequencing — spawn order by dependency, RED waves ahead of GREEN, and one writer per file set
owns:
  - delegation.sequencing
  - delegation.lanes
  - delegation.waves
requires:
peers:
  - method.delegation
  - method.delegation-cycle-economy
load_when:
  - "spawn order, parallel or sequential, which spawn waits for which"
  - "one writer per file set, parallel lanes, concurrent writers, who writes the shared file"
  - "RED wave ahead of GREEN wave, is this increment ready, held increment, expected-red at the tip"
prevents: Dependent units dispatched together and merged by hand, ready units held back by invented caps, a whole batch paused for one increment's problem, or two lanes racing on one file.
est_tokens: 2398
---

## Spawns are sequenced by dependency

When work spans specialists, decide by **independence**: units that
touch disjoint files/contracts and consume none of each other's outputs
may be spawned in parallel, each with its own complete brief and all of
them named in the plan. Units where one's output feeds the next are
sequenced, because spawning them together means merging them by hand.
Genuine parallelism is wall-clock you keep; false parallelism is a merge
conflict you scheduled.

**Dispatch every ready unit at once.** Unless the plan's §6 records an
owner-set spawn limit, dispatch all ready units together, in one message;
an unmeasured cap only delays ready work. Under a recorded limit, ready
REDs go first, lowest wave first and then in §9 order, then GREEN, then
prose; that rule orders units and sets no cap. Ready means its files are
disjoint from every live lane (`delegation.lanes`) and everything it
depends on is satisfied, which for implementation work `delegation.waves`
defines below. Machine load is handled in the brief, which carries the
clauses of `method.bounded-execution`. A shard that times out under load
is a transient failure; `protocol.recover` owns its retry budget.

**The run that gates the goal goes first.** When the goal waits on one run,
such as the next run in the real environment, the plan names it. The work that
run needs is dispatched first, ahead of the order above under a recorded limit,
with the lightest review the step's rules allow (a light reviewer,
`delegation.light-variants`, where the surface allows one); every other unit
runs beside it, never ahead. An increment that gates the run is split: the part
the run needs lands first, and the rest follows in the same lane.

**A read-only review starts as soon as there is committed work to read.** It
consumes only committed work, so it is independent of the writers still
running. When the plan includes a read-only review, such as a security review,
of a surface where a finding would reshape the increments that depend on it (a
credential holder, a writer to a shared resource), start that review right
after the first increment on the surface commits. Its ruling then lands before
the dependent work is written instead of after it.

The sequence is read, not improvised. A protocol pass takes it from
the protocol's phase table (`grill.flow` is the model: each phase names
what it needs and the one phase it may run beside); implementation
takes it from grill.md §9, whose rows are listed in dependency order
and whose `Depends on:` field is what "independent" means; the plan
linter prints those rows as waves (`delegation.waves`). A caller
issues a spawn only after every handback that spawn needs has
returned; the `spawn_id` ordinals it mints (`delegation.tracing`, in
`method.delegation-bounds`) are then the record of the order it actually
used, and a §15 entry cites them in that order. A flat numbered list is
not a sequence (it says nothing about which edges are dependencies), so
a document that only has one is not yet a source to spawn from.

## Lanes: one writer per file set (`delegation.lanes`)

A **lane** is the file set one live worker writes. **One writer per file
set.** Parallel lanes need disjoint files, and disjointness is measured on
files: two units about different subjects that edit one file share a lane.
A shared artifact, such as a spec or the plan-of-record, has one writer at a
time. A worker whose lane does not hold the shared artifact lists the rows it
would change (the row, its new status, the test that justifies it) in its
handback, and the lane holder applies them. A lane is done when its handback
returns, not when its files stop changing.

**Decide the order before dispatch, because a worker stopped partway leaves
its lane half-written.** Settle the dispatch order in the plan. A finding that
surfaces while lanes are live goes to a live lane only if that lane owns the
files the finding touches; otherwise it waits for the next dispatch. A shared
write ledger, where each worker claims its files before writing, works only
when every brief tells the worker to claim there.

**Take baselines without moving the shared tree.** When several lanes write
one working tree, a worker gets a baseline by copying the file or reading
`git show HEAD:<path>`, and runs no `git stash`, `checkout`, `restore` or
`reset`, because those move other writers' uncommitted files. The
orchestrator commits each lane by pathspec.

Two cheap signs show that a race between lanes did damage: an orphaned leaf
that no node references, and a heading duplicated inside a node two lanes
touched. Check for both after lanes that shared a neighbourhood return.

## Waves: RED ahead of GREEN (`delegation.waves`)

A wave is a set of increments that the plan's §9 `Depends on:` rows allow in
flight together. The session reads the schedule from `grill-lint.py --waves`.
That report is a static schedule. Which increments are already satisfied is
live state, and the session reads it from the plan's §15 entries, the commit
log and the batch record (the RED hashes and the expected-red list). A RED and
its GREEN are separate §9 increments, and the GREEN names the RED in `Depends
on:`, so the RED falls in an earlier wave with no rule needed to put it there.

**Work runs in cycles.** A RED wave writes every ready RED, spread over as many
parallel tester spawns as `delegation.effort-scale` requires, each sized
exactly as that scale gives it, with independent prose beside them. A GREEN
wave follows over the clean increments only, and no ruling pass comes before
it. The tip runs once the GREEN wave has handed back. One ruling pass, beside
or after the tip, then covers every flag both waves raised; it rules on the
held increments and the provisional readings only and is skipped when nothing
is flagged. The next cycle re-issues only the held increments and the work a
reversed provisional reading was built on, RED again where a ruling changed a
contract they encode and GREEN otherwise, together with any work that has newly
become ready. Cycles repeat until nothing is held. The batch still sizes
spawns; the cycle is the unit the ruling pass and the tip follow. The question
file and the shapes of an entry and a ruling are `delegation.question-file`, in
`method.delegation-cycle-economy`.

**When a dependency is satisfied.** A RED's own GREEN is the increment that
turns it green: the GREEN or prose increment whose `Depends on:` names the RED
and whose `Spec contracts:` include one of the RED's. For its own GREEN, a RED
is satisfied once the orchestrator has observed it red for the right reason
and recorded its hashes (`delegation.green-self-test`). For every other
dependent, a RED is satisfied only when its own GREEN has committed, because
what a dependent needs is the behavior, not the failing test. A dependency that
is not a RED is satisfied when it is committed after its review (the COMMIT of
`test-first.cycle`). Whether a RED's files commit alone or with its GREEN is
the plan's commit practice, and nothing here depends on it.

An observed RED whose own GREEN has not committed holds its test and fixture
files as a live lane (`delegation.lanes`), because its hashes are recorded and
any other writer would break them. Two REDs that must write one test file go
to one tester spawn, or the second waits for the first's GREEN to commit.

**Readiness.** A RED goes to a tester as soon as every increment it depends on
is satisfied, its files are disjoint from every live lane, and it is not held.
It does not wait for an unrelated batch's GREEN, tip or ruling pass. An
increment is clean when its RED was observed for the right reason and hashed,
and it is not held. Only clean increments enter a GREEN wave: the work that
turns a RED green is dispatched there when its RED is satisfied for it, every
other dependency is satisfied, its files are disjoint from every live lane,
and neither it nor its RED is held.

**The increment pauses; the rest of the batch runs on.** An increment is
held while any of these is true:

1. A question-file entry not yet ruled on touches it: its `where:` or
   `work held:` names the increment, a file in its `Files touched:`, or a
   contract in its `Spec contracts:` or a spec section that contract cites.
   When the orchestrator cannot tell, the entry touches it. A provisional
   reading holds nothing (`delegation.question-file`).
2. Its RED failed at observation for the wrong reason, or a test it wrote is
   under question.
3. A tip failure that is not on the expected-red list is attributed to it, by
   the failing test's contract or files; `protocol.recover` attributes it when
   that is unclear.

Every increment that depends on a held increment is held with it. Every other
increment in the batch proceeds, its GREEN included.

When a ruling amends a contract, or reverses a provisional reading, that a RED
already encodes, the session re-briefs that RED to a tester against the amended
text. The orchestrator records the old and new `sha256sum` of each test or
fixture file that changed, in the batch record beside the ruling id, and the
GREEN is briefed from the new hashes.

**Expected-red at the tip.** At each tip, once per cycle after its GREEN wave
(`delegation.tip-cadence`), every observed RED whose own GREEN has not
committed is listed by test id in the batch record as expected-red. A test id
is the finest name its gate reports: a unittest method, a shell case's
invariant label, or, for a lint step, the finding line. A failure whose id is
on the list does not fail the tip. A failure whose id is not on it does, even
inside a step that also carries a listed id, and it holds the increment it is
attributed to. A listed id that passes before its GREEN lands is reported and
goes to the question file, because the RED no longer fails for the reason it
was written for.

A gate step that aborts at its first failure proves nothing past the abort. The
tip record lists every case the step did not execute as `not run`, by id where
the step names its cases and otherwise as "the rest of `<step>`". A `not run`
id is neither a pass nor a failure, and by itself it holds no increment. A
change leaves the branch (merge, push or tag) only from a tip whose
expected-red list is empty and which lists no `not run` id, and only when no
provisional reading is unruled. The final tip is such a tip.
