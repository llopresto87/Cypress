<!-- Increment 10 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 10: RED: the graft ledger classifies each machinery file three ways and prints the graft's base
- Item: T1 and T2 (class S)
- Spec contracts: none: contained seed tool; no spec owns it. Why: the graft classified base, seed and plant by a hand-written script, and inferred its base by comparing file contents, because most releases carry no tag
- Files touched: `tests/test-graft-tools.sh` (new cases in the collecting block)
- Tests to write (RED): with a synthetic seed repository of three tagged releases and a plant stamped at the second: (a) `python3 tools/graft-ledger.py <plant> <seed>` prints one row per seed-owned machinery file with one class of FAST-FORWARD, KEEP-PLANT, MERGE, CURRENT, SEED-NEW or HARVESTED; (b) a plant addition the seed already carries is HARVESTED, not MERGE; (c) `--base` prints the tag of the stamped version and says it came from the tag; (d) with that tag deleted it prints the commit found by content lineage, the number of files that matched, and says it was inferred. Observed red: every case
- Behavior added: none (tests only)
- Gate: `bash tests/test-graft-tools.sh`: existing cases green, one `FAIL <label>` per new case
- Rollback path: drop the cases
- Effort: medium-hard
- Phase: RED
- Depends on: increment 1
