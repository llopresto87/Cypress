"""Fixture: the existing test SPEC-0401's covered contract names."""
from forms import route


def test_legacy_redirect():
    assert route("/old").status in (301, 308)
