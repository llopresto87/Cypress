### Increment 3 — RED: agent effort
- Spec contracts: SPEC-0005/AGENT_DECLARES_EFFORT
- Files touched: `tests/test_agent_lint.py` (the `agent_md` builder gains `effort="medium"`, `effort=None` omits the line; new `LintEffortTests`)
- Tests to write (RED): the §10 rows for AGENT_DECLARES_EFFORT and AGENT_WITHOUT_EFFORT_AFTER_GRAFT (the bad value is `xhigh`)
- Behavior added: none (tests only)
- Gate: the new cases fail; every existing agent-lint case still passes with the builder change
- Rollback path: drop the class and the builder change
- Effort: medium-low
- Phase: RED
- Depends on: none
