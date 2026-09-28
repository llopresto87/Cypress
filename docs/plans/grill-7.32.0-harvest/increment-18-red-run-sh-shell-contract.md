<!-- Increment 18 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 18: RED: seed-lint fails when tests/run.sh drops its shell contract
- Item: D4b (class S), decision 4
- Spec contracts: none: contained; seed-lint's checks are seed-only. Why: dropping `-u` or `pipefail` from `tests/run.sh` would turn a red gate into a clean exit and nothing would say so
- Files touched: `tests/test-seed-lint.sh` (one planted-violation case only)
- Tests to write (RED): in a scratch copy of the tree, remove `pipefail` from the `set -euo pipefail` line of `tests/run.sh`, then remove `-u`, then move the line below the first `add_step`; each time seed-lint names `tests/run.sh` and the missing flag. Observed red: seed-lint passes all three today
- Behavior added: none (tests only)
- Gate: `bash tests/test-seed-lint.sh` red on the new case only; its clean-copy baseline stays green
- Rollback path: drop the case
- Effort: low
- Phase: RED
- Depends on: increment 1
