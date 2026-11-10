---
status: active
status_date: 2026-11-01
owner: architect
---

# SPEC-0501: order totals

## 0. Metadata

- **Identifier:** SPEC-0501-orders
- **Status:** see frontmatter (single home)
- **Owner:** architect
- **Date:** 2026-11-01
- **Related grill section:** docs/graph/plans/grill.md, increment 3
- **Sign-offs:** product [x] · architect [x] · tester [x]

## 1. Summary

The cart computes an order's total, caps a discount and refuses an empty cart.

## 4. Functional contracts

### Contract: ORDER_TOTAL_IS_SUMMED
- **Given:** a cart with two lines
- **When:** the order is priced
- **Then:** the total is the sum of the line totals

### Contract: ORDER_DISCOUNT_IS_CAPPED
- **Given:** a discount code worth more than the cap
- **When:** the order is priced
- **Then:** the discount is the cap
- **And:** the receipt names the cap, so a customer reading it
  sees why the code took less than it promised

### Contract: ORDER_EMPTY_CART_IS_REFUSED
- **Given:** an empty cart
- **When:** checkout starts
- **Then:** it is refused with a message

## 7. Failure modes

### Failure: PRICE_SERVICE_DOWN
- **Trigger:** the price service does not answer
- **Response:** checkout waits and retries once

## 9. Acceptance criteria

- [x] AC-1: totals and the cap hold; maps to ORDER_TOTAL_IS_SUMMED, ORDER_DISCOUNT_IS_CAPPED
- [x] AC-2: an empty cart is refused; maps to ORDER_EMPTY_CART_IS_REFUSED

## 10. Test mapping

| Contract / Failure | Test name | Test file | Level | Status |
|---|---|---|---|---|
| ORDER_TOTAL_IS_SUMMED | test_order_total_is_summed | tests/test_orders.py | unit | green |
| ORDER_DISCOUNT_IS_CAPPED | test_discount_cap | vendor/lib/orders_test.py | unit | green |
| ORDER_EMPTY_CART_IS_REFUSED | test_empty_cart_is_refused | tests/test_orders.py | unit | green |

## 12. Changelog

- 2026-11-01 — created.
