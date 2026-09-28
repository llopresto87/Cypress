<!-- Increment 8 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 8: RED: both session-start hooks inject the anchor line
- Item: F (class P)
- Spec contracts: SPEC-0003/STATUS_HOOK_INJECTS_THE_ANCHOR_LINE, SPEC-0003/STATUS_HOOK_ANCHOR_FAILURE_FAILS_TOWARD_INCLUSION, SPEC-0003/STATUS_EXTENSION_INJECTS_THE_ANCHOR_LINE (promoted in this commit, with the failure ANCHOR_CHECK_DID_NOT_RUN and §10 rows)
- Files touched: `tests/test-bound-hook.sh` (new cases in the same collecting block), `docs/specs/SPEC-0003-per-prompt-injection.md` (the promotions, §7, §10 rows)
- Tests to write (RED): status-hook cases with a stub `docs/graph/code-anchor.py` that prints a fixed line, exits non-zero, prints nothing, or sleeps past `ANCHOR_TIMEOUT`, with and without a register; a structural case over `integrations/prime-agent/status-extension.ts`. Observed red: every non-guard case; the ledger-reset assertion is a guard
- Behavior added: none (tests and the spec promotion)
- Gate: `bash tests/test-bound-hook.sh`: existing cases green, one `FAIL <label>` per new non-guard case
- Rollback path: drop the cases and move the headings back
- Effort: medium
- Phase: RED
- Depends on: increment 1
