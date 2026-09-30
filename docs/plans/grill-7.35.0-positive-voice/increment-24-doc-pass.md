<!-- Increment 24 of `docs/plans/grill-7.35.0-positive-voice.md`; its §9 index row points here. -->

### Increment 24: Prose: the doc pass, through the seed-release skill
- Item: owner ruling D1 and the skill's step 3: one writer brings every human doc into line with the round, with the humanizer, and writes the version bump and the CHANGELOG entry
- Spec contracts: none: prose. The published figures it re-derives are held by `check_published_figures` and `check_reference_tables`, re-run at the final tip
- Files touched: `documentation/*.md`, `README.md`, `DOCUMENTATION.md`, `INSTALL.md`, `manifest.json`, `CHANGELOG.md`; `skills/humanizer/LICENSE.upstream` (the holder, owner ruling D3) was already applied by lane L6 and needs no edit here (`skills/humanizer/LICENSE.upstream:29`)
- Tests to write (RED): none: prose
- Behavior added: none. The docs describe the seed as it now is; every reference row, walkthrough and figure the lanes moved is re-derived
- Gate: `python3 tests/seed-lint.py` PASS, `check_reference_tables` and `check_published_figures` included; `python3 tools/prose-lint.py --file` per file written
- Rollback path: revert the doc files
- Effort: high
- Phase: prose
- Depends on: increment 13, increment 19, increment 20, increment 21, increment 22, increment 23
