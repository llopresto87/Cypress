---
id: method.delegation-wave-integrity
tier: 2
kind: method
origin: seed
title: wave integrity — the written lane table, a hash baseline diffed after the wave, and output that survives an interruption
owns:
  - delegation.lane-table
  - delegation.wave-baseline
  - delegation.durable-output
requires:
peers:
  - method.delegation-sequencing
  - method.delegation-briefs
load_when:
  - "lane table for a parallel wave, which paths may each worker write"
  - "a write is needed outside the lane's paths"
  - "hash baseline before a wave, prove nobody wrote outside their lane"
  - "an interrupted spawn left nothing on disk, in-progress output file"
prevents: An out-of-lane write that nobody detects, a shared file split across two lanes, an accepted uncommitted edit reverted as if a lane had made it, and an interrupted worker that leaves nothing on disk.
est_tokens: 872
---

# Running a parallel wave

`delegation.lanes` (in `method.delegation-sequencing`) sets the rule: one
writer per file set. This node is how a wave of parallel lanes is set up before
dispatch and checked after it hands back.

## The lane table (`delegation.lane-table`)

**A parallel wave runs from a written lane table.** Before dispatch the caller
writes the wave's lanes as a table: one row per worker, with the paths it may
write and, in a separate column, the paths it must treat as read-only (the
shared inputs it reads and the files another lane holds). Beside the table
goes the list of shared files that force the wave's order: a file several
lanes would need to write, such as an index, a registry, a golden corpus or the
plan, is never split across rows; it belongs to one lane, waits for a later
wave, or reaches its holder as handback rows. Each brief carries its worker's
row and names the concurrent writers (`delegation.briefs`). A worker that finds
it needs a write outside its row stops there and hands back with the edit it
needs instead of making it in passing, because a fix in passing is a second
writer the lane holder does not know about.

## The baseline, diffed after the wave (`delegation.wave-baseline`)

**Baseline the tree before a wave and diff it after.** Before dispatch, record
a content hash of every file the wave must not change, which is everything
outside the union of the table's writable columns. A file that already carries
an accepted uncommitted edit goes into the baseline as it stands, so the
comparison does not read that edit as a lane's write and nobody reverts it.
Hash the content: a status listing already shows a dirty file as dirty, so it
cannot show a second write to it. After the wave hands back, hash again and
diff: a changed file outside every row is an out-of-lane write, named before
anything commits. Take baselines without
moving the shared tree: hash the files, copy them, or read
`git show HEAD:<path>`, and run no `git stash`, `checkout`, `restore` or
`reset`, because those move other writers' uncommitted files. The
orchestrator commits each lane by pathspec.

Two cheap signs show that a race between lanes did damage: an orphaned leaf
that no node references, and a heading duplicated inside a node two lanes
touched. Check for both after lanes that shared a neighbourhood return, beside
the baseline diff.

## Output that survives an interrupted worker (`delegation.durable-output`)

**A worker's file deliverable survives its interruption.** A worker whose
deliverable is a file creates that file first, with an in-progress status
marker at its top, appends each finding as it is found and flushes it to disk,
and changes the marker to complete as its last write. A worker stopped by a
usage limit, a host restart or a stall then leaves durable partial output,
marked as partial, that the resumed or the next worker continues from; one that
writes only at the end leaves nothing. The report body's overflow note follows
the same rule (`templates/prompts/handback-payload.md`).
