"""Fixture: the test SPEC-0401's §10 row cites."""
from forms import submit


def test_valid_form_accepted():
    assert submit({"name": "a"}).status // 100 == 2
