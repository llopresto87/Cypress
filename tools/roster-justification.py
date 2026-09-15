#!/usr/bin/env python3
"""roster-justification: derive the roster's justification table, per component.

HANDOFF Decision C (U-40) asks whether anything in the roster merges or retires,
and says what a justification owes before anyone proposes removing a component
again: the responsibility it holds, the failure it prevents, evidence it has
been used, what overlaps it, and its class.

Four of those five already have a home, or cannot have one:

  responsibility   -> the node's own `title:` and `owns:` keys
  what overlaps it -> the node's own `peers:` edges
  the failure      -> the node's own `prevents:` key (added for this; the one
                      item that was owed and missing, and the only thing this
                      work authored)
  evidence of use  -> NOT DERIVABLE HERE. The only honest signal is usage, and
                      usage happens in grown plants. The seed is not one.
  class            -> NOT DERIVABLE HERE. essential / beneficial / situational /
                      redundant / transitional / obsolete is a CONCLUSION drawn
                      from evidence of use, so it cannot be sounder than the row
                      above it. Asserting one per node would ship a guess with a
                      taxonomy's authority.

So this prints a table and does not publish one. Every column below is read out
of the node that owns it at the moment you run this. The handoff's §6 held the
same table as prose, and two of its nineteen golden-row counts drifted inside a
single session of editing the corpus they count.

WHAT THIS DELIBERATELY DOES NOT PRINT
-------------------------------------
A "named in method" column, and the "thin" label §6 derived from it. That
column counts how often a component's name appears across the method surface.
Measured against routing demand (golden-corpus rows) across the 19 agents it
gave Pearson r = 0.17 across the 19 agents of the day — essentially
unrelated — and it is wrong in
a specific, misleading direction: it scores a component by how much OTHER prose
has to talk about it. A component with a clean boundary is named rarely because
nothing needs to disambiguate it. `devils-advocate` carries the joint-most
golden rows in the roster — 4 contract, 1 paraphrase, 2 adversarial, which is
why this tool prints them per class — and §6 labelled it thin.

Usage:
    python3 tools/roster-justification.py             # the table
    python3 tools/roster-justification.py --markdown  # same, as markdown
    python3 tools/roster-justification.py --gaps      # only nodes missing data
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

import importlib.util as _ilu
_fm_spec = _ilu.spec_from_file_location(
    "cypress_frontmatter", Path(__file__).resolve().parent / "frontmatter.py")
_frontmatter = _ilu.module_from_spec(_fm_spec)
_fm_spec.loader.exec_module(_frontmatter)


UNREADABLE: list[str] = []


def frontmatter(path: Path) -> dict:
    """Delegates to the one frontmatter reader (see frontmatter.py beside this).

    Held its own parser, one of seven. Permissive by accident: any line matching
    neither of its two regexes fell through and was dropped silently.

    A node it cannot read is RECORDED, not skipped. Returning `{}` and letting
    the caller `continue` was the fifth instance of the defect class this
    release fixed in four other linters, and the worst-placed: `--gaps` is a
    gate step, and the node simply left the denominator. `chmod 000` on one
    agent took the report from "0 node(s) with a gap, of 60" to "0 node(s) with
    a gap, of 59", at exit 0, with no diagnostic — and three reference documents
    publish this tool as the home for why each node is on the roster.
    """
    try:
        meta, _body = _frontmatter.parse_file(path)
    except (_frontmatter.FrontmatterError, OSError) as exc:
        rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
        UNREADABLE.append(f"{rel}: {exc}")
        return {}
    return meta


def nodes() -> list[tuple[str, Path]]:
    out = [("protocol", p) for p in sorted((ROOT / "protocols").glob("*.md"))]
    out += [("skill", d / "SKILL.md") for d in sorted((ROOT / "skills").iterdir())
            if (d / "SKILL.md").exists()]
    out += [("agent", p) for p in sorted((ROOT / "agents").glob("*.md"))
            if not p.name.startswith("_")]
    out += [("method", p) for p in sorted((ROOT / "core" / "method").glob("*.md"))]
    return out


def golden_demand() -> dict:
    """Routing demand per agent, BROKEN OUT BY CORPUS CLASS.

    Derived, never transcribed. Zero is not a verdict — `orchestrator` has zero
    because it is the default route, which is correct.

    The class breakdown is not decoration. An earlier version summed the rows
    and printed one number, which is exactly what SPEC-0002 §4
    (`EVERY_NUMBER_NAMES_ITS_CORPUS`) forbids for `--eval`: the classes measure
    different things and merging them hides which one you are looking at. A
    `contract` row is drawn from the agent's own triggers and proves only that a
    trigger still selects its owner; a `paraphrase` row is held-out evidence; an
    `adversarial` row is a bait. "7 golden rows" spanning all three is four
    facts pretending to be one. This tool escaped that spec only because §2
    scopes it to `--eval`, which is a gap in the spec, not a licence.
    """
    counts: dict = {}
    path = ROOT / "agents" / "_routes.golden.tsv"
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = [c.strip() for c in line.split("\t")]
        if len(parts) >= 2:
            cls = parts[2] if len(parts) >= 3 and parts[2] else "contract"
            counts.setdefault(parts[1], Counter())[cls] += 1
    return counts


def rows() -> list[dict]:
    demand = golden_demand()
    out = []
    for kind, path in nodes():
        fm = frontmatter(path)
        if not fm:
            continue   # recorded in UNREADABLE by frontmatter(); see report_unreadable()
        name = fm.get("name") or path.stem
        out.append({
            "kind": kind,
            "name": name,
            "path": str(path.relative_to(ROOT)),
            "responsibility": fm.get("title", ""),
            "owns": fm.get("owns", []),
            "overlaps": fm.get("peers", []),
            "prevents": fm.get("prevents", ""),
            "demand": demand.get(name, Counter()) if kind == "agent" else None,
        })
    return out


def report_unreadable() -> bool:
    """Say which nodes could not be read, and make it an exit condition.

    A node that cannot be read is not a node with nothing to say; it is a node
    nobody looked at. Reporting "0 gaps, of 59" when there are 60 is a smaller
    denominator presented as a clean bill.
    """
    if not UNREADABLE:
        return False
    for line in UNREADABLE:
        print(f"  !! unreadable: {line}", file=sys.stderr)
    print(f"roster-justification: FAIL — {len(UNREADABLE)} node(s) could not be "
          f"read, so they are absent from every count below rather than counted "
          f"as complete", file=sys.stderr)
    return True


def main(argv: list[str]) -> int:
    data = rows()
    unreadable = report_unreadable()
    if "--gaps" in argv:
        gaps = [r for r in data if not r["prevents"] or not r["overlaps"]]
        for r in gaps:
            missing = [k for k in ("prevents", "overlaps") if not r[k]]
            print(f"{r['path']}: missing {', '.join(missing)}")
        print(f"\n{len(gaps)} node(s) with a gap, of {len(data)}")
        return 1 if (gaps or unreadable) else 0

    md = "--markdown" in argv
    for kind in ("agent", "protocol", "skill", "method"):
        group = [r for r in data if r["kind"] == kind]
        print(f"\n## {kind}s ({len(group)})\n")
        for r in group:
            if r["demand"] is None:
                demand = ""
            elif not r["demand"]:
                demand = "  [golden rows: none]"
            else:
                per = ", ".join(f"{n} {c}" for c, n in sorted(r["demand"].items()))
                demand = f"  [golden rows: {per}]"
            if md:
                print(f"### `{r['name']}`{demand}\n")
                print(f"- **responsibility** — {r['responsibility']}")
                print(f"- **prevents** — {r['prevents']}")
                print(f"- **overlaps** — {', '.join(r['overlaps']) or 'none declared'}")
                print(f"- **owns** — {', '.join(r['owns'])}\n")
            else:
                print(f"{r['name']}{demand}")
                print(f"    responsibility  {r['responsibility']}")
                print(f"    prevents        {r['prevents']}")
                print(f"    overlaps        {', '.join(r['overlaps']) or 'none declared'}")
                print()

    print("\n" + "=" * 74)
    print(f"{len(data)} machinery nodes, every column read from the node that owns it.")
    print()
    print("NOT SHOWN, because the seed cannot source it:")
    print("  evidence of use — needs a grown plant's spawn and protocol-entry record")
    print("  class           — a conclusion drawn from evidence of use; without")
    print("                    that row it would be a guess wearing a taxonomy")
    print()
    print("Golden rows measure ROUTING DEMAND, not value, and only for agents.")
    print("They are shown PER CORPUS CLASS and never summed: a `contract` row is")
    print("drawn from the agent's own triggers and proves only that a trigger still")
    print("selects its owner; `paraphrase` is held-out evidence; `adversarial` is a")
    print("bait. Merging them is what SPEC-0002 forbids for --eval.")
    print("`orchestrator` reads none because it is the default route.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
