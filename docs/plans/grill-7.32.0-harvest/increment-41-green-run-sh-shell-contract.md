<!-- Increment 41 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 41: GREEN: seed-lint holds tests/run.sh to its shell contract
- Item: D4b (class S)
- Spec contracts: none: contained, as increment 18
- Files touched: `tests/seed-lint.py` (one check, called from `main`)
- Tests to write (RED): none new: increment 18's case
- Behavior added: a gate that stops failing because its flags were dropped is caught
- Gate: `bash tests/test-seed-lint.sh` green; `python3 tests/seed-lint.py` PASS
- Rollback path: revert the check
- Effort: low
- Phase: GREEN
- Depends on: increment 18
