<!-- Increment 60 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 60: RED: the session-start wait for the anchor is one value, 5 s, in every home
- Item: F (class P)
- Spec contracts: SPEC-0003/STATUS_HOOK_ANCHOR_FAILURE_FAILS_TOWARD_INCLUSION (§6 `ANCHOR_TIMEOUT`, amended from 15 s to 5 s by the session before this spawn, from the cycle 1 ruling). Why: the wait is paid before the first answer of any session whose Git is slow. A compare costs milliseconds (each of its Git calls took 2 to 4 ms on a plant of 646 tracked files), and when the wait runs out the session gets the not-checked line, which is what every plant had before this round. 15 s copied `ROUTER_TIMEOUT`, which bounds a different job
- Files touched: `tests/test-bound-hook.sh` (one structural case, X165), `docs/specs/SPEC-0003-per-prompt-injection.md` (§10: one row under the contract)
- Tests to write (RED): X165: the `ANCHOR_TIMEOUT` value SPEC-0003 §6 gives, the module literal `ANCHOR_TIMEOUT` in `integrations/claude-code/status-hook.py` (seconds) and the `timeout` of the anchor's `pi.exec` in `integrations/prime-agent/status-extension.ts` (milliseconds) are one value. Observed red: the spec says 5 s and both files say 15
- Behavior added: none (a test and a §10 row)
- Gate: `bash tests/test-bound-hook.sh`: X165 the one FAIL
- Rollback path: drop X165 and its row
- Effort: low
- Phase: RED
- Depends on: increment 31
