### Increment 23 — RED: rule homes and stale pointers
- Spec contracts: SPEC-0005/ADOPTED_RULE_HOMES
- Files touched: `tests/test-seed-lint.sh` (`case_ce_home_*`, `case_ce_stale_pointer`; and, ruling pass 1, one comment line `# X3NN <SLUG>` in each batch-1 shell case per SPEC-0005 §10, X336 to X346, plus X347 to X355 on this batch's own cases), `tests/check-coverage-binder.py`
- Tests to write (RED): the §10 rows for ADOPTED_RULE_HOMES and STALE_POINTER
- Behavior added: none (tests only)
- Gate: the planted cases fail on the missing check
- Rollback path: drop the cases
- Effort: medium
- Phase: RED
- Depends on: none
