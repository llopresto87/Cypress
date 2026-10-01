---
status: accepted
status_date: 2026-10-01
owner: seed steward
---

# ADR-0027: the kernel's FIRST MOVE runs the router and `index.md` becomes the fallback map, because a measurement favoured it

## Status

See frontmatter, which is the single home. Filed 2026-10-01 for 7.37.0 from
the owner's ruling D2 of that round, kept with the round's working records
outside the seed. Its precondition measurement favoured the change, the
increment it names landed in the same round, and the body was brought in line
with the shipped text before the record was flipped to `accepted` at the
release pass of 2026-10-01. It supersedes no earlier ADR. It amends in part the consequence of
[ADR-0017](adr-0017-pre-growth-pointers-leave-the-kernel.md) that the kernel's
FIRST MOVE opens `docs/graph/index.md`; ADR-0017's decision, that the
pre-growth pointers live in the placeholder index, stands, and the new FIRST
MOVE still reaches that index.

## Date

2026-10-01

## Context

The kernel's FIRST MOVE tells every session to open `docs/graph/index.md` and
pick two or three nodes, with `graph-lint.py --plan` as an optional check. In
practice the hooks route every prompt, so hooked hosts route twice, and the
hookless hosts (opencode, codex) get no mechanical route unless the model
chooses the optional check. When `index.md` is read it costs about 5,500 to
6,000 tokens. Two early counts of how often it is read disagreed (7% of Prime
Agent session logs, and 68% of graph-touching parent sessions on a looser
count). The precondition replay settled it with one strict definition (a tool
call whose result shows the index's opening lines): 41 of 59 graph-touching
Prime Agent parents (69%) and 25 of 43 Claude Code parents working in a plant
(58%) open it, children rarely (4%); the 7% mixed children in. Parents already
ran `--plan` in 38 of 68 graph sessions, children in 534 of 667, so the change
partly codifies what models do.

The owner's ruling D2: "maybe yes. maybe the first step should be to run the
graph lint instead of index.md".

Two conditions had to hold first. The router had to stop forcing root and stop
routing pasted briefs, because a first move bound to a router with 0.39
paraphrase recall needs an honest way to say "no signal" (ADR-0026). And the
four `plant:` facts that only `index.md` carried had to reach the session
another way (ADR-0025 puts them on the plan).

Amendment, 2026-10-01 (owner ruling): the first move routes through Python
because the router's output grows with the task, while `index.md` grows with
the graph. Route compute is not a cost this design optimizes; model tokens
are, paid on input and on output. The owner: "python can scale to larger
graphs better than index.md can do."

## Decision

The FIRST MOVE routes the task line, through the injected suggestion or
`python3 docs/graph/graph-lint.py --plan "<task>"`, reads the LOAD nodes with
their `requires:` closure through `graph-lint.py --show <id>...`, and acts on
any `!` notice, since an empty plan's notice names the next step. It opens
`docs/graph/index.md`, the fallback map, only when the router fails, the plan
stays empty or wrong, or the task explores the graph itself.

## Consequences

- The change landed on a measurement, as this record required. The
  precondition replay ran after the router change, over real short sessions
  (two to five prompts) in seven plants, and scored the first move as it was
  (route text plus the observed `index.md` reads) against the new one (route
  text, `--show` reads, the notice), with the route held at the new hook text
  in both arms so that only this change was measured. Counts are a
  cl100k-compatible token count. The new first move was not larger on either
  host, in totals or medians:

  | Sessions | First-move window | Whole session |
  |---|---|---|
  | Prime Agent, 15 short | 25,359 -> 14,739 (-42%) | 56,662 -> 37,846 (-33%) |
  | Claude Code, 9 short | 56,189 -> 32,418 (-42%) | 66,572 -> 42,247 (-37%) |

  One Claude Code session of the nine grew, by 56 tokens (a partial index
  read replaced by a longer `--plan`; that session had no hook).
- The saving rests on one assumption the replay could not observe: that a
  session following the new FIRST MOVE stops opening `index.md` and opens the
  same nodes. That is the residual risk. On short Prime Agent sessions the
  first-move window breaks even when 14.2% of them still read `index.md`
  (whole session: 25.1%; Claude Code about 70%); before the change 33% (5 of
  15) did. A replay of sessions run after the release, under the same
  definition, settles it. If the read rate stays above break-even, the kernel
  text is the place to fix, and this record's Reversibility holds.
- The shipped FIRST MOVE is 583 bytes (`len(.encode())`, its ten lines and
  the blank line that follows), against 511 before, measured the same way;
  the kernel is 7,928 of its 8,000-byte budget:

  ```
  > ## ► FIRST MOVE — before reading code or writing anything
  > Route the task line: take the router suggestion the host injected,
  > or run `python3 docs/graph/graph-lint.py --plan "<task>"`.
  > 1. Read only the LOAD nodes (`requires:` closure included):
  >    `python3 docs/graph/graph-lint.py --show <id>...`.
  > 2. Say which nodes you loaded and which you skipped.
  > 3. Act on any `!` notice; an empty plan's notice names the next step.
  >
  > Open `docs/graph/index.md`, the fallback map, only when the router
  > fails, the plan stays empty or wrong, or the task explores the graph.
  ```

- Kernel §2 enters through the `protocol.*` node the route names, and falls
  back to the **Method** table in `docs/graph/index.md` only when the route
  names none, so protocol entry does not bring back a standing `index.md`
  read. Kernel §5 names `index.md` as the hand-written map: the Method table
  and the node table, the fallback the FIRST MOVE names. The hook pointer
  line ("the kernel's FIRST MOVE and §0 apply") does not change.
- `index.md` keeps what is needed at protocol entry or for orientation, not
  per prompt: the Method table, the task-shape table, the node table, cost
  discipline, and "when the graph is wrong".
- The seed files a plant receives say the same: the orchestrator's Turn 0,
  the tier table of `skills/knowledge-graph/SKILL.md`,
  `templates/docs/README.md` and the tree in `protocols/from-scratch.md` call
  `index.md` the fallback map, and the Prime Agent overlay points at the
  FIRST MOVE.
- An ungrown plant routes to an empty plan with a `no_signal` notice that
  names `protocol.initialize` among the protocol entry nodes, and the
  placeholder index still holds the pre-growth pointer for step 3
  (`PRE_GROWTH_POINTER_LIVES_IN_THE_PLACEHOLDER_INDEX` still holds).
- The full plan prints the four `plant:` scalars on one line
  (`PLAN_PRINTS_PLANT_BLOCK`), because a session that follows this FIRST MOVE
  may never open `index.md`, the only page that carried them. A key that is
  missing, unfilled or still a `<placeholder>` (an inline ` #` comment
  stripped first) prints no line, and a reminder prints none.
- A spawned child without the canonical brief still has the kernel, so its
  floor is "route your task line", which is why children need no injected
  route (ADR-0024).
- `skills/context-router/SKILL.md`, the traversal's one home, says the same
  in its own words: route first, read through `--show`, a reminder names
  surfaced ids, children are not routed.
- The doctrine edits are proved by runs, not new tests (ADR-0023): the kernel
  budget and restatement checks of `tests/seed-lint.py`, the full install's
  pre-growth case, and `--plan` on an ungrown fixture printing `no_signal`.
  The `plant:` line is behaviour and has its RED case.
- Landed after the router change (ADR-0026), because a first move bound to a
  router that forces root and routes pasted briefs is worse than the map, and
  after `--show` existed (ADR-0025).

## Alternatives considered

- **Keep `index.md` first and the router optional.** The default had the
  measurement gone against the change. Against it: D2, the measurement, and
  on hooked hosts every prompt is routed anyway, so a session that also reads
  the map pays for two routes (all seven hooked short Claude Code sessions
  read `index.md` after the route was injected).
- **On an empty plan, open `index.md`.** Rejected: one read costs about 5,500
  tokens, more than the route it would replace; the notice names the protocol
  entry nodes for about 155.
- **Print the Method table on every plan.** Rejected: it is needed at protocol
  entry, not per prompt, and protocol nodes already route (22 of 23 on the
  contract rows that name them).
- **Carry the `plant:` facts in the status hook.** Rejected: that reaches
  hooked hosts only; opencode and codex would lose them.

## Reversibility

`reversible`. Kernel text, one skill section, one overlay line, four
plant-installed wording lines and one renderer line.

## References

- Spec: SPEC-0003 `PLAN_PRINTS_PLANT_BLOCK`
- Plan: `docs/plans/grill-7.37.0-routing-context.md`, increment 4
- [ADR-0017](adr-0017-pre-growth-pointers-leave-the-kernel.md) (amended in
  part), [ADR-0023](adr-0023-a-declarative-edit-is-proved-by-a-run.md) (proof
  by a run), [ADR-0025](adr-0025-compact-route-lines-json-between-programs.md),
  [ADR-0026](adr-0026-node-router-ladder-and-gated-corpus.md)
- Owner ruling D2 of 7.37.0, the round's measurements and refutation pass,
  and the increment-4 precondition replay, kept with the round's working
  records outside the seed

## Ratification

Ratified by the owner after the 7.37.0 release, 2026-10-01: "accepted ratified".
