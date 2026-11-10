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
    work by a citation nobody can read. A bare `ADR-NNNN` names no
    repository, so it is always read as this plan's own: a number that
    collides with another repository's decision resolves here and passes.
    Cite another repository's decision as `<name>:ADR-NNNN` (`seed:ADR-0009`);
    it is reported once as external and not checked, never resolved against
    this plan's decisions;
  - the plan↔spec alignment check, mechanically: every contract a §9 row
    names is declared in a live spec, and every contract of those specs
    appears in some increment;
  - no `[verify]` survives in §9 or §13 (an assumption with no home);
  - no `### Increment N` heading sits outside §9, where none of the checks
    above would read it;
  - every §6 row graded `one-way` or `expensive` (now, or after a named
    milestone) carries
    its press verdict (`could-not-refute`, `refuted`, or `waived by owner`),
    in the row or on a plan line naming an ADR the row cites: a press the
    plan never ran is otherwise invisible (`grill.press`); a struck-through
    Reversibility cell is superseded;
  - a §11 risk table carries at least one press verdict, in a row or a
    press note in §11: the top risk goes to the press;
  - §14 is one action.

A fenced code block (``` or ~~~) is an example, not the plan: a heading inside
one opens no section and no increment, and its `- Label:` lines are no fields.
A fence indented under a field is that field's value, not a blank.

`--batches` is a second report beside the gate: within each wave it groups
the increments into spawns by the owner's batch table
(`delegation.effort-scale`): a batch is no larger than its hardest `Effort:`
allows, increments naming a common file run as consecutive batches past
that size, each a fresh spawn after the one before, and prose takes one writer per disjoint
file set (SPEC-0005 GRILL_BATCHES_FOLLOW_THE_EFFORT_TABLE).

`--waves` is a report beside the gate, never part of it: every check above
runs unchanged and decides the exit status. It levels the §9 increments into
waves (1 for an increment that depends on no increment, else one after its
latest dependency), prints each with its `Phase:`, and warns when two
increments no dependency path orders both name one file in `Files touched:`
(`delegation.waves`, `docs/graph/method/delegation-sequencing.md`). The
schedule is static: it reads §9 alone, never §15 or what is committed. A plan
no `Phase:` reaches is `unscheduled`; a dependency defect, or two increments
sharing one number, leaves it `not computed`, because a wave keyed on a wrong
edge is worse than none. `Files touched:` is free text, so its paths are
matched as strings only — nothing named there is opened or resolved — and an
overlap is a warning.

The ledger of a plan is the directory beside it named for its stem:
plans/grill.md keeps its increments in plans/grill/, and a plan at
docs/plans/<stem>.md keeps them in docs/plans/<stem>/. An index row's path
ends `<stem>/<file>.md`; it is read from the plan's side, so both
`plans/grill/x.md` and `docs/graph/plans/grill/x.md` reach plans/grill/x.md.

Installed at docs/graph/grill-lint.py by install.sh (like spec-lint.py).
Dependency-free. No project config: the plan's path and the spec heading
form are the seed's own contract. A plan kept outside docs/graph/ (the
seed's own round plans) names its spec and decision homes with --specs and
--decisions.

Usage:
  python3 docs/graph/grill-lint.py             # gate: exit 1 on a defect
  python3 docs/graph/grill-lint.py --list      # print the §9 increment graph
  python3 docs/graph/grill-lint.py --waves     # also print the §9 wave schedule
  python3 docs/graph/grill-lint.py --warn      # report but always exit 0
  python3 docs/graph/grill-lint.py --plan P    # lint another plan file
  python3 docs/graph/grill-lint.py --specs D   # read specs from D, not docs/graph/specs/
  python3 docs/graph/grill-lint.py --decisions D   # read decisions from D
"""
import fnmatch
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

FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
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
# The path ends `<stem>/<file>.md`, the plan's ledger (`index_path_re`).
FIELD_RE = re.compile(r"^\s*-\s*([A-Za-z][^:]{0,40}):(.*)$")
LABEL_ONLY_RE = re.compile(r"^\s*-\s*[^:]+:\s*$")
TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
LIB_REF_RE = re.compile(r"docs/graph/libraries/([\w.\-]+)\.md")
# A bare reference is one no `<name>:` qualifies; the qualified form cites
# another repository's decision and is never read as a bare number.
ADR_REF_RE = re.compile(r"(?<![\w.-]:)\bADR-(\d{4})\b")
QUALIFIED_ADR_RE = re.compile(r"(?<![\w.-])([A-Za-z0-9_][\w.-]*):ADR-(\d{4})\b")
ADR_FILE_RE = re.compile(r"^(?:adr-)?(\d{4})\b")
INC_REF_RE = re.compile(r"\bincrement\s+(\d+)", re.I)
CONTRACT_REF_RE = re.compile(r"(SPEC-\d{4})[\w\-]*/([A-Z][A-Z0-9_]{2,})")
CONTRACT_DECL_RE = re.compile(r"^###\s+Contract:\s*([A-Z][A-Z0-9_]{2,})\s*$", re.M)
STATUS_RE = re.compile(r"\*\*Status:\*\*\s*([\w-]+)")
FRONT_STATUS_RE = re.compile(r"^status:\s*([\w-]+)", re.M)
NA_RE = re.compile(r"^\s*(not applicable|n/?a|none)\b", re.I)
PRESSED_GRADE_RE = re.compile(r"\b(one-way|expensive)\b", re.I)
VERDICT_RE = re.compile(r"could-not-refute|\brefuted\b|waived by owner", re.I)
ADR_ID_RE = re.compile(r"\bADR-\d{4}\b")
REQUIRED_FIELDS = ("Spec contracts", "Tests to write (RED)", "Rollback path", "Depends on")
# Contract kinds: a spec whose §0 carries `- **Contract form:** kinds` gives
# each contract a `- **Check:** <kind>` line; a spec without it is legacy.
CONTRACT_FORM_RE = re.compile(r"^\s*-\s*\*\*Contract form:\*\*\s*kinds\b", re.M | re.I)
CHECK_RE = re.compile(r"^\s*-\s*\*\*Check:\*\*\s*(test|run|review|covered)\b", re.M | re.I)
HEADING_RE = re.compile(r"^#{2,3}\s", re.M)
SLUG_RE = re.compile(r"\b[A-Z][A-Z0-9_]{2,}\b")
QUOTED_RE = re.compile(r"[\"“]([^\"”]+)[\"”]")
PHASES = ("RED", "GREEN", "prose")
# Path tokens of a `Files touched:` value. One brace group, not nested, per
# whitespace-free chunk; a trailing `:12` or `:12-40` line reference; the
# characters prose wraps a path in; a bare file name, wildcards allowed.
BRACE_RE = re.compile(r"([^{}]*)\{([^{}]*)\}([^{}]*)")
LINE_REF_RE = re.compile(r":\d+(?:-\d+)?$")
PATH_EDGE = "'\"()[]<>:"
BARE_NAME_RE = re.compile(r"^[A-Za-z0-9_.*?-]*\.[A-Za-z0-9*]{1,10}$")
GLOB_RE = re.compile(r"[*?\[]")


def strip_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def fenced(lines: list[str]) -> list[bool]:
    """Per line: is it part of a fenced code block, fence lines included? A
    fence closes on a run of its own character at least as long as the one
    that opened it; an unclosed fence runs to the end, as CommonMark reads it."""
    out: list[bool] = []
    fence = ""                                  # the opening run, while inside
    for ln in lines:
        body = ln.rstrip("\r\n")
        m = FENCE_RE.match(body)
        out.append(bool(fence) or m is not None)
        if not fence and m:
            fence = m.group(1)
        elif fence and m and m.group(1).startswith(fence) and not body[m.end():].strip():
            fence = ""
    return out


def mask_fences(text: str) -> str:
    """The text with every fenced code block blanked to spaces, fence lines
    included. Length and line breaks are kept, so an offset found in the mask
    is the same offset in the text."""
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    for ln, inside in zip(lines, fenced(lines)):
        body = ln.rstrip("\r\n")
        out.append(" " * len(body) + ln[len(body):] if inside else ln)
    return "".join(out)


def section_spans(text: str) -> list[tuple[int, int, int]]:
    """(number, body start, body end) per `## N. Title` header outside a fence."""
    matches = list(SECTION_RE.finditer(mask_fences(text)))
    return [(int(m.group(1)), m.end(),
             matches[i + 1].start() if i + 1 < len(matches) else len(text))
            for i, m in enumerate(matches)]


def sections(text: str) -> dict[int, str]:
    """Section number -> body text (header excluded). The body keeps its
    fenced blocks: an example is still content that populates a section."""
    return {n: text[start:end] for n, start, end in section_spans(text)}


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


def unpressed_decisions(body: str, pressed: set[str]) -> list[tuple[str, str]]:
    """(decision, reversibility) of each §6 table row graded one-way or
    expensive with no
    press verdict: none in the row, and no ADR the row cites in `pressed` (the
    ADRs a verdict line of the plan names). The Reversibility column is found
    by its header, per table; a fenced table is an example and is not read."""
    out: list[tuple[str, str]] = []
    lines = body.splitlines()
    col = None                                  # None: not inside a table
    for raw, inside in zip(lines, fenced(lines)):
        s = raw.strip()
        if inside or not s.startswith("|"):
            col = None
            continue
        if TABLE_SEP_RE.match(s):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if col is None:                         # the table's header row
            col = next((i for i, c in enumerate(cells)
                        if c.lower().startswith("reversib")), -1)
            continue
        if not 0 <= col < len(cells):
            continue
        rev = cells[col]
        if rev.startswith("~~") or not PRESSED_GRADE_RE.search(rev) or VERDICT_RE.search(s):
            continue
        if pressed & set(ADR_ID_RE.findall(s)):
            continue
        out.append((cells[0].replace("~~", "")[:70], rev[:70]))
    return out


def fields(block: str) -> dict[str, str]:
    """`- Label: value` fields of an increment block; a value continues on
    indented lines until the next label. Strikethrough markers are dropped.

    A `- Label:` line inside a fence is an example, not a field; an indented
    fenced line is still text of the current value, so a RED command written
    as a fence under its label is a value and not a blank."""
    out: dict[str, str] = {}
    current = None
    lines = block.splitlines()
    for raw, inside in zip(lines, fenced(lines)):
        ln = raw.replace("~~", "")
        m = None if inside else FIELD_RE.match(ln)
        if m:
            current = m.group(1).strip()
            out[current] = m.group(2).strip()
        elif current and ln.startswith((" ", "\t")) and ln.strip():
            out[current] = (out[current] + " " + ln.strip()).strip()
    return out


def index_path_re(plan: Path) -> re.Pattern:
    """An index row's path: it ends `<stem>/<file>.md`, the plan's ledger."""
    return re.compile(r"(?<![\w.-])((?:[\w./-]*/)?" + re.escape(plan.stem) + r"/[\w.-]+\.md)")


def ledger_target(rel: str, plan: Path) -> Path:
    """The file an index row's path names, read from the plan's side.

    The path's part before `<stem>/` is where the row writer stood: nothing
    (`grill/x.md`), the plan's directory (`plans/grill/x.md`), or more of the
    path above it (`docs/graph/plans/grill/x.md`). When that part is the tail
    of the plan's directory, the row names the plan's own ledger. Anything else
    is joined to the plan's directory as written, and the containment check
    decides."""
    path = Path(rel)
    k = len(path.parts) - 2                     # the stem, before the file name
    here = plan.parent.parts
    if not path.is_absolute() and k <= len(here) and path.parts[:k] == here[len(here) - k:]:
        return plan.parent / Path(*path.parts[k:])
    return plan.parent / path


def increments(body: str, errs: list | None = None,
               plan: Path = PLAN) -> list[tuple[int, str, str]]:
    """(number, title, block) per increment in §9, in either form.

    INLINE — `### Increment N — title` written straight into §9. Every plant
    already has this, so it keeps working unchanged.

    LEDGER — §9 is an index, one row per increment, each pointing at a file
    in the plan's ledger (`plans/grill/` for `plans/grill.md`) that holds it. A plan-of-record grows for as long as
    the project does and §9 grows fastest: contracts, RED tests, rollback paths
    and dependencies for every increment ever planned. Held in one file that is
    read whole, a mature plan becomes the largest single thing a session loads,
    and the progressive discovery the whole method rests on is defeated by the
    document describing the work. The plan stays the ledger; the increments
    become files under it, and a session reads the index plus the one increment
    it is working on.

    Both forms may appear together — that is how a plan migrates, one increment
    at a time, without a flag day. Neither form is read inside a fence: blocks
    are sliced at offsets found in the masked text, and each block is returned
    unmasked, because a fence under a field is that field's value.
    """
    masked = mask_fences(body)
    out = []
    matches = list(INCREMENT_RE.finditer(masked))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        title = m.group(2).strip(" —-–:").strip()
        out.append((int(m.group(1)), title, body[m.end():end]))

    inline_nums = {n for n, _t, _b in out}
    seen = set(inline_nums)
    referenced: set[str] = set()
    grill_dir = plan.parent / plan.stem
    shown = f"{plan.parent.name}/{plan.stem}/"      # plans/grill/ for the plant
    path_re = index_path_re(plan)
    for row in INDEX_ROW_RE.finditer(masked):
        path_m = path_re.search(row.group(2))
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
        target = ledger_target(rel, plan)
        try:
            inside = target.resolve().is_relative_to(grill_dir.resolve())
        except (OSError, ValueError):
            inside = False
        if not inside:
            if errs is not None:
                errs.append(f"§9: increment {num} points outside {shown} "
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
        cm = list(INCREMENT_RE.finditer(mask_fences(child)))
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
    if errs is not None and grill_dir.is_dir():
        # Every .md in the ledger, at any depth and under any name. The
        # glob was `increment-*.md` and non-recursive, so a child called
        # `inc-03.md`, `increment_03.md`, or filed in a subdirectory was
        # unreachable work the orphan check could not see.
        for f in sorted(grill_dir.rglob("*.md")):
            if f.name not in referenced:
                errs.append(f"{shown}{f.name} is not indexed by §9 — an "
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


def plan_graph(incs: list[tuple[int, str, str]], fails: list):
    """(graph, efforts, dependency_defect, lib_needed, contract_refs) of the §9
    increments; each field defect is appended to `fails`. A graph row is
    (number, title, increment deps, library deps, contracts, Phase:, Files touched:).
    The one reading of §9's fields: the gate, `--waves`, `--batches` and
    `cycle.py` all take it from here."""
    numbers = [n for n, _, _ in incs]
    known = set(numbers)
    lib_needed: dict[str, list[int]] = {}
    contract_refs: dict[str, dict[str, list[int]]] = {}
    graph: list[tuple[int, str, list[int], list[str], list[str], str, str]] = []
    efforts: dict[int, str] = {}
    dependency_defect = False
    for n, title, block in incs:
        f = fields(block)
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
            else:
                continue
            dependency_defect = True            # every branch above; --waves will not level over it
        libs = LIB_REF_RE.findall(dep)
        for lib in libs:
            lib_needed.setdefault(lib, []).append(n)
        refs = CONTRACT_REF_RE.findall(f.get("Spec contracts", ""))
        for spec, slug in refs:
            contract_refs.setdefault(spec, {}).setdefault(slug, []).append(n)
        efforts[n] = f.get("Effort", "")
        graph.append((n, title, inc_deps, libs, [f"{s}/{c}" for s, c in refs],
                      f.get("Phase", "").strip(), f.get("Files touched", "")))
        if "[verify]" in mask_fences(block):
            fails.append(f"§9 increment {n}: carries `[verify]` — an assumption with no home; resolve it or move it to §12")
    return graph, efforts, dependency_defect, lib_needed, contract_refs


def spec_files(specs: Path = SPECS) -> dict[str, tuple[Path, str]]:
    """SPEC-NNNN -> (path, status) for every spec on disk."""
    out: dict[str, tuple[Path, str]] = {}
    if specs.is_dir():
        for p in sorted(specs.glob("SPEC-*.md")):
            key = p.name[:9]
            text = p.read_text(encoding="utf-8", errors="replace")
            out[key] = (p, spec_status(text))
    return out


# The specs directory's own pages: not specs, and never misnamed ones.
SPEC_DIR_EXEMPT = {"index.md", "readme.md"}


def misnamed_specs(specs: Path = SPECS) -> list[Path]:
    """Every Markdown file in the specs directory that is not `SPEC-*.md`,
    apart from its index and readme. `spec_files` reads the pattern alone, so
    a misnamed spec was skipped and a plan over it passed with its contracts
    unseen; spec-lint.py applies the same rule."""
    if not specs.is_dir():
        return []
    return sorted(p for p in specs.glob("*.md")
                  if not p.name.startswith("SPEC-") and p.name.lower() not in SPEC_DIR_EXEMPT)


def spec_status(text: str) -> str:
    """Frontmatter first, as spec-lint.py's status_of(); the body line only
    when the frontmatter has none, and never the template's "see frontmatter"."""
    if text.startswith("---"):
        m = FRONT_STATUS_RE.search(text.split("\n---", 1)[0])
        if m:
            return m.group(1).lower()
    m = STATUS_RE.search(text)
    return m.group(1).lower() if m and m.group(1).lower() != "see" else "unknown"


def spec_kinds(text: str) -> tuple[dict[str, str] | None, list[tuple[str, str, set[str]]]]:
    """(kind per contract, §10 rows) of a spec. Each contract's kind is its own
    `Check:` line; a contract with none reads as `test`, the kind for doubt
    (in a spec whose §0 declares `Contract form: kinds`, spec-lint names the
    missing line). The kinds are None for a spec with neither that §0 line nor
    any `Check:` line: its contracts read as kind `test` and add no check, so
    it lints exactly as before kinds existed. A §10 row is (risk, test cell,
    contracts covered): the Covers column when the header has one, else the
    first cell (the legacy `Contract / Failure` column)."""
    masked = mask_fences(text)
    secs = sections(masked)
    kinds: dict[str, str] = {}
    labelled = bool(CONTRACT_FORM_RE.search(secs.get(0, "")))
    for m in CONTRACT_DECL_RE.finditer(masked):
        nxt = HEADING_RE.search(masked, m.end())
        check = CHECK_RE.search(masked[m.end():nxt.start() if nxt else len(masked)])
        kinds[m.group(1)] = check.group(1).lower() if check else "test"
        labelled = labelled or check is not None
    if not labelled:
        return None, []
    rows: list[tuple[str, str, set[str]]] = []
    header = None
    for ln in secs.get(10, "").splitlines():
        s = ln.strip()
        if not s.startswith("|"):
            header = None
            continue
        if TABLE_SEP_RE.match(s):
            continue
        cells = [c.strip().strip("`") for c in s.strip("|").split("|")]
        if header is None:
            header = cells
            continue
        cov = next((i for i, c in enumerate(header) if c.lower().startswith("covers")), 0)
        test = next((i for i, c in enumerate(header) if c.lower().startswith("test")), 1)
        if max(cov, test) < len(cells):
            rows.append((cells[0] if cov else "", cells[test], set(SLUG_RE.findall(cells[cov]))))
    return kinds, rows


def cites_row(value: str, risk: str, test: str) -> bool:
    """Does a `Tests to write (RED):` value cite this §10 row: its test name
    (the part after `::`, or the whole cell), or its risk text, whole or as a
    quoted prefix (`"A malformed form payload..."`)?"""
    name = test.rsplit("::", 1)[-1].strip()
    if len(name) >= 3 and name in value:
        return True
    if risk and risk in value:
        return True
    return any(len(q) >= 8 and risk.startswith(q)
               for q in (q.strip().rstrip(".…").strip() for q in QUOTED_RE.findall(value)))


def kind_checks(incs: list[tuple[int, str, str]], specs: dict[str, tuple[Path, str]],
                shown: str) -> list[str]:
    """The checks contract kinds add to §9 (`grill.increment-shape`): a
    test-kind contract's increment cites a §10 row covering it; an increment
    with no test-kind contract schedules no RED; a run contract needs a `Run:`
    field and a review contract a `Review:` field. Only contracts of a spec in
    the kinds form are read; a legacy contract counts as kind test and adds no
    check, so a plan in today's form lints exactly as before."""
    out: list[str] = []
    cache: dict[str, tuple] = {}
    for n, _title, block in incs:
        f = fields(block)
        labels = {k.split("(")[0].strip(): v for k, v in f.items()}
        tests = f.get("Tests to write (RED)", "").strip()
        refs = CONTRACT_REF_RE.findall(f.get("Spec contracts", ""))
        kinds_here: list[tuple[str, str, str]] = []
        for spec, slug in refs:
            if spec not in specs:
                continue
            if spec not in cache:
                cache[spec] = spec_kinds(specs[spec][0].read_text(encoding="utf-8", errors="replace"))
            kinds, _rows = cache[spec]
            kinds_here.append((spec, slug, "test" if kinds is None else kinds.get(slug, "test")))
        if not any(cache[s][0] is not None for s, _c, _k in kinds_here):
            continue
        where = f"{shown} §9 increment {n}"
        for spec, slug, kind in kinds_here:
            if cache[spec][0] is None:
                continue
            if kind == "test":
                covering = [(r, t) for r, t, cov in cache[spec][1] if slug in cov]
                if not any(cites_row(tests, r, t) for r, t in covering):
                    fix = (f"rows covering it: {', '.join(t for _r, t in covering)}" if covering else
                           f"{spec} §10 has no row covering it yet; the spec owes one first (specify)")
                    out.append(f"{where}: contract {spec}/{slug} has kind test but `Tests to write (RED):` "
                               f"cites no {spec} §10 row covering it; cite the row's risk text in quotes "
                               f"or its test name ({fix})")
            elif kind in ("run", "review") and not labels.get(kind.capitalize(), "").strip():
                what = "the command that proves it" if kind == "run" else "what the reviewer confirms"
                out.append(f"{where}: contract {spec}/{slug} has kind {kind} but the increment has no "
                           f"`{kind.capitalize()}:` field; add `- {kind.capitalize()}: <{what}>`")
        if not any(k == "test" for _s, _c, k in kinds_here):
            if tests and not tests.lower().startswith("none"):
                out.append(f"{where}: no contract here has kind test, yet `Tests to write (RED):` "
                           f"schedules a RED spawn; write `none — <why>` (its run, review and covered "
                           f"contracts are proved without one)")
            if f.get("Phase", "").strip().split()[:1] == ["RED"]:
                out.append(f"{where}: no contract here has kind test, yet `Phase: RED`; its phase is GREEN")
    return out


def decision_files(decisions: Path = DECISIONS) -> dict[str, Path]:
    """ADR-NNNN -> path for every decision filed on disk.

    Both filename forms this seed has shipped resolve: `adr-NNNN-<slug>.md`,
    which the ADR template prescribes, and a bare `NNNN-<slug>.md`.
    """
    out: dict[str, Path] = {}
    if decisions.is_dir():
        for p in sorted(decisions.glob("*.md")):
            m = ADR_FILE_RE.match(p.name)
            if m:
                out[f"ADR-{m.group(1)}"] = p
    return out


def path_pieces(value: str) -> list[str]:
    """Candidate path tokens of a `Files touched:` value, which is free text.

    Backticks go; one brace group per whitespace-free chunk expands
    (`a{b,c}d` gives `abd` and `acd`); the chunk splits on `,` and `;`; each
    piece loses its line reference and wrapping punctuation until stable, then
    one leading `./`. A URL is no path. Which bare names count is the plan's
    to decide (`wave_report`), so they are all returned here."""
    out: list[str] = []
    for chunk in value.replace("`", "").split():
        m = BRACE_RE.fullmatch(chunk)
        for alt in (m.group(2).split(",") if m else [None]):
            for piece in re.split(r"[,;]", chunk if alt is None else m.group(1) + alt + m.group(3)):
                before = None
                while piece != before:
                    before = piece
                    piece = LINE_REF_RE.sub("", piece).strip(PATH_EDGE).rstrip(".")
                piece = piece[2:] if piece.startswith("./") else piece
                if piece and "://" not in piece:
                    out.append(piece)
    return out


def shared_file(x: str, y: str) -> str | None:
    """The file two path tokens both name, or None. They name one file when
    they are equal, when one is a glob `fnmatch` matches the other against,
    when one is a bare name equal to the other's last segment, or when one is a
    directory (a trailing `/`) the other sits under. The rule leans toward a
    false overlap: that costs a warning line, a missed one costs a lane race.

    The name printed is the more specific token: the one without a wildcard;
    else the one with a `/`; else `x`."""
    for a, b in ((x, y), (y, x)):
        if (a == b or (GLOB_RE.search(a) and fnmatch.fnmatchcase(b, a))
                or ("/" not in a and a == b.rsplit("/", 1)[-1])
                or (a.endswith("/") and b.startswith(a))):
            break
    else:
        return None
    if bool(GLOB_RE.search(x)) != bool(GLOB_RE.search(y)):
        return y if GLOB_RE.search(x) else x
    if ("/" in x) != ("/" in y):
        return x if "/" in x else y
    return x


def levels(graph: list[tuple]) -> tuple[dict[int, int], dict[int, set[int]]]:
    """(wave per increment, every increment each transitively depends on).

    The checks refused every forward, missing and self dependency before this
    runs, so what is left is acyclic in document order and one pass levels it."""
    wave: dict[int, int] = {}
    after: dict[int, set[int]] = {}
    for n, _title, deps, *_ in graph:
        wave[n] = 1 + max((wave[d] for d in deps), default=0)
        after[n] = set(deps).union(*(after[d] for d in deps))
    return wave, after


def file_tokens(graph: list[tuple]) -> dict[int, list[str]]:
    """The paths each increment's `Files touched:` names.

    A bare name is a path only when its extension ends a slashed path of this
    plan: a dotted fact key (`delegation.waves`) has a file name's shape, and a
    warning that fires on keys trains its reader to ignore it."""
    pieces = {n: path_pieces(files) for n, *_, files in graph}
    slashed = [p.lower() for ps in pieces.values() for p in ps if "/" in p]
    return {n: [p for p in ps if "/" in p or (
                BARE_NAME_RE.match(p) and any(s.endswith("." + p.rsplit(".", 1)[1].lower()) for s in slashed))]
            for n, ps in pieces.items()}


# The owner's batch table (`delegation.effort-scale`): increments per spawn by
# the hardest effort in the batch. RED `low` is "7 or more"; the planner uses 7.
BATCH_SIZE = {
    "RED":   {"low": 7, "medium-low": 7, "medium": 6, "medium-hard": 5, "hard": 5},
    "GREEN": {"low": 5, "medium-low": 3, "medium": 3, "medium-hard": 2, "hard": 1},
}
EFFORT_RE = re.compile(r"^\s*(medium-low|medium-hard|low|medium|hard)\b", re.I)
WORKER = {"RED": "tester", "GREEN": "implementer", "prose": "writer"}


def effort_labels(graph: list[tuple], efforts: dict[int, str]) -> dict[int, str | None]:
    """Each increment's `Effort:` label, or None when it carries none."""
    label: dict[int, str | None] = {}
    for n, *_ in graph:
        m = EFFORT_RE.match(efforts.get(n, ""))
        label[n] = m.group(1).lower() if m else None
    return label


def pack(members: list[int], ph: str, tokens: dict[int, list[str]],
         label: dict[int, str | None], order: dict[int, int],
         warns: list[str]) -> list[tuple[list[int], str]]:
    """The batches the effort table gives `members` of one phase, in §9 order:
    (increments, `increments 1, 4 (hardest low, size 7)`) per spawn. The one
    packing of `delegation.effort-scale`: `--batches` packs a wave, `cycle.py`
    the increments ready now."""
    # units: increments joined by a shared file, in §9 order
    parent = {n: n for n in members}

    def root(x: int) -> int:
        while parent[x] != x:
            x = parent[x]
        return x
    for i, a in enumerate(members):
        for b in members[i + 1:]:
            if any(shared_file(x, y) for x in tokens[a] for y in tokens[b]):
                parent[root(b)] = root(a)
    units: dict[int, list[int]] = {}
    for n in members:
        units.setdefault(root(n), []).append(n)
    ordered = sorted(units.values(), key=lambda u: order[u[0]])

    def cap(unit: list[int]) -> int:
        if ph == "prose":
            return len(unit)
        sizes = [BATCH_SIZE[ph][label[n]] if label[n] else 1 for n in unit]
        return min(sizes)

    # A unit larger than its size runs as consecutive batches, each a fresh
    # spawn: a shared file means one writer at a time, never a bigger spawn.
    batches: list[list[int]] = []
    after_prev: set[int] = set()            # batch index that waits for the one before
    if ph == "prose":
        batches = ordered
    else:
        for unit in ordered:
            for n in unit:
                if label[n] is None:
                    warns.append(f"§9 increment {n}: no Effort: label "
                                 f"({', '.join(BATCH_SIZE['RED'])}) — batched alone")
            if len(unit) > cap(unit):
                chunks, cur = [], []
                for n in unit:
                    if cur and len(cur) + 1 > cap(cur + [n]):
                        chunks.append(cur)
                        cur = []
                    cur.append(n)
                chunks.append(cur)
                for i, c in enumerate(chunks):
                    if i:
                        after_prev.add(len(batches))
                    batches.append(c)
            elif batches and len(batches) - 1 not in after_prev \
                    and len(batches[-1]) + len(unit) <= min(cap(batches[-1]), cap(unit)):
                batches[-1].extend(unit)
            else:
                batches.append(list(unit))
    out = []
    rank = list(BATCH_SIZE["RED"])
    for bi, b in enumerate(batches):
        hard = [label[n] for n in b if label[n]]
        hardest = max(hard, key=rank.index) if hard else "unlabelled"
        size = "" if ph == "prose" else f", size {cap(b)}"
        over = " — after the batch above: they share files" if bi in after_prev else ""
        out.append((b, f"increment{'s' if len(b) > 1 else ''} "
                       f"{', '.join(map(str, sorted(b, key=order.get)))} (hardest {hardest}{size}){over}"))
    return out


def batch_report(graph: list[tuple], efforts: dict[int, str],
                 dependency_defect: bool) -> tuple[list[str], list[str]]:
    """The `--batches` report: the spawns the effort table gives each wave.

    Within one wave and phase, increments that name a common file form one
    unit (one writer per file set, `delegation.lanes`); units are packed in §9
    order while the batch stays within the size its hardest member allows.
    Prose takes one writer per disjoint file set. An increment with no effort
    label is a batch of one. Like `--waves`, it reads §9 alone and changes no
    verdict."""
    if dependency_defect or len({n for n, *_ in graph}) < len(graph):
        return ["batches: not computed — §9 has dependency defects or duplicate numbers"], []
    if not any(phase for *_, phase, _files in graph):
        return ["batches: unscheduled — no §9 increment carries a Phase: field"], []
    wave, _after = levels(graph)
    tokens = file_tokens(graph)
    order = {n: i for i, (n, *_) in enumerate(graph)}
    warns: list[str] = []
    label = effort_labels(graph, efforts)
    cells: dict[tuple[int, str], list[int]] = {}
    for n, *_, phase, _files in graph:
        ph = phase.split()[0] if phase else ""
        if ph in PHASES:
            cells.setdefault((wave[n], ph), []).append(n)
    lines: list[str] = []
    counts = {"RED": 0, "GREEN": 0, "prose": 0}
    for (w, ph), members in sorted(cells.items(), key=lambda kv: (kv[0][0], PHASES.index(kv[0][1]))):
        for b, describe in pack(members, ph, tokens, label, order, warns):
            counts[ph] += 1
            lines.append(f"  wave {w} {ph} {WORKER[ph]}: {describe}")
    total = sum(counts.values())
    header = (f"batches: {total} spawn(s) for {sum(len(v) for v in cells.values())} increment(s) — "
              f"{counts['RED']} tester, {counts['GREEN']} implementer, {counts['prose']} prose "
              f"(delegation.effort-scale; security or concurrency GREEN stays a batch of one)")
    return [header] + lines, warns


def wave_report(graph: list[tuple], dependency_defect: bool) -> tuple[list[str], list[str]]:
    """The `--waves` report of §9: (lines to print, WARN lines to add).

    Reads each increment's title, `Phase:`, increment dependencies and
    `Files touched:` from the graph the checks built, and nothing else. It
    changes no verdict, so it cannot fail: a plan it cannot level gets a
    header saying why, and no wave line."""
    if not any(phase for *_, phase, _files in graph):
        return ["waves: unscheduled — no §9 increment carries a Phase: field"], []
    warns: list[str] = []
    for n, *_, phase, _files in graph:
        if not phase:
            warns.append(f"§9 increment {n}: no Phase: field")
        elif phase.split()[0] not in PHASES:
            warns.append(f"§9 increment {n}: Phase: {phase} is not RED, GREEN or prose")
    numbers = [n for n, *_ in graph]
    # A number carried twice makes every `Depends on:` naming it ambiguous; a
    # map keyed by number would level one of the two by the other's edges.
    if len(set(numbers)) < len(numbers):
        return ["waves: not computed — §9 has duplicate increment numbers"], warns
    if dependency_defect:
        return ["waves: not computed — §9 has dependency defects (see below)"], warns

    wave, after = levels(graph)
    lines = [f"waves: {max(wave.values())} wave(s), {len(graph)} increment(s) — "
             f"a static schedule from §9; what is committed is not read"]
    for _, (n, title, deps, _libs, _refs, phase, _files) in sorted(
            enumerate(graph), key=lambda e: (wave[e[1][0]], e[0])):
        arrows = f" <- {', '.join(map(str, dict.fromkeys(deps)))}" if deps else ""
        lines.append(f"  wave {wave[n]}: increment {n} "
                     f"({phase.split()[0] if phase else 'no phase'}) {title or '(untitled)'}{arrows}")

    tokens = file_tokens(graph)
    # Two increments no dependency path orders can be live at once, in one wave
    # or not; only a path from the earlier to the later can exist here.
    for i, a in enumerate(numbers):
        for b in numbers[i + 1:]:
            if a in after[b]:
                continue
            shared = dict.fromkeys(name for x in tokens[a] for y in tokens[b]
                                   if (name := shared_file(x, y)))
            if shared:
                warns.append(f"§9 increments {a} and {b} may run together and both name "
                             f"{', '.join(shared)} — one spawn holds both, or they are "
                             f"sequenced (delegation.lanes)")
    return lines, warns


def main() -> int:
    argv = sys.argv[1:]
    list_mode = "--list" in argv
    waves_mode = "--waves" in argv
    batches_mode = "--batches" in argv
    warn_mode = "--warn" in argv
    plan = PLAN
    if "--plan" in argv:
        plan = Path(argv[argv.index("--plan") + 1]).resolve()
    specs_dir, specs_shown = SPECS, "docs/graph/specs/"
    if "--specs" in argv:
        specs_shown = argv[argv.index("--specs") + 1]
        specs_dir, specs_shown = Path(specs_shown).resolve(), specs_shown.rstrip("/") + "/"
    decisions_dir, decisions_shown = DECISIONS, "docs/graph/decisions/"
    if "--decisions" in argv:
        decisions_shown = argv[argv.index("--decisions") + 1]
        decisions_dir, decisions_shown = Path(decisions_shown).resolve(), decisions_shown.rstrip("/") + "/"

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

    # --- §6: every one-way or expensive decision was pressed (grill.press) ----
    if 6 in secs:
        pressed = {a for ln in mask_fences(text).splitlines() if VERDICT_RE.search(ln)
                   for a in ADR_ID_RE.findall(ln)}
        for decision, rev in unpressed_decisions(secs[6], pressed):
            fails.append(f"§6: `{decision}` ({rev}) has no press verdict — spawn "
                         f"devils-advocate (grill.press) and record `could-not-refute`, `refuted`, "
                         f"or `waived by owner <date>` in the row's Refutation cell")

    # --- §11: the top risk was pressed (grill.press) -------------------------
    if 11 in secs:
        body11 = mask_fences(secs[11])
        risk_rows = [ln for ln in body11.splitlines()
                     if ln.strip().startswith("|") and not TABLE_SEP_RE.match(ln.strip())]
        if len(risk_rows) > 1 and not VERDICT_RE.search(body11):
            fails.append("§11: no risk carries a press verdict — the top risk by probability × "
                         "impact goes to devils-advocate (grill.press); record `could-not-refute`, "
                         "`refuted`, or `waived by owner <date>` in its Refutation cell")

    # --- §9: increment shape and dependency order ---------------------------
    # A heading outside §9 is well formed and read by nothing: its fields,
    # dependencies and contracts all go unchecked while the plan passes.
    spans = section_spans(text)
    for m in INCREMENT_RE.finditer(mask_fences(text)):
        where = next((n for n, start, end in spans if start <= m.start() < end), None)
        if where != 9:
            fails.append(f"{'§' + str(where) if where is not None else 'before §0'}: "
                         f"`### Increment {m.group(1)}` — increment heading outside §9 — "
                         f"invisible to the plan checks; move it into §9 or the ledger")
    incs = increments(secs.get(9, ""), fails, plan)
    if 9 in secs and not incs and not any(NA_RE.match(ln) for ln in populated.get(9, [])):
        fails.append("§9: no `### Increment N — title` rows, and no index rows "
                     f"pointing at files under {plan.parent.name}/{plan.stem}/")
    graph, efforts, dependency_defect, lib_needed, contract_refs = plan_graph(incs, fails)

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
    decisions = decision_files(decisions_dir)
    for num in sorted(set(ADR_REF_RE.findall(text))):
        if f"ADR-{num}" not in decisions:
            fails.append(f"ADR-{num} is named by the plan but is not filed in "
                         f"{decisions_shown} — a decision that is not yet "
                         f"accepted is filed with the status that says so "
                         f"(`status: proposed`), not left as a number in a table")
    # Another repository's decision: its number is that repository's, so a
    # local file of the same number proves nothing. Named once, never checked.
    external = dict.fromkeys(f"{name}:ADR-{num}" for name, num in QUALIFIED_ADR_RE.findall(text))
    notes = [f"{ref} is external (another repository's decision): not checked here"
             for ref in external]

    # --- plan <-> spec alignment ---------------------------------------------
    specs = spec_files(specs_dir)
    for p in misnamed_specs(specs_dir):
        fails.append(f"misnamed spec, not checked: {p.name} in {specs_shown} — a "
                     f"spec file is SPEC-NNNN-<surface>.md; rename it, or its "
                     f"contracts are never checked against a plan")
    for spec, slugs in sorted(contract_refs.items()):
        if spec not in specs:
            fails.append(f"§9 names {spec}, which is not in {specs_shown}")
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
    fails.extend(kind_checks(incs, specs, plan.name))

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
        for n, title, deps, libs, refs, _phase, _files in graph:
            arrows = ", ".join(f"<- {d}" for d in deps) or "<- (root)"
            print(f"  {n:>2} {title or '(untitled)'}  {arrows}"
                  f"{'  libs: ' + ', '.join(libs) if libs else ''}"
                  f"{'  contracts: ' + ', '.join(refs) if refs else ''}")
    if waves_mode:
        report, report_warns = wave_report(graph, dependency_defect)
        print("\n".join(report))
        warns.extend(report_warns)
    if batches_mode:
        report, report_warns = batch_report(graph, efforts, dependency_defect)
        print("\n".join(report))
        warns.extend(report_warns)

    for w in warns:
        print(f"  WARN {w}")
    for n in notes:
        print(f"  NOTE {n}")
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
