"""Fixture: cases written with their verdicts in
tests/fixtures/worth/adversarial.tsv before worth-check.py ran over them, on
the rule that a string key shaped like an HTTP header name declares a security
control, and that a header-shaped string used as a compared value is content."""
from app.settings import HEADERS, LABELS, RESPONSE, X_CONTENT_TYPE_OPTIONS


def test_content_type_options_under_a_subscript():
    assert HEADERS["X-Content-Type-Options"] == "nosniff"


def test_referrer_policy_under_a_response_subscript():
    assert RESPONSE.headers["Referrer-Policy"] == "no-referrer"


def test_permissions_policy_under_a_subscript():
    assert HEADERS["Permissions-Policy"] == "camera=()"


def test_opener_policy_in_a_dict_literal():
    assert HEADERS == {"Cross-Origin-Opener-Policy": "same-origin"}


def test_hint_names_a_header():
    assert LABELS["header_hint"] == "X-Frame-Options"


def test_sniffing_constant():
    assert X_CONTENT_TYPE_OPTIONS == "nosniff"
