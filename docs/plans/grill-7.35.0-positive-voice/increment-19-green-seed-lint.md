<!-- Increment 19 of `docs/plans/grill-7.35.0-positive-voice.md`; its §9 index row points here. -->

### Increment 19: GREEN: the seed-lint checks of increment 14
- Item: the checks increment 14's rows fail on, plus two changes green on arrival: the `delegation.model-map` row of `ADOPTED_RULE_HOMES`, and `docs/skills` in the agnosticism scan
- Spec contracts: SPEC-0001/SEED_ONLY_FILES_NEVER_PLACED, SPEC-0003/BRIEF_TEMPLATES_BYTE_IDENTICAL, SPEC-0005/ADOPTED_RULE_HOMES (a data row under the existing contract)
- Files touched: `tests/seed-lint.py`, `tests/ratchets.json` only if a ratchet moves
- Tests to write (RED): none: increment 14 holds them
- Behavior added: seed-lint gains `check_seed_only_stays_home` and `check_decision_index`, compares the COMPANION block across the brief templates, compares each quoted `load_when` of the protocols reference with its protocol's frontmatter (whitespace runs collapsed), and checks the published protocol count
- Gate: `bash tests/test-seed-lint.sh` all green with no test edited; `python3 tests/seed-lint.py` shows no finding that names these checks on the real tree
- Rollback path: revert `tests/seed-lint.py`
- Effort: medium
- Phase: GREEN
- Depends on: increment 14
