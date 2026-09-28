---
status: proposed
status_date: 2026-09-28
owner: seed steward
---

# ADR-0017: the pre-growth pointers leave the kernel and live in the placeholder index that grow rewrites

## Status

See frontmatter, which is the single home. Filed 2026-09-28 for 7.32.0 by the
round's joint specify and grill pass, planned in
[`../plans/grill-7.32.0-harvest.md`](../plans/grill-7.32.0-harvest.md). The
owner ratified the round's scope; this record stays `proposed` until the
increments it names land. It supersedes no earlier ADR.

## Date

2026-09-28

## Context

The kernel is loaded in every session of every plant. Two of its passages
serve only a plant that has not been grown yet: the FIRST MOVE fallback "If
there is no `docs/graph/` yet, use the installed `EXPERT_SEED_INSTALL_PROMPT.md`"
and the §5 bullet naming `EXPERT_SEED_INSTALL_PROMPT.md` and
`protocol.initialize`. After an install `docs/graph/` always exists, so the
first condition is never true; after grow neither passage has a reader. A
survey of the plant's own session history found the install prompt named in 53
tool calls and read in 4, which is the investigation such lines prompt.

The owner's rules for this round:

> "things that are about the seed should never be installed on the plant unless
> there is an absolute need. we can't waste lines of prompts loaded for things
> that are only about the seed"

> "models should not reason on facts already provided/present in their context
> because we already establish them through growth and the docs/graph"

The kernel sits at 7,931 of its 8,000 bytes, and the second rule needs one
sentence in §3.2 (ADR-0018).

## Decision

Both passages leave the kernel. The placeholder `docs/graph/index.md` that the
installer places, and that grow rewrites, carries them in one delimited
pre-growth block, and grow removes the block when it sets `grown: true`. The
kernel's §3.2 gains the settled-facts sentence of ADR-0018 in the bytes freed,
and the kernel's size goes down overall.

## Consequences

- A pre-growth session still meets the pointer: the kernel's FIRST MOVE opens
  `docs/graph/index.md`, which is the placeholder, and the install log prints
  the same fork. A target with no graph at all gets the route hook's no-graph
  message, which names the install prompt.
- A grown plant loads none of it.
- An existing plant's `index.md` is plant-owned and is not touched; it loses
  the kernel lines at its next graft, and it has been grown already.
- SPEC-0001 gains `PRE_GROWTH_POINTER_LIVES_IN_THE_PLACEHOLDER_INDEX`, pending.
- The published eager figures move; the round's docs increment re-derives them.
- Test that fails if this is reversed: the placement case of
  `tests/test-full-install.sh` (plan increments 16 and 40).

## Alternatives considered

- **Move the pointers into `EXPERT_SEED_INSTALL_PROMPT.md` only.** Rejected: a
  session that has not found that file cannot read a pointer inside it.
- **Keep them in the kernel and pay for the §3.2 sentence elsewhere.**
  Rejected: nothing else in the kernel is as idle after grow, and the rule is
  that seed-only lines do not load in a plant without an absolute need.

## Reversibility

`reversible`: the lines return to the kernel in one edit, within the budget
they used before.

## References

- Spec: SPEC-0001, pending block of §4
- Grill: plan §6 decision 8, §9 increments 16, 40 and 43
