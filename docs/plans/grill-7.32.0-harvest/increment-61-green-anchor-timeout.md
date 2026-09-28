<!-- Increment 61 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 61: GREEN: the session-start hooks wait 5 s for the anchor
- Item: F (class P)
- Spec contracts: SPEC-0003/STATUS_HOOK_ANCHOR_FAILURE_FAILS_TOWARD_INCLUSION, SPEC-0003/STATUS_EXTENSION_INJECTS_THE_ANCHOR_LINE
- Files touched: `integrations/claude-code/status-hook.py` (`ANCHOR_TIMEOUT = 5`), `integrations/prime-agent/status-extension.ts` (the anchor's `pi.exec` `timeout: 5_000`; the register's call keeps its own value)
- Tests to write (RED): none new: increment 60's case
- Behavior added: a session whose Git is slow waits at most 5 s for the anchor, then gets the not-checked line
- Gate: `bash tests/test-bound-hook.sh` green (X162 still rewrites the literal and passes; X165 OK)
- Rollback path: revert the two literals
- Effort: low
- Phase: GREEN
- Depends on: increment 60
