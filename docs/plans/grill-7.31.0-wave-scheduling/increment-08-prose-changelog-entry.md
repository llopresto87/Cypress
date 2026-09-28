### Increment 8 — Prose: the CHANGELOG entry
- Spec contracts: none — the release record
- Files touched: `CHANGELOG.md` (the 7.31.0 entry: waves, `--waves`, ADR-0012, and that it supersedes in part the 7.30.0 decision declining a RED ahead of its GREEN; (M1:) the memory-residency track, ADR-0013: the kernel's §3.2 sentence, the session record and its form, canonize filing it, the Prime Agent overlay no longer storing lessons in its own memory, and that existing plants receive it by graft; the S1 explain-first rule, the S3 shared-tree rule and the S2 seed convention; records outside the seed are cited as kept with the round's working records, never by path)
- Tests to write (RED): none — prose increment
- Behavior added: none
- Gate: `python3 tests/seed-lint.py` (manifest version and changelog agree); the `skills/humanizer` pass at canonize
- Rollback path: revert
- Effort: low
- Phase: prose
- Depends on: increment 7
