### Increment 14 — Prose: test-first, verify and recover pointers
- Spec contracts: none — accepted by review (SPEC-0005 AC-15)
- Files touched: `protocols/test-first.md` (the cycle's opening paragraph points at batching; the GREEN row: the implementer runs the tests and edits none; the exit condition becomes targeted plus cross-cutting, with the tip rule by pointer), `protocols/verify.md` (cadence and mutation pointers), `protocols/recover.md` (the Ambiguity row: inside a batch, the question file and the ruling pass), `documentation/protocols-reference.md` (changed rows)
- Tests to write (RED): none — prose increment
- Behavior added: the three protocols agree with the cycle-economy leaf and restate none of it
- Gate: `python3 tests/seed-lint.py`; `prose-lint` per file against baseline
- Rollback path: revert
- Effort: medium
- Phase: prose
- Depends on: increment 13
