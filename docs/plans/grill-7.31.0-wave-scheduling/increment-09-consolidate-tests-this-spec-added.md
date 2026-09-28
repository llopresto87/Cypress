### Increment 9 — Consolidate the tests this spec added
- Spec contracts: SPEC-0005/GRILL_WAVES_LEVELS_FROM_DEPENDS_ON, SPEC-0005/GRILL_WAVES_OVERLAP_IS_A_WARNING, SPEC-0005/GRILL_WAVES_UNSCHEDULED_WITHOUT_PHASE, SPEC-0005/GRILL_WAVES_NOT_COMPUTED_ON_DEPENDENCY_DEFECT, SPEC-0005/GRILL_WAVES_LEAVES_THE_GATE_UNCHANGED
- Files touched: `tests/test-grill-lint.sh`, the helpers increment 1 added under `tests/fixtures/grill/`; (M1:) `tests/test-seed-lint.sh` and `tests/test-plant-state.sh`, only the cases increment 10 and 11 added
- Tests to write (RED): none — consolidation
- Behavior added: none; survey the wave cases against case 1 (`--list`) and case 14 (the ledger form) and against any cases ruling pass 2 adds for mutation survivors, rule on each overlap, then merge or delete under `skill.test-first`. (M1:) Survey increment 10's planted-violation case against the existing §3.1–§3.8 heading case, and increment 11's case against `case_plan_records`, and do the same
- Gate: the suite stays green, no contract loses its test, and every §10 row still binds to its label
- Rollback path: revert the consolidation commit
- Effort: low
- Phase: RED (a tester lane; the suite stays green)
- Depends on: increment 5, increment 12, increment 13
