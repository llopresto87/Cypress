---
status: active
status_date: 2026-11-02
owner: architect
---

# SPEC-0502: refunds

## 0. Metadata

- **Identifier:** SPEC-0502-refunds
- **Status:** see frontmatter (single home)
- **Owner:** architect
- **Sign-offs:** product [x] · architect [x] · tester [x]

## 4. Functional contracts

### Contract: REFUND_RESTORES_THE_BALANCE
- **Given:** a paid order
- **When:** it is refunded
- **Then:** the balance is what it was before the order

### Contract: REFUND_BUTTON_LABEL_IS_REFUND
- **Given:** the order page
- **When:** it renders
- **Then:** the button reads Refund
- **Check:** run — `make build && grep -c Refund dist/order.html` → pass (2026-11-02)

## 7. Failure modes

### Failure: REFUND_TWICE
- **Trigger:** a second refund of the same order
- **Response:** refused

## 10. Test mapping

| Contract / Failure | Test name | Test file | Level | Status |
|---|---|---|---|---|
| REFUND_RESTORES_THE_BALANCE | test_refund_restores_the_balance | checks/refund_check.py | integration | green |

## 12. Changelog

- 2026-11-02 — created; the label contract carries a run check.
