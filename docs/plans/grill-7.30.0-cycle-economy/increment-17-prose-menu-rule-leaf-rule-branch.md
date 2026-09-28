### Increment 17 — Prose: the menu rule, the leaf rule, the branch shape, the graph-over-harness and no-lint-only-tests rules
- Spec contracts: none here — increment 25 holds the keys
- Files touched: `skills/context-router/SKILL.md` (`context-router.menu`; `context-router.graph-over-harness`), `skills/knowledge-graph/SKILL.md` (§4: `knowledge-graph.branch-shape`, the leaf rule, the branch shape, the link-farm reconciliation for branch nodes; the ceiling ledger named), `skills/test-first/SKILL.md` (`test-first.no-lint-only-tests`), `templates/knowledge-graph/_schema.md` ("Body": the branch shape; "Key semantics", `load_when`: one file pattern per piece, no brace expansion, no all-wildcard pattern), `documentation/skills-and-templates-reference.md` (changed rows), `templates/knowledge-graph/index.md` (ruling pass 2: the delegation row keeps its question and lists all six ids, `method.delegation`, `method.delegation-model-classes`, `method.delegation-cycle-economy`, `method.delegation-briefs`, `method.delegation-sequencing`, `method.delegation-bounds`, the way the posture row lists its nodes)
- Tests to write (RED): none — prose increment
- Behavior added: one home each for the menu rule, the leaf rule, the graph-over-harness rule and the no-lint-only-tests rule
- Gate: `python3 tests/seed-lint.py`; `python3 -m unittest tests.test_router_reach`
- Rollback path: revert
- Effort: medium
- Phase: prose
- Depends on: increment 11
