### Increment 4 — RED: the leaf ceiling ledger
- Spec contracts: SPEC-0005/LEAF_BODY_CEILING_HELD
- Files touched: `tests/test-seed-lint.sh` (`case_ce_leaf_*`), `tests/check-coverage-binder.py` (`COVERED` for `check_leaf_body_ceiling`)
- Tests to write (RED): the §10 rows for LEAF_BODY_CEILING_HELD, LEDGER_REGROWS and SIBLING_OVER_CEILING; at RED the constant is absent, so each case fails with an explicit "check missing" message, never a traceback
- Behavior added: none (tests only)
- Gate: the planted cases fail on the missing check; the binder fails naming the check (an expected RED id)
- Rollback path: drop the cases and the binder entry
- Effort: medium
- Phase: RED
- Depends on: none
