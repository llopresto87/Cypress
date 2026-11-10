"""Fixture: the plant's order tests (spec-convert and the engine-arrival cases)."""
from shop.cart import Cart, price


def test_order_total_is_summed():
    cart = Cart([("pen", 2, 150), ("pad", 1, 300)])
    assert price(cart).total == 600, "ORDER_TOTAL_IS_SUMMED"


def test_empty_cart_is_refused():
    try:
        price(Cart([]))
    except ValueError as e:
        assert "empty" in str(e), "ORDER_EMPTY_CART_IS_REFUSED"
    else:
        raise AssertionError("ORDER_EMPTY_CART_IS_REFUSED: an empty cart was priced")
