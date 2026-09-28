<!-- Increment 47 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 47: Prose: the 7.30.0 and 7.31.0 plans become ledgers, verbatim
- Item: decision 7 (class S)
- Spec contracts: none: records
- Files touched: `docs/plans/grill-7.30.0-cycle-economy.md` and `docs/plans/grill-7.30.0-cycle-economy/` (new), `docs/plans/grill-7.31.0-wave-scheduling.md` and `docs/plans/grill-7.31.0-wave-scheduling/` (new)
- Tests to write (RED): none new: `tools/verify-ledger.py` is the proof
- Behavior added: the seed's older round plans follow the owner's ledger rule, and no byte of either plan changed meaning or position once rebuilt
- Gate: `python3 tools/verify-ledger.py` exits 0 for each plan against its pre-conversion copy (kept outside the seed); the byte counts it prints are recorded in §15
- Rollback path: revert both plans and delete the two directories
- Effort: low
- Phase: prose
- Depends on: increment 25, increment 27
