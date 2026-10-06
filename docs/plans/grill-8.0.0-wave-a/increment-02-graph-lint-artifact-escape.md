<!-- Increment 2 of `docs/plans/grill-8.0.0-wave-a.md`; its §9 index row points here. -->

### Increment 2: graph-lint's artifact escape check is lexical, so a symlink install stops reporting escapes
- Item: Defect row W0-01, confirmed. Under a `--symlink` install every `artifacts: templates/...` edge resolves through the link to the seed, outside `docs/graph/`, and `check_artifacts()` reports "path escapes docs/graph/" for each
- Spec contracts: SPEC-0001/SYMLINK_MODE_IS_UNIFORM (the install mode the regression fixture uses). The escape check itself carries no spec (plan §12 question 2)
- Files touched: `templates/knowledge-graph/graph-lint.py` (`check_artifacts`: the containment test is lexical, `os.path.normpath` on the joined path with no link followed; only the existence test follows links); `tests/test_graph_lint.py`; a fixture directory `tests/fixtures/symlink-artifacts/` holding a graph whose templates directory is a symlink
- Tests to write (RED): at most 1 case over SPEC-0001/SYMLINK_MODE_IS_UNIFORM: under a symlinked `templates/`, an in-graph artifact edge passes and a `../` edge still fails as an escape
- Behavior added: no false escape under a symlink install; a lexical escape still fails; a dangling edge still fails as missing
- Gate: `bash tests/run.sh`; and `graph-lint.py` over a fresh `install.sh claude-code --symlink` into a temp directory reports no artifact error
- Rollback path: revert; one function and one test
- Effort: medium-low
- Phase: GREEN (done 2026-10-04)
- Reproduction: `install.sh claude-code --symlink` into a temp plant, then `python3 graph-lint.py` in its `docs/graph/`: 38 lines of the form `✗ method.delegation-briefs: artifacts → path escapes docs/graph/: 'templates/prompts/graph-session-bootstrap.md'`. Confirmed
- RED: `python3 tests/test_graph_lint.py ArtifactsEdgeTests` failed `test_symlinked_templates_edge_is_not_an_escape` with `✗ root: artifacts → path escapes docs/graph/: 'templates/prompts/brief.md'` and `✗ domain.gone: artifacts → path escapes docs/graph/: 'templates/prompts/absent.md'`: the in-graph edge through the link and the dangling edge were both reported as escapes
- GREEN: the same case passes, and `tests/test_graph_lint.py` runs 108 tests OK. The temp plant's `graph-lint.py`, replaced by the fixed copy, reports no artifact error: `graph-lint: OK — 75 nodes`
- Depends on: none
