<!-- Increment 64 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 64: GREEN: the install preflight walks only the trees a run writes
- Item: C5 (class S)
- Spec contracts: SPEC-0001/PREFLIGHT_SCOPED_TO_WRITTEN_TREES
- Files touched: `install.sh` (`preflight_destinations()`: the two deep walks, for an unwritable directory and for an escaping symlink, start at roots derived from the selected adapters' `adapter_dirs()` plus `docs/graph` and `.cypress`, and no longer at `$PROJECT_DIR`; `.github` is walked only by its four written subdirectories), `manifest.json` (7.32.1), `CHANGELOG.md`, `DOCUMENTATION.md` and `documentation/README.md` (documented version)
- Tests to write (RED): none new: increment 63's case
- Behavior added: an install into a plant with unwritable trees outside the written set succeeds; a read-only directory or an escaping symlink inside a written tree still refuses before the first byte
- Gate: `bash tests/test-install-adoption.sh` and `bash tests/test-install-placement.sh` green, `case_unrelated_trees` OK; `bash tests/run.sh` green
- Rollback path: revert `install.sh`
- Effort: medium-low
- Phase: GREEN
- Depends on: increment 63
