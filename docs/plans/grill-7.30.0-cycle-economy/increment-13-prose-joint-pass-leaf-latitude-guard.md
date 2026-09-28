### Increment 13 — Prose: the joint-pass leaf and the latitude guard
- Spec contracts: none — accepted by review (SPEC-0005 AC-16); keys held by increment 25
- Files touched: new `protocols/specify-joint-pass.md` (`protocol.specify-joint-pass`, owning `specify.joint-pass` and `specify.design-latitude`; no `command:` key), `protocols/specify.md` (phase 0 pointer; stays at or under 170 body lines), `protocols/grill.md` (pointer line in `grill.flow`; `grill.press` checks decisions against the recorded latitude; the increment-shape example gains `Phase:` and the effort vocabulary pointer), `templates/grill.template.md` (the §6 `Design latitude:` row and the §9 `Phase:` field), `manifest.json` (`protocols[]` entry), `documentation/protocols-reference.md` (the new row and section; changed rows)
- Tests to write (RED): none — prose increment
- Behavior added: the latitude is asked once and held; one joint pass
- Gate: `python3 tests/seed-lint.py` (manifest catalog, protocols-reference mirror, leaf ceiling); `bash tests/test-grill-lint.sh`
- Rollback path: revert
- Effort: medium
- Phase: prose
- Depends on: increment 11
