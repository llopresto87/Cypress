### Increment 2 — RED: reachability through listed nodes, delegation routing
- Spec contracts: SPEC-0005/LISTED_NODE_EDGES_REACH, SPEC-0005/DELEGATION_LEAVES_ROUTE
- Files touched: `tests/test_graph_lint.py` (`ListedNodeEdgesTests`; `DelegationRoutingTests` on a fresh install, `setUpClass`, with a sibling-exists assertion before reading `load_when`)
- Tests to write (RED): the §10 rows for the two contracts, SIBLING_UNREACHABLE_AFTER_GRAFT and ORPHAN_ISLAND
- Behavior added: none (tests only)
- Gate: the new non-guard cases fail for the missing reachability or the missing siblings; the rest of the file passes
- Rollback path: drop the new classes
- Effort: medium-low
- Phase: RED
- Depends on: none
