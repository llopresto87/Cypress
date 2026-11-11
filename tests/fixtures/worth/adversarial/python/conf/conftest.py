"""Fixture: an autouse fixture in a conftest.py beside the test, which has the
code under test write the page the test then reads (independent tester, round 3)."""
import pytest

from app.build import build_site


@pytest.fixture(autouse=True)
def built():
    build_site(out="conf")
