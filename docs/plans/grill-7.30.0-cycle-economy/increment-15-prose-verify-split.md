### Increment 15 — Prose: the verify split
- Spec contracts: SPEC-0005/LEAF_BODY_CEILING_HELD
- Files touched: `protocols/verify.md`, new `protocols/verify-new-gates.md` and `protocols/verify-disagreement.md` (sections per SPEC-0005 §6 "Leaf splits", moved verbatim; `rule.verify` stays), `manifest.json` (`protocols[]` entries), `documentation/protocols-reference.md` (rows and sections)
- Tests to write (RED): none new; increment 4's ledger cases hold it
- Behavior added: a routine gate run no longer loads the exception and new-gate sections
- Gate: `python3 tests/seed-lint.py`; `python3 -m unittest tests.test_router_reach`; the one-time verbatim record in the handback; the key mapping listed in the handback
- Rollback path: revert
- Effort: medium
- Phase: prose
- Depends on: increment 10, increment 14
