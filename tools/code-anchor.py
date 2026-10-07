#!/usr/bin/env python3
"""code-anchor.py: what the code looked like when the graph last matched it.

The graph states facts about code, and code moves under it: a commit, a branch
checkout, uncommitted work. This tool marks the state of the code at canonize,
the moment the graph was last reconciled against it, and says once per session
start whether any code moved since. Paths under `docs/graph/` and `.cypress/`
are the graph and its state, not code, and never count; nor do build and backup
files (`__pycache__/`, `*.pyc`, `*.bak`, `*.bak-*`), which no fact describes
(SPEC-0003, "Code anchor").

Placed in a plant as `docs/graph/code-anchor.py` and run from the plant root:

    python3 docs/graph/code-anchor.py --record          # canonize: write the anchor
    python3 docs/graph/code-anchor.py --compare         # session start: one short report
    python3 docs/graph/code-anchor.py --compare --all   # every moved path, no budget

Governed repositories are the plant root, when it is a Git work tree, plus each
distinct `repo:` value in node frontmatter under `docs/graph/` that resolves,
inside the plant root, to a directory holding `.git`. Those rules, the code-path
rule, the Git boundary, the content hash and the atomic write are the seed's
path rules, held by `source_paths.py` beside this file, which reads node
frontmatter through `frontmatter.py` beside it (the installer places all three
in `docs/graph/`). `--record` finds them and stores, per repository, the
branch, the commit and each uncommitted code path with its Git blob hash in
`.cypress/anchor.json`. `--compare` reads the list from the anchor and names
the paths that moved: changed between the recorded commit and HEAD, uncommitted
now and not at the anchor, or holding content other than the recorded hash. A
path whose content equals its recorded hash has not moved.

Every doubt resolves toward checking the code. `--compare` always exits 0: an
anchor that is missing, unreadable or of another version, or no `git` on
PATH, gives the not-recorded line; a recorded commit this clone lacks makes
that repository's line say its code facts are unverified. It writes nothing:
Git runs with optional locks off, so not even the index is refreshed.

`--record` writes the anchor the way the session ledger is written: relative
to a descriptor on `.cypress/`, never through a symlink, into an exclusive
temp file that replaces the anchor atomically. It never creates `.cypress/`.
Any refusal is one stderr line and exit 1, with the old anchor untouched.
"""

import argparse
import json
import os
import re
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path
import importlib.util as _ilu
_sp_spec = _ilu.spec_from_file_location(
    "cypress_source_paths", Path(__file__).resolve().parent / "source_paths.py")
source_paths = _ilu.module_from_spec(_sp_spec)
_sp_spec.loader.exec_module(source_paths)

# --- constants and texts (SPEC-0003 §6): this file is their one home. ---
# ANCHOR_TIMEOUT and the not-checked line are the callers': the hooks print
# that line when this tool is absent, fails or runs past their wait.
ANCHOR_VERSION = 1
ANCHOR_QUIET_MAX_BYTES = 160
ANCHOR_MAX_PATHS = 20
ANCHOR_MAX_BYTES = 2048
ANCHOR_DIRTY_MAX = 256

QUIET = ("Code anchor: no code changed since the last canonize (repositories: {n}). "
         "The graph's facts about code are current.")
MOVED_HEADER = ("Code anchor: code changed since the last canonize. Facts about the paths "
                "below may be stale; check them against the code. Every other fact stands "
                "as the graph states it.")
REPO_LINE = "- {repo}: {label}"
MORE_PATHS = "- and {k} more path(s): python3 docs/graph/code-anchor.py --compare --all"
NOT_RECORDED = ("Code anchor: not recorded ({reason}). Facts about code in the graph are "
                "unverified until the next canonize records one; settled facts stay settled.")
RECORD_LINE = "Code anchor recorded {at}: {repos}"
RECORD_REPO = "{repo} {branch}@{sha7} ({k} uncommitted)"

ANCHOR_DIR, ANCHOR_NAME = ".cypress", "anchor.json"
ANCHOR_KEYS = {"version", "recorded_at", "repositories"}
REPO_KEYS = {"path", "branch", "commit", "dirty", "dirty_overflow"}
DETACHED = "(detached)"
TEMP_PREFIX = ".tmp-anchor-"
SHA1 = re.compile(r"^[0-9a-f]{40}$")
ISO_UTC = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?(Z|\+00:00)$")

ROOT = Path.cwd()


class Unrecorded(Exception):
    """No usable anchor, or no Git to compare with. The message is the reason
    the not-recorded line carries."""


# --- Git reads of the anchored state -----------------------------------------
def head_state(repo: Path):
    """(branch or None when detached, commit) of the work tree at `repo`."""
    commit = source_paths.git(repo, "rev-parse", "--verify", "HEAD^{commit}").decode().strip()
    if not SHA1.match(commit):
        raise source_paths.GitFailed("HEAD is not a SHA-1 commit")
    try:
        branch = (source_paths.git(repo, "symbolic-ref", "-q", "--short", "HEAD")
                  .decode().strip() or None)
    except source_paths.GitFailed:
        branch = None
    return branch, commit


def uncommitted(repo: Path) -> list:
    """Every path `git status` shows as changed or untracked, relative to the
    repository, ignored files left out."""
    out = source_paths.git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all",
                           "--no-renames")
    return [e[3:].decode("utf-8", "surrogateescape") for e in out.split(b"\0") if len(e) > 3]


def changed_between(repo: Path, old: str, new: str) -> list:
    out = source_paths.git(repo, "diff-tree", "-r", "-z", "--name-only", "--no-renames", old, new)
    return [p.decode("utf-8", "surrogateescape") for p in out.split(b"\0") if p]


def reachable(repo: Path, commit: str) -> bool:
    try:
        source_paths.git(repo, "cat-file", "-e", commit + "^{commit}")
    except source_paths.GitFailed:
        return False
    return True


# --- the anchor file ---------------------------------------------------------
def anchor_problem(doc):
    """Why `doc` is not a version-1 anchor, or None."""
    if not isinstance(doc, dict):
        return "not an anchor object"
    if type(doc.get("version")) is not int or doc["version"] != ANCHOR_VERSION:
        return "unknown version"
    if set(doc) != ANCHOR_KEYS:
        return "not an anchor object"
    if not isinstance(doc["recorded_at"], str) or not ISO_UTC.match(doc["recorded_at"]):
        return "bad recorded_at"
    repos = doc["repositories"]
    if not isinstance(repos, list):
        return "bad repositories"
    seen = set()
    for e in repos:
        if not isinstance(e, dict) or set(e) != REPO_KEYS:
            return "bad repository entry"
        if not source_paths.relative(e["path"]) or e["path"] in seen:
            return "bad repository path"
        seen.add(e["path"])
        if not (e["branch"] is None or isinstance(e["branch"], str)):
            return "bad branch"
        if not isinstance(e["commit"], str) or not SHA1.match(e["commit"]):
            return "bad commit"
        dirty = e["dirty"]
        if not isinstance(dirty, dict) or not all(
                source_paths.relative(k) and isinstance(v, str)
                and (v == source_paths.DELETED or SHA1.match(v))
                for k, v in dirty.items()):
            return "bad dirty"
        if type(e["dirty_overflow"]) is not bool:
            return "bad dirty_overflow"
    return None


def read_anchor() -> dict:
    """The recorded anchor, or Unrecorded naming why there is none to use."""
    try:
        dir_fd = source_paths.open_dir(ROOT, ANCHOR_DIR)
    except FileNotFoundError:
        raise Unrecorded(f"no {ANCHOR_DIR}/ directory") from None
    except OSError as e:
        raise Unrecorded(f"{ANCHOR_DIR}/ is unusable, {e.strerror or type(e).__name__}") from None
    try:
        fd = os.open(ANCHOR_NAME, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=dir_fd)
    except FileNotFoundError:
        raise Unrecorded(f"no {ANCHOR_DIR}/{ANCHOR_NAME}") from None
    except OSError as e:
        raise Unrecorded(f"the anchor file is unusable, {e.strerror or type(e).__name__}") from None
    finally:
        os.close(dir_fd)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise Unrecorded("the anchor file is not a regular file")
        with os.fdopen(fd, "rb", closefd=False) as f:
            raw = f.read()
    finally:
        os.close(fd)
    try:
        doc = json.loads(raw)
    except (ValueError, RecursionError):
        raise Unrecorded("the anchor file is not JSON") from None
    problem = anchor_problem(doc)
    if problem == "unknown version":
        raise Unrecorded(f"unknown anchor version {str(doc.get('version'))[:20]}")
    if problem:
        raise Unrecorded(f"the anchor file breaks the version-1 shape, {problem}")
    return doc


# --- record ------------------------------------------------------------------
def snapshot(root: Path, rel: str):
    """One repository's anchor entry, and how many uncommitted code paths it
    has: branch, commit, and each such path with its content (at most
    ANCHOR_DIRTY_MAX, else dirty_overflow and none). A path that cannot be
    hashed is left out, so a compare counts it moved."""
    repo = root / rel
    branch, commit = head_state(repo)
    paths = [p for p in uncommitted(repo) if source_paths.is_code(rel, p)]
    overflow = len(paths) > ANCHOR_DIRTY_MAX
    states = {} if overflow else {p: source_paths.content_state(repo, p) for p in sorted(paths)}
    dirty = {p: s for p, s in states.items() if s is not None}
    return {"path": rel, "branch": branch, "commit": commit, "dirty": dirty,
            "dirty_overflow": overflow}, len(paths)


def record() -> int:
    try:
        dir_fd = source_paths.open_dir(ROOT, ANCHOR_DIR)
    except FileNotFoundError:
        raise source_paths.Refused(f"{ANCHOR_DIR}/ is missing, and this tool never creates "
                                   f"it; nothing written") from None
    except OSError as e:
        raise source_paths.Refused(f"{ANCHOR_DIR}/ is unusable "
                                   f"({e.strerror or type(e).__name__}); nothing written") from None
    try:
        repos = source_paths.governed_repositories(ROOT)
        if not repos:
            raise source_paths.Refused("no governed Git repository (the plant root is not a "
                                       "work tree and no repo: resolves to one); nothing written")
        snaps = []
        for rel in repos:
            try:
                snaps.append(snapshot(ROOT, rel))
            except source_paths.GitMissing:
                raise source_paths.Refused("git is not on PATH; nothing written") from None
            except source_paths.GitFailed as e:
                raise source_paths.Refused(f"{rel}: {e}; nothing written") from None
        entries = [entry for entry, _ in snaps]
        at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        doc = {"version": ANCHOR_VERSION, "recorded_at": at, "repositories": entries}
        try:
            source_paths.atomic_write(dir_fd, ANCHOR_NAME,
                                      (json.dumps(doc, indent=2) + "\n").encode(),
                                      TEMP_PREFIX, f"{ANCHOR_DIR}/{ANCHOR_NAME}")
        except OSError as e:
            raise source_paths.Refused(f"{ANCHOR_DIR}/{ANCHOR_NAME} not written "
                                       f"({e.strerror or type(e).__name__}); "
                                       f"the old anchor stands") from None
    finally:
        os.close(dir_fd)
    print(RECORD_LINE.format(at=at, repos="; ".join(
        RECORD_REPO.format(repo=e["path"], branch=e["branch"] or DETACHED,
                           sha7=e["commit"][:7], k=k)
        for e, k in snaps)))
    return 0


# --- compare -----------------------------------------------------------------
def moved(root: Path, entry: dict):
    """The report lines of one recorded repository: (label, paths) pairs, the
    committed paths first, then the uncommitted ones; a repository whose
    recorded state cannot be checked gives one `unverified` label."""
    rel = entry["path"]
    repo = root / rel
    if not (repo.is_dir() and (repo / ".git").exists()):
        return [("unverified (no Git work tree here now)", [])]
    try:
        if not reachable(repo, entry["commit"]):
            return [(f"unverified (commit {entry['commit'][:7]} is not in this clone)", [])]
        branch, commit = head_state(repo)
        committed = set(changed_between(repo, entry["commit"], commit))
        now = set(uncommitted(repo))
    except source_paths.GitFailed as e:
        return [(f"unverified ({e})", [])]
    recorded = {} if entry["dirty_overflow"] else entry["dirty"]
    hits = {p for p in committed | now | set(recorded) if source_paths.is_code(rel, p)
            and (p not in recorded or source_paths.content_state(repo, p) != recorded[p])}
    in_commits = sorted(p for p in hits if p in committed and p not in now)
    rest = sorted(hits.difference(in_commits))
    lines = []
    if in_commits:
        if branch != entry["branch"]:
            label = f"branch {entry['branch'] or DETACHED} -> {branch or DETACHED}"
        else:
            label = f"commit {entry['commit'][:7]}..{commit[:7]}"
        lines.append((label, in_commits))
    if rest:
        lines.append(("uncommitted", rest))
    return lines


def report(lines: list, everything: bool) -> list:
    """The moved header and the repository lines. Unless `everything`, at most
    ANCHOR_MAX_PATHS paths are named and the whole output stays within
    ANCHOR_MAX_BYTES; the rest is counted on the more-paths line."""
    total = sum(len(paths) for _, _, paths in lines)
    budget = ANCHOR_MAX_BYTES - len(MORE_PATHS.format(k=total).encode()) - 1
    out = [MOVED_HEADER]
    used = len(MOVED_HEADER.encode()) + 1
    shown = 0
    for repo, label, paths in lines:
        line = REPO_LINE.format(repo=repo, label=label)
        taken = []
        for p in paths:
            longer = line + (", " if taken else ": ") + p
            if not everything and (shown >= ANCHOR_MAX_PATHS
                                   or used + len(longer.encode()) + 1 > budget):
                continue
            line, shown = longer, shown + 1
            taken.append(p)
        if taken or not paths:
            if not everything and used + len(line.encode()) + 1 > budget:
                continue
            out.append(line)
            used += len(line.encode()) + 1
    hidden = total - shown
    if hidden:
        out.append(MORE_PATHS.format(k=hidden))
    return out


def compare(everything: bool) -> int:
    try:
        doc = read_anchor()
        lines = []
        for entry in doc["repositories"]:
            lines.extend((entry["path"], label, paths) for label, paths in moved(ROOT, entry))
    except source_paths.GitMissing:
        print(NOT_RECORDED.format(reason="git is not on PATH, so nothing can be compared"))
        return 0
    except Unrecorded as e:
        print(NOT_RECORDED.format(reason=e))
        return 0
    if not lines:
        print(QUIET.format(n=len(doc["repositories"])))
    else:
        print("\n".join(report(lines, everything)))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--record", action="store_true",
                      help="canonize: write .cypress/anchor.json for every governed repository")
    mode.add_argument("--compare", action="store_true",
                      help="session start: say whether code moved since the anchor; writes nothing")
    ap.add_argument("--all", action="store_true",
                    help="with --compare: name every moved path, past the output budget")
    args = ap.parse_args()
    if args.all and not args.compare:
        ap.error("--all goes with --compare")
    if args.compare:
        return compare(args.all)
    try:
        return record()
    except source_paths.Refused as e:
        print(f"code-anchor: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
