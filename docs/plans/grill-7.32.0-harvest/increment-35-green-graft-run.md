<!-- Increment 35 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 35: GREEN: the graft run driver
- Item: T3 (class S)
- Spec contracts: none: as increment 11
- Files touched: `tools/graft-run.py` (new; stdlib; it runs the installer, the engine tool, the audit, the graft ledger and growth-audit's plan mode against the stage only, and writes nothing else)
- Tests to write (RED): none new: increment 11's cases
- Behavior added: one command runs the mechanical half of a graft on a stage and prints the gate table; the judgment gates stay with the protocol
- Gate: `bash tests/test-graft-tools.sh` green; `bash tests/test-tool-help.sh` green
- Rollback path: delete the new file
- Effort: hard
- Phase: GREEN
- Depends on: increment 11, increment 32, increment 34
