"""Fixture: adversarial cases written by an independent tester to probe
worth-check.py for false positives (a good test flagged) and false negatives
(a read-back test spared). The verdict each test is owed is in
tests/fixtures/worth/adversarial.tsv, written before the tool was run; the
cases the tool classified otherwise are listed in
tests/fixtures/worth/known-gaps.tsv."""
import unittest
from pathlib import Path

import pytest

from app.build import build_site
from app.repo import users
from app.router import router
from app.settings import (API_BASE_URL, BRAND_COLOUR, CSRF_HEADER, DARK_MODE_DEFAULT,
                          ROUTES, SUBMIT_LABEL)


# --- false-negative probes: read-backs the check could miss ----------------

@pytest.mark.parametrize("path,handler", [("/submit", "submit_form"), ("/cancel", "cancel_form")])
def test_routes_parametrized(path, handler):
    assert ROUTES[path] == handler


def check_label(value):
    assert value == "Send"


def test_label_through_a_helper():
    check_label(SUBMIT_LABEL)


def test_label_against_a_literal_built_from_literals():
    expected = "Se" + "nd"
    assert SUBMIT_LABEL == expected


def test_label_against_a_joined_literal():
    expected = "".join(["Se", "nd"])
    assert SUBMIT_LABEL == expected


def test_label_against_a_golden_file():
    assert SUBMIT_LABEL == Path("golden/label.txt").read_text(encoding="utf-8").strip()


async def test_label_in_an_async_test():
    assert SUBMIT_LABEL == "Send"


def test_regression_label_text():
    assert SUBMIT_LABEL == "Send"


def test_api_base_url():
    assert API_BASE_URL == "https://api.example.com"


def test_brand_colour():
    # brand colour #112233 from the style guide
    assert BRAND_COLOUR == "#112233"


def test_dark_mode_off_by_default():
    assert DARK_MODE_DEFAULT is False


def test_label_not_empty_and_is_send():
    assert SUBMIT_LABEL != ""
    assert SUBMIT_LABEL == "Send"


def test_csrf_header_name():
    assert CSRF_HEADER == "X-CSRF-Token"


# --- false-positive probes: logic tests the check could flag ----------------

def test_router_precedence_through_get():
    assert router.get("/submit/new") == "submit_new"


def test_user_lookup_by_email():
    assert users.find("alice@example.com") == "alice"


def test_label_rendered_for_a_snapshot(snapshot):
    assert SUBMIT_LABEL == snapshot


class TestBuiltPage(unittest.TestCase):
    def setUp(self):
        build_site(out="dist")

    def test_built_page_carries_the_label(self):
        text = Path("dist/submit.html").read_text(encoding="utf-8")
        self.assertIn('value="Send"', text)
