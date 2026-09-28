<!-- Increment 15 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 15: RED: the stamp keeps keys the installer does not own
- Item: D2s (class I), decision 2
- Spec contracts: SPEC-0001/UNKNOWN_STAMP_KEYS_SURVIVE (promoted in this commit, with the failure STAMP_NOT_AN_OBJECT, the §6 rule and a §10 row)
- Files touched: `tests/test-plant-state.sh` (one new last case only), `docs/specs/SPEC-0001-install-placement.md` (the promotion, §6, §7, §10 row)
- Tests to write (RED): a stamp with a string key and an object key the installer does not own survives `install.sh all` with JSON-equal values, in order, after the installer's keys; a stamp that is not a JSON object is moved to a backup and one warning names it. Observed red: the keys are dropped
- Behavior added: none (tests and the spec promotion)
- Gate: `bash tests/test-plant-state.sh` red on the new case only
- Rollback path: drop the case and move the headings back
- Effort: medium-low
- Phase: RED
- Depends on: increment 1
