<!-- Increment 10 of `docs/plans/grill-8.0.0-wave-a.md`; its §9 index row points here. -->

### Increment 10: the installer resolves the jurisdiction once
- Item: Defect row W0-02, confirmed: a re-install with no `--legal-jurisdiction` prints "national jurisdiction undecided" in the closing NEXT STEP banner and the national-layer report over a stamp that records a jurisdiction. The flag is read at the report and the banner, the stamp only at the writer
- Spec contracts: SPEC-0001/DECISIONS_SURVIVE_SILENCE, SPEC-0001/RECORD_AGREES_WITH_DISK, SPEC-0001/JURISDICTION_RESOLVED_ONCE (declared by increment 1)
- Files touched: `install.sh` (one resolution, the flag first and then the stamp's recorded value, read by the national-layer report, the stamp writer and the NEXT STEP banner); `tests/test-plant-state.sh`; `docs/specs/SPEC-0001-install-placement.md` (§10 status cells; the status moves to `active` with this RED, plan §12 question 5)
- Tests to write (RED): at most 1 case over the declared jurisdiction contract: a plant stamped with a jurisdiction, re-installed with no flag, prints no "undecided" line and keeps the stamp's value
- Behavior added: the report and the banner agree with the stamp
- Gate: `bash tests/run.sh`
- Rollback path: revert; the stamp's format is unchanged
- RED (2026-10-04, `bash tests/test-plant-state.sh __case case_jurisdiction_resolved_once`, exit 1): `FAIL: JURISDICTION_RESOLVED_ONCE: a re-install with no flag called the recorded jurisdiction undecided: [seed] NEXT STEP — national jurisdiction undecided (.cypress/seed.json).` The defect reproduced as reported: the stamp kept `it`, and the banner called it undecided
- GREEN (2026-10-04): `bash tests/test-plant-state.sh` PASS, all 11 scenarios, S13 `case_jurisdiction_resolved_once` among them. `install.sh` resolves the jurisdiction once, after the recorded corpus decision is read: with no flag on a prior install, a two-letter code in the stamp becomes `LEGAL_JURISDICTION`, which the national-layer report, the stamp writer and the NEXT STEP banner already read. `undecided` or an out-of-domain value is not inherited, so the banner still asks. SPEC-0001 moves to `active` with this RED (plan §12 question 5), its §10 row `green`
- Effort: medium-low
- Phase: GREEN
- Depends on: increment 1
