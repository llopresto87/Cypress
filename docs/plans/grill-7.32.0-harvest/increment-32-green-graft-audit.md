<!-- Increment 32 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 32: GREEN: graft-audit without the four false alarms, and one shared walk
- Item: C1 to C4 (class S)
- Spec contracts: SPEC-0001/EVERY_BACKUP_IS_CLASSIFIABLE
- Files touched: `tools/graft-audit.py` (`--base`, the engine signal check, the plant-owned projection class, the pruned walk), `tools/plant_walk.py` (new: the walk that skips symlinked directories and any directory holding its own `.cypress/seed.json`; one responsibility, two callers today)
- Tests to write (RED): none new: increment 9's cases
- Behavior added: a graft audit reports only what a steward must act on
- Gate: `bash tests/test-graft-tools.sh` green on increment 9's labels; its other new labels stay red until their GREEN; `bash tests/test-install-placement.sh` green (the M8 audit-totality case)
- Rollback path: revert `tools/graft-audit.py`, delete `tools/plant_walk.py`
- Effort: medium-hard
- Phase: GREEN
- Depends on: increment 9
