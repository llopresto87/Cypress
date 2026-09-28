<!-- Increment 22 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 22: Prose: the Opus version tables leave the Prime Agent overlay
- Item: 8c' (class P), owner rule R7
- Spec contracts: none: overlay prose; SPEC-0003's Prime Agent contracts cover only the `## Surfaced nodes` section and the eager budget, which falls
- Files touched: `integrations/prime-agent/APPEND_SYSTEM.md` (the Opus rows of the task-kind table, the whole per-phase table and the paragraphs that explain them, replaced by the two-line rule of ADR-0019; the non-Opus rows stay), `agents/multi-agent-architect.md` (the default-model sentence, same rule)
- Tests to write (RED): none new: `tests/seed-lint.py` eager-surface computation
- Behavior added: no Opus version table ships; the rule maps class to version in two lines
- Gate: `python3 tests/seed-lint.py`: the eager surface falls and only the published-figure lines differ, attributed to increment 52; `bash tests/test-bound-hook.sh` Prime Agent structural cases green
- Rollback path: revert the two files
- Effort: low
- Phase: prose
- Depends on: increment 19
