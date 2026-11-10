"""Fixture: regression tests for bugs. The second has the shape of a read-back,
and it stays: a bug reproduction is always written and kept (ADR-0034)."""
from app.billing import DEFAULT_CURRENCY, FakeGateway, pay


# Bug: the retry after a timeout charged the card twice (issue #412).
def test_retry_after_timeout_charges_once():
    gateway = FakeGateway(fail_first=True)
    pay(gateway, amount=500)
    assert gateway.charges == 1


def test_default_currency_stays_eur():
    """Regression: a release shipped USD as the default currency and every
    invoice of that week was wrong (bug #388)."""
    assert DEFAULT_CURRENCY == "EUR"
