<!-- Increment 9 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 9: RED: graft-audit stops raising four false alarms
- Item: C1 to C4 (class S)
- Spec contracts: SPEC-0001/EVERY_BACKUP_IS_CLASSIFIABLE (C3 only: the projection of a plant-owned agent is a backup the installer made, and today it is UNMAPPED, which the contract forbids; the spec is right and the code is wrong). C1, C2 and C4: none; contained, because which class a classifiable backup gets is no contract. Why: each alarm sent a graft steward to disprove it by hand
- Files touched: `tests/test-graft-tools.sh` (new cases in one collecting block after every existing case)
- Tests to write (RED): C1: a backup byte-identical to the seed at a base revision is DELTA under `--base <rev>` and stays CUSTOMIZED without it. C2: an engine backup whose signal lines all survive in the plant's current engine of the same name is not CUSTOMIZED. C3: the `.claude/agents/<name>.md` projection of a plant node `docs/graph/agents/<name>.md` with `origin: project` is classed as a named exclusion, not UNMAPPED, and the audit exits 0 for it. C4: backups under a directory that holds its own `.cypress/seed.json` are not counted. Observed red: all four
- Behavior added: none (tests only)
- Gate: `bash tests/test-graft-tools.sh`: existing cases green, one `FAIL <label>` per new case
- Rollback path: drop the cases
- Effort: medium
- Phase: RED
- Depends on: increment 1
