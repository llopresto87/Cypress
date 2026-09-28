### Increment 39 — GREEN: the widened, wrap-joined stale-pointer scan
- Spec contracts: SPEC-0005/ADOPTED_RULE_HOMES
- Files touched: `tests/seed-lint.py` (`check_adopted_rule_homes`: each line read joined with the next; roots widened per SPEC-0005 §4)
- Tests to write (RED): none new; increment 33's cases
- Behavior added: a wrapped pointer, or one in a front-door or documentation file, is caught
- Gate: `bash tests/test-seed-lint.sh`; `python3 tests/check-coverage-binder.py .`; `python3 tests/seed-lint.py` on the real tree (increment 35 must have landed; a finding outside `tests/seed-lint.py` is a question)
- Rollback path: revert
- Effort: medium
- Phase: GREEN
- Depends on: increment 33, increment 35
