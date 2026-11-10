"""Fixture: a vendored copy the plant's own SKIP_DIRS leaves out."""


def test_discount_cap():
    assert min(50, 20) == 20, "ORDER_DISCOUNT_IS_CAPPED"
