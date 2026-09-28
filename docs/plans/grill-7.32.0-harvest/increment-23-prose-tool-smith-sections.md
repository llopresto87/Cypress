<!-- Increment 23 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 23: Prose: the tool-smith charter gains its two missing sections
- Item: B1 (class P)
- Spec contracts: none: charter prose accepted by review
- Files touched: `agents/tool-smith.md` (a handback pointer of three sentences and a "What you do not do" section, in the roster's shape; the description is unchanged)
- Tests to write (RED): none: prose
- Behavior added: every charter carries both sections
- Gate: `python3 tests/seed-lint.py` PASS; `python3 integrations/claude-code/agent-lint.py --lint --dir agents` PASS; reviewer compares with `agents/09-docs-librarian.md`
- Rollback path: revert the file
- Effort: low
- Phase: prose
- Depends on: increment 1
