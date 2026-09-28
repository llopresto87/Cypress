---
status: accepted
status_date: 2026-09-28
owner: seed steward
---

# ADR-0012: work runs in cycles of a RED wave and a clean GREEN wave, holds are per increment, and one ruling pass per cycle rules on what was flagged

## Status

See frontmatter, which is the single home. Filed 2026-09-28 in the joint
specify and grill pass for 7.31.0, planned in
[`../plans/grill-7.31.0-wave-scheduling.md`](../plans/grill-7.31.0-wave-scheduling.md)
(§6, §7, §9). The owner chose the design and then defined its cycle, so it is
filed `accepted`. It supersedes no earlier ADR. It supersedes, in part, an owner
decision of the 7.30.0 round (O-5, below). The owner's decisions are kept with
the round's working records outside the seed.

## Date

2026-09-28

## Context

The owner asked: "for 7.30 did we include to run all testers as many as posible
before spawing implementators". The answer was no. `protocols/test-first.md`
(`test-first.cycle`) already lets an increment's RED run early when §9's
`Depends on:` rows make it independent. `core/method/delegation-sequencing.md`
(`delegation.sequencing`) already forbids holding a ready unit back to fit an
invented cap. One rule blocked both: the cycle-economy ruling pass held every
spawn of batch `<N+1>` until batch `<N>` had handed back and been ruled on.

That gate put into practice the owner's 7.30.0 decision O-5, whose timing clause
reads: "once all in- flight testers or other agents for one "batch" of
implementation of increments that was spawned by orchestrator has landed,
before the next increment run architect and we fix/correct/complete based on
the new rulings of the architect". The same decision carries its reason, from
the owner's note on it: the "architect performs at it's best when it can see and
undertsand the whole picture instead of small bits/things to fix at 1 time".

The 7.30.0 round also recorded O-18, "a RED running ahead on landed
candidates", as not adopted. That was the session's own assumption for an item
the owner was never asked, not an owner decision.

In this round the owner asked for "this rule regarding spawing agents in waves -
smartly of course in respect to dependencies between test increments and
implementation increments", and chose the balanced latitude. Asked whether
waves override O-5's timing, the owner chose "Waves override O-5", then
confirmed: "oooh ok. so of course a single test having issues in a batch should
not stop or pause the batch, only the individual increment." The owner then
defined the cycle: "the target/goal is to do as much work as possible for each
spawned subagent withouth losing quality of output, and to optimize the
development cycle of the grill protocol to use less token total and run faster.
so the testers should write as many tests as possible, you run implementer on
the parts that passed implementer withoth needing architect arbitration, and
once that has completed we run architect on the parts that got flagged all in a
single batch and we re-issue the cycle for those blocked/paused increments".

## Decision

**Work runs in cycles: a RED wave that writes every ready RED, a GREEN wave over
the clean increments with no ruling pass before it, the tip, then one ruling pass
over every flag the cycle raised. The next cycle re-issues only the held
increments. The unit that pauses is the increment, never the batch, and
`grill-lint.py --waves` reports the dependency schedule the waves follow.**

The rule is one owned id, `delegation.waves`, in
`core/method/delegation-sequencing.md`. Its text is SPEC-0005 §6 "Waves"; the
report is SPEC-0005 §6 "Wave report" and §4's five `GRILL_WAVES_*` contracts.
The central tradeoff: a GREEN that runs before the ruling pass, or a RED written
ahead, can be invalidated by a later ruling and cost a re-issue. In exchange,
nothing clean waits for a ruling it does not need, and every ready RED is
written in the same wave. The wave uses as many parallel tester spawns as the
effort scale requires, and the scale's per-spawn sizes do not change.

**What this supersedes.** It supersedes, in part, O-5. Its timing clause,
"before the next increment run architect", no longer holds work that no
question touches. The ruling pass now comes after the clean GREEN wave. O-5's
other part stands: the architect still rules in one pass over the whole
picture. That pass covers every flag of the cycle, and none is ruled piecemeal.

O-18 is not superseded by the owner, because the owner never decided it. As
7.30.0 defined it, a RED running ahead on landed candidates, it is now partly
adopted: a RED may run on work that is committed while its tip is still
pending. What stays out of scope is SPEC-0005 §2's item: "a RED written
against an earlier increment's candidate before that increment's GREEN lands".

## Consequences

- **What makes something ready.** A RED's own GREEN may start once the RED is
  observed for the right reason with its hashes recorded. Any other dependent
  of a RED waits for that RED's GREEN to commit. Anything that is not a RED is
  satisfied once committed after review. No rule depends on whether a RED
  commits alone or with its GREEN.
- **Observed REDs hold a lane.** An observed RED whose GREEN has not committed
  holds its test files as a live lane, so no other writer breaks its hashes.
- **Holds are per increment.** An increment is held when a question touches it,
  when its test failed for the wrong reason or is under question, or when an
  unexpected red at the tip is attributed to it. Whatever depends on it is held
  too. Everything else proceeds, its GREEN included.
- **The tip carries early REDs and names blind spots.** Each tip lists early
  REDs as expected-red by test id (R0.1). A step that aborted proves nothing
  past its abort, and its unexecuted cases are listed as `not run`. Nothing
  leaves the branch until a tip carries neither.
- **An amended contract re-issues its RED,** and the hash change is recorded
  beside the ruling id.
- **There is no new cap.** Without an owner-set spawn limit, every ready unit
  goes out in one message.
- **`grill-lint.py` gains `--waves`, which ships to plants.**
  - It is a report: its exit status is the plain lint's, and overlap lines are
    WARN.
  - A plan without `Phase:` prints "unscheduled". Duplicate increment numbers
    print "not computed".
  - The unchanged-gate claim holds on every plan `tests/test-grill-lint.sh`
    builds. No wider claim is made.
- **Files that change:**
  - doctrine: `core/method/delegation-sequencing.md`,
    `core/method/delegation-cycle-economy.md`, `protocols/test-first.md`,
    `agents/00-orchestrator.md`;
  - tool and tests: `templates/knowledge-graph/grill-lint.py`,
    `tests/test-grill-lint.sh`, `tests/seed-lint.py` (`ADOPTED_RULE_HOMES`),
    `tools/gate-registry.py` (one entry);
  - mirrors: `DOCUMENTATION.md`, `documentation/*-reference.md`,
    `manifest.json`, `CHANGELOG.md`.

  Plan §9 lists them by increment.
- **Verification.**
  - If the rule's home were moved, `ADOPTED_RULE_HOMES` would fail on
    `delegation.waves`.
  - If `--waves` gained a hard failure or crashed on a built plan,
    `GRILL_WAVES_LEAVES_THE_GATE_UNCHANGED` would fail.
  - The dispatch rule itself is doctrine and is judged by review. No test fails
    if a session pauses a whole batch for one increment.
- **Wiki:** none; no library is involved.

## Alternatives considered

### SIMPLE: narrow the gate, build no tool

The session would read waves off `Depends on:` by hand. Rejected: hand
derivation at every cycle, with nothing checking it, and the plan's success
criteria ask for the schedule to come from the linter.

### CREATIVE: no batches, question-pressure rulings, a schedule file

Rejected: it adds concepts the goal did not ask for, a schedule file and
rulings triggered by pressure. A ruling that fires on part of the flags breaks
O-5's whole-picture pass, which the owner kept. The owner stored this design
and chose balanced.

### Keep O-5's timing: rule at every batch boundary

The batch lands, then the ruling pass runs, then the next increments. Rejected
by the owner (Q0.8): one problem would pause a whole batch, where the owner
wants only the increment paused. It also holds clean GREENs for a ruling they do
not need.

### Waves as batches: one RED batch, a ruling pass, then GREEN

This keeps O-5's timing literally by making each wave a batch. Rejected by the
owner's cycle definition: implementers run on the parts that passed "withoth
needing architect arbitration", and the architect comes after.

## Reversibility

`reversible until tagged`. Before v7.31.0 is tagged, reverting restores the
7.30.0 gate paragraph and drops the flag. After the tag, `--waves` has shipped
to plants and published tags cannot move, so removing it is a behavior change
that needs its own release (C9 of the round's refutation pass). It needs no data
migration: the report writes nothing, and no plan format changes.

## References

- Spec: `docs/specs/SPEC-0005-cycle-economy.md` §4 (the `GRILL_WAVES_*`
  contracts), §6 ("Waves", "Wave report", "Adopted rule homes", the ruling-pass
  paragraph), §7
- Plan: `docs/plans/grill-7.31.0-wave-scheduling.md` §2, §6, §7, §9;
  `docs/plans/grill-7.30.0-cycle-economy.md` (the round whose gate this changes)
- Rule homes: `core/method/delegation-sequencing.md` (`delegation.sequencing`,
  `delegation.lanes`, `delegation.waves`), `core/method/delegation-cycle-economy.md`
  (`delegation.question-file`, `delegation.tip-cadence`)
- Enforcement vocabulary: `adr-0003-enforcement-layering-honesty.md`
