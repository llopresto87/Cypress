<!-- Increment 20 of `docs/plans/grill-7.35.0-positive-voice.md`; its §9 index row points here. -->

### Increment 20: GREEN: agent-lint rule 6, the model token
- Item: the rule increment 15 fails on
- Spec contracts: SPEC-0005/AGENT_DECLARES_MODEL_CLASS
- Files touched: `integrations/claude-code/agent-lint.py`
- Tests to write (RED): none: increment 15 holds them
- Behavior added: `agent-lint.py --lint` fails an agent with no `model:` or a value outside `opus`, `sonnet`, `haiku`, `inherit`, naming the agent and the value
- Gate: `python3 -m unittest tests.test_agent_lint` green; `python3 integrations/claude-code/agent-lint.py --lint --dir agents` and `--eval` unchanged
- Rollback path: revert the rule
- Effort: low
- Phase: GREEN
- Depends on: increment 4, increment 15
