"""Fixture: read-back tests. Each test's only assertions read back a literal
the change under test adds, so the test is red while the line is absent and
green once it is present. worth-check.py flags every test in this file; the
expected verdicts are in tests/fixtures/worth/expected.tsv."""
import unittest
from pathlib import Path

from app.settings import MAX_UPLOAD_MB, ROUTES, SUBMIT_LABEL

HERE = Path(__file__).resolve().parent
PAGE = HERE.parent / "web" / "submit.html"


def test_submit_button_label_is_send():
    assert SUBMIT_LABEL == "Send"


def test_page_carries_the_label():
    html = PAGE.read_text(encoding="utf-8")
    assert 'value="Send"' in html


def test_checkout_total_is_computed():
    # The name promises logic; the body reads a declared value back.
    assert ROUTES["/checkout"] == "checkout_total"


def test_route_and_limit_declared():
    assert ROUTES["/submit"] == "submit_form"
    assert MAX_UPLOAD_MB == 25
    assert ROUTES["/cancel"] == "cancel_form"
    assert ROUTES["/edit"] == "edit_form"
    assert ROUTES["/delete"] == "delete_form"
    assert ROUTES["/export"] == "export_form"


class TestFooterCopy(unittest.TestCase):
    def test_footer_text(self):
        with open("web/footer.html", encoding="utf-8") as fh:
            text = fh.read()
        self.assertIn("All rights reserved", text)
