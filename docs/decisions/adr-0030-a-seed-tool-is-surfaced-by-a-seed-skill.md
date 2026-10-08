---
status: proposed
status_date: 2026-10-07
owner: architect
---

# ADR-0030: a placed seed tool is surfaced by a seed skill node, and a plant's docs/graph/tools/ stays the plant's catalog

## Status

See frontmatter (single home). Proposed with the 8.1.2 contracts of
SPEC-0007; the owner rules on it as question 1 of
`docs/plans/grill-8.1.2-tool-surfacing.md` §12.

## Date

2026-10-07

## Context

The installer places `docs/graph/source-index.py` in every plant (8.1.0),
and the protocols call it at verify, canonize, grow and adopt. A session
that asks "what depends on this file" or "where is this name defined"
outside those protocols does not find it: no seed node names the tool in
its `load_when`, and even in the steward plant
`graph-lint.py --plan "find where a function is defined"` loads no node.
The steward plant finds it for the other three questions only through its
own `subsystem.source-index` node; the card
`docs/graph/tools/source-index.md` its canonize wrote is not routed.

The owner approved, on 2026-10-07, that the seed place such a card and a
catalog row in every plant. Reading the engines showed three facts the
approval did not have in view:

- The router routes Tier-2 nodes only. `docs/graph/tools/**` is Tier 3,
  opened only when a loaded node names it (`templates/knowledge-graph/_schema.md`,
  "Tiers"). A card alone is never routed, so it does not make the tool
  found by topic.
- `tools/` is a growth-audit collection (the seed ships its catalog template,
  `tools/index.md` under `templates/docs/`).
  A seed card there is a substantive leaf of every plant, so a coverage row
  that answers `ABSENT` for `tools/` turns `CONTRADICTED`, and a `COVERED`
  row passes on the seed's text (`lint_collections`). Every plant that
  recorded "no tools of our own" would fail its next graft gate.
- `docs/graph/tools/index.md` and every card in that folder are plant-owned
  (`skill.toolcraft`, canonize). Writing a row into it is a second in-place
  rewrite of a plant file (SPEC-0001 SINGLE_WRITER names one,
  `fill_plant_facts`), and its backup would be flagged by `graft-audit.py` as
  a knowledge overwrite.

## Decision

A placed seed tool reaches sessions through a seed skill node,
`skills/<tool>/SKILL.md`, placed as `docs/graph/skills/<tool>.md` with
`origin: seed` and projected into each harness's skills by the existing
placement; the seed writes no card and no catalog row into a plant's
`docs/graph/tools/`. For 8.1.2 the one such skill is `skill.source-index`.

## Consequences

- The tool is routed by its skill's `load_when`, and hosts that read skill
  descriptions (Claude Code, opencode, Prime Agent) see it natively.
- No new placer, provenance line, stamp key, collection exclusion or backup
  class: every seed skill is placed by `place_file` on every install and
  graft, flagged `RETIRED` if the seed drops it, and backed up when a plant
  holds a page of the same name (SPEC-0007 SKILL_NAME_HELD_BY_THE_PLANT).
- A card the plant wrote, such as the steward plant's
  `docs/graph/tools/source-index.md`, and every row of its catalog are never
  touched. The fresh-plant catalog template says that the seed's placed
  tools are described by seed skills and need no row.
- Plant-specific facts about a seed tool (a measurement, a pitfall in this
  project) belong in a plant card or node, not in the seed skill, which the
  next install replaces.
- The test that fails if this is reversed:
  SOURCE_INDEX_SKILL_ROUTES_ITS_FOUR_QUESTIONS (its route arms, and its arm
  that the installer writes nothing under `docs/graph/tools/` beyond the
  missing catalog).
- Reversal cost: reversible. Removing the skill is a seed edit; plants drop
  it at their next graft through `RETIRED`.

## Alternatives considered

- **A seed card in `docs/graph/tools/` plus a seed block in
  `tools/index.md` (the approved shape):** rejected because it still needs
  a Tier-2 node to be routed, and it costs a provenance rule for cards, a
  growth-audit exclusion for seed cards and the seed block, a
  `graft-audit.py --unfilled` reading that strips the block, a second
  SINGLE_WRITER exception and a backup class for the catalog, all to repeat
  what a skill node does with the placement that exists.
- **The card placed as a `tool-corpus/` page through `--expertise`:**
  rejected because the corpus holds tools a project may build, not the
  seed's own machinery, and the page would be placed only on the owner's
  list and stay Tier 3.
- **Phrases for the four questions added to an existing seed node, such as
  `skill.context-router`:** rejected because that node is loaded for most
  tasks and owns the knowledge rule; tool usage there would be a second
  subject in one node.

## Reversibility

`reversible`: one seed skill file and a manifest entry; no plant data.

## References

- `docs/specs/SPEC-0007-source-index.md` §2 and §4 "Surfacing (8.1.2)"
- `docs/plans/grill-8.1.2-tool-surfacing.md` §6, §7, §12
- `tools/growth-audit.py` `required_collections`, `lint_collections`;
  `tools/graft-audit.py` MODE 1; `install.sh` `place_graph_machinery`
