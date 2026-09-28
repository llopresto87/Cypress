### Increment 27 — Prose: CHANGELOG, harvest log and ratification
- Spec contracts: none — release record
- Files touched: `CHANGELOG.md` (7.30.0 entry, round 2), the harvest log, the ratification proposal kept with the harvest's records (outside the seed)
- Tests to write (RED): none — prose increment, written by the session in-session
- Behavior added: the release record names every adopted rule and its home, and the held owner items
- Gate: `python3 tests/seed-lint.py`; harvest gate G1 over the round's diff with the donor forbid list
- Rollback path: revert
- Effort: low
- Phase: prose
- Depends on: increment 26
