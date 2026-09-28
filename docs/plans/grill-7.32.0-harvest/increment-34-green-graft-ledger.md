<!-- Increment 34 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 34: GREEN: the graft ledger tool
- Item: T1 and T2 (class S)
- Spec contracts: none: contained, as increment 10
- Files touched: `tools/graft-ledger.py` (new; stdlib; it walks the plant through the shared walk of increment 32)
- Tests to write (RED): none new: increment 10's cases
- Behavior added: the three-way table and the base are printed, not worked out
- Gate: `bash tests/test-graft-tools.sh` green on increment 10's labels; `bash tests/test-tool-help.sh` green
- Rollback path: delete the new file
- Effort: medium-hard
- Phase: GREEN
- Depends on: increment 10, increment 32
