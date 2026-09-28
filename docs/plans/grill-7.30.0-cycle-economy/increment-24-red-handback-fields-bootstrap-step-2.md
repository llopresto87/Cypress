### Increment 24 — RED: handback fields, bootstrap step 2, pending phrases
- Spec contracts: SPEC-0005/HANDBACK_CARRIES_EFFORT_AND_EXPERTISE_GAP, SPEC-0005/BOOTSTRAP_STEP2_LOADS_A_MENU, SPEC-0005/ADOPTED_RULES_NOT_PENDING
- Files touched: `tests/test-seed-lint.sh`, `tests/check-coverage-binder.py`
- Tests to write (RED): the §10 rows for the three contracts; the step-2 plant rewords all six copies alike and greps the fragment unique to the new check
- Behavior added: none (tests only)
- Gate: the planted cases fail on the missing checks; the rewrap guard passes
- Rollback path: drop the cases
- Effort: low
- Phase: RED
- Depends on: none
