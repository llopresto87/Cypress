<!-- Increment 17 of `docs/plans/grill-7.35.0-positive-voice.md`; its §9 index row points here. -->

### Increment 17: RED: an unfilled model map is disclosed at graft, not blocked on
- Item: session ruling S4: `graft.gate.scaffolds` lists an unfilled `docs/graph/models.md` as a disclosed row and passes on it; `growth-audit.py` reports it and does not fail on it
- Spec contracts: none: contained. The change is to the report of two seed-only audit tools, and neither writes the disclosed leaf into a plant. Why: an unfilled map row already means "inherit the caller's model, and say so" (ADR-0022), so blocking a graft on it holds a plant for a choice it has already made
- Files touched: `tests/test-graft-tools.sh` (new cases in its collecting block), `tests/test-growth-audit.sh` (new cases), fixture files those cases need (new files only)
- Tests to write (RED): (a) `graft-audit.py <plant> <seed> --unfilled` over a plant whose only template-identical leaf is `docs/graph/models.md` exits 0, names the file on a disclosed line, and does not count it among the unfilled scaffolds; (b) with `runbooks/rollback.md` also unfilled it still exits 1, naming rollback only as unfilled (guard); (c) `--rename` leaves `models.md` in place; (d) `growth-audit.py` over a grown plant whose record has no `models.md` row and whose map is the template exits as it does without the map, and names `docs/graph/models.md` as unfilled. Observed red: (a), (c) and (d) fail on the unmodified tools
- Behavior added: none (tests only)
- Gate: `bash tests/test-graft-tools.sh` and `bash tests/test-growth-audit.sh`: the new cases fail by name, the guard and every existing case green
- Rollback path: drop the new cases and fixtures
- Effort: medium
- Phase: RED
- Depends on: increment 3, increment 10
