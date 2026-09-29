#!/usr/bin/env python3
r"""verify-ledger: prove a plan's ledger conversion byte for byte.

A plan converted to a ledger keeps its §9 increments as leaf files in the
directory beside it and a §9 index table that points at them. The conversion
is sound only when the ledger and its leaves rebuild the plan it came from
exactly. Counting characters proves nothing about bytes: a multibyte
character is one character and two or more bytes. So this rebuilds the file
and compares bytes.

The rebuild rule: the rebuilt file is the ledger plan with each §9 index
table (the contiguous lines from a `| # | Increment | Status | Detail |` header
row through its last index row) replaced by the content of that table's
indexed leaves, in row order, joined by one newline byte (`\n`). A §9 that
grew appended subsections carries one index table per part; every table
counts, in document order. Every byte outside the tables is kept as it is.
A leaf is used verbatim: no pointer line is stripped. The byte count printed
is the UTF-8 length of the rebuilt file.

It fails (exit 1) when the rebuild differs from the monolith, naming the
first differing byte as a 0-based offset in the rebuilt file and, when that
byte came from a leaf, the leaf and the offset in it; when a row points at a
leaf that does not exist; and when a leaf in the directory is named by no row,
because a leaf nobody indexes is text the rebuild silently drops.

Usage:
  python3 tools/verify-ledger.py --monolith M --ledger P --leaves D
      M  the plan as one file, before the conversion
      P  the ledger plan (its §9 holds the index tables)
      D  the directory holding the leaves (beside P, named for its stem)

Exit 0 on an exact rebuild, 1 on a mismatch or a ledger defect, 2 on a usage
or read error. Stdlib only; it writes nothing.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HEADER = ["#", "Increment", "Status", "Detail"]
ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|")
LEAF_RE = re.compile(r"([\w./-]*[\w.-]+\.md)")


def cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def index_tables(lines: list[bytes]) -> list[tuple[int, int, list[str]]]:
    """(first line, line after the last index row, leaf names in row order)
    of each index table, in document order; empty when the plan has no such
    header row."""
    text = [ln.decode("utf-8", errors="replace").rstrip("\r\n") for ln in lines]
    tables: list[tuple[int, int, list[str]]] = []
    start = 0
    while start < len(text):
        ln = text[start]
        if not (ln.lstrip().startswith("|") and cells(ln) == HEADER):
            start += 1
            continue
        end, leaves = start + 1, []
        for i in range(start + 1, len(text)):
            if not text[i].lstrip().startswith("|"):
                break
            if ROW_RE.match(text[i].lstrip()):
                m = LEAF_RE.search("|".join(cells(text[i])[1:]).replace("`", " "))
                if m:
                    leaves.append(Path(m.group(1)).name)
                end = i + 1
        tables.append((start, end, leaves))
        start = end
    return tables


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="verify-ledger.py",
        description="Prove that a ledger plan and its leaves rebuild the monolith byte for byte.")
    ap.add_argument("--monolith", required=True, type=Path, help="the plan as one file, before the conversion")
    ap.add_argument("--ledger", required=True, type=Path, help="the ledger plan, whose §9 is the index table")
    ap.add_argument("--leaves", required=True, type=Path, help="the directory holding the leaves")
    args = ap.parse_args()

    try:
        monolith = args.monolith.read_bytes()
        lines = args.ledger.read_bytes().splitlines(keepends=True)
    except OSError as e:
        print(f"verify-ledger: cannot read: {e}", file=sys.stderr)
        return 2
    if not args.leaves.is_dir():
        print(f"verify-ledger: no leaves directory at {args.leaves}", file=sys.stderr)
        return 2

    tables = index_tables(lines)
    if not tables:
        print(f"verify-ledger: FAIL: {args.ledger.name} has no index table "
              f"(a `| {' | '.join(HEADER)} |` header row)")
        return 1
    names = [name for _, _, table in tables for name in table]

    defects: list[str] = []
    for f in sorted(args.leaves.rglob("*.md")):
        rel = f.relative_to(args.leaves).as_posix()
        if rel not in names:
            defects.append(f"{rel} is a leaf no index row points at; the rebuild would drop it")
    leaves: dict[str, bytes] = {}
    for name in names:
        p = args.leaves / name
        if not p.is_file():
            defects.append(f"an index row points at {name}, which is not in {args.leaves}")
            continue
        leaves[name] = p.read_bytes()
    if defects:
        print(f"verify-ledger: FAIL: {len(defects)} ledger defect(s):")
        for d in defects:
            print(f"  - {d}")
        return 1

    # The rebuild, table by table, with the span each leaf occupies in it.
    parts: list[bytes] = []
    spans: list[tuple[str, int, int]] = []
    at = kept = 0
    for start, end, table in tables:
        parts.append(b"".join(lines[kept:start]))
        at += len(parts[-1])
        for i, name in enumerate(table):
            if i:
                parts.append(b"\n")
                at += 1
            spans.append((name, at, at + len(leaves[name])))
            parts.append(leaves[name])
            at += len(leaves[name])
        kept = end
    parts.append(b"".join(lines[kept:]))
    rebuilt = b"".join(parts)

    if rebuilt == monolith:
        print(f"verify-ledger: PASS: {len(rebuilt)} bytes; {args.ledger.name} and "
              f"{len(names)} leaves rebuild {args.monolith.name} exactly")
        return 0

    off = next((i for i, (a, b) in enumerate(zip(rebuilt, monolith)) if a != b),
               min(len(rebuilt), len(monolith)))
    where = next(((n, off - s) for n, s, e in spans if s <= off < e), None)
    print(f"verify-ledger: FAIL: the rebuild ({len(rebuilt)} bytes) differs from "
          f"{args.monolith.name} ({len(monolith)} bytes)")
    print(f"  first differing byte: offset {off} in the rebuilt file (0-based)")
    if where:
        print(f"  it comes from the leaf {where[0]}, at offset {where[1]} in the leaf (0-based)")
    else:
        print(f"  it comes from {args.ledger.name}, outside the index tables")
    return 1


if __name__ == "__main__":
    sys.exit(main())
