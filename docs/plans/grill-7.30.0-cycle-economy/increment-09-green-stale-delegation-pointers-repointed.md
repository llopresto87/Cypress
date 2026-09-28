### Increment 9 — GREEN: stale delegation pointers repointed
- Spec contracts: SPEC-0005/ADOPTED_RULE_HOMES
- Files touched: `install.sh` (log and comment strings naming `delegation.md` with `delegation.harness-registration`), `integrations/claude-code/status-hook.py` (the `delegation.briefs` pointer), `integrations/claude-code/agent-lint.py` (the registration pointer in two messages)
- Tests to write (RED): none new; increment 23's stale-pointer case holds this later
- Behavior added: each pointer names the sibling that owns the key
- Gate: `grep -n 'method/delegation.md' install.sh integrations/claude-code/*.py` shows no moved key beside it; `python3 -m unittest tests.test_agent_lint`; `bash tests/test-full-install.sh` (the stale-pointer check lands later, so this grep is the gate for now)
- Rollback path: revert
- Effort: low
- Phase: GREEN
- Depends on: increment 8
