### Increment 31 — RED: whole-token trigger phrases (ruling pass 5)
- Spec contracts: SPEC-0005/PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE
- Files touched: `tests/test_graph_lint.py` (new `test_plan_partial_version_token_does_not_promote`: a node whose piece is `net10.0` is not promoted by `target net10`, and is promoted by `target net10.0`; `test_plan_selects_major_by_tfm_token` asserts the matched term, and its comment at :1271-1278 is corrected)
- Tests to write (RED): the one new case; it fails on the current tokenizer
- Behavior added: none (tests only)
- Gate: the new case fails for the missing behaviour; every other case passes
- Rollback path: drop the case; restore the comment
- Effort: medium
- Phase: RED
- Depends on: increment 6
