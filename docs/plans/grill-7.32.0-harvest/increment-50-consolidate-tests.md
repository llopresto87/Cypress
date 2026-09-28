<!-- Increment 50 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 50: Consolidate the tests this round added
- Item: the consolidation increment of `grill.increment-shape`
- Spec contracts: SPEC-0001/PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION, SPEC-0001/RECREATED_LIST_IS_COMPLETE, SPEC-0001/UNKNOWN_STAMP_KEYS_SURVIVE, SPEC-0001/CODE_ANCHOR_TOOL_IS_PLACED, SPEC-0001/EVERY_BACKUP_IS_CLASSIFIABLE, SPEC-0003/ANCHOR_NAMES_PATHS_WHEN_THE_COMMIT_MOVED, SPEC-0003/ANCHOR_NAMES_NEW_UNCOMMITTED_WORK
- Files touched: `tests/test-graft-tools.sh`, `tests/test-bound-hook.sh`, `tests/test-grill-lint.sh`, `tests/test-install-kernel-modes.sh`, `tests/test-install-adoption.sh`, `tests/test-plant-state.sh`, `tests/test-full-install.sh` (the cases this round added and the older cases they overlap; the older `set -e` cases of `tests/test-graft-tools.sh` move into the collecting pattern, the candidate 7.31.0 recorded)
- Tests to write (RED): none: consolidation
- Behavior added: none; survey the round's tests and their overlaps, rule on each, then merge or delete under `skill.test-first`
- Gate: the suite stays green and no contract loses its test; `spec-lint.py` coverage unchanged
- Rollback path: revert the consolidation commit
- Effort: medium-low
- Phase: RED
- Depends on: increment 26, increment 27, increment 28, increment 33, increment 35, increment 41, increment 49
