<!-- Increment 14 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 14: RED: the full re-created list is written to a file
- Item: D2 (class I)
- Spec contracts: SPEC-0001/RECREATED_LIST_IS_COMPLETE (promoted in this commit, with its §6 shape and a §10 row)
- Files touched: `tests/test-install-adoption.sh` (new cases only), `docs/specs/SPEC-0001-install-placement.md` (the promotion, §6, §10 row)
- Tests to write (RED): delete twelve seed-owned nodes from an installed temp plant and re-install: `.cypress/recreated-nodes.txt` has the header line and all twelve paths; the console shows ten and names the file; a clean re-install rewrites the file with the header alone. Observed red: the file is absent
- Behavior added: none (tests and the spec promotion)
- Gate: `bash tests/test-install-adoption.sh` red on the new cases only
- Rollback path: drop the cases and move the heading back
- Effort: medium-low
- Phase: RED
- Depends on: increment 1
