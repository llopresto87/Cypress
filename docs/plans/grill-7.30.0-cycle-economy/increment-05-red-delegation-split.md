### Increment 5 — RED: the delegation split
- Spec contracts: SPEC-0005/DELEGATION_SPLIT_INTO_SIBLINGS
- Files touched: `tests/test-seed-lint.sh` (`case_ce_split_*`; the existing `registration-home` case repointed to `core/method/delegation-bounds.md` with an existence guard printing "split not landed"), `tests/check-coverage-binder.py`
- Tests to write (RED): the §10 rows for DELEGATION_SPLIT_INTO_SIBLINGS
- Behavior added: none (tests only)
- Gate: the new cases and the repointed case fail until the split lands
- Rollback path: drop the cases; restore the registration case's path
- Effort: medium
- Phase: RED
- Depends on: none
