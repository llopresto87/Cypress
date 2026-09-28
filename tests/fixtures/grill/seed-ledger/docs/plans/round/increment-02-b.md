### Increment 2 — Persist the round
- Spec contracts: SPEC-0042/ROUND_BETA
- Files touched: src/round/store.py
- Tests to write (RED): test_round_beta_persists
- Behavior added: a durable store — naïve rows kept as written
- Gate: integration test
- Rollback path: revert; no migration
- Effort: 1 cycle
- Depends on: increment 1 (validation)
