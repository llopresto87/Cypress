### Increment 34 — RED (strengthening): the plant-agent effort case asserts its reason
- Spec contracts: SPEC-0005/AGENT_DECLARES_EFFORT
- Files touched: `tests/test_agent_lint.py` (`test_lint_fails_on_plant_agent_without_effort` asserts the error line names `effort`, so it cannot pass on some other error naming the agent)
- Tests to write (RED): none new; one assertion added; it passes on the current code
- Behavior added: none (tests only)
- Gate: `python3 -m unittest tests.test_agent_lint`
- Rollback path: drop the assertion
- Effort: low
- Phase: RED
- Depends on: increment 8
