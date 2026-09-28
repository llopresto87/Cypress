### Increment 38 — GREEN: whole-token trigger phrases (security surface)
- Spec contracts: SPEC-0005/PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE
- Files touched: `templates/knowledge-graph/graph-lint.py` (`_load_when_pieces` tokenizes a phrase with `_split_terms(piece)[0]`; two whitespace and comment-wrap nits in the same file; the canonical stemmer and stopword blocks untouched)
- Tests to write (RED): none new; increment 31's case, with increment 32's characterization cases staying green
- Behavior added: a dotted or hyphenated phrase word must be named whole
- Gate: `python3 -m unittest tests.test_graph_lint tests.test_router_reach`; `python3 tests/seed-lint.py`; the security review at high effort, clean, before the commit
- Rollback path: revert
- Effort: medium (a security surface: GREEN batch of one, high effort)
- Phase: GREEN
- Depends on: increment 31, increment 32
