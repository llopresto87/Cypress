---
status: proposed
status_date: 2026-10-05
owner: seed steward
---

# ADR-0028: harvest takes a plant's knowledge whole: generalize instead of reject, admit documented version facts, verify every fact by provenance

## Status

See frontmatter, which is the single home. Filed for 8.0.0 from the owner's
decisions of 2026-10-04 and 2026-10-05: generalize rather than reject, admit
stack-keyed pages and deep stack knowledge, land only withdraw-ready pages,
keep an observed fact beside what the docs say, admit problem-to-fix records,
put each lesson into the surface that already owns its subject, admit
documented version facts, and keep security facts and a plant's own version
out. It supersedes no ADR.

## Date

2026-10-05

## Context

`protocols/harvest.md` was written for one plant at a time and a thin corpus:
reject when in doubt, harvest the "surface" only, keep every version number
out, leave incident narratives in the plant. Use showed what
that cost. Every stack-bound procedure proved in practice hit the "stays out"
clause. The durability gate's "upgrade diffs between two pins" clause rejected
the upgrade skill the owner had asked for. A library page stripped of version
facts sent the next plant back to a scout. Reviews spent effort stripping facts
the owner then ruled admissible. Meanwhile the wider latitude moved the main
risk from leaks to truth: source pages carried wrong facts, workers added facts from
their own knowledge, and the independent reviews found that unverified facts
were the most common defect. Doing nothing keeps the seed thin and keeps every
plant re-researching what an earlier plant already paid for.

## Decision

Harvest generalizes rather than rejects: every plant-authored skill,
procedure, tool, agent and gate is a candidate, a stack-bound one lands as a
stack-keyed page, deep library expertise lands whole (or not at all), and
problem-to-fix cases and owner decision rules are woven into the existing page
that owns their subject. A corpus page may carry any version fact the
library's own release notes or documentation state, written with the subject
it qualifies. Security facts (CVE ids, advisories, exposure warnings) and
calendar dates stay out, and a plant's own version is never stated or cited as
evidence. Every fact is classed plant-proven, upstream-fetched or
model-supplied, and a model-supplied fact lands only after a fetch confirms it.

## Consequences

- `protocols/harvest.md` gains the multi-plant flow (per-plant survey,
  per-library cross-plant wave, consolidation by lineage), the provenance
  classes and merge rule, the G5 baseline form, the extra Phase 1 donor surfaces
  (the harvest-candidate record, pre-graft agent systems, harness-only skills,
  session metrics through the reader), and a rewritten durability gate. The
  corpus READMEs and `HARVEST_PROMPT.md` follow it, and the documentation
  mirrors become pointers to those homes.
- Review effort moves from stripping version numbers to checking sources: G3
  spot-checks re-open cited sources and check each sampled fact's provenance
  class, and G2 reads the version rule, which has no detector.
- Owner preferences are not project rules; where one lands (public corpus or
  private overlay) is the owner's decision, asked first.
- Test that would fail if this were silently reversed: none mechanical. The
  version rule is judgment (G2); `tools/agnosticism-lint.py`'s CVE rule still
  holds the one mechanical part (`tests/test-agnosticism-lint.sh`). A
  mechanical check for dates or advisory-shaped facts would be new code, with
  its own spec and RED test.
- Wiki effect: library pages grow version sections and battle-tested
  pitfalls; plants confirm each version fact against their own pin through
  `ingest-library`.

## Alternatives considered

- **Keep the major-line-only rule** (the 2026-10-04 decision): rejected,
  because minimum versions and "changed in" notes are what a reader needs
  most, and stripping them forced each plant to re-fetch them.
- **Admit security facts with version bounds:** rejected; scanners and
  advisory feeds own exposure data, read against each plant's lockfile, and a
  corpus copy goes stale silently.
- **A new expertise corpus for cases and decisions:** rejected; every case
  has an existing home, and a second surface splits facts across two homes.

## Reversibility

`reversible now → expensive after the first harvest that lands version facts
under this decision`: reversing it then means stripping version facts from
every page that carries them, and the cost grows with each later harvest.

## References

- `protocols/harvest.md`, "The second gate: durability (surface, not pin)"
- `library-corpus/README.md`
- [ADR-0023](adr-0023-a-declarative-edit-is-proved-by-a-run.md),
  [ADR-0013](adr-0013-harness-memory-is-not-a-home.md)
- The owner's decisions of 2026-10-04 and 2026-10-05, stated under Status
