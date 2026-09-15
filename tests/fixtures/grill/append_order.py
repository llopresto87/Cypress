"""Rewrite §9 so increment 3 is APPENDED after 1 and 2, and 2 depends on it.

Legal in document order — the dependency is written before the dependent — and
the convention this seed prescribes (append, do not renumber). It failed the
moment increments() sorted numerically.
"""
import re
import sys
from pathlib import Path

p = Path(sys.argv[1])
t = p.read_text()
s, e = t.index("## 9. Implementation Plan"), t.index("## 10.")
blocks = re.split(r"(?=^### Increment )", t[s:e], flags=re.M)
head, incs = blocks[0], blocks[1:]
appended = "\n".join([
    "### Increment 3 — Appended later",
    "- Spec contracts: none",
    "- Files touched: src/x.py",
    "- Tests to write (RED): tests/test_x.py::test_x",
    "- Behavior added: x",
    "- Gate: pytest",
    "- Rollback path: revert",
    "- Effort: S",
    "- Depends on: increment 1",
    "", "",
])
incs[-1] = incs[-1].rstrip() + "\n- Depends on: increment 1; increment 3\n\n"
p.write_text(t[:s] + head + incs[0] + appended + incs[1] + t[e:])
