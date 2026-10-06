#!/usr/bin/env python3
"""session-metrics: read the Session metrics block of a plant's delivery entries.

`protocols/deliver.md` defines a Session metrics block that every full-form
(Tier 2 and Tier 3) delivery carries, appended to the plant's
`docs/graph/changelog.md`. This tool reads that block. It has two roles.

  lint   --since YYYY-MM-DD [--entry LINE]
         judges every delivery entry dated on or after --since (or, with
         --entry, only the entry whose heading is on LINE; every other
         since-date defect is printed on a `note:` line). Exit 1 when a
         judged Tier 2 or Tier 3 entry has no block, a missing line, an
         empty line, a `not recorded` with no reason, or a Tier value that
         names no tier.
  query  --all [--json]   one record per entry, with its raw line values
         --labels         the labels of the deliver node's template block

The labels are read at run time from the deliver node's fenced template
(the first fenced block holding a `## Session metrics` line); this file
holds no copy of the list, so a plant that changes its block is checked
against its own block. Stdlib only, config-free, writes nothing.

Exit codes: 0 pass (query: always, on content); 1 lint findings;
2 usage error, `--entry` naming a line that is not a delivery heading,
a missing or unreadable input, a deliver node with no template block.
Contract: SPEC-0006-session-metrics.
"""
import argparse
import datetime
import json
import os
import re
import sys

FORMS = ("a delivery entry is a heading `Delivery — <title> — YYYY-MM-DD` "
         "or `T<n> delivery — <title> — YYYY-MM-DD`")
DELIVERY_RE = re.compile(
    r"^(?:T(?P<tier>[0-3])\s+)?delivery(?P<compact>\s*\(compact\))?(?:\s*[—–]|\s+-\s)",
    re.IGNORECASE)
LINE_RE = re.compile(
    r"^\s*[-*+]\s+(?:\*\*)?(?P<label>[^:*]+?)(?:\*\*)?\s*:\s*(?P<value>.*)$")
ITEM_RE = re.compile(r"^\s*[-*+]\s")
HEADING_RE = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*$")
FENCE_OPEN_RE = re.compile(r"^( {0,3})(`{3,}|~{3,})(.*)$")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
SLOT_RE = re.compile(r"^<[^<>]*>")
TIER_VALUE_RE = re.compile(r"^(?:tier\s+)?(T[0-3])(?![0-9])", re.IGNORECASE)
EMPTY_WORDS = {"tbd", "todo", "?", "...", "…", "-", "–", "—"}


def split_lines(text):
    """Lines counted the way `grep -n` counts them (§6 Reading the file):
    only `\n` ends a line, and one `\r` before it is dropped. A lone `\r`,
    a form feed, U+2028, U+2029 and U+0085 never split a line, which
    `str.splitlines()` would do."""
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return [ln[:-1] if ln.endswith("\r") else ln for ln in lines]


class Fatal(Exception):
    """An input problem: exit 2 with the message."""


def norm(label):
    return " ".join(label.split()).casefold()


def read_text(path):
    try:
        with open(path, encoding="utf-8-sig", newline="") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError) as exc:
        raise Fatal(f"{path} could not be read: {exc}")


def fence_mask(lines):
    """A list of booleans: True where the line is part of a fenced block
    (the fence lines included). CommonMark fences: up to three spaces of
    indent, three or more backticks or tildes, closed by the same character
    at least as long; an unclosed fence runs to the end."""
    mask = [False] * len(lines)
    open_char, open_len = None, 0
    for i, line in enumerate(lines):
        if open_char is None:
            m = FENCE_OPEN_RE.match(line)
            if m and not (m.group(2)[0] == "`" and "`" in m.group(3)):
                open_char, open_len = m.group(2)[0], len(m.group(2))
                mask[i] = True
            continue
        mask[i] = True
        s = line.rstrip()
        stripped = s.lstrip(" ")
        if (len(s) - len(stripped) <= 3 and stripped
                and set(stripped) == {open_char} and len(stripped) >= open_len):
            open_char, open_len = None, 0
    return mask


def headings(lines, mask):
    """[(index, level, text)] for every ATX heading outside a fence."""
    out = []
    for i, line in enumerate(lines):
        if mask[i]:
            continue
        m = HEADING_RE.match(line)
        if m:
            out.append((i, len(m.group(1)), (m.group(2) or "").strip()))
    return out


def parse_deliver(path):
    """(labels in template order, section names) from the deliver node."""
    if not os.path.isfile(path):
        raise Fatal(f"the deliver node {path} does not exist")
    lines = split_lines(read_text(path))
    i = 0
    while i < len(lines):
        m = FENCE_OPEN_RE.match(lines[i])
        if not m or (m.group(2)[0] == "`" and "`" in m.group(3)):
            i += 1
            continue
        ch, n = m.group(2)[0], len(m.group(2))
        j = i + 1
        body = []
        while j < len(lines):
            s = lines[j].rstrip()
            st = s.lstrip(" ")
            if len(s) - len(st) <= 3 and st and set(st) == {ch} and len(st) >= n:
                break
            body.append(lines[j])
            j += 1
        if any(b.strip() == "## Session metrics" for b in body):
            labels, sections, inside = [], [], False
            for b in body:
                hm = HEADING_RE.match(b)
                if hm:
                    text = (hm.group(2) or "").strip()
                    if len(hm.group(1)) == 2:
                        sections.append(text)
                    inside = b.strip() == "## Session metrics"
                    continue
                if inside:
                    lm = LINE_RE.match(b)
                    if lm and lm.group("label").strip():
                        labels.append(" ".join(lm.group("label").split()))
            if not labels:
                raise Fatal(f"{path}: no Session metrics template was found: "
                            "the fenced `## Session metrics` block names no label")
            return labels, sections
        i = j + 1
    raise Fatal(f"{path}: no Session metrics template was found: no fenced block "
                "holds a `## Session metrics` line")


def classify(value):
    """None when the value is filled, else the finding code."""
    v = value.strip()
    if not v or SLOT_RE.match(v) or v.casefold() in EMPTY_WORDS:
        return "METRICS_LINE_EMPTY"
    if v.casefold().startswith("not recorded"):
        rest = v[len("not recorded"):].strip()
        for p in (":", "—", "–", "-", "("):
            if rest.startswith(p):
                rest = rest[len(p):].strip()
                break
        if not any(c.isalnum() for c in rest) or SLOT_RE.match(rest):
            return "METRICS_REASON_MISSING"
    return None


def read_block(lines, mask, start, end):
    """[(index, label, value)] of the metrics lines in lines[start:end].
    A fenced line is not a metrics line (§6)."""
    items = []
    for i in range(start, end):
        if mask[i]:
            continue
        line = lines[i]
        m = LINE_RE.match(line)
        if m:
            value = m.group("value").strip()
            if line.lstrip()[1:].lstrip().startswith("**") and value.startswith("**"):
                value = value[2:].strip()
            items.append([i, m.group("label").strip(), value])
        elif items and line.strip() and len(line) - len(line.lstrip(" ")) >= 2 \
                and not ITEM_RE.match(line):
            items[-1][2] = (items[-1][2] + " " + line.strip()).strip()
    return items


def judge(entry, lines, mask, labels):
    """Fill entry['tier'], ['status'], ['lines'], ['findings']."""
    findings = []
    items = read_block(lines, mask, entry["block"] + 1, entry["block_end"]) \
        if entry["block"] is not None else []
    first = {}
    for idx, label, value in items:
        first.setdefault(norm(label), (idx, label, value))
    entry["lines"] = {label: value for _, label, value in
                      (first[k] for k in first)}
    tier = entry["heading_tier"]
    tier_line = first.get("tier")
    tier_unreadable = None
    if tier_line is not None:
        tv = tier_line[2]
        m = TIER_VALUE_RE.match(tv.lstrip("`*_"))
        if m:
            tier = m.group(1).upper()
        elif classify(tv) is None and not tv.casefold().startswith("not recorded"):
            tier_unreadable = tier_line
    entry["tier"] = tier
    if entry["marker"] == "compact" or tier in ("T0", "T1"):
        entry["status"], entry["findings"] = "exempt", []
        return
    if entry["block"] is None:
        findings.append(("METRICS_BLOCK_MISSING", entry["line"],
                         "the entry has no Session metrics block"))
    else:
        bline = entry["block"] + 1
        for label in labels:
            got = first.get(norm(label))
            if got is None:
                findings.append(("METRICS_LINE_MISSING", bline,
                                 f"{label}: the block has no `- {label}:` line; fill it, "
                                 "or write `not recorded: <reason>`"))
                continue
            code = classify(got[2])
            if code == "METRICS_LINE_EMPTY":
                findings.append((code, got[0] + 1,
                                 f"{label}: the value is empty or a template placeholder; "
                                 "fill it, or write `not recorded: <reason>`"))
            elif code == "METRICS_REASON_MISSING":
                findings.append((code, got[0] + 1,
                                 f"{label}: `not recorded` needs a reason: "
                                 "`not recorded: <reason>`"))
            elif tier_unreadable is not None and got is tier_unreadable:
                findings.append(("METRICS_TIER_UNREADABLE", got[0] + 1,
                                 f"{label}: `{got[2]}` names no tier; start the value "
                                 "with T0, T1, T2 or T3"))
    entry["findings"] = [{"code": c, "line": ln, "message": msg}
                         for c, ln, msg in findings]
    entry["status"] = "incomplete" if findings else "filled"


def parse_changelog(text, sections):
    """Every delivery entry and every unmarked block, in file order."""
    lines = split_lines(text)
    mask = fence_mask(lines)
    heads = headings(lines, mask)
    section_set = {norm(s) for s in sections}
    is_metrics = lambda t: norm(t.rstrip().rstrip(":")) == "session metrics"
    entries, spans = [], []
    for k, (i, level, text) in enumerate(heads):
        m = DELIVERY_RE.match(text)
        if not m:
            continue
        end_k = len(heads)
        for kk in range(k + 1, len(heads)):
            _, lv, tx = heads[kk]
            if norm(tx) in section_set:
                continue
            # a delivery heading, a dated heading at any level, or a same-or-higher
            # heading ends the entry (§6 span; DATED_SUBHEADING_IN_ENTRY is its price)
            if DELIVERY_RE.match(tx) or DATE_RE.search(tx) or lv <= level:
                end_k = kk
                break
        end = heads[end_k][0] if end_k < len(heads) else len(lines)
        block = block_end = None
        for kk in range(k + 1, end_k):
            if is_metrics(heads[kk][2]):
                block = heads[kk][0]
                block_end = heads[kk + 1][0] if kk + 1 < end_k else end
                break
        dates = DATE_RE.findall(text)
        entries.append({
            "line": i + 1, "heading": text, "date": dates[-1] if dates else None,
            "marker": "compact" if m.group("compact") else "delivery",
            "heading_tier": f"T{m.group('tier')}" if m.group("tier") else None,
            "block": block, "block_end": block_end})
        spans.append((i, end))
    for k, (i, level, text) in enumerate(heads):
        if not is_metrics(text) or any(a <= i < b for a, b in spans):
            continue
        parent = None
        for kk in range(k - 1, -1, -1):
            if heads[kk][1] < level:
                parent = heads[kk]
                break
        block_end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        pi, _, ptext = parent if parent else heads[k]
        dates = DATE_RE.findall(ptext)
        entries.append({
            "line": pi + 1, "heading": ptext, "date": dates[-1] if dates else None,
            "marker": "unmarked", "heading_tier": None,
            "block": i, "block_end": block_end})
    entries.sort(key=lambda e: (e["line"], e["block"] if e["block"] is not None else -1))
    return lines, mask, entries


def record(entry):
    return {k: entry[k] for k in
            ("line", "heading", "date", "marker", "tier", "status", "lines", "findings")}


def finding_text(path, f):
    return f"{path}:{f['line']}: {f['code']}: {f['message']}"


def run_lint(args, path, labels, sections, default_changelog):
    since = args.since
    if not os.path.exists(path):
        if default_changelog:
            print(f"session metrics: FAIL (1 finding) — {path}, entries since {since}")
            print(f"  - {path}: NO_DELIVERY_ENTRY: {path} does not exist; {FORMS}")
            return 1
        raise Fatal(f"the changelog {path} does not exist")
    lines, mask, entries = parse_changelog(read_text(path), sections)
    entries = [e for e in entries if e["marker"] != "unmarked"]
    target = None
    if args.entry is not None:
        target = next((e for e in entries if e["line"] == args.entry), None)
        if target is None:
            print(f"{path}:{args.entry}: ENTRY_LINE_NOT_A_DELIVERY_HEADING: line "
                  f"{args.entry} is not a delivery heading; {FORMS}", file=sys.stderr)
            return 2
    notes = []
    since_entries = []
    for e in entries:
        if e is target:
            continue
        if e["date"] is None:
            notes.append(f"  note: {path}:{e['line']}: undated delivery heading, not judged")
        elif e["date"] >= since:
            since_entries.append(e)
    if target is not None:
        judged, others = [target], since_entries
    else:
        judged, others = since_entries, []
    for e in judged + others:
        judge(e, lines, mask, labels)
    for e in others:
        for f in e["findings"]:
            notes.append(f"  note: {finding_text(path, f)} (not this run's entry; not judged)")
    if not judged:
        print(f"session metrics: FAIL (1 finding) — {path}, entries since {since}")
        print(f"  - {path}: NO_DELIVERY_ENTRY: no delivery entry dated on or after {since}; {FORMS}")
        for n in notes:
            print(n)
        return 1
    found = [f for e in judged for f in e["findings"]]
    n = len(judged)
    noun = "delivery entry" if n == 1 else "delivery entries"
    scope = f" (line {target['line']})" if target is not None else ""
    if not found:
        filled = sum(e["status"] == "filled" for e in judged)
        exempt = sum(e["status"] == "exempt" for e in judged)
        print(f"session metrics: PASS — {n} {noun}{scope} since {since}: "
              f"{filled} filled, {exempt} exempt")
        rc = 0
    else:
        word = "finding" if len(found) == 1 else "findings"
        print(f"session metrics: FAIL ({len(found)} {word}) — {path}, {n} {noun}{scope} "
              f"since {since}")
        for f in found:
            print(f"  - {finding_text(path, f)}")
        rc = 1
    for note in notes:
        print(note)
    return rc


def run_all(args, path, labels, sections):
    if not os.path.exists(path):
        raise Fatal(f"the changelog {path} does not exist")
    lines, mask, entries = parse_changelog(read_text(path), sections)
    for e in entries:
        judge(e, lines, mask, labels)
    if args.json:
        print(json.dumps([record(e) for e in entries], ensure_ascii=False, indent=2))
    else:
        for e in entries:
            print(f"{e['status']}  {e['date'] or '-'}  {e['tier'] or '-'}  "
                  f"{path}:{e['line']}  {e['heading']}")
    return 0


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"session-metrics: error: {message}", file=sys.stderr)
        sys.exit(2)


def main(argv=None):
    p = Parser(
        prog="session-metrics.py",
        usage=("\n  session-metrics.py --since YYYY-MM-DD [--entry LINE] [--root DIR] "
               "[--changelog FILE] [--deliver FILE]"
               "\n  session-metrics.py --all [--json] [--root DIR] [--changelog FILE] "
               "[--deliver FILE]"
               "\n  session-metrics.py --labels [--root DIR] [--deliver FILE]"),
        description="Read the Session metrics block of delivery entries (SPEC-0006).")
    p.add_argument("--since", help="lint role: judge entries dated on or after YYYY-MM-DD")
    p.add_argument("--entry", type=int, metavar="LINE",
                   help="lint role: judge only the entry whose heading is on LINE")
    p.add_argument("--all", action="store_true", help="query role: every entry")
    p.add_argument("--json", action="store_true", help="with --all: a JSON array")
    p.add_argument("--labels", action="store_true", help="query role: the template's labels")
    p.add_argument("--root", default=None, help="graph root (default docs/graph)")
    p.add_argument("--changelog", help="changelog (default <root>/changelog.md)")
    p.add_argument("--deliver", help="deliver node (default <root>/protocols/deliver.md)")
    args = p.parse_args(argv)

    roles = [r for r, on in (("--since", args.since is not None), ("--all", args.all),
                             ("--labels", args.labels)) if on]
    if not roles:
        p.error("one role is required: --since YYYY-MM-DD (lint), --all or --labels")
    if len(roles) > 1:
        p.error(f"give one role, not {' and '.join(roles)}")
    if args.since is not None:
        ok = re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.since)
        try:
            ok = ok and datetime.date.fromisoformat(args.since)
        except ValueError:
            ok = False
        if not ok:
            p.error(f"--since takes a date YYYY-MM-DD, not {args.since!r}")
    if args.entry is not None and args.since is None:
        p.error("--entry needs --since YYYY-MM-DD")
    if args.json and not args.all:
        p.error("--json goes with --all")

    root = args.root if args.root is not None else os.path.join("docs", "graph")
    needs_root = args.deliver is None or (not args.labels and args.changelog is None)
    try:
        if needs_root and not os.path.isdir(root):
            raise Fatal(f"the graph root {root} does not exist")
        deliver = args.deliver or os.path.join(root, "protocols", "deliver.md")
        labels, sections = parse_deliver(deliver)
        if args.labels:
            for label in labels:
                print(label)
            return 0
        path = args.changelog or os.path.join(root, "changelog.md")
        if args.all:
            return run_all(args, path, labels, sections)
        return run_lint(args, path, labels, sections, args.changelog is None)
    except Fatal as exc:
        print(f"session-metrics: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
