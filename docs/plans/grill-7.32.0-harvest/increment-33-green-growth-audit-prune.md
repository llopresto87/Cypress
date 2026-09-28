<!-- Increment 33 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 33: GREEN: growth-audit walks through the shared walk
- Item: C4 (class S)
- Spec contracts: none: contained, as increment 12
- Files touched: `tools/growth-audit.py` (its three walks call `tools/plant_walk.py`)
- Tests to write (RED): none new: increment 12's scenarios
- Behavior added: a nested or symlinked copy is not audited as part of the plant
- Gate: `bash tests/test-growth-audit.sh` green
- Rollback path: revert the file
- Effort: low
- Phase: GREEN
- Depends on: increment 12, increment 32
