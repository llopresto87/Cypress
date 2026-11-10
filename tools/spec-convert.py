#!/usr/bin/env python3
"""spec-convert.py — convert one plant spec from the legacy form to the kinds
form, the mechanical part only (SPEC-0010).

A legacy spec has no `- **Contract form:** kinds` line in its §0 Metadata, and
its plant's spec-lint reads each unlabelled contract as kind test, linked to
its test by the §10 row and the slug in the test's code. The kinds form gives
each contract a `- **Check:**` line of kind test, run, review or covered, adds
a declared-values table, and designs §10 by risk. Converting a spec is a shape
migration the steward ratifies in the graft's shape-migration section
(protocols/graft.md); this tool does only its mechanical part, and the plant's
architect does the judgment after the ratification.

The mechanical part, and nothing else:
  §0  adds `- **Contract form:** kinds` and `- **Trust path:** no` (before the
      Sign-offs line, else after the section's last bullet); a Trust path line
      already present is kept;
  §4  gives each contract with no Check line `- **Check:** test`, after the
      last bullet of its block; a contract already labelled keeps its line.
Given/When/Then, §7, §9, the §10 table and its header, and the changelog stay
byte for byte. The report names each contract's present mapping (its §10 row,
and the slug in the plant's tests as the plant's spec-lint.py TEST_GLOBS and
SKIP_DIRS find it), which the architect keeps as evidence or replaces.

The judgment it leaves alone: re-labelling a contract run, review or covered,
writing a declared-values table, designing a risk-based §10, setting the
Trust path to yes for a security, data-integrity or money contract.

It runs from the seed against a plant's spec path, like the graft tools, and is
never placed in a plant: no install, graft step or tool runs it unless the
steward starts it.

Usage:
  spec-convert.py [--dry-run] SPEC_PATH [--root DIR]
  spec-convert.py --write --steward-ratified SPEC_PATH [--root DIR]
  spec-convert.py --help

  --dry-run           print the report and write nothing (the default)
  --write             write the mechanical part; refused unless
                      --steward-ratified and SPEC_PATH are both given. The
                      spec as it was is kept beside it as
                      SPEC_PATH.bak-<YYYYmmdd-HHMMSS>
  --steward-ratified  the steward ratified this conversion in the graft record
  --root DIR          the plant root, where docs/graph/spec-lint.py declares
                      the test layout (default: three levels above a spec
                      under docs/graph/specs/)

Exit 0: the report was printed, the spec was written, or it is already in the
kinds form. Exit 1: the spec's shape is not recognised (named; nothing
written). Exit 2: a usage error, a refused --write, or an unreadable path.
Dependency-free.
"""
from __future__ import annotations

import ast
import os
import re
import shutil
import sys
import time
from pathlib import Path

# the plant engine's own patterns (templates/knowledge-graph/spec-lint.py)
CONTRACT_RE = re.compile(r"^###\s+Contract:\s*([A-Z][A-Z0-9_]{2,})\s*$")
CONTRACT_ANY_RE = re.compile(r"^#{1,6}\s+Contract:\s*([A-Z][A-Z0-9_]{2,})\s*$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
SECTION0_RE = re.compile(r"^0\.")
SECTION10_RE = re.compile(r"^10\.")
FORM_LINE_RE = re.compile(r"^- \*\*Contract form:\*\*\s*(.*?)\s*$")
TRUST_LINE_RE = re.compile(r"^- \*\*Trust path:\*\*\s*(.*?)\s*$")
SIGNOFF_RE = re.compile(r"^- \*\*Sign-offs:\*\*")
CHECK_RE = re.compile(r"^- \*\*Check:\*\*[ \t]*(.*)$")
BULLET_RE = re.compile(r"^- \*\*")
PIPE_RE = re.compile(r"(?<!\\)\|")
DELIM_ROW_RE = re.compile(r"^\s*\|?\s*:?-+:?\s*(?:\|\s*:?-+:?\s*)*\|?\s*$")
SPEC_NAME_RE = re.compile(r"^SPEC-.+\.md$")
DEFAULT_SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__",
                     "dist", "build", "target", ".next"}

FORM_LINE = "- **Contract form:** kinds"
TRUST_LINE = "- **Trust path:** no"
CHECK_LINE = "- **Check:** test"
UNCHANGED = (" unchanged: Given/When/Then, §7, §9, §10 header (legacy §10 stays valid), "
             "changelog")
JUDGMENT = (" judgment, NOT done here: re-labelling a contract run / review / covered, a "
            "declared-values table, a risk-based §10: the plant's architect, after the "
            "steward ratifies")


class Usage(Exception):
    """A usage error or a refused write: exit 2."""


def parse(argv: list[str]) -> dict:
    opts = {"dry": False, "write": False, "ratified": False, "root": None, "paths": []}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--help", "-h"):
            print(__doc__)
            sys.exit(0)
        if a == "--dry-run":
            opts["dry"] = True
        elif a == "--write":
            opts["write"] = True
        elif a == "--steward-ratified":
            opts["ratified"] = True
        elif a == "--root" or a.startswith("--root="):
            if a == "--root":
                if i + 1 >= len(argv) or argv[i + 1].startswith("-"):
                    raise Usage("--root needs a directory")
                opts["root"], i = argv[i + 1], i + 1
            else:
                opts["root"] = a.split("=", 1)[1]
        elif a.startswith("-"):
            raise Usage(f"unknown option {a}")
        else:
            opts["paths"].append(a)
        i += 1
    if opts["dry"] and opts["write"]:
        raise Usage("--dry-run and --write name two modes; choose one")
    if len(opts["paths"]) > 1:
        raise Usage(f"one spec path per run; got {len(opts['paths'])}")
    if opts["write"]:
        missing = ([] if opts["ratified"] else ["--steward-ratified"]) + \
                  ([] if opts["paths"] else ["the spec path"])
        if missing:
            raise Usage(f"--write refused: it needs --steward-ratified and the spec path, "
                        f"and this run lacks {' and '.join(missing)}. The steward ratifies "
                        f"the conversion in the graft record's shape-migration section "
                        f"first; nothing written")
    elif not opts["paths"]:
        raise Usage("name the spec path to report on")
    return opts


# -- reading the spec ---------------------------------------------------------

def outline(lines: list[str]):
    """(headings outside fences as (index, level, text), the index of each line
    inside a fence)."""
    heads, fenced, fence = [], set(), None
    for i, raw in enumerate(lines):
        line = raw.rstrip("\r\n")
        m = FENCE_RE.match(line)
        if fence:
            fenced.add(i)
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) \
                    and not line.strip()[len(m.group(1)):].strip():
                fence = None
            continue
        if m:
            fence = m.group(1)
            fenced.add(i)
            continue
        h = HEADING_RE.match(line)
        if h:
            heads.append((i, len(h.group(1)), h.group(2)))
    return heads, fenced


def block_end(heads, at: int, nlines: int, max_level: int) -> int:
    """The index of the first heading after line `at` of level <= max_level."""
    for i, level, _ in heads:
        if i > at and level <= max_level:
            return i
    return nlines


def after_last_bullet(lines: list[str], start: int, end: int, fenced: set) -> int | None:
    """The index after the block's last `- **...` bullet and its continuation
    lines, or None when the block has no bullet."""
    last = None
    for i in range(start, end):
        if i not in fenced and BULLET_RE.match(lines[i]):
            last = i
    if last is None:
        return None
    j = last + 1
    while j < end and j not in fenced and lines[j].strip() and lines[j][:1] in (" ", "\t"):
        j += 1
    return j


def cells_of(line: str) -> list[str]:
    s = line.strip()
    s = s[1:] if s.startswith("|") else s
    s = s[:-1] if s.endswith("|") and not s.endswith("\\|") else s
    return [c.strip().strip("`").strip() for c in PIPE_RE.split(s)]


def section10_rows(lines: list[str], heads, fenced: set) -> dict[str, list[str]]:
    """{contract: [a note per §10 row naming it]} from every table in §10: a
    legacy row by its first cell, a risk row by its Covers cell."""
    sec = next((h for h in heads if h[1] == 2 and SECTION10_RE.match(h[2])), None)
    if not sec:
        return {}
    end = block_end(heads, sec[0], len(lines), 2)
    rows: dict[str, list[str]] = {}
    header = None
    for i in range(sec[0] + 1, end):
        line = lines[i].rstrip("\r\n")
        if i in fenced or not PIPE_RE.search(line):
            header = None
            continue
        if DELIM_ROW_RE.match(line):
            continue
        cells = cells_of(line)
        nxt = lines[i + 1].rstrip("\r\n") if i + 1 < end else ""
        if header is None or DELIM_ROW_RE.match(nxt):
            header = [c.lower() for c in cells]
            continue
        if header and header[0].startswith("risk") and "covers" in header:
            ci = header.index("covers")
            ti = next((k for k, c in enumerate(header) if c.startswith("test")), 1)
            covers = [t.strip().strip("`") for t in (cells[ci] if ci < len(cells) else "").split(",")]
            for slug in filter(None, covers):
                rows.setdefault(slug, []).append(cells[ti] if ti < len(cells) else "")
        elif cells and cells[0]:
            rows.setdefault(cells[0], []).append(", ".join(c for c in cells[1:3] if c))
    return rows


# -- the plant's tests --------------------------------------------------------

def plant_root(spec: Path, given: str | None) -> Path | None:
    if given:
        return Path(given)
    p = spec.resolve().parents
    if len(p) > 3 and p[0].name == "specs" and p[1].name == "graph" and p[2].name == "docs":
        return p[3]
    return None


def test_layout(root: Path):
    """(TEST_GLOBS, SKIP_DIRS) from the plant's docs/graph/spec-lint.py, read
    with ast and never imported; None when the plant declares no TEST_GLOBS."""
    try:
        tree = ast.parse((root / "docs/graph/spec-lint.py").read_text(encoding="utf-8"))
    except (OSError, SyntaxError, ValueError, UnicodeDecodeError):
        return None
    found = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id in ("TEST_GLOBS", "SKIP_DIRS"):
                    try:
                        found[t.id] = ast.literal_eval(node.value)
                    except (ValueError, TypeError, SyntaxError):
                        pass
    globs = found.get("TEST_GLOBS")
    if not isinstance(globs, list) or not all(isinstance(g, str) for g in globs):
        return None
    skip = found.get("SKIP_DIRS", DEFAULT_SKIP_DIRS)
    return globs, set(skip) if isinstance(skip, (set, list, tuple)) else DEFAULT_SKIP_DIRS


def slug_hits(root: Path, layout, slugs: list[str]) -> dict[str, list[str]]:
    """{slug: [plant-relative test files naming it]}, the slug or its lower-case
    form, guarded at word edges as the plant's spec-lint guards them."""
    globs, skip = layout
    specs = (root / "docs/graph/specs").resolve()
    files = set()
    for g in globs:
        for f in root.glob(g):
            if f.is_file() and not (set(f.relative_to(root).parts) & skip) \
                    and specs not in f.resolve().parents:
                files.add(f)
    out: dict[str, list[str]] = {s: [] for s in slugs}
    pats = {s: (re.compile(rf"(?<![A-Z0-9_]){re.escape(s)}(?![A-Z0-9_])"),
                re.compile(rf"(?<![a-z0-9]){re.escape(s.lower())}(?![a-z0-9_])")) for s in slugs}
    for f in sorted(files):
        try:
            body = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = f.relative_to(root).as_posix()
        for s, (up, low) in pats.items():
            if up.search(body) or low.search(body):
                out[s].append(rel)
    return out


# -- the conversion -----------------------------------------------------------

def read_spec(spec: Path):
    """The parsed spec, or a list of the reasons its shape is not recognised."""
    try:
        text = spec.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise Usage(f"{spec}: not UTF-8 text; nothing written") from None
    except OSError as e:
        raise Usage(f"{spec}: cannot be read ({e.strerror or e}); nothing written") from None
    lines = text.splitlines(keepends=True)
    heads, fenced = outline(lines)
    problems = []
    if not SPEC_NAME_RE.match(spec.name):
        problems.append("the file name is not SPEC-*.md, so the plant's spec-lint reads it as misnamed")
    sec0 = next((h for h in heads if h[1] == 2 and SECTION0_RE.match(h[2])), None)
    if not sec0:
        problems.append("no `## 0.` metadata section")
    for i in sorted(fenced):
        if CONTRACT_ANY_RE.match(lines[i].rstrip("\r\n")):
            problems.append(f"a `### Contract:` heading inside a code fence at line {i + 1}, "
                            f"which the plant's spec-lint still reads as a contract")
    contracts = []
    for i, level, _ in heads:
        m = CONTRACT_RE.match(lines[i].rstrip("\r\n"))
        if level == 3 and m:
            contracts.append((i, m.group(1)))
    if not contracts:
        problems.append("no `### Contract:` heading")
    form = None
    if sec0:
        end0 = block_end(heads, sec0[0], len(lines), 2)
        for i in range(sec0[0] + 1, end0):
            m = FORM_LINE_RE.match(lines[i].rstrip("\r\n")) if i not in fenced else None
            if m:
                form = m.group(1)
        if form is not None and form != "kinds":
            problems.append(f"§0 declares `Contract form: {form}`, a form this tool does not know")
    if problems:
        return problems
    return {"text": text, "lines": lines, "heads": heads, "fenced": fenced,
            "sec0": sec0, "contracts": contracts, "kinds": form == "kinds"}


def plan(s: dict) -> tuple[list[tuple[int, str]], dict]:
    """[(insert before line index, line)] and what the report says."""
    lines, heads, fenced = s["lines"], s["heads"], s["fenced"]
    inserts = []
    end0 = block_end(heads, s["sec0"][0], len(lines), 2)
    trust = None
    signoff = None
    for i in range(s["sec0"][0] + 1, end0):
        if i in fenced:
            continue
        line = lines[i].rstrip("\r\n")
        m = TRUST_LINE_RE.match(line)
        if m:
            trust = m.group(1)
        if signoff is None and SIGNOFF_RE.match(line):
            signoff = i
    at0 = signoff if signoff is not None else (
        after_last_bullet(lines, s["sec0"][0] + 1, end0, fenced) or s["sec0"][0] + 1)
    inserts.append((at0, FORM_LINE))
    if trust is None:
        inserts.append((at0, TRUST_LINE))
    todo, kept = [], []
    for at, slug in s["contracts"]:
        end = block_end(heads, at, len(lines), 3)
        check = next((CHECK_RE.match(lines[i].rstrip("\r\n")).group(1).strip()
                      for i in range(at + 1, end)
                      if i not in fenced and CHECK_RE.match(lines[i].rstrip("\r\n"))), None)
        if check is not None:
            kept.append((slug, (re.match(r"\w+", check) or [check or "empty"])[0]))
            continue
        todo.append(slug)
        inserts.append((after_last_bullet(lines, at + 1, end, fenced) or at + 1, CHECK_LINE))
    return inserts, {"trust": trust, "todo": todo, "kept": kept}


def mapping_notes(spec: Path, s: dict, todo: list[str], root_arg) -> list[str]:
    rows = section10_rows(s["lines"], s["heads"], s["fenced"])
    root = plant_root(spec, root_arg)
    layout = test_layout(root) if root else None
    hits = slug_hits(root, layout, todo) if layout else {}
    notes = []
    for slug in todo:
        r = rows.get(slug, [])
        row = (f"§10 row{'s' if len(r) > 1 else ''} ({'; '.join(r)})" if r else "no §10 row")
        if layout is None:
            where = root / "docs/graph/spec-lint.py" if root else "a plant root (pass --root)"
            test = f"slug in test not looked up (no TEST_GLOBS in {where})"
        elif hits.get(slug):
            more = len(hits[slug]) - 2
            test = f"slug in test ({', '.join(hits[slug][:2])}{f' +{more} more' if more > 0 else ''})"
        else:
            test = "slug in no test file the plant's TEST_GLOBS read"
        notes.append(f"    {slug}: {row}; {test}")
    return notes


def write(spec: Path, s: dict, inserts: list[tuple[int, str]]) -> str:
    lines = list(s["lines"])
    nl = "\r\n" if "\r\n" in s["text"] else "\n"
    if lines and not lines[-1].endswith(("\n", "\r")):
        lines[-1] += nl
    groups: dict[int, list[str]] = {}
    for at, new in inserts:               # lines at one index keep their order
        groups.setdefault(at, []).append(new)
    for at in sorted(groups, reverse=True):
        lines[at:at] = [l + nl for l in groups[at]]
    stamp = time.strftime("%Y%m%d-%H%M%S")
    bak = spec.with_name(f"{spec.name}.bak-{stamp}")
    shutil.copy2(spec, bak)
    tmp = spec.with_name(f".{spec.name}.spec-convert.tmp")
    tmp.write_text("".join(lines), encoding="utf-8", newline="")
    os.replace(tmp, spec)
    return bak.name


def main(argv: list[str]) -> int:
    try:
        opts = parse(argv)
        spec = Path(opts["paths"][0])
        if not spec.is_file():
            raise Usage(f"{spec}: no such file; nothing written")
        s = read_spec(spec)
    except Usage as e:
        print(f"spec-convert: {e}", file=sys.stderr)
        return 2
    if isinstance(s, list):
        print(f"spec-convert: {spec.name}: unrecognised spec shape: {'; '.join(s)}; nothing written")
        return 1
    if s["kinds"]:
        print(f"spec-convert: {spec.name}: already in the kinds form; nothing to convert")
        return 0
    inserts, said = plan(s)
    notes = mapping_notes(spec, s, said["todo"], opts["root"])
    if opts["write"]:
        bak = write(spec, s, inserts)
        head = f"spec-convert: {spec.name} (legacy form -> kinds form) — WRITTEN, backup {bak}"
    else:
        head = f"spec-convert: {spec.name} (legacy form -> kinds form) — DRY RUN, nothing written"
    print(head)
    if said["trust"] is None:
        print(f' §0: add "{FORM_LINE}" and "{TRUST_LINE}"   (set yes if a contract is security, '
              f'data-integrity or money)')
    else:
        print(f' §0: add "{FORM_LINE}"   ("- **Trust path:** {said["trust"]}" already present, kept)')
    print(f' §4: {len(said["todo"])} contracts -> "{CHECK_LINE}" each (present mapping kept as '
          f'evidence: §10 row / slug in test)')
    for n in notes:
        print(n)
    if said["kept"]:
        print(" §4: kept as written, already labelled: "
              + ", ".join(f"{slug} ({kind})" for slug, kind in said["kept"]))
    print(UNCHANGED)
    print(JUDGMENT)
    if opts["write"]:
        print(f"spec-convert: next, from the plant root: python3 docs/graph/spec-lint.py; "
              f"the spec as it was is {bak}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
