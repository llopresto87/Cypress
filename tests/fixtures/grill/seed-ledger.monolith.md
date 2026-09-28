# grill: round

## 0. Metadata
- Project: round  - Date: 2026-09-28  - Spec: SPEC-0042

## 1. Artifact Discovery
- Existing files inspected: src/round/handler.py
- Existing docs inspected: docs/plans/round.md
- Existing tests inspected: tests/test_round.py
- Existing specs inspected: docs/specs/SPEC-0042-round.md
- Existing architecture signals: none — a synthetic seed-shaped fixture
- Libraries already wikified: none — stdlib only
- External sources downloaded: none — nothing new
- Constraints discovered: none — see §4

## 2. Shared Understanding
A seed-shaped plan: its ledger sits beside it in docs/plans/round/, its specs in docs/specs/ and its decisions in docs/decisions/.

## 3. User Goal
- Primary user: steward  - Primary outcome: a seed plan that lints in place

## 4. Operating Constraints
- Runtime constraints: python 3.12, café-grade patience

## 5. Research Summary
- Key findings: nothing to research; stdlib only.

## 6. Decisions Made
| Decision | Evidence | Reversibility | ADR |
|---|---|---|---|
| Keep the ledger beside the plan | docs/plans/round.md | two-way | ADR-0007 |

## 7. Options Considered
- One ledger directory for every plan — rejected: each plan would read the others as orphans.

## 8. Architecture Plan
plan -> ledger -> leaves

## 9. Implementation Plan

The index below is the whole of §9's increments; each row's file holds one block.

### Increment 1 — Validate the round
- Spec contracts: SPEC-0042/ROUND_ALPHA
- Files touched: src/round/validate.py
- Tests to write (RED): test_round_alpha
- Behavior added: 422 on a malformed round
- Gate: unit tests
- Rollback path: revert
- Effort: 1 cycle
- Depends on: none

### Increment 2 — Persist the round
- Spec contracts: SPEC-0042/ROUND_BETA
- Files touched: src/round/store.py
- Tests to write (RED): test_round_beta_persists
- Behavior added: a durable store — naïve rows kept as written
- Gate: integration test
- Rollback path: revert; no migration
- Effort: 1 cycle
- Depends on: increment 1 (validation)

## 10. Verification Plan
Both contracts' tests run under the round's gate.

## 11. Risks and Mitigations
| Risk | Probability | Impact | Mitigation | Verification |
|---|---:|---:|---|---|
| Session leak | low | high | context manager | test_store_closes_session |

## 12. Open Questions
| # | Question | Why it matters | Current assumption | How to resolve | Owner | Pinned by |
|---:|---|---|---|---|---|---|
| 1 | Retention period? | compliance | 30 days | ask the steward | steward | — |

## 13. Done Criteria
Both contracts green in the gate.

## 14. Recommended Next Step
Enter test-first for increment 1.

## 15. Changelog
- 2026-09-28: synthetic fixture written for the seed-layout cases of tests/test-grill-lint.sh.
