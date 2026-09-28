### Increment 8 — GREEN: agent effort
- Spec contracts: SPEC-0005/AGENT_DECLARES_EFFORT
- Files touched: `integrations/claude-code/agent-lint.py` (rule 5 in `cmd_lint()`), `agents/*.md` (one `effort:` line each, per SPEC-0005 §6), `templates/agent.template.md` (the key, with a comment naming the closed set)
- Tests to write (RED): none new; increment 3's cases
- Behavior added: every agent declares a default effort; agent-lint holds the closed set on every agent
- Gate: `python3 -m unittest tests.test_agent_lint`; `python3 integrations/claude-code/agent-lint.py --lint --dir agents`; cross-cutting: `python3 tests/seed-lint.py` (frontmatter ceiling, eager surface, agents-reference mirror if it names the key), `bash tests/test-full-install.sh` (projection lint per host; no transform drops the key)
- Rollback path: revert
- Effort: medium-low
- Phase: GREEN
- Depends on: increment 3
