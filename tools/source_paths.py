"""source_paths: the seed's rules for what counts as source and how a path is named.

One home for the path rules the seed's tools share, so no two of them can
disagree about a path:

  * the code-path rule: paths under `docs/graph/` and `.cypress/` are the
    graph and its state, not code, and neither are build and backup files
    (`__pycache__/`, `*.pyc`, `*.bak`, `*.bak-*`), which no fact describes
    (SPEC-0003, "Code anchor");
  * the governed repositories: the plant root when it is a Git work tree,
    plus each `repo:` value in node frontmatter that resolves inside the root
    to a directory holding `.git`;
  * the Git boundary: every Git call, with the variables that would point it
    at another repository removed and optional locks off;
  * the content state of a path, as its Git blob hash;
  * the descriptor-relative atomic write under `.cypress/`, which never
    follows a symlink;
  * the citation grammar and `cite_problem`, the strict plant-relative reading
    of a cited path (SPEC-0007 §6 "Helper").

A scratch directory under `.cypress/` that the atomic write fills ignores
itself with an inner `.gitignore` of `*`; the other home of that self-ignore
rule is route-hook.py's `.cypress/session/` writer.

Library module, no CLI. code-anchor.py and growth-audit.py load it by file
path from beside themselves, like frontmatter.py; it loads the one
frontmatter reader, `frontmatter.py`, from beside itself. install.sh places it
in a plant's `docs/graph/`, beside code-anchor.py. No function reads a
module-global root: each takes the root, or the repository, as a parameter.
"""

import hashlib
import os
import posixpath
import re
import secrets
import stat
import subprocess
from pathlib import Path
import importlib.util as _ilu
_fm_spec = _ilu.spec_from_file_location(
    "cypress_frontmatter", Path(__file__).resolve().parent / "frontmatter.py")
_frontmatter = _ilu.module_from_spec(_fm_spec)
_fm_spec.loader.exec_module(_frontmatter)

GIT_TIMEOUT = 10            # seconds per Git call
NOT_CODE = ("docs/graph/", ".cypress/")
NOISE_DIR = "__pycache__"                       # build and backup files: never code
NOISE_NAME = re.compile(r"\.(pyc|bak)$|\.bak-\d")   # *.bak-<digit>*: the installer's stamp
DELETED = "deleted"

# Variables that would point Git at some other repository or index than the
# work tree it runs in.
GIT_LOCATORS = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
                "GIT_OBJECT_DIRECTORY")

# Every file call of the atomic write is relative to a directory descriptor. A
# platform without these has no safe way to refuse a symlink, so it gets no
# write, never a path-string fallback. os.replace rides on renameat, listed as
# `rename`.
DIR_FD_CALLS = {"open", "stat", "unlink", "rename"}

MISSING_CITATION = "does not exist in the plant"
MALFORMED_CITATION = "is not a path citation"

# The shape a citation may take: a relative path, an optional `:line` (or
# `:line:col`, or `:line-line`) suffix, and — stripped before this is ever
# asked — a `#anchor`. A segment may hold a space, because a repository path
# may; what it may not hold is the punctuation prose arrives with, which is
# what makes a trailing note detectable as one.
_CITE_SEG = r"[^\s/:'\"()\[\]{}<>|*?=,;]+(?: [^\s/:'\"()\[\]{}<>|*?=,;]+)*"
CITATION_RE = re.compile(
    rf"{_CITE_SEG}(?:/{_CITE_SEG})*/?(?::\d+(?::\d+)?(?:-\d+)?)?")
_LINE_SUFFIX = re.compile(r":(\d+)(?::\d+)?(-\d+)?$")


class Refused(Exception):
    """A write that must not happen. The message is the line the caller shows."""


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


# --- paths and content -------------------------------------------------------
def plant_path(repo: str, path: str) -> str:
    """A repository-relative path made plant-relative ("." is the root)."""
    return path if repo == "." else posixpath.join(repo, path)


def is_code(repo: str, path: str) -> bool:
    """False for the graph and its state, and for build and backup noise
    (SPEC-0003 ANCHOR_IGNORES_BUILD_AND_BACKUP_NOISE)."""
    rel = plant_path(repo, path.rstrip("/"))
    *dirs, name = rel.split("/")
    return not ((rel + "/").startswith(NOT_CODE) or NOISE_DIR in dirs or NOISE_NAME.search(name))


def relative(path) -> bool:
    """True for a clean path inside the directory it is relative to."""
    return isinstance(path, str) and (path == "." or (
        not path.startswith("/") and posixpath.normpath(path) == path
        and ".." not in path.split("/")))


def content_state(repo: Path, path: str):
    """The Git blob hash of the path's content now, DELETED when nothing is
    there, or None when it cannot be hashed (a directory, a nested work tree,
    an unreadable file). A symlink hashes its link text."""
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
    """Each string `repo:` value the one frontmatter reader returns for a node
    under `graph`. A node it refuses, or an unreadable file, is skipped."""
    for dirpath, dirnames, filenames in os.walk(graph):
        for name in filenames:
            if not name.endswith(".md"):
                continue
            try:
                meta, _ = _frontmatter.parse_file(os.path.join(dirpath, name))
            except (OSError, _frontmatter.FrontmatterError):
                continue
            value = meta.get("repo")
            if isinstance(value, str) and value:
                yield value


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


# --- the descriptor-relative atomic write ------------------------------------
def open_dir(root: Path, *parts: str) -> int:
    """A descriptor on <root>/<parts...>, each part opened relative to the one
    before and never through a symlink. FileNotFoundError when a part is
    absent; any other OSError when unusable."""
    if not (hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY")
            and DIR_FD_CALLS <= {f.__name__ for f in os.supports_dir_fd}):
        raise OSError(0, "no descriptor-relative file calls on this platform")
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in parts:
            inner = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = inner
    except BaseException:
        os.close(fd)
        raise
    return fd


def atomic_write(dir_fd: int, name: str, data: bytes, temp_prefix: str, shown: str) -> None:
    """Replace `name` under `dir_fd` atomically: a 0644 temp file named
    `temp_prefix` plus a random suffix, created exclusively, then os.replace
    onto the name. On any failure the temp file is removed and the old file,
    if any, stays as it was. A name that is anything but a regular file (a
    symlink above all) is Refused, never replaced; `shown` names it there."""
    try:
        st = os.stat(name, dir_fd=dir_fd, follow_symlinks=False)
        if not stat.S_ISREG(st.st_mode):
            raise Refused(f"refusing {shown}: not a regular file "
                          f"(a symlink is never followed); nothing written")
    except FileNotFoundError:
        pass
    tmp = temp_prefix + secrets.token_hex(8)
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644, dir_fd=dir_fd)
    try:
        try:
            os.fchmod(fd, 0o644)
            view = memoryview(data)
            while view:
                view = view[os.write(fd, view):]
        finally:
            os.close(fd)
        os.replace(tmp, name, src_dir_fd=dir_fd, dst_dir_fd=dir_fd)
    except BaseException:
        try:
            os.unlink(tmp, dir_fd=dir_fd)
        except FileNotFoundError:
            pass
        raise


# --- citations ---------------------------------------------------------------
def split_citation(ref):
    """(cited, path, line) of a reference: `cited` with any `#anchor`
    stripped, `path` with the `:line`, `:line:col` or `:line-line` suffix
    stripped too, and the first line it names, or None."""
    cited = str(ref).split("#", 1)[0].strip()
    m = _LINE_SUFFIX.search(cited)
    return cited, _LINE_SUFFIX.sub("", cited).strip(), int(m.group(1)) if m else None


def shape_problem(ref):
    """The part of a reference that never was a path, as a phrase — or None
    when the whole of it parses as a citation.

    Asked only of a reference the filesystem could not answer for, because
    wherever a path resolves its shape is past arguing about. A reference
    carrying a trailing note, a quoted value or a parenthetical named no file
    to begin with, and reporting it as a missing one asserts a fact about the
    filesystem that was never tested: it sends the reader hunting for a file
    that is sitting exactly where the message says it is not."""
    m = CITATION_RE.match(ref)
    rest = (ref[m.end():] if m else ref).strip()
    if not rest:
        return None
    return f"{MALFORMED_CITATION} — {rest!r} is not part of a path"


def cite_problem(plant, ref):
    """Why a cited path does not resolve, as a phrase — or None when it does.

    A citation names a real file INSIDE the plant, and the line it names is in
    that file. Anchor suffixes (`path#section`) are stripped and not checked:
    there is no cheap check for an anchor, and inventing one is a different
    job. A line suffix IS checked, because the line number is the part of a
    citation a reader actually follows — `manifest.json:999999` resolved
    against a file whose last line is 457 for as long as the suffix was
    stripped and forgotten. A directory is not a citation
    (`docs/graph/sources/` names where the evidence would live, not any
    evidence), and an absolute path is not a claim about this plant at all.

    A reference that is not a citation at all is reported as one. "This file
    does not exist" is a claim about the filesystem, and a reference that never
    parsed as a path never reached the filesystem to earn it — every shape the
    grammar did not recognise collapsed into that one phrase, and the reader
    went looking for the wrong defect."""
    cited, raw, cited_line = split_citation(ref)
    if not raw:
        return f"{MALFORMED_CITATION} — it names no path"
    if Path(raw).is_absolute():
        return MISSING_CITATION
    target = plant / raw
    try:
        target.resolve().relative_to(plant.resolve())
    except (ValueError, OSError):
        return MISSING_CITATION
    if not target.is_file():
        return shape_problem(cited) or MISSING_CITATION
    if cited_line:
        try:
            held = len(target.read_text(encoding="utf-8",
                                        errors="replace").splitlines())
        except OSError:
            return MISSING_CITATION
        if cited_line > held:
            return (f"names line {cited_line} of a file that holds "
                    f"{held} lines")
    return None
