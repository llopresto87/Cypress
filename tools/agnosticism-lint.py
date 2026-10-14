#!/usr/bin/env python3
"""agnosticism-lint: prove a shared component names no single project.

A component meant for ANY project — a seed, a template repository, a
corpus of doctrine — is worth exactly as much as its agnosticism. One
leaked project name, host address, install path, or "this project's X"
example silently narrows it for everyone downstream, and review misses
those far more often than it catches them. This is the mechanical floor
under the human judgement, over any tree, for any component.

Four objective classes:

  forbidden term   a caller-supplied identifier — project, product,
                   company, service, internal component, operator, path,
                   or the stack fingerprint that names one — passed with
                   --forbid (repeatable)
  host-IP literal  a real address; loopback / unspecified / broadcast and
                   the RFC 5737 documentation ranges are allowed, since
                   those are what an example is supposed to use
  pinned advisory  a CVE id; durable components carry surface knowledge,
                   not one release's security bulletin
  home path        an absolute operator home directory — /home/<user>/,
                   /Users/<user>/, /root/<name>, C:\\Users\\<user>\\ — a real
                   filesystem location that names one machine's owner, the
                   same objective class as a host-IP literal; generic
                   documentation placeholders (/home/user/, /home/AGENTS.md,
                   /root/ + ellipsis, C:\\Users\\Public\\) are allowed, the way
                   the documentation IP ranges are

What it cannot do is guess the caller's own identity: a component cannot
enumerate the names it must not contain without containing them. That is
what --forbid is for — the adopting tree passes its own tokens, the way
graft-audit.py takes --tokens. Everything subtler than these four (a
domain noun, a stack combination, an identifying count) stays human
judgement and is not faked here.

Usage:
    agnosticism-lint.py --root <dir> [--root <dir> ...]
                        [--file <path> ...] [--forbid <term> ...]
                        [--forbid-file <list> ...] [--optional-forbid-file <list>]
                        [--glob <pat> ...] [--tracked] [--terms-only]

    --root    directory scanned recursively (repeatable; default: .)
    --file    one file, scanned whatever --glob says (repeatable)
    --forbid  a literal term, matched case-insensitively as a SUBSTRING
              (repeatable) — fail-closed on purpose, so a token also hits
              the compounds built from it
    --forbid-file
              a list of terms, one per line, with its own exemptions
              (`!allow <text>`, `!allow-in <glob> <text>`; see
              read_forbid_file). A steward's list of every project a
              component was harvested from is kept local and out of the
              component, the way the names in it must be
    --optional-forbid-file
              the same list where it may be absent: absent, the run prints
              SKIPPED and exits 0, so a clone without it says what it did
              not check instead of passing
    --glob    filename pattern under each --root (repeatable;
              default: *.md)
    --tracked every file Git tracks under each --root, whatever its suffix,
              in place of the --glob walk: the tree a component ships
    --terms-only
              report forbidden terms alone, for a tree whose fixtures plant
              the other classes on purpose (they have their own gate)

Exit 0 clean (or SKIPPED), 1 with findings, 2 on a usage error —
including a run that matched no file at all, or a forbid list with no
term, which would otherwise print the same clean verdict a real scan earns.

Importable: scan() returns Finding records and iter_files() the file
list, so a host linter reuses the detection and renders it in its own
voice instead of keeping a second copy (tests/seed-lint.py does).
Dependency-free.
"""
import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
CVE_RE = re.compile(r"\bCVE-\d{4}-\d+\b")
# loopback, unspecified, broadcast + the RFC 5737 documentation ranges:
# an address an example is entitled to use is not a leak.
IP_ALLOWED = frozenset({"127.0.0.1", "0.0.0.0", "255.255.255.255"})
IP_ALLOWED_PREFIXES = ("192.0.2.", "198.51.100.", "203.0.113.")

# Absolute operator home paths. A real /home/<user>/, /Users/<user>/,
# /root/<name> or C:\Users\<user>\ names one machine's owner, the same
# objective class as a host-IP literal. The account segment must start with an
# alphanumeric and use real account characters, which (a) keeps a generic
# placeholder like /home/<user>/ and this module's own regex source from
# self-matching, and (b) requires a real name after /root/, so a redacted
# /root/... example is not a leak. A leading boundary keeps a /home/ embedded
# in a URL host (".../home/docweb/") from matching.
HOME_USER_RE = re.compile(
    r"(?<![A-Za-z0-9._-])(?:/home/|/Users/)([A-Za-z0-9][A-Za-z0-9._-]*)/")
HOME_ROOT_RE = re.compile(
    r"(?<![A-Za-z0-9._-])/root/([A-Za-z0-9][A-Za-z0-9._-]*)")
HOME_WIN_RE = re.compile(
    r"(?<![A-Za-z0-9])[Cc]:\\Users\\([A-Za-z0-9][A-Za-z0-9._ -]*)\\")
# The generic account names a placeholder is entitled to use, the way a
# documentation IP is: an example home under one of these is not a leak.
HOME_ALLOWED_USER = frozenset({
    "user", "username", "you", "youruser", "example", "name", "me",
    "public", "default", "someone",
})

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


def _home_paths(line):
    """Every absolute operator home path on `line`, in match order. An account
    segment in HOME_ALLOWED_USER is a generic placeholder and is skipped; a
    /root/<name> is always a real name (the regex already excludes the redacted
    ellipsis form) and is always reported."""
    hits = []
    for rx in (HOME_USER_RE, HOME_WIN_RE):
        for m in rx.finditer(line):
            if m.group(1).lower() not in HOME_ALLOWED_USER:
                hits.append(m.group(0))
    for m in HOME_ROOT_RE.finditer(line):
        hits.append(m.group(0))
    return hits


@dataclass(frozen=True)
class Allow:
    """An exemption a forbid list carries: a forbidden term found inside
    `text` is not a finding, in every file (`glob` empty) or only in a file
    whose path matches `glob` from the right (`other/*.md`)."""
    text: str
    glob: str = ""


def read_forbid_file(path):
    """(terms, allows) from a forbid list: one literal term per non-blank
    line, a line starting with `#` included (a colour, a channel name is a
    term, so the list has no comment syntax). Two directives, each on its own
    line, carry the list's exemptions:

      !allow <text>              a term inside <text> is exempt everywhere
      !allow-in <glob> <text>    the same, only in files <glob> matches

    The exemptions live in the list, beside the terms they qualify, and never
    in this tool: the owner's own name or a component's repository URL is
    exempted by the steward who keeps the list."""
    terms, allows = [], []
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("!allow-in "):
            parts = line.split(None, 2)
            if len(parts) == 3:
                allows.append(Allow(parts[2], parts[1]))
                continue
        elif line.startswith("!allow "):
            allows.append(Allow(line.split(None, 1)[1]))
            continue
        terms.append(line)
    return terms, allows


def _exempt(line, start, end, path, allows):
    """True when the hit line[start:end] lies inside an allowed text that
    applies to `path`."""
    low = line.lower()
    for a in allows:
        if a.glob and not PurePosixPath(path).match(a.glob):
            continue
        t = a.text.lower()
        i = low.find(t)
        while i >= 0:
            if i <= start and end <= i + len(t):
                return True
            i = low.find(t, i + 1)
    return False


def tracked_files(roots):
    """The files each root's Git repository tracks under it: what the
    component ships, whatever the suffix, and nothing untracked or ignored."""
    out = []
    for r in roots:
        res = subprocess.run(["git", "-C", str(r), "ls-files", "-z", "--", "."],
                             capture_output=True, text=True)
        if res.returncode != 0:
            raise OSError(f"{r}: not a Git working tree ({res.stderr.strip()})")
        out += [Path(r) / p for p in res.stdout.split("\0") if p]
    return [p for p in out if p.is_file() and not p.is_symlink()]


def scan(paths, forbid=(), globs=DEFAULT_GLOBS, relative_to=None, allows=()):
    """Every finding over `paths`, in file order then line order, with the
    three classes applied in a fixed order per line. `relative_to` trims
    the reported path to a root the caller reports against; `allows` are a
    forbid list's exemptions (read_forbid_file)."""
    words = [t for t in (s.strip() for s in forbid) if t]
    terms = [(t.casefold(), re.compile(re.escape(t), re.I)) for t in words]
    findings: list[Finding] = []
    for f in iter_files(paths, globs):
        rel_for_error = (f.relative_to(relative_to).as_posix()
                         if relative_to else f.as_posix())
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError) as exc:
            # NOT a silent skip. The comment here used to read "binary or
            # unreadable: carries no prose", but DEFAULT_GLOBS is ("*.md",) —
            # a markdown file that will not decode is a prose file this tool
            # could not read, which is the one thing it must never report as
            # clean. An unread input is UNKNOWN, and unknown is not green.
            findings.append(Finding(
                rel_for_error, 0, "unreadable", "",
                f"could not be read, so it was NOT scanned: {exc}"))
            continue
        rel = (f.relative_to(relative_to).as_posix()
               if relative_to else f.as_posix())
        # A list of hundreds of terms is narrowed per file first: only the
        # terms the file holds at all are searched for line by line.
        folded = text.casefold()
        present = [rx for low, rx in terms if low in folded]
        for n, line in enumerate(text.splitlines(), 1):
            for rx in present:
                for m in rx.finditer(line):
                    if allows and _exempt(line, m.start(), m.end(), rel, allows):
                        continue
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
            for hit in _home_paths(line):
                findings.append(Finding(
                    rel, n, "home-path", hit,
                    f"absolute operator home path '{hit}' — agnosticism gate "
                    f"(use a <home> placeholder, not a real operator location)"))
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
    ap.add_argument("--forbid-file", action="append", metavar="PATH", default=[],
                    help="a forbid list: one term per line, with its "
                         "!allow / !allow-in exemptions (repeatable)")
    ap.add_argument("--optional-forbid-file", metavar="PATH",
                    help="a forbid list that may be absent: absent, the run "
                         "prints SKIPPED and exits 0")
    ap.add_argument("--tracked", action="store_true",
                    help="scan every file Git tracks under each --root, "
                         "whatever its suffix, instead of --glob matches")
    ap.add_argument("--terms-only", action="store_true",
                    help="report only forbidden terms (and unreadable files): "
                         "for a tree whose test fixtures plant the other "
                         "classes on purpose")
    args = ap.parse_args()

    lists = list(args.forbid_file)
    if args.optional_forbid_file:
        if not Path(args.optional_forbid_file).is_file():
            print(f"agnosticism lint: SKIPPED — no local forbid list at "
                  f"{args.optional_forbid_file}; nothing was checked against "
                  f"the steward's terms")
            return 0
        lists.append(args.optional_forbid_file)
    terms, allows = list(args.forbid), []
    for f in lists:
        try:
            t, a = read_forbid_file(f)
        except (OSError, UnicodeDecodeError) as exc:
            print(f"  !! cannot read the forbid list {f}: {exc}")
            return 2
        if not t:
            print(f"  !! the forbid list {f} holds no term — refusing a vacuous pass")
            return 2
        terms += t
        allows += a

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

    relative_to = None
    if args.tracked:
        try:
            files = iter_files(tracked_files(roots) + [Path(p) for p in args.file])
        except OSError as exc:
            print(f"  !! {exc}")
            return 2
        if len(roots) == 1:
            relative_to = Path(roots[0])
    else:
        files = iter_files([Path(p) for p in named], globs)
    # A scan over an empty set is a green lie: a mistyped --glob would
    # otherwise print the same PASS a real scan earns.
    if not files:
        print(f"  !! matched 0 files ({'tracked' if args.tracked else ' '.join(globs)} "
              f"under {', '.join(named)}) — refusing a vacuous pass")
        return 2

    findings = scan(files, forbid=terms, relative_to=relative_to, allows=allows)
    if args.terms_only:
        findings = [f for f in findings if f.rule in ("forbidden-term", "unreadable")]
    if findings:
        print(f"agnosticism lint: FAIL ({len(findings)} finding(s))")
        for f in findings:
            print(f"  - {f.path}:{f.line}: {f.message}")
        return 1
    print(f"agnosticism lint: PASS — {len(files)} file(s) scanned, "
          f"{len(terms)} forbidden term(s), {len(allows)} exemption(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
