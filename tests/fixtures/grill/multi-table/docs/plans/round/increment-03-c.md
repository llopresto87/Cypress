### Increment 3 — Refuse a duplicate batch
- Spec contracts: SPEC-0043/BATCH_UNIQUE
- Files touched: src/batch/store.py
- Tests to write (RED): test_batch_duplicate_refused
- Behavior added: a second batch with the same id is refused; the first one stays
- Gate: integration test
- Rollback path: revert
- Effort: 1 cycle
- Depends on: increment 2
