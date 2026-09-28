<!-- Increment 59 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 59: RED: only the session-start hooks run the code anchor
- Item: F (class P), the owner's once-per-session rule
- Spec contracts: SPEC-0003/STATUS_HOOK_INJECTS_THE_ANCHOR_LINE and SPEC-0003/STATUS_EXTENSION_INJECTS_THE_ANCHOR_LINE (their 7.32.0 And clauses: once per session; `route-hook.py`, `route-extension.ts` and no pre-tool hook ever inject either line). Why: the owner set every new session apart from every prompt and every pre-tool hook ("a big one"), and no case asserts those clauses today
- Files touched: `tests/test-bound-hook.sh` (one structural case, X164), `docs/specs/SPEC-0003-per-prompt-injection.md` (§10: one guard row under each of the two contracts)
- Tests to write (RED): X164: `integrations/claude-code/route-hook.py`, `integrations/claude-code/bound-hook.py` and `integrations/prime-agent/route-extension.ts` name no `code-anchor.py` and carry no `Code anchor` literal; `integrations/claude-code/settings.json` and `integrations/github-copilot/hooks/status.json` wire `status-hook.py` under `SessionStart` and under no other event. A guard: green on arrival, recorded as a guard in §10, and the mutation pass shows it can fail
- Behavior added: none (a guard)
- Gate: `bash tests/test-bound-hook.sh` green with X164 OK; `spec-lint.py --specs docs/specs --root . --uncovered-budget 2` within budget
- Rollback path: drop X164 and its two rows
- Effort: low
- Phase: RED
- Depends on: increment 31
