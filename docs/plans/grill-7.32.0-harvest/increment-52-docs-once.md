<!-- Increment 52 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 52: Prose: docs once, at the end, by one writer
- Item: the owner's docs rule; S (manifest principle R3/R5), P (reach plan)
- Spec contracts: none: mirrors and records
- Files touched: `README.md`, `DOCUMENTATION.md`, `documentation/*.md` (every mirror the round moved; the eager figures re-derived from seed-lint's computation, never by hand), `INSTALL.md` (only where a claim moved), `integrations/prime-agent/README.md` (the model-table mention), `integrations/claude-code/README.md` (the anchor line), `manifest.json` (version 7.32.0; `tools` gains `tools/code-anchor.py`; `principles` gains R3 and R5 once), `CHANGELOG.md` (the 7.32.0 entry, with the reach plan: new plants at install, existing plants at their next graft, the anchor at their next canonize), `.github/RELEASE_NOTES.md` (staged by `python3 tools/prepare-release.py`)
- Tests to write (RED): none: prose; seed-lint holds the mirrors
- Behavior added: the public record describes 7.32.0
- Gate: `python3 tests/seed-lint.py` PASS with no expected-red line left; `python3 tools/prose-lint.py --file` on README and DOCUMENTATION green; the CHANGELOG entry passes the humanizer pass
- Rollback path: revert the docs commit
- Effort: medium
- Phase: prose
- Depends on: increment 51
