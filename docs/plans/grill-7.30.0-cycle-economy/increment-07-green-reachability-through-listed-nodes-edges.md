### Increment 7 — GREEN: reachability through listed nodes' edges
- Spec contracts: SPEC-0005/LISTED_NODE_EDGES_REACH
- Files touched: `templates/knowledge-graph/graph-lint.py` (`check_reachability()` rooted branch follows index-listed nodes' edges)
- Tests to write (RED): none new; increment 2's cases for this contract
- Behavior added: a node reached by an edge from an index-listed node is reachable; islands still fail
- Gate: `python3 -m unittest tests.test_graph_lint`; cross-cutting: `python3 tests/seed-lint.py`, the install test that lints an installed graph
- Rollback path: revert
- Effort: medium-low
- Phase: GREEN
- Depends on: increment 2, increment 6
