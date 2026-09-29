### Increment 2 — Store the batch
- Spec contracts: SPEC-0043/BATCH_STORE
- Files touched: src/batch/store.py
- Tests to write (RED): test_batch_store
- Behavior added: a parsed batch is kept as written
- Gate: integration test
- Rollback path: revert; no migration
- Effort: 1 cycle
- Depends on: increment 1
