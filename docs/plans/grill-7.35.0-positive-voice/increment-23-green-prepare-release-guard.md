<!-- Increment 23 of `docs/plans/grill-7.35.0-positive-voice.md`; its §9 index row points here. -->

### Increment 23: GREEN: prepare-release refuses a truncated entry; three tool docstrings follow the release pass
- Item: the guard increment 18 fails on, and the tool comments that quote text the release pass retired
- Spec contracts: none: contained, as increment 18
- Files touched: `tools/prepare-release.py`, `tools/ratchet-lint.py` (docstring only), `tests/legal-lint.py` (docstring only), `tools/gate-registry.py` (text only: two stale facts corrected)
- Tests to write (RED): none: increment 18 holds the guard; the docstrings carry no behaviour
- Behavior added: `extract_changelog_section` raises `ReleasePrepError` naming a level-two heading inside the entry that is not a version heading; `tools/gate-registry.py` states the router eval's slack as measured (60 of 61, still passing at 58 of 61) and the `prevents:` check as `tests/seed-lint.py` makes it (at least 60 characters, no `title:` tail)
- Gate: `python3 -m unittest tests.test_prepare_release` green; `python3 tools/ratchet-lint.py` and `python3 tests/legal-lint.py` unchanged
- Rollback path: revert the four files
- Effort: low
- Phase: GREEN
- Depends on: increment 12, increment 18
