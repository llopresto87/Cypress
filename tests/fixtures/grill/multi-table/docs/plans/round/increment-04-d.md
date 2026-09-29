### Increment 4 — Report the refused batches
- Spec contracts: SPEC-0043/BATCH_REPORT
- Files touched: src/batch/report.py
- Tests to write (RED): test_batch_report_names_refusals
- Behavior added: the nightly report names each refused batch; a naïve count is not enough
- Gate: unit tests
- Rollback path: revert
- Effort: 1 cycle
- Depends on: increment 3
