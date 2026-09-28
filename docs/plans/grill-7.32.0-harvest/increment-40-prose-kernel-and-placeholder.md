<!-- Increment 40 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 40: Prose: the kernel sheds its pre-growth lines and states the settled-facts rule; the placeholder index carries the pointer
- Item: 8a (class P) and R5 (class P), decisions 8 and 12
- Spec contracts: SPEC-0001/PRE_GROWTH_POINTER_LIVES_IN_THE_PLACEHOLDER_INDEX
- Files touched: `core/AGENTS.md` (FIRST MOVE loses its last three lines; §5 loses its last bullet; §3.2 gains the sentence of ADR-0018, byte for byte), `templates/knowledge-graph/index.md` (the delimited pre-growth block)
- Tests to write (RED): none new: increment 16's cases
- Behavior added: a grown plant loads no pre-growth line, and every session reads that a fact the graph states is settled
- Gate: `bash tests/test-full-install.sh` green; `python3 tests/seed-lint.py`: the kernel is under 7,931 bytes (7,797 by this pass's simulation of the edit) and within `KERNEL_BUDGET`, `KERNEL_POINTS_AT_THE_SESSION_RECORD` holds, and only the published-figure lines differ, attributed to increment 52; `bash tests/test-bound-hook.sh` green (the kernel-restatement checks). Reviewer checks the sentence against ADR-0018 byte for byte
- Rollback path: revert both files
- Effort: medium
- Phase: prose
- Depends on: increment 16, increment 19
