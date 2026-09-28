<!-- Increment 6 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 6: RED: the router prints each node's file beside its id, and the route hook keeps it
- Item: decision 9 (class B)
- Spec contracts: SPEC-0003/PLAN_ENTRY_NAMES_THE_NODE_FILE, SPEC-0003/ROUTE_HOOK_KEEPS_THE_PATH (promoted from the pending block of SPEC-0003 §4 in this increment's commit, each with its §10 row)
- Files touched: `tests/test_graph_lint.py` (one new test class only), `tests/test-bound-hook.sh` (new cases in its collecting pattern only), `docs/specs/SPEC-0003-per-prompt-injection.md` (the two promotions, the §6 grammar line, two §10 rows, one §12 entry)
- Tests to write (RED): `test_plan_entry_names_the_node_file`: a fixture graph whose `root` lives at `docs/graph/nodes/root.md`; every LOAD and NOT LOADED entry line has that path as its second token. A route-hook case per contract: the stub router prints pathed entry lines; the full injection holds them verbatim; the reminder's new-entry lines hold the path; the ledger stores ids only. Observed red: the graph-lint test (no path today) and the full-injection assertion (the stub's grammar is new, the hook passes it through, so this case may be a guard: the tester records which)
- Behavior added: none (tests and the spec promotion)
- Gate: `python3 tests/test_graph_lint.py` red on the new test only; `bash tests/test-bound-hook.sh` red on the new non-guard labels only; `spec-lint.py` over `docs/specs` stays within budget, because both slugs now sit in a test
- Rollback path: drop the tests and move the two headings back into the pending block
- Effort: medium
- Phase: RED
- Depends on: increment 1
