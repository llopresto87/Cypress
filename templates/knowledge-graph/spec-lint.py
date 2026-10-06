#!/usr/bin/env python3
"""spec-lint: mechanical proof that "specs are executable" (kernel §3.1).

The spec rule says every functional contract maps to at least one test,
and tests reuse the contract's stable UPPER_SNAKE_SLUG. Two passes make
that a gate instead of an aspiration:

  SHAPE — every spec on disk, whatever its status:
  - contract slugs are unique within the spec;
  - a §9 acceptance criterion that "maps to" a slug maps to a declared one;
  - a SIGNED spec (product, architect, tester ticked in §0) or a LIVE one
    has a §10 test-mapping row per contract — the specify exit condition,
    checked rather than promised;
  - a live spec carries its sign-offs, EXCEPT a back-written one, which had no promotion to sign and is refused if it carries them (a promotion nobody signed);
  - an `implemented` spec has no §10 row still `red` or `pending`.

  COVERAGE — live specs only (status active / implemented / back-written):
  - every contract must appear in >=1 test file;
  - a slug appearing in tests but in no live spec is drift (renamed or
    retired contract still asserted somewhere) -> WARN;
  - live contracts + ZERO matching test files is a green lie
    (kernel §3.5) -> FAIL loudly, never a vacuous pass.

A draft is shape-checked and not counted for coverage: it turns active in
the change that lands its RED tests (test-first COMMIT), so a spec in
authoring never reports uncovered. Leaving it out is said out loud: the
headline names every draft it did not coverage-check, and a draft whose
slugs the tests already carry, and no live spec declares, is a WARN, because
its RED landed and the promotion did not. Status is read from frontmatter first —
the schema's single home — and from a body `**Status:**` only when the
frontmatter has none (the template's body line says "see frontmatter").

SLICE — `--slice SLUG...` is a reader, not a check. It prints only what one
contract needs, so a worker briefed on a slug loads that and not the whole
spec: the `### Contract:` or `### Failure:` block up to the next heading of
the same or a higher level, the slug's §10 row(s) each under its table
header, and with --refs `file:line` pointers to the §6/§7 headings the block
cites (pointers, never their text). --lines prints `file:start-end` ranges
instead of text. Headings inside ``` or ~~~ fences are text (the CommonMark
fence rule grill-lint uses). A slug declared in several specs is sliced from
each, with a stderr note naming every file. Exit 0 every slug found; 1 a slug
is missing (the found ones still print) or a spec is misnamed; 2 usage error.

DISCOVERY — a spec is `specs/SPEC-*.md`. Every other Markdown file in the
specs directory, apart from its index and readme, is a misnamed spec: a FAIL
naming the file, because the pattern alone skipped it and reported a pass over
an empty set.

Installed at docs/graph/spec-lint.py by install.sh (like graph-lint.py).
Dependency-free. Set TEST_GLOBS for the project's layout.

Usage:
  python3 docs/graph/spec-lint.py           # gate: exit 1 on a defect
  python3 docs/graph/spec-lint.py --list    # dump contract -> tests map
  python3 docs/graph/spec-lint.py --warn    # report but always exit 0
  python3 docs/graph/spec-lint.py --slice [--refs] [--lines] SLUG...
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# ---- project configuration (edit these when installing) -------------------
# TEST_GLOBS is an owner fact, not a guess: the plant's owner confirms which
# directories hold its tests (grow asks it with the plant facts, under
# grow.plant-facts; graft puts it to the steward when the kept globs are still
# this default or miss a test directory). The default below reads only the
# conventional unit layouts and is deliberately narrow; a black-box directory
# of another name (end-to-end suites, shell checks) is added here per plant on
# the owner's word, never by widening this default for every plant.
TEST_GLOBS = [
    "tests/**/*.*", "test/**/*.*", "spec/**/*.*",
    "**/*_test.*", "**/*.test.*", "**/test_*.*",
]
# `back-written` is LIVE. It was added to this set after a review found that
# moving two specs to `back-written` silenced every check on them: the
# coverage pass skipped them ("0 live specs") and the SHAPE pass, gated on
# `is_signed or live`, skipped them too because a back-written spec is also
# unsigned. A status that means "written after the fact" must not also mean
# "exempt from its own contracts".
LIVE_STATUSES = {"active", "implemented", "back-written"}
# The full vocabulary. `LIVE_STATUSES` alone was an allow-list: any word outside
# it — `stable`, `retrofitted`, or `back_written`, a typo of the value the
# previous fix added — silenced every check on the spec and printed
# "0 live spec(s)". An unknown status is now a defect, not an exemption.
KNOWN_STATUSES = LIVE_STATUSES | {"draft", "superseded"}
# ----------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent          # docs/graph/
ROOT = HERE.parent.parent                       # repo root
SPECS = HERE / "specs"
# The specs directory's own pages: not specs, and never misnamed ones.
SPEC_DIR_EXEMPT = {"index.md", "readme.md"}
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__",
             "dist", "build", "target", ".next"}
CONTRACT_RE = re.compile(r"^###\s+Contract:\s*([A-Z][A-Z0-9_]{2,})\s*$", re.M)
FAILURE_RE = re.compile(r"^###\s+Failure:\s*([A-Z][A-Z0-9_]{2,})\s*$", re.M)
FRONT_STATUS_RE = re.compile(r"^status:\s*([\w-]+)", re.M)
BODY_STATUS_RE = re.compile(r"\*\*Status:\*\*\s*([\w-]+)")
SECTION_RE = re.compile(r"^##\s+(\d+)\.\s*(.*)$", re.M)
SIGNOFF_RE = re.compile(r"\*\*Sign-offs:\*\*(.*)")
SLUG_RE = re.compile(r"(?<![A-Z0-9_])[A-Z][A-Z0-9_]{2,}(?![A-Z0-9_])")
SIGNERS = ("product", "architect", "tester")
STILL_OPEN = {"red", "pending"}
# A table's cell boundary: a pipe not escaped as `\|` (GFM). The delimiter
# row under a header is dashes with optional colons, one run per column.
PIPE_RE = re.compile(r"(?<!\\)\|")
DELIM_ROW_RE = re.compile(r"^\s*\|?\s*:?-+:?\s*(?:\|\s*:?-+:?\s*)*\|?\s*$")
# --slice reads the spec as headings rather than as text, because a block's
# end is the next heading of its level and a heading inside a fence is not one.
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
# The CommonMark fence opener, identical to grill-lint.py's FENCE_RE: at most
# three spaces of indent, then a run of three or more backticks or tildes.
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
NUMBER_RE = re.compile(r"^§?(\d+(?:\.\d+)*)\.?(?:\s|$)")
CITE_RE = re.compile(r"§\s?(\d+(?:\.\d+)*)")
REF_TOPS = ("6", "7")          # the template's data-shape and failure-mode sections
Head = tuple[int, int, str]    # (1-based line, level, text)


def test_files() -> list[Path]:
    seen: set[Path] = set()
    for pattern in TEST_GLOBS:
        for p in ROOT.glob(pattern):
            if p.is_file() and not (set(p.parts) & SKIP_DIRS) and SPECS not in p.parents:
                seen.add(p)
    return sorted(seen)


def spec_paths() -> tuple[list[Path], list[Path]]:
    """(specs, misnamed): the `SPEC-*.md` files, and every other Markdown
    file in the specs directory apart from its index and readme. Discovery by
    the pattern alone skipped a misnamed spec and printed "PASS, 0 live
    spec(s)" over a directory of specs, a green over an empty set. A misnamed
    spec is now a defect named by file, never a silent skip."""
    if not SPECS.is_dir():
        return [], []
    specs = sorted(SPECS.glob("SPEC-*.md"))
    misnamed = sorted(p for p in SPECS.glob("*.md")
                      if p not in specs and p.name.lower() not in SPEC_DIR_EXEMPT)
    return specs, misnamed


def misnamed_message(p: Path) -> str:
    return (f"misnamed spec, not checked: {p.name} — a spec file is "
            f"SPEC-NNNN-<surface>.md; rename it, or it is never linted")


def status_of(text: str) -> str:
    """Frontmatter first (the single home); the body line only when the
    frontmatter has none, and never the template's "see frontmatter"."""
    if text.startswith("---"):
        head = text.split("\n---", 1)[0]
        m = FRONT_STATUS_RE.search(head)
        if m:
            return m.group(1).lower()
    m = BODY_STATUS_RE.search(text)
    return m.group(1).lower() if m and m.group(1).lower() != "see" else "unknown"


def sections(text: str) -> dict[int, str]:
    out: dict[int, str] = {}
    matches = list(SECTION_RE.finditer(text))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out[int(m.group(1))] = text[m.end():end]
    return out


def signed(text: str) -> tuple[bool, list[str]]:
    """(all three signers ticked, the ones that are not)."""
    m = SIGNOFF_RE.search(text)
    line = m.group(1).lower() if m else ""
    missing = [s for s in SIGNERS if not re.search(rf"{s}\s*\[\s*x\s*\]", line)]
    return (not missing, missing)


def section_lines(text: str, num: int) -> list[tuple[int, str]]:
    """[(1-based line, text)] of section `num`'s body, the heading excluded,
    so a finding in it can name the line of the file."""
    matches = list(SECTION_RE.finditer(text))
    for i, m in reversed(list(enumerate(matches))):   # the last wins, as in sections()
        if int(m.group(1)) != num:
            continue
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        first = text.count("\n", 0, m.start()) + 1
        body = text[m.end():end].split("\n")[1:]      # [0] is the heading's own rest
        return [(first + k, ln) for k, ln in enumerate(body, 1)]
    return []


def row_cells(line: str) -> list[str]:
    """A table line's cells, read as GFM reads them: the outer pipes are
    optional, and an escaped pipe `\\|` is text inside its cell, not a
    cell boundary."""
    ln = line.strip()
    if ln.startswith("|"):
        ln = ln[1:]
    if ln.endswith("|") and not ln.endswith("\\|"):
        ln = ln[:-1]
    return [c.strip() for c in PIPE_RE.split(ln)]


def table_rows(lines: list[tuple[int, str]]) -> list[tuple[int, list[str], int]]:
    """[(line, cells, header cell count)] for each table line in `lines`.
    A table is a line holding a pipe with a delimiter row under it; its body
    runs to the first line without an unescaped pipe, and every body row is
    read against the header's count. A pipe-led line with no delimiter row
    under it is read as before 7.32.0: a row on its own, its own header."""
    out: list[tuple[int, list[str], int]] = []
    i = 0
    while i < len(lines):
        n, ln = lines[i]
        nxt = lines[i + 1][1] if i + 1 < len(lines) else ""
        if PIPE_RE.search(ln) and "|" in nxt and DELIM_ROW_RE.match(nxt):
            width = len(row_cells(ln))
            out.append((n, row_cells(ln), width))
            i += 2                                  # the delimiter row is no row
            while i < len(lines) and PIPE_RE.search(lines[i][1]):
                out.append((lines[i][0], row_cells(lines[i][1]), width))
                i += 1
            continue
        if ln.strip().startswith("|"):
            cells = row_cells(ln)
            out.append((n, cells, len(cells)))
        i += 1
    return out


def mapping_rows(lines10: list[tuple[int, str]]) -> dict[str, str]:
    """§10 table: first cell -> status cell (last non-empty cell)."""
    rows: dict[str, str] = {}
    for _, cells, _ in table_rows(lines10):
        if len(cells) < 2 or set(cells[0]) <= set("-: "):
            continue
        rows[cells[0]] = cells[-1].lower()
    return rows


def shape(spec: Path, text: str, status: str, fails: list[str], warns: list[str]) -> None:
    secs = sections(text)
    slugs = CONTRACT_RE.findall(text)
    for dup in sorted({s for s in slugs if slugs.count(s) > 1}):
        fails.append(f"{spec.name}: contract {dup} is declared twice")
    declared = set(slugs)
    for ln in secs.get(9, "").splitlines():
        if "maps to" not in ln:
            continue
        for slug in SLUG_RE.findall(ln.split("maps to", 1)[1]):
            if slug.startswith("AC_"):
                continue
            if slug not in declared:
                fails.append(f"{spec.name}: §9 maps to {slug}, which is not a `### Contract:` of this spec")
    is_signed, missing = signed(text)
    if status not in KNOWN_STATUSES:
        fails.append(f"{spec.name}: unknown status {status!r} — a status outside "
                     f"{sorted(KNOWN_STATUSES)} exempts the spec from every check "
                     f"below, so it is refused rather than honoured")
    live = status in LIVE_STATUSES
    # `back-written` means the spec was written AFTER the behaviour, so there
    # was no promotion for anyone to sign. Demanding signatures there is what
    # produced a fabricated sign-off line in this repository once already —
    # someone wrote "signed when its RED landed" to clear this check, and no
    # RED had landed. The status carries the disclosure; the contracts below
    # are still held. Every OTHER live status must be signed.
    if live and missing and status != "back-written":
        fails.append(f"{spec.name}: status {status} but unsigned by {', '.join(missing)} — a promotion nobody signed")
    if status == "back-written" and is_signed:
        fails.append(f"{spec.name}: status back-written but carries sign-offs — "
                     f"a back-written spec had no promotion to sign, so a "
                     f"signature on one is a record of something that did not happen")
    if live and not declared:
        fails.append(f"{spec.name}: live spec with no `### Contract:` at all — "
                     f"a spec that contracts nothing passes every coverage check "
                     f"vacuously, which is the shape of a false green")
    # A §10 row whose cell count differs from its table's header reads its
    # status from the wrong column, and nothing downstream can tell.
    lines10 = section_lines(text, 10)
    for n, cells, width in table_rows(lines10):
        if len(cells) != width:
            fails.append(f"{spec.name}:{n}: §10 row has {len(cells)} cells and its "
                         f"header has {width}; its status is read from the wrong column")
    if (is_signed or live) and declared:
        rows = mapping_rows(lines10)
        for slug in sorted(declared - set(rows)):
            fails.append(f"{spec.name}: contract {slug} has no §10 test-mapping row"
                         f" ({'signed' if is_signed else status} — the mapping is owed, status `pending` is a value)")
        if status == "implemented":
            for slug, st in sorted(rows.items()):
                if st in STILL_OPEN and slug in declared:
                    fails.append(f"{spec.name}: implemented, but §10 row {slug} is `{st}`")
        if not FAILURE_RE.search(text):
            warns.append(f"{spec.name}: no `### Failure:` mode — a happy-path-only spec is half a spec")


def headings(lines: list[str]) -> list[Head]:
    """Every heading outside a fence. The fence rule is grill-lint.py's
    mask_fences, ported rather than imported because the two linters install
    as separate files; keep them identical. A fence closes only on a run of
    its own character at least as long as the opener with nothing after it,
    and an unclosed fence runs to the end, as CommonMark reads it. A toggle on
    any fence line once let a `~~~` inside a ``` block close it, which sliced
    the fenced example and made the real heading after it unsliceable."""
    out: list[Head] = []
    fence = ""                                  # the opening run, while inside
    for n, ln in enumerate(lines, 1):
        m = FENCE_RE.match(ln)
        if not fence and m:
            fence = m.group(1)
        elif fence and m and m.group(1).startswith(fence) and not ln[m.end():].strip():
            fence = ""
        elif not fence and (h := HEADING_RE.match(ln)):
            out.append((n, len(h.group(1)), h.group(2)))
    return out


def section_end(heads: list[Head], head: Head, nlines: int) -> int:
    """Last line of head's section: before the next heading of its level or higher."""
    return next((n - 1 for n, level, _ in heads if n > head[0] and level <= head[1]), nlines)


def numbered(heads: list[Head]) -> dict[str, Head]:
    """Section number -> its heading ("6.2 The record" -> "6.2")."""
    out: dict[str, Head] = {}
    for h in heads:
        if m := NUMBER_RE.match(h[2]):
            out.setdefault(m.group(1), h)
    return out


def slice_rows(lines: list[str], sec10: Head | None,
               heads: list[Head], slug: str) -> list[tuple[int, list[int]]]:
    """[(table header line, [row lines])] for the slug's rows inside §10.
    §10 alone: the same slug in an open-questions table is not a mapping."""
    if sec10 is None:
        return []
    groups: list[tuple[int, list[int]]] = []
    header = None
    for n in range(sec10[0] + 1, section_end(heads, sec10, len(lines)) + 1):
        ln = lines[n - 1].strip()
        if not ln.startswith("|"):
            header = None
            continue
        if header is None:
            header = n                  # a table's first line is its header
            continue
        cells = [c.strip().strip("`").strip() for c in ln.strip("|").split("|")]
        if cells[0] != slug:
            continue
        if groups and groups[-1][0] == header:
            groups[-1][1].append(n)
        else:
            groups.append((header, [n]))
    return groups


def cited_refs(block: str, nums: dict[str, Head]) -> list[Head]:
    """Headings of the §6/§7 sections a block cites. §6.3.1 with no heading of
    its own falls back to §6.3, then §6."""
    refs: list[Head] = []
    for m in CITE_RE.finditer(block):
        parts = m.group(1).split(".")
        if parts[0] not in REF_TOPS:
            continue
        while parts and ".".join(parts) not in nums:
            parts.pop()
        if parts and nums[".".join(parts)] not in refs:
            refs.append(nums[".".join(parts)])
    return sorted(refs)


def slice_specs(slugs: list[str], refs: bool, as_lines: bool) -> int:
    """--slice: print each slug's block, §10 rows and, with refs, pointers.
    A heading is matched by the same CONTRACT_RE / FAILURE_RE the gate uses,
    but the two do not read the same text: the reader skips headings inside
    fences, and the coverage gate matches over the whole file, fences
    included. A contract heading shown only inside a fenced example is
    counted by the gate and is unsliceable here.
    A slug declared in more than one spec is sliced from each, and stderr
    names the slug and every file, so no one block is taken for the only one."""
    out: list[str] = []
    missing = set(slugs)
    found_in: dict[str, list[str]] = {slug: [] for slug in slugs}
    specs, misnamed = spec_paths()
    for p in misnamed:
        print(f"spec lint: {misnamed_message(p)}", file=sys.stderr)
    for spec in specs:
        lines = spec.read_text(encoding="utf-8", errors="replace").splitlines()
        heads = headings(lines)
        nums = numbered(heads)
        name = spec.relative_to(ROOT) if ROOT in spec.parents else spec
        declared: dict[str, tuple[str, Head]] = {}
        for h in heads:
            head_line = lines[h[0] - 1]
            for kind, rx in (("contract", CONTRACT_RE), ("failure", FAILURE_RE)):
                if m := rx.match(head_line):
                    declared.setdefault(m.group(1), (kind, h))
        for slug in slugs:
            if slug not in declared:
                continue
            missing.discard(slug)
            found_in[slug].append(str(name))
            kind, h = declared[slug]
            end = section_end(heads, h, len(lines))
            while end > h[0] and not lines[end - 1].strip():
                end -= 1                # trailing blank lines are not the block
            rows = slice_rows(lines, nums.get("10"), heads, slug)
            if as_lines:
                out.append(f"{name}:{h[0]}-{end}\t{slug} {kind} block")
                for header, ns in rows:
                    out.append(f"{name}:{header}-{header + 1}\t{slug} §10 table header")
                    out += [f"{name}:{n}-{n}\t{slug} §10 row" for n in ns]
            else:
                if out:
                    out.append("")
                out.append(f"<!-- {name}:{h[0]}-{end} -->")
                out += lines[h[0] - 1:end]
                for header, ns in rows:
                    out += ["", f"<!-- §10 {name}:{header} -->", lines[header - 1], lines[header]]
                    out += [lines[n - 1] for n in ns]
            if not rows:
                out.append(f"# note: {slug} has no §10 test-mapping row in {name}")
            if refs:
                for n, level, text in cited_refs("\n".join(lines[h[0] - 1:end]), nums):
                    out.append(f"{name}:{n}\t{'#' * level} {text}")
    for slug in slugs:
        if slug in missing:
            print(f"spec lint: no `### Contract: {slug}` or `### Failure: {slug}` "
                  f"heading in {SPECS}", file=sys.stderr)
        elif len(found_in[slug]) > 1:
            print(f"spec lint: note — {slug} is declared in {len(found_in[slug])} "
                  f"specs, each sliced: {', '.join(found_in[slug])}",
                  file=sys.stderr)
    if out:
        print("\n".join(out))
    return 1 if missing or misnamed else 0


PLAN_FIELD_RE = re.compile(r"^- (Spec contracts|Tests to write \(RED\)):(.*)$", re.M)


def run_proved(slugs: set[str]) -> set[str]:
    """The live contracts the plan judged to need no test.

    grill.increment-shape asks of every increment whether it needs a test; a
    no reads `Tests to write (RED): none — <why>; proved by <run>`, and the
    contracts that increment names are covered by that run. `none —
    consolidation` covers nothing: its contracts keep their tests. Reads
    plans/grill.md and its ledger, plans/grill/**/*.md."""
    plans = SPECS.parent / "plans"
    proved: set[str] = set()
    for f in [plans / "grill.md", *sorted((plans / "grill").glob("**/*.md"))]:
        if not f.is_file():
            continue
        for block in re.split(r"^#+ Increment\b", f.read_text(encoding="utf-8", errors="replace"), flags=re.M):
            fields = dict(PLAN_FIELD_RE.findall(block))
            tests = fields.get("Tests to write (RED)", "").strip()
            if re.match(r"none\b", tests, re.I) and re.search(r"proved by\s+\S", tests, re.I):
                proved |= set(re.findall(r"[A-Z][A-Z0-9_]*", fields.get("Spec contracts", ""))) & slugs
    return proved

def main() -> int:
    list_mode = "--list" in sys.argv
    warn_mode = "--warn" in sys.argv

    # `--specs DIR` (and `--root DIR`) exist because this linter ships INTO a
    # plant at docs/graph/ and resolves its paths from its own location, which
    # means that in the SEED — where it lives at templates/knowledge-graph/ —
    # it looked for `templates/knowledge-graph/specs`, printed
    # "SKIP — no docs/graph/specs/ directory", and exited 0. The seed's own two
    # specs were therefore checked by nothing at all: the fabricated sign-off
    # line this remediation calls its worst product could be put straight back
    # with the whole gate green, and so could an invented `status:` value or a
    # spec with no contracts. The override is what lets the seed run its own
    # linter over its own specs.
    specs, root = SPECS, ROOT
    for flag, target in (("--specs", "specs"), ("--root", "root")):
        if flag in sys.argv:
            i = sys.argv.index(flag)
            if i + 1 >= len(sys.argv):
                print(f"spec lint: FAIL — {flag} needs a directory", file=sys.stderr)
                return 1
            chosen = Path(sys.argv[i + 1]).resolve()
            if target == "specs":
                specs = chosen
            else:
                root = chosen
    if specs is not SPECS and not specs.is_dir():
        # An override naming a directory that is not there must FAIL. Reusing
        # the SKIP below would turn a typo into a pass, which is the shape of
        # the defect this flag exists to close.
        print(f"spec lint: FAIL — --specs {specs} is not a directory", file=sys.stderr)
        return 1
    globals()["SPECS"], globals()["ROOT"] = specs, root

    if "--slice" in sys.argv:
        valued = {"--specs", "--root", "--uncovered-budget"}
        slugs = [a for i, a in enumerate(sys.argv[1:], 1)
                 if not a.startswith("--") and sys.argv[i - 1] not in valued]
        if not slugs:
            print("spec lint: usage — --slice [--refs] [--lines] SLUG...", file=sys.stderr)
            return 2
        return slice_specs(slugs, "--refs" in sys.argv, "--lines" in sys.argv)

    if not SPECS.is_dir():
        print("spec lint: SKIP — no docs/graph/specs/ directory")
        return 0

    fails: list[str] = []
    warns: list[str] = []
    contracts: dict[str, str] = {}          # slug -> spec file (live only)
    drafts: dict[str, list[str]] = {}       # draft spec file -> its slugs
    live_specs = 0
    spec_list, misnamed = spec_paths()
    fails.extend(misnamed_message(p) for p in misnamed)
    for spec in spec_list:
        text = spec.read_text(encoding="utf-8", errors="replace")
        status = status_of(text)
        shape(spec, text, status, fails, warns)
        if status == "draft":
            drafts[spec.name] = CONTRACT_RE.findall(text)
        if status not in LIVE_STATUSES:
            continue
        live_specs += 1
        for slug in CONTRACT_RE.findall(text):
            contracts[slug] = spec.name
    # A draft is left out of coverage, and a headline that says so only by
    # omission read "PASS — no live contracts to cover" over a spec already in
    # implementation, which a report then quoted as zero findings. Every
    # headline names what it did not check.
    unchecked = f"; not coverage-checked: {', '.join(drafts)} (draft)" if drafts else ""

    def finish(headline: str, rc: int) -> int:
        for w in warns:
            print(f"  WARN {w}")
        if fails:
            print(f"spec lint: {'WARN' if warn_mode else 'FAIL'} — {len(fails)} shape defect(s):")
            for f in fails:
                print(f"  - {f}")
            rc = 1
        else:
            print(headline)
        return 0 if warn_mode else rc

    draft_slugs = {slug for slugs in drafts.values() for slug in slugs}
    files = test_files() if contracts or draft_slugs else []
    if contracts and not files:
        print(f"spec lint: FAIL — {len(contracts)} live contract(s) but the "
              f"test globs matched ZERO files. A coverage check over an "
              f"empty set is a green lie; fix TEST_GLOBS or write the tests.")
        finish("", 0)
        return 0 if warn_mode else 1

    # Draft slugs are scanned too, never counted: a test already carrying one
    # means the RED landed and the promotion did not.
    hits: dict[str, list[str]] = {slug: [] for slug in draft_slugs | set(contracts)}
    # Boundary-guarded and longest-first: a bare substring scan let a
    # prefix slug steal the match from PARSE_JSON_STRICT and let an
    # UNREGISTERED extension (PARSE_JSON_V2 in a test) credit PARSE_JSON.
    slug_union = re.compile(
        "(?<![A-Z0-9_])(?:"
        + "|".join(re.escape(s) for s in sorted(hits, key=len, reverse=True))
        + ")(?![A-Z0-9_])")
    for f in files:
        try:
            body = f.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            # `errors="replace"` already tolerates bad encoding, so reaching
            # this except means the file could not even be opened
            # (permissions, or something removed it mid-scan). Skipping it
            # silently let a coverage run vouch for a slug it never actually
            # searched for; it is now a shape defect like any other, so it
            # fails the run through the same `fails` list, and the reason
            # goes to stderr, where a CI log gets read from.
            print(f"  !! {f}: unreadable ({e})", file=sys.stderr)
            fails.append(f"{f.relative_to(ROOT)}: unreadable test file ({e})"
                         f" — coverage cannot vouch for a file it never read")
            continue
        for m in slug_union.finditer(body):
            hits[m.group(0)].append(str(f.relative_to(ROOT)))
    # A draft slug a live spec also declares is skipped: the test carrying it
    # proves the live contract, and says nothing about the draft's promotion.
    for name, slugs in drafts.items():
        if tested := [s for s in slugs if hits[s] and s not in contracts]:
            warns.append(f"{name}: draft, but tests already carry {', '.join(tested)} — "
                         f"its RED landed and its promotion to active did not "
                         f"(test-first COMMIT), so its coverage is not checked")

    if not contracts:
        return finish(f"spec lint: PASS — no live contracts to cover "
                      f"({live_specs} live spec(s)){unchecked}", 0)

    proved = {s for s in run_proved(set(contracts)) if not hits[s]}
    uncovered = sorted(s for s in contracts if not hits[s] and s not in proved)

    if list_mode:
        for slug in sorted(contracts):
            where = (", ".join(sorted(set(hits[slug]))[:3])
                     or ("proved by a run (plan)" if slug in proved else "UNCOVERED"))
            print(f"  {slug}  ({contracts[slug]})  ->  {where}")

    if uncovered:
        # `--uncovered-budget N` separates the two things this linter checks.
        # SHAPE defects — a fabricated sign-off, an invented status, a live spec
        # with no contracts — are always fatal, because each asserts something
        # that did not happen. COVERAGE is enumerated debt: the seed's own two
        # specs are back-written over behaviour that already shipped, so most
        # contracts have no test carrying their slug, and that gap is real but
        # is not a lie. Ratcheting it is what makes it shrink: the budget lives
        # in tests/ratchets.json and may only fall, so a contract losing its
        # test fails the gate even while the honest backlog stands.
        budget = None
        if "--uncovered-budget" in sys.argv:
            i = sys.argv.index("--uncovered-budget")
            if i + 1 >= len(sys.argv):
                print("spec lint: FAIL — --uncovered-budget needs a number",
                      file=sys.stderr)
                return 1
            budget = int(sys.argv[i + 1])
        over = budget is None or len(uncovered) > budget
        label = "WARN" if (warn_mode or not over) else "FAIL"
        print(f"spec lint: {label} — "
              f"{len(uncovered)}/{len(contracts)} live contract(s) have no test"
              + (f" (recorded budget {budget})" if budget is not None else "")
              + unchecked + ":")
        for slug in uncovered:
            print(f"  - {slug}  ({contracts[slug]})")
        if budget is not None and len(uncovered) < budget:
            print(f"spec lint: FAIL — {len(uncovered)} uncovered against a "
                  f"recorded budget of {budget}. The debt SHRANK and the record "
                  f"did not: lower the budget in tests/ratchets.json, or the "
                  f"next contract to lose its test is absorbed silently.")
            finish("", 0)
            return 0 if warn_mode else 1
        finish("", 0)
        if not over:
            return 1 if fails else 0
        return 0 if warn_mode else 1

    by_run = f"; proved by a run per the plan: {', '.join(sorted(proved))}" if proved else ""
    return finish(f"spec lint: PASS — {len(contracts)} live contract(s) covered "
                  f"across {len(files)} test file(s){by_run}{unchecked}", 0)


if __name__ == "__main__":
    sys.exit(main())
