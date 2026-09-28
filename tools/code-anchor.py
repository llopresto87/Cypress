#!/usr/bin/env python3
"""code-anchor.py: what the code looked like when the graph last matched it.

The graph states facts about code, and code moves under it: a commit, a branch
checkout, uncommitted work. This tool marks the state of the code at canonize,
the moment the graph was last reconciled against it, and says once per session
start whether any code moved since. Paths under `docs/graph/` and `.cypress/`
are the graph and its state, not code, and never count (SPEC-0003, "Code
anchor").

Placed in a plant as `docs/graph/code-anchor.py` and run from the plant root:

    python3 docs/graph/code-anchor.py --record          # canonize: write the anchor
    python3 docs/graph/code-anchor.py --compare         # session start: one short report
    python3 docs/graph/code-anchor.py --compare --all   # every moved path, no budget

Governed repositories are the plant root, when it is a Git work tree, plus
each distinct `repo:` value in node frontmatter under `docs/graph/` that
resolves, inside the plant root, to a directory holding `.git`. `--record`
finds them and stores, per repository, the branch, the commit and each
uncommitted code path with its Git blob hash in `.cypress/anchor.json`.
`--compare` reads the list from the anchor and names the paths that moved:
changed between the recorded commit and HEAD, uncommitted now and not at the
anchor, or holding content other than the recorded hash. A path whose content
equals its recorded hash has not moved.

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
import hashlib
import json
import os
import posixpath
import re
import secrets
import stat
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# --- constants and texts (SPEC-0003 §6): this file is their one home. ---
# ANCHOR_TIMEOUT and the not-checked line are the callers': the hooks print
# that line when this tool is absent, fails or runs past their wait.
ANCHOR_VERSION = 1
ANCHOR_QUIET_MAX_BYTES = 160
ANCHOR_MAX_PATHS = 20
ANCHOR_MAX_BYTES = 2048
ANCHOR_DIRTY_MAX = 256
GIT_TIMEOUT = 10            # seconds per Git call

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
NOT_CODE = ("docs/graph/", ".cypress/")
DELETED = "deleted"
DETACHED = "(detached)"
TEMP_PREFIX = ".tmp-anchor-"
SHA1 = re.compile(r"^[0-9a-f]{40}$")
REPO_VALUE = re.compile(r"^repo:[ \t]*(.*?)[ \t]*$")
ISO_UTC = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?(Z|\+00:00)$")

# Every anchor file call is relative to a descriptor on `.cypress/`. A platform
# without these has no safe way to refuse a symlink, so it gets no anchor, never
# a path-string fallback. os.replace rides on renameat, listed as `rename`.
DIR_FD_CALLS = {"open", "stat", "unlink", "rename"}

# Variables that would point Git at some other repository or index than the
# work tree it runs in.
GIT_LOCATORS = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
                "GIT_OBJECT_DIRECTORY")

ROOT = Path.cwd()


class Refused(Exception):
    """A record that must not be written. The message is the stderr line."""


class Unrecorded(Exception):
    """No usable anchor, or no Git to compare with. The message is the reason
    the not-recorded line carries."""


class GitMissing(Exception):
    pass


class GitFailed(Exception):
    pass


# --- Git: the one boundary to the repositories ------------------------------
def git(repo: Path, *args: str) -> bytes:
    """One Git call in `repo`, as an argument list, bounded by GIT_TIMEOUT.
    Optional locks and the fsmonitor are off, so no call rewrites the index
    or leaves a file behind; a partial clone never fetches a missing object."""
    env = {k: v for k, v in os.environ.items() if k not in GIT_LOCATORS}
    env.update(GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0", GIT_NO_LAZY_FETCH="1")
    try:
        r = subprocess.run(["git", "--no-optional-locks", "-c", "core.fsmonitor=false", *args],
                           cwd=str(repo), env=env, stdin=subprocess.DEVNULL,
                           capture_output=True, timeout=GIT_TIMEOUT)
    except FileNotFoundError:
        raise GitMissing() from None
    except (OSError, subprocess.SubprocessError) as e:
        raise GitFailed(f"git {args[0]}: {type(e).__name__}") from None
    if r.returncode != 0:
        raise GitFailed(f"git {args[0]} exited {r.returncode}")
    return r.stdout


def head_state(repo: Path):
    """(branch or None when detached, commit) of the work tree at `repo`."""
    commit = git(repo, "rev-parse", "--verify", "HEAD^{commit}").decode().strip()
    if not SHA1.match(commit):
        raise GitFailed("HEAD is not a SHA-1 commit")
    try:
        branch = git(repo, "symbolic-ref", "-q", "--short", "HEAD").decode().strip() or None
    except GitFailed:
        branch = None
    return branch, commit


def uncommitted(repo: Path) -> list:
    """Every path `git status` shows as changed or untracked, relative to the
    repository, ignored files left out."""
    out = git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--no-renames")
    return [e[3:].decode("utf-8", "surrogateescape") for e in out.split(b"\0") if len(e) > 3]


def changed_between(repo: Path, old: str, new: str) -> list:
    out = git(repo, "diff-tree", "-r", "-z", "--name-only", "--no-renames", old, new)
    return [p.decode("utf-8", "surrogateescape") for p in out.split(b"\0") if p]


def reachable(repo: Path, commit: str) -> bool:
    try:
        git(repo, "cat-file", "-e", commit + "^{commit}")
    except GitFailed:
        return False
    return True


# --- paths and content -------------------------------------------------------
def plant_path(repo: str, path: str) -> str:
    return path if repo == "." else posixpath.join(repo, path)


def is_code(repo: str, path: str) -> bool:
    rel = plant_path(repo, path.rstrip("/")) + "/"
    return not rel.startswith(NOT_CODE)


def content_state(repo: Path, path: str):
    """The Git blob hash of the path's content now, DELETED when nothing is
    there, or None when it cannot be hashed (a directory, a nested work tree,
    an unreadable file). None never equals a recorded hash, so such a path
    always counts as moved."""
    p = repo / path
    try:
        st = os.lstat(p)
        if stat.S_ISLNK(st.st_mode):
            data = os.fsencode(os.readlink(p))
        elif stat.S_ISREG(st.st_mode):
            data = p.read_bytes()
        else:
            return None
    except FileNotFoundError:
        return DELETED
    except OSError:
        return None
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


# --- governed repositories ---------------------------------------------------
def repo_values(graph: Path):
    """Each `repo:` value in the frontmatter of a node under `graph`."""
    for dirpath, dirnames, filenames in os.walk(graph):
        for name in filenames:
            if not name.endswith(".md"):
                continue
            try:
                with open(os.path.join(dirpath, name), encoding="utf-8", errors="replace") as f:
                    if f.readline().rstrip("\r\n") != "---":
                        continue
                    for line in f:
                        line = line.rstrip("\r\n")
                        if line == "---":
                            break
                        m = REPO_VALUE.match(line)
                        value = m.group(1).split(" #", 1)[0].strip().strip("'\"") if m else ""
                        if value:
                            yield value
            except OSError:
                continue


def governed_repositories(root: Path) -> list:
    """The plant root when it is a Git work tree, then each distinct `repo:`
    value that resolves inside the root to a directory holding `.git`, as
    paths relative to the root ("." is the root)."""
    top = root.resolve()
    nested = set()
    for value in repo_values(root / "docs" / "graph"):
        target = (root / value).resolve()
        try:
            rel = target.relative_to(top).as_posix()
        except ValueError:
            continue
        if rel != "." and target.is_dir() and (target / ".git").exists():
            nested.add(rel)
    return (["."] if (root / ".git").exists() else []) + sorted(nested)


# --- the anchor file ---------------------------------------------------------
def open_anchor_dir():
    """A descriptor on <ROOT>/.cypress, opened without following a symlink.
    FileNotFoundError when it is absent; any other OSError when unusable."""
    if not (hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY")
            and DIR_FD_CALLS <= {f.__name__ for f in os.supports_dir_fd}):
        raise OSError(0, "no descriptor-relative file calls on this platform")
    return os.open(ROOT / ANCHOR_DIR, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)


def relative(path) -> bool:
    """True for a clean path inside the directory it is relative to."""
    return isinstance(path, str) and (path == "." or (
        not path.startswith("/") and posixpath.normpath(path) == path
        and ".." not in path.split("/")))


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
        if not relative(e["path"]) or e["path"] in seen:
            return "bad repository path"
        seen.add(e["path"])
        if not (e["branch"] is None or isinstance(e["branch"], str)):
            return "bad branch"
        if not isinstance(e["commit"], str) or not SHA1.match(e["commit"]):
            return "bad commit"
        dirty = e["dirty"]
        if not isinstance(dirty, dict) or not all(
                relative(k) and isinstance(v, str) and (v == DELETED or SHA1.match(v))
                for k, v in dirty.items()):
            return "bad dirty"
        if type(e["dirty_overflow"]) is not bool:
            return "bad dirty_overflow"
    return None


def read_anchor() -> dict:
    """The recorded anchor, or Unrecorded naming why there is none to use."""
    try:
        dir_fd = open_anchor_dir()
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


def write_anchor(dir_fd: int, doc: dict) -> None:
    """Replace the anchor atomically: a 0644 temp file created exclusively,
    then os.replace onto the name. On any failure the temp file is removed and
    the old anchor, if any, stays as it was. An anchor name that is anything
    but a regular file (a symlink above all) is refused, never replaced."""
    try:
        st = os.stat(ANCHOR_NAME, dir_fd=dir_fd, follow_symlinks=False)
        if not stat.S_ISREG(st.st_mode):
            raise Refused(f"refusing {ANCHOR_DIR}/{ANCHOR_NAME}: not a regular file "
                          f"(a symlink is never followed); nothing written")
    except FileNotFoundError:
        pass
    data = (json.dumps(doc, indent=2) + "\n").encode()
    tmp = TEMP_PREFIX + secrets.token_hex(8)
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644, dir_fd=dir_fd)
    try:
        try:
            os.fchmod(fd, 0o644)
            view = memoryview(data)
            while view:
                view = view[os.write(fd, view):]
        finally:
            os.close(fd)
        os.replace(tmp, ANCHOR_NAME, src_dir_fd=dir_fd, dst_dir_fd=dir_fd)
    except BaseException:
        try:
            os.unlink(tmp, dir_fd=dir_fd)
        except FileNotFoundError:
            pass
        raise


# --- record ------------------------------------------------------------------
def snapshot(root: Path, rel: str):
    """One repository's anchor entry, and how many uncommitted code paths it
    has: branch, commit, and each such path with its content (at most
    ANCHOR_DIRTY_MAX, else dirty_overflow and none). A path that cannot be
    hashed is left out, so a compare counts it moved."""
    repo = root / rel
    branch, commit = head_state(repo)
    paths = [p for p in uncommitted(repo) if is_code(rel, p)]
    overflow = len(paths) > ANCHOR_DIRTY_MAX
    states = {} if overflow else {p: content_state(repo, p) for p in sorted(paths)}
    dirty = {p: s for p, s in states.items() if s is not None}
    return {"path": rel, "branch": branch, "commit": commit, "dirty": dirty,
            "dirty_overflow": overflow}, len(paths)


def record() -> int:
    try:
        dir_fd = open_anchor_dir()
    except FileNotFoundError:
        raise Refused(f"{ANCHOR_DIR}/ is missing, and this tool never creates it; "
                      f"nothing written") from None
    except OSError as e:
        raise Refused(f"{ANCHOR_DIR}/ is unusable ({e.strerror or type(e).__name__}); "
                      f"nothing written") from None
    try:
        repos = governed_repositories(ROOT)
        if not repos:
            raise Refused("no governed Git repository (the plant root is not a work tree and "
                          "no repo: resolves to one); nothing written")
        snaps = []
        for rel in repos:
            try:
                snaps.append(snapshot(ROOT, rel))
            except GitMissing:
                raise Refused("git is not on PATH; nothing written") from None
            except GitFailed as e:
                raise Refused(f"{rel}: {e}; nothing written") from None
        entries = [entry for entry, _ in snaps]
        at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        doc = {"version": ANCHOR_VERSION, "recorded_at": at, "repositories": entries}
        try:
            write_anchor(dir_fd, doc)
        except OSError as e:
            raise Refused(f"{ANCHOR_DIR}/{ANCHOR_NAME} not written "
                          f"({e.strerror or type(e).__name__}); the old anchor stands") from None
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
    except GitFailed as e:
        return [(f"unverified ({e})", [])]
    recorded = {} if entry["dirty_overflow"] else entry["dirty"]
    hits = {p for p in committed | now | set(recorded) if is_code(rel, p)
            and (p not in recorded or content_state(repo, p) != recorded[p])}
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
    except GitMissing:
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
    except Refused as e:
        print(f"code-anchor: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
