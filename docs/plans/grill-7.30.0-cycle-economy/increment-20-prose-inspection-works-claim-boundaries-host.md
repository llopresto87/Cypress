### Increment 20 — Prose: the inspection and works-claim boundaries in host parity
- Spec contracts: none here — increment 25 holds `engineering-posture.no-write-inspection`
- Files touched: `core/method/host-parity.md` (`engineering-posture.no-write-inspection`: inspection on a shared host never writes, and a fix that lets a loop continue past a failure re-checks what the failure protected; the works-claim rule as a sharpening of "Validate where it runs")
- Tests to write (RED): none — prose increment
- Behavior added: each boundary in one home
- Gate: `python3 tests/seed-lint.py`; `prose-lint` against baseline
- Rollback path: revert
- Effort: medium-low
- Phase: prose
- Depends on: increment 19
