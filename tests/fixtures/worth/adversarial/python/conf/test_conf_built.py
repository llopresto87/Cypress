"""Fixture: reads a page an autouse fixture of conftest.py had the code under
test write (independent tester, round 3; verdict in adversarial.tsv)."""
from pathlib import Path


def test_page_built_by_a_conftest_fixture():
    assert 'value="Send"' in Path("conf/submit.html").read_text(encoding="utf-8")
