### Increment 40 — GREEN: agent-lint messages name the seed's spec
- Spec contracts: SPEC-0005/AGENT_DECLARES_EFFORT
- Files touched: `integrations/claude-code/agent-lint.py` (rule 5's messages cite `delegation.effort` or "the seed's SPEC-0005", unambiguous in a plant, and still name `effort`)
- Tests to write (RED): none new; increment 34's assertion holds the word
- Behavior added: the message reads right in a plant
- Gate: `python3 -m unittest tests.test_agent_lint`; `python3 integrations/claude-code/agent-lint.py --lint --dir agents`
- Rollback path: revert
- Effort: low
- Phase: GREEN
- Depends on: increment 34
