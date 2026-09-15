# Slice 1 — `from-scratch` absorbs its bootstrap and owns its entry

**Status:** implemented 2026-09-14, gate green.
**Depends on:** nothing. **Blocks:** slice 2, which routes to this protocol and
must not route to it before its entry conditions are correct.

## Why

Two defects, one file.

1. **The Phase 2 circularity** (evidence E5). Phase 2 runs `install.sh`, but the
   documented route reaches this protocol only *after* installing. The phase
   order assumes an entry the installer does not create.
2. **`from-scratch-bootstrap` is the thinnest split in the roster** — 680 tokens,
   one owned fact, under a 1 500-token protocol that already owns
   `from-scratch.phases`. The protocol/skill split elsewhere separates a workflow
   from a technique; here the skill's share is *"the honesty"*, which is a
   posture, not a technique.

Slice 2 needs an entry section to point at. Writing one is the natural moment to
absorb the skill, because the honesty discipline **is** entry material: it is
what stops phase 2 being declared done when a skeleton was created and nothing
runs.

## What changes

| File | Change |
|---|---|
| `protocols/from-scratch.md` | new `## Entry` section before the phase table: preconditions, the three entry routes (installer fork, `/initialize`, direct), and the absorbed honesty discipline. Phase 2 becomes **verify-then-install**, idempotent |
| `skills/from-scratch-bootstrap/SKILL.md` | **deleted.** `from-scratch-bootstrap.method` is re-homed into `from-scratch.entry` |
| `manifest.json` | skill entry removed; skill count follows |
| `install.sh` | placement line for the skill removed |
| `core/AGENTS.md` | nothing in this slice (slice 2 owns the kernel edit) |
| `documentation/skills-and-templates-reference.md` | skill section removed |
| `README.md` | skill named in the roster list — follows |
| `protocols/brainstorm.md`, `skills/brainstorm-socratic/SKILL.md` | `peers:` drop `skill.from-scratch-bootstrap` where declared |
| `agents/*`, `skills/adopt-existing/SKILL.md` | any `skill.from-scratch-bootstrap` edge re-pointed at `protocol.from-scratch` |

## The Phase 2 rewrite, precisely

Today Phase 2 says "create the project skeleton" and describes `install.sh`
dropping the overlay. After:

- **If `docs/graph/` and the kernel are already present** (the installer fork
  route, which is now the documented one), Phase 2 **verifies** the skeleton
  against the same tree it would have created, records what is present, and does
  not re-run the installer.
- **If they are absent** (direct entry), Phase 2 runs `install.sh` as it does
  today.
- Either way the phase exits on the same postcondition, so the phase table, the
  `Needs` column and every later phase are untouched.

`install.sh` is already idempotent and recoverable — the gate asserts "376
destinations recoverable, symlink-safe, idempotent, link-uniform" — so this is a
statement of what already happens, not new mechanism.

## Contract

`AN_INSTALLED_SEED_DOES_NOT_REINSTALL_ITSELF` — entering `from-scratch` on a
tree that already carries the kernel and `docs/graph/` completes Phase 2 without
invoking `install.sh`, and reports the skeleton as verified rather than created.

## Regression, observed RED first

`tests/test-entry-paths.sh` (new):

1. a tree with kernel + `docs/graph/` present — from-scratch's Phase 2 text must
   name the verify branch, and must not present installing as unconditional;
2. `skills/from-scratch-bootstrap/` is gone and nothing references it — no
   `skill.from-scratch-bootstrap` edge resolves anywhere, no manifest entry, no
   `install.sh` placement, no reference-page section;
3. `from-scratch.entry` is owned exactly once across the tree.

RED is observed by running 1–3 before the edit: (2) and (3) fail on the current
tree because the skill exists and `from-scratch.entry` does not.

## Risk

**Deleting a node is the only irreversible-feeling move in this plan.** It is
`origin: seed` machinery, so no plant owns a customization of it; a grafted plant
re-receives the roster and loses a node it never edited. The content is not lost
— it moves into `from-scratch`'s entry section in the same commit, and the
absorbed text is quoted in this record.

`seed-lint`'s `owns` uniqueness check is what proves the fact moved rather than
duplicated.
