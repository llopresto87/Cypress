#!/usr/bin/env python3
"""agnosticism-lint: prove a shared component names no single project.

A component meant for ANY project — a seed, a template repository, a
corpus of doctrine — is worth exactly as much as its agnosticism. One
leaked project name, host address, install path, or "this project's X"
example silently narrows it for everyone downstream, and review misses
those far more often than it catches them. This is the mechanical floor
under the human judgement, over any tree, for any component.

Three objective classes:

  forbidden term   a caller-supplied identifier — project, product,
                   company, service, internal component, operator, path,
                   or the stack fingerprint that names one — passed with
                   --forbid (repeatable)
  host-IP literal  a real address; loopback / unspecified / broadcast and
                   the RFC 5737 documentation ranges are allowed, since
                   those are what an example is supposed to use
  pinned advisory  a CVE id; durable components carry surface knowledge,
                   not one release's security bulletin

What it cannot do is guess the caller's own identity: a component cannot
enumerate the names it must not contain without containing them. That is
what --forbid is for — the adopting tree passes its own tokens, the way
graft-audit.py takes --tokens. Everything subtler than these three (a
domain noun, a stack combination, an identifying count) stays human
judgement and is not faked here.

Usage:
    agnosticism-lint.py --root <dir> [--root <dir> ...]
                        [--file <path> ...] [--forbid <term> ...]
                        [--glob <pat> ...]

    --root    directory scanned recursively (repeatable; default: .)
    --file    one file, scanned whatever --glob says (repeatable)
    --forbid  a literal term, matched case-insensitively as a SUBSTRING
              (repeatable) — fail-closed on purpose, so a token also hits
              the compounds built from it
    --glob    filename pattern under each --root (repeatable;
              default: *.md)

Exit 0 clean, 1 with findings, 2 on a usage error — including a run that
matched no file at all, which would otherwise print the same clean
verdict a real scan earns.

Importable: scan() returns Finding records and iter_files() the file
list, so a host linter reuses the detection and renders it in its own
voice instead of keeping a second copy (tests/seed-lint.py does).
Dependency-free.
"""
import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
CVE_RE = re.compile(r"\bCVE-\d{4}-\d+\b")
# loopback, unspecified, broadcast + the RFC 5737 documentation ranges:
# an address an example is entitled to use is not a leak.
IP_ALLOWED = frozenset({"127.0.0.1", "0.0.0.0", "255.255.255.255"})
IP_ALLOWED_PREFIXES = ("192.0.2.", "198.51.100.", "203.0.113.")

DEFAULT_GLOBS = ("*.md",)


@dataclass(frozen=True)
class Finding:
    """One violation. `message` carries no path prefix so each caller can
    render it its own way — the CLI as `path:line: message`, a host
    linter in whatever form its own findings already take."""
    path: str
    line: int
    rule: str
    term: str
    message: str


def iter_files(paths, globs=DEFAULT_GLOBS):
    """The files to scan: a directory contributes its matches for every
    glob, a file contributes itself. Sorted per root and de-duplicated by
    real path, so a run is reproducible and an overlapping --root/--file
    pair is scanned once."""
    seen: dict = {}
    for p in paths:
        p = Path(p)
        if p.is_dir():
            for g in globs:
                for f in sorted(p.rglob(g)):
                    if f.is_file():
                        seen.setdefault(f.resolve(), f)
        elif p.is_file():
            seen.setdefault(p.resolve(), p)
    return list(seen.values())


def scan(paths, forbid=(), globs=DEFAULT_GLOBS, relative_to=None):
    """Every finding over `paths`, in file order then line order, with the
    three classes applied in a fixed order per line. `relative_to` trims
    the reported path to a root the caller reports against."""
    terms = [re.compile(re.escape(t), re.I)
             for t in (s.strip() for s in forbid) if t]
    findings: list[Finding] = []
    for f in iter_files(paths, globs):
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue          # binary or unreadable: carries no prose
        rel = (f.relative_to(relative_to).as_posix()
               if relative_to else f.as_posix())
        for n, line in enumerate(text.splitlines(), 1):
            for rx in terms:
                for m in rx.finditer(line):
                    findings.append(Finding(
                        rel, n, "forbidden-term", m.group(0),
                        f"project-identifying term '{m.group(0)}' — "
                        f"agnosticism gate (a shared component names no "
                        f"project, path, or operator)"))
            for m in IP_RE.finditer(line):
                ip = m.group(0)
                if ip in IP_ALLOWED or ip.startswith(IP_ALLOWED_PREFIXES):
                    continue
                findings.append(Finding(
                    rel, n, "host-ip", ip,
                    f"leaked host-IP literal '{ip}' — agnosticism gate "
                    f"(use a <host> placeholder, not a real address)"))
            for m in CVE_RE.finditer(line):
                findings.append(Finding(
                    rel, n, "advisory", m.group(0),
                    f"pinned advisory '{m.group(0)}' — durability gate "
                    f"(belongs in a plant's docs, never the seed)"))
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", action="append", metavar="DIR",
                    help="directory to scan recursively "
                         "(repeatable; default: .)")
    ap.add_argument("--file", action="append", metavar="PATH", default=[],
                    help="one file to scan whatever --glob says (repeatable)")
    ap.add_argument("--forbid", action="append", metavar="TERM", default=[],
                    help="project-identifying term, matched "
                         "case-insensitively as a substring (repeatable)")
    ap.add_argument("--glob", action="append", metavar="PAT",
                    help="filename pattern under each --root "
                         "(repeatable; default: *.md)")
    args = ap.parse_args()

    # "." is the default only when the caller named nothing at all. A bare
    # --file must scan that file and nothing else: silently widening a scan
    # to the whole tree is the surprising direction for a gate to fail in.
    roots = args.root or ([] if args.file else ["."])
    globs = tuple(args.glob or DEFAULT_GLOBS)
    named = roots + args.file
    missing = [p for p in named if not Path(p).exists()]
    if missing:
        for p in missing:
            print(f"  !! no such path: {p}")
        return 2

    files = iter_files([Path(p) for p in named], globs)
    # A scan over an empty set is a green lie: a mistyped --glob would
    # otherwise print the same PASS a real scan earns.
    if not files:
        print(f"  !! matched 0 files ({' '.join(globs)} under "
              f"{', '.join(named)}) — refusing a vacuous pass")
        return 2

    findings = scan(files, forbid=args.forbid)
    if findings:
        print(f"agnosticism lint: FAIL ({len(findings)} finding(s))")
        for f in findings:
            print(f"  - {f.path}:{f.line}: {f.message}")
        return 1
    print(f"agnosticism lint: PASS — {len(files)} file(s) scanned, "
          f"{len(args.forbid)} forbidden term(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
