"""Fixture: security negative controls. Each asserts that something is refused
or absent; worth-check.py flags none of them."""
from pathlib import Path

import pytest

from app.settings import PRODUCTION, SESSION_COOKIE_SECURE
from app.uploads import safe_upload_path


def test_upload_name_with_traversal_is_refused():
    with pytest.raises(ValueError):
        safe_upload_path("../../etc/passwd")


def test_debug_is_off_in_production_settings():
    assert PRODUCTION["DEBUG"] is False


def test_admin_page_not_linked_from_public_nav():
    nav = Path("web/nav.html").read_text(encoding="utf-8")
    assert "/admin" not in nav


def test_session_cookie_flag():
    assert SESSION_COOKIE_SECURE is True
