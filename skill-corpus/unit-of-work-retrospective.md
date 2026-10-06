# Suggested skill: unit-of-work-retrospective

> Optional procedure: a large unit of work (a spec implemented over many
> increments, a migration, a multi-day session with dozens of spawns) has
> closed or reached a natural stop, and the owner wants to know what it cost,
> what made it slow, and what to do differently. **Composes**
> `protocols/deliver.md` (the "Session metrics" block, used where a delivery
> carries one), `tool-corpus/ops/session-cost-profiler.md` (the metric
> contract, the cost and quality lines, and, where an adapter exists, the
> reader), `protocols/canonize.md` (the close-out that files each lesson in
> its owning node), and
> `core/method/stewardship-posture.md` (§6: what is learned is written into
> the plant, not kept in memory) by reference. What it adds is the shape of a
> measured retrospective: numbers taken from records, root causes stated as
> decisions, a counterfactual order, and a table of which shortcuts are safe.

**Instantiate by supplying:** `<SPAN>` (the start and end of the unit of
work, as timestamps), `<TRANSCRIPTS>` (where the host records the main session
and each spawned worker), `<CODE_RANGE>` (the commit range the unit produced),
`<RUN_RECORDS>` (where real-environment runs are recorded: pipeline run ids,
deploy logs), `<PLAN>` (the unit's plan of record and its increments), and
`<RETRO_PAGE>` (where the retrospective is written; a plan page beside the
unit's plan). In a graph plant, `<RETRO_PAGE>` is a plan node with the
plant's node frontmatter (id, owns, load_when), so a later session can route
to it.

## When to apply

- A unit of work took much longer or cost much more than its plan said, and
  nobody can say from memory where the time went.
- The owner asks "why was this slow", "what would you do differently", or
  "where can we cut corners next time".
- Before planning a unit of the same shape, so the next plan starts from
  measured cost instead of the last plan's estimate.

Not for a short session: the `deliver` metrics block already covers it.

## 1. Method: measure from records, never from recall

Every number on the page comes from a record, and the page says which. A
fact that no record holds (a refusal seen on screen, a question the owner
answered aloud) may stand only when it is labelled with who supplied it
first-hand.

The metric set itself (spawns, tokens, wall time, stalls, handback sizes,
the quality line) is the profiler's contract
(`tool-corpus/ops/session-cost-profiler.md` §2). Where a delivery already
carries a "Session metrics" block (`protocols/deliver.md`), use its lines.
Measure the rest from records. Never back-fill an empty delivery block with
the retrospective's figures: `protocols/canonize.md` keeps an empty block
empty, because reconstructed numbers are guesses that a later harvest
would read as data. What a retrospective adds to the profiler's contract:

- **Spawns and agent types** from the host's records of each worker
  (`<TRANSCRIPTS>`). Exclude the spawn writing the retrospective.
- **Tokens** in two classes, summed once per model request. Input-side
  tokens are input plus cache writes plus cache reads; on a long session,
  cache reads usually dominate them. Output tokens are reported separately.
  Every share on the page says which class it uses, or two retrospectives
  cannot be compared.
- **One request, several lines.** Where the host documents a per-request
  usage event (one host's telemetry emits one event per API request, with
  its request id and the four token counts), sum those events. Otherwise sum
  transcript lines, and deduplicate first. Observed in practice, and stated
  in one host's own documentation: a model response is written as one
  transcript line per content block, so a naive sum double counts. Input-side
  figures repeat on every line of a request. On some host versions output
  tokens grow across those lines as the response streams. So key each
  request on the message id and the request id together, and keep its last
  line (or the line with a final stop reason), not the first. Check a few
  requests by hand before trusting a total.
- **Wall time** per transcript, from its first to its last timestamp. Idle
  gaps in the main loop (longer than a stated threshold) are listed
  separately, with their cause when a record shows it (a usage limit, a wait
  on the owner). Calibrate the threshold from measured durations of the work
  being run (the profiler's stall-threshold pitfall), and state it on the page.
- **Activity class** per spawn (writing a failing test, implementing,
  reviewing, ruling on the spec, maintaining spec rows, ingesting libraries,
  diagnosing a real-environment run). Classify from each spawn's agent type and
  task title. That is a keyword classification, so the page says the shares
  are close, not exact.
- **Code** from `<CODE_RANGE>`: commits, files, lines added and removed, and
  test lines against other lines.
- **Real-environment runs** from `<RUN_RECORDS>`: the first time each run
  appears.

Scripts written for this are disposable unless the plant keeps a profiler.
Name where they ran, so a reader can rerun them, and say when a tool would
have done it (a candidate for `skills/toolcraft/SKILL.md`).

## 2. Timeline and cost

Three tables, each with its unit and its source:

1. **The whole unit:** elapsed time, idle gaps, spawns by model class, worker
   hours, tokens (worker and main loop, and the main loop's share), context
   compactions, commits and lines, test count at start and end, final spec
   size. Add handback sizes (median, p90, largest), worker stalls with their
   longest silence, declined spawns, and any spawn that ended with no
   handback.
2. **Where the worker cost went:** one row per activity class, with spawns,
   agent-hours, tokens and share of tokens, sorted by share. Under the table,
   write the two or three readings that stand out, each as one sentence with
   its number ("spec work cost more than the code that implemented it").
3. **Cycle time per increment:** the median time from a failing test's start
   to the passing change's end, the fastest and slowest increments, and spawns
   per increment.

Beside the cost, report the **quality line**, as the profiler's metric
contract defines it ("two lines, never one"): review Critical/Major findings
per increment, red full-suite runs, and mutants killed/total, or "no mutation
pass". A cost figure with no quality line beside it cannot tell a faster
order from a skipped check.

Then the **critical-path event table**: when did the work first meet the real
environment (the first pipeline run, the first deploy, the first run on real
data), measured in hours from the start and in commits and spawns already
spent. When that event came late, it is usually the finding that explains
most of the rest: list what each real run found that no local test could, and
estimate how much work was built on assumptions those runs corrected.

## 3. What went wrong, and why

One subsection per problem, each in the same four parts:

- **Symptom:** what was observed, with its number.
- **Decision:** the choice that produced it (an increment order, a review
  depth, a rule that arrived late). A root cause is a decision someone made,
  not "it was slow".
- **The owner's words**, quoted, when the owner commented at the time.
- **Row:** the lesson's row in the plant's harvest-candidate record (§6).

Include the method slips the owner had to correct, and the near misses: a fix
that taught a loop to continue past a failure, a cleanup that deleted
something live. They are the cheapest lessons on the page.

## 4. The faster order, at comparable quality

Write the order of work that would have reached the same quality sooner, as a
numbered plan with rough hours. Say first what quality is held fixed (the
guards, the security rules, the proofs that tests can fail), so a reader
cannot mistake the plan for "skip the checks".

A common shape when the real environment came late: a walking skeleton first
(the pipeline or deploy path with every step stubbed, run once on the real
target), then one domain per increment behind it, with a real run per batch.

Add a **savings table**: one row per lever, with what it would have saved,
derived from the measured costs of §2. Label every figure an estimate. Give a
total range, never a single number.

## 5. The corner table

One row per shortcut that was taken, or proposed, or that the owner asked
about:

| corner | safe to cut? | why | row |
|---|---|---|---|
| <what was done each time> → <the cheaper alternative> | Yes / Yes, if <condition> / **No** | <the evidence, or the risk it would remove> | <harvest-candidate row> |

Rows that say **No** matter as much as the others: write down, for example,
that proving a test can fail stays per increment, that a secrets rule stays
absolute, and that production acts stay with the owner. A later session
looking to save time reads this table first, and a missing "No" row reads as
permission.

## 6. Feed every lesson forward

- **Harvest candidates.** Each lesson that might belong in the seed is
  flagged a harvest candidate for the close-out, which adds its row to the
  plant's record, `docs/graph/plans/harvest-candidates.md`
  (`canonize.harvest-candidates` owns when a row is added; the blank form,
  `docs/graph/plans/_harvest-candidates.template.md`, holds the columns and
  the admission test).
  The retrospective states the evidence and links the row; it does not
  restate the lesson.
- **A lesson that already has a row** gets the measured cost added to that
  row, not a new row.
- **Plant lessons.** A lesson that is the plant's own goes to its owning node
  through the canonize close-out (`protocols/canonize.md`), never into
  harness memory (`stewardship-posture.compounding-knowledge`).
- **Process changes already adopted** during the unit are listed with their
  rows, with a note when they arrived too late to help most of the work.

## 7. Revise by appending

When the unit continues after the retrospective, a second pass appends a
dated section ("v2") that covers only what happened since. It reruns the §1
method over the whole span, gives whole-unit and since-the-cut columns side by
side, and links earlier numbers that still hold instead of restating them.
The first pass stays as written.

## Reference files

- `protocols/deliver.md` (Session metrics: the per-delivery block, used where
  it exists)
- `tool-corpus/ops/session-cost-profiler.md` (metric contract, the two lines;
  adapters)
- `protocols/canonize.md` (filing plant lessons in their owning nodes; an
  empty metrics block stays empty)
- `core/method/stewardship-posture.md` (§6, knowledge compounds in the graph)
- `skills/toolcraft/SKILL.md` (when a disposable script should become a tool)
