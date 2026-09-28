### Increment 1 — RED: expertise promotion, stack inference, closure, descent reshape
- Spec contracts: SPEC-0005/PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE, SPEC-0005/PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES, SPEC-0005/PLAN_PROMOTED_NODE_TAKES_ITS_CLOSURE
- Files touched: `tests/test_graph_lint.py` (new `PromotionTests`, `InferenceTests`, `PromotedClosureTests` beside `DescentTests`; the four `DescentTests` cases reshaped at RED, because the new promotion rule would otherwise turn them red for a reason the implementer may not fix)
- Tests to write (RED): every SPEC-0005 §10 row for the three contracts and for PROMOTION_FLOODS_LOAD, HOSTILE_TASK_LINE, TASK_LINE_WITHOUT_PATHS, PATTERN_BRACE_SPLIT, EXTENSIONLESS_BARE_NAME and DESCENT_TEST_NOW_SEEDS_THE_CHILD. The three-outscoring-nodes fixture is measured on the unmodified tool and the measurement recorded in the docstring; each positive case asserts its suffix on the node's own LOAD line
- Behavior added: none (tests only)
- Gate: `python3 -m unittest tests.test_graph_lint` shows the new non-guard cases failing on the missing suffix or behaviour, every guard passing, and every other pre-existing case passing
- Rollback path: drop the new classes; restore the four reshaped cases
- Effort: medium-hard
- Phase: RED
- Depends on: none
