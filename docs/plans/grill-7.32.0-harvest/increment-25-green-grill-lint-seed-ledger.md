<!-- Increment 25 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 25: GREEN: grill-lint reads a plan's ledger beside it and takes its spec and decision homes from flags
- Item: G3 (class B)
- Spec contracts: none: contained, as increment 2
- Files touched: `templates/knowledge-graph/grill-lint.py` (the ledger home becomes the directory beside the plan named for its stem; an index row's path ends `<stem>/<file>.md`; `--specs DIR` and `--decisions DIR`, read the way the other flags are; the docstring's usage lines; nothing else)
- Tests to write (RED): none new: increment 2's cases
- Behavior added: a seed round plan lints in place; a plant's default layout is unchanged
- Gate: `bash tests/test-grill-lint.sh` green, increment 2's hashes unchanged; `python3 tools/gate-registry.py --summary` classifies every step
- Rollback path: revert the file
- Effort: medium
- Phase: GREEN
- Depends on: increment 2
