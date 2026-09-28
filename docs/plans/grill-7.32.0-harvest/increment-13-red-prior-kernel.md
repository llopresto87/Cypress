<!-- Increment 13 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 13: RED: a kernel identical to an earlier seed kernel files no migration row
- Item: D1 (class I)
- Spec contracts: SPEC-0001/PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION (promoted in this commit, with the failure SEED_HISTORY_UNAVAILABLE and a §10 row)
- Files touched: `tests/test-install-kernel-modes.sh` (new cases only), `docs/specs/SPEC-0001-install-placement.md` (the promotion, §2 line, §7, §10 row)
- Tests to write (RED): the target kernel is the seed's `core/AGENTS.md` at an earlier commit of a temp clone of the seed (built from the real seed with `git clone --local`); after the install, no adopted-instructions row, no `OVERWRITTEN` line, one backup; a second run files no row; guard: a kernel with one plant line added is filed as today; failure case: the same over a seed copy with no `.git` files the row and prints the one fallback line. Observed red: the no-row assertion
- Behavior added: none (tests and the spec promotion)
- Gate: `bash tests/test-install-kernel-modes.sh` red on the new non-guard cases only; `spec-lint.py` within budget
- Rollback path: drop the cases and move the headings back
- Effort: medium
- Phase: RED
- Depends on: increment 1
