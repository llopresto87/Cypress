"""Fixture: a third round of adversarial cases by the independent tester:
setup variants that run the code under test before a test reads its output.
Verdicts are in tests/fixtures/worth/adversarial.tsv, written first."""
import unittest
from pathlib import Path

from app.build import build_site


class TestBuiltAsync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await build_site(out="async")

    async def test_page_built_by_async_set_up(self):
        self.assertIn('value="Send"', Path("async/submit.html").read_text(encoding="utf-8"))


class TestBuiltPerMethod:
    def setup_method(self, method):
        build_site(out="method")

    def test_page_built_by_setup_method(self):
        assert 'value="Send"' in Path("method/submit.html").read_text(encoding="utf-8")


class TestBuiltPerClass:
    @classmethod
    def setup_class(cls):
        build_site(out="klass")

    def test_page_built_by_setup_class(self):
        assert 'value="Send"' in Path("klass/submit.html").read_text(encoding="utf-8")
