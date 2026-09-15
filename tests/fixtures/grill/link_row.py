"""Rewrite one index row as five columns with a markdown link.

The first INDEX_ROW_RE demanded exactly four columns with the path alone in the
fourth, so an added column or a `[detail](path)` link went unseen — and an
unseen row is an increment nothing validates.
"""
import re
import sys
from pathlib import Path

p = Path(sys.argv[1])
t = re.sub(
    r"\| 2 \| ([^|]*)\| ([^|]*)\| `(plans/grill/[^`]*)` \|",
    r"| 2 | \1| \2| me | [detail](\3) |",
    p.read_text(), count=1)
p.write_text(t)
