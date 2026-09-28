<!-- Increment 20 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 20: Prose: graft and harvest carry three small rules
- Item: A3, D6 and D4a (class P), decisions 4 and 6
- Spec contracts: none: protocol prose accepted by review
- Files touched: `protocols/graft.md` (Phase 3: read the plant's operator node at its path before calling a migration optional; the rootstock line: a corrected plant fact is kept as one dated line of history, one sentence; `graft.gate.rootstock`: one sentence on why it uses the narrow porcelain form), `protocols/harvest.md` (G5: the same one sentence for its narrow form)
- Tests to write (RED): none: prose
- Behavior added: a graft reads the plant's recorded standing decisions before it calls a migration optional; a corrected plant fact keeps its history; both gates say why their porcelain form is narrow
- Gate: `python3 tools/prose-lint.py --file` on both files, compared with a baseline from a scratch copy of each; `python3 tests/seed-lint.py` PASS (lifecycle body ceiling); reviewer checks the operator node is named as a seed node kind and not as a plant path
- Rollback path: revert the two files
- Effort: low
- Phase: prose
- Depends on: increment 1
