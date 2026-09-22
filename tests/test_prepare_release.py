#!/usr/bin/env python3
"""tools/prepare-release.py's own regression.

The script stages .github/RELEASE_NOTES.md from the CHANGELOG.md entry for
the current manifest.json version — the file
.github/workflows/release.yml reads when a matching vX.Y.Z tag is pushed.
Nothing else in the gate touches this path, so its own suite holds both the
extraction logic (unit) and the CLI's exit behaviour end to end (integration,
against a disposable temp repo — never the seed's own CHANGELOG.md, which
would make the test's pass condition move every time a release ships).

Stdlib unittest, like every other suite here; no third-party imports.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEED = HERE.parent
TOOL = SEED / "tools" / "prepare-release.py"


def load_tool():
    spec = importlib.util.spec_from_file_location("prepare_release_under_test", TOOL)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["prepare_release_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


TOOL_MOD = load_tool()

SAMPLE_CHANGELOG = """# Changelog

## 2.0.0 — the second entry, newer than the first (2026-01-02)

Body of the second entry. Two paragraphs.

Second paragraph.

## Seed integrity gate (verdicts only)

Not a version heading; must never be mistaken for one.

## 1.0.0 — the first entry (2026-01-01)

Body of the first entry.
"""


class ExtractionTests(unittest.TestCase):
    """The pure functions, against fixture text — no filesystem, no git."""

    def test_extracts_the_matching_version_section(self):
        section = TOOL_MOD.extract_changelog_section(SAMPLE_CHANGELOG, "1.0.0")
        self.assertTrue(section.startswith("## 1.0.0 — the first entry"))
        self.assertIn("Body of the first entry.", section)
        self.assertNotIn("second entry", section)

    def test_stops_at_the_next_level_two_heading_even_when_not_a_version(self):
        section = TOOL_MOD.extract_changelog_section(SAMPLE_CHANGELOG, "2.0.0")
        self.assertIn("Second paragraph.", section)
        self.assertNotIn("Seed integrity gate", section)
        self.assertNotIn("first entry", section)

    def test_missing_version_raises(self):
        with self.assertRaises(TOOL_MOD.ReleasePrepError):
            TOOL_MOD.extract_changelog_section(SAMPLE_CHANGELOG, "9.9.9")

    def test_non_semver_manifest_version_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "manifest.json"
            manifest.write_text(json.dumps({"version": "7.26"}), encoding="utf-8")
            with self.assertRaises(TOOL_MOD.ReleasePrepError):
                TOOL_MOD.read_version(manifest)

    def test_plain_semver_reads_cleanly(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "manifest.json"
            manifest.write_text(json.dumps({"version": "1.2.3"}), encoding="utf-8")
            self.assertEqual(TOOL_MOD.read_version(manifest), "1.2.3")


class CliTests(unittest.TestCase):
    """End to end, against a disposable temp repo — never the seed's own."""

    def _repo(self, tmp: str, version: str, changelog: str) -> Path:
        root = Path(tmp)
        (root / "manifest.json").write_text(
            json.dumps({"version": version}), encoding="utf-8"
        )
        (root / "CHANGELOG.md").write_text(changelog, encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.invalid"],
            cwd=root, check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "test"], cwd=root, check=True
        )
        return root

    def _run(self, root: Path):
        return subprocess.run(
            [sys.executable, str(TOOL), "--root", str(root)],
            capture_output=True,
            text=True,
        )

    def test_stages_the_file_and_prints_the_next_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp, "1.0.0", SAMPLE_CHANGELOG)
            result = self._run(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            staged = root / ".github" / "RELEASE_NOTES.md"
            self.assertTrue(staged.is_file())
            self.assertIn("first entry", staged.read_text(encoding="utf-8"))
            self.assertIn("v1.0.0", result.stdout)
            self.assertIn("git push && git push origin v1.0.0", result.stdout)

    def test_missing_changelog_entry_fails_loudly(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp, "9.9.9", SAMPLE_CHANGELOG)
            result = self._run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("no CHANGELOG.md entry", result.stderr)
            self.assertFalse((root / ".github" / "RELEASE_NOTES.md").exists())

    def test_already_tagged_version_fails_loudly(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp, "1.0.0", SAMPLE_CHANGELOG)
            (root / "f").write_text("x", encoding="utf-8")
            subprocess.run(["git", "add", "f"], cwd=root, check=True)
            subprocess.run(
                ["git", "commit", "-q", "-m", "init"], cwd=root, check=True
            )
            subprocess.run(["git", "tag", "v1.0.0"], cwd=root, check=True)
            result = self._run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("already exists", result.stderr)

    def test_help_exits_zero(self):
        result = subprocess.run(
            [sys.executable, str(TOOL), "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertTrue(result.stdout.strip())


if __name__ == "__main__":
    unittest.main()
