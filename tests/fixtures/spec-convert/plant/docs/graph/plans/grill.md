# grill — orders and forms

## 0. Metadata
- Project: shop  - Date: 2026-11-03  - Spec: SPEC-0401, SPEC-0501

## 1. Artifact Discovery
- Existing files inspected: src/shop/cart.py
- Existing docs inspected: docs/graph/index.md
- Existing tests inspected: tests/test_orders.py
- Existing specs inspected: docs/graph/specs/SPEC-0501-orders.md
- Existing architecture signals: none — one module
- Libraries already wikified: none — stdlib only
- External sources downloaded: none — nothing new
- Constraints discovered: none — see §4

## 2. Shared Understanding
Price orders and accept valid forms.

## 3. User Goal
- Primary user: customer  - Primary outcome: a correct total

## 4. Operating Constraints
- Runtime constraints: python 3.12

## 5. Research Summary
- Wikified libraries: none — stdlib only

## 6. Decisions Made
| Decision | Evidence | Reversibility |
|---|---|---|
| Price in cents | src/shop/cart.py | two-way |

## 7. Options Considered
- Floats — rejected: rounding.

## 8. Architecture Plan
cart -> price -> receipt

## 9. Implementation Plan

### Increment 1 — Accept valid forms
- Spec contracts: SPEC-0401/SUBMIT_VALID_FORM_RETURNS_2XX
- Files touched: src/forms/submit.py
- Tests to write (RED): SPEC-0401 §10 rows: "A valid form is refused and the customer cannot submit"
- Behavior added: 2xx on a valid form
- Gate: unit tests
- Rollback path: revert
- Effort: 1 cycle
- Depends on: none

### Increment 2 — Label the button
- Spec contracts: SPEC-0401/SUBMIT_BUTTON_LABEL_IS_SEND
- Files touched: web/submit.html
- Tests to write (RED): none — a declared label holds no logic
- Behavior added: the button reads Send
- Gate: build
- Rollback path: revert
- Effort: 1 cycle
- Depends on: increment 1

### Increment 3 — Sum the order
- Spec contracts: SPEC-0501/ORDER_TOTAL_IS_SUMMED
- Files touched: src/shop/cart.py
- Tests to write (RED): test_order_total_is_summed
- Behavior added: totals
- Gate: unit tests
- Rollback path: revert
- Effort: 1 cycle
- Depends on: none

## 10. Verification Plan
not applicable — the standard gates cover this plan.

## 11. Risks and Mitigations
| Risk | Probability | Impact | Mitigation | Verification |
|---|---:|---:|---|---|
| Rounding | low | high | cents | test_order_total_is_summed; devils-advocate orchestrator.3: could-not-refute |

## 12. Open Questions
| # | Question | Why it matters | Current assumption | How to resolve | Owner | Pinned by |
|---:|---|---|---|---|---|---|
| 1 | Currency? | display | one | ask product | product | — |

## 13. Done Criteria
Every contract green in CI.

## 14. Recommended Next Step
Build increment 1.

## 15. Changelog
- 2026-11-03: grill pass; spawns orchestrator.1 (research-scout), orchestrator.2 (architect).
