<!-- Increment 39 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 39: GREEN: the installer places the code-anchor tool
- Item: F (class I)
- Spec contracts: SPEC-0001/CODE_ANCHOR_TOOL_IS_PLACED
- Files touched: `install.sh` (one `place_file` line beside the status register's, with its comment)
- Tests to write (RED): none new: increment 17's cases
- Behavior added: every plant has the tool the hooks call
- Gate: `bash tests/test-full-install.sh` green; `bash tests/test-install-placement.sh` green. seed-lint's manifest catalog may name the new placed tool as missing from `manifest.json`; that line is expected-red, attributed to increment 52
- Rollback path: revert the line
- Effort: low
- Phase: GREEN
- Depends on: increment 17, increment 30, increment 38
