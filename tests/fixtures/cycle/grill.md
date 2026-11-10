# grill.md: Plan of Record: a synthetic cycle for cycle.py

The sections a plant fills are left out: cycle.py reads §9 alone.

## 9. Implementation Plan

### Increment 1 — RED alpha
- Spec contracts: SPEC-0001/ALPHA
- Files touched: `tests/test_alpha.sh`
- Tests to write (RED): alpha.case_one
- Rollback path: delete the test
- Effort: low
- Phase: RED
- Depends on: none

### Increment 2 — RED beta
- Spec contracts: SPEC-0001/BETA
- Files touched: `tests/test_beta.sh`
- Tests to write (RED): beta.case_one
- Rollback path: delete the test
- Effort: low
- Phase: RED
- Depends on: none

### Increment 3 — GREEN alpha
- Spec contracts: SPEC-0001/ALPHA
- Files touched: `src/alpha.py`
- Tests to write (RED): none — increment 1 wrote them
- Rollback path: revert the commit
- Effort: low
- Phase: GREEN
- Depends on: increment 1

### Increment 4 — GREEN beta
- Spec contracts: SPEC-0001/BETA
- Files touched: `src/beta.py`
- Tests to write (RED): none — increment 2 wrote them
- Rollback path: revert the commit
- Effort: low
- Phase: GREEN
- Depends on: increment 2

### Increment 5 — RED gamma
- Spec contracts: SPEC-0001/GAMMA
- Files touched: `tests/test_gamma.sh`
- Tests to write (RED): gamma.case_one
- Rollback path: delete the test
- Effort: medium
- Phase: RED
- Depends on: increment 3, increment 4

### Increment 6 — GREEN gamma
- Spec contracts: SPEC-0001/GAMMA
- Files touched: `src/gamma.py`
- Tests to write (RED): none — increment 5 wrote them
- Rollback path: revert the commit
- Effort: medium
- Phase: GREEN
- Depends on: increment 5

### Increment 7 — prose guide
- Spec contracts: none
- Files touched: `docs/guide.md`
- Tests to write (RED): none — prose
- Rollback path: revert the commit
- Effort: low
- Phase: prose
- Depends on: none

### Increment 8 — RED delta
- Spec contracts: SPEC-0001/DELTA
- Files touched: `tests/test_delta.sh`
- Tests to write (RED): delta.case_one
- Rollback path: delete the test
- Effort: low
- Phase: RED
- Depends on: none

## 15. Changelog
- 2026-11-10: a synthetic plan for the cycle driver's tests.
