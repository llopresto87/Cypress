<!-- Increment 31 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 31: GREEN: the session-start hooks inject the anchor line
- Item: F (class P)
- Spec contracts: SPEC-0003/STATUS_HOOK_INJECTS_THE_ANCHOR_LINE, SPEC-0003/STATUS_HOOK_ANCHOR_FAILURE_FAILS_TOWARD_INCLUSION, SPEC-0003/STATUS_EXTENSION_INJECTS_THE_ANCHOR_LINE
- Files touched: `integrations/claude-code/status-hook.py`, `integrations/prime-agent/status-extension.ts`
- Tests to write (RED): none new: increment 8's cases
- Behavior added: every Claude Code and Prime Agent session starts with the one anchor line
- Gate: `bash tests/test-bound-hook.sh` green; `python3 tests/seed-lint.py` PASS
- Rollback path: revert the two files
- Effort: medium
- Phase: GREEN
- Depends on: increment 8, increment 30
