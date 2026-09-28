---
status: proposed
status_date: 2026-09-28
owner: seed steward
---

# ADR-0015: a plan may cite another repository's decision by a qualified reference, and grill-lint reports it as external

## Status

See frontmatter, which is the single home. Filed 2026-09-28 for 7.32.0 by the
round's joint specify and grill pass, planned in
[`../plans/grill-7.32.0-harvest.md`](../plans/grill-7.32.0-harvest.md). The
owner ratified the round's scope; this record stays `proposed` until the
increments it names land. It supersedes no earlier ADR.

## Date

2026-09-28

## Context

`grill-lint.py` reads every `ADR-NNNN` in a plan and fails the plan unless a
file with that number sits in the plan's own `decisions/` directory. It has one
namespace. A plant whose plan cites a decision of another repository, the seed's
host-tier decision for example, has two outcomes and both are wrong:
- the number is not filed locally, and the plan fails for a citation that is
  correct;
- a local ADR happens to carry the same number, and the lint passes over a
  citation that reaches a different decision.

A graft met the first case on a real plant: the plan cited two seed ADRs and
the plant's lint failed on both. The second case is latent in any plant whose
own ADR numbers overlap the seed's.

## Decision

A plan may cite another repository's decision as `<name>:ADR-NNNN`, where
`<name>` is a word naming that repository. `grill-lint.py` does not resolve a
qualified reference; it prints one line per distinct reference saying it is
external and was not checked, and it neither fails nor passes the plan on it. A
bare `ADR-NNNN` resolves against the plan's own decisions exactly as today.

## Consequences

- A plan can record what it rests on outside its own repository without
  failing the lint and without a false resolution.
- The lint cannot catch a bare number that was meant as external. That limit
  is stated in the lint's docstring; the qualified form is the way out of it.
- `grill-lint.py` ships to plants, so the change reaches every plant at its
  next graft (the engine reconciliation of ADR-0014).
- Test that fails if this is reversed: the external-reference case of
  `tests/test-grill-lint.sh` (plan increments 3 and 26).

## Alternatives considered

- **A declared external-decisions root per plan.** Rejected: it adds a
  configuration surface, and the lint would then read files from another
  repository, which it has no business opening.
- **Warn on every bare reference that has no local file.** Rejected: that is
  today's failure with a softer exit code, and it still passes a bare number
  that collides with a local ADR.

## Reversibility

`reversible`: one parser branch and its test.

## References

- Spec: none; grill-lint's decision check is no spec's contract (plan §6)
- Grill: plan §6 decision 1, §9 increments 3 and 26
