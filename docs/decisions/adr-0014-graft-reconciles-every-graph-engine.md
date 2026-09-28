---
status: accepted
status_date: 2026-09-28
owner: seed steward
---

# ADR-0014: graft reconciles every graph engine, with the config each one carries; the installer keeps engines plant-owned

## Status

See frontmatter, which is the single home. Filed 2026-09-28 for 7.31.0, planned in
[`../plans/grill-7.31.0-wave-scheduling.md`](../plans/grill-7.31.0-wave-scheduling.md)
(§6 rows P1 to P4, §9 increments 15 to 18). The owner asked for the change, and the
design latitude is the round's (balanced), so it is filed `accepted`. It supersedes no
earlier ADR.

## Date

2026-09-28

## Context

The owner asked that new and existing plants both pick up what 7.31.0 ships:

> "please remember to update the graft and growht/install protocol as needed for a new
> /old plant to pick up our changes"

A fresh install places everything 7.31.0 ships, `grill-lint.py --waves` included. An
existing plant receives almost all of it through graft's installer re-run. Seed-owned
nodes, the kernel, the Prime Agent overlay and the template tree fast-forward with a
backup, and the new session-record form is added because it is missing. One file does
not arrive: `docs/graph/grill-lint.py`.

- The installer places the three graph engines (`graph-lint.py`, `spec-lint.py`,
  `grill-lint.py`) add-if-missing (`install.sh`, `place_graph_scaffold`), because a
  plant owns them once they are placed. Graft's Phase 3 reconciles them with
  `tools/graft-graph-engine.py`, a config-preserving fast-forward with a backup.
- `protocols/graft.md` names only `graph-lint.py` and `spec-lint.py` for that
  reconciliation, in its ownership list and in Phase 3.
- `tools/graft-graph-engine.py` defaults `--preserve` to `ROOT_ID,KINDS,KIND_PREFIX` and
  refuses (exit 2) when the seed engine lacks one of them. So, run without a hand-picked
  `--preserve`, it refuses `grill-lint.py`, which carries no config. It also refuses
  `spec-lint.py`, whose config is `TEST_GLOBS`, and graft names no flag for it.
- `tools/graft-audit.py --engine` keeps only the last value it is given. Graft's engine
  gate checks `graph-lint.py` alone, so a stale `grill-lint.py` is reported nowhere.

The mechanism exists. What is broken is its reach: which engines graft names, the
default config the tool assumes, and the audit's single pair.

## Decision

The installer keeps the three engines plant-owned (add-if-missing, real files under
`--symlink`). Graft carries every engine to an existing plant through
`tools/graft-graph-engine.py`. With no `--preserve`, the tool takes the config set that
belongs to the engine it is given:
- `graph-lint.py`: `ROOT_ID`, `KINDS`, `KIND_PREFIX`;
- `spec-lint.py`: `TEST_GLOBS`;
- `grill-lint.py`: none;
- any other name: the `graph-lint.py` set, which is today's default.

`tools/graft-audit.py` checks every `--engine` pair it is given. `protocols/graft.md`
names all three engines in its ownership list, in Phase 3 and in its engine and
customization gates. SPEC-0001 covers the engine reconciliation, the one write the
seed's graft tools make into a plant's placed engines.

## Consequences

- An existing plant gets `grill-lint.py --waves` at its next graft, with its old engine
  backed up. A plain re-install still leaves the engines alone, because upgrading an
  existing plant is graft's job and graft is the owner's to start.
- `spec-lint.py` reconciliation stops refusing. That was a latent defect of the same
  path, fixed by the same default.
- A plant that customized an engine is protected as before. Graft-audit classifies the
  backup (the plant-signal check marks it CUSTOMIZED), and the tool reports KEEP-PLANT
  when the plant engine is a strict superset of the seed's.
- SPEC-0001's scope gains the engine reconciliation and the audit's engine check. Graft
  as a whole stays out of scope.
- Tests that fail if this is silently reversed:
  - `tests/test-graft-tools.sh`: the per-engine default and the repeated `--engine`;
  - `tests/test-plant-state.sh`: an installed plant with an older `grill-lint.py` is
    left alone by a re-install and brought current, `--waves` included, by the engine
    reconciliation.
- No installer code changes, and SPEC-0001's `SINGLE_WRITER` census is unchanged.

## Alternatives considered

- **The installer fast-forwards `grill-lint.py`, because it carries no config.** This is
  rejected. It would create a third placement policy: a copy-mode fast-forward, since
  `grill-lint.py` resolves the plan, the specs and the decisions beside its own resolved
  path and so cannot be a link into the seed. It would also move one engine out of the
  plant-owned class that SPEC-0001's link-uniformity exception list and graft's
  engine-vs-instance rule both rely on. And it would leave the refusal on `spec-lint.py`.
- **Document `--preserve=` for each engine in `graft.md` and change no tool.** This is
  rejected. It keeps a tool whose default refuses two of the three engines, and an audit
  that silently drops all but one `--engine` pair. A steward who follows the protocol
  loosely would still get a stale engine and a clean report.
- **A new spec for the graft tools.** This is rejected. Seed-lint refuses a seed spec in
  `draft`, and the reconciliation is placement of seed files into a plant, which is
  SPEC-0001's subject. That spec already contracts graft-audit's classification of
  install backups.
- **A version-aware or hash-aware replace of every seed-owned engine at install.** This
  is rejected as new machinery. The existing config-preserving reconciliation already
  handles plant config and plant-ahead engines.

## Reversibility

`reversible until tagged`. The tool defaults and the audit's pairs are small code
changes, and the protocol text is prose. After v7.31.0 is tagged, plants grafted with it
carry the reconciled engines, and their backups keep the old bodies.

## References

- Spec: [SPEC-0001](../specs/SPEC-0001-install-placement.md) (`ENGINE_RECONCILE_PICKS_CONFIG_BY_ENGINE`, `ENGINE_AUDIT_CHECKS_EVERY_PAIR`, `EXISTING_PLANT_RECEIVES_CURRENT_ENGINES`, as amended for 7.31.0)
- Grill: [`../plans/grill-7.31.0-wave-scheduling.md`](../plans/grill-7.31.0-wave-scheduling.md) §6 P1–P4, §9 increments 15–18
- Code: `install.sh` (`place_graph_scaffold`), `tools/graft-graph-engine.py`, `tools/graft-audit.py`, `protocols/graft.md` (Phase 3; `graft.gate.engine`, `graft.gate.customization`)
- Related: [ADR-0013](adr-0013-harness-memory-is-not-a-home.md) (the session record, which graft's memory migration fills)
