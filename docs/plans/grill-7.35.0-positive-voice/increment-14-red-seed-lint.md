<!-- Increment 14 of `docs/plans/grill-7.35.0-positive-voice.md`; its §9 index row points here. -->

### Increment 14: RED: seed-lint holds the seed-only files, the COMPANION block, the reference load_when strings, the protocol count and the decision index
- Item: owner ruling D2 (lint keeps the docs aligned) and ADR-0021, through the rows 1 to 9 of the round's test plan; plus the harness fix in `tests/test-seed-lint.sh`
- Spec contracts: SPEC-0001/SEED_ONLY_FILES_NEVER_PLACED (X393 to X395); SPEC-0003/BRIEF_TEMPLATES_BYTE_IDENTICAL (X396, the COMPANION block beside the GRAPH DISCIPLINE block). The `load_when`, protocol-count and decision-index rows bind no contract. Why: seed-internal consistency checks over the seed's own docs, siblings of spec-free rows such as `skills-count`
- Files touched: `tests/test-seed-lint.sh` (rows in its table only, and the harness fix)
- Tests to write (RED): X393 a copied `manifest.json` whose `tools` map names `tools/prepare-release.py`; X394 a copied `install.sh` that places `docs/skills/seed-release.md`; X395 a copied `manifest.json` that drops `tools/code-anchor.py`; X396 one word changed inside the COMPANION block of `templates/prompts/investigation-brief.md`; `reference-load-when-drift` a reworded quoted `load_when` in `documentation/protocols-reference.md`; `reference-load-when-rewrapped` a guard, re-wrapped with no finding; `protocol-count` a claim of 99 protocols in `README.md`; `decision-index-unlisted` and `decision-index-dangling`. Harness fix first: a row whose check is missing, or whose baseline is red on the real tree, fails that row by name and the table runs on (SPEC-0005 failure ABORTED_STEP_HIDES_CASES). Observed red: each non-guard row fails on the unmodified seed-lint
- Behavior added: none (tests only)
- Gate: `bash tests/test-seed-lint.sh`: every existing row green, one FAIL line per new non-guard row, the guard green; the tree each RED was shown on is recorded, because `check()` and `check_reference_tables` are red on the working tree until increments 22 and 24
- Rollback path: drop the new rows and the harness change
- Effort: medium
- Phase: RED
- Depends on: increment 3, increment 4, increment 12
