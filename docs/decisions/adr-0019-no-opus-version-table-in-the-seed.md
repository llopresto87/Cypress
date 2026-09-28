---
status: proposed
status_date: 2026-09-28
owner: seed steward
---

# ADR-0019: the seed names no Opus version table; a protocol names the model class, and one rule maps the class to a version

## Status

See frontmatter, which is the single home. Filed 2026-09-28 for 7.32.0 by the
round's joint specify and grill pass, planned in
[`../plans/grill-7.32.0-harvest.md`](../plans/grill-7.32.0-harvest.md). The
owner ratified the round's scope; this record stays `proposed` until the
increments it names land. It supersedes no earlier ADR.

## Date

2026-09-28

## Context

The Prime Agent overlay, `integrations/prime-agent/APPEND_SYSTEM.md`, is
appended to every Prime Agent session. It carries two version tables: one maps
task kinds to model versions, and one maps each phase of grow, harvest and
graft to a version. The second duplicates the class each protocol already
names, and both go stale with every model release. The multi-agent-architect
charter pins "Opus 4.8" as its default for planning agents. The owner's rule:

> "scrap the opus version selection table. if you need to use opus, from now on
> use opus 5-5 (5.5) or opus 4.6 for extremely light/low effort authoring that
> you don't feel confident should be handled by sonnet." (R7)

## Decision

The overlay loses the Opus rows of its task-kind table and the whole
per-phase table, and states the rule in two lines: Opus-class work runs on
Opus 5.5, and Opus 4.6 only for extremely light authoring that Sonnet should
not be trusted with; the Sonnet floor stays Sonnet 4.6 or newer. The task-kind
table keeps its non-Opus rows.
The protocols keep naming the class of each phase, and that class is the one
home. The multi-agent-architect charter follows the same rule.

## Consequences

- Every Prime Agent session loads fewer bytes, which lowers the always-loaded
  cost the round's owner rules ask to cut.
- The overlay no longer tells a session which Opus version fits a harvest
  phase; the phase's class does, and the rule maps it.
- The published eager figures move, and the round's docs increment re-derives
  them. The CHANGELOG's 7.22.0 entry and the Prime Agent README are checked
  for other homes of the table in the same docs pass.
- Test that fails if this is reversed: `tests/seed-lint.py`'s eager-surface
  computation against the published figures, once the docs increment has
  re-derived them (plan increments 22 and 52).

## Alternatives considered

- **Keep the task-kind table whole and drop only the per-phase table.**
  Rejected: the owner scrapped the Opus selection itself, and the Opus rows
  are the ones that go stale.
- **Drop the non-Opus rows too.** Not done: the owner's rule names only the
  Opus selection, and the round's latitude is simple.
- **Move the tables into a node loaded on routing.** Rejected: that keeps a
  second home for a class the protocols already name.

## Reversibility

`reversible`: text in one overlay and one charter.

## References

- Spec: SPEC-0003's Prime Agent eager-surface contract, unchanged
- Grill: plan §6 decision 8 (8c') and R7, §9 increment 22
