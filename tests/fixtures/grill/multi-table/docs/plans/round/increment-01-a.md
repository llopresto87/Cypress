### Increment 1 — Parse the batch
- Spec contracts: SPEC-0043/BATCH_PARSE
- Files touched: src/batch/parse.py
- Tests to write (RED): test_batch_parse
- Behavior added: a malformed batch is refused with its line number
- Gate: unit tests
- Rollback path: revert
- Effort: 1 cycle
- Depends on: none
