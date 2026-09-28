### Increment 20 — GREEN: growth-audit skips the underscore forms, as graft-audit does
- Spec contracts: SPEC-0005/SESSION_RECORD_FORM_IS_NOT_A_SCAFFOLD
- Files touched: `tools/growth-audit.py`: `collection_leaves` (:551-563) skips a leaf whose name starts with `_` or ends in `.template.md`, the exclusion `tools/graft-audit.py` uses (:380, :603); nothing else
- Tests to write (RED): none new; increment 19
- Behavior added: R2.1; ADR-0013's placement claim holds for growth-audit
- Gate: `bash tests/test-growth-audit.sh` all green (the new scenario and the four); `python3 tests/seed-lint.py`; the RED hash re-check before the commit
- Rollback path: revert; increment 19 and the four scenarios go red again
- Effort: low
- Phase: GREEN
- Depends on: increment 19
