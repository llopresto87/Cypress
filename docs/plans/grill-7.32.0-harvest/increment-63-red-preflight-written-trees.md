<!-- Increment 63 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 63: RED: the install preflight ignores unwritable trees the installer never writes
- Item: C5 (class S), raised by a graft of a plant whose Docker runs left root-owned trees
- Spec contracts: SPEC-0001/PREFLIGHT_SCOPED_TO_WRITTEN_TREES. Why: `preflight_destinations()` walked every directory beneath the project root, so a root-owned `node_modules/`, `.next/`, data volume or nested checkout refused the whole install, though the installer never opens them. The promise the walk serves is a refusal that writes nothing, and that concerns the trees a run writes
- Files touched: `tests/test-install-adoption.sh` (case `case_unrelated_trees`, label D6 in the banner: read-only trees and a directory link leaving the target, in five trees outside the written set; the install must exit 0, write the stamp and leave those trees unchanged), `docs/specs/SPEC-0001-install-placement.md` (the new contract, its §10 row opening D6, one §12 line). Both files commit together, at increment 64
- Tests to write (RED): `case_unrelated_trees`. Observed red: the preflight refuses and names the read-only paths; nothing is written
- Behavior added: none (test and spec rows)
- Gate: `bash tests/test-install-adoption.sh __case case_unrelated_trees` fails on the refusal; every other adoption case unchanged; `python3 tests/seed-lint.py` finds the D6 row bound
- Rollback path: drop the case, the contract, the §10 row and the §12 line
- Effort: low
- Phase: RED
- Depends on: increment 17
