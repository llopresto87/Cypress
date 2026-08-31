<!--
Template: adr.template.md
Authored by: architect, orchestrator
Lives at: docs/graph/decisions/adr-NNNN-<slug>.md
Used: on every non-obvious technical decision; one ADR per decision
Filled by copying this template into the target path and replacing
every <placeholder>. Stable section numbers must not be renumbered;
agents and tooling index into them.
-->

# ADR-NNNN: <short slug>

## Status

`proposed` | `accepted` | `superseded by ADR-NNNN` | `deprecated`

## Date

YYYY-MM-DD

## Context

What is the situation that forces a decision? Include the constraint
that makes "do nothing" not viable. Cross-link to the relevant
sections of grill.md and the spec.

## Decision

What we have decided, in one sentence. Optionally a short paragraph
that names the central tradeoff.

## Consequences

What changes as a result of this decision. Include:
- New constraints downstream.
- Migration or rewrite cost if the decision is reversed.
- Effect on the verification plan.
- Effect on the wiki (new libraries to wikify, idioms to record).

## Alternatives considered

For each alternative we rejected, one paragraph naming the
alternative and the reason it lost. The reason must be concrete
("requires a vendor lock-in that violates §4 constraint C-3"), not
generic ("not as good").

- **Alternative A:** … — rejected because …
- **Alternative B:** … — rejected because …

## Reversibility

`reversible` | `expensive` | `one-way`

Reversibility can degrade over time: a decision that is cheap to undo
today may become expensive or one-way once a specific operational
milestone occurs. Record that as a graduated value and name the
trigger — e.g. `reversible now → expensive after <milestone>` (once
external consumers depend on a stable identifier, once issued
artifacts are live in the field).

If `expensive` or `one-way` — now or after the named milestone — state
the cost in concrete terms (e.g. "changing this after external
consumers trust it requires coordinating a migration with every
downstream client and one week of engineering work").

## References

- Spec: <SPEC-NNNN-*>
- Grill: <docs/graph/plans/grill.md §N>
- Wiki: <docs/graph/libraries/*>
- External sources: <docs/graph/sources/normalized/*>
