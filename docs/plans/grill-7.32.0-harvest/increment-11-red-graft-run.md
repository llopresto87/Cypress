<!-- Increment 11 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 11: RED: one command stages a graft and prints its gate table
- Item: T3 (class S), decision 10
- Spec contracts: none: the driver writes only into a staging directory outside the plant root; every write into a plant copy is made by the installer and the engine tool, which SPEC-0001 already contracts (§6 of the plan records this ruling). Why: the graft rebuilt this procedure by hand twice
- Files touched: `tests/test-graft-tools.sh` (new cases in the collecting block)
- Tests to write (RED): with a synthetic plant and seed: (a) `python3 tools/graft-run.py <plant> <seed> --stage <dir>` refuses, exit 2, when `<dir>` is inside `<plant>`, and writes nothing; (b) after a run the plant tree is byte-identical (a checksum of every file, `.git` included, before and after); (c) the stage holds a copy of the plant with the installer run in it, and the captured install log; (d) the three engines in the stage are reconciled; (e) the `--tokens` list it prints is derived from the plant (its stamp, its name, its node ids); (f) stdout ends with the Phase 7 gate table, one row per mechanical gate, in the graft record's format, with every judgment gate marked as not run by the tool. Observed red: every case
- Behavior added: none (tests only)
- Gate: `bash tests/test-graft-tools.sh`: existing cases green, one `FAIL <label>` per new case
- Rollback path: drop the cases
- Effort: hard
- Phase: RED
- Depends on: increment 1
