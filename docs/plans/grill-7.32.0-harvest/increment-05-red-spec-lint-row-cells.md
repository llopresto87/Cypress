<!-- Increment 5 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 5: RED: spec-lint refuses a table row whose cell count differs from its header
- Item: G2 (class B)
- Spec contracts: none: contained; spec-lint's table parsing is no spec's contract. Why: a §10 row with a missing cell reads its status from the wrong column and nothing says so
- Files touched: `tests/test-spec-lint.sh` (new cases only)
- Tests to write (RED): (a) a fixture spec whose §10 row has one cell fewer than its header fails, and the finding names the spec, the line and both counts; (b) one cell more fails the same way; (c) guard: a cell holding an escaped pipe `\|` counts as one cell; (d) guard: leading and trailing pipes are optional, as GFM allows. Before GREEN, the tester runs the rule from a scratch copy of the linter over the seed's `docs/specs` and, read-only, over one real plant's `docs/graph/specs`, and records the finding count; a count above zero goes to the question file before any GREEN. Observed red: (a) and (b)
- Behavior added: none (tests only)
- Gate: `bash tests/test-spec-lint.sh`: existing cases green, the new non-guard cases red
- Rollback path: drop the new cases
- Effort: medium-low
- Phase: RED
- Depends on: increment 1
