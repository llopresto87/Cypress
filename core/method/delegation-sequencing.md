---
id: method.delegation-sequencing
tier: 2
kind: method
origin: seed
title: delegation sequencing — spawn order by dependency, and one writer per file set
owns:
  - delegation.sequencing
  - delegation.lanes
requires:
peers:
  - method.delegation
  - method.delegation-cycle-economy
load_when:
  - "spawn order, parallel or sequential, which spawn waits for which"
  - "one writer per file set, parallel lanes, concurrent writers, who writes the shared file"
prevents: Dependent units dispatched together and merged by hand, ready units held back by invented caps, or two lanes racing on one file.
est_tokens: 977
---

## Spawns are sequenced by dependency

When work spans specialists, decide by **independence**: units that
touch disjoint files/contracts and consume none of each other's outputs
may be spawned in parallel, each with its own complete brief and all of
them named in the plan. Units where one's output feeds the next are
sequenced — never spawned together and merged by hand. Genuine
parallelism is wall-clock you keep; false parallelism is a merge
conflict you scheduled.

**No invented concurrency cap.** A ready unit is never held back to fit an
unmeasured cap. Absent an owner-set limit recorded in the plan, dispatch all
ready units together, in one message. Ready means its files are disjoint from
every live lane (`delegation.lanes`) and everything it depends on has landed.
Machine load is handled in the brief, which carries the bounded-execution
clauses of `method.engineering-posture`, not by rationing spawns. A shard that
times out under load is a transient failure, whose retry budget
`protocol.recover` owns, and never a defect to "fix".

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
and whose `Depends on:` field is what "independent" means. A caller
issues a spawn only after every handback that spawn needs has
returned; the `spawn_id` ordinals it mints (`delegation.tracing`, in
`method.delegation-bounds`) are then the record
of the order it actually used, and a §15 entry cites them in that
order. A flat numbered list is not a sequence — it says nothing about
which edges are dependencies — so a document that only has one is not
yet a source to spawn from.

## Lanes: one writer per file set (`delegation.lanes`)

A **lane** is the file set one live worker writes. **One writer per file
set.** Parallel lanes need disjoint files, and disjointness is measured on
files, never on topics: two units about different subjects that both edit one
file are not independent. A shared artifact, such as a spec or the
plan-of-record, has one writer at a time. A worker whose lane does not hold the
shared artifact lists the rows it would change (the row, its new status, the
test that justifies it) in its handback, and the lane holder applies them. A
lane is done when its handback returns, not when its files stop changing.

**Decide the order before dispatch, because a live spawn cannot be recalled.**
There is no way to stop a worker partway through, so the dispatch order is
settled in the plan, not corrected mid-flight. A finding that surfaces while
lanes are live goes to a live lane only if that lane owns the files the finding
touches. Otherwise it waits for the next dispatch, and it is never bolted onto a
spawn that does not own its files. A shared write ledger, where each worker
claims its files before writing, works only when every brief tells the worker
to claim there.

Two cheap signs show that a race between lanes did damage: an orphaned leaf
that no node references, and a heading duplicated inside a node two lanes
touched. Check for both after lanes that shared a neighbourhood return.
