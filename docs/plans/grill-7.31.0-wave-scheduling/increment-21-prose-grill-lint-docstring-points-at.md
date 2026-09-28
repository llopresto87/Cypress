### Increment 21 — Prose: grill-lint's docstring points at the rule, not the seed's spec
- Spec contracts: none — a comment in a shipped file, accepted by review (R2.4 (b))
- Files touched: `templates/knowledge-graph/grill-lint.py` :42 only: "(SPEC-0005 §6 "Wave report")" becomes "(`delegation.waves`, `docs/graph/method/delegation-sequencing.md`)", because the file ships to plants, where a bare SPEC slug names the plant's own spec
- Tests to write (RED): none — no behavior
- Behavior added: none
- Gate: `bash tests/test-grill-lint.sh` green (the golden plain output does not include the docstring); `bash tests/test-full-install.sh`; `python3 tests/seed-lint.py`
- Rollback path: revert
- Effort: low
- Phase: prose
- Depends on: increment 5
