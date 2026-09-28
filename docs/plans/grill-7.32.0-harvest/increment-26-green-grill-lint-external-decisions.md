<!-- Increment 26 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 26: GREEN: grill-lint reports qualified decision references as external
- Item: G1 (class B)
- Spec contracts: none: contained, as increment 3
- Files touched: `templates/knowledge-graph/grill-lint.py` (the decision check; the docstring states the bare-number limit)
- Tests to write (RED): none new: increment 3's cases
- Behavior added: `<name>:ADR-NNNN` is reported once as external and never resolved locally
- Gate: `bash tests/test-grill-lint.sh` green
- Rollback path: revert the change
- Effort: medium-low
- Phase: GREEN
- Depends on: increment 3, increment 25
