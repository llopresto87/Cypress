### Increment 21 — Prose: the design-posture split
- Spec contracts: SPEC-0005/LEAF_BODY_CEILING_HELD
- Files touched: `core/method/design-posture.md` (including its own two pointers into moved sections), new `core/method/restrictive-policy.md`, `core/method/maintenance-contracts.md`, `core/method/design-governance.md` (sections per SPEC-0005 §6, moved verbatim)
- Tests to write (RED): none new; increment 4's ledger cases hold it
- Behavior added: the plurality of structural questions no longer loads the policy, artifact and governance sections
- Gate: `python3 tests/seed-lint.py`; `python3 -m unittest tests.test_router_reach`; the one-time verbatim record and the key mapping in the handback
- Rollback path: revert
- Effort: medium
- Phase: prose
- Depends on: increment 10
