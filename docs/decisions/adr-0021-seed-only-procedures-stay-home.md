---
status: proposed
status_date: 2026-09-30
owner: seed steward
---

# ADR-0021: a seed-only procedure lives under `docs/skills/`, and seed-lint proves it never reaches a plant

## Status

See frontmatter, which is the single home. Filed 2026-09-30 for 7.35.0 from the
owner's rulings D1 and D2 of that round, which are kept with the round's working
records outside the seed. This record stays `proposed` until the increments it
names land. It supersedes no earlier ADR.

## Date

2026-09-30

## Context

The owner asked for a release procedure that keeps the seed's documentation
current with each round's changes, and set its boundaries (ruling D1):

> "we need a "release skill" that is run with canonize(it will call canonize but
> we will not pollute canonize and it will be seed-only and on this plant for
> convenience) so that all docs are kept up-to-date with seed t changes"

and asked that copies of one fact be held by lint or replaced by a pointer
(ruling D2): "lint to keep the aligned, or they reference a leaf/node with the
information so that it's only stored once and deduped."

The seed has no home for a procedure that runs only on its own tree. The
release flow sits in the body of `CLAUDE.md`, which every seed session loads.
The two machinery homes both ship: `install.sh` places every
`skills/*/SKILL.md` and every `protocols/*.md` into every plant, and
`tests/seed-lint.py`'s `check()` requires each of them in `manifest.json`.
`tools/prepare-release.py` stays home only because `manifest.json`'s `tools`
map leaves it out, and no check holds that. The same map and the installer's
tool placements agree today, and no check holds those together either.

## Decision

A procedure that runs only on the seed's own tree lives under `docs/skills/`
with `origin: seed-only`, and `tests/seed-lint.py`'s
`check_seed_only_stays_home` holds every seed-only file out of `manifest.json`
and `install.sh` and holds the manifest's `tools` map equal to the tools the
installer places.

## Consequences

- The release skill, `docs/skills/seed-release.md` (`skill.seed-release`), is
  the first file there. It runs once at the end of a round and enters the
  steward plant's canonize as its close-out step, so `protocols/canonize.md`
  gets no edit. `CLAUDE.md` `## Release` becomes a pointer to it.
- The check's `SEED_ONLY` tuple names `tools/prepare-release.py` and
  `docs/skills/seed-release.md`. A new seed-only file joins the tuple in the
  change that adds it.
- `install.sh` reads no `$SEED_ROOT/docs` path, and the check fails the day it
  starts to. A move of the skill into `skills/` fails `check()` first, for the
  missing catalog entry, and this check second.
- `docs/skills` joins the agnosticism scan, because seed text carries no
  session residue and no path outside the seed.
- A plant that wants the procedure at hand (the owner's plant) carries a
  pointer node with `origin: project`, authored through its own canonize. The
  seed file stays the one home.
- Contract: SPEC-0001 `SEED_ONLY_FILES_NEVER_PLACED`. Tests that fail if this
  is reversed: its rows in `tests/test-seed-lint.sh`.

## Alternatives considered

- **`skills/seed-release/SKILL.md`.** Rejected: `place_graph_machinery` places
  every `skills/*/SKILL.md` into every plant, and `check()` requires the
  manifest catalog entry, so the procedure would ship.
- **`protocols/seed-release.md`.** Rejected for the same reason:
  `install.sh` places the whole `protocols/` tree.
- **The body of `CLAUDE.md`.** Rejected: every seed session pays for it, and
  the procedure grows with the inventory of doc surfaces it keeps current.
- **`.claude/skills/` in the seed.** Rejected: the seed's `.gitignore` excludes
  `.claude/`.
- **A home in the owner's plant only.** Rejected: the procedure edits the seed
  tree and names seed checks, and a plant copy drifts from them. The owner's
  words make the plant the convenient copy ("on this plant for convenience").
- **A copy or a symlink in the plant.** Rejected: a copy is a second home. A
  symlink pins the main checkout while a round runs in a worktree, and the
  plant's `graph-lint.py` would lint a seed file as a plant node.

## Reversibility

`reversible`: one file moves, and one check and one tuple change with it.

## References

- Spec: SPEC-0001 `SEED_ONLY_FILES_NEVER_PLACED`
- `CLAUDE.md` `## Release` and "Canonical homes"
- Owner rulings D1 and D2 of 7.35.0, kept with the round's working records
  outside the seed
