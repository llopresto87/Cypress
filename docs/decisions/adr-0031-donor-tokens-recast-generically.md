---
status: accepted
status_date: 2026-10-14
owner: seed steward
---

# ADR-0031: a donor-identifying token is recast as a generic reference that keeps every fact, in every record, an ADR body included

## Status

See frontmatter, which is the single home. It amends
[ADR-0011](adr-0011-donor-token-redaction.md) in two places: limit (a) of the
exception, and the bar on editing an ADR body. The scope otherwise, the
owner-decision trigger and limits (b) to (d) stand. The owner decided on
2026-10-14 that a donor token in a seed record is rewritten with a generic
reference instead of the fixed placeholder, superseding the placeholder choice
made earlier the same day, and decided the same day that the recast applies to
every record, an ADR body included. This record transcribes both decisions and
does not re-open them.

## Date

2026-10-14

## Context

A harvest round on 2026-10-14 found plant names in the default branch,
published in the 8.1.0 to 8.1.2 releases. The 8.1.0 plan of record cited one
plant throughout as the second tree its measurements ran on, and two more where
it recorded the owner's `repo:` ruling; SPEC-0007 cites them in its measured
figures and examples; ADR-0029 names one in its context and an alternative; one
8.1.2 CHANGELOG entry and its staged release notes name a plant a test graft
ran on; one routing golden row and one installer test carry a name in a path.
The plan, the spec's changelog, ADR-0029 and the CHANGELOG are append-only;
the spec body, the release notes and the two tests are integrated in place.

ADR-0011's exception covered only the append-only records outside
`docs/decisions/`, under limit (a): each token span becomes the one fixed
placeholder `[redacted]`, and no sentence is reworded or deleted. Applied to
these records, the placeholder removes the name and the fact the name carried.
"0 edges on [redacted] (no Python outside `docs/`)" no longer says why the tree
had no Python edges: it was a TypeScript web application, which is the reason
TS/JS extraction entered the tool's scope. A placeholder repeated through a
measurement section also reads as a seam, and a reader cannot tell whether two
of them name the same tree. In a test or a golden row, `[redacted]` would be a
path no project has. And under ADR-0011 an ADR body kept the token for good,
excepted by path from the steward's whole-tree G1.

## Decision

**A donor-identifying token in any seed record, an ADR body included, is recast
in place as a generic reference: a description of the project by its stack or
its role in the record ("a TypeScript web plant", "the second plant measured"),
introduced once and then used consistently within the record, so that each
sentence reads as if it had always been written that way and loses no fact.**
This replaces ADR-0011's limit (a) and lifts its bar on ADR bodies. The
reference names no project, domain noun, host, port or identifying path; every
figure, path and finding of the original stands; no sentence is deleted; the
only words that change are the token span and the grammatical glue the
reference needs (an article, "of", a possessive). The edit happens by owner
decision only and is always disclosed: limit (b) in the release's CHANGELOG
entry, limit (c) as a dated line in each edited plan's or spec's changelog, and,
for an ADR, as a dated section appended to that ADR. The wording of the
exception is held in one home, [`CLAUDE.md`](../../CLAUDE.md), Conventions,
"Append-only artifacts", as ADR-0011 set; this record does not restate it.

Files that are not append-only (a spec body, staged release notes, a test, a
fixture, a golden row) were always ordinary edits under ADR-0011. They follow
the same generic rule, so one leak is fixed one way in every file it reached.

The tradeoff: a recast is a reword, so the reviewer's word-diff no longer shows
one fixed string at every edit. The reviewer instead checks each substitution
for a lost fact and an identifying residue, which is slower than matching a
placeholder. The seed accepts that cost to keep the records true and readable.

## Consequences

- Recast under this rule on 2026-10-14: the 8.1.0 and 8.1.2 plans of record,
  SPEC-0007, ADR-0029, the 8.1.2 CHANGELOG entry and `.github/RELEASE_NOTES.md`,
  `tests/graph-routes.golden.tsv` and `tests/test-install-adoption.sh`. The plans
  and the spec each carry the limit (c) line in their changelog, ADR-0029 an
  appended dated section, and the next release's CHANGELOG entry carries the
  limit (b) statement naming the edited records and the token class (plant
  names), never a token.
- ADR-0011's residual `DONOR_TOKEN_IN_ADR_BODY` and the whole-tree G1 path
  exception it allowed are retired: no record keeps a donor token.
- `CLAUDE.md` Conventions takes the new wording in the change that lands this
  record, so the home and this decision agree.
- Verification: the agnosticism lint run with the local forbid list over each
  changed file finds no token; the reviewer's word-diff against the prior tag
  shows only token spans replaced by the record's generic reference (with its
  glue words) plus appended disclosure lines; the graph-route eval and the
  edited test pass unchanged in result. No CI test would fail if this decision
  were silently reversed, because the forbid list is never committed. That gap
  is recorded here and not closed.

## Alternatives considered

- **Keep limit (a) as written, the fixed `[redacted]` placeholder:** rejected
  by the owner on 2026-10-14. It drops the fact the name carried (what kind of
  tree was measured), reads as a seam, and in a test or golden row it puts a
  path into the suite that no project would have.
- **Keep ADR bodies outside the exception:** rejected by the owner on
  2026-10-14. An ADR is read longest of all the seed's records, so a token left
  there leaks to every later reader, and the path exception it needs weakens
  the whole-tree G1 for good. The appended disclosure keeps the visible record
  of the change that append-only exists to keep.
- **Erratum only, editing nothing:** rejected for the reason ADR-0011 gives;
  the default branch and future clones would keep carrying the names.

## Reversibility

`one-way` for the records already recast: reverting would put the plant names
back in the default branch. The rule itself is `reversible`: a later ADR can
restore the placeholder or the ADR-body bar for future edits, but the recast
records stay recast.

## References

- Amends: [ADR-0011](adr-0011-donor-token-redaction.md), limit (a) and the bar
  on ADR bodies
- Convention home: [`CLAUDE.md`](../../CLAUDE.md), Conventions, "Append-only
  artifacts"
- Recast records: [`../plans/grill-8.1.0-source-index.md`](../plans/grill-8.1.0-source-index.md)
  §15; [`../plans/grill-8.1.2-tool-surfacing.md`](../plans/grill-8.1.2-tool-surfacing.md) §1, §15;
  [`../specs/SPEC-0007-source-index.md`](../specs/SPEC-0007-source-index.md);
  [ADR-0029](adr-0029-source-index-is-derived-scratch.md), "Recast, 2026-10-14"
- Harvest gates: `protocols/harvest.md` (G1)
