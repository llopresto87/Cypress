<!-- Increment 57 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 57: RED: graft-audit classes every projection of a plant-owned node, and the contract rows bind
- Item: C3 (class S), widened by the cycle 1 ruling pass
- Spec contracts: SPEC-0001/EVERY_BACKUP_IS_CLASSIFIABLE. Why: increment 32 made the `.claude/agents/<name>.md` projection of an `origin: project` agent a named exclusion, the one arm a test covered. Two more backups the installer makes of plant-owned nodes stay UNMAPPED, which the contract forbids: the `<adapter>/skills/<name>/SKILL.md` projection of a plant skill node `docs/graph/skills/<name>.md` with `origin: project` (`install.sh` `project_skills`), and `.github/agents/<name>.agent.md`, the Copilot view of a plant agent. And GA-C3's row could not land in §10: `tests/seed-lint.py` binds a row that cites a `.sh` file only by a leading label `[MSKVXE]<digits>` or `D<digits>` that the file contains, and `GA-C3` is neither
- Files touched: `tests/test-graft-tools.sh` (the round's collecting block: the GA-C3 case runs under label X390, its description keeping "GA-C3"; two new cases, X391 for the skill projection and X392 for the Copilot agent view, each asserting that the backup is not UNMAPPED and the audit exits 0; the block's header comment names the three X labels), `docs/specs/SPEC-0001-install-placement.md` (§10 only: three EVERY_BACKUP_IS_CLASSIFIABLE rows opening X390, X391 and X392, the first `green`, the two new ones `red`; one §12 line). Both files commit together, at the later of increments 35 and 58
- Tests to write (RED): X391 and X392 as above, on synthetic plants. Observed red: both, each on its first assertion (UNMAPPED, exit 1). X390 stays green: a relabel with the same assertions
- Behavior added: none (tests and §10 rows)
- Gate: `bash tests/test-graft-tools.sh`: every older case in its state, X390 OK, one `FAIL` line each for X391 and X392, GL and GR unchanged; `python3 tests/seed-lint.py` gains no finding (the three rows bind); `spec-lint.py --specs docs/specs --root . --uncovered-budget 2` within budget
- Rollback path: drop the two cases, restore the GA-C3 label, remove the three rows
- Effort: medium-low
- Phase: RED
- Depends on: increment 32
