### Increment 32 — RED (characterization): mutation survivors and test-strength gaps
- Spec contracts: SPEC-0005/PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES, SPEC-0005/PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE, SPEC-0005/PLAN_PROMOTED_NODE_TAKES_ITS_CLOSURE, SPEC-0005/LISTED_NODE_EDGES_REACH
- Files touched: `tests/test_graph_lint.py`: a case for every mutant the first mutation pass left alive (the whole-path argument order, the long-token flood, the path-only cap, the 256-character boundary, a literal-name pattern in a subdirectory, a slash piece without a star, a phrase holding a slash, path and piece report order, two-character words, stopwords, seed-before-promotion order, the prefix fold) and `test_plan_backslash_only_token_is_not_path_like`, named as in SPEC-0005 §10; subTest rows for the repeated strip (`(infra/main.tf).`) and the backslash fold (`infra/sub\main.tf`) in `test_plan_inferred_path_echo_is_normalized_and_sanitized`; a second planted fault class not derived from `RuntimeError` in `test_plan_hostile_task_line_never_raises`, so the handler's breadth is pinned; `self.assertEqual(r.returncode, 0)` in `test_listed_node_peer_is_reachable`. Each new method's first docstring line is `Asserts SPEC-0005 <its §10 slug>.`
- Tests to write (RED): characterization; every case passes on the current code, and each kills its named mutant, which the tester re-runs in a scratch copy and records
- Behavior added: none (tests only)
- Gate: `python3 -m unittest tests.test_graph_lint` passes; each named mutant turns its case red in a scratch copy
- Rollback path: drop the cases
- Effort: medium-low
- Phase: RED
- Depends on: increment 6
