<!-- Increment 29 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 29: GREEN: graph-lint prints each node's file beside its id
- Item: decision 9 (class B)
- Spec contracts: SPEC-0003/PLAN_ENTRY_NAMES_THE_NODE_FILE, SPEC-0003/ROUTE_HOOK_KEEPS_THE_PATH
- Files touched: `templates/knowledge-graph/graph-lint.py` (the `--plan` printer only; the scoring block that seed-lint holds byte-identical with agent-lint is not touched)
- Tests to write (RED): none new: increment 6's tests
- Behavior added: no session searches for a node file the router already found
- Gate: `python3 tests/test_graph_lint.py` green; `bash tests/test-bound-hook.sh` green; `python3 tests/test_router_reach.py` green
- Rollback path: revert the file
- Effort: medium-low
- Phase: GREEN
- Depends on: increment 6
