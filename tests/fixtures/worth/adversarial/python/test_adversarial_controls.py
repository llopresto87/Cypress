"""Fixture: a second round of adversarial cases by the independent tester, in a
file with no setup hook, written with their verdicts in
tests/fixtures/worth/adversarial.tsv before worth-check.py ran over them. Each
probes the narrowed sparing rules for a false positive."""
from pathlib import Path

import pytest

from app.settings import HEADERS, SETTINGS, SUBMIT_LABEL, TEMPLATE_LABEL
from app.uploads import store


def test_absence_of_a_draft_link():
    nav = Path("web/nav.html").read_text(encoding="utf-8")
    assert "/drafts" not in nav


def test_absence_beside_a_presence():
    nav = Path("web/nav.html").read_text(encoding="utf-8")
    assert "/internal" not in nav
    assert "/help" in nav


def test_oversized_upload_raises():
    with pytest.raises(ValueError):
        store(b"x" * 10_000_000)


def test_policy_header_held_in_a_keyed_setting():
    assert HEADERS["Content-Security-Policy"] == "default-src 'self'"


def test_cookie_flag_held_in_a_keyed_setting():
    assert SETTINGS["SESSION_COOKIE_SECURE"] is True


def test_two_homes_held_equal():
    assert SUBMIT_LABEL == TEMPLATE_LABEL
