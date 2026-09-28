<!-- Increment 38 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 38: GREEN: the installer carries the stamp's other keys
- Item: D2s (class I)
- Spec contracts: SPEC-0001/UNKNOWN_STAMP_KEYS_SURVIVE
- Files touched: `install.sh` (`write_seed_stamp`: read the prior stamp with `python3`, emit the keys it does not own after its own; the not-an-object backup and warning; the comment)
- Tests to write (RED): none new: increment 15's case
- Behavior added: a stamp annotation survives every install
- Gate: `bash tests/test-plant-state.sh` green; `bash tests/test-full-install.sh` green. The mandatory mutation pass covers this change
- Rollback path: revert the function
- Effort: medium
- Phase: GREEN
- Depends on: increment 15, increment 37
