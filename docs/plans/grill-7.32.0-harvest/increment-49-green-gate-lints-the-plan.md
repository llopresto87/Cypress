<!-- Increment 49 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 49: GREEN: the gate lints the active round plan
- Item: G3 (class S), the gate half
- Spec contracts: none: gate wiring; no spec owns `tests/run.sh`
- Files touched: `tests/run.sh` (one variable naming the active plan, one `add_step` running `templates/knowledge-graph/grill-lint.py --plan` on it with `--specs docs/specs --decisions docs/decisions`), `tools/gate-registry.py` (one entry: what the step reads and what it misses: every other plan)
- Tests to write (RED): the new step itself: it is observed red before this plan's pending references are all promoted and green after
- Behavior added: the seed's plan of record is checked on every gate run
- Gate: `bash tests/run.sh` shows the step green; `python3 tools/gate-registry.py --lint` PASS; `python3 tests/test_gate_registry.py` green
- Rollback path: revert the two lines and the entry
- Effort: low
- Phase: GREEN
- Depends on: increment 25, increment 26, increment 29, increment 31, increment 36, increment 37, increment 38, increment 39, increment 40
