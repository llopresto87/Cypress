<!-- Increment 54 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 54: Prose: a tester's RED spawn writes the test, confirms the red, and hands back
- Item: the owner's tester rule of 2026-09-28 (class P)
- Spec contracts: none: charter and protocol text. Why: three RED spawns of this round built throwaway implementations to prove their tests could pass, and the owner ruled that a tester only writes the test, confirms it is red and hands back
- Files touched: `agents/04-tester.md` (the body only: the rule, the owner's dated quote and four steps at the end of "Scope of one spawn", under `tester.spawn-scope`; the frontmatter's `description:` byte-identical), `protocols/test-first.md` (one pointer line in RED step 5)
- Tests to write (RED): none (prose)
- Behavior added: every plant's tester stops at a confirmed red, and a point the spec, the leaf and today's behaviour do not settle goes to the question file
- Gate: `python3 tests/seed-lint.py` gains no finding (charter vocabulary: no rare word used five times or more in the charter body; stale pointers: `tester.spawn-scope` resolves; body ceilings); `python3 tools/prose-lint.py --file` on both files, no new tell against a copy taken before the edit; `python3 integrations/claude-code/agent-lint.py --eval` unchanged, because the description is unchanged; the reviewer checks the quote byte for byte and the description byte-identical
- Rollback path: revert both files
- Effort: low
- Phase: prose
- Depends on: increment 1
