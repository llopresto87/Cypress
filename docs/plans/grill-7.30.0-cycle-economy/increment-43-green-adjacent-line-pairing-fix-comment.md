### Increment 43 — GREEN: the adjacent-line pairing fix, and a comment reflow
- Spec contracts: SPEC-0005/ADOPTED_RULE_HOMES
- Files touched: `tests/seed-lint.py` (`check_adopted_rule_homes`: a key on line L+1 pairs with a `method/delegation.md` path on line L only when line L+1 names no `method/delegation-*.md` path, and the mirror rule for a key-first wrap), `integrations/claude-code/agent-lint.py` (:935 comment reflowed under 120 characters)
- Tests to write (RED): none new; increment 42's X360
- Behavior added: a correct sibling pointer beside a hub pointer is not reported
- Gate: `bash tests/test-seed-lint.sh` (X356 to X360 green); `python3 tests/seed-lint.py`; `python3 -m unittest tests.test_agent_lint`
- Rollback path: revert
- Effort: medium-low
- Phase: GREEN
- Depends on: increment 42
