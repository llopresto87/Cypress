### Increment 42 — RED: the last mutation survivors and the adjacent-pointer guard (ruling pass 6)
- Spec contracts: SPEC-0005/PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE, SPEC-0005/ADOPTED_RULE_HOMES
- Files touched: `tests/test_graph_lint.py` (`test_plan_dotted_compound_named_whole_promotes`: phrase `aspnet-core.mvc`, task `upgrade aspnet-core.mvc`, suffix `<- promoted on "aspnet-core.mvc"`; it kills two stricter-only tokenizer mutants), `tests/test-seed-lint.sh` (X356's expected line tightened to the line holding the path only, so an off-by-one report is caught; X358 `case_ce_stale_pointer_root_prompt` plants in `INSTALL_PROMPT.md`, so the root prompt glob is exercised; X359 `case_ce_stale_pointer_wrapped_key_first`, key on the first line and path on the next, reported at the key's line; X360 `case_ce_adjacent_correct_pointers_pass`: `docs/graph/method/delegation.md` (`delegation.roster`) on one line and `docs/graph/method/delegation-sequencing.md` (`delegation.lanes`) on the next yield no finding). Each case carries its label and `# Asserts SPEC-0005 <SLUG>.`
- Tests to write (RED): X360 is red on the current check; the other four pass on arrival, and the tester re-runs their mutants in a scratch copy to record each kill
- Behavior added: none (tests only)
- Gate: `python3 -m unittest tests.test_graph_lint`; `bash tests/test-seed-lint.sh` fails on exactly X360
- Rollback path: drop the cases; restore X356's expectation
- Effort: medium-low
- Phase: RED
- Depends on: increment 38, increment 39
