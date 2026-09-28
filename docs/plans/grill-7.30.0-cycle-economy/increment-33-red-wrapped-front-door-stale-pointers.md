### Increment 33 — RED: wrapped and front-door stale pointers
- Spec contracts: SPEC-0005/ADOPTED_RULE_HOMES
- Files touched: `tests/test-seed-lint.sh` (X356 `case_ce_stale_pointer_wrapped`: `docs/graph/method/delegation.md` at the end of one line and `delegation.lanes` at the start of the next; X357 `case_ce_stale_pointer_front_door`: the stale pointer planted in `README.md`, `INSTALL.md` and a `documentation/` page), `tests/check-coverage-binder.py` (the stale "expected RED" comment at :68-77), `tests/fixtures/front-door/` (any fixture line the widened scan would flag, repointed to `docs/graph/method/delegation-bounds.md`, with the fixture hashes re-recorded)
- Tests to write (RED): X356, X357
- Behavior added: none (tests only)
- Gate: X356 and X357 fail on the current check; every other case passes
- Rollback path: drop the cases; restore the comment and the fixture lines
- Effort: medium
- Phase: RED
- Depends on: increment 25
