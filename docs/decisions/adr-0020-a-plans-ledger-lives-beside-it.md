---
status: proposed
status_date: 2026-09-28
owner: seed steward
---

# ADR-0020: a plan's increments live in the directory beside it named for its stem, and the seed's own round plans are ledgers

## Status

See frontmatter, which is the single home. Filed 2026-09-28 for 7.32.0 by the
round's joint specify and grill pass, planned in
[`../plans/grill-7.32.0-harvest.md`](../plans/grill-7.32.0-harvest.md). The
owner ratified the round's scope; this record stays `proposed` until the
increments it names land. It supersedes no earlier ADR.

## Date

2026-09-28

## Context

The owner's standing rule is that a plan of record is a ledger: an index in §9
and one file per increment. `grill-lint.py` supports the ledger, but only for
one layout: the plan is `plans/grill.md` and its increments sit in
`plans/grill/` beside the linter, with specs and decisions beside it too. The
seed keeps one plan per round under `docs/plans/`, specs under `docs/specs/`
and decisions under `docs/decisions/`. So the seed's own plans were written
monolithic (44 increments in one file for 7.30.0, 21 for 7.31.0), and no gate
lints them: run from `templates/knowledge-graph/`, the linter finds no specs.

## Decision

A plan's ledger lives in the directory beside the plan, named for the plan
file's stem. For a plant's `plans/grill.md` that is `plans/grill/`, exactly as
today. `grill-lint.py` gains `--specs DIR` and `--decisions DIR`, as
`spec-lint.py` has `--specs`. The seed's round plans are ledgers from this
round on, `tests/run.sh` lints the active round's plan with those flags, and
the 7.30.0 and 7.31.0 plans are converted to ledgers verbatim, proven
byte-for-byte by the ledger verification tool (decisions 5 and 7).

## Consequences

- A plant sees no change: its plan and ledger paths resolve as before.
- The seed's plan checks run on every gate. The active plan is named once, in
  `tests/run.sh`, and each round moves it.
- Older seed plans are converted or left as history, and the gate does not
  lint them; `tools/gate-registry.py` says so for the step.
- An evidence directory named for a plan's stem (7.15.0 and 7.29.0 have them)
  would read as orphan increments if that plan were ever linted. Those plans
  are history and are not linted.
- Tests that fail if this is reversed: the seed-layout cases of
  `tests/test-grill-lint.sh` (plan increments 2 and 25) and the plan step in
  `tests/run.sh` (increment 49).

## Alternatives considered

- **Stage a temporary `docs/graph/` layout for each seed plan.** Rejected: a
  copy with rewritten paths lints the copy, not the plan.
- **Put every round's increments in one `docs/plans/grill/` directory.**
  Rejected: each round's lint would report the other rounds' files as orphans.

## Reversibility

`reversible`: the flags default to today's paths, and a ledger can be rebuilt
into one file by the verification tool.

## References

- Spec: none; the plan layout is no spec's contract (plan §6)
- Grill: plan §6 decisions 5 and 7 and G3, §9 increments 2, 25, 47 and 49
