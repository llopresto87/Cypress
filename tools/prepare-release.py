#!/usr/bin/env python3
"""prepare-release: stage the GitHub release notes for the current version.

Seed-only. Absent from manifest.json's `tools` map on purpose: a plant
publishes releases on its own terms, and this script's whole job is specific
to how CYPRESS's own repository ships itself. See CLAUDE.md's Release
section for the full flow.

It does not write prose. `.github/RELEASE_NOTES.md` is the CHANGELOG.md
entry for the current `manifest.json` version, taken verbatim: that entry
already passed canonize's humanizer pass, and drafting a second version of
the same release for the same reader would be a second home for one fact.
`.github/workflows/release.yml` reads the staged file when the matching
`vX.Y.Z` tag is pushed and hands it to `gh release create` unedited — CI has
no access to the judgment `skills/humanizer` and `skill-corpus/discardme.md`
both require, so nothing there may author or rewrite it.

Usage:
    python3 tools/prepare-release.py [--root PATH]

Exit 0 on success (the file is staged and the next commands are printed),
1 when the version has no matching CHANGELOG entry, is already tagged, or
manifest.json's version is not plain semver.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

VERSION_RE = re.compile(r"\d+\.\d+\.\d+")
VERSION_HEADING = re.compile(r"^## (\d+\.\d+\.\d+) — .*$")


class ReleasePrepError(Exception):
    pass


def read_version(manifest_path: Path) -> str:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    version = data.get("version", "")
    if not VERSION_RE.fullmatch(version):
        raise ReleasePrepError(
            f"manifest.json version {version!r} is not plain semver x.y.z"
        )
    return version


def extract_changelog_section(changelog_text: str, version: str) -> str:
    lines = changelog_text.splitlines()
    start = None
    for i, line in enumerate(lines):
        m = VERSION_HEADING.match(line)
        if m and m.group(1) == version:
            start = i
            break
    if start is None:
        raise ReleasePrepError(
            f"no CHANGELOG.md entry for {version} — write it before staging "
            f"the release"
        )
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    section = "\n".join(lines[start:end]).strip("\n")
    return section + "\n"


def tag_exists(root: Path, tag: str) -> bool:
    result = subprocess.run(
        ["git", "tag", "-l", tag],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return bool(result.stdout.strip())


def prepare(root: Path) -> str:
    """Stage the release notes; return the tag name. Raises ReleasePrepError."""
    version = read_version(root / "manifest.json")
    tag = f"v{version}"
    if tag_exists(root, tag):
        raise ReleasePrepError(
            f"tag {tag} already exists locally — bump manifest.json's version "
            f"before staging the next release"
        )
    section = extract_changelog_section(
        (root / "CHANGELOG.md").read_text(encoding="utf-8"), version
    )
    stage = root / ".github" / "RELEASE_NOTES.md"
    stage.parent.mkdir(parents=True, exist_ok=True)
    stage.write_text(section, encoding="utf-8")
    return tag


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Stage .github/RELEASE_NOTES.md from the CHANGELOG.md "
        "entry for the current manifest.json version."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="seed root (default: the repository this script lives in)",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()

    try:
        tag = prepare(root)
    except ReleasePrepError as exc:
        print(f"prepare-release: {exc}", file=sys.stderr)
        return 1

    stage_rel = (root / ".github" / "RELEASE_NOTES.md").relative_to(root)
    print(f"staged {stage_rel} for {tag}")
    print()
    print("next, once the working tree is green (bash tests/run.sh):")
    print(f"  git add {stage_rel}")
    print(f'  git commit -m "stage {tag} release notes"')
    print(f'  git tag -a {tag} -m "{tag}"')
    print(f"  git push && git push origin {tag}")
    print()
    print(
        "pushing the tag is a publish — it needs your explicit go-ahead, "
        "same as any other push (core/method/vcs-posture.md)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
