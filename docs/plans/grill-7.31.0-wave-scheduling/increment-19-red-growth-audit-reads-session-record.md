### Increment 19 — RED: growth-audit reads the session-record form as a form
- Spec contracts: SPEC-0005/SESSION_RECORD_FORM_IS_NOT_A_SCAFFOLD
- Files touched: `tests/test-growth-audit.sh`: one new scenario with an invariant label, after every existing one, in its own installed target; `tools/gate-registry.py` only if the step's "Reads" line becomes false (the R0.5 precedent)
- Tests to write (RED): an installed plant whose coverage record claims `plans/` ABSENT with a reason, whose `plans/` holds the placed `sessions/_session-record.template.md` and whose `grill.md` scaffold is renamed `.unfilled.md`: growth-audit prints no CONTRADICTED line naming the form. And in the same run a non-underscore leaf byte-identical to its seed scaffold in an ABSENT collection is still named. Observed red: the CONTRADICTED line for `_session-record.template.md`. The four scenarios already red at the cycle-1 tip (scn_absent, scn_nostaff, scn_x34, scn_x41) are the same defect and are not edited
- Behavior added: none (tests only)
- Gate: `bash tests/test-growth-audit.sh` fails only on the new label and the four known scenarios
- Rollback path: drop the scenario
- Effort: low
- Phase: RED
- Depends on: none
