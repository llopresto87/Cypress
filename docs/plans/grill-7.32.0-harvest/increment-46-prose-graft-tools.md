<!-- Increment 46 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 46: Prose: graft points at the tools that now do its mechanical steps
- Item: T1, T2, T3, C1 and D2 in graft (class P)
- Spec contracts: none: protocol prose accepted by review
- Files touched: `protocols/graft.md` (Phase 1 prints the base with `tools/graft-ledger.py --base`; Phases 2 and 3 read the ledger's classes, HARVESTED included, instead of classifying by hand; the customization gate passes `--base`; `graft.gate.recreated-nodes` reads `.cypress/recreated-nodes.txt`; a pointer to `tools/graft-run.py` for the staged run, keeping every judgment gate and the ratification in the protocol)
- Tests to write (RED): none: prose
- Behavior added: a graft runs its mechanical steps by command
- Gate: `python3 tests/seed-lint.py` PASS (lifecycle body ceiling); prose-lint against a scratch-copy baseline; reviewer checks no judgment gate moved into a tool
- Rollback path: revert the file
- Effort: medium
- Phase: prose
- Depends on: increment 20, increment 32, increment 34, increment 35, increment 37
