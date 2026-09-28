<!-- Increment 43 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 43: Prose: grow removes the pre-growth block and names why it establishes facts
- Item: 8a and R5 (class P)
- Spec contracts: none: protocol prose accepted by review
- Files touched: `protocols/grow.md` (the phase that sets `grown: true` removes the pre-growth block; the completeness contract names its purpose: grow establishes these facts so no later session has to)
- Tests to write (RED): none: prose
- Behavior added: a grown index carries no pre-growth block, and grow's purpose is stated where its contract is
- Gate: `python3 tests/seed-lint.py` PASS (lifecycle body ceiling); prose-lint against a scratch-copy baseline
- Rollback path: revert the file
- Effort: low
- Phase: prose
- Depends on: increment 40
