<!-- Increment 27 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 27: GREEN: the ledger verification tool
- Item: D5 (class S)
- Spec contracts: none: contained, as increment 4
- Files touched: `tools/verify-ledger.py` (new; stdlib; `--help` in the shape `tests/test-tool-help.sh` holds)
- Tests to write (RED): none new: increment 4's cases
- Behavior added: a ledger conversion is proven byte for byte, and a mismatch names its leaf and offset
- Gate: `bash tests/test-grill-lint.sh` green; `bash tests/test-tool-help.sh` green
- Rollback path: delete the new file
- Effort: medium-low
- Phase: GREEN
- Depends on: increment 4
