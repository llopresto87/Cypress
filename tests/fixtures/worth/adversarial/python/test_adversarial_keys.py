"""Fixture: a third round of adversarial cases by the independent tester,
written with their verdicts in tests/fixtures/worth/adversarial.tsv before
worth-check.py ran over them: keys in different shapes, and security words in
keys against security words in values."""
from app.settings import CSP_HEADER, HEADERS, LABELS, MESSAGES, PROD_SETTINGS, SETTINGS


def test_nested_security_setting():
    assert SETTINGS["security"]["csp"] == "default-src 'self'"


def test_setting_read_through_get():
    assert SETTINGS.get("SESSION_COOKIE_SECURE") is True


def test_header_keyed_by_a_constant():
    assert HEADERS[CSP_HEADER] == "default-src 'self'"


def test_transport_header_keyed_by_a_string():
    assert HEADERS["Strict-Transport-Security"] == "max-age=63072000"


def test_frame_header_keyed_by_a_string():
    assert HEADERS["X-Frame-Options"] == "DENY"


def test_footer_message_value():
    assert MESSAGES["footer"] == "Secure checkout"


def test_plain_label_under_a_plain_key():
    assert LABELS["submit"] == "Send"


def test_key_absent_from_production():
    assert "DEBUG" not in PROD_SETTINGS
