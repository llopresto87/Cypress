<!-- Increment 37 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 37: GREEN: the installer writes the whole re-created list
- Item: D2 (class I)
- Spec contracts: SPEC-0001/RECREATED_LIST_IS_COMPLETE
- Files touched: `install.sh` (`report_recreated_nodes` and the stamp step: the list file through `place_state`)
- Tests to write (RED): none new: increment 14's cases
- Behavior added: graft's re-created-nodes gate reads a file, not a truncated console
- Gate: `bash tests/test-install-adoption.sh` green; `bash tests/test-install-placement.sh` green; `python3 tests/seed-lint.py` PASS
- Rollback path: revert the change
- Effort: medium-low
- Phase: GREEN
- Depends on: increment 14, increment 36
