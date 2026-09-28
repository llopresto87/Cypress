<!-- Increment 7 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 7: RED: the code anchor is recorded at canonize and compared once per session
- Item: F (class P), decision 12
- Spec contracts: SPEC-0003/ANCHOR_RECORD_NAMES_EVERY_REPOSITORY, SPEC-0003/ANCHOR_QUIET_WHEN_NOTHING_MOVED, SPEC-0003/ANCHOR_NAMES_PATHS_WHEN_THE_COMMIT_MOVED, SPEC-0003/ANCHOR_NAMES_BOTH_BRANCHES_WHEN_THE_BRANCH_MOVED, SPEC-0003/ANCHOR_NAMES_NEW_UNCOMMITTED_WORK, SPEC-0003/ANCHOR_ABSENT_FAILS_TOWARD_INCLUSION, SPEC-0003/ANCHOR_OUTPUT_WITHIN_BUDGET, SPEC-0003/ANCHOR_COMPARE_WRITES_NOTHING, SPEC-0003/ANCHOR_RECORD_REFUSES_A_SYMLINK (promoted in this commit, with the failures ANCHOR_UNUSABLE and ANCHOR_COMMIT_UNREACHABLE, the §6 shapes, constants and texts, and §10 rows)
- Files touched: `tests/test-bound-hook.sh` (new cases, one collecting block), `docs/specs/SPEC-0003-per-prompt-injection.md` (the promotions, §6, §7, §10 rows, one §12 entry)
- Tests to write (RED): one case per contract, each against temp Git repositories built in the test with synthetic files; the tool is run as `python3 <seed>/tools/code-anchor.py` from the temp plant root. Observed red: every case, because the tool does not exist; each fails on its first assertion and none on a traceback in the harness
- Behavior added: none (tests and the spec promotion)
- Gate: `bash tests/test-bound-hook.sh`: existing cases green, one `FAIL <label>` per new case; `spec-lint.py` over `docs/specs` within budget
- Rollback path: drop the cases and move the headings back into the pending block
- Effort: medium-hard
- Phase: RED
- Depends on: increment 1
