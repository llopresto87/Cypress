### Increment 11 — RED: every plant receives the session-record form, and keeps its records
- Spec contracts: SPEC-0001/SESSION_RECORD_FORM_IS_PLACED
- Files touched: `tests/test-plant-state.sh`: one new case, `case_session_records`, called after every existing case, so a red stops nothing after it. It builds its own `mktemp -d` target. The comment at :201-202 ("ships an empty grill.md scaffold into plans/ and nothing else") becomes true again: it names the session-record form as the second leaf
- Tests to write (RED): the case, with an invariant label. A fresh `install.sh claude-code --project-dir <t>` must hold `docs/graph/plans/sessions/_session-record.template.md`, byte-identical to the seed's `templates/docs/plans/sessions/_session-record.template.md`. The case then writes a plant record `docs/graph/plans/sessions/2026-01-01-example.md` (synthetic text) and edits the placed form, re-installs with `install.sh all`, and requires both files byte-identical and no `.bak-*` beside either. Observed red: the first assertion, because the form does not exist
- Behavior added: none (tests only)
- Gate: `bash tests/test-plant-state.sh` runs every existing case green and fails only on the new case's label
- Rollback path: drop the case and restore the comment
- Effort: low
- Phase: RED
- Depends on: none
