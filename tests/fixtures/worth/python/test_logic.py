"""Fixture: tests that look like read-backs but feed inputs to logic: a
pattern, a condition, an order of precedence, a computed value, and a file the
code under test wrote. worth-check.py flags none of them."""
from pathlib import Path

from app.forms import (EMAIL_RE, build_site, is_eligible, order_total,
                       render_label, resolve_handler)
from app.settings import SUBMIT_LABEL

TEMPLATE = Path("web/submit.html")


def test_submit_button_label_is_send():
    # Same name as a read-back test; this one renders the label for a locale.
    assert render_label(locale="en") == "Send"


def test_email_pattern_accepts_plus_addresses():
    assert EMAIL_RE.fullmatch("a+b@example.com")


def test_eligibility_boundary():
    assert is_eligible(age=18) is True
    assert is_eligible(age=17) is False


def test_route_precedence():
    assert resolve_handler("/submit/new") == "submit_new"


def test_total_with_discount():
    assert order_total([("pen", 2, 150)], discount=0.1) == 270


def test_built_page_carries_the_label(tmp_path):
    build_site(out=tmp_path)
    assert 'value="Send"' in (tmp_path / "submit.html").read_text()


def test_template_uses_the_declared_label():
    assert SUBMIT_LABEL in TEMPLATE.read_text(encoding="utf-8")
