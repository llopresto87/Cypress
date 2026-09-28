<!-- Increment 36 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 36: GREEN: the installer recognises every earlier seed kernel
- Item: D1 (class I)
- Spec contracts: SPEC-0001/PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION
- Files touched: `install.sh` (one helper that compares a body with every revision the seed kernel has had in the seed checkout's history, used by `place_kernel`, `sweep_orphaned_instruction_backups` and the Copilot kernel path; the one fallback log line)
- Tests to write (RED): none new: increment 13's cases
- Behavior added: an upgrade over a pristine older kernel is a quiet fast-forward
- Gate: `bash tests/test-install-kernel-modes.sh` green; `bash tests/test-install-placement.sh` green; `bash tests/test-unified-graph-install.sh` green; `python3 tests/seed-lint.py` PASS (install write sites). Bash 3.2 syntax only
- Rollback path: revert the helper and its three call sites
- Effort: medium
- Phase: GREEN
- Depends on: increment 13
