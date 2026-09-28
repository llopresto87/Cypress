### Increment 16 — RED: an existing plant receives the current engines through graft
- Spec contracts: SPEC-0001/EXISTING_PLANT_RECEIVES_CURRENT_ENGINES
- Files touched: `tests/test-plant-state.sh`: one new case, `case_engine_upgrade`, called after every existing case (after increment 11's `case_session_records`), in its own `mktemp -d` target
- Tests to write (RED): install `claude-code`, then overwrite `docs/graph/grill-lint.py` with an older body (the seed copy with every line containing `waves` removed). Re-run `install.sh claude-code`: `docs/graph/grill-lint.py` is unchanged (the engines stay plant-owned). Run `tools/graft-graph-engine.py` with no `--preserve` over each of the three engines: every run exits 0; `docs/graph/grill-lint.py` is byte-identical to the seed's; one `.bak-*` holds the older body; `python3 docs/graph/grill-lint.py --waves` prints a line starting `waves:`; and `tools/graft-audit.py <plant> <seed>` with the three `--engine` pairs reports every engine current. Observed red: the reconciliation of `grill-lint.py` exits 2
- Behavior added: none (tests only)
- Gate: `bash tests/test-plant-state.sh` runs every existing case green and fails only on the new case's label
- Rollback path: drop the case
- Effort: medium-low
- Phase: RED
- Depends on: increment 12
