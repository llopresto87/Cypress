<!-- Increment 44 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 44: Prose: canonize records the anchor and the session record carries its line
- Item: F (class P)
- Spec contracts: none: protocol prose accepted by review
- Files touched: `protocols/canonize.md` (the one brief runs `python3 docs/graph/code-anchor.py --record` after the graph is reconciled and puts its line in the session record), `templates/docs/plans/sessions/_session-record.template.md` (one `Code anchor:` line)
- Tests to write (RED): none: prose
- Behavior added: every canonize leaves an anchor, and a host with no hook finds the line in the newest record
- Gate: `python3 tests/seed-lint.py` PASS; `bash tests/test-plant-state.sh` green (the session-record form is placed); prose-lint against a scratch-copy baseline
- Rollback path: revert both files
- Effort: low
- Phase: prose
- Depends on: increment 30
