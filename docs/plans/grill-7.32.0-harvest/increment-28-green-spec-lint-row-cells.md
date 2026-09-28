<!-- Increment 28 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 28: GREEN: spec-lint checks each table row against its header
- Item: G2 (class B)
- Spec contracts: none: contained, as increment 5
- Files touched: `templates/knowledge-graph/spec-lint.py` (the row parser and one shape check)
- Tests to write (RED): none new: increment 5's cases
- Behavior added: a row with too few or too many cells is a shape defect naming the line
- Gate: `bash tests/test-spec-lint.sh` green; `spec-lint.py --specs docs/specs --root .` finds no row defect in the seed's own specs
- Rollback path: revert the file
- Effort: medium-low
- Phase: GREEN
- Depends on: increment 5
