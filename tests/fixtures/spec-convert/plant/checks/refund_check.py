"""Fixture: a check directory only the plant's own TEST_GLOBS reads."""
from shop.ledger import Ledger


def test_refund_restores_the_balance():
    ledger = Ledger(100)
    ledger.pay(40)
    ledger.refund(40)
    assert ledger.balance == 100, "REFUND_RESTORES_THE_BALANCE"
