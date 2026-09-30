<!-- Increment 16 of `docs/plans/grill-7.35.0-positive-voice.md`; its §9 index row points here. -->

### Increment 16: RED: the opencode projection reads the model map, and --check compares it
- Item: ADR-0022 and session ruling S1: the map template is placed, the opencode projection writes its `model:` line from the map or none, an unreadable map fails closed, and `install.sh opencode --check` reports drift, the `model:` line included
- Spec contracts: SPEC-0001/MODEL_MAP_TEMPLATE_IS_PLACED (E7, a guard), SPEC-0001/OPENCODE_MODEL_FROM_MAP (E8), SPEC-0001/OPENCODE_NO_MAP_ROW_NO_MODEL_LINE (E9), SPEC-0001/OPENCODE_MAP_UNREADABLE_FAILS_CLOSED (E10), SPEC-0001/OPENCODE_CHECK_DETECTS_DRIFT (E11), SPEC-0001/CHECK_WITHOUT_COPILOT_SAYS_SO (D3, a guard edit), SPEC-0001/SYMLINK_MODE_IS_UNIFORM (M9, a companion edit)
- Files touched: `tests/test-full-install.sh` (E7 to E11), `tests/test-install-placement.sh` (`is_generated` gains `.opencode/agents/*`), `tests/test-install-adoption.sh` (D3's second arm installs `claude-code codex` instead of `all codex`)
- Tests to write (RED): E7 to E11 as SPEC-0001 §10 states them; E8 includes a plant agent with `model: haiku`, E9 one with `model: inherit`, E11 a hand edit, a cell edit with no re-run, `all --check`, a digest of the plant around every run, and a broken map. Observed red: E8 to E11 fail on the unmodified installer (verbatim projection, no map log line, no map read, `--check` checks only Copilot); E7, D3 and the M9 edit pass before and after
- Behavior added: none (tests only)
- Gate: `bash tests/test-full-install.sh`: E8 to E11 fail by label, every other case green; `bash tests/test-install-adoption.sh` and `bash tests/test-install-placement.sh` green
- Rollback path: drop E7 to E11, and restore D3's setup and the M9 list
- Effort: medium
- Phase: RED
- Depends on: increment 3, increment 10
