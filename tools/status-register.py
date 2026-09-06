#!/usr/bin/env python3
"""status-register: one lifecycle vocabulary, in frontmatter, machine-checked.

A plant accumulates decisions, specs, deviations and risks, and each of
them is at some point in a life: proposed, open, deferred, closed, or
superseded by something newer. When that fact lives in body prose it
drifts — an ADR's "## Status" says accepted while its index row says
superseded, a spec's metadata bullet still reads draft two releases
after it shipped — and nothing can answer "what is still open?" without
a human reading every file. This tool is the mechanical floor: the
status lives in frontmatter, in one vocabulary, with the companion keys
that make it honest, and any tree can be asked what it owes.

Vocabulary (frontmatter `status:`):

  base            open | deferred | hotfix | rejected | superseded | closed
  kind: adr       + proposed | accepted
  kind: spec      + draft | active | implemented | back-written
  kind: deviation + standing

Required companions:

  closed                  status_evidence
  superseded              superseded_by
  deferred                reopen_when
  open | hotfix | deferred  owner
  standing                ends_when
  always                  status_date  (YYYY-MM-DD)

The kind comes from frontmatter `kind:`; a file without one under a
`decisions/` or `specs/` directory is read as an ADR or spec, and the
finding says so when that inference is what decided it. A body
`## Status` section (or a `**Status:**` metadata bullet) may only point
at the frontmatter; a body value that differs is a failure naming both.
`legal_status` is a different vocabulary and is never read here.

Usage:
    status-register.py [--root DIR ...] [--strict-unknown]      # lint
    status-register.py [--root DIR ...] --open|--hotfix|--deferred|--rejected
                       [--by-kind K ...] [--since YYYY-MM-DD] [--json]
    status-register.py [--root DIR ...] --summary [--json]

    --root            directory scanned recursively for *.md
                      (repeatable; default: .)
    --strict-unknown  lint only: a file of kind adr/spec/deviation/risk
                      with no `status:` at all is a finding (default:
                      silent, so adoption is incremental)
    --open/--hotfix/--deferred/--rejected
                      query: list items in these statuses (any given;
                      none given lists every status-carrying file)
    --by-kind K       query: keep only this kind (repeatable)
    --since DATE      query: keep only status_date >= DATE
    --summary         query: one short paragraph — counts per status and
                      the three oldest open/hotfix — sized for a
                      session-start hook to inject
    --json            query: the same result as JSON, for tooling

Lint exits 0 clean, 1 with findings, 2 on a usage error — including a
run that matched no markdown file at all, which would otherwise print
the same clean verdict a real scan earns. Any query flag selects the
query role, which never fails on content: exit 0 (2 only on usage).

One line per query item, oldest status_date first:

    status  kind  id-or-path  owner  status_date  [companion]

where the companion is the one the status requires (reopen_when,
ends_when, status_evidence, superseded_by) and `-` stands for absent.

Importable: scan() returns Item records and lint() Finding records, so
a hook or a host linter calls them in-process instead of keeping a
second copy. Dependency-free; bare python3.
"""
import argparse
import datetime as _dt
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

BASE_STATUSES = ("open", "deferred", "hotfix", "rejected", "superseded", "closed")
KIND_STATUSES = {
    "adr": ("proposed", "accepted"),
    "spec": ("draft", "active", "implemented", "back-written"),
    "deviation": ("standing",),
}
ALL_STATUSES = frozenset(BASE_STATUSES).union(*KIND_STATUSES.values())
# Kinds that must carry a lifecycle status once --strict-unknown is on.
STATUS_KINDS = ("adr", "spec", "deviation", "risk")
# Directory name → kind, for ADRs and specs whose frontmatter carries no kind.
DIR_KINDS = {"decisions": "adr", "specs": "spec"}
# status → the companion key it requires (owner handled separately: three
# statuses share it).
COMPANION = {
    "closed": "status_evidence",
    "superseded": "superseded_by",
    "deferred": "reopen_when",
    "standing": "ends_when",
}
OWNER_STATUSES = frozenset({"open", "hotfix", "deferred"})
# The order statuses are reported in (--summary counts, and the tie-break
# inside one status_date): attention first, then the lifecycle's rest.
STATUS_ORDER = ("hotfix", "open", "deferred", "standing", "proposed", "draft",
                "active", "accepted", "implemented", "back-written",
                "rejected", "superseded", "closed")

DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
HEADING_RE = re.compile(r"^#{1,6}\s*(?:\d+[.)]?\s*)?status\s*$", re.I)
ANY_HEADING_RE = re.compile(r"^#{1,6}\s")
STATUS_BULLET_RE = re.compile(r"^\s*[-*]\s*\*\*status:?\*\*:?\s*(.*)$", re.I)
TOKEN_RE = re.compile(r"[a-z][a-z-]*")


@dataclass(frozen=True)
class Finding:
    """One violation. `message` carries no path prefix so each caller can
    render it its own way — the CLI as `path:line: message`."""
    path: str
    line: int
    rule: str
    message: str


@dataclass
class Item:
    """One markdown file with frontmatter. `status` is None for a file
    that carries no `status:` key — kept so --strict-unknown can ask why."""
    path: str
    meta: dict
    lines: dict                      # frontmatter key → line number
    kind: str | None
    kind_source: str | None          # "frontmatter" | "directory" | None
    body_statuses: list = field(default_factory=list)  # [(line, value)]

    @property
    def status(self):
        return _text(self.meta.get("status"))

    @property
    def id(self) -> str:
        return _text(self.meta.get("id")) or self.path

    @property
    def line(self) -> int:
        return self.lines.get("status", 1)

    def value(self, key):
        return _text(self.meta.get(key))

    @property
    def companion_key(self):
        return COMPANION.get(self.status)

    def kind_label(self) -> str:
        """The kind as a finding should name it: an inferred kind says
        where the inference came from, so a reader can correct the file
        or the directory rather than guess which one decided."""
        if self.kind is None:
            return "kind unknown (no `kind:` key, not under decisions/ or specs/)"
        if self.kind_source == "directory":
            return f"kind {self.kind}, inferred from the directory name"
        return f"kind {self.kind}"

    def as_dict(self) -> dict:
        return {
            "path": self.path, "id": self.id, "kind": self.kind,
            "status": self.status, "owner": self.value("owner"),
            "status_date": self.value("status_date"),
            "status_evidence": self.value("status_evidence"),
            "superseded_by": self.value("superseded_by"),
            "reopen_when": self.value("reopen_when"),
            "ends_when": self.value("ends_when"),
        }


def _text(v):
    """A frontmatter value as the string it is, or None when absent/empty.
    The parser hands back ints for bare digits and [] for a key with no
    scalar; a companion is present only when it says something."""
    if v is None or v == "" or v == []:
        return None
    if isinstance(v, list):
        return "; ".join(str(x) for x in v)
    return str(v)


def _scalar(v: str):
    v = v.strip()
    if v and v[0] in "\"'" and v[-1] == v[0] and len(v) > 1:
        return v[1:-1]
    if "  #" in v:
        v = v.split("  #", 1)[0].strip()
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    return v


def parse_frontmatter(text: str):
    """The YAML subset the node contract permits (`key: scalar`, and
    `key:` followed by `  - item` lines), the way graph-lint reads it —
    but tolerant: a line that fits neither shape is skipped rather than
    raised, because frontmatter well-formedness is graph-lint's rule, not
    this one's. Returns (meta, key→line, body, body_first_line) or None
    when the file has no terminated frontmatter block."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    raw, body = text[4:end], text[end + 5:]
    meta: dict = {}
    lines: dict = {}
    current = None
    for lineno, line in enumerate(raw.split("\n"), start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")):
            item = line.strip()
            if item.startswith("- ") and current is not None:
                meta.setdefault(current, []).append(_scalar(item[2:]))
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        lines[key] = lineno
        if value:
            meta[key] = _scalar(value)
            current = None
        else:
            meta[key] = []
            current = key
    body_first_line = raw.count("\n") + 3      # opening ---, raw, closing ---
    return meta, lines, body, body_first_line


def _body_statuses(body: str, first_line: int):
    """Every vocabulary value the body states as a status: the tokens
    under a `## Status` heading (until the next heading) and on any
    `**Status:**` metadata bullet. Returned as (line, value) so a finding
    can point at the restatement, not the file."""
    found = []
    in_section = False
    for n, line in enumerate(body.split("\n"), start=first_line):
        if ANY_HEADING_RE.match(line):
            in_section = bool(HEADING_RE.match(line))
            continue
        m = STATUS_BULLET_RE.match(line)
        scope = m.group(1) if m else (line if in_section else None)
        if scope is None:
            continue
        for tok in TOKEN_RE.findall(scope.lower()):
            if tok in ALL_STATUSES:
                found.append((n, tok))
    return found


def infer_kind(meta: dict, path: Path):
    """(kind, source): frontmatter wins; else the nearest enclosing
    directory named in DIR_KINDS; else nothing."""
    k = _text(meta.get("kind"))
    if k:
        return k, "frontmatter"
    for part in reversed(path.parent.parts):
        if part in DIR_KINDS:
            return DIR_KINDS[part], "directory"
    return None, None


def iter_files(paths):
    """Every *.md under each directory (a file contributes itself), sorted
    per root and de-duplicated by real path."""
    seen: dict = {}
    for p in paths:
        p = Path(p)
        if p.is_dir():
            for f in sorted(p.rglob("*.md")):
                # Blank forms are not items: anything under a templates/ tree, an
                # underscore-prefixed file, or *.template.md carries placeholder
                # status by design and must neither lint nor count.
                rel_parts = f.relative_to(p).parts
                if "templates" in rel_parts[:-1] or f.name.startswith("_") or f.name.endswith(".template.md"):
                    continue
                if f.is_file():
                    seen.setdefault(f.resolve(), f)
        elif p.is_file():
            seen.setdefault(p.resolve(), p)
    return list(seen.values())


def scan(paths, relative_to=None):
    """One Item per markdown file with frontmatter under `paths`, in file
    order. Files without frontmatter carry no lifecycle and are not
    items. `relative_to` trims the reported path to a root the caller
    reports against."""
    items: list[Item] = []
    for f in iter_files(paths):
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        parsed = parse_frontmatter(text)
        if parsed is None:
            continue
        meta, lines, body, first = parsed
        rel = (f.relative_to(relative_to).as_posix()
               if relative_to else f.as_posix())
        kind, source = infer_kind(meta, f)
        items.append(Item(rel, meta, lines, kind, source,
                          _body_statuses(body, first)))
    return items


def allowed_statuses(kind):
    return BASE_STATUSES + KIND_STATUSES.get(kind, ())


def _owning_kinds(status):
    return [k for k, vals in KIND_STATUSES.items() if status in vals]


def lint(items, strict_unknown=False):
    """Every D-STATUS finding over `items`, in item order then rule order:
    vocabulary, companions, status_date, body restatement. With
    `strict_unknown`, a status-less file of a kind that must carry one
    is a finding too."""
    findings: list[Finding] = []

    def add(item, line, rule, msg):
        findings.append(Finding(item.path, line, rule, msg))

    for it in items:
        status = it.status
        if status is None:
            if strict_unknown and it.kind in STATUS_KINDS:
                add(it, 1, "missing-status",
                    f"no `status:` in frontmatter ({it.kind_label()}; "
                    f"this kind must carry a lifecycle status)")
            continue

        allowed = allowed_statuses(it.kind)
        if status not in allowed:
            owners = _owning_kinds(status)
            hint = (f"; '{status}' belongs to kind {'/'.join(owners)}"
                    if owners else "")
            add(it, it.line, "vocabulary",
                f"status '{status}' is not in the vocabulary for "
                f"{it.kind_label()} — allowed: {' | '.join(allowed)}{hint}")

        if status in OWNER_STATUSES and not it.value("owner"):
            add(it, it.line, "companion",
                f"status '{status}' requires `owner`")
        key = COMPANION.get(status)
        if key and not it.value(key):
            add(it, it.line, "companion",
                f"status '{status}' requires `{key}`")

        date = it.value("status_date")
        if date is None:
            add(it, it.line, "status-date",
                "`status_date` is required whenever `status` is set")
        elif not _valid_date(date):
            add(it, it.lines.get("status_date", it.line), "status-date",
                f"`status_date` '{date}' is not a YYYY-MM-DD date")

        for line, value in it.body_statuses:
            if value != status:
                add(it, line, "body-status",
                    f"body states status '{value}' but frontmatter says "
                    f"'{status}' — status lives in frontmatter only; the "
                    f"body may carry a pointer, never a value")
    return findings


def _valid_date(s: str) -> bool:
    if not DATE_RE.fullmatch(s):
        return False
    try:
        _dt.date.fromisoformat(s)
    except ValueError:
        return False
    return True


# ----------------------------------------------------------------- query ---

def _sort_key(it: Item):
    """Oldest status_date first; a missing date sorts last (it cannot
    claim age); ties break attention-first then by id."""
    date = it.value("status_date")
    rank = (STATUS_ORDER.index(it.status)
            if it.status in STATUS_ORDER else len(STATUS_ORDER))
    return (date is None, date or "", rank, it.id)


def select(items, statuses=(), kinds=(), since=None):
    """The status-carrying items matching every given filter, sorted
    oldest-first. Empty `statuses` / `kinds` mean "any"."""
    out = []
    for it in items:
        if it.status is None:
            continue
        if statuses and it.status not in statuses:
            continue
        if kinds and it.kind not in kinds:
            continue
        if since:
            d = it.value("status_date")
            if d is None or not _valid_date(d) or d < since:
                continue
        out.append(it)
    return sorted(out, key=_sort_key)


def format_line(it: Item) -> str:
    companion = it.value(it.companion_key) if it.companion_key else None
    cols = [it.status, it.kind or "-", it.id, it.value("owner") or "-",
            it.value("status_date") or "-"]
    if it.companion_key:
        cols.append(f"{it.companion_key}={companion or '-'}")
    return "  ".join(cols)


def summarize(items, roots=()):
    """Counts per status and the three oldest open/hotfix, as a dict; the
    prose rendering is summary_text()."""
    tracked = select(items)
    counts: dict = {}
    for it in tracked:
        counts[it.status] = counts.get(it.status, 0) + 1
    ordered = {s: counts[s] for s in STATUS_ORDER if s in counts}
    ordered.update({s: c for s, c in sorted(counts.items())
                    if s not in ordered})
    attention = select(items, statuses=("open", "hotfix"))[:3]
    return {"tracked": len(tracked), "counts": ordered,
            "oldest_attention": [it.as_dict() for it in attention],
            "roots": [str(r) for r in roots]}


def summary_text(summary: dict) -> str:
    """One paragraph, sized for a session-start hook (~400 chars): what
    the register holds and the three oldest items that need a hand."""
    if not summary["tracked"]:
        where = ", ".join(summary["roots"]) or "."
        return f"Status register: no status-carrying files under {where}."
    counts = ", ".join(f"{n} {s}" for s, n in summary["counts"].items())
    text = f"Status register: {summary['tracked']} tracked — {counts}."
    oldest = summary["oldest_attention"]
    if not oldest:
        return text + " Nothing open or hotfix."
    parts = []
    for d in oldest:
        owner = f", owner {d['owner']}" if d["owner"] else ""
        parts.append(f"{d['id']} ({d['status']} since "
                     f"{d['status_date'] or 'undated'}{owner})")
    return text + " Oldest needing attention: " + "; ".join(parts) + "."


# ------------------------------------------------------------------- CLI ---

def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", action="append", metavar="DIR",
                    help="directory scanned recursively for *.md "
                         "(repeatable; default: .)")
    ap.add_argument("--strict-unknown", action="store_true",
                    help="lint: a status-less adr/spec/deviation/risk "
                         "is a finding")
    q = ap.add_argument_group("query (never fails on content)")
    for s in ("open", "hotfix", "deferred", "rejected"):
        q.add_argument(f"--{s}", action="append_const", dest="statuses",
                       const=s, help=f"list items with status {s}")
    q.add_argument("--by-kind", action="append", metavar="K", default=[],
                   help="keep only this kind (repeatable)")
    q.add_argument("--since", metavar="YYYY-MM-DD",
                   help="keep only status_date >= this date")
    q.add_argument("--summary", action="store_true",
                   help="one paragraph: counts + three oldest open/hotfix")
    q.add_argument("--json", action="store_true",
                   help="emit the query result as JSON")
    args = ap.parse_args()

    roots = args.root or ["."]
    missing = [p for p in roots if not Path(p).exists()]
    if missing:
        for p in missing:
            print(f"  !! no such path: {p}")
        return 2
    if args.since and not _valid_date(args.since):
        print(f"  !! --since wants YYYY-MM-DD, got {args.since!r}")
        return 2

    querying = bool(args.statuses or args.by_kind or args.since
                    or args.summary or args.json)
    files = iter_files(roots)
    if not files and not querying:
        # A lint over an empty set is a green lie: a mistyped --root would
        # otherwise print the PASS a real scan earns. A query may be empty
        # — a fresh plant owes nothing yet — and says so.
        print(f"  !! matched 0 markdown files under {', '.join(roots)} — "
              f"refusing a vacuous pass")
        return 2
    items = scan(roots)

    if querying:
        if args.summary:
            summary = summarize(items, roots)
            print(json.dumps(summary, indent=2) if args.json
                  else summary_text(summary))
            return 0
        chosen = select(items, statuses=args.statuses or (),
                        kinds=args.by_kind, since=args.since)
        if args.json:
            print(json.dumps([it.as_dict() for it in chosen], indent=2))
        else:
            for it in chosen:
                print(format_line(it))
        return 0

    findings = lint(items, strict_unknown=args.strict_unknown)
    if findings:
        print(f"status register: FAIL ({len(findings)} finding(s))")
        for f in findings:
            print(f"  - {f.path}:{f.line}: {f.message}")
        return 1
    carrying = sum(1 for it in items if it.status is not None)
    print(f"status register: PASS — {len(files)} file(s) scanned, "
          f"{carrying} status-carrying")
    return 0


if __name__ == "__main__":
    sys.exit(main())
