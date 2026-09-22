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
  - every decision the plan cites by identifier is filed under
    docs/graph/decisions/ — a number that reaches no record authorizes
    work by a citation nobody can read;
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
DECISIONS = HERE / "decisions"
REQUIRED_SECTIONS = range(0, 16)
RETIRED_STATUSES = {"superseded", "retired", "deprecated", "withdrawn"}

SECTION_RE = re.compile(r"^##\s+(\d+)\.\s*(.*)$", re.M)
INCREMENT_RE = re.compile(r"^###\s+Increment\s+(\d+)\b(.*)$", re.M)
# An index row: a table row whose first cell is the increment number and whose
# last cell names the file holding it. `| 3 | Persist | planned | `plans/grill/
# increment-03-persist.md` |`
# The path may sit in ANY cell, in backticks, bare, or as a markdown link, and
# the row may have any number of columns. The first version demanded exactly
# four columns with the path alone in the fourth, so an added Owner column, a
# `[detail](path)` link — the idiomatic way to point at a file — or a three
# column table all went UNSEEN. An index row nobody parses is an increment that
# is never validated, which is the orphan failure arriving through the parser.
INDEX_ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|(.*)\|\s*$", re.M)
INDEX_PATH_RE = re.compile(r"([\w./-]*plans/grill/[\w.-]+\.md)")
FIELD_RE = re.compile(r"^\s*-\s*([A-Za-z][^:]{0,40}):(.*)$")
LABEL_ONLY_RE = re.compile(r"^\s*-\s*[^:]+:\s*$")
TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
LIB_REF_RE = re.compile(r"docs/graph/libraries/([\w.\-]+)\.md")
ADR_REF_RE = re.compile(r"\bADR-(\d{4})\b")
ADR_FILE_RE = re.compile(r"^(?:adr-)?(\d{4})\b")
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


def increments(body: str, errs: list | None = None) -> list[tuple[int, str, str]]:
    """(number, title, block) per increment in §9, in either form.

    INLINE — `### Increment N — title` written straight into §9. Every plant
    already has this, so it keeps working unchanged.

    LEDGER — §9 is an index, one row per increment, each pointing at a file
    under `plans/grill/` that holds it. A plan-of-record grows for as long as
    the project does and §9 grows fastest: contracts, RED tests, rollback paths
    and dependencies for every increment ever planned. Held in one file that is
    read whole, a mature plan becomes the largest single thing a session loads,
    and the progressive discovery the whole method rests on is defeated by the
    document describing the work. The plan stays the ledger; the increments
    become files under it, and a session reads the index plus the one increment
    it is working on.

    Both forms may appear together — that is how a plan migrates, one increment
    at a time, without a flag day.
    """
    out = []
    matches = list(INCREMENT_RE.finditer(body))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        title = m.group(2).strip(" —-–:").strip()
        out.append((int(m.group(1)), title, body[m.end():end]))

    inline_nums = {n for n, _t, _b in out}
    seen = set(inline_nums)
    referenced: set[str] = set()
    for row in INDEX_ROW_RE.finditer(body):
        path_m = INDEX_PATH_RE.search(row.group(2))
        if not path_m:
            continue
        num, rel = int(row.group(1)), path_m.group(1).strip()
        referenced.add(Path(rel).name)
        # Containment. `Path.__truediv__` DISCARDS the left side when the right
        # is absolute, and `..` walks out, so an index row reading
        # `/anywhere/plans/grill/x.md` or `../../../plans/grill/x.md` made the
        # lint read and bless a file nowhere near the plan — a plan could claim
        # contract coverage from a file no reviewer would think to open. The
        # increments of a plan live under that plan.
        grill_home = (HERE / "plans" / "grill").resolve()
        stripped = rel[len("docs/graph/"):] if rel.startswith("docs/graph/") else rel
        target = (HERE / stripped)
        try:
            inside = target.resolve().is_relative_to(grill_home)
        except (OSError, ValueError):
            inside = False
        if not inside:
            if errs is not None:
                errs.append(f"§9: increment {num} points outside plans/grill/ "
                            f"({rel}) — an increment of this plan must live "
                            f"under it")
            continue
        if not target.is_file():
            if errs is not None:
                errs.append(f"§9: increment {num} points at {rel}, which does "
                            f"not exist — an index row is a promise that the "
                            f"work is written down somewhere")
            continue
        child = strip_comments(target.read_text(encoding="utf-8"))
        cm = list(INCREMENT_RE.finditer(child))
        if not cm:
            if errs is not None:
                errs.append(f"§9: {rel} carries no `### Increment {num} — title` "
                            f"heading, so the file the index points at does not "
                            f"say which increment it is")
            continue
        for j, m in enumerate(cm):
            end = cm[j + 1].start() if j + 1 < len(cm) else len(child)
            n = int(m.group(1))
            if j == 0 and n != num and errs is not None:
                errs.append(f"§9: the index says increment {num} but {rel} is "
                            f"headed `Increment {n}` — renumbering one and not "
                            f"the other is exactly the drift an index is "
                            f"supposed to make checkable")
            if n in seen and errs is not None:
                where = "inline" if n in inline_nums else "another index row"
                errs.append(f"§9: increment {n} is defined twice — once "
                            f"{where} and once in {rel}")
            seen.add(n)
            out.append((n, m.group(2).strip(" —-–:").strip(), child[m.end():end]))

    # An increment file nobody indexes is work that exists and is unreachable:
    # it will not be read, reviewed, or counted, and it looks like progress.
    grill_dir = HERE / "plans" / "grill"
    if errs is not None and grill_dir.is_dir():
        # Every .md under plans/grill/, at any depth and under any name. The
        # glob was `increment-*.md` and non-recursive, so a child called
        # `inc-03.md`, `increment_03.md`, or filed in a subdirectory was
        # unreachable work the orphan check could not see.
        for f in sorted(grill_dir.rglob("*.md")):
            if f.name not in referenced:
                errs.append(f"plans/grill/{f.name} is not indexed by §9 — an "
                            f"increment nobody points at is unreachable work")

    # NOT sorted by number. The forward-dependency check reads position in this
    # list as DOCUMENT order — "is the dependency written before the thing that
    # needs it" — and §9 is the top-to-bottom order an orchestrator spawns in.
    # Sorting numerically silently redefined that: a plan that appends increment
    # 3 after 1 and 2 (the append-don't-renumber convention this seed itself
    # prescribes) would start failing on a forward dependency it does not have,
    # with no change to the plan file — a break delivered by upgrading the tool.
    # Index rows are appended in the order §9 lists them, which is the same
    # document order, so both forms agree.
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


def decision_files() -> dict[str, Path]:
    """ADR-NNNN -> path for every decision filed on disk.

    Both filename forms this seed has shipped resolve: `adr-NNNN-<slug>.md`,
    which the ADR template prescribes, and a bare `NNNN-<slug>.md`.
    """
    out: dict[str, Path] = {}
    if DECISIONS.is_dir():
        for p in sorted(DECISIONS.glob("*.md")):
            m = ADR_FILE_RE.match(p.name)
            if m:
                out[f"ADR-{m.group(1)}"] = p
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
    incs = increments(secs.get(9, ""), fails)
    if 9 in secs and not incs and not any(NA_RE.match(ln) for ln in populated.get(9, [])):
        fails.append("§9: no `### Increment N — title` rows, and no index rows "
                     "pointing at files under plans/grill/")
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

    # --- every decision the plan cites resolves to a filed decision ---------
    decisions = decision_files()
    for num in sorted(set(ADR_REF_RE.findall(text))):
        if f"ADR-{num}" not in decisions:
            fails.append(f"ADR-{num} is named by the plan but is not filed in "
                         f"docs/graph/decisions/ — a decision that is not yet "
                         f"accepted is filed with the status that says so "
                         f"(`status: proposed`), not left as a number in a table")

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
