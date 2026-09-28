### Increment 14 — Prose: explain before asking the owner, and the seed's no-residue convention
- Spec contracts: none — doctrine accepted by review (§6 rows S1 and S2)
- Files touched: `protocols/deliver.md` (`deliver.numbered-decisions` :127-138: ~~two sentences stating §6 row S1~~ (R2.9, the owner's answer:) a lead sentence in the owner's principle — a question to the owner is as understandable as possible — then S1's method as how it is met, in at most three sentences; no `owns:` change; `est_tokens` re-measured; `description:` unchanged); `documentation/protocols-reference.md` (the deliver row and section, only if `check_protocol_reference` names them); `CLAUDE.md`, the seed's own and never shipped: one Conventions bullet stating §6 row S2. It runs after increment 12 in the same writer, because both write `documentation/protocols-reference.md`
- Tests to write (RED): none — prose increment
- Behavior added: an owner decision arrives explained; seed text stays free of session residue
- Gate: `python3 tests/seed-lint.py` (protocol reference, machinery body ceiling, pending phrases); `python3 tools/prose-lint.py --file <each file>` against its baseline count
- Rollback path: revert
- Effort: low
- Phase: prose
- Depends on: increment 12
