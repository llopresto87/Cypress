<!-- Increment 18 of `docs/plans/grill-7.35.0-positive-voice.md`; its §9 index row points here. -->

### Increment 18: RED: prepare-release refuses an entry it would cut short
- Item: the design's truncation finding: `extract_changelog_section` stops at any level-two heading, so an entry that holds one is cut short and staged silently; a real tool bug gets its regression test (owner rule of 2026-09-30)
- Spec contracts: none: contained. `tools/prepare-release.py` is seed-only, writes only in the seed and reports no figure. Why: a release note cut short without a word is published as written
- Files touched: `tests/test_prepare_release.py`
- Tests to write (RED): replace `test_stops_at_the_next_level_two_heading_even_when_not_a_version`, which asserts the bug, with `test_non_version_level_two_heading_inside_the_entry_refuses`: the extraction raises `ReleasePrepError` naming the heading, and a CLI case exits 1 and stages no `.github/RELEASE_NOTES.md`. Observed red: no raise on the unmodified tool
- Behavior added: none (tests only)
- Gate: `python3 -m unittest tests.test_prepare_release`: the new case fails, every other case green
- Rollback path: restore the replaced test
- Effort: low
- Phase: RED
- Depends on: increment 3
