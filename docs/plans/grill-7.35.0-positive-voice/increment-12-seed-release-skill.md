<!-- Increment 12 of `docs/plans/grill-7.35.0-positive-voice.md`; its §9 index row points here. -->

### Increment 12: Prose: the seed-release skill, and CLAUDE.md points at it
- Item: owner ruling D1: a seed-only release skill keeps every doc current with the seed's changes and calls canonize, which stays unchanged (ADR-0021)
- Spec contracts: none: prose. The skill is a procedure the seed runs on itself and never ships; SPEC-0001/SEED_ONLY_FILES_NEVER_PLACED (increments 14 and 19) holds that it stays home
- Files touched: `docs/skills/seed-release.md` (new), `CLAUDE.md`
- Tests to write (RED): none: prose
- Behavior added: none in a plant. The seed gains its release procedure in one file; `CLAUDE.md`'s Release section becomes a pointer to it
- Gate: `python3 tools/prose-lint.py --file` on both files; `python3 tools/agnosticism-lint.py --file` on both files PASS
- Rollback path: delete `docs/skills/seed-release.md` and `git checkout 7b219d7 -- CLAUDE.md`
- Effort: medium
- Phase: prose
- Depends on: increment 2
- Record: done 2026-09-30
