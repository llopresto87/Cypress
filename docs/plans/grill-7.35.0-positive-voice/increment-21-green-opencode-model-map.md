<!-- Increment 21 of `docs/plans/grill-7.35.0-positive-voice.md`; its §9 index row points here. -->

### Increment 21: GREEN: install.sh projects opencode agents from the map and checks them
- Item: the installer change increment 16 fails on
- Spec contracts: SPEC-0001/OPENCODE_MODEL_FROM_MAP, SPEC-0001/OPENCODE_NO_MAP_ROW_NO_MODEL_LINE, SPEC-0001/OPENCODE_MAP_UNREADABLE_FAILS_CLOSED, SPEC-0001/OPENCODE_CHECK_DETECTS_DRIFT
- Files touched: `install.sh`
- Tests to write (RED): none: increment 16 holds them
- Behavior added: `install_opencode` parses the map once (SPEC-0001 §6) and writes each agent projection through `place_generated` with the map's `model:` line or none, and one log line counting the agents with none; the stamp records opencode `verbatim: false`; `--check` renders the same set into its stage and compares it when the run names opencode and the record carries it; the usage text names opencode under `--check`
- Gate: `bash tests/test-full-install.sh`, `bash tests/test-install-placement.sh`, `bash tests/test-install-adoption.sh`, `bash tests/test-plant-state.sh` green; `python3 tests/seed-lint.py` `check_install_write_sites` unchanged (the exception count stays 11)
- Rollback path: revert `install.sh`; a plant re-installed after the revert gets verbatim projections again
- Effort: hard
- Phase: GREEN
- Depends on: increment 16
