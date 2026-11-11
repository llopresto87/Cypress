"""Fixture: a second round of adversarial cases by the independent tester,
written with their verdicts in tests/fixtures/worth/adversarial.tsv before
worth-check.py ran over them. Most probe for false positives: a logic test, or
a test reading output the code under test wrote, that a static reading could
take for a read-back."""
import unittest
from pathlib import Path

import pytest

from app.build import build_site, render_page
from app.forms import EMAIL_RE, is_eligible
from app.orders import Order
from app.settings import SUBMIT_LABEL


def setup_module():
    build_site(out="dist")


def test_page_built_by_setup_module():
    text = Path("dist/submit.html").read_text(encoding="utf-8")
    assert 'value="Send"' in text


@pytest.fixture(autouse=True)
def built_site():
    build_site(out="out")


def test_page_built_by_an_autouse_fixture():
    assert 'value="Send"' in Path("out/submit.html").read_text(encoding="utf-8")


@pytest.mark.usefixtures("site_from_conftest")
def test_page_built_by_a_named_fixture():
    assert 'value="Send"' in Path("site/submit.html").read_text(encoding="utf-8")


@pytest.mark.parametrize("age,ok", [(18, True), (17, False)])
def test_eligibility_table(age, ok):
    assert is_eligible(age=age) is ok


@pytest.mark.parametrize("address", ["a+b@example.com", "x.y@example.org"])
def test_email_pattern_table(address):
    assert EMAIL_RE.fullmatch(address)


def make_order():
    return Order([("pen", 2, 150)], discount=0.1)


def test_total_through_a_local_factory():
    assert make_order().total == 270


def test_absence_without_a_security_word():
    nav = Path("web/nav.html").read_text(encoding="utf-8")
    assert "/drafts" not in nav


class TestBuiltOnce(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build_site(out="once")

    def test_page_built_by_set_up_class(self):
        self.assertIn('value="Send"', Path("once/submit.html").read_text(encoding="utf-8"))


class TestRenderedAttribute:
    page = render_page("submit")

    def test_label_in_a_class_attribute(self):
        assert 'value="Send"' in self.page


class TestSetUpOnlyReads(unittest.TestCase):
    def setUp(self):
        self.label = SUBMIT_LABEL

    def test_label_read_in_set_up(self):
        self.assertEqual(self.label, "Send")


def test_constant_beside_a_setup_module():
    assert SUBMIT_LABEL == "Send"
