### Increment 2 — RED: the rule home of `delegation.waves`
- Spec contracts: SPEC-0005/ADOPTED_RULE_HOMES
- Files touched: `tests/seed-lint.py` (one entry in `ADOPTED_RULE_HOMES`: `"delegation.waves": "core/method/delegation-sequencing.md"`, and nothing else)
- Tests to write (RED): no new case. The entry is the assertion, and the existing generic cases X347 and X348 hold the check itself. Observed red: `python3 tests/seed-lint.py` reports `delegation.waves: not owned by core/method/delegation-sequencing.md`
- Behavior added: none
- Gate: seed-lint's only new finding is that line, compared with a baseline run on a scratch copy of the file (copy and `diff`; never `git stash`). (R0.4:) while the entry is carried, `tests/test-seed-lint.sh` fails its clean-copy baseline and runs no case. Each tip records the baseline line as expected-red and the rest of that script as `not run`, in words, until increment 6 commits
- Rollback path: drop the entry
- Effort: low
- Phase: RED
- Depends on: none
