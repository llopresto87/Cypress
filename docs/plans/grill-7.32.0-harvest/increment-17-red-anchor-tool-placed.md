<!-- Increment 17 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 17: RED: the installer places the code-anchor tool and writes no anchor
- Item: F (class I, the placement half)
- Spec contracts: SPEC-0001/CODE_ANCHOR_TOOL_IS_PLACED (promoted in this commit, with a §10 row)
- Files touched: `tests/test-full-install.sh` (new cases only), `docs/specs/SPEC-0001-install-placement.md` (the promotion, §2 line, §10 row)
- Tests to write (RED): a fresh `install.sh all`: `docs/graph/code-anchor.py` byte-identical to `tools/code-anchor.py`, and no `.cypress/anchor.json`; a re-install over an older copy leaves one backup. Observed red: the tool is absent
- Behavior added: none (tests and the spec promotion)
- Gate: `bash tests/test-full-install.sh` red on the new cases only
- Rollback path: drop the cases and move the heading back
- Effort: low
- Phase: RED
- Depends on: increment 1
