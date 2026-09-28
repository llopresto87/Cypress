### Increment 19 — Prose: the engineering-posture split
- Spec contracts: SPEC-0005/LEAF_BODY_CEILING_HELD
- Files touched: `core/method/engineering-posture.md`, new `core/method/minimum-sufficient-work.md`, `core/method/decision-economy.md`, `core/method/host-parity.md`, `core/method/bounded-execution.md` (sections per SPEC-0005 §6 "Leaf splits", moved verbatim; keys move with their sections; siblings cross-linked by `peers:`)
- Tests to write (RED): none new; increment 4's ledger cases hold it
- Behavior added: a task on one of the four topics loads that leaf, not the whole posture
- Gate: `python3 tests/seed-lint.py`; `python3 -m unittest tests.test_router_reach`; the one-time verbatim record and the key mapping in the handback
- Rollback path: revert
- Effort: medium
- Phase: prose
- Depends on: increment 10
