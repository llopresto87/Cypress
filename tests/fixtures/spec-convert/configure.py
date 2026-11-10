"""Fixture helper: give a copy of spec-lint.py the plant's own test layout.

    python3 configure.py <spec-lint.py in> <spec-lint.py out>

The plant reads its tests from tests/ and checks/ and from any *_test.py, and
skips a vendored directory: TEST_GLOBS and SKIP_DIRS both differ from the
seed's defaults, so an engine reconcile that drops either one changes what the
engine reads. Works on the engine of any seed version that carries the two
assignments at top level.
"""
import re
import sys

src = open(sys.argv[1], encoding="utf-8").read()
src, n1 = re.subn(r"^TEST_GLOBS = \[.*?\n\]", 'TEST_GLOBS = ["tests/**/*.py", "checks/**/*.py", "**/*_test.py"]',
                  src, count=1, flags=re.S | re.M)
src, n2 = re.subn(r"^SKIP_DIRS = \{.*?\}", 'SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__", "vendor"}',
                  src, count=1, flags=re.S | re.M)
if n1 != 1 or n2 != 1:
    sys.exit(f"configure.py: {sys.argv[1]} has no top-level TEST_GLOBS list or SKIP_DIRS set")
open(sys.argv[2], "w", encoding="utf-8").write(src)
