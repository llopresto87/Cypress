<!-- Increment 58 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 58: GREEN: graft-audit names the plant-owned skill projection and Copilot agent view
- Item: C3 (class S)
- Spec contracts: SPEC-0001/EVERY_BACKUP_IS_CLASSIFIABLE
- Files touched: `tools/graft-audit.py` (`plant_owned_node()` reads the skill arm of `projected_sub()` against `docs/graph/skills/<name>.md`, and the Copilot view `.github/agents/<name>.agent.md` against `docs/graph/agents/<name>.md`, both through the `PLANT-OWNED` class of increment 32; the docstring names both)
- Tests to write (RED): none new: increment 57's cases
- Behavior added: a graft audit classes the backup of a projection of the plant's own skill, and of the Copilot view of its own agent, as `PLANT-OWNED` and exits 0 for them
- Gate: `bash tests/test-graft-tools.sh`: X390 to X392 OK, every other case in its state; `bash tests/test-install-placement.sh` green (the M8 audit-totality case)
- Rollback path: revert `tools/graft-audit.py`
- Effort: medium-low
- Phase: GREEN
- Depends on: increment 57
