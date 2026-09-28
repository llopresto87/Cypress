<!-- Increment 30 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 30: GREEN: the code-anchor tool
- Item: F (class P)
- Spec contracts: SPEC-0003/ANCHOR_RECORD_NAMES_EVERY_REPOSITORY, SPEC-0003/ANCHOR_QUIET_WHEN_NOTHING_MOVED, SPEC-0003/ANCHOR_NAMES_PATHS_WHEN_THE_COMMIT_MOVED, SPEC-0003/ANCHOR_NAMES_BOTH_BRANCHES_WHEN_THE_BRANCH_MOVED, SPEC-0003/ANCHOR_NAMES_NEW_UNCOMMITTED_WORK, SPEC-0003/ANCHOR_ABSENT_FAILS_TOWARD_INCLUSION, SPEC-0003/ANCHOR_OUTPUT_WITHIN_BUDGET, SPEC-0003/ANCHOR_COMPARE_WRITES_NOTHING, SPEC-0003/ANCHOR_RECORD_REFUSES_A_SYMLINK
- Files touched: `tools/code-anchor.py` (new; stdlib; `--record`, `--compare`, `--compare --all`; Git through `subprocess` with an argument list and a timeout; the write discipline of the session ledger)
- Tests to write (RED): none new: increment 7's cases
- Behavior added: canonize records the anchor in one command, and a session start compares it once
- Gate: `bash tests/test-bound-hook.sh` green; `bash tests/test-tool-help.sh` green. The mandatory mutation pass (§10) covers this file
- Rollback path: delete the new file
- Effort: medium-hard
- Phase: GREEN
- Depends on: increment 7
