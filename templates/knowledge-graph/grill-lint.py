#!/usr/bin/env python3
"""grill-lint: mechanical proof that the plan-of-record is a plan (kernel §3.3).

The grill rule says docs/graph/plans/grill.md is the living plan-of-record
and the source the orchestrator sequences spawns from. Until now its shape
was aspiration enforced by prose — and the two sections that prose named
first as "never skip" (§1 discovery, §5 research) were the two nothing
gated. This makes the shape a gate:

  - every section §0–§15 is populated: content of its own, or an explicit
    `not applicable — <reason>`; a template label with nothing after it
    is neither (template lines are subtracted, so the form does not count
    as the plan);
  - every §1 line cites what was read, or reads `none — <reason>`;
  - every §9 increment names spec contracts, RED tests, a rollback and its
    dependencies, and the rows are in DEPENDENCY ORDER: a row that depends
    on a later row (or a row that does not exist) is what an orchestrator
    misreads as independent and spawns in parallel;
  - §5 covers every docs/graph/libraries/ page a §9 row depends on — the
    research set is derived from the plan, not judged — and every library
    page the plan names exists;
  - the plan↔spec alignment check, mechanically: every contract a §9 row
    names is declared in a live spec, and every contract of those specs
    appears in some increment;
  - no `[verify]` survives in §9 or §13 (an assumption with no home);
  - §14 is one action.

Installed at docs/graph/grill-lint.py by install.sh (like spec-lint.py).
Dependency-free. No project config: the plan's path and the spec heading
form are the seed's own contract.

Usage:
  python3 docs/graph/grill-lint.py             # gate: exit 1 on a defect
  python3 docs/graph/grill-lint.py --list      # print the §9 increment graph
  python3 docs/graph/grill-lint.py --warn      # report but always exit 0
  python3 docs/graph/grill-lint.py --plan P    # lint another plan file
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # docs/graph/
PLAN = HERE / "plans" / "grill.md"
TEMPLATE = HERE / "templates" / "grill.template.md"
SPECS = HERE / "specs"
LIBRARIES = HERE / "libraries"
REQUIRED_SECTIONS = range(0, 16)
RETIRED_STATUSES = {"superseded", "retired", "deprecated", "withdrawn"}

SECTION_RE = re.compile(r"^##\s+(\d+)\.\s*(.*)$", re.M)
INCREMENT_RE = re.compile(r"^###\s+Increment\s+(\d+)\b(.*)$", re.M)
FIELD_RE = re.compile(r"^\s*-\s*([A-Za-z][^:]{0,40}):(.*)$")
LABEL_ONLY_RE = re.compile(r"^\s*-\s*[^:]+:\s*$")
TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
LIB_REF_RE = re.compile(r"docs/graph/libraries/([\w.\-]+)\.md")
INC_REF_RE = re.compile(r"\bincrement\s+(\d+)", re.I)
CONTRACT_REF_RE = re.compile(r"(SPEC-\d{4})[\w\-]*/([A-Z][A-Z0-9_]{2,})")
CONTRACT_DECL_RE = re.compile(r"^###\s+Contract:\s*([A-Z][A-Z0-9_]{2,})\s*$", re.M)
STATUS_RE = re.compile(r"\*\*Status:\*\*\s*([\w-]+)")
NA_RE = re.compile(r"^\s*(not applicable|n/?a|none)\b", re.I)
REQUIRED_FIELDS = ("Spec contracts", "Tests to write (RED)", "Rollback path", "Depends on")


def strip_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def sections(text: str) -> dict[int, str]:
    """Section number -> body text (header excluded), for `## N. Title` headers."""
    out: dict[int, str] = {}
    matches = list(SECTION_RE.finditer(text))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out[int(m.group(1))] = text[m.end():end]
    return out


def content_lines(body: str, template_lines: set[str]) -> list[str]:
    """Lines that are the plan's own: not blank, not the form's own prose,
    not an unfilled label, not a table header/separator."""
    raw = [ln.rstrip() for ln in body.splitlines()]
    out: list[str] = []
    for i, ln in enumerate(raw):
        s = ln.strip()
        if not s or s in template_lines or LABEL_ONLY_RE.match(s) or TABLE_SEP_RE.match(s):
            continue
        if i + 1 < len(raw) and TABLE_SEP_RE.match(raw[i + 1].strip()):
            continue                                # a table header row
        out.append(s)
    return out


def fields(block: str) -> dict[str, str]:
    """`- Label: value` fields of an increment block; a value continues on
    indented lines until the next label."""
    out: dict[str, str] = {}
    current = None
    for ln in block.splitlines():
        m = FIELD_RE.match(ln)
        if m:
            current = m.group(1).strip()
            out[current] = m.group(2).strip()
        elif current and ln.startswith((" ", "\t")) and ln.strip():
            out[current] = (out[current] + " " + ln.strip()).strip()
    return out


def increments(body: str) -> list[tuple[int, str, str]]:
    """(number, title, block) per `### Increment N — title` in §9."""
    out = []
    matches = list(INCREMENT_RE.finditer(body))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        title = m.group(2).strip(" —-–:").strip()
        out.append((int(m.group(1)), title, body[m.end():end]))
    return out


def spec_files() -> dict[str, tuple[Path, str]]:
    """SPEC-NNNN -> (path, status) for every spec on disk."""
    out: dict[str, tuple[Path, str]] = {}
    if SPECS.is_dir():
        for p in sorted(SPECS.glob("SPEC-*.md")):
            key = p.name[:9]
            text = p.read_text(encoding="utf-8", errors="replace")
            m = STATUS_RE.search(text)
            out[key] = (p, (m.group(1).lower() if m else "unknown"))
    return out


def main() -> int:
    argv = sys.argv[1:]
    list_mode = "--list" in argv
    warn_mode = "--warn" in argv
    plan = PLAN
    if "--plan" in argv:
        plan = Path(argv[argv.index("--plan") + 1]).resolve()

    if not plan.is_file():
        print(f"grill lint: SKIP — no plan at {plan}")
        return 0

    text = strip_comments(plan.read_text(encoding="utf-8", errors="replace"))
    template_lines: set[str] = set()
    if TEMPLATE.is_file():
        template_lines = {ln.strip() for ln in
                          strip_comments(TEMPLATE.read_text(encoding="utf-8", errors="replace")).splitlines()
                          if ln.strip()}

    fails: list[str] = []
    warns: list[str] = []
    secs = sections(text)

    # --- shape: every section present and populated -------------------------
    for n in REQUIRED_SECTIONS:
        if n not in secs:
            fails.append(f"§{n}: section missing (headers are `## {n}. Title`; numbers are stable)")
    populated = {n: content_lines(secs[n], template_lines) for n in secs}
    for n in REQUIRED_SECTIONS:
        if n in secs and not populated[n]:
            fails.append(f"§{n}: not populated — content, or one line `not applicable — <reason>`")

    # --- §1: every line cites, or says none — <reason> ------------------------
    if 1 in secs:
        for ln in secs[1].splitlines():
            if LABEL_ONLY_RE.match(ln.strip()):
                fails.append(f"§1: `{ln.strip()}` has no path and no `none — <reason>` (read it; do not guess)")

    # --- §9: increment shape and dependency order ---------------------------
    incs = increments(secs.get(9, ""))
    if 9 in secs and not incs and not any(NA_RE.match(ln) for ln in populated.get(9, [])):
        fails.append("§9: no `### Increment N — title` rows")
    numbers = [n for n, _, _ in incs]
    known = set(numbers)
    lib_needed: dict[str, list[int]] = {}
    contract_refs: dict[str, dict[str, list[int]]] = {}
    graph: list[tuple[int, str, list[int], list[str], list[str]]] = []
    for n, title, block in incs:
        f = fields(block.replace("~~", ""))
        for name in REQUIRED_FIELDS:
            if not f.get(name, "").strip():
                fails.append(f"§9 increment {n}: `{name}:` is blank (`none` is a value; blank is not)")
        dep = f.get("Depends on", "")
        inc_deps = [int(x) for x in INC_REF_RE.findall(dep)]
        for d in inc_deps:
            if d not in known:
                fails.append(f"§9 increment {n}: depends on increment {d}, which does not exist")
            elif d == n:
                fails.append(f"§9 increment {n}: depends on itself")
            elif numbers.index(d) > numbers.index(n):
                fails.append(f"§9 increment {n}: depends on increment {d}, listed after it — "
                             f"rows are in dependency order; an orchestrator reads a later row as independent")
        libs = LIB_REF_RE.findall(dep)
        for lib in libs:
            lib_needed.setdefault(lib, []).append(n)
        refs = CONTRACT_REF_RE.findall(f.get("Spec contracts", ""))
        for spec, slug in refs:
            contract_refs.setdefault(spec, {}).setdefault(slug, []).append(n)
        graph.append((n, title, inc_deps, libs, [f"{s}/{c}" for s, c in refs]))
        if "[verify]" in block:
            fails.append(f"§9 increment {n}: carries `[verify]` — an assumption with no home; resolve it or move it to §12")

    # --- §5 is derived from §9; every library page named exists -------------
    body5 = secs.get(5, "")
    for lib, rows in sorted(lib_needed.items()):
        if f"docs/graph/libraries/{lib}.md" not in body5:
            fails.append(f"§5: silent about docs/graph/libraries/{lib}.md, which increment "
                         f"{', '.join(map(str, rows))} depends on — research it or say why not")
    for lib in sorted(set(LIB_REF_RE.findall(text))):
        if LIBRARIES.is_dir() and not (LIBRARIES / f"{lib}.md").is_file():
            fails.append(f"docs/graph/libraries/{lib}.md is named by the plan but does not exist (ingest-library)")

    # --- plan <-> spec alignment ---------------------------------------------
    specs = spec_files()
    for spec, slugs in sorted(contract_refs.items()):
        if spec not in specs:
            fails.append(f"§9 names {spec}, which is not in docs/graph/specs/")
            continue
        path, status = specs[spec]
        declared = set(CONTRACT_DECL_RE.findall(path.read_text(encoding="utf-8", errors="replace")))
        for slug, rows in sorted(slugs.items()):
            if slug not in declared:
                fails.append(f"§9 increment {', '.join(map(str, rows))}: {spec}/{slug} is not a "
                             f"`### Contract:` of {path.name} — the plan invents a contract; go back to specify")
        if status in RETIRED_STATUSES:
            warns.append(f"§9 implements {spec} whose status is {status}")
            continue
        for slug in sorted(declared - set(slugs)):
            fails.append(f"{path.name}: contract {slug} appears in no §9 increment — the plan does not implement the spec")

    # --- §13 carries no unverified claim; §14 is one action -----------------
    if 13 in secs and "[verify]" in secs[13]:
        fails.append("§13: carries `[verify]` — a done criterion cannot be an unverified claim")
    if 14 in secs:
        bullets = [ln for ln in populated[14] if ln.startswith(("-", "*", "1.", "2."))]
        if len(bullets) > 1 or len(populated[14]) > 3:
            fails.append(f"§14: {max(len(bullets), len(populated[14]))} lines — one action, not a list")
    for n in (6, 8, 11):
        if n in secs and "[verify]" in secs[n]:
            warns.append(f"§{n}: carries `[verify]` — fine while the pass is open; the press resolves it")

    if list_mode:
        for n, title, deps, libs, refs in graph:
            arrows = ", ".join(f"<- {d}" for d in deps) or "<- (root)"
            print(f"  {n:>2} {title or '(untitled)'}  {arrows}"
                  f"{'  libs: ' + ', '.join(libs) if libs else ''}"
                  f"{'  contracts: ' + ', '.join(refs) if refs else ''}")

    for w in warns:
        print(f"  WARN {w}")
    if fails:
        print(f"grill lint: {'WARN' if warn_mode else 'FAIL'} — {len(fails)} defect(s) in {plan.name}:")
        for f in fails:
            print(f"  - {f}")
        return 0 if warn_mode else 1
    print(f"grill lint: PASS — {plan.name}: {len(incs)} increment(s), "
          f"{sum(len(v) for v in contract_refs.values())} contract ref(s), {len(lib_needed)} library dep(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
