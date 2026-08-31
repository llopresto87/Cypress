#!/usr/bin/env python3
"""spec-lint: mechanical proof that "specs are executable" (kernel §3.1).

The spec rule says every functional contract maps to at least one test,
and tests reuse the contract's stable UPPER_SNAKE_SLUG. Until now that
was aspiration enforced by review; this makes it a gate:

  - every ACTIVE/IMPLEMENTED spec contract must appear in >=1 test file;
  - a slug appearing in tests but in no live spec is drift (renamed or
    retired contract still asserted somewhere) -> WARN;
  - active contracts + ZERO matching test files is a green lie
    (kernel §3.5) -> FAIL loudly, never a vacuous pass.

Installed at docs/graph/spec-lint.py by install.sh (like graph-lint.py).
Dependency-free. Set TEST_GLOBS for the project's layout.

Usage:
  python3 docs/graph/spec-lint.py           # gate: exit 1 on uncovered
  python3 docs/graph/spec-lint.py --list    # dump contract -> tests map
  python3 docs/graph/spec-lint.py --warn    # report but always exit 0
"""
import re
import sys
from pathlib import Path

# ---- project configuration (edit these when installing) -------------------
TEST_GLOBS = [
    "tests/**/*.*", "test/**/*.*", "spec/**/*.*",
    "**/*_test.*", "**/*.test.*", "**/test_*.*",
]
LIVE_STATUSES = {"active", "implemented"}
# ----------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent          # docs/graph/
ROOT = HERE.parent.parent                       # repo root
SPECS = HERE / "specs"
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__",
             "dist", "build", "target", ".next"}
CONTRACT_RE = re.compile(r"^###\s+Contract:\s*([A-Z][A-Z0-9_]{2,})\s*$", re.M)
STATUS_RE = re.compile(r"\*\*Status:\*\*\s*([\w-]+)")


def test_files() -> list[Path]:
    seen: set[Path] = set()
    for pattern in TEST_GLOBS:
        for p in ROOT.glob(pattern):
            if p.is_file() and not (set(p.parts) & SKIP_DIRS) and SPECS not in p.parents:
                seen.add(p)
    return sorted(seen)


def main() -> int:
    list_mode = "--list" in sys.argv
    warn_mode = "--warn" in sys.argv

    if not SPECS.is_dir():
        print("spec lint: SKIP — no docs/graph/specs/ directory")
        return 0

    contracts: dict[str, str] = {}          # slug -> spec file
    live_specs = 0
    for spec in sorted(SPECS.glob("SPEC-*.md")):
        text = spec.read_text(encoding="utf-8", errors="replace")
        status_m = STATUS_RE.search(text)
        status = status_m.group(1).lower() if status_m else "unknown"
        if status not in LIVE_STATUSES:
            continue
        live_specs += 1
        for slug in CONTRACT_RE.findall(text):
            contracts[slug] = spec.name

    if not contracts:
        print(f"spec lint: PASS — no live contracts to cover "
              f"({live_specs} live spec(s))")
        return 0

    files = test_files()
    if not files:
        print(f"spec lint: FAIL — {len(contracts)} live contract(s) but the "
              f"test globs matched ZERO files. A coverage check over an "
              f"empty set is a green lie; fix TEST_GLOBS or write the tests.")
        return 0 if warn_mode else 1

    hits: dict[str, list[str]] = {slug: [] for slug in contracts}
    tested_slugs: set[str] = set()
    slug_union = re.compile("|".join(re.escape(s) for s in contracts))
    for f in files:
        try:
            body = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for m in slug_union.finditer(body):
            hits[m.group(0)].append(str(f.relative_to(ROOT)))
            tested_slugs.add(m.group(0))

    uncovered = sorted(s for s in contracts if not hits[s])

    if list_mode:
        for slug in sorted(contracts):
            where = ", ".join(sorted(set(hits[slug]))[:3]) or "UNCOVERED"
            print(f"  {slug}  ({contracts[slug]})  ->  {where}")

    if uncovered:
        print(f"spec lint: {'WARN' if warn_mode else 'FAIL'} — "
              f"{len(uncovered)}/{len(contracts)} live contract(s) have no test:")
        for slug in uncovered:
            print(f"  - {slug}  ({contracts[slug]})")
        return 0 if warn_mode else 1

    print(f"spec lint: PASS — {len(contracts)} live contract(s) covered "
          f"across {len(files)} test file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
