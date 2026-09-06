#!/usr/bin/env python3
"""status-migrate.py — move a plant's lifecycle status from body prose into
frontmatter, in the schema's one vocabulary.

Before 7.0.0 every artifact kind carried its status as prose in a different
place with a different vocabulary: an ADR's `## Status` line, a spec's
`- **Status:**` bullet, a threat model's metadata row. None was machine-
readable, so nothing could answer "what is still open?" and two copies of the
same status drifted apart. This tool performs the one-time migration an
adopted or pre-7.0.0 plant needs: it reads the old value, maps it onto the
lifecycle vocabulary (schema §"Lifecycle status"), writes `status:`,
`status_date:` and the companion keys into frontmatter, and turns the body
line into a pointer — one home.

    python3 status-migrate.py --root docs/graph            # dry run: table only
    python3 status-migrate.py --root docs/graph --write    # apply
    python3 status-migrate.py --root docs/graph --write --kind adr --kind spec

Mappings (old → new). Where the old vocabulary carries a fact the new one needs
and the artifact does not state it, the companion is written as
`not recorded — <why>` rather than invented; the lint accepts a non-empty
value and a human sees exactly what is owed.

  adr     proposed → proposed · accepted → accepted ·
          "superseded by ADR-NNNN" → superseded + superseded_by: ADR-NNNN ·
          deprecated → superseded + superseded_by: "not recorded — deprecated without a named successor"
  spec    draft/active/implemented/back-written → same ·
          superseded → superseded + superseded_by from the "Superseded by:" bullet, else "not recorded"

Threat models, data contracts and prompt contracts are REPORTED, not migrated:
their old `active` means "in force", which is not a lifecycle-debt state, and
choosing its new home is an owner decision (see the report line). Use
`--map <kind>:<old>=<new>` to apply a chosen mapping once decided.

Exit 0 when nothing needs migrating (or after a successful --write), 1 when
the dry run found work, 2 on usage error. Dependency-free.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import re
import sys
from pathlib import Path

KIND_DIRS = {"decisions": "adr", "specs": "spec"}
REPORT_ONLY_DIRS = {"prompts": "prompt-contract", "data": "data-contract"}
DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
ADR_STATUS_LINE = re.compile(r"^##\s+Status\s*\n+\s*`?([^`\n]+?)`?\s*$", re.M)
BULLET_STATUS = re.compile(r"^-\s+\*\*Status:\*\*\s*(.+?)\s*$", re.M)
BULLET_SUPERSEDED_BY = re.compile(r"^-\s+\*\*Superseded by:\*\*\s*(.+?)\s*$", re.M)
BULLET_OWNER = re.compile(r"^-\s+\*\*Owner:\*\*\s*(.+?)\s*$", re.M)
BULLET_DATE = re.compile(r"^-\s+\*\*Date:\*\*\s*(.+?)\s*$", re.M)
ADR_DATE_SECTION = re.compile(r"^##\s+Date\s*\n+\s*(\S+)", re.M)
SUPERSEDED_BY_RE = re.compile(r"superseded\s+by\s+([A-Za-z]+-\d+)", re.I)
POINTER = "See frontmatter — the single home. Do not restate the value here."
NOT_RECORDED_DEPRECATED = "not recorded — deprecated without a named successor"
NOT_RECORDED = "not recorded"


def has_frontmatter(text: str) -> bool:
    return text.startswith("---\n") and "\n---\n" in text[4:]


def frontmatter_has_status(text: str) -> bool:
    if not has_frontmatter(text):
        return False
    end = text.find("\n---\n", 4)
    return re.search(r"^status:\s*\S", text[4:end], re.M) is not None


def detect(kind: str, text: str):
    """Return (old_status_raw, superseded_by, owner, date) or None."""
    if kind == "adr":
        m = ADR_STATUS_LINE.search(text)
        if not m:
            return None
        raw = m.group(1).strip()
        d = ADR_DATE_SECTION.search(text)
        date = d.group(1) if d and DATE_RE.fullmatch(d.group(1)) else None
        return raw, None, None, date
    m = BULLET_STATUS.search(text)
    if not m:
        return None
    raw = m.group(1).strip()
    sb = BULLET_SUPERSEDED_BY.search(text)
    ow = BULLET_OWNER.search(text)
    dt = BULLET_DATE.search(text)
    sb_v = sb.group(1).strip() if sb else None
    if sb_v and (sb_v.startswith("<") or sb_v.lower().startswith("n/a")):
        sb_v = None
    ow_v = ow.group(1).strip() if ow else None
    if ow_v and ow_v.startswith("<"):
        ow_v = None
    date = dt.group(1).strip() if dt and DATE_RE.fullmatch(dt.group(1).strip()) else None
    return raw, sb_v, ow_v, date


ANNOTATED = re.compile(r"^\s*`?\*{0,2}([A-Za-z][A-Za-z-]*)\*{0,2}`?\s*(?:\((.*)\)|—\s*(.*)|-\s+(.*))?\s*$", re.S)


def split_annotation(raw: str):
    """A status written as `active (INC-0..7 implemented, promotes when …)` or
    `ACCEPTED — implemented 2026-07-13 …` is a status plus a note. Return
    (status_token, note_or_None). The note is carried into frontmatter as
    `status_note:` so nothing the author wrote is dropped — only relocated."""
    m = ANNOTATED.match(raw)
    if not m:
        return raw, None
    token = m.group(1)
    note = next((g for g in m.groups()[1:] if g), None)
    if note:
        note = " ".join(note.split())
    return token, note


def map_status(kind: str, raw: str, superseded_by, overrides: dict):
    """Return (new_status, companions: dict) or (None, reason)."""
    token, note = split_annotation(raw)
    if note and token.lower() not in ("superseded",):
        raw = token          # map on the token; the note rides along separately
    low = raw.lower().strip("`* ")
    key = f"{kind}:{low}"
    if key in overrides:
        return overrides[key], {}
    if kind == "adr":
        if low in ("proposed", "accepted"):
            return low, {}
        m = SUPERSEDED_BY_RE.search(raw)
        if m:
            return "superseded", {"superseded_by": m.group(1)}
        if low.startswith("superseded"):
            return "superseded", {"superseded_by": NOT_RECORDED}
        if low == "deprecated":
            return "superseded", {"superseded_by": NOT_RECORDED_DEPRECATED}
        return None, f"unknown ADR status {raw!r}"
    if kind == "spec":
        if low in ("draft", "active", "implemented", "back-written"):
            return low, {}
        if low.startswith("superseded"):
            m = SUPERSEDED_BY_RE.search(raw)
            return "superseded", {"superseded_by": (m.group(1) if m else (superseded_by or NOT_RECORDED))}
        return None, f"unknown spec status {raw!r}"
    return None, f"{kind}: '{raw}' needs an owner decision (use --map {kind}:{low}=<new>)"


def rewrite(kind: str, text: str, new_status: str, companions: dict, owner, date: str) -> str:
    lines = [f"status: {new_status}", f"status_date: {date}"]
    if owner:
        lines.append(f"owner: {owner}")
    for k, v in companions.items():
        lines.append(f"{k}: {v}")
    block = "---\n" + "\n".join(lines) + "\n---\n\n"
    if has_frontmatter(text):
        end = text.find("\n---\n", 4)
        head, rest = text[4:end], text[end + 5:]
        text = "---\n" + head.rstrip("\n") + "\n" + "\n".join(lines) + "\n---\n" + rest
    else:
        text = block + text
    if kind == "adr":
        text = ADR_STATUS_LINE.sub("## Status\n\n" + POINTER, text, count=1)
    else:
        text = BULLET_STATUS.sub("- **Status:** see frontmatter (single home)", text, count=1)
    return text


def iter_targets(root: Path, kinds: set):
    for d, kind in sorted(KIND_DIRS.items()):
        if kind not in kinds:
            continue
        p = root / d
        if not p.is_dir():
            continue
        for f in sorted(p.glob("*.md")):
            if f.name.lower() in ("readme.md", "index.md") or f.name.startswith("_"):
                continue
            yield kind, f
    for d, kind in sorted(REPORT_ONLY_DIRS.items()):
        p = root / d
        if p.is_dir():
            for f in sorted(p.rglob("*.md")):
                if f.name.lower() in ("readme.md", "index.md"):
                    continue
                yield kind, f
    p = root / "decisions"
    if p.is_dir():
        for f in sorted(p.glob("threat-model-*.md")):
            yield "threat-model", f


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default="docs/graph", metavar="DIR")
    ap.add_argument("--write", action="store_true", help="apply (default: dry run)")
    ap.add_argument("--kind", action="append", choices=sorted(set(KIND_DIRS.values())), help="restrict (repeatable)")
    ap.add_argument("--map", action="append", default=[], metavar="KIND:OLD=NEW",
                    help="override or supply a mapping, e.g. --map threat-model:active=open")
    ap.add_argument("--today", default=_dt.date.today().isoformat(), help=argparse.SUPPRESS)
    args = ap.parse_args()
    root = Path(args.root)
    if not root.is_dir():
        print(f"  !! no such directory: {root}")
        return 2
    kinds = set(args.kind or KIND_DIRS.values())
    overrides = {}
    for m in args.map:
        try:
            k, rest = m.split(":", 1)
            old, new = rest.split("=", 1)
            overrides[f"{k}:{old.lower()}"] = new
        except ValueError:
            print(f"  !! bad --map {m!r} (want KIND:OLD=NEW)")
            return 2

    migrated, skipped, decisions, already = [], [], [], 0
    for kind, f in iter_targets(root, kinds):
        text = f.read_text(encoding="utf-8")
        if frontmatter_has_status(text):
            already += 1
            continue
        det = detect(kind if kind in ("adr", "spec") else "spec", text)
        if det is None:
            skipped.append((kind, f, "no status line found"))
            continue
        raw, sb, owner, date = det
        if raw.startswith("<") or "|" in raw:
            skipped.append((kind, f, f"template placeholder {raw!r}"))
            continue
        new, comp = map_status(kind, raw, sb, overrides)
        if new is None:
            decisions.append((kind, f, comp))
            continue
        _, note = split_annotation(raw)
        if note:
            comp = dict(comp, status_note=note.replace(":", " -"))
        migrated.append((kind, f, raw, new, comp, owner, date or args.today))

    rel = lambda p: p.relative_to(root).as_posix()
    if migrated:
        print(f"{'kind':14} {'old':34} {'new':12} {'companions':40} file")
        for kind, f, raw, new, comp, owner, date in migrated:
            c = ", ".join(f"{k}={v}" for k, v in comp.items()) or "-"
            print(f"{kind:14} {raw[:34]:34} {new:12} {c[:40]:40} {rel(f)}")
    for kind, f, why in decisions:
        print(f"  ? {rel(f)}: {why}")
    for kind, f, why in skipped:
        print(f"  - {rel(f)}: skipped — {why}")
    print(f"\nstatus-migrate: {len(migrated)} to migrate, {already} already in frontmatter, "
          f"{len(decisions)} need a decision, {len(skipped)} skipped")

    if not args.write:
        return 1 if migrated else 0
    for kind, f, raw, new, comp, owner, date in migrated:
        f.write_text(rewrite(kind, f.read_text(encoding="utf-8"), new, comp, owner, date), encoding="utf-8")
    print(f"status-migrate: wrote {len(migrated)} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
